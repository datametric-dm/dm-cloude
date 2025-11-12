from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from database.base import get_db, clients_collection, projects_collection, invoices_collection, payments_collection
from routers.auth_mongo import get_current_user
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
            response = await client.post(url, json=data, timeout=10.0)
            return response.json()
    except Exception as e:
        return {"error": str(e)}

@router.post("/send-message")
async def send_message(
    message: str, 
    chat_id: str = TELEGRAM_CHAT_ID,
    current_user = Depends(get_current_user)
):
    """Отправка произвольного сообщения"""
    result = await send_telegram_message(message, chat_id)
    return result

@router.post("/notify-overdue")
async def notify_overdue_payments(
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Уведомление о просроченных платежах"""
    
    # Получаем просроченные счета из MongoDB
    overdue_invoices = list(invoices_collection.find({
        "status": "overdue"
    }))
    
    if not overdue_invoices:
        return {"message": "Просроченных платежей нет"}
    
    # Формируем сообщение
    message = "<b>🚨 Просроченные платежи</b>\n\n"
    
    total_overdue = 0
    for invoice in overdue_invoices:
        # Получаем клиента
        client = clients_collection.find_one({"id": invoice.get("client_id")})
        project = projects_collection.find_one({"id": invoice.get("project_id")})
        
        if client:
            message += f"📅 <b>{client.get('name', 'Не указан')}</b>\n"
            if project:
                message += f"📁 Проект: {project.get('name', 'Не указан')}\n"
            message += f"💰 Сумма: {invoice.get('amount', 0):,.2f} ₽\n"
            message += f"📝 Счет: {invoice.get('number', 'Не указан')}\n\n"
            
            total_overdue += invoice.get('amount', 0)
    
    message += f"<b>📈 Общая сумма просрочки: {total_overdue:,.2f} ₽</b>"
    
    background_tasks.add_task(send_telegram_message, message)
    
    return {
        "message": f"Уведомление о {len(overdue_invoices)} просроченных платежах отправлено",
        "count": len(overdue_invoices),
        "total_amount": total_overdue
    }

@router.post("/daily-report")
async def send_daily_report(
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Отправка ежедневного отчёта"""
    
    # Получаем статистику
    total_clients = clients_collection.count_documents({})
    total_projects = projects_collection.count_documents({})
    active_projects = projects_collection.count_documents({"status": "in_progress"})
    
    # Неоплаченные счета
    unpaid_invoices = invoices_collection.count_documents({"status": {"$in": ["draft", "sent"]}})
    
    # Просроченные счета
    overdue_invoices = invoices_collection.count_documents({"status": "overdue"})
    
    # Оплаченные счета за сегодня
    today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    today_end = today_start + timedelta(days=1)
    
    paid_today = invoices_collection.count_documents({
        "status": "paid",
        "created_at": {"$gte": today_start, "$lt": today_end}
    })
    
    # Получаем общую выручку за сегодня
    today_invoices = list(invoices_collection.find({
        "status": "paid",
        "created_at": {"$gte": today_start, "$lt": today_end}
    }))
    today_revenue = sum(inv.get('amount', 0) for inv in today_invoices)
    
    message = f"<b>📅 Ежедневный отчёт - {datetime.utcnow().strftime('%d.%m.%Y')}</b>\n\n"
    message += f"👥 Всего клиентов: {total_clients}\n"
    message += f"📁 Всего проектов: {total_projects}\n"
    message += f"🔄 Активные проекты: {active_projects}\n\n"
    message += f"💰 Выручка за сегодня: {today_revenue:,.2f} ₽\n"
    message += f"✅ Оплачено счетов сегодня: {paid_today}\n"
    message += f"📝 Неоплаченные счета: {unpaid_invoices}\n"
    message += f"⚠️ Просроченные счета: {overdue_invoices}\n"
    
    background_tasks.add_task(send_telegram_message, message)
    
    return {"message": "Ежедневный отчёт отправлен"}

@router.get("/test")
async def test_telegram(current_user = Depends(get_current_user)):
    """Тест подключения к Telegram Bot"""
    if not TELEGRAM_BOT_TOKEN:
        return {"status": "error", "message": "Telegram bot token не настроен. Добавьте TELEGRAM_BOT_TOKEN в .env файл"}
    
    test_message = f"🚀 Тест подключения CRM системы\n\n📅 {datetime.utcnow().strftime('%d.%m.%Y %H:%M')}\n✅ Подключение работает!"
    result = await send_telegram_message(test_message)
    
    if 'error' in result:
        return {"status": "error", "message": result['error']}
    
    return {"status": "success", "message": "Тестовое сообщение отправлено", "result": result}
