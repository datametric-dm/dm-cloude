from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database.base import get_db
from models.payment import Payment, PaymentStatus
from models.invoice import Invoice, InvoiceStatus
from models.client import Client
from datetime import datetime, timedelta
import os
import asyncio
import httpx
from typing import List

router = APIRouter(prefix="/telegram")

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '-1001234567890')  # Чат по умолчанию

async def send_telegram_message(message: str, chat_id: str = TELEGRAM_CHAT_ID):
    """Отправка сообщения в Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        return {"error": "Telegram bot token не настроен"}
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            return response.json()
    except Exception as e:
        return {"error": str(e)}

@router.post("/send-message")
async def send_message(message: str, chat_id: str = TELEGRAM_CHAT_ID):
    """Отправка произвольного сообщения"""
    result = await send_telegram_message(message, chat_id)
    return result

@router.post("/notify-overdue")
async def notify_overdue_payments(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Уведомление о просроченных платежах"""
    # Получаем просроченные платежи
    overdue_payments = db.query(Payment).join(Client).filter(
        Payment.payment_date_planned < datetime.utcnow(),
        Payment.status == PaymentStatus.PLANNED
    ).all()
    
    if not overdue_payments:
        return {"message": "Просроченных платежей нет"}
    
    # Формируем сообщение
    message = "<b>🚨 Просроченные платежи</b>\n\n"
    
    total_overdue = 0
    for payment in overdue_payments:
        client = payment.client
        days_overdue = (datetime.utcnow() - payment.payment_date_planned).days
        
        message += f"📅 <b>{client.name}</b>\n"
        if client.company:
            message += f"🏢 {client.company}\n"
        message += f"💰 Сумма: {payment.amount:,.2f} ₽\n"
        message += f"⏰ Просрочка: {days_overdue} дн.\n\n"
        
        total_overdue += payment.amount
    
    message += f"<b>📈 Общая сумма просрочки: {total_overdue:,.2f} ₽</b>"
    
    background_tasks.add_task(send_telegram_message, message)
    
    return {
        "message": f"Уведомление о {len(overdue_payments)} просроченных платежах отправлено",
        "count": len(overdue_payments),
        "total_amount": total_overdue
    }

@router.post("/daily-report")
async def send_daily_report(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Отправка ежедневного отчёта"""
    today = datetime.utcnow().date()
    
    # Платежи на сегодня
    today_payments = db.query(Payment).filter(
        Payment.payment_date_planned >= datetime.combine(today, datetime.min.time()),
        Payment.payment_date_planned < datetime.combine(today + timedelta(days=1), datetime.min.time()),
        Payment.status == PaymentStatus.PLANNED
    ).count()
    
    # Просроченные платежи
    overdue_count = db.query(Payment).filter(
        Payment.payment_date_planned < datetime.utcnow(),
        Payment.status == PaymentStatus.PLANNED
    ).count()
    
    # Неоплаченные счета
    unpaid_invoices = db.query(Invoice).filter(
        Invoice.status != InvoiceStatus.PAID
    ).count()
    
    message = f"<b>📅 Ежедневный отчёт</b>\n\n"
    message += f"📅 Платежи на сегодня: {today_payments}\n"
    message += f"⚠️ Просроченные платежи: {overdue_count}\n"
    message += f"📝 Неоплаченные счета: {unpaid_invoices}\n"
    
    background_tasks.add_task(send_telegram_message, message)
    
    return {"message": "Ежедневный отчёт отправлен"}

@router.get("/test")
async def test_telegram():
    """Тест подключения к Telegram Bot"""
    if not TELEGRAM_BOT_TOKEN:
        return {"status": "error", "message": "Telegram bot token не настроен"}
    
    test_message = "🚀 Тест подключения DataMetrics Cloud MVP"
    result = await send_telegram_message(test_message)
    
    if 'error' in result:
        return {"status": "error", "message": result['error']}
    
    return {"status": "success", "message": "Тестовое сообщение отправлено"}
