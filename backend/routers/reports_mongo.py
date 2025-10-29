from fastapi import APIRouter, Depends, Query
from database.base import get_db, clients_collection, projects_collection, invoices_collection, payments_collection
from routers.auth_mongo import get_current_user
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime

router = APIRouter(prefix="/reports")

class DashboardStats(BaseModel):
    total_clients: int
    active_projects: int
    total_projects: int
    total_revenue: float
    pending_revenue: float
    pending_invoices: int
    overdue_invoices: int
    overdue_payments_count: int
    overdue_amount: float
    total_payments: int

class MonthlyRevenue(BaseModel):
    month: str
    revenue: float

class ClientRevenue(BaseModel):
    client_name: str
    client_id: str
    total_revenue: float

class ProjectStatusDistribution(BaseModel):
    status: str
    count: int

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Получить статистику для дашборда"""
    
    # Подсчитываем статистику
    total_clients = clients_collection.count_documents({})
    total_projects = projects_collection.count_documents({})
    active_projects = projects_collection.count_documents({"status": {"$in": ["in_progress", "planning"]}})
    pending_invoices = invoices_collection.count_documents({"status": {"$in": ["draft", "sent"]}})
    overdue_invoices = invoices_collection.count_documents({"status": "overdue"})
    total_payments = payments_collection.count_documents({"status": "completed"})
    overdue_payments_count = payments_collection.count_documents({"status": "pending"})
    
    # Подсчитываем общую выручку из оплаченных счетов
    paid_invoices = list(invoices_collection.find({"status": "paid"}))
    total_revenue = sum(inv.get("amount", 0) for inv in paid_invoices)
    
    # Подсчитываем ожидаемую выручку из неоплаченных счетов
    pending_invoices_list = list(invoices_collection.find({"status": {"$in": ["draft", "sent"]}}))
    pending_revenue = sum(inv.get("amount", 0) for inv in pending_invoices_list)
    
    # Подсчитываем сумму просроченных платежей
    overdue_payments_list = list(payments_collection.find({"status": "pending"}))
    overdue_amount = sum(pay.get("amount", 0) for pay in overdue_payments_list)
    
    return {
        "total_clients": total_clients,
        "total_projects": total_projects,
        "active_projects": active_projects,
        "total_revenue": total_revenue,
        "pending_revenue": pending_revenue,
        "pending_invoices": pending_invoices,
        "overdue_invoices": overdue_invoices,
        "overdue_payments_count": overdue_payments_count,
        "overdue_amount": overdue_amount,
        "total_payments": total_payments
    }

@router.get("/monthly-revenue", response_model=List[MonthlyRevenue])
async def get_monthly_revenue(
    year: int = Query(default=2025),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Получить помесячную выручку"""
    
    # Получаем все оплаченные счета за указанный год
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)
    
    paid_invoices = list(invoices_collection.find({
        "status": "paid",
        "issue_date": {"$gte": start_date, "$lte": end_date}
    }))
    
    # Группируем по месяцам
    monthly_data = {}
    months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
    
    for month_name in months:
        monthly_data[month_name] = 0.0
    
    for invoice in paid_invoices:
        issue_date = invoice.get("issue_date")
        if isinstance(issue_date, datetime):
            month_name = months[issue_date.month - 1]
            monthly_data[month_name] += invoice.get("amount", 0)
    
    result = [{"month": month, "revenue": revenue} for month, revenue in monthly_data.items()]
    return result

@router.get("/client-revenue", response_model=List[ClientRevenue])
async def get_client_revenue(
    limit: int = Query(default=10, ge=1, le=50),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Получить топ клиентов по выручке"""
    
    # Получаем все оплаченные счета
    paid_invoices = list(invoices_collection.find({"status": "paid"}))
    
    # Группируем по клиентам
    client_revenue_map = {}
    
    for invoice in paid_invoices:
        client_id = invoice.get("client_id")
        amount = invoice.get("amount", 0)
        
        if client_id:
            if client_id not in client_revenue_map:
                client_revenue_map[client_id] = 0
            client_revenue_map[client_id] += amount
    
    # Получаем информацию о клиентах
    result = []
    for client_id, revenue in client_revenue_map.items():
        client = clients_collection.find_one({"id": client_id})
        if client:
            result.append({
                "client_name": client.get("name", "Без названия"),
                "client_id": client_id,
                "total_revenue": revenue
            })
    
    # Сортируем по убыванию выручки
    result.sort(key=lambda x: x["total_revenue"], reverse=True)
    
    return result[:limit]

@router.get("/project-status-distribution", response_model=List[ProjectStatusDistribution])
async def get_project_status_distribution(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Получить распределение проектов по статусам"""
    
    # Подсчитываем проекты по статусам
    statuses = ["planning", "in_progress", "completed", "cancelled"]
    status_names = {
        "planning": "Планирование",
        "in_progress": "В работе",
        "completed": "Завершен",
        "cancelled": "Отменен"
    }
    
    result = []
    for status in statuses:
        count = projects_collection.count_documents({"status": status})
        result.append({
            "status": status_names.get(status, status),
            "count": count
        })
    
    return result
