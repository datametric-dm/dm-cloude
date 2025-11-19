"""
Project Flow API - Kanban, stages, progress tracking
"""
from fastapi import APIRouter, HTTPException, Header, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import uuid4

from database.base import (
    project_stages_collection,
    kanban_columns_collection,
    projects_collection
)
from routers.auth_mongo import get_current_user
from models.project_stage import (
    ProjectStage,
    SubStage,
    KanbanColumn,
    StageStatus,
    StageType
)

router = APIRouter(tags=["project-flow"], prefix="/project-flow")


# ============= Kanban Columns =============

class KanbanColumnCreate(BaseModel):
    name: str
    type: str
    color: Optional[str] = "#3B82F6"
    order: Optional[int] = 0
    wip_limit: Optional[int] = None


@router.post("/columns")
async def create_kanban_column(
    column_data: KanbanColumnCreate,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Create a new Kanban column for company"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    column_dict = column_data.dict()
    column_dict.update({
        "id": uuid4().hex,
        "tenant_id": x_company_id,
        "is_active": True,
        "created_at": datetime.utcnow()
    })
    
    kanban_columns_collection.insert_one(column_dict)
    column_dict.pop("_id", None)
    
    return {"message": "Kanban column created", "column": column_dict}


@router.get("/columns")
async def get_kanban_columns(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get all Kanban columns for company"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    columns = list(kanban_columns_collection.find({
        "tenant_id": x_company_id,
        "is_active": True
    }).sort("order", 1))
    
    for col in columns:
        col.pop("_id", None)
    
    return {"columns": columns}


