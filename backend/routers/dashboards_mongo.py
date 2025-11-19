"""
Dashboards API - Owner Dashboard and Analytics
"""
from fastapi import APIRouter, HTTPException, Header, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict

from database.base import (
    companies_collection,
    projects_collection,
    clients_collection,
    invoices_collection,
    payments_collection,
    project_stages_collection,
    user_company_roles_collection,
    work_time_records_collection,
    client_health_scores_collection,
    risks_collection
)
from routers.auth_mongo import get_current_user

router = APIRouter(tags=["dashboards"], prefix="/dashboards")


# ============= Owner Dashboard (Главный дашборд собственника) =============

@router.get("/owner")
async def get_owner_dashboard(
    period: str = Query("month", description="week, month, quarter, year"),
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Owner Dashboard - главный дашборд для собственника"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Calculate period
    now = datetime.utcnow()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "quarter":
        start_date = now - timedelta(days=90)
    else:  # year
        start_date = now - timedelta(days=365)
    
    # ===== ФИНАНСОВЫЕ МЕТРИКИ =====
    
    # MRR текущий (Monthly Recurring Revenue)
    invoices_this_month = list(invoices_collection.find({
        "tenant_id": x_company_id,
        "date_issued": {"$gte": now - timedelta(days=30), "$lte": now}
    }))
    
    current_mrr = sum(inv.get("amount", 0) for inv in invoices_this_month) / 30 * 30  # Approximate MRR
    
    # Прогноз MRR на 30 дней
    future_invoices = list(invoices_collection.find({
        "tenant_id": x_company_id,
        "date_due": {"$gte": now, "$lte": now + timedelta(days=30)},
        "status": {"$in": ["draft", "sent"]}
    }))
    
    forecast_mrr = sum(inv.get("amount", 0) for inv in future_invoices)
    
    # Факт поступлений за неделю
    week_start = now - timedelta(days=7)
    week_payments = list(payments_collection.find({
        "tenant_id": x_company_id,
        "date_received": {"$gte": week_start, "$lte": now},
        "status": "received"
    }))
    
    week_received = sum(pay.get("amount", 0) for pay in week_payments)
    
    # Планируемые поступления на следующую неделю
    next_week = now + timedelta(days=7)
    planned_next_week = list(invoices_collection.find({
        "tenant_id": x_company_id,
        "date_due": {"$gte": now, "$lte": next_week},
        "status": {"$in": ["draft", "sent"]}
    }))
    
    planned_amount_next_week = sum(inv.get("amount", 0) for inv in planned_next_week)
    
    # Просрочки
    overdue_invoices = list(invoices_collection.find({
        "tenant_id": x_company_id,
        "status": "overdue"
    }))
    
    clients_in_overdue = len(set([inv.get("client_id") for inv in overdue_invoices if inv.get("client_id")]))
    total_overdue = sum(inv.get("amount", 0) for inv in overdue_invoices)
    
    # Средний чек
    all_invoices = list(invoices_collection.find({"tenant_id": x_company_id}))
    avg_check = sum(inv.get("amount", 0) for inv in all_invoices) / len(all_invoices) if all_invoices else 0
    
    # ARPU (Average Revenue Per User/Client)
    all_clients = list(clients_collection.find({"tenant_id": x_company_id, "is_active": True}))
    arpu = current_mrr / len(all_clients) if all_clients else 0
    
    # ===== ПРОЕКТНЫЕ МЕТРИКИ =====
    
    # Активные проекты
    active_projects = list(projects_collection.find({
        "tenant_id": x_company_id,
        "status": {"$in": ["planning", "in_progress", "review"]}
    }))
    
    total_active_projects = len(active_projects)
    
    # Проекты в зоне риска
    project_risks = list(risks_collection.find({
        "tenant_id": x_company_id,
        "category": {"$in": ["project_delay", "low_velocity"]},
        "status": {"$in": ["detected", "acknowledged"]}
    }))
    
    projects_at_risk = len(set([r.get("project_id") for r in project_risks if r.get("project_id")]))
    
    # Проекты без движения >7 дней
    all_stages = list(project_stages_collection.find({
        "tenant_id": x_company_id,
        "status": {"$in": ["not_started", "in_progress"]}
    }))
    
    stuck_projects = set()
    for stage in all_stages:
        last_activity = stage.get("last_activity_at", stage.get("created_at", now))
        days_inactive = (now - last_activity).days
        if days_inactive > 7:
            stuck_projects.add(stage.get("project_id"))
    
    projects_stuck = len(stuck_projects)
    
    # Средняя скорость выполнения задач
    completed_stages = [s for s in all_stages if s.get("status") == "completed"]
    avg_completion_speed = len(completed_stages) / len(all_stages) if all_stages else 0
    
    # ===== КОМАНДА =====
    
    # Нагрузка по отделам
    team_members = list(user_company_roles_collection.find({
        "company_id": x_company_id,
        "is_active": True
    }))
    
    # Нагрузка по менеджерам
    week_time_records = list(work_time_records_collection.find({
        "tenant_id": x_company_id,
        "date": {"$gte": week_start, "$lte": now}
    }))
    
    load_by_user = defaultdict(float)
    for rec in week_time_records:
        load_by_user[rec.get("user_id")] += rec.get("hours", 0)
    
    # TOP менеджеры по эффективности (часы работы)
    top_performers = sorted(load_by_user.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Перегруженные менеджеры (>90% capacity)
    overloaded_count = len([uid for uid, hours in load_by_user.items() if hours > 36])
    
    # ===== РИСКИ =====
    
    # Клиенты с вероятностью оттока
    high_churn_risks = list(risks_collection.find({
        "tenant_id": x_company_id,
        "category": "client_churn",
        "level": {"$in": ["high", "critical"]},
        "status": {"$in": ["detected", "acknowledged"]}
    }))
    
    clients_at_churn_risk = len(high_churn_risks)
    
    # Предстоящие дедлайны (в ближайшие 7 дней)
    upcoming_deadlines = list(project_stages_collection.find({
        "tenant_id": x_company_id,
        "deadline": {"$gte": now, "$lte": next_week},
        "status": {"$ne": "completed"}
    }))
    
    # Текущие проблемы
    all_risks = list(risks_collection.find({
        "tenant_id": x_company_id,
        "status": {"$in": ["detected", "acknowledged"]}
    }))
    
    critical_risks = len([r for r in all_risks if r.get("level") == "critical"])
    high_risks = len([r for r in all_risks if r.get("level") == "high"])
    
    # Рекомендации AI
    ai_recommendations = []
    if clients_at_churn_risk > 0:
        ai_recommendations.append(f"⚠️ {clients_at_churn_risk} клиентов в зоне риска оттока - требуется внимание")
    if projects_stuck > 0:
        ai_recommendations.append(f"🚨 {projects_stuck} проектов без активности >7 дней")
    if overloaded_count > 0:
        ai_recommendations.append(f"👥 {overloaded_count} сотрудников перегружены")
    if len(overdue_invoices) > 5:
        ai_recommendations.append(f"💰 {len(overdue_invoices)} просроченных счетов - срочно!")
    
    # Build dashboard
    dashboard = {
        "period": period,
        "generated_at": now.isoformat(),
        
        # Финансовые
        "financial": {
            "current_mrr": current_mrr,
            "forecast_mrr": forecast_mrr,
            "mrr_growth": ((forecast_mrr - current_mrr) / current_mrr * 100) if current_mrr > 0 else 0,
            "week_received": week_received,
            "planned_next_week": planned_amount_next_week,
            "clients_in_overdue": clients_in_overdue,
            "total_overdue": total_overdue,
            "avg_check": avg_check,
            "arpu": arpu
        },
        
        # Проектные
        "projects": {
            "total_active": total_active_projects,
            "at_risk": projects_at_risk,
            "stuck": projects_stuck,
            "avg_completion_rate": avg_completion_speed * 100,
            "upcoming_deadlines": len(upcoming_deadlines)
        },
        
        # Команда
        "team": {
            "total_members": len(team_members),
            "top_performers": [{"user_id": uid, "hours": hours} for uid, hours in top_performers],
            "overloaded_count": overloaded_count
        },
        
        # Риски
        "risks": {
            "clients_churn_risk": clients_at_churn_risk,
            "upcoming_deadlines": len(upcoming_deadlines),
            "critical_risks": critical_risks,
            "high_risks": high_risks,
            "total_active_risks": len(all_risks)
        },
        
        # AI Рекомендации
        "ai_recommendations": ai_recommendations
    }
    
    return {"dashboard": dashboard}


# ============= Project Analytics Dashboard =============

@router.get("/project-analytics")
async def get_project_analytics(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Project Analytics Dashboard"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Все проекты
    all_projects = list(projects_collection.find({"tenant_id": x_company_id}))
    
    # Воронка проектов (по статусам)
    funnel = defaultdict(int)
    for proj in all_projects:
        status = proj.get("status", "unknown")
        funnel[status] += 1
    
    # Конверсия по этапам
    total = len(all_projects)
    conversions = {}
    if total > 0:
        for status, count in funnel.items():
            conversions[status] = (count / total) * 100
    
    # Средняя длительность этапа
    all_stages = list(project_stages_collection.find({"tenant_id": x_company_id}))
    
    completed_stages = [s for s in all_stages if s.get("status") == "completed"]
    
    stage_durations = []
    for stage in completed_stages:
        if stage.get("start_date") and stage.get("end_date"):
            duration = (stage["end_date"] - stage["start_date"]).days
            stage_durations.append(duration)
    
    avg_stage_duration = sum(stage_durations) / len(stage_durations) if stage_durations else 0
    
    # Доля зависших проектов
    now = datetime.utcnow()
    stuck_count = 0
    for stage in all_stages:
        last_activity = stage.get("last_activity_at", stage.get("created_at", now))
        if (now - last_activity).days > 7 and stage.get("status") in ["not_started", "in_progress"]:
            stuck_count += 1
    
    stuck_percentage = (stuck_count / len(all_stages) * 100) if all_stages else 0
    
    # ТОП проблемных проектов
    problem_projects = list(risks_collection.find({
        "tenant_id": x_company_id,
        "category": {"$in": ["project_delay", "low_velocity"]},
        "status": {"$in": ["detected", "acknowledged"]}
    }).limit(10))
    
    for risk in problem_projects:
        risk.pop("_id", None)
    
    # Прогноз окончания проектов
    active_projects = [p for p in all_projects if p.get("status") in ["in_progress", "planning"]]
    
    analytics = {
        "total_projects": len(all_projects),
        "funnel": dict(funnel),
        "conversions": conversions,
        "avg_stage_duration_days": avg_stage_duration,
        "stuck_percentage": stuck_percentage,
        "problem_projects": problem_projects,
        "active_projects_count": len(active_projects),
        "generated_at": datetime.utcnow().isoformat()
    }
    
    return {"analytics": analytics}


# ============= Financial Dashboard =============

@router.get("/financial")
async def get_financial_dashboard(
    period: str = Query("month", description="week, month, quarter"),
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Financial Dashboard"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    now = datetime.utcnow()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:  # quarter
        start_date = now - timedelta(days=90)
    
    # План/Факт платежей
    planned_invoices = list(invoices_collection.find({
        "tenant_id": x_company_id,
        "date_due": {"$gte": start_date, "$lte": now}
    }))
    
    planned_total = sum(inv.get("amount", 0) for inv in planned_invoices)
    
    actual_payments = list(payments_collection.find({
        "tenant_id": x_company_id,
        "date_received": {"$gte": start_date, "$lte": now},
        "status": "received"
    }))
    
    actual_total = sum(pay.get("amount", 0) for pay in actual_payments)
    
    # Просрочки
    overdue_invoices = list(invoices_collection.find({
        "tenant_id": x_company_id,
        "status": "overdue"
    }))
    
    overdue_total = sum(inv.get("amount", 0) for inv in overdue_invoices)
    
    # Динамика MRR (по месяцам за последние 6 месяцев)
    mrr_dynamics = []
    for i in range(6):
        month_start = now - timedelta(days=30 * (i + 1))
        month_end = now - timedelta(days=30 * i)
        
        month_invoices = list(invoices_collection.find({
            "tenant_id": x_company_id,
            "date_issued": {"$gte": month_start, "$lte": month_end}
        }))
        
        month_revenue = sum(inv.get("amount", 0) for inv in month_invoices)
        mrr_dynamics.append({
            "month": f"Month -{i}",
            "revenue": month_revenue
        })
    
    mrr_dynamics.reverse()
    
    # Прогноз кассовых разрывов
    future_weeks = []
    balance = actual_total - planned_total  # Simplified
    
    for week in range(4):
        week_start = now + timedelta(weeks=week)
        week_end = week_start + timedelta(days=7)
        
        week_income = sum(
            inv.get("amount", 0) 
            for inv in invoices_collection.find({
                "tenant_id": x_company_id,
                "date_due": {"$gte": week_start, "$lte": week_end}
            })
        )
        
        balance += week_income
        
        future_weeks.append({
            "week": week + 1,
            "projected_balance": balance,
            "risk": "high" if balance < 0 else "low"
        })
    
    dashboard = {
        "period": period,
        "planned_income": planned_total,
        "actual_income": actual_total,
        "variance": actual_total - planned_total,
        "variance_percentage": ((actual_total - planned_total) / planned_total * 100) if planned_total > 0 else 0,
        "overdue_count": len(overdue_invoices),
        "overdue_amount": overdue_total,
        "mrr_dynamics": mrr_dynamics,
        "cash_flow_forecast": future_weeks,
        "generated_at": now.isoformat()
    }
    
    return {"dashboard": dashboard}


# ============= Team Load Dashboard =============

@router.get("/team-load")
async def get_team_load_dashboard(
    period: str = Query("week", description="week, month"),
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Team Load Dashboard"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    now = datetime.utcnow()
    if period == "week":
        start_date = now - timedelta(days=7)
        capacity_per_user = 40
    else:  # month
        start_date = now - timedelta(days=30)
        capacity_per_user = 160
    
    # Получить всех членов команды
    team_members = list(user_company_roles_collection.find({
        "company_id": x_company_id,
        "is_active": True
    }))
    
    # Загрузка по сотрудникам
    load_data = []
    total_capacity = 0
    total_actual = 0
    
    for member in team_members:
        user_id = member.get("user_id")
        
        time_records = list(work_time_records_collection.find({
            "tenant_id": x_company_id,
            "user_id": user_id,
            "date": {"$gte": start_date, "$lte": now}
        }))
        
        actual_hours = sum(rec.get("hours", 0) for rec in time_records)
        load_percentage = (actual_hours / capacity_per_user * 100) if capacity_per_user > 0 else 0
        
        status = "underloaded" if load_percentage < 60 else "normal" if load_percentage <= 90 else "overloaded" if load_percentage <= 110 else "critical"
        
        load_data.append({
            "user_id": user_id,
            "actual_hours": actual_hours,
            "capacity_hours": capacity_per_user,
            "load_percentage": load_percentage,
            "status": status
        })
        
        total_capacity += capacity_per_user
        total_actual += actual_hours
    
    # Группировка по статусам
    underloaded = [m for m in load_data if m["status"] == "underloaded"]
    normal = [m for m in load_data if m["status"] == "normal"]
    overloaded = [m for m in load_data if m["status"] == "overloaded"]
    critical = [m for m in load_data if m["status"] == "critical"]
    
    dashboard = {
        "period": period,
        "team_size": len(team_members),
        "total_capacity_hours": total_capacity,
        "total_actual_hours": total_actual,
        "average_load_percentage": (total_actual / total_capacity * 100) if total_capacity > 0 else 0,
        "load_distribution": {
            "underloaded": len(underloaded),
            "normal": len(normal),
            "overloaded": len(overloaded),
            "critical": len(critical)
        },
        "members": load_data,
        "generated_at": now.isoformat()
    }
    
    return {"dashboard": dashboard}


# ============= Client 360 Dashboard =============

@router.get("/client-360")
async def get_client_360_dashboard(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Client 360 Dashboard - overview of all clients"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Все клиенты
    all_clients = list(clients_collection.find({
        "tenant_id": x_company_id,
        "is_active": True
    }))
    
    # Health scores
    health_scores = list(client_health_scores_collection.find({
        "tenant_id": x_company_id
    }))
    
    # Распределение по health status
    health_distribution = defaultdict(int)
    for score in health_scores:
        status = score.get("status", "fair")
        health_distribution[status] += 1
    
    # Клиенты по тегам
    tags_distribution = defaultdict(int)
    for score in health_scores:
        for tag in score.get("tags", []):
            tags_distribution[tag] += 1
    
    # ТОП клиенты по revenue
    top_clients = []
    for client in all_clients:
        client_invoices = list(invoices_collection.find({
            "client_id": client.get("id"),
            "tenant_id": x_company_id
        }))
        
        total_revenue = sum(inv.get("amount", 0) for inv in client_invoices)
        
        top_clients.append({
            "client_id": client.get("id"),
            "client_name": client.get("name"),
            "total_revenue": total_revenue
        })
    
    top_clients = sorted(top_clients, key=lambda x: x["total_revenue"], reverse=True)[:10]
    
    # Clients at risk
    at_risk = len([s for s in health_scores if "churn_risk" in s.get("tags", [])])
    vip_clients = len([s for s in health_scores if "vip" in s.get("tags", [])])
    
    dashboard = {
        "total_clients": len(all_clients),
        "health_distribution": dict(health_distribution),
        "tags_distribution": dict(tags_distribution),
        "top_clients": top_clients,
        "at_risk_count": at_risk,
        "vip_count": vip_clients,
        "generated_at": datetime.utcnow().isoformat()
    }
    
    return {"dashboard": dashboard}
