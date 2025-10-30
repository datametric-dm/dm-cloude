from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database.base import get_db
from models.project import Project, ProjectStatus
from models.client import Client
from schemas.project import ProjectCreate, ProjectUpdate, ProjectRead, ProjectList
from typing import Optional

router = APIRouter(prefix="/projects")

@router.post("/", response_model=ProjectRead)
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)):
    """Создание нового проекта"""
    # Проверяем, что клиент существует
    client = db.query(Client).filter(Client.id == project_data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    project = Project(**project_data.dict())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/", response_model=ProjectList)
def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Поиск по названию или описанию"),
    client_id: Optional[str] = Query(None, description="Фильтр по клиенту"),
    status: Optional[ProjectStatus] = Query(None, description="Фильтр по статусу"),
    active_only: bool = Query(True, description="Показывать только активные проекты"),
    db: Session = Depends(get_db)
):
    """Получение списка проектов"""
    query = db.query(Project)
    
    if active_only:
        query = query.filter(Project.is_active == True)
    
    if client_id:
        query = query.filter(Project.client_id == client_id)
    
    if status:
        query = query.filter(Project.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Project.name.ilike(search_term),
                Project.description.ilike(search_term)
            )
        )
    
    total = query.count()
    projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
    
    return ProjectList(
        projects=projects,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, db: Session = Depends(get_db)):
    """Получение проекта по ID"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project

@router.put("/{project_id}", response_model=ProjectRead)
def update_project(project_id: str, project_data: ProjectUpdate, db: Session = Depends(get_db)):
    """Обновление проекта"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    update_data = project_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    """Мягкое удаление проекта"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    project.is_active = False
    db.commit()
    
    return {"message": "Проект успешно деактивирован"}

@router.get("/by-status/{status}")
def get_projects_by_status(status: ProjectStatus, db: Session = Depends(get_db)):
    """Получение проектов по статусу"""
    projects = db.query(Project).filter(
        Project.status == status,
        Project.is_active == True
    ).order_by(Project.created_at.desc()).all()
    
    return {"projects": projects, "count": len(projects)}
