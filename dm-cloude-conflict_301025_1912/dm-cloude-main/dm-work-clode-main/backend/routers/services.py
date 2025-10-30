from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.base import get_db
from models.service import Service, ProjectService
from models.project import Project
from schemas.service import ServiceCreate, ServiceUpdate, ServiceRead, ProjectServiceCreate, ProjectServiceRead
from typing import Optional, List

router = APIRouter(prefix="/services")

@router.post("/", response_model=ServiceRead)
def create_service(service_data: ServiceCreate, db: Session = Depends(get_db)):
    """Создание новой услуги"""
    service = Service(**service_data.dict())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

@router.get("/", response_model=List[ServiceRead])
def get_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    active_only: bool = Query(True, description="Показывать только активные услуги"),
    db: Session = Depends(get_db)
):
    """Получение списка услуг"""
    query = db.query(Service)
    
    if active_only:
        query = query.filter(Service.is_active == True)
    
    if category:
        query = query.filter(Service.category == category)
    
    services = query.order_by(Service.name).offset(skip).limit(limit).all()
    return services

@router.get("/{service_id}", response_model=ServiceRead)
def get_service(service_id: str, db: Session = Depends(get_db)):
    """Получение услуги по ID"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    return service

@router.put("/{service_id}", response_model=ServiceRead)
def update_service(service_id: str, service_data: ServiceUpdate, db: Session = Depends(get_db)):
    """Обновление услуги"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    
    update_data = service_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)
    
    db.commit()
    db.refresh(service)
    return service

# Услуги проекта
@router.post("/project-services/", response_model=ProjectServiceRead)
def add_service_to_project(project_service_data: ProjectServiceCreate, db: Session = Depends(get_db)):
    """Добавление услуги к проекту"""
    # Проверяем существование проекта и услуги
    project = db.query(Project).filter(Project.id == project_service_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    service = db.query(Service).filter(Service.id == project_service_data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    
    project_service = ProjectService(**project_service_data.dict())
    db.add(project_service)
    db.commit()
    db.refresh(project_service)
    return project_service

@router.get("/project-services/{project_id}", response_model=List[ProjectServiceRead])
def get_project_services(project_id: str, db: Session = Depends(get_db)):
    """Получение всех услуг проекта"""
    project_services = db.query(ProjectService).filter(ProjectService.project_id == project_id).all()
    return project_services

@router.get("/categories/")
def get_service_categories(db: Session = Depends(get_db)):
    """Получение списка всех категорий услуг"""
    categories = db.query(Service.category).filter(
        Service.category.isnot(None),
        Service.is_active == True
    ).distinct().all()
    
    return {"categories": [cat[0] for cat in categories if cat[0]]}
