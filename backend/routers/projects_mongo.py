from fastapi import APIRouter, Depends, HTTPException, Query, Header
from database.base import get_db, projects_collection
from routers.auth_mongo import get_current_user
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
import uuid

router = APIRouter(prefix="/projects")

# Pydantic схемы для направлений проекта
class ProjectDirection(BaseModel):
    name: str  # продвижение, аналитика, внедрение CRM, интеграция CRM и МИС, колл-центр, создание сайта
    budget: Optional[float] = 0.0
    start_date: Optional[date] = None  # Дата старта направления
    end_date: Optional[date] = None  # Дата остановки направления

class ProjectBase(BaseModel):
    name: str
    client_id: str
    description: Optional[str] = None
    status: str = "planning"  # planning, in_progress, completed, cancelled
    priority: Optional[int] = 3  # Приоритет 1-5 (1 - самый высокий)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = 0.0  # Общий бюджет (вычисляется автоматически)
    directions: Optional[List[ProjectDirection]] = []  # Направления с бюджетами
    project_manager: Optional[str] = None  # Проект-менеджер (Прыгункова Елена, Гарасюта Александр)
    # Услуги и зоны развития
    connected_services: Optional[List[str]] = []  # Подключенные услуги
    development_zones: Optional[List[str]] = []  # Зоны для развития
    # Детальная информация проекта
    brief: Optional[str] = None
    requirements: Optional[str] = None
    deliverables: Optional[str] = None
    notes: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None
    client_id: Optional[str] = None
    status: Optional[str] = None

class ProjectRead(BaseModel):
    id: str
    name: str
    client_id: str
    description: Optional[str] = None
    status: str = "planning"
    priority: Optional[int] = 3
    start_date: Optional[datetime] = None  # Изменено на datetime для совместимости с MongoDB
    end_date: Optional[datetime] = None  # Изменено на datetime для совместимости с MongoDB
    budget: Optional[float] = 0.0
    directions: Optional[List[ProjectDirection]] = []  # Направления с бюджетами
    project_manager: Optional[str] = None  # Проект-менеджер
    connected_services: Optional[List[str]] = []
    development_zones: Optional[List[str]] = []
    # Детальная информация проекта
    brief: Optional[str] = None
    requirements: Optional[str] = None
    deliverables: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class ProjectListResponse(BaseModel):
    projects: List[ProjectRead]
    total: int

@router.get("/", response_model=ProjectListResponse)
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    client_id: Optional[str] = None,
    direction: Optional[str] = None,  # Фильтр по направлению
    project_manager: Optional[str] = None,  # Фильтр по проект-менеджеру
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Получить список проектов с пагинацией и фильтрами"""
    query = {}
    
    if status:
        query["status"] = status
    if client_id:
        query["client_id"] = client_id
    if direction:
        # Фильтр по направлению - ищем в массиве directions
        query["directions.name"] = direction
    if project_manager:
        query["project_manager"] = project_manager
    
    projects = list(projects_collection.find(query).skip(skip).limit(limit))
    total = projects_collection.count_documents(query)
    
    for project in projects:
        project.pop("_id", None)
    
    return {"projects": projects, "total": total}

@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Получить проект по ID"""
    project = projects_collection.find_one({"id": project_id})
    
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    project.pop("_id", None)
    return project

@router.post("/", response_model=ProjectRead, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Создать новый проект"""
    
    project_dict = project_data.dict()
    
    # Рассчитываем общий бюджет как сумму бюджетов направлений
    if project_dict.get("directions"):
        total_budget = sum(direction.get("budget", 0.0) for direction in project_dict["directions"])
        project_dict["budget"] = total_budget
        
        # Конвертируем даты направлений в datetime
        for direction in project_dict["directions"]:
            if direction.get("start_date") and not isinstance(direction["start_date"], datetime):
                direction["start_date"] = datetime.combine(direction["start_date"], datetime.min.time())
            if direction.get("end_date") and not isinstance(direction["end_date"], datetime):
                direction["end_date"] = datetime.combine(direction["end_date"], datetime.min.time())
    
    # Конвертируем date в datetime для MongoDB
    if project_dict.get("start_date") and not isinstance(project_dict["start_date"], datetime):
        project_dict["start_date"] = datetime.combine(project_dict["start_date"], datetime.min.time())
    if project_dict.get("end_date") and not isinstance(project_dict["end_date"], datetime):
        project_dict["end_date"] = datetime.combine(project_dict["end_date"], datetime.min.time())
    
    project_dict.update({
        "id": str(uuid.uuid4()),
        "created_at": datetime.utcnow(),
        "updated_at": None
    })
    
    projects_collection.insert_one(project_dict)
    
    project_dict.pop("_id", None)
    return project_dict

@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Обновить проект"""
    
    existing = projects_collection.find_one({"id": project_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    update_data = project_data.dict(exclude_unset=True)
    
    # Рассчитываем общий бюджет как сумму бюджетов направлений
    if update_data.get("directions"):
        total_budget = sum(direction.get("budget", 0.0) for direction in update_data["directions"])
        update_data["budget"] = total_budget
        
        # Конвертируем даты направлений в datetime
        for direction in update_data["directions"]:
            if direction.get("start_date") and not isinstance(direction["start_date"], datetime):
                direction["start_date"] = datetime.combine(direction["start_date"], datetime.min.time())
            if direction.get("end_date") and not isinstance(direction["end_date"], datetime):
                direction["end_date"] = datetime.combine(direction["end_date"], datetime.min.time())
    
    # Конвертируем date в datetime
    if update_data.get("start_date") and not isinstance(update_data["start_date"], datetime):
        update_data["start_date"] = datetime.combine(update_data["start_date"], datetime.min.time())
    if update_data.get("end_date") and not isinstance(update_data["end_date"], datetime):
        update_data["end_date"] = datetime.combine(update_data["end_date"], datetime.min.time())
    
    update_data["updated_at"] = datetime.utcnow()
    
    projects_collection.update_one(
        {"id": project_id},
        {"$set": update_data}
    )
    
    updated_project = projects_collection.find_one({"id": project_id})
    updated_project.pop("_id", None)
    
    return updated_project

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Удалить проект"""
    
    result = projects_collection.delete_one({"id": project_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    return {"message": "Проект успешно удален", "id": project_id}

@router.get("/by-status/{status}", response_model=List[ProjectRead])
async def get_projects_by_status(
    status: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Получить проекты по статусу"""
    projects = list(projects_collection.find({"status": status}))
    
    for project in projects:
        project.pop("_id", None)
    
    return projects
