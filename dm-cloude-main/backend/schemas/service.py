from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    unit: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class ServiceRead(ServiceBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProjectServiceBase(BaseModel):
    project_id: str
    service_id: str
    quantity: float = 1.0
    price: float
    total: float
    notes: Optional[str] = None

class ProjectServiceCreate(ProjectServiceBase):
    pass

class ProjectServiceRead(ProjectServiceBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
