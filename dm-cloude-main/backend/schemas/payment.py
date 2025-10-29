from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.payment import PaymentStatus, PaymentType

class PaymentBase(BaseModel):
    client_id: str
    invoice_id: Optional[str] = None
    amount: float
    payment_date_planned: datetime
    payment_date_actual: Optional[datetime] = None
    status: PaymentStatus = PaymentStatus.PLANNED
    payment_type: Optional[PaymentType] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    reference_number: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    payment_date_planned: Optional[datetime] = None
    payment_date_actual: Optional[datetime] = None
    status: Optional[PaymentStatus] = None
    payment_type: Optional[PaymentType] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    reference_number: Optional[str] = None

class PaymentRead(PaymentBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PaymentList(BaseModel):
    payments: List[PaymentRead]
    total: int
    page: int
    size: int
