# 🚀 Celery + Redis Infrastructure

## Обзор

Реализована полная инфраструктура для фоновых задач и автоматизации:
- **Celery** - распределенная очередь задач
- **Redis** - брокер сообщений и результатов
- **Celery Beat** - планировщик периодических задач (cron-like)

## 📦 Компоненты

### 1. Celery Worker
**Назначение:** Выполнение фоновых задач

**Очереди:**
- `integrations` - синхронизация с внешними системами
- `reports` - генерация отчетов
- `notifications` - отправка уведомлений
- `billing` - обработка платежей и подписок
- `celery` - общая очередь

**Запуск:**
```bash
celery -A celery_app worker --loglevel=info --concurrency=4
```

**Статус:**
```bash
supervisorctl status celery-worker
```

### 2. Celery Beat
**Назначение:** Планировщик периодических задач

**Расписание задач:**

| Задача | Расписание | Описание |
|--------|-----------|----------|
| `weekly-financial-summary` | Понедельник 9:00 | Еженедельная финансовая сводка |
| `daily-integration-sync` | Ежедневно 2:00 | Синхронизация интеграций |
| `check-overdue-invoices` | Ежедневно 10:00 | Проверка просроченных счетов |
| `check-trial-expiring` | Ежедневно 8:00 | Проверка истекающих trial |
| `process-billing-renewals` | Ежедневно 3:00 | Обработка продлений подписок |

**Запуск:**
```bash
celery -A celery_app beat --loglevel=info
```

### 3. Redis
**Назначение:** Брокер сообщений и хранилище результатов

**URL:** `redis://localhost:6379/0`

**Проверка:**
```bash
redis-cli ping
# PONG
```

## 📝 Реализованные задачи

### Integrations (`tasks/integrations.py`)

**sync_all_integrations**
- Синхронизация всех активных компаний
- Запускается ежедневно в 2:00 AM
- Вызывает: sync_crm_data, sync_bank_transactions, sync_accounting_data

**sync_crm_data(company_id)**
- Синхронизация данных из CRM (amoCRM, Bitrix24)
- Обновление проектов и клиентов

**sync_bank_transactions(company_id)**
- Синхронизация банковских транзакций
- Сопоставление с счетами
- Обновление статусов платежей

**sync_accounting_data(company_id)**
- Синхронизация бухгалтерских данных
- PlanFact, Finolog, Контур

### Reports (`tasks/reports.py`)

**generate_weekly_financial_summary**
- Генерация еженедельных финансовых сводок для всех компаний
- Запускается каждый понедельник в 9:00 AM

**generate_company_weekly_report(company_id)**
- Генерация отчета для конкретной компании
- Включает:
  - Планируемые поступления
  - Фактические поступления
  - Просрочки
  - Прогноз кассы

**generate_monthly_report(company_id, year, month)**
- Ежемесячный отчет по компании

### Notifications (`tasks/notifications.py`)

**check_overdue_invoices**
- Проверка просроченных счетов
- Обновление статусов
- Отправка уведомлений
- Запускается ежедневно в 10:00 AM

**send_overdue_notification(company_id, invoice_id, client_id)**
- Уведомление о просроченном счете

**send_email(to_email, subject, body, company_id)**
- Отправка email уведомлений

**send_telegram(chat_id, message, company_id)**
- Отправка Telegram уведомлений

### Billing (`tasks/billing.py`)

**check_trial_expiring**
- Проверка истекающих trial подписок
- Уведомление за 3 дня до окончания
- Запускается ежедневно в 8:00 AM

**process_renewals**
- Обработка продлений подписок
- Автоматическое списание
- Запускается ежедневно в 3:00 AM

**process_company_renewal(company_id)**
- Обработка продления для конкретной компании
- Интеграция с Тинькофф эквайринг (TODO)

**freeze_expired_companies**
- Заморозка компаний с истекшими подписками

## 🔌 API Endpoints

### POST `/api/tasks/trigger`
Запустить задачу вручную