@router.put("/columns/{column_id}")
async def update_kanban_column(
    column_id: str,
    column_data: KanbanColumnCreate,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Update Kanban column"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    update_data = column_data.dict(exclude_unset=True)
    
    result = kanban_columns_collection.update_one(
        {"id": column_id, "tenant_id": x_company_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Column not found")
    
    return {"message": "Column updated"}


@router.delete("/columns/{column_id}")
async def delete_kanban_column(
    column_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Delete Kanban column (soft delete)"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    result = kanban_columns_collection.update_one(
        {"id": column_id, "tenant_id": x_company_id},
        {"$set": {"is_active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Column not found")
    
    return {"message": "Column deleted"}


# ============= Project Stages =============

class StageCreate(BaseModel):
    project_id: str
    name: str
    type: Optional[str] = "custom"
    description: Optional[str] = None
    order: Optional[int] = 0
    deadline: Optional[datetime] = None
    estimated_hours: Optional[float] = 0.0
    assigned_to: Optional[List[str]] = []
    responsible: Optional[str] = None


class StageUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[float] = None
    deadline: Optional[datetime] = None
    assigned_to: Optional[List[str]] = None
    responsible: Optional[str] = None
    notes: Optional[str] = None


@router.post("/stages")
async def create_stage(
    stage_data: StageCreate,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """Create a new project stage"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Verify project exists
    project = projects_collection.find_one({
        "id": stage_data.project_id,
        "tenant_id": x_company_id
    })
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    stage_dict = stage_data.dict()
    stage_dict.update({
        "id": uuid4().hex,
        "tenant_id": x_company_id,
        "status": StageStatus.NOT_STARTED.value,
        "progress": 0.0,
        "actual_hours": 0.0,
        "is_stuck": False,
        "stuck_days": 0,
        "is_overdue": False,
        "sub_stages": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": x_user_id,
        "last_activity_at": datetime.utcnow()
    })
    
    project_stages_collection.insert_one(stage_dict)
    stage_dict.pop("_id", None)
    
    return {"message": "Stage created", "stage": stage_dict}


@router.get("/stages/project/{project_id}")
async def get_project_stages(
    project_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get all stages for a project"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    stages = list(project_stages_collection.find({
        "project_id": project_id,
        "tenant_id": x_company_id
    }).sort("order", 1))
    
    for stage in stages:
        stage.pop("_id", None)
    
    return {"stages": stages}


@router.get("/stages/{stage_id}")
async def get_stage(
    stage_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get stage details"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    stage = project_stages_collection.find_one({
        "id": stage_id,
        "tenant_id": x_company_id
    })
    
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    stage.pop("_id", None)
    return {"stage": stage}


@router.put("/stages/{stage_id}")
async def update_stage(
    stage_id: str,
    stage_data: StageUpdate,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Update stage"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    update_data = stage_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    update_data["last_activity_at"] = datetime.utcnow()
    
    # Check if overdue
    if "deadline" in update_data:
        if update_data["deadline"] and update_data["deadline"] < datetime.utcnow():
            update_data["is_overdue"] = True
    
    result = project_stages_collection.update_one(
        {"id": stage_id, "tenant_id": x_company_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    updated_stage = project_stages_collection.find_one({
        "id": stage_id,
        "tenant_id": x_company_id
    })
    updated_stage.pop("_id", None)
    
    return {"message": "Stage updated", "stage": updated_stage}


@router.delete("/stages/{stage_id}")
async def delete_stage(
    stage_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Delete stage"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    result = project_stages_collection.delete_one({
        "id": stage_id,
        "tenant_id": x_company_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    return {"message": "Stage deleted"}


# ============= Sub-stages =============

class SubStageCreate(BaseModel):
    name: str
    description: Optional[str] = None
    estimated_hours: Optional[float] = 0.0
    assigned_to: Optional[str] = None
    deadline: Optional[datetime] = None


@router.post("/stages/{stage_id}/substages")
async def create_substage(
    stage_id: str,
    substage_data: SubStageCreate,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Create a sub-stage"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    stage = project_stages_collection.find_one({
        "id": stage_id,
        "tenant_id": x_company_id
    })
    
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    substage_dict = substage_data.dict()
    substage_dict.update({
        "id": uuid4().hex,
        "status": StageStatus.NOT_STARTED.value,
        "actual_hours": 0.0,
        "is_completed": False
    })
    
    project_stages_collection.update_one(
        {"id": stage_id, "tenant_id": x_company_id},
        {
            "$push": {"sub_stages": substage_dict},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"message": "Sub-stage created", "substage": substage_dict}


@router.put("/stages/{stage_id}/substages/{substage_id}")
async def update_substage(
    stage_id: str,
    substage_id: str,
    substage_data: dict,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Update a sub-stage"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Update sub-stage in array
    update_fields = {
        f"sub_stages.$.{k}": v 
        for k, v in substage_data.items()
    }
    update_fields["updated_at"] = datetime.utcnow()
    
    result = project_stages_collection.update_one(
        {
            "id": stage_id,
            "tenant_id": x_company_id,
            "sub_stages.id": substage_id
        },
        {"$set": update_fields}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sub-stage not found")
    
    return {"message": "Sub-stage updated"}


# ============= Kanban Board View =============

@router.get("/kanban/{project_id}")
async def get_kanban_board(
    project_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get Kanban board view for a project"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Get project
    project = projects_collection.find_one({
        "id": project_id,
        "tenant_id": x_company_id
    })
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.pop("_id", None)
    
    # Get columns
    columns = list(kanban_columns_collection.find({
        "tenant_id": x_company_id,
        "is_active": True
    }).sort("order", 1))
    
    # Get stages
    stages = list(project_stages_collection.find({
        "project_id": project_id,
        "tenant_id": x_company_id
    }))
    
    # Organize stages by type/column
    kanban_data = {}
    for col in columns:
        col.pop("_id", None)
        col_type = col["type"]
        col["stages"] = []
        
        # Find stages for this column
        for stage in stages:
            stage.pop("_id", None)
            if stage.get("type") == col_type:
                col["stages"].append(stage)
        
        kanban_data[col_type] = col
    
    return {
        "project": project,
        "kanban": kanban_data,
        "columns": columns
    }


# ============= Analytics =============

@router.get("/analytics/stuck-stages")
async def get_stuck_stages(
    days: int = Query(7, description="Days of inactivity to consider stuck"),
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get stages with no activity for X days"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    stuck_stages = list(project_stages_collection.find({
        "tenant_id": x_company_id,
        "status": {"$in": [StageStatus.IN_PROGRESS.value, StageStatus.BLOCKED.value]},
        "last_activity_at": {"$lt": cutoff_date}
    }))
    
    # Update stuck flag
    for stage in stuck_stages:
        stage.pop("_id", None)
        stuck_days = (datetime.utcnow() - stage.get("last_activity_at", datetime.utcnow())).days
        
        project_stages_collection.update_one(
            {"id": stage["id"]},
            {
                "$set": {
                    "is_stuck": True,
                    "stuck_days": stuck_days
                }
            }
        )
        stage["is_stuck"] = True
        stage["stuck_days"] = stuck_days
    
    return {"stuck_stages": stuck_stages, "count": len(stuck_stages)}


@router.get("/analytics/overdue-stages")
async def get_overdue_stages(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get all overdue stages"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    now = datetime.utcnow()
    
    overdue_stages = list(project_stages_collection.find({
        "tenant_id": x_company_id,
        "deadline": {"$lt": now},
        "status": {"$ne": StageStatus.COMPLETED.value}
    }))
    
    # Update overdue flag
    for stage in overdue_stages:
        stage.pop("_id", None)
        project_stages_collection.update_one(
            {"id": stage["id"]},
            {"$set": {"is_overdue": True}}
        )
        stage["is_overdue"] = True
    
    return {"overdue_stages": overdue_stages, "count": len(overdue_stages)}
