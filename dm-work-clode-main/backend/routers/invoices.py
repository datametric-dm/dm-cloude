from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.base import get_db
from models.invoice import Invoice, InvoiceItem, InvoiceStatus
from models.client import Client
from models.project import Project
from schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceRead, InvoiceList
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/invoices")

@router.post("/", response_model=InvoiceRead)
def create_invoice(invoice_data: InvoiceCreate, db: Session = Depends(get_db)):
    """Создание нового счёта"""
    # Проверяем клиента
    client = db.query(Client).filter(Client.id == invoice_data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    # Проверяем проект (если указан)
    if invoice_data.project_id:
        project = db.query(Project).filter(Project.id == invoice_data.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Создаём счёт
    invoice_dict = invoice_data.dict()
    items_data = invoice_dict.pop('items', [])
    
    invoice = Invoice(**invoice_dict)
    db.add(invoice)
    db.flush()  # Получаем ID счёта
    
    # Добавляем позиции
    for item_data in items_data:
        item = InvoiceItem(invoice_id=invoice.id, **item_data)
        db.add(item)
    
    db.commit()
    db.refresh(invoice)
    return invoice

@router.get("/", response_model=InvoiceList)
def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    client_id: Optional[str] = Query(None, description="Фильтр по клиенту"),
    status: Optional[InvoiceStatus] = Query(None, description="Фильтр по статусу"),
    overdue_only: bool = Query(False, description="Показать только просроченные"),
    db: Session = Depends(get_db)
):
    """Получение списка счетов"""
    query = db.query(Invoice)
    
    if client_id:
        query = query.filter(Invoice.client_id == client_id)
    
    if status:
        query = query.filter(Invoice.status == status)
    
    if overdue_only:
        query = query.filter(
            Invoice.date_due < datetime.utcnow(),
            Invoice.status != InvoiceStatus.PAID
        )
    
    total = query.count()
    invoices = query.order_by(Invoice.date_issued.desc()).offset(skip).limit(limit).all()
    
    return InvoiceList(
        invoices=invoices,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice(invoice_id: str, db: Session = Depends(get_db)):
    """Получение счёта по ID"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Счёт не найден")
    return invoice

@router.put("/{invoice_id}", response_model=InvoiceRead)
def update_invoice(invoice_id: str, invoice_data: InvoiceUpdate, db: Session = Depends(get_db)):
    """Обновление счёта"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Счёт не найден")
    
    update_data = invoice_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)
    
    db.commit()
    db.refresh(invoice)
    return invoice

@router.get("/overdue/list")
def get_overdue_invoices(db: Session = Depends(get_db)):
    """Получение просроченных счетов"""
    overdue_invoices = db.query(Invoice).filter(
        Invoice.date_due < datetime.utcnow(),
        Invoice.status != InvoiceStatus.PAID
    ).all()
    
    return {
        "overdue_invoices": overdue_invoices,
        "count": len(overdue_invoices),
        "total_amount": sum(invoice.total for invoice in overdue_invoices)
    }
