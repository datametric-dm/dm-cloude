from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from database.base import get_db
from models.client import Client
from models.project import Project, ProjectStatus
from models.invoice import Invoice, InvoiceStatus
from models.payment import Payment, PaymentStatus
from typing import Optional
from datetime import datetime, timedelta
import calendar

router = APIRouter(prefix="/reports")

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Получение основных метрик для дашборда"""
    # Общая статистика
    total_clients = db.query(Client).filter(Client.is_active == True).count()
    total_projects = db.query(Project).filter(Project.is_active == True).count()
    active_projects = db.query(Project).filter(
        Project.is_active == True,
        Project.status.in_([ProjectStatus.PLANNING, ProjectStatus.IN_PROGRESS])
    ).count()
    
    # Финансовая статистика
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == PaymentStatus.RECEIVED
    ).scalar() or 0
    
    pending_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == PaymentStatus.PLANNED
    ).scalar() or 0
    
    overdue_payments = db.query(Payment).filter(
        Payment.payment_date_planned < datetime.utcnow(),
        Payment.status == PaymentStatus.PLANNED
    ).count()
    
    overdue_amount = db.query(func.sum(Payment.amount)).filter(
        Payment.payment_date_planned < datetime.utcnow(),
        Payment.status == PaymentStatus.PLANNED
    ).scalar() or 0
    
    # Счета
    unpaid_invoices = db.query(Invoice).filter(
        Invoice.status != InvoiceStatus.PAID
    ).count()
    
    return {
        "total_clients": total_clients,
        "total_projects": total_projects,
        "active_projects": active_projects,
        "total_revenue": total_revenue,
        "pending_revenue": pending_revenue,
        "overdue_payments_count": overdue_payments,
        "overdue_amount": overdue_amount,
        "unpaid_invoices": unpaid_invoices
    }

@router.get("/monthly-revenue")
def get_monthly_revenue(
    year: int = Query(datetime.now().year, description="Год для отчёта"),
    db: Session = Depends(get_db)
):
    """Месячная выручка"""
    monthly_data = []
    
    for month in range(1, 13):
        revenue = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.status == PaymentStatus.RECEIVED,
                extract('year', Payment.payment_date_actual) == year,
                extract('month', Payment.payment_date_actual) == month
            )
        ).scalar() or 0
        
        monthly_data.append({
            "month": month,
            "month_name": calendar.month_name[month],
            "revenue": revenue
        })
    
    return {"year": year, "monthly_revenue": monthly_data}

@router.get("/project-status-distribution")
def get_project_status_distribution(db: Session = Depends(get_db)):
    """Распределение проектов по статусам"""
    status_counts = db.query(
        Project.status,
        func.count(Project.id).label('count')
    ).filter(Project.is_active == True).group_by(Project.status).all()
    
    distribution = []
    for status, count in status_counts:
        distribution.append({
            "status": status.value,
            "count": count
        })
    
    return {"distribution": distribution}

@router.get("/client-revenue")
def get_client_revenue(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Топ клиентов по выручке"""
    client_revenue = db.query(
        Client.id,
        Client.name,
        Client.company,
        func.sum(Payment.amount).label('total_revenue')
    ).join(Payment, Client.id == Payment.client_id).filter(
        Payment.status == PaymentStatus.RECEIVED
    ).group_by(Client.id, Client.name, Client.company).order_by(
        func.sum(Payment.amount).desc()
    ).offset(skip).limit(limit).all()
    
    result = []
    for client_id, name, company, revenue in client_revenue:
        result.append({
            "client_id": client_id,
            "name": name,
            "company": company,
            "total_revenue": revenue
        })
    
    return {"client_revenue": result}

@router.get("/overdue-summary")
def get_overdue_summary(db: Session = Depends(get_db)):
    """Сводка по просрочкам"""
    # Просроченные платежи
    overdue_payments = db.query(
        Payment.id,
        Payment.amount,
        Payment.payment_date_planned,
        Client.name.label('client_name'),
        Client.company.label('client_company')
    ).join(Client, Payment.client_id == Client.id).filter(
        Payment.payment_date_planned < datetime.utcnow(),
        Payment.status == PaymentStatus.PLANNED
    ).order_by(Payment.payment_date_planned.asc()).all()
    
    # Просроченные счета
    overdue_invoices = db.query(
        Invoice.id,
        Invoice.number,
        Invoice.total,
        Invoice.date_due,
        Client.name.label('client_name'),
        Client.company.label('client_company')
    ).join(Client, Invoice.client_id == Client.id).filter(
        Invoice.date_due < datetime.utcnow(),
        Invoice.status != InvoiceStatus.PAID
    ).order_by(Invoice.date_due.asc()).all()
    
    return {
        "overdue_payments": [
            {
                "id": p.id,
                "amount": p.amount,
                "planned_date": p.payment_date_planned,
                "days_overdue": (datetime.utcnow() - p.payment_date_planned).days,
                "client_name": p.client_name,
                "client_company": p.client_company
            }
            for p in overdue_payments
        ],
        "overdue_invoices": [
            {
                "id": i.id,
                "number": i.number,
                "total": i.total,
                "due_date": i.date_due,
                "days_overdue": (datetime.utcnow() - i.date_due).days,
                "client_name": i.client_name,
                "client_company": i.client_company
            }
            for i in overdue_invoices
        ]
    }
