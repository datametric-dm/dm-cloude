"""
Financial Flow models
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class PaymentType(str, Enum):
    """Payment type enum"""
    INCOME = "income"
    EXPENSE = "expense"
    PLANNED = "planned"
    ACTUAL = "actual"


class TransactionStatus(str, Enum):
    """Transaction status"""
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    MATCHED = "matched"


class FinancialRecord(BaseModel):
    """Financial record (income/expense)"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    
    # Type
    type: PaymentType
    status: TransactionStatus = TransactionStatus.PENDING
    
    # Amount
    amount: float
    currency: str = "RUB"
    
    # Related entities
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    invoice_id: Optional[str] = None
    payment_id: Optional[str] = None
    
    # Dates
    planned_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    
    # Description
    description: Optional[str] = None
    category: Optional[str] = None
    
    # Bank integration
    bank_transaction_id: Optional[str] = None
    bank_account: Optional[str] = None
    auto_matched: bool = False
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None


class CashFlowForecast(BaseModel):
    """Cash flow forecast"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    
    # Period
    forecast_date: datetime
    period_start: datetime
    period_end: datetime
    
    # Forecast data
    opening_balance: float = 0.0
    planned_income: float = 0.0
    planned_expense: float = 0.0
    actual_income: float = 0.0
    actual_expense: float = 0.0
    closing_balance: float = 0.0
    
    # Analysis
    variance: float = 0.0  # Difference between planned and actual
    risk_level: str = "low"  # low, medium, high
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None


class WeeklySummary(BaseModel):
    """Weekly financial summary"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    tenant_id: str
    
    # Period
    week_number: int
    year: int
    week_start: datetime
    week_end: datetime
    
    # Income
    planned_income: float = 0.0
    actual_income: float = 0.0
    income_variance: float = 0.0
    
    # Expenses
    planned_expense: float = 0.0
    actual_expense: float = 0.0
    expense_variance: float = 0.0
    
    # Overdue
    overdue_invoices_count: int = 0
    overdue_amount: float = 0.0
    
    # Clients
    clients_with_overdue: List[str] = []
    projects_without_payment: List[str] = []
    
    # Budget changes
    budget_changes: List[dict] = []
    
    # Generated
    generated_at: datetime = Field(default_factory=datetime.utcnow)
