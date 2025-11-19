"""
Celery application configuration
"""
from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Redis URL for Celery broker and result backend
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "dm_cloud_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        'tasks.integrations',
        'tasks.reports',
        'tasks.notifications',
        'tasks.billing',
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    result_expires=3600,  # 1 hour
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule (Celery Beat)
celery_app.conf.beat_schedule = {
    # Weekly financial summary - every Monday at 9:00 AM
    'weekly-financial-summary': {
        'task': 'tasks.reports.generate_weekly_financial_summary',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },
    
    # Daily sync with integrations - every day at 2:00 AM
    'daily-integration-sync': {
        'task': 'tasks.integrations.sync_all_integrations',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # Check overdue invoices - every day at 10:00 AM
    'check-overdue-invoices': {
        'task': 'tasks.notifications.check_overdue_invoices',
        'schedule': crontab(hour=10, minute=0),
    },
    
    # Check trial subscriptions expiring - daily at 8:00 AM
    'check-trial-expiring': {
        'task': 'tasks.billing.check_trial_expiring',
        'schedule': crontab(hour=8, minute=0),
    },
    
    # Process billing renewals - daily at 3:00 AM
    'process-billing-renewals': {
        'task': 'tasks.billing.process_renewals',
        'schedule': crontab(hour=3, minute=0),
    },
}

# Task routes - route specific tasks to specific queues
celery_app.conf.task_routes = {
    'tasks.integrations.*': {'queue': 'integrations'},
    'tasks.reports.*': {'queue': 'reports'},
    'tasks.notifications.*': {'queue': 'notifications'},
    'tasks.billing.*': {'queue': 'billing'},
}

if __name__ == '__main__':
    celery_app.start()
