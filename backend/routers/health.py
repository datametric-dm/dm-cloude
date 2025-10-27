from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.base import get_db
from sqlalchemy import text
import os

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Проверка состояния системы"""
    try:
        # Проверяем подключение к базе данных
        db.execute(text("SELECT 1"))
        db_status = "OK"
    except Exception as e:
        db_status = f"ERROR: {str(e)}"
    
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    telegram_status = "Configured" if telegram_token else "Not configured"
    
    return {
        "status": "OK",
        "database": db_status,
        "telegram": telegram_status,
        "version": "2.0.0",
        "service": "DataMetrics Cloud MVP"
    }

@router.get("/")
def root():
    """Корневой эндпоинт API"""
    return {
        "message": "DataMetrics Cloud MVP API",
        "version": "2.0.0",
        "docs": "/docs"
    }

@router.get("/healthz")
def healthz_check():
    """Simple health check for Docker"""
    return {"status": "OK"}
