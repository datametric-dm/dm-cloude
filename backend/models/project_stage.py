"""
Project Stage model for Kanban workflow
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class StageStatus(str, Enum):
    """Stage status enum"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class StageType(str, Enum):
    """Stage type enum"""
    CUSTOM = "custom"
    NEW = "new"
    IN_WORK = "in_work"
    PRESENTATION = "presentation"
    CONTROL = "control"
    DONE = "done"
    ARCHIVED = "archived"


class SubStage(BaseModel):
    """Sub-stage model"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    name: str
    description: Optional[str] = None
    status: StageStatus = StageStatus.NOT_STARTED
    assigned_to: Optional[str] = None  # User ID
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    actual_hours: float = 0.0
    estimated_hours: float = 0.0
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None


class ProjectStage(BaseModel):
    """Project Stage model for Kanban"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    project_id: str
    tenant_id: str
    
    # Stage info
    name: str
    type: StageType = StageType.CUSTOM
    description: Optional[str] = None
    order: int = 0  # Order in Kanban board
    
    # Status and dates
    status: StageStatus = StageStatus.NOT_STARTED
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    is_overdue: bool = False
    
    # Progress
    progress: float = 0.0  # 0-100%
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    
    # Assignment
    assigned_to: Optional[List[str]] = []  # User IDs
    responsible: Optional[str] = None  # Main responsible user ID
    
    # Sub-stages
    sub_stages: Optional[List[SubStage]] = []
    
    # Automation
    auto_close_on_crm_update: bool = False
    crm_deal_id: Optional[str] = None
    crm_stage_id: Optional[str] = None
    
    # Metadata
    is_stuck: bool = False  # Auto-detected if no activity for X days
    stuck_days: int = 0
    last_activity_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    # Comments/Notes
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "proj123",
                "tenant_id": "company123",
                "name": "Разработка дизайна",
                "type": "in_work",
                "status": "in_progress",
                "progress": 45.5,
                "deadline": "2025-12-01T00:00:00",
                "assigned_to": ["user1", "user2"]
            }
        }


class KanbanColumn(BaseModel):
    """Kanban column configuration for a company"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    
    name: str
    type: StageType
    color: Optional[str] = "#3B82F6"  # Tailwind blue
    order: int = 0
    is_active: bool = True
    
    # Limits
    wip_limit: Optional[int] = None  # Work In Progress limit
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "В работе",
                "type": "in_work",
                "color": "#3B82F6",
                "order": 2,
                "wip_limit": 5
            }
        }
