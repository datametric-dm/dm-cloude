"""
Tasks and background jobs management API
"""
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from routers.auth_mongo import get_current_user
from celery_app import celery_app
from tasks.integrations import sync_crm_data, sync_bank_transactions
from tasks.reports import generate_company_weekly_report
from tasks.notifications import send_email, send_telegram
from tasks.billing import process_company_renewal

router = APIRouter(tags=["tasks"], prefix="/tasks")


class TriggerTaskRequest(BaseModel):
    task_name: str
    company_id: Optional[str] = None
    params: Optional[dict] = {}


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None


@router.post("/trigger")
async def trigger_task(
    task_request: TriggerTaskRequest,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """
    Trigger a background task manually
    """
    company_id = task_request.company_id or x_company_id
    
    if not company_id:
        raise HTTPException(status_code=400, detail="Company ID is required")
    
    task_name = task_request.task_name
    params = task_request.params or {}
    
    # Map task names to functions
    task_map = {
        "sync_crm": sync_crm_data,
        "sync_bank": sync_bank_transactions,
        "weekly_report": generate_company_weekly_report,
        "process_renewal": process_company_renewal,
    }
    
    if task_name not in task_map:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown task: {task_name}. Available: {list(task_map.keys())}"
        )
    
    # Trigger task
    task_func = task_map[task_name]
    result = task_func.delay(company_id, **params)
    
    return {
        "message": f"Task '{task_name}' triggered",
        "task_id": result.id,
        "company_id": company_id
    }


@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    current_user=Depends(get_current_user)
):
    """
    Get status of a background task
    """
    result = celery_app.AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": result.status,
        "ready": result.ready(),
    }
    
    if result.ready():
        try:
            response["result"] = result.result
        except Exception as e:
            response["error"] = str(e)
    
    return response


@router.get("/stats")
async def get_celery_stats(
    current_user=Depends(get_current_user)
):
    """
    Get Celery worker stats
    """
    inspector = celery_app.control.inspect()
    
    stats = inspector.stats()
    active = inspector.active()
    scheduled = inspector.scheduled()
    registered = inspector.registered()
    
    return {
        "workers": stats or {},
        "active_tasks": active or {},
        "scheduled_tasks": scheduled or {},
        "registered_tasks": registered or {},
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/cancel/{task_id}")
async def cancel_task(
    task_id: str,
    current_user=Depends(get_current_user)
):
    """
    Cancel a running task
    """
    result = celery_app.AsyncResult(task_id)
    result.revoke(terminate=True)
    
    return {
        "message": "Task cancelled",
        "task_id": task_id
    }


@router.get("/scheduled")
async def get_scheduled_tasks(
    current_user=Depends(get_current_user)
):
    """
    Get list of scheduled periodic tasks
    """
    schedule = celery_app.conf.beat_schedule
    
    tasks = []
    for task_name, config in schedule.items():
        tasks.append({
            "name": task_name,
            "task": config["task"],
            "schedule": str(config["schedule"]),
            "enabled": True
        })
    
    return {"scheduled_tasks": tasks}
