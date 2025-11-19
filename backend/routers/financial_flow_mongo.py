"""
Financial Flow API - доходы, расходы, прогноз кассы
"""
from fastapi import APIRouter, HTTPException, Header, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import uuid4

from database.base import (
    financial_records_collection,
    cash_flow_forecasts_collection,
    weekly_summaries_collection,
    invoices_collection,
    payments_collection,
    projects_collection,
    clients_collection
)
from routers.auth_mongo import get_current_user

router = APIRouter(tags=["financial-flow"], prefix="/financial-flow")


# ============= Financial Records =============

class FinancialRecordCreate(BaseModel):
    type: str  # income, expense, planned, actual
    amount: float
    planned_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


@router.post("/records")
async def create_financial_record(
    record_data: FinancialRecordCreate,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """Create financial record"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    record_dict = record_data.dict()
    record_dict.update({
        "id": uuid4().hex,
        "tenant_id": x_company_id,
        "status": "pending",
        "currency": "RUB",
        "auto_matched": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": x_user_id
    })
    
    financial_records_collection.insert_one(record_dict)
    record_dict.pop("_id", None)
    
    return {"message": "Financial record created", "record": record_dict}


@router.get("/records")
async def get_financial_records(
    type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get financial records"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    query = {"tenant_id": x_company_id}
    if type:
        query["type"] = type
    if status:
        query["status"] = status
    
    if start_date and end_date:
        query["planned_date"] = {
            "$gte": datetime.fromisoformat(start_date),
            "$lte": datetime.fromisoformat(end_date)
        }
    
    records = list(financial_records_collection.find(query).sort("planned_date", -1))
    for rec in records:
        rec.pop("_id", None)
    
    return {"records": records, "count": len(records)}


# ============= Income vs Expense =============

@router.get("/summary")
async def get_financial_summary(
    period: str = Query("month", description="week, month, quarter, year"),
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get financial summary"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Calculate period dates
    now = datetime.utcnow()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "quarter":
        start_date = now - timedelta(days=90)
    else:  # year
        start_date = now - timedelta(days=365)
    
    # Get invoices (planned income)
    planned_invoices = list(invoices_collection.find({
        "tenant_id": x_company_id,
        "date_due": {"$gte": start_date, "$lte": now}
    }))
    
    planned_income = sum(inv.get("amount", 0) for inv in planned_invoices)
    
    # Get payments (actual income)
    actual_payments = list(payments_collection.find({
        "tenant_id": x_company_id,
        "date_received": {"$gte": start_date, "$lte": now},
        "status": "received"
    }))
    
    actual_income = sum(pay.get("amount", 0) for pay in actual_payments)
    
    # Get overdue
    overdue_invoices = list(invoices_collection.find({
        "tenant_id": x_company_id,
        "status": "overdue"
    }))
    
    overdue_amount = sum(inv.get("amount", 0) for inv in overdue_invoices)
    
    # Get pending payments
    pending_payments = list(payments_collection.find({
        "tenant_id": x_company_id,
        "status": "pending"
    }))
    
    pending_amount = sum(pay.get("amount", 0) for pay in pending_payments)
    
    return {
        "period": period,
        "period_start": start_date.isoformat(),
        "period_end": now.isoformat(),
        "planned_income": planned_income,
        "actual_income": actual_income,
        "variance": actual_income - planned_income,
        "variance_percentage": ((actual_income - planned_income) / planned_income * 100) if planned_income > 0 else 0,
        "overdue_count": len(overdue_invoices),
        "overdue_amount": overdue_amount,
        "pending_count": len(pending_payments),
        "pending_amount": pending_amount,
        "collection_rate": (actual_income / planned_income * 100) if planned_income > 0 else 0
    }


# ============= Cash Flow Forecast =============

@router.get("/forecast")
async def get_cash_flow_forecast(
    weeks: int = Query(4, description="Number of weeks to forecast"),
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get cash flow forecast"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    forecasts = []
    current_balance = 0.0  # TODO: Get from accounting
    
    for week in range(weeks):
        week_start = datetime.utcnow() + timedelta(weeks=week)
        week_end = week_start + timedelta(days=7)
        
        # Get expected income
        expected_invoices = list(invoices_collection.find({
            "tenant_id": x_company_id,
            "date_due": {"$gte": week_start, "$lte": week_end},
            "status": {"$in": ["draft", "sent"]}
        }))
        
        planned_income = sum(inv.get("amount", 0) for inv in expected_invoices)
        
        # Get expected expenses (simplified)
        planned_expense = 0.0
        
        # Calculate forecast
        closing_balance = current_balance + planned_income - planned_expense
        
        forecast = {
            "week": week + 1,
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "opening_balance": current_balance,
            "planned_income": planned_income,
            "planned_expense": planned_expense,
            "closing_balance": closing_balance,
            "risk_level": "low" if closing_balance > 0 else "high"
        }
        
        forecasts.append(forecast)
        current_balance = closing_balance
    
    return {"forecasts": forecasts}


# ============= Weekly Summary =============

@router.get("/weekly-summary")
async def get_weekly_summary(
    week_offset: int = Query(0, description="0=current week, -1=last week, etc"),
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get weekly financial summary"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Calculate week dates
    now = datetime.utcnow()
    week_start = now - timedelta(days=now.weekday()) + timedelta(weeks=week_offset)
    week_end = week_start + timedelta(days=7)
    
    # Planned income
    planned_invoices = list(invoices_collection.find({
        "tenant_id": x_company_id,
        "date_due": {"$gte": week_start, "$lte": week_end}
    }))
    planned_income = sum(inv.get("amount", 0) for inv in planned_invoices)
    
    # Actual income
    actual_payments = list(payments_collection.find({
        "tenant_id": x_company_id,
        "date_received": {"$gte": week_start, "$lte": week_end},
        "status": "received"
    }))
    actual_income = sum(pay.get("amount", 0) for pay in actual_payments)
    
    # Overdue
    overdue_invoices = list(invoices_collection.find({
        "tenant_id": x_company_id,
        "status": "overdue"
    }))
    overdue_amount = sum(inv.get("amount", 0) for inv in overdue_invoices)
    
    # Clients with overdue
    clients_with_overdue = list(set([inv.get("client_id") for inv in overdue_invoices if inv.get("client_id")]))
    
    # Projects without payment
    all_projects = list(projects_collection.find({"tenant_id": x_company_id}))
    projects_without_payment = []
    
    for proj in all_projects:
        proj_payments = list(payments_collection.find({
            "tenant_id": x_company_id,
            "project_id": proj.get("id"),
            "status": "received"
        }))
        if len(proj_payments) == 0:
            projects_without_payment.append(proj.get("id"))
    
    summary = {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "planned_income": planned_income,
        "actual_income": actual_income,
        "income_variance": actual_income - planned_income,
        "overdue_invoices_count": len(overdue_invoices),
        "overdue_amount": overdue_amount,
        "clients_with_overdue": clients_with_overdue,
        "projects_without_payment": projects_without_payment,
        "generated_at": datetime.utcnow().isoformat()
    }
    
    return {"summary": summary}


# ============= Auto-matching =============

@router.post("/auto-match")
async def auto_match_payments(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Auto-match bank transactions with invoices"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Get unmatched bank transactions (TODO: implement bank integration)
    # Get pending invoices
    pending_invoices = list(invoices_collection.find({
        "tenant_id": x_company_id,
        "status": {"$in": ["sent", "overdue"]}
    }))
    
    matched_count = 0
    
    # Simple matching logic (by amount and date proximity)
    # TODO: Implement more sophisticated matching
    
    return {
        "message": f"Auto-matched {matched_count} transactions",
        "matched_count": matched_count
    }


# ============= Overdue Analysis =============

@router.get("/overdue-analysis")
async def get_overdue_analysis(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get detailed overdue analysis"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    overdue_invoices = list(invoices_collection.find({
        "tenant_id": x_company_id,
        "status": "overdue"
    }))
    
    # Group by client
    by_client = {}
    for inv in overdue_invoices:
        client_id = inv.get("client_id")
        if client_id:
            if client_id not in by_client:
                by_client[client_id] = {
                    "client_id": client_id,
                    "invoices": [],
                    "total_overdue": 0,
                    "oldest_invoice_date": None
                }
            
            by_client[client_id]["invoices"].append(inv.get("id"))
            by_client[client_id]["total_overdue"] += inv.get("amount", 0)
            
            inv_date = inv.get("date_due")
            if inv_date:
                if not by_client[client_id]["oldest_invoice_date"] or inv_date < by_client[client_id]["oldest_invoice_date"]:
                    by_client[client_id]["oldest_invoice_date"] = inv_date
    
    # Calculate days overdue
    now = datetime.utcnow()
    for client_data in by_client.values():
        if client_data["oldest_invoice_date"]:
            days_overdue = (now - client_data["oldest_invoice_date"]).days
            client_data["days_overdue"] = days_overdue
    
    return {
        "total_overdue": sum(inv.get("amount", 0) for inv in overdue_invoices),
        "invoices_count": len(overdue_invoices),
        "clients_count": len(by_client),
        "by_client": list(by_client.values())
    }
