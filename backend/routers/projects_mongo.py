from fastapi import APIRouter, Depends, HTTPException, Query
from database.base import get_db, projects_collection
from routers.auth_mongo import get_current_user
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
import uuid

router = APIRouter(prefix="/projects")

# Pydantic схемы
class ProjectBase(BaseModel):
    name: str
    client_id: str
    description: Optional[str] = None
    status: str = "planning"  # planning, in_progress, completed, cancelled
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = 0.0
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
    start_date: Optional[datetime] = None  # Изменено на datetime для совместимости с MongoDB
    end_date: Optional[datetime] = None  # Изменено на datetime для совместимости с MongoDB
    budget: Optional[float] = 0.0
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
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Получить список проектов с пагинацией и фильтрами"""
    query = {}
    
    if status:
        query["status"] = status
    if client_id:
        query["client_id"] = client_id
    
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
    
    # Конвертируем date в datetime
    if update_data.get("start_date"):
        update_data["start_date"] = datetime.combine(update_data["start_date"], datetime.min.time())
    if update_data.get("end_date"):
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
