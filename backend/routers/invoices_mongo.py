from fastapi import APIRouter, Depends, HTTPException, Query
from database.base import get_db, invoices_collection
from routers.auth_mongo import get_current_user
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
import uuid

router = APIRouter(prefix="/invoices")

class InvoiceBase(BaseModel):
    project_id: str
    client_id: str
    number: str
    amount: float
    status: str = "draft"  # draft, sent, paid, overdue, cancelled
    date_issued: date
    date_due: date
    description: Optional[str] = None
    notes: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(InvoiceBase):
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    number: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    date_issued: Optional[date] = None
    date_due: Optional[date] = None

class InvoiceRead(BaseModel):
    id: str
    project_id: str
    client_id: str
    number: str
    amount: float
    status: str = "draft"
    date_issued: datetime
    date_due: datetime
    description: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

class InvoiceListResponse(BaseModel):
    invoices: List[InvoiceRead]
    total: int

@router.get("/", response_model=InvoiceListResponse)
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    query = {}
    if status:
        query["status"] = status
    
    invoices = list(invoices_collection.find(query).skip(skip).limit(limit))
    total = invoices_collection.count_documents(query)
    
    for invoice in invoices:
        invoice.pop("_id", None)
    return {"invoices": invoices, "total": total}

@router.get("/overdue/list", response_model=List[InvoiceRead])
async def get_overdue_invoices(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    invoices = list(invoices_collection.find({"status": "overdue"}))
    for invoice in invoices:
        invoice.pop("_id", None)
    return invoices

@router.get("/{invoice_id}", response_model=InvoiceRead)
async def get_invoice(
    invoice_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    invoice = invoices_collection.find_one({"id": invoice_id})
    if not invoice:
        raise HTTPException(status_code=404, detail="Счет не найден")
    invoice.pop("_id", None)
    return invoice

@router.post("/", response_model=InvoiceRead, status_code=201)
async def create_invoice(
    invoice_data: InvoiceCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    invoice_dict = invoice_data.dict()
    
    if invoice_dict.get("date_issued") and not isinstance(invoice_dict["date_issued"], datetime):
        invoice_dict["date_issued"] = datetime.combine(invoice_dict["date_issued"], datetime.min.time())
    if invoice_dict.get("date_due") and not isinstance(invoice_dict["date_due"], datetime):
        invoice_dict["date_due"] = datetime.combine(invoice_dict["date_due"], datetime.min.time())
    
    invoice_dict.update({
        "id": str(uuid.uuid4()),
        "created_at": datetime.utcnow()
    })
    
    invoices_collection.insert_one(invoice_dict)
    invoice_dict.pop("_id", None)
    return invoice_dict

@router.put("/{invoice_id}", response_model=InvoiceRead)
async def update_invoice(
    invoice_id: str,
    invoice_data: InvoiceUpdate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    existing = invoices_collection.find_one({"id": invoice_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Счет не найден")
    
    update_data = invoice_data.dict(exclude_unset=True)
    
    if update_data.get("date_issued") and not isinstance(update_data["date_issued"], datetime):
        update_data["date_issued"] = datetime.combine(update_data["date_issued"], datetime.min.time())
    if update_data.get("date_due") and not isinstance(update_data["date_due"], datetime):
        update_data["date_due"] = datetime.combine(update_data["date_due"], datetime.min.time())
    
    invoices_collection.update_one({"id": invoice_id}, {"$set": update_data})
    
    updated_invoice = invoices_collection.find_one({"id": invoice_id})
    updated_invoice.pop("_id", None)
    return updated_invoice

@router.delete("/{invoice_id}")
async def delete_invoice(
    invoice_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    result = invoices_collection.delete_one({"id": invoice_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Счет не найден")
    return {"message": "Счет успешно удален", "id": invoice_id}
