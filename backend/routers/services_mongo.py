from fastapi import APIRouter, Depends, HTTPException, Header, Query
from database.base import get_db, services_collection
from routers.auth_mongo import get_current_user
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

router = APIRouter(prefix="/services")

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = 0.0
    category: Optional[str] = None
    unit: str = "шт"

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(ServiceBase):
    name: Optional[str] = None
    price: Optional[float] = None

class ServiceRead(ServiceBase):
    id: str
    tenant_id: Optional[str] = None
    created_at: datetime

class ServiceListResponse(BaseModel):
    services: List[ServiceRead]
    total: int

@router.get("/", response_model=ServiceListResponse)
async def get_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    query = {}
    if x_company_id:
        query["tenant_id"] = x_company_id
    
    services = list(services_collection.find(query).skip(skip).limit(limit))
    total = services_collection.count_documents(query)
    for service in services:
        service.pop("_id", None)
    return {"services": services, "total": total}

@router.get("/{service_id}", response_model=ServiceRead)
async def get_service(
    service_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    query = {"id": service_id}
    if x_company_id:
        query["tenant_id"] = x_company_id
    
    service = services_collection.find_one(query)
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    service.pop("_id", None)
    return service

@router.post("/", response_model=ServiceRead, status_code=201)
async def create_service(
    service_data: ServiceCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID header is required")
    
    service_dict = service_data.dict()
    service_dict.update({
        "id": str(uuid.uuid4()),
        "tenant_id": x_company_id,
        "created_at": datetime.utcnow()
    })
    services_collection.insert_one(service_dict)
    service_dict.pop("_id", None)
    return service_dict

@router.put("/{service_id}", response_model=ServiceRead)
async def update_service(
    service_id: str,
    service_data: ServiceUpdate,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    query = {"id": service_id}
    if x_company_id:
        query["tenant_id"] = x_company_id
    
    existing = services_collection.find_one(query)
    if not existing:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    
    update_data = service_data.dict(exclude_unset=True)
    services_collection.update_one(query, {"$set": update_data})
    
    updated_service = services_collection.find_one(query)
    updated_service.pop("_id", None)
    return updated_service

@router.delete("/{service_id}")
async def delete_service(
    service_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    query = {"id": service_id}
    if x_company_id:
        query["tenant_id"] = x_company_id
    
    result = services_collection.delete_one(query)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    return {"message": "Услуга успешно удалена", "id": service_id}

@router.get("/categories/", response_model=List[str])
async def get_categories(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    # Возвращаем уникальные категории
    categories = services_collection.distinct("category")
    return [cat for cat in categories if cat]
