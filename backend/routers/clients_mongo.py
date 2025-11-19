from fastapi import APIRouter, Depends, HTTPException, Query, Header
from database.base import get_db, clients_collection
from routers.auth_mongo import get_current_user
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid

router = APIRouter(prefix="/clients")

# Pydantic схемы для контактного лица
class ContactPerson(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

# Pydantic схемы для подрядчиков/партнеров
class Contractor(BaseModel):
    name: str  # Название компании
    work_area: Optional[str] = None  # Область работы
    contact_person: Optional[str] = None  # Контактное лицо
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    notes: Optional[str] = None  # Примечания

class ClientBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    ogrn: Optional[str] = None
    edo: Optional[str] = None  # Система ЭДО (новое поле)
    status: Optional[str] = "active"  # active, suspended, churned (Приостановлен, Отвалился)
    # Старые поля контактов (для обратной совместимости)
    contact_person: Optional[str] = None
    contact_position: Optional[str] = None
    # Новое поле - множественные контакты
    contacts: Optional[List[ContactPerson]] = []
    # Подрядчики и партнеры
    contractors: Optional[List['Contractor']] = []
    notes: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    name: Optional[str] = None

class ClientRead(ClientBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class ClientListResponse(BaseModel):
    clients: List[ClientRead]
    total: int

@router.get("/", response_model=ClientListResponse)
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Получить список клиентов с пагинацией (с учетом tenant_id)"""
    query = {}
    if x_company_id:
        query["tenant_id"] = x_company_id
    
    clients = list(clients_collection.find(query).skip(skip).limit(limit))
    total = clients_collection.count_documents(query)
    
    # Убираем _id из MongoDB
    for client in clients:
        client.pop("_id", None)
    
    return {"clients": clients, "total": total}

@router.get("/{client_id}", response_model=ClientRead)
async def get_client(
    client_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Получить клиента по ID"""
    client = clients_collection.find_one({"id": client_id})
    
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    client.pop("_id", None)
    return client

@router.post("/", response_model=ClientRead, status_code=201)
async def create_client(
    client_data: ClientCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Создать нового клиента"""
    
    # Создаем клиента
    client_dict = client_data.dict()
    client_dict.update({
        "id": str(uuid.uuid4()),
        "created_at": datetime.utcnow(),
        "updated_at": None
    })
    
    clients_collection.insert_one(client_dict)
    
    client_dict.pop("_id", None)
    return client_dict

@router.put("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Обновить клиента"""
    
    # Проверяем существование
    existing = clients_collection.find_one({"id": client_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    # Обновляем только переданные поля
    update_data = client_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    clients_collection.update_one(
        {"id": client_id},
        {"$set": update_data}
    )
    
    # Получаем обновленного клиента
    updated_client = clients_collection.find_one({"id": client_id})
    updated_client.pop("_id", None)
    
    return updated_client

@router.delete("/{client_id}")
async def delete_client(
    client_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Удалить клиента"""
    
    result = clients_collection.delete_one({"id": client_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    return {"message": "Клиент успешно удален", "id": client_id}
