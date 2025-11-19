"""
Report generation tasks
"""
from celery_app import celery_app
from database.base import (
    companies_collection,
    invoices_collection,
    payments_collection,
    projects_collection,
    user_company_roles_collection
)
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name='tasks.reports.generate_weekly_financial_summary')
def generate_weekly_financial_summary():
    """
    Generate weekly financial summary for all companies
    Runs every Monday at 9:00 AM
    """
    logger.info("Generating weekly financial summaries")
    
    companies = list(companies_collection.find({"is_active": True}))
    
    for company in companies:
        company_id = company.get("id")
        logger.info(f"Generating weekly summary for company: {company_id}")
        
        # Generate report for this company
        generate_company_weekly_report.delay(company_id)
    
    return {"companies_processed": len(companies)}


@celery_app.task(name='tasks.reports.generate_company_weekly_report')
def generate_company_weekly_report(company_id: str):
    """
    Generate weekly financial report for a specific company
    """
    logger.info(f"Generating weekly report for company: {company_id}")
    
    # Date range: last 7 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    # Get financial data
    planned_payments = list(invoices_collection.find({
        "tenant_id": company_id,
        "date_due": {"$gte": start_date, "$lte": end_date}
    }))
    
    actual_payments = list(payments_collection.find({
        "tenant_id": company_id,
        "date_received": {"$gte": start_date, "$lte": end_date},
        "status": "received"
    }))
    
    overdue_invoices = list(invoices_collection.find({
        "tenant_id": company_id,
        "status": "overdue"
    }))
    
    # Calculate totals
    planned_total = sum(inv.get("amount", 0) for inv in planned_payments)
    actual_total = sum(pay.get("amount", 0) for pay in actual_payments)
    overdue_total = sum(inv.get("amount", 0) for inv in overdue_invoices)
    
    report = {
        "company_id": company_id,
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "planned_payments": planned_total,
        "actual_payments": actual_total,
        "overdue_total": overdue_total,
        "overdue_count": len(overdue_invoices),
        "generated_at": datetime.utcnow().isoformat()
    }
    
    # TODO: Send report via email or Telegram
    logger.info(f"Weekly report generated: {report}")
    
    return report


@celery_app.task(name='tasks.reports.generate_monthly_report')
def generate_monthly_report(company_id: str, year: int, month: int):
    """
    Generate monthly report for a company
    """
    logger.info(f"Generating monthly report for {company_id}: {year}-{month}")
    
    # TODO: Implement monthly report logic
    
    return {"status": "success", "company_id": company_id}
