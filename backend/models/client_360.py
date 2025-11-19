"""
Client 360 models - comprehensive client view
"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from enum import Enum


class ClientTag(str, Enum):
    """Client tags"""
    VIP = "vip"
    RISK = "risk"
    CHURN_RISK = "churn_risk"
    ACTIVE = "active"
    INACTIVE = "inactive"
    NEW = "new"
    LOYAL = "loyal"
    PROBLEMATIC = "problematic"


class InteractionType(str, Enum):
    """Interaction type"""
    EMAIL = "email"
    CALL = "call"
    MEETING = "meeting"
    PROJECT_UPDATE = "project_update"
    INVOICE_SENT = "invoice_sent"
    PAYMENT_RECEIVED = "payment_received"
    COMPLAINT = "complaint"
    FEEDBACK = "feedback"
    CRM_UPDATE = "crm_update"


class ClientHealthStatus(str, Enum):
    """Client health status"""
    EXCELLENT = "excellent"  # 80-100
    GOOD = "good"  # 60-79
    FAIR = "fair"  # 40-59
    POOR = "poor"  # 20-39
    CRITICAL = "critical"  # 0-19


class ClientInteraction(BaseModel):
    """Client interaction record"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    client_id: str
    
    # Interaction details
    type: InteractionType
    title: str
    description: Optional[str] = None
    
    # Participants
    user_id: Optional[str] = None  # Our team member
    contact_person: Optional[str] = None  # Client contact
    
    # Related entities
    project_id: Optional[str] = None
    invoice_id: Optional[str] = None
    payment_id: Optional[str] = None
    
    # Metadata
    interaction_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    # Source
    source: Optional[str] = None  # manual, crm, email, auto
    external_id: Optional[str] = None


class ClientHealthScore(BaseModel):
    """Client health scoring"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    client_id: str
    
    # Overall score
    score: float = 0.0  # 0-100
    status: ClientHealthStatus = ClientHealthStatus.FAIR
    
    # Score components
    payment_score: float = 0.0  # Payment history
    project_score: float = 0.0  # Project success
    communication_score: float = 0.0  # Response rate
    engagement_score: float = 0.0  # Activity level
    satisfaction_score: float = 0.0  # Feedback/NPS
    
    # Metrics
    total_revenue: float = 0.0
    avg_payment_delay: float = 0.0  # Days
    overdue_count: int = 0
    completed_projects: int = 0
    active_projects: int = 0
    last_interaction_days: int = 0
    
    # Tags
    tags: List[ClientTag] = []
    
    # Risk indicators
    churn_probability: float = 0.0  # 0-1
    risk_level: str = "low"  # low, medium, high
    
    # Recommendations
    recommendations: List[str] = []
    
    # Calculated
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    next_calculation_at: Optional[datetime] = None


class ClientTimeline(BaseModel):
    """Client timeline event"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    client_id: str
    
    # Event
    event_type: str  # project_started, payment_received, etc
    event_title: str
    event_description: Optional[str] = None
    event_date: datetime
    
    # Related entities
    related_id: Optional[str] = None
    related_type: Optional[str] = None  # project, invoice, payment
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Client360Profile(BaseModel):
    """Complete client profile"""
    client_id: str
    tenant_id: str
    
    # Basic info
    client_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    
    # Health
    health_score: Optional[ClientHealthScore] = None
    
    # History
    total_projects: int = 0
    active_projects: int = 0
    completed_projects: int = 0
    
    total_revenue: float = 0.0
    total_paid: float = 0.0
    total_overdue: float = 0.0
    
    # Engagement
    first_project_date: Optional[datetime] = None
    last_project_date: Optional[datetime] = None
    last_payment_date: Optional[datetime] = None
    last_interaction_date: Optional[datetime] = None
    
    days_since_last_interaction: int = 0
    interaction_count: int = 0
    
    # Timeline
    timeline: List[ClientTimeline] = []
    
    # Interactions
    recent_interactions: List[ClientInteraction] = []
    
    # Tags
    tags: List[str] = []
