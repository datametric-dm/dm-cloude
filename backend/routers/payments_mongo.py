from fastapi import APIRouter, Depends, HTTPException, Query
from database.base import get_db, payments_collection
from routers.auth_mongo import get_current_user
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
import uuid

router = APIRouter(prefix="/payments")

class PaymentBase(BaseModel):
    invoice_id: Optional[str] = None
    client_id: str
    amount: float
    payment_date: date
    payment_method: str = "bank_transfer"
    status: str = "pending"
    description: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(PaymentBase):
    client_id: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None

class PaymentRead(BaseModel):
    id: str
    invoice_id: Optional[str] = None
    client_id: str
    amount: float
    payment_date: datetime
    payment_method: str = "bank_transfer"
    status: str = "pending"
    description: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

class PaymentListResponse(BaseModel):
    payments: List[PaymentRead]
    total: int

@router.get("/", response_model=PaymentListResponse)
async def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    query = {}
    if status:
        query["status"] = status
    
    payments = list(payments_collection.find(query).skip(skip).limit(limit))
    total = payments_collection.count_documents(query)
    
    for payment in payments:
        payment.pop("_id", None)
    return {"payments": payments, "total": total}

@router.get("/overdue/list", response_model=List[PaymentRead])
async def get_overdue_payments(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    payments = list(payments_collection.find({"status": "pending"}))
    for payment in payments:
        payment.pop("_id", None)
    return payments

@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(
    payment_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    payment = payments_collection.find_one({"id": payment_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    payment.pop("_id", None)
    return payment

@router.post("/", response_model=PaymentRead, status_code=201)
async def create_payment(
    payment_data: PaymentCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    payment_dict = payment_data.dict()
    
    if payment_dict.get("payment_date") and not isinstance(payment_dict["payment_date"], datetime):
        payment_dict["payment_date"] = datetime.combine(payment_dict["payment_date"], datetime.min.time())
    
    payment_dict.update({
        "id": str(uuid.uuid4()),
        "created_at": datetime.utcnow()
    })
    
    payments_collection.insert_one(payment_dict)
    payment_dict.pop("_id", None)
    return payment_dict

@router.put("/{payment_id}", response_model=PaymentRead)
async def update_payment(
    payment_id: str,
    payment_data: PaymentUpdate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    existing = payments_collection.find_one({"id": payment_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    
    update_data = payment_data.dict(exclude_unset=True)
    
    if update_data.get("payment_date"):
        update_data["payment_date"] = datetime.combine(update_data["payment_date"], datetime.min.time())
    
    payments_collection.update_one({"id": payment_id}, {"$set": update_data})
    
    updated_payment = payments_collection.find_one({"id": payment_id})
    updated_payment.pop("_id", None)
    return updated_payment

@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    result = payments_collection.delete_one({"id": payment_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    return {"message": "Платеж успешно удален", "id": payment_id}

@router.post("/{payment_id}/mark-received")
async def mark_payment_received(
    payment_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    existing = payments_collection.find_one({"id": payment_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    
    payments_collection.update_one(
        {"id": payment_id},
        {"$set": {"status": "completed"}}
    )
    
    return {"message": "Платеж отмечен как полученный", "id": payment_id}
