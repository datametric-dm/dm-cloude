"""
Team Load API - workload tracking and forecasting
"""
from fastapi import APIRouter, HTTPException, Header, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import uuid4

from database.base import (
    work_time_records_collection,
    user_workloads_collection,
    department_workloads_collection,
    task_assignments_collection,
    workload_forecasts_collection,
    user_company_roles_collection,
    project_stages_collection,
    projects_collection
)
from routers.auth_mongo import get_current_user

router = APIRouter(tags=["team-load"], prefix="/team-load")


# ============= Work Time Records =============

class WorkTimeCreate(BaseModel):
    user_id: str
    project_id: Optional[str] = None
    stage_id: Optional[str] = None
    date: datetime
    hours: float
    description: Optional[str] = None
    is_billable: bool = True


@router.post("/time-records")
async def create_time_record(
    record_data: WorkTimeCreate,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """Create work time record"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    record_dict = record_data.dict()
    record_dict.update({
        "id": uuid4().hex,
        "tenant_id": x_company_id,
        "is_overtime": record_data.hours > 8,
        "created_at": datetime.utcnow(),
        "created_by": x_user_id
    })
    
    work_time_records_collection.insert_one(record_dict)
    record_dict.pop("_id", None)
    
    return {"message": "Time record created", "record": record_dict}


@router.get("/time-records")
async def get_time_records(
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get work time records"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    query = {"tenant_id": x_company_id}
    if user_id:
        query["user_id"] = user_id
    if project_id:
        query["project_id"] = project_id
    
    if start_date and end_date:
        query["date"] = {
            "$gte": datetime.fromisoformat(start_date),
            "$lte": datetime.fromisoformat(end_date)
        }
    
    records = list(work_time_records_collection.find(query).sort("date", -1))
    for rec in records:
        rec.pop("_id", None)
    
    return {"records": records, "count": len(records)}


# ============= User Workload =============

@router.get("/users/{user_id}/workload")
async def get_user_workload(
    user_id: str,
    period: str = Query("week", description="week, month"),
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get user workload"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Calculate period
    now = datetime.utcnow()
    if period == "week":
        period_start = now - timedelta(days=7)
    else:  # month
        period_start = now - timedelta(days=30)
    
    # Get time records
    time_records = list(work_time_records_collection.find({
        "tenant_id": x_company_id,
        "user_id": user_id,
        "date": {"$gte": period_start, "$lte": now}
    }))
    
    # Calculate totals
    total_hours = sum(rec.get("hours", 0) for rec in time_records)
    billable_hours = sum(rec.get("hours", 0) for rec in time_records if rec.get("is_billable"))
    overtime_hours = sum(rec.get("hours", 0) for rec in time_records if rec.get("is_overtime"))
    
    # Get active projects
    active_projects = list(set([rec.get("project_id") for rec in time_records if rec.get("project_id")]))
    
    # Calculate capacity (40 hours/week)
    weeks = (now - period_start).days / 7
    total_capacity = weeks * 40
    
    load_percentage = (total_hours / total_capacity * 100) if total_capacity > 0 else 0
    
    # Determine status
    if load_percentage < 60:
        status = "underloaded"
    elif load_percentage <= 90:
        status = "normal"
    elif load_percentage <= 110:
        status = "overloaded"
    else:
        status = "critical"
    
    workload = {
        "user_id": user_id,
        "period_start": period_start.isoformat(),
        "period_end": now.isoformat(),
        "total_capacity_hours": total_capacity,
        "actual_hours": total_hours,
        "billable_hours": billable_hours,
        "overtime_hours": overtime_hours,
        "load_percentage": load_percentage,
        "status": status,
        "active_projects_count": len(active_projects),
        "available_hours": max(0, total_capacity - total_hours)
    }
    
    return {"workload": workload}


# ============= Team Workload =============

@router.get("/team/workload")
async def get_team_workload(
    period: str = Query("week", description="week, month"),
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get team workload summary"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Get all team members
    team_members = list(user_company_roles_collection.find({
        "company_id": x_company_id,
        "is_active": True
    }))
    
    # Calculate period
    now = datetime.utcnow()
    if period == "week":
        period_start = now - timedelta(days=7)
        capacity_per_user = 40
    else:  # month
        period_start = now - timedelta(days=30)
        capacity_per_user = 160
    
    team_workload = []
    total_capacity = 0
    total_actual = 0
    
    for member in team_members:
        user_id = member.get("user_id")
        
        # Get time records
        time_records = list(work_time_records_collection.find({
            "tenant_id": x_company_id,
            "user_id": user_id,
            "date": {"$gte": period_start, "$lte": now}
        }))
        
        actual_hours = sum(rec.get("hours", 0) for rec in time_records)
        load_percentage = (actual_hours / capacity_per_user * 100) if capacity_per_user > 0 else 0
        
        # Determine status
        if load_percentage < 60:
            status = "underloaded"
        elif load_percentage <= 90:
            status = "normal"
        elif load_percentage <= 110:
            status = "overloaded"
        else:
            status = "critical"
        
        team_workload.append({
            "user_id": user_id,
            "capacity_hours": capacity_per_user,
            "actual_hours": actual_hours,
            "load_percentage": load_percentage,
            "status": status
        })
        
        total_capacity += capacity_per_user
        total_actual += actual_hours
    
    # Summary by status
    underloaded = [m for m in team_workload if m["status"] == "underloaded"]
    normal = [m for m in team_workload if m["status"] == "normal"]
    overloaded = [m for m in team_workload if m["status"] == "overloaded"]
    critical = [m for m in team_workload if m["status"] == "critical"]
    
    return {
        "period": period,
        "period_start": period_start.isoformat(),
        "period_end": now.isoformat(),
        "team_size": len(team_members),
        "total_capacity_hours": total_capacity,
        "total_actual_hours": total_actual,
        "average_load_percentage": (total_actual / total_capacity * 100) if total_capacity > 0 else 0,
        "members": team_workload,
        "summary": {
            "underloaded": len(underloaded),
            "normal": len(normal),
            "overloaded": len(overloaded),
            "critical": len(critical)
        }
    }


# ============= Department Workload =============

@router.get("/departments/{department_name}/workload")
async def get_department_workload(
    department_name: str,
    period: str = Query("week", description="week, month"),
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get department workload"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # TODO: Implement department structure
    # For now, treat as team workload filtered by department
    
    return {
        "department_name": department_name,
        "message": "Department workload - requires department structure implementation"
    }


# ============= Workload Forecast =============

@router.get("/users/{user_id}/forecast")
async def get_workload_forecast(
    user_id: str,
    weeks: int = Query(3, description="Number of weeks to forecast"),
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get workload forecast for user"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Get assigned stages/tasks with deadlines
    assigned_stages = list(project_stages_collection.find({
        "tenant_id": x_company_id,
        "assigned_to": {"$in": [user_id]},
        "status": {"$in": ["not_started", "in_progress"]}
    }))
    
    # Build forecast for next N weeks
    forecasts = []
    for week in range(weeks):
        week_start = datetime.utcnow() + timedelta(weeks=week)
        week_end = week_start + timedelta(days=7)
        
        # Find tasks due in this week
        week_tasks = []
        total_hours = 0
        
        for stage in assigned_stages:
            deadline = stage.get("deadline")
            if deadline and week_start <= deadline <= week_end:
                estimated = stage.get("estimated_hours", 0)
                actual = stage.get("actual_hours", 0)
                remaining = max(0, estimated - actual)
                
                week_tasks.append({
                    "stage_id": stage.get("id"),
                    "project_id": stage.get("project_id"),
                    "name": stage.get("name"),
                    "hours": remaining
                })
                total_hours += remaining
        
        load_percentage = (total_hours / 40 * 100)
        
        if load_percentage < 60:
            status = "underloaded"
        elif load_percentage <= 90:
            status = "normal"
        elif load_percentage <= 110:
            status = "overloaded"
        else:
            status = "critical"
        
        forecasts.append({
            "week": week + 1,
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "forecasted_hours": total_hours,
            "capacity_hours": 40,
            "load_percentage": load_percentage,
            "status": status,
            "tasks": week_tasks
        })
    
    # Recommendations
    recommendations = []
    if any(f["status"] == "critical" for f in forecasts):
        recommendations.append("Critical overload detected - consider redistributing tasks")
    if any(f["status"] == "underloaded" for f in forecasts):
        recommendations.append("Capacity available - can take on new tasks")
    
    return {
        "user_id": user_id,
        "forecasts": forecasts,
        "recommendations": recommendations
    }


# ============= Overtime Analysis =============

@router.get("/analytics/overtime")
async def get_overtime_analysis(
    period: str = Query("month", description="week, month, quarter"),
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get overtime analysis"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Calculate period
    now = datetime.utcnow()
    if period == "week":
        period_start = now - timedelta(days=7)
    elif period == "month":
        period_start = now - timedelta(days=30)
    else:  # quarter
        period_start = now - timedelta(days=90)
    
    # Get overtime records
    overtime_records = list(work_time_records_collection.find({
        "tenant_id": x_company_id,
        "is_overtime": True,
        "date": {"$gte": period_start, "$lte": now}
    }))
    
    # Group by user
    by_user = {}
    for rec in overtime_records:
        user_id = rec.get("user_id")
        if user_id not in by_user:
            by_user[user_id] = {
                "user_id": user_id,
                "overtime_hours": 0,
                "overtime_days": 0
            }
        by_user[user_id]["overtime_hours"] += rec.get("hours", 0)
        by_user[user_id]["overtime_days"] += 1
    
    total_overtime = sum(rec.get("hours", 0) for rec in overtime_records)
    
    return {
        "period": period,
        "period_start": period_start.isoformat(),
        "period_end": now.isoformat(),
        "total_overtime_hours": total_overtime,
        "users_with_overtime": len(by_user),
        "by_user": list(by_user.values())
    }


# ============= Capacity Planning =============

@router.get("/analytics/capacity")
async def get_capacity_analysis(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get capacity planning analysis"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Get team size
    team_members = list(user_company_roles_collection.find({
        "company_id": x_company_id,
        "is_active": True
    }))
    
    team_size = len(team_members)
    weekly_capacity = team_size * 40
    
    # Get active projects
    active_projects = list(projects_collection.find({
        "tenant_id": x_company_id,
        "status": {"$in": ["in_progress", "planning"]}
    }))
    
    # Get active stages
    active_stages = list(project_stages_collection.find({
        "tenant_id": x_company_id,
        "status": {"$in": ["not_started", "in_progress"]}
    }))
    
    # Calculate total required hours
    total_required = sum(
        max(0, stage.get("estimated_hours", 0) - stage.get("actual_hours", 0))
        for stage in active_stages
    )
    
    # Current week utilization
    now = datetime.utcnow()
    week_start = now - timedelta(days=7)
    
    week_records = list(work_time_records_collection.find({
        "tenant_id": x_company_id,
        "date": {"$gte": week_start, "$lte": now}
    }))
    
    week_actual = sum(rec.get("hours", 0) for rec in week_records)
    utilization = (week_actual / weekly_capacity * 100) if weekly_capacity > 0 else 0
    
    return {
        "team_size": team_size,
        "weekly_capacity_hours": weekly_capacity,
        "current_utilization": utilization,
        "active_projects": len(active_projects),
        "active_stages": len(active_stages),
        "total_required_hours": total_required,
        "estimated_weeks_to_complete": total_required / weekly_capacity if weekly_capacity > 0 else 0,
        "capacity_status": "overbooked" if total_required > weekly_capacity * 4 else "normal"
    }
