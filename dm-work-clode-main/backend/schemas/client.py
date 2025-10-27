from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class ClientBase(BaseModel):
    name: str
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    
    # Реквизиты
    inn: Optional[str] = None
    kpp: Optional[str] = None
    ogrn: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    bank_bik: Optional[str] = None
    
    # Контактные лица
    contact_person: Optional[str] = None
    contact_position: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    
    # Дополнительная информация
    notes: Optional[str] = None
    is_active: bool = True

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    ogrn: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    bank_bik: Optional[str] = None
    contact_person: Optional[str] = None
    contact_position: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class ClientRead(ClientBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ClientList(BaseModel):
    clients: List[ClientRead]
    total: int
    page: int
    size: int
