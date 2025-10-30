from fastapi import APIRouter, Depends, Query, HTTPException
from database.base import get_db, clients_collection, projects_collection, invoices_collection, payments_collection
from routers.auth_mongo import get_current_user
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
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
        "date_issued": {"$gte": start_date, "$lte": end_date}
    }))
    
    # Группируем по месяцам
    monthly_data = {}
    months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
    
    for month_name in months:
        monthly_data[month_name] = 0.0
    
    for invoice in paid_invoices:
        date_issued = invoice.get("date_issued")
        if isinstance(date_issued, datetime):
            month_name = months[date_issued.month - 1]
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


# Схема для отчета по проекту
class ProjectReport(BaseModel):
    project_id: str
    project_name: str
    monthly_revenue: float  # Месячная выручка
    average_check: float  # Средний чек
    pending_payments: float  # Ожидание платежей
    overdue_payments: float  # Просрочено платежей
    total_invoices: int  # Всего счетов
    paid_invoices: int  # Оплаченных счетов
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

from typing import Optional

@router.get("/project/{project_id}", response_model=ProjectReport)
async def get_project_report(
    project_id: str,
    period_months: int = Query(default=1, ge=1, le=12),  # Период в месяцах
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Получить отчет по конкретному проекту"""
    from datetime import datetime, timedelta
    
    # Проверяем существование проекта
    project = projects_collection.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Определяем период
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=30 * period_months)
    
    # Получаем счета по проекту за период
    invoices = list(invoices_collection.find({
        "project_id": project_id,
        "created_at": {"$gte": period_start, "$lte": period_end}
    }))
    
    # Получаем платежи по проекту за период
    payments = list(payments_collection.find({
        "project_id": project_id,
        "payment_date": {"$gte": period_start, "$lte": period_end}
    }))
    
    # Рассчитываем метрики
    total_invoices = len(invoices)
    paid_invoices = len([inv for inv in invoices if inv.get("status") == "paid"])
    
    # Месячная выручка (из оплаченных счетов)
    paid_amount = sum(inv.get("amount", 0) for inv in invoices if inv.get("status") == "paid")
    monthly_revenue = paid_amount / period_months if period_months > 0 else paid_amount
    
    # Средний чек
    average_check = paid_amount / paid_invoices if paid_invoices > 0 else 0
    
    # Ожидание платежей (неоплаченные счета)
    pending_payments = sum(inv.get("amount", 0) for inv in invoices if inv.get("status") in ["draft", "sent"])
    
    # Просрочено платежей
    overdue_payments = sum(inv.get("amount", 0) for inv in invoices if inv.get("status") == "overdue")
    
    return {
        "project_id": project_id,
        "project_name": project.get("name", ""),
        "monthly_revenue": monthly_revenue,
        "average_check": average_check,
        "pending_payments": pending_payments,
        "overdue_payments": overdue_payments,
        "total_invoices": total_invoices,
        "paid_invoices": paid_invoices,
        "period_start": period_start,
        "period_end": period_end
    }

# Схема для сводного отчета
class SummaryReport(BaseModel):
    total_projects: int
    total_revenue: float
    monthly_revenue: float
    average_check: float
    pending_payments: float
    overdue_payments: float
    total_invoices: int
    paid_invoices: int
    projects_by_manager: Dict[str, int]  # Распределение проектов по менеджерам

@router.get("/summary", response_model=SummaryReport)
async def get_summary_report(
    period_months: int = Query(default=1, ge=1, le=12),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Получить сводный отчет по всем проектам"""
    from datetime import datetime, timedelta
    
    # Определяем период
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=30 * period_months)
    
    # Получаем все проекты
    all_projects = list(projects_collection.find({}))
    total_projects = len(all_projects)
    
    # Получаем все счета за период
    all_invoices = list(invoices_collection.find({
        "created_at": {"$gte": period_start, "$lte": period_end}
    }))
    
    total_invoices = len(all_invoices)
    paid_invoices = len([inv for inv in all_invoices if inv.get("status") == "paid"])
    
    # Рассчитываем метрики
    total_revenue = sum(inv.get("amount", 0) for inv in all_invoices if inv.get("status") == "paid")
    monthly_revenue = total_revenue / period_months if period_months > 0 else total_revenue
    average_check = total_revenue / paid_invoices if paid_invoices > 0 else 0
    pending_payments = sum(inv.get("amount", 0) for inv in all_invoices if inv.get("status") in ["draft", "sent"])
    overdue_payments = sum(inv.get("amount", 0) for inv in all_invoices if inv.get("status") == "overdue")
    
    # Распределение проектов по менеджерам
    projects_by_manager = {}
    for project in all_projects:
        manager = project.get("project_manager", "Не назначен")
        projects_by_manager[manager] = projects_by_manager.get(manager, 0) + 1
    
    return {
        "total_projects": total_projects,
        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
        "average_check": average_check,
        "pending_payments": pending_payments,
        "overdue_payments": overdue_payments,
        "total_invoices": total_invoices,
        "paid_invoices": paid_invoices,
        "projects_by_manager": projects_by_manager
    }

