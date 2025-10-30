from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.project import ProjectStatus

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    client_id: str
    status: ProjectStatus = ProjectStatus.PLANNING
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    budget: Optional[float] = None
    brief: Optional[str] = None
    requirements: Optional[str] = None
    deliverables: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    budget: Optional[float] = None
    actual_cost: Optional[float] = None
    brief: Optional[str] = None
    requirements: Optional[str] = None
    deliverables: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class ProjectRead(ProjectBase):
    id: str
    actual_cost: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProjectList(BaseModel):
    projects: List[ProjectRead]
    total: int
    page: int
    size: int
