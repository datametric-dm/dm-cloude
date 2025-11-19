"""
Billing and subscription tasks
"""
from celery_app import celery_app
from database.base import companies_collection
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name='tasks.billing.check_trial_expiring')
def check_trial_expiring():
    """
    Check for trial subscriptions expiring soon
    Send notifications 3 days before expiry
    Runs daily at 8:00 AM
    """
    logger.info("Checking trial subscriptions expiring")
    
    # Find trials expiring in 3 days
    three_days_from_now = datetime.utcnow() + timedelta(days=3)
    
    expiring_trials = list(companies_collection.find({
        "subscription_status": "trial",
        "trial_ends_at": {
            "$gte": datetime.utcnow(),
            "$lte": three_days_from_now
        }
    }))
    
    for company in expiring_trials:
        company_id = company.get("id")
        logger.info(f"Trial expiring for company: {company_id}")
        
        # Send notification
        send_trial_expiring_notification.delay(company_id)
    
    return {"expiring_trials": len(expiring_trials)}


@celery_app.task(name='tasks.billing.send_trial_expiring_notification')
def send_trial_expiring_notification(company_id: str):
    """
    Send notification about trial expiring
    """
    logger.info(f"Sending trial expiring notification for company: {company_id}")
    
    # TODO: Send email/notification
    
    return {"status": "sent", "company_id": company_id}


@celery_app.task(name='tasks.billing.process_renewals')
def process_renewals():
    """
    Process subscription renewals
    Charge customers and update subscription status
    Runs daily at 3:00 AM
    """
    logger.info("Processing subscription renewals")
    
    # Find subscriptions due for renewal today
    today = datetime.utcnow().date()
    
    due_renewals = list(companies_collection.find({
        "subscription_status": "active",
        "subscription_ends_at": {
            "$lte": datetime.combine(today, datetime.min.time())
        }
    }))
    
    for company in due_renewals:
        company_id = company.get("id")
        logger.info(f"Processing renewal for company: {company_id}")
        
        # Process payment
        process_company_renewal.delay(company_id)
    
    return {"renewals_processed": len(due_renewals)}


@celery_app.task(name='tasks.billing.process_company_renewal')
def process_company_renewal(company_id: str):
    """
    Process renewal for a specific company
    """
    logger.info(f"Processing renewal for company: {company_id}")
    
    company = companies_collection.find_one({"id": company_id})
    if not company:
        logger.error(f"Company not found: {company_id}")
        return {"status": "error", "message": "Company not found"}
    
    # TODO: Implement payment processing with Тинькофф
    # - Charge the card on file
    # - Update subscription_ends_at
    # - If payment fails, suspend account
    
    # For now, just extend subscription by 30 days
    new_end_date = datetime.utcnow() + timedelta(days=30)
    
    companies_collection.update_one(
        {"id": company_id},
        {
            "$set": {
                "subscription_ends_at": new_end_date,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"Renewed subscription for company: {company_id}")
    return {"status": "success", "company_id": company_id, "new_end_date": new_end_date.isoformat()}


@celery_app.task(name='tasks.billing.freeze_expired_companies')
def freeze_expired_companies():
    """
    Freeze companies with expired subscriptions
    """
    logger.info("Freezing expired companies")
    
    # Find companies with expired subscriptions
    today = datetime.utcnow()
    
    expired = list(companies_collection.find({
        "subscription_status": "active",
        "subscription_ends_at": {"$lt": today}
    }))
    
    for company in expired:
        company_id = company.get("id")
        
        # Freeze company
        companies_collection.update_one(
            {"id": company_id},
            {
                "$set": {
                    "subscription_status": "frozen",
                    "is_active": False,
                    "updated_at": today
                }
            }
        )
        
        logger.info(f"Frozen company: {company_id}")
    
    return {"frozen_count": len(expired)}
