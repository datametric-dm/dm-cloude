"""
Billing and Subscription models
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class SubscriptionPlanType(str, Enum):
    """Subscription plan types"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class BillingCycle(str, Enum):
    """Billing cycle"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class SubscriptionStatusEnum(str, Enum):
    """Subscription status"""
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class PaymentMethodType(str, Enum):
    """Payment method type"""
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    INVOICE = "invoice"


class SubscriptionPlan(BaseModel):
    """Subscription plan definition"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    
    # Plan details
    name: str
    plan_type: SubscriptionPlanType
    description: Optional[str] = None
    
    # Pricing
    monthly_price: float = 0.0
    quarterly_price: float = 0.0
    yearly_price: float = 0.0
    currency: str = "RUB"
    
    # Limits
    max_users: int = 5
    max_projects: int = 10
    max_storage_gb: int = 10
    
    # Features
    features: List[str] = []
    has_api_access: bool = False
    has_integrations: bool = False
    has_advanced_reports: bool = False
    has_priority_support: bool = False
    
    # Metadata
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Subscription(BaseModel):
    """Company subscription"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    
    # Plan
    plan_id: str
    plan_type: SubscriptionPlanType
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    
    # Status
    status: SubscriptionStatusEnum = SubscriptionStatusEnum.TRIAL
    
    # Dates
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # Pricing
    amount: float = 0.0
    currency: str = "RUB"
    
    # Payment
    payment_method_id: Optional[str] = None
    next_billing_date: Optional[datetime] = None
    auto_renew: bool = True
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PaymentMethod(BaseModel):
    """Payment method for company"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    
    # Type
    type: PaymentMethodType
    
    # Card details (masked for security)
    card_last4: Optional[str] = None
    card_brand: Optional[str] = None  # Visa, MasterCard, Mir
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    
    # Bank details
    bank_name: Optional[str] = None
    account_number_last4: Optional[str] = None
    
    # Payment gateway
    gateway: str = "tinkoff"  # tinkoff, sberbank, alfabank
    gateway_customer_id: Optional[str] = None
    gateway_payment_method_id: Optional[str] = None
    
    # Status
    is_default: bool = False
    is_active: bool = True
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BillingTransaction(BaseModel):
    """Billing transaction record"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    subscription_id: str
    
    # Transaction details
    type: str = "charge"  # charge, refund, adjustment
    amount: float
    currency: str = "RUB"
    description: str
    
    # Status
    status: str = "pending"  # pending, succeeded, failed, refunded
    
    # Payment
    payment_method_id: Optional[str] = None
    gateway: str = "tinkoff"
    gateway_transaction_id: Optional[str] = None
    
    # Dates
    attempted_at: Optional[datetime] = None
    succeeded_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    
    # Error
    failure_code: Optional[str] = None
    failure_message: Optional[str] = None
    
    # Metadata
    metadata: Optional[dict] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Invoice(BaseModel):
    """Billing invoice"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    subscription_id: str
    
    # Invoice details
    invoice_number: str
    amount: float
    currency: str = "RUB"
    
    # Period
    period_start: datetime
    period_end: datetime
    
    # Status
    status: str = "draft"  # draft, open, paid, void
    
    # Payment
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    payment_method_id: Optional[str] = None
    
    # Files
    pdf_url: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
