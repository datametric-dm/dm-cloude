from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.base import get_db
from models.payment import Payment, PaymentStatus, PaymentType
from models.client import Client
from models.invoice import Invoice
from schemas.payment import PaymentCreate, PaymentUpdate, PaymentRead, PaymentList
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/payments")

@router.post("/", response_model=PaymentRead)
def create_payment(payment_data: PaymentCreate, db: Session = Depends(get_db)):
    """Создание нового платежа"""
    # Проверяем клиента
    client = db.query(Client).filter(Client.id == payment_data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    # Проверяем счёт (если указан)
    if payment_data.invoice_id:
        invoice = db.query(Invoice).filter(Invoice.id == payment_data.invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Счёт не найден")
    
    payment = Payment(**payment_data.dict())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

@router.get("/", response_model=PaymentList)
def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    client_id: Optional[str] = Query(None, description="Фильтр по клиенту"),
    status: Optional[PaymentStatus] = Query(None, description="Фильтр по статусу"),
    overdue_only: bool = Query(False, description="Показать только просроченные"),
    db: Session = Depends(get_db)
):
    """Получение списка платежей"""
    query = db.query(Payment)
    
    if client_id:
        query = query.filter(Payment.client_id == client_id)
    
    if status:
        query = query.filter(Payment.status == status)
    
    if overdue_only:
        query = query.filter(
            Payment.payment_date_planned < datetime.utcnow(),
            Payment.status == PaymentStatus.PLANNED
        )
    
    total = query.count()
    payments = query.order_by(Payment.payment_date_planned.desc()).offset(skip).limit(limit).all()
    
    return PaymentList(
        payments=payments,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: str, db: Session = Depends(get_db)):
    """Получение платежа по ID"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Платёж не найден")
    return payment

@router.put("/{payment_id}", response_model=PaymentRead)
def update_payment(payment_id: str, payment_data: PaymentUpdate, db: Session = Depends(get_db)):
    """Обновление платежа"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Платёж не найден")
    
    update_data = payment_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payment, field, value)
    
    # Если платёж отмечен как полученный, устанавливаем дату
    if payment_data.status == PaymentStatus.RECEIVED and not payment.payment_date_actual:
        payment.payment_date_actual = datetime.utcnow()
    
    db.commit()
    db.refresh(payment)
    return payment

@router.get("/overdue/list")
def get_overdue_payments(db: Session = Depends(get_db)):
    """Получение просроченных платежей"""
    overdue_payments = db.query(Payment).filter(
        Payment.payment_date_planned < datetime.utcnow(),
        Payment.status == PaymentStatus.PLANNED
    ).all()
    
    return {
        "overdue_payments": overdue_payments,
        "count": len(overdue_payments),
        "total_amount": sum(payment.amount for payment in overdue_payments)
    }

@router.post("/{payment_id}/mark-received")
def mark_payment_received(payment_id: str, db: Session = Depends(get_db)):
    """Отметить платёж как полученный"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Платёж не найден")
    
    payment.status = PaymentStatus.RECEIVED
    payment.payment_date_actual = datetime.utcnow()
    
    db.commit()
    db.refresh(payment)
    
    return {"message": "Платёж отмечен как полученный", "payment": payment}
