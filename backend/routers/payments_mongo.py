from fastapi import APIRouter, Depends, HTTPException, Query, Header
from database.base import get_db, payments_collection
from routers.auth_mongo import get_current_user
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
import uuid

router = APIRouter(prefix="/payments")

class PaymentBase(BaseModel):
    invoice_id: str
    client_id: str
    project_id: Optional[str] = None
    amount: float
    date_expected: date
    date_received: Optional[date] = None
    status: str = "pending"
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(PaymentBase):
    invoice_id: Optional[str] = None
    client_id: Optional[str] = None
    amount: Optional[float] = None
    date_expected: Optional[date] = None
    status: Optional[str] = None

class PaymentRead(BaseModel):
    id: str
    invoice_id: str
    client_id: str
    tenant_id: Optional[str] = None
    project_id: Optional[str] = None
    amount: float
    date_expected: datetime
    date_received: Optional[datetime] = None
    status: str
    payment_method: Optional[str] = None
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
    db = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    query = {}
    if x_company_id:
        query["tenant_id"] = x_company_id
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
    db = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    query = {"status": "pending"}
    if x_company_id:
        query["tenant_id"] = x_company_id
    
    payments = list(payments_collection.find(query))
    for payment in payments:
        payment.pop("_id", None)
    return payments

@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(
    payment_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    query = {"id": payment_id}
    if x_company_id:
        query["tenant_id"] = x_company_id
    
    payment = payments_collection.find_one(query)
    if not payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    
    payment.pop("_id", None)
    return payment

@router.post("/", response_model=PaymentRead, status_code=201)
async def create_payment(
    payment_data: PaymentCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID header is required")
    
    payment_dict = payment_data.dict()
    
    if payment_dict.get("date_expected") and not isinstance(payment_dict["date_expected"], datetime):
        payment_dict["date_expected"] = datetime.combine(payment_dict["date_expected"], datetime.min.time())
    if payment_dict.get("date_received") and not isinstance(payment_dict["date_received"], datetime):
        payment_dict["date_received"] = datetime.combine(payment_dict["date_received"], datetime.min.time())
    
    payment_dict.update({
        "id": str(uuid.uuid4()),
        "tenant_id": x_company_id,
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
    db = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    query = {"id": payment_id}
    if x_company_id:
        query["tenant_id"] = x_company_id
    
    existing = payments_collection.find_one(query)
    if not existing:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    
    update_data = payment_data.dict(exclude_unset=True)
    
    if update_data.get("date_expected") and not isinstance(update_data["date_expected"], datetime):
        update_data["date_expected"] = datetime.combine(update_data["date_expected"], datetime.min.time())
    if update_data.get("date_received") and not isinstance(update_data["date_received"], datetime):
        update_data["date_received"] = datetime.combine(update_data["date_received"], datetime.min.time())
    
    payments_collection.update_one(query, {"$set": update_data})
    updated_payment = payments_collection.find_one(query)
    updated_payment.pop("_id", None)
    return updated_payment

@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    query = {"id": payment_id}
    if x_company_id:
        query["tenant_id"] = x_company_id
    
    result = payments_collection.delete_one(query)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    
    return {"message": "Платеж успешно удален", "id": payment_id}

@router.post("/{payment_id}/mark-received")
async def mark_payment_received(
    payment_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    query = {"id": payment_id}
    if x_company_id:
        query["tenant_id"] = x_company_id
    
    payment = payments_collection.find_one(query)
    if not payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    
    payments_collection.update_one(
        query,
        {"$set": {"status": "received", "date_received": datetime.utcnow()}}
    )
    
    return {"message": "Платеж отмечен как полученный"}
