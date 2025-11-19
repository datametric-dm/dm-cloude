"""
Notification tasks (email, Telegram, SMS)
"""
from celery_app import celery_app
from database.base import (
    invoices_collection,
    payments_collection,
    companies_collection,
    user_company_roles_collection,
    users_collection
)
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name='tasks.notifications.check_overdue_invoices')
def check_overdue_invoices():
    """
    Check for overdue invoices and send notifications
    Runs daily at 10:00 AM
    """
    logger.info("Checking overdue invoices")
    
    # Find invoices past due date
    today = datetime.utcnow()
    
    overdue_invoices = list(invoices_collection.find({
        "date_due": {"$lt": today},
        "status": {"$in": ["draft", "sent"]}
    }))
    
    # Update status to overdue
    for invoice in overdue_invoices:
        invoices_collection.update_one(
            {"id": invoice["id"]},
            {"$set": {"status": "overdue"}}
        )
        
        # Send notification
        send_overdue_notification.delay(
            invoice.get("tenant_id"),
            invoice.get("id"),
            invoice.get("client_id")
        )
    
    logger.info(f"Marked {len(overdue_invoices)} invoices as overdue")
    return {"overdue_count": len(overdue_invoices)}


@celery_app.task(name='tasks.notifications.send_overdue_notification')
def send_overdue_notification(company_id: str, invoice_id: str, client_id: str):
    """
    Send notification about overdue invoice
    """
    logger.info(f"Sending overdue notification for invoice: {invoice_id}")
    
    # TODO: Implement notification logic
    # - Get company owners/admins
    # - Send email notification
    # - Send Telegram notification if configured
    
    return {"status": "sent", "invoice_id": invoice_id}


@celery_app.task(name='tasks.notifications.send_email')
def send_email(to_email: str, subject: str, body: str, company_id: str = None):
    """
    Send email notification
    """
    logger.info(f"Sending email to: {to_email}, subject: {subject}")
    
    # TODO: Implement email sending (SendGrid, AWS SES, etc.)
    
    return {"status": "sent", "to": to_email}


@celery_app.task(name='tasks.notifications.send_telegram')
def send_telegram(chat_id: str, message: str, company_id: str = None):
    """
    Send Telegram notification
    """
    logger.info(f"Sending Telegram message to chat: {chat_id}")
    
    # TODO: Implement Telegram notification
    
    return {"status": "sent", "chat_id": chat_id}
