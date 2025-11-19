"""
Risk Analyzer models - AI-powered risk detection
"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(str, Enum):
    """Risk category"""
    PROJECT_DELAY = "project_delay"
    PAYMENT_DELAY = "payment_delay"
    CLIENT_CHURN = "client_churn"
    TEAM_OVERLOAD = "team_overload"
    BUDGET_OVERRUN = "budget_overrun"
    LOW_VELOCITY = "low_velocity"
    COMMUNICATION_GAP = "communication_gap"
    SCOPE_CREEP = "scope_creep"


class RiskStatus(str, Enum):
    """Risk status"""
    DETECTED = "detected"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class Risk(BaseModel):
    """Risk record"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    
    # Risk details
    category: RiskCategory
    level: RiskLevel
    status: RiskStatus = RiskStatus.DETECTED
    
    # Description
    title: str
    description: str
    impact: str  # Business impact description
    
    # Related entities
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    user_id: Optional[str] = None
    stage_id: Optional[str] = None
    
    # Metrics
    probability: float = 0.0  # 0-1
    severity_score: float = 0.0  # 0-100
    confidence: float = 0.0  # AI confidence 0-1
    
    # Indicators
    indicators: List[str] = []  # What triggered this risk
    
    # Recommendations
    recommendations: List[str] = []
    action_items: List[str] = []
    
    # Timeline
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Assignment
    assigned_to: Optional[str] = None
    acknowledged_by: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectRiskAnalysis(BaseModel):
    """Project risk analysis"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    project_id: str
    
    # Overall risk
    overall_risk_level: RiskLevel = RiskLevel.LOW
    overall_risk_score: float = 0.0  # 0-100
    
    # Component risks
    timeline_risk: float = 0.0
    budget_risk: float = 0.0
    team_risk: float = 0.0
    client_risk: float = 0.0
    scope_risk: float = 0.0
    
    # Detected risks
    active_risks: List[Risk] = []
    risk_count: int = 0
    
    # Indicators
    days_since_last_activity: int = 0
    stage_delay_days: int = 0
    budget_utilization: float = 0.0
    team_utilization: float = 0.0
    
    # Predictions
    estimated_completion_date: Optional[datetime] = None
    estimated_budget_overrun: float = 0.0
    success_probability: float = 0.0
    
    # Recommendations
    priority_actions: List[str] = []
    
    # Analysis
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    next_analysis_at: Optional[datetime] = None


class TeamRiskAnalysis(BaseModel):
    """Team/user risk analysis"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    user_id: str
    
    # Overload risk
    overload_risk_level: RiskLevel = RiskLevel.LOW
    current_load_percentage: float = 0.0
    forecasted_load_1week: float = 0.0
    forecasted_load_2weeks: float = 0.0
    
    # Performance risk
    velocity_score: float = 0.0  # Tasks completed / estimated
    quality_score: float = 0.0
    
    # Active assignments
    active_tasks_count: int = 0
    overdue_tasks_count: int = 0
    
    # Recommendations
    recommendations: List[str] = []
    
    # Analysis
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class ClientChurnRisk(BaseModel):
    """Client churn risk analysis"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    client_id: str
    
    # Churn risk
    churn_probability: float = 0.0  # 0-1
    risk_level: RiskLevel = RiskLevel.LOW
    
    # Indicators
    days_since_last_interaction: int = 0
    overdue_payments_count: int = 0
    overdue_amount: float = 0.0
    project_satisfaction_score: float = 0.0
    communication_responsiveness: float = 0.0
    
    # Behavioral changes
    engagement_trend: str = "stable"  # increasing, stable, declining
    payment_trend: str = "stable"
    
    # Recommendations
    retention_actions: List[str] = []
    priority_level: str = "normal"
    
    # Analysis
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class RiskDashboard(BaseModel):
    """Risk dashboard summary"""
    tenant_id: str
    
    # Overall
    total_risks: int = 0
    critical_risks: int = 0
    high_risks: int = 0
    medium_risks: int = 0
    low_risks: int = 0
    
    # By category
    risks_by_category: Dict[str, int] = {}
    
    # Top risks
    top_risks: List[Risk] = []
    
    # Trends
    new_risks_24h: int = 0
    resolved_risks_24h: int = 0
    
    # Generated
    generated_at: datetime = Field(default_factory=datetime.utcnow)
