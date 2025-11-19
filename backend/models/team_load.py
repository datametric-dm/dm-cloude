"""
Team Load models for workload tracking
"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from enum import Enum


class LoadStatus(str, Enum):
    """Load status"""
    UNDERLOADED = "underloaded"  # < 60%
    NORMAL = "normal"  # 60-90%
    OVERLOADED = "overloaded"  # 90-110%
    CRITICAL = "critical"  # > 110%


class WorkTimeRecord(BaseModel):
    """Work time record for task/project"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    
    # Assignment
    user_id: str
    project_id: Optional[str] = None
    stage_id: Optional[str] = None
    task_id: Optional[str] = None
    
    # Time
    date: datetime
    hours: float
    description: Optional[str] = None
    
    # Type
    is_billable: bool = True
    is_overtime: bool = False
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None


class UserWorkload(BaseModel):
    """User workload summary"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    user_id: str
    
    # Period
    period_start: datetime
    period_end: datetime
    
    # Capacity
    total_capacity_hours: float = 40.0  # Weekly capacity
    allocated_hours: float = 0.0
    actual_hours: float = 0.0
    available_hours: float = 0.0
    
    # Load percentage
    load_percentage: float = 0.0
    status: LoadStatus = LoadStatus.NORMAL
    
    # Breakdown
    billable_hours: float = 0.0
    non_billable_hours: float = 0.0
    overtime_hours: float = 0.0
    
    # Projects
    active_projects_count: int = 0
    active_tasks_count: int = 0
    
    # Forecast
    forecasted_hours_1week: float = 0.0
    forecasted_hours_2weeks: float = 0.0
    forecasted_hours_3weeks: float = 0.0
    
    # Metadata
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class DepartmentWorkload(BaseModel):
    """Department workload summary"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    
    # Department
    department_name: str
    department_id: Optional[str] = None
    
    # Period
    period_start: datetime
    period_end: datetime
    
    # Team
    team_size: int = 0
    total_capacity_hours: float = 0.0
    total_allocated_hours: float = 0.0
    total_actual_hours: float = 0.0
    
    # Load
    average_load_percentage: float = 0.0
    status: LoadStatus = LoadStatus.NORMAL
    
    # Members breakdown
    underloaded_members: List[str] = []
    normal_members: List[str] = []
    overloaded_members: List[str] = []
    critical_members: List[str] = []
    
    # Overtime
    total_overtime_hours: float = 0.0
    members_with_overtime: int = 0
    
    # Metadata
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskAssignment(BaseModel):
    """Task assignment with time tracking"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    
    # Assignment
    user_id: str
    project_id: str
    stage_id: Optional[str] = None
    task_name: str
    
    # Time
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    remaining_hours: float = 0.0
    
    # Dates
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Status
    status: str = "assigned"  # assigned, in_progress, completed, blocked
    progress: float = 0.0  # 0-100%
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkloadForecast(BaseModel):
    """Workload forecast for team member"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    user_id: str
    
    # Forecast periods
    week_1: Dict[str, float] = {}  # {date: hours}
    week_2: Dict[str, float] = {}
    week_3: Dict[str, float] = {}
    
    # Summary
    week_1_total: float = 0.0
    week_2_total: float = 0.0
    week_3_total: float = 0.0
    
    week_1_status: LoadStatus = LoadStatus.NORMAL
    week_2_status: LoadStatus = LoadStatus.NORMAL
    week_3_status: LoadStatus = LoadStatus.NORMAL
    
    # Recommendations
    recommendations: List[str] = []
    
    # Generated
    generated_at: datetime = Field(default_factory=datetime.utcnow)
