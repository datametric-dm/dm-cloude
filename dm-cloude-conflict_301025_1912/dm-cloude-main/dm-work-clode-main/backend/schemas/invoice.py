from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.invoice import InvoiceStatus

class InvoiceItemBase(BaseModel):
    description: str
    quantity: float = 1.0
    price: float
    total: float

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemRead(InvoiceItemBase):
    id: str
    
    class Config:
        from_attributes = True

class InvoiceBase(BaseModel):
    number: str
    client_id: str
    project_id: Optional[str] = None
    date_due: datetime
    subtotal: float
    tax_rate: float = 20.0
    tax_amount: float
    total: float
    status: InvoiceStatus = InvoiceStatus.DRAFT
    description: Optional[str] = None
    notes: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate] = []

class InvoiceUpdate(BaseModel):
    number: Optional[str] = None
    date_due: Optional[datetime] = None
    status: Optional[InvoiceStatus] = None
    description: Optional[str] = None
    notes: Optional[str] = None

class InvoiceRead(InvoiceBase):
    id: str
    date_issued: datetime
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemRead] = []
    
    class Config:
        from_attributes = True

class InvoiceList(BaseModel):
    invoices: List[InvoiceRead]
    total: int
    page: int
    size: int
