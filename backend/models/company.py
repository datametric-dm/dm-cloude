"""
Company (Tenant) model for multi-tenancy architecture
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class SubscriptionStatus(str, Enum):
    """Subscription status enum"""
    TRIAL = "trial"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    FROZEN = "frozen"


class SubscriptionPlan(str, Enum):
    """Subscription plan enum"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Company(BaseModel):
    """Company (Tenant) model"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    name: str = Field(..., description="Company name")
    
    # Company details
    legal_name: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    ogrn: Optional[str] = None
    legal_address: Optional[str] = None
    actual_address: Optional[str] = None
    
    # Contact information
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    
    # Subscription details
    subscription_plan: SubscriptionPlan = SubscriptionPlan.FREE
    subscription_status: SubscriptionStatus = SubscriptionStatus.TRIAL
    trial_ends_at: Optional[datetime] = None
    subscription_started_at: Optional[datetime] = None
    subscription_ends_at: Optional[datetime] = None
    
    # Settings
    is_active: bool = True
    max_users: int = 5
    max_projects: int = 10
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # User ID who created the company
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Acme Marketing Agency",
                "email": "info@acme.com",
                "subscription_plan": "professional",
                "subscription_status": "active"
            }
        }
