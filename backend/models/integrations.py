"""
Integrations models
"""
from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from enum import Enum


class IntegrationType(str, Enum):
    """Integration type"""
    CRM = "crm"
    ACCOUNTING = "accounting"
    BANK = "bank"
    TASK_MANAGEMENT = "task_management"
    EMAIL = "email"
    SMS = "sms"
    PAYMENT = "payment"


class IntegrationProvider(str, Enum):
    """Integration providers"""
    # CRM
    AMOCRM = "amocrm"
    BITRIX24 = "bitrix24"
    
    # Accounting
    PLANFACT = "planfact"
    FINOLOG = "finolog"
    KONTUR = "kontur"
    ONE_C = "1c"
    MY_WAREHOUSE = "my_warehouse"
    
    # Banks
    TINKOFF = "tinkoff"
    SBERBANK = "sberbank"
    ALFABANK = "alfabank"
    
    # Task Management
    TRELLO = "trello"
    NOTION = "notion"
    CLICKUP = "clickup"
    JIRA = "jira"
    PLANFIX = "planfix"
    
    # Communication
    TELEGRAM = "telegram"
    EMAIL_SMTP = "email_smtp"
    SMS_RU = "sms_ru"


class IntegrationStatus(str, Enum):
    """Integration status"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"
    CONFIGURING = "configuring"


class SyncFrequency(str, Enum):
    """Sync frequency"""
    MANUAL = "manual"
    EVERY_15_MIN = "every_15_min"
    HOURLY = "hourly"
    EVERY_6_HOURS = "every_6_hours"
    DAILY = "daily"


class Integration(BaseModel):
    """Integration configuration"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    
    # Integration details
    name: str
    type: IntegrationType
    provider: IntegrationProvider
    description: Optional[str] = None
    
    # Status
    status: IntegrationStatus = IntegrationStatus.INACTIVE
    is_enabled: bool = False
    
    # Configuration
    config: Dict = {}  # Provider-specific configuration
    credentials: Dict = {}  # API keys, tokens (encrypted)
    
    # Sync settings
    sync_frequency: SyncFrequency = SyncFrequency.HOURLY
    last_sync_at: Optional[datetime] = None
    next_sync_at: Optional[datetime] = None
    
    # Features
    sync_clients: bool = False
    sync_projects: bool = False
    sync_invoices: bool = False
    sync_payments: bool = False
    sync_transactions: bool = False
    
    # Error handling
    last_error: Optional[str] = None
    error_count: int = 0
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None


class IntegrationLog(BaseModel):
    """Integration sync log"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    integration_id: str
    
    # Sync details
    sync_type: str  # manual, scheduled, webhook
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Status
    status: str = "running"  # running, completed, failed
    
    # Results
    records_processed: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_failed: int = 0
    
    # Errors
    errors: List[str] = []
    
    # Metadata
    metadata: Optional[dict] = {}


class IntegrationMapping(BaseModel):
    """Field mapping for integration"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    integration_id: str
    
    # Mapping
    entity_type: str  # client, project, invoice, etc
    source_field: str  # External system field
    target_field: str  # Our system field
    
    # Transformation
    transform_function: Optional[str] = None
    default_value: Optional[str] = None
    
    # Metadata
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AccountingIntegrationConfig(BaseModel):
    """Specific config for accounting integrations"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    integration_id: str
    tenant_id: str
    
    # General settings
    company_id: Optional[str] = None  # ID in accounting system
    organization_name: Optional[str] = None
    
    # Sync settings
    auto_create_counterparties: bool = True
    auto_create_invoices: bool = True
    auto_match_payments: bool = True
    
    # Account mapping
    income_account: Optional[str] = None
    expense_account: Optional[str] = None
    tax_account: Optional[str] = None
    
    # Tax settings
    vat_rate: float = 20.0  # %
    include_vat: bool = True
    
    # Export settings
    export_format: str = "json"  # json, xml, csv
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CRMIntegrationConfig(BaseModel):
    """Specific config for CRM integrations"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    integration_id: str
    tenant_id: str
    
    # Pipeline settings
    pipeline_id: Optional[str] = None
    default_stage_id: Optional[str] = None
    
    # Field mapping
    contact_fields: Dict = {}
    company_fields: Dict = {}
    deal_fields: Dict = {}
    
    # Sync settings
    sync_contacts: bool = True
    sync_companies: bool = True
    sync_deals: bool = True
    sync_tasks: bool = False
    
    # Webhooks
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BankIntegrationConfig(BaseModel):
    """Specific config for bank integrations"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    integration_id: str
    tenant_id: str
    
    # Account settings
    bank_account_id: Optional[str] = None
    account_number: Optional[str] = None
    
    # Sync settings
    auto_import_transactions: bool = True
    auto_match_invoices: bool = True
    sync_days_back: int = 30
    
    # Matching rules
    match_by_amount: bool = True
    match_by_date: bool = True
    match_by_description: bool = True
    match_tolerance_days: int = 3
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