# Схема для отчета по менеджеру
class ManagerReport(BaseModel):
    manager_name: str
    total_projects: int
    total_revenue: float
    monthly_revenue: float
    average_check: float
    pending_payments: float
    overdue_payments: float
    total_invoices: int
    paid_invoices: int
    projects: List[Dict[str, Any]]  # Список проектов с кратким описанием

@router.get("/by-manager/{manager_name}", response_model=ManagerReport)
async def get_manager_report(
    manager_name: str,
    period_months: int = Query(default=1, ge=1, le=12),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Получить отчет по проект-менеджеру"""
    from datetime import datetime, timedelta
    
    # Определяем период
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=30 * period_months)
    
    # Получаем проекты менеджера
    manager_projects = list(projects_collection.find({"project_manager": manager_name}))
    total_projects = len(manager_projects)
    
    if total_projects == 0:
        return {
            "manager_name": manager_name,
            "total_projects": 0,
            "total_revenue": 0,
            "monthly_revenue": 0,
            "average_check": 0,
            "pending_payments": 0,
            "overdue_payments": 0,
            "total_invoices": 0,
            "paid_invoices": 0,
            "projects": []
        }
    
    # Получаем ID проектов менеджера
    project_ids = [p.get("id") for p in manager_projects]
    
    # Получаем счета по проектам менеджера за период
    manager_invoices = list(invoices_collection.find({
        "project_id": {"$in": project_ids},
        "created_at": {"$gte": period_start, "$lte": period_end}
    }))
    
    total_invoices = len(manager_invoices)
    paid_invoices = len([inv for inv in manager_invoices if inv.get("status") == "paid"])
    
    # Рассчитываем метрики
    total_revenue = sum(inv.get("amount", 0) for inv in manager_invoices if inv.get("status") == "paid")
    monthly_revenue = total_revenue / period_months if period_months > 0 else total_revenue
    average_check = total_revenue / paid_invoices if paid_invoices > 0 else 0
    pending_payments = sum(inv.get("amount", 0) for inv in manager_invoices if inv.get("status") in ["draft", "sent"])
    overdue_payments = sum(inv.get("amount", 0) for inv in manager_invoices if inv.get("status") == "overdue")
    
    # Формируем информацию о проектах
    projects_info = []
    for project in manager_projects:
        # Считаем выручку по проекту
        project_invoices = [inv for inv in manager_invoices if inv.get("project_id") == project.get("id")]
        project_revenue = sum(inv.get("amount", 0) for inv in project_invoices if inv.get("status") == "paid")
        
        projects_info.append({
            "id": project.get("id"),
            "name": project.get("name"),
            "status": project.get("status"),
            "budget": project.get("budget", 0),
            "revenue": project_revenue
        })
    
    return {
        "manager_name": manager_name,
        "total_projects": total_projects,
        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
        "average_check": average_check,
        "pending_payments": pending_payments,
        "overdue_payments": overdue_payments,
        "total_invoices": total_invoices,
        "paid_invoices": paid_invoices,
        "projects": projects_info
    }