**Request:**
```json
{
  "task_name": "sync_crm",
  "company_id": "company_id_here",
  "params": {}
}
```

**Доступные задачи:**
- `sync_crm` - Синхронизация CRM
- `sync_bank` - Синхронизация банка
- `weekly_report` - Еженедельный отчет
- `process_renewal` - Обработка продления

**Response:**
```json
{
  "message": "Task 'sync_crm' triggered",
  "task_id": "task-uuid",
  "company_id": "company_id"
}
```

### GET `/api/tasks/status/{task_id}`
Проверить статус задачи

**Response:**
```json
{
  "task_id": "task-uuid",
  "status": "SUCCESS",
  "ready": true,
  "result": {"status": "success", "company_id": "..."}
}
```

### GET `/api/tasks/stats`
Получить статистику Celery workers

**Response:**
```json
{
  "workers": {...},
  "active_tasks": {...},
  "scheduled_tasks": {...},
  "registered_tasks": {...}
}
```

### GET `/api/tasks/scheduled`
Получить список запланированных задач

**Response:**
```json
{
  "scheduled_tasks": [
    {
      "name": "weekly-financial-summary",
      "task": "tasks.reports.generate_weekly_financial_summary",
      "schedule": "crontab: 0 9 * * 1",
      "enabled": true
    }
  ]
}
```

### POST `/api/tasks/cancel/{task_id}`
Отменить выполняющуюся задачу

## 🧪 Тестирование

### Проверка работы Celery

```bash
# Проверка workers
celery -A celery_app inspect active

# Проверка registered tasks
celery -A celery_app inspect registered

# Проверка stats
celery -A celery_app inspect stats
```

### Запуск задачи из Python

```python
from tasks.reports import generate_company_weekly_report

# Синхронный вызов
result = generate_company_weekly_report(company_id="test123")

# Асинхронный вызов (в очередь)
task = generate_company_weekly_report.delay(company_id="test123")
print(task.id)  # ID задачи
print(task.status)  # Статус
print(task.result)  # Результат (когда готово)
```

### Тестирование через API

```bash
# Запустить еженедельный отчет
curl -X POST https://agencyops.preview.emergentagent.com/api/tasks/trigger \
  -H "Authorization: Bearer token" \
  -H "X-User-ID: user_id" \
  -H "X-Company-ID: company_id" \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "weekly_report",
    "company_id": "company_id"
  }'

# Проверить статус
curl -X GET https://agencyops.preview.emergentagent.com/api/tasks/status/{task_id} \
  -H "Authorization: Bearer token"
```

## 📊 Мониторинг

### Supervisor Logs

```bash
# Worker logs
tail -f /var/log/supervisor/celery-worker.log

# Beat logs
tail -f /var/log/supervisor/celery-beat.log

# Redis logs
tail -f /var/log/supervisor/redis.log
```

### Flower (Web UI для Celery)
Flower установлен, можно запустить для мониторинга:

```bash
celery -A celery_app flower
# Откроется на http://localhost:5555
```

## 🔧 Конфигурация

### Celery App (`celery_app.py`)
- Брокер: Redis
- Backend: Redis
- Сериализация: JSON
- Таймауты: 30 минут
- Результаты хранятся: 1 час

### Environment Variables
```env
REDIS_URL=redis://localhost:6379/0
```

### Supervisor Config (`/etc/supervisor/conf.d/celery.conf`)
- celery-worker: 4 concurrent workers
- celery-beat: планировщик
- Автоматический перезапуск при сбое

## 🚀 Готово к использованию!

Инфраструктура Celery + Redis полностью настроена и работает:

✅ Celery Worker запущен (4 воркера)
✅ Celery Beat запущен (планировщик)
✅ Redis запущен
✅ 15+ задач зарегистрировано
✅ 5 периодических задач настроено
✅ API endpoints для управления
✅ Логирование и мониторинг

Можно использовать для:
- Интеграций с внешними системами
- Автоматических отчетов
- Email/SMS уведомлений
- Обработки платежей
- Любых долгих операций в фоне
