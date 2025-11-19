# 📚 ПОЛНАЯ API ДОКУМЕНТАЦИЯ
## AgencyOps Platform API Reference

**Version:** 1.0.0  
**Base URL:** `https://your-domain.com/api`  
**Authentication:** Bearer Token (JWT) + X-Company-ID Header

---

## 🔐 АУТЕНТИФИКАЦИЯ

### Headers (обязательные для всех запросов):

```http
Authorization: Bearer <jwt_token>
X-Company-ID: <company_id>
Content-Type: application/json
```

### Получение токена:

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

## 🏢 COMPANIES API

### 1. Создать компанию
```http
POST /api/companies
```

**Body:**
```json
{
  "name": "Моё Агентство",
  "legal_name": "ООО Моё Агентство",
  "inn": "1234567890",
  "address": "г. Москва, ул. Ленина, д. 1",
  "subscription_plan": "startup"
}
```

**Response:**
```json
{
  "id": "comp_123",
  "name": "Моё Агентство",
  "subscription_status": "trial",
  "max_users": 5,
  "max_projects": 10,
  "created_at": "2024-11-19T10:00:00Z"
}
```

### 2. Получить мои компании
```http
GET /api/companies/my
```

**Response:**
```json
{
  "companies": [
    {
      "id": "comp_123",
      "name": "Моё Агентство",
      "role": "owner",
      "permissions": ["all"]
    }
  ]
}
```

---

## 👥 CLIENTS API

### 1. Список клиентов
```http
GET /api/clients
X-Company-ID: comp_123
```

**Query Parameters:**
- `status` (optional): active, inactive, archived
- `search` (optional): поиск по имени/email
- `limit` (optional): кол-во записей (default: 50)
- `offset` (optional): смещение

**Response:**
```json
{
  "clients": [
    {
      "id": "client_456",
      "tenant_id": "comp_123",
      "name": "ООО Клиент",
      "email": "client@example.com",
      "phone": "+7 999 123-45-67",
      "status": "active",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 25
}
```

### 2. Создать клиента
```http
POST /api/clients
X-Company-ID: comp_123
```

**Body:**
```json
{
  "name": "ООО Новый Клиент",
  "email": "newclient@example.com",
  "phone": "+7 999 888-77-66",
  "address": "г. Санкт-Петербург",
  "inn": "9876543210",
  "contact_person": "Иван Иванов",
  "status": "active"
}
```

**Response:**
```json
{
  "id": "client_789",
  "tenant_id": "comp_123",
  "name": "ООО Новый Клиент",
  "created_at": "2024-11-19T10:00:00Z"
}
```

### 3. Обновить клиента
```http
PUT /api/clients/{client_id}
X-Company-ID: comp_123
```

### 4. Удалить клиента
```http
DELETE /api/clients/{client_id}
X-Company-ID: comp_123
```

---

## 📁 PROJECTS API

### 1. Список проектов
```http
GET /api/projects
X-Company-ID: comp_123
```

**Query Parameters:**
- `status`: active, completed, on_hold, cancelled
- `client_id`: фильтр по клиенту

**Response:**
```json
{
  "projects": [
    {
      "id": "proj_111",
      "tenant_id": "comp_123",
      "name": "Разработка сайта",
      "client_id": "client_456",
      "client_name": "ООО Клиент",
      "status": "active",
      "budget": 500000,
      "start_date": "2024-11-01",
      "end_date": "2024-12-31",
      "progress": 45,
      "created_at": "2024-11-01T10:00:00Z"
    }
  ]
}
```

### 2. Создать проект
```http
POST /api/projects
X-Company-ID: comp_123
```

**Body:**
```json
{
  "name": "Новый проект",
  "client_id": "client_456",
  "description": "Описание проекта",
  "budget": 750000,
  "start_date": "2024-12-01",
  "end_date": "2025-03-31",
  "status": "active",
  "manager_id": "user_123"
}
```

---

## 📋 PROJECT FLOW API (Kanban)

### 1. Получить колонки Kanban
```http
GET /api/project-flow/columns
X-Company-ID: comp_123
```

**Response:**
```json
{
  "columns": [
    {
      "id": "col_1",
      "name": "Backlog",
      "type": "backlog",
      "color": "#94A3B8",
      "order": 0,
      "wip_limit": null
    },
    {
      "id": "col_2",
      "name": "In Progress",
      "type": "in_progress",
      "color": "#F59E0B",
      "order": 2,
      "wip_limit": 5
    }
  ]
}
```

### 2. Создать колонку
```http
POST /api/project-flow/columns
X-Company-ID: comp_123
```

**Body:**
```json
{
  "name": "Review",
  "type": "review",
  "color": "#8B5CF6",
  "order": 3,
  "wip_limit": 3
}
```

### 3. Получить этапы (stages)
```http
GET /api/project-flow/stages
X-Company-ID: comp_123
```

**Query Parameters:**
- `project_id`: фильтр по проекту
- `status`: backlog, todo, in_progress, review, done

**Response:**
```json
{
  "stages": [
    {
      "id": "stage_1",
      "project_id": "proj_111",
      "name": "Дизайн главной страницы",
      "description": "Создать макет главной страницы",
      "column_id": "col_2",
      "status": "in_progress",
      "stage_type": "task",
      "assigned_to": "user_123",
      "due_date": "2024-11-25",
      "progress": 60,
      "created_at": "2024-11-10T10:00:00Z"
    }
  ]
}
```

### 4. Создать этап
```http
POST /api/project-flow/stages
X-Company-ID: comp_123
```

**Body:**
```json
{
  "project_id": "proj_111",
  "name": "Разработка формы контактов",
  "description": "Создать форму с валидацией",
  "column_id": "col_1",
  "stage_type": "task",
  "assigned_to": "user_456",
  "due_date": "2024-11-30",
  "progress": 0
}
```

### 5. Обновить этап (перемещение)
```http
PUT /api/project-flow/stages/{stage_id}
X-Company-ID: comp_123
```

**Body:**
```json
{
  "column_id": "col_3",
  "status": "done",
  "progress": 100
}
```

---

## 💰 FINANCIAL FLOW API

### 1. Получить сводку (план vs факт)
```http
GET /api/financial-flow/summary?period=month
X-Company-ID: comp_123
```

**Query Parameters:**
- `period`: week, month, quarter, year

**Response:**
```json
{
  "summary": {
    "total_planned": 5000000,
    "total_actual": 4750000,
    "achievement_rate": 95.0,
    "on_time_count": 12,
    "on_time_amount": 3500000,
    "pending_count": 5,
    "pending_amount": 1250000,
    "overdue_count": 2,
    "overdue_amount": 250000,
    "trend": [
      {
        "period": "2024-10",
        "planned_income": 1500000,
        "actual_income": 1450000,
        "expenses": 800000
      },
      {
        "period": "2024-11",
        "planned_income": 2000000,
        "actual_income": 1900000,
        "expenses": 1000000
      }
    ]
  }
}
```

### 2. Сравнение по проектам/клиентам
```http
GET /api/financial-flow/comparison?period=month
X-Company-ID: comp_123
```

**Response:**
```json
{
  "comparison": {
    "by_project": [
      {
        "id": "proj_111",
        "name": "Проект А",
        "planned": 500000,
        "actual": 480000
      }
    ],
    "by_client": [
      {
        "id": "client_456",
        "name": "Клиент А",
        "planned": 1000000,
        "actual": 950000
      }
    ]
  }
}
```

---

## 👨‍💼 TEAM LOAD API

### 1. Обзор загрузки команды
```http
GET /api/team-load/overview
X-Company-ID: comp_123
```

**Response:**
```json
{
  "total_members": 10,
  "avg_workload": 78.5,
  "underloaded_count": 2,
  "normal_count": 6,
  "overloaded_count": 2,
  "total_capacity": 1600,
  "total_allocated": 1256,
  "members": [
    {
      "id": "user_123",
      "name": "Иван Петров",
      "role": "Дизайнер",
      "workload_percent": 85.0,
      "available_hours": 160,
      "allocated_hours": 136,
      "project_count": 3,
      "active_projects": ["Проект А", "Проект Б"]
    }
  ]
}
```

### 2. Детали загрузки сотрудника
```http
GET /api/team-load/member/{user_id}
X-Company-ID: comp_123
```

**Response:**
```json
{
  "member": {
    "id": "user_123",
    "name": "Иван Петров",
    "workload_details": {
      "by_project": [
        {
          "project_id": "proj_111",
          "project_name": "Проект А",
          "hours_allocated": 80,
          "period": "2024-11"
        }
      ]
    }
  }
}
```

---

## 🎯 CLIENT 360 API

### 1. Полный профиль клиента
```http
GET /api/client-360/{client_id}
X-Company-ID: comp_123
```

**Response:**
```json
{
  "client": {
    "id": "client_456",
    "name": "ООО Клиент",
    "email": "client@example.com",
    "phone": "+7 999 123-45-67",
    "status": "active",
    "created_at": "2024-01-15T10:00:00Z"
  },
  "history": {
    "total_projects": 8,
    "active_projects": 2,
    "completed_projects": 6,
    "total_revenue": 4500000,
    "lifetime_value": 5200000,
    "avg_check": 562500,
    "health_score": 85,
    "unpaid_invoices": 1,
    "unpaid_amount": 250000,
    "revenue_trend": [
      {
        "period": "2024-01",
        "amount": 500000
      },
      {
        "period": "2024-02",
        "amount": 750000
      }
    ]
  },
  "projects": [
    {
      "id": "proj_111",
      "name": "Проект А",
      "status": "active",
      "budget": 500000,
      "progress": 45
    }
  ],
  "invoices": [
    {
      "id": "inv_789",
      "invoice_number": "INV-2024-001",
      "amount": 250000,
      "status": "pending",
      "date": "2024-11-01"
    }
  ],
  "interactions": [
    {
      "type": "meeting",
      "title": "Встреча по проекту",
      "description": "Обсудили следующий этап",
      "date": "2024-11-15T14:00:00Z"
    },
    {
      "type": "email",
      "title": "Отправили предложение",
      "description": "КП на новый проект",
      "date": "2024-11-10T10:00:00Z"
    }
  ]
}
```

---

## ⚠️ RISK ANALYZER API

### 1. Обзор рисков
```http
GET /api/risk-analyzer/overview?period=month
X-Company-ID: comp_123
```

**Response:**
```json
{
  "overview": {
    "overall_risk_score": 42.5,
    "critical_risk_count": 2,
    "critical_risk_value": 1500000,
    "high_risk_count": 5,
    "high_risk_value": 2500000,
    "medium_risk_count": 8,
    "low_risk_count": 12,
    "low_risk_percent": 44.4,
    "total_items": 27,
    "budget_risk": 35,
    "timeline_risk": 50,
    "team_risk": 40,
    "client_risk": 30,
    "quality_risk": 45
  },
  "projects": [
    {
      "id": "proj_222",
      "name": "Проект в зоне риска",
      "client_name": "Клиент Б",
      "risk_level": "high",
      "risk_score": 75.5,
      "risk_factors": ["Превышение бюджета", "Задержка сроков"],
      "budget": 800000,
      "progress": 30,
      "days_remaining": -5
    }
  ],
  "clients": [
    {
      "id": "client_789",
      "name": "Клиент в зоне оттока",
      "lifetime_value": 2000000,
      "days_since_last_contact": 45,
      "project_count": 1,
      "churn_risk": 68.5,
      "churn_indicators": ["Нет активности 45 дней", "Снижение заказов"]
    }
  ]
}
```

### 2. Рекомендации
```http
GET /api/risk-analyzer/recommendations
X-Company-ID: comp_123
```

**Response:**
```json
{
  "recommendations": [
    {
      "title": "Связаться с клиентом Б",
      "description": "Клиент не выходил на связь 45 дней. Рекомендуется назначить встречу.",
      "priority": "high"
    },
    {
      "title": "Пересмотреть бюджет проекта X",
      "description": "Проект превышает бюджет на 20%. Необходимо обсудить с клиентом.",
      "priority": "high"
    }
  ]
}
```

---

## 📊 DASHBOARDS API

### 1. Owner Dashboard
```http
GET /api/dashboards/owner?period=month
X-Company-ID: comp_123
```

**Response:**
```json
{
  "financial_metrics": {
    "current_mrr": 450000,
    "mrr_growth": 12.5,
    "forecast_mrr": 495000,
    "avg_check": 562500,
    "week_received": 180000,
    "total_overdue": 250000,
    "clients_in_overdue": 2,
    "overdue_count": 3
  },
  "project_metrics": {
    "active_projects": 12,
    "projects_growth": 8.3,
    "completed_projects": 6,
    "success_rate": 94.5,
    "planned_projects": 4,
    "active_budget": 6000000,
    "planned_budget": 2500000,
    "problematic_projects": 2
  },
  "client_metrics": {
    "active_clients": 25,
    "clients_growth": 5.2,
    "churn_risk": 3
  },
  "risk_metrics": {
    "projects_at_risk": 7,
    "low_risk": 12,
    "medium_risk": 8,
    "high_risk": 5,
    "portfolio_risk": 42.5
  }
}
```

---

## 💳 BILLING API

### 1. Получить тарифные планы
```http
GET /api/billing/plans
```

**Response:**
```json
{
  "plans": [
    {
      "id": "free_plan",
      "name": "Free",
      "monthly_price": 0,
      "max_users": 5,
      "max_projects": 10,
      "features": ["Базовый функционал"]
    },
    {
      "id": "startup_plan",
      "name": "Startup",
      "monthly_price": 5990,
      "quarterly_price": 16170,
      "yearly_price": 59880,
      "max_users": 15,
      "max_projects": 50,
      "features": [
        "Все из Free",
        "Интеграции",
        "Приоритетная поддержка"
      ]
    }
  ]
}
```

### 2. Получить текущую подписку
```http
GET /api/billing/subscription
X-Company-ID: comp_123
```

**Response:**
```json
{
  "subscription": {
    "id": "sub_123",
    "tenant_id": "comp_123",
    "plan_id": "startup_plan",
    "plan_type": "startup",
    "billing_cycle": "monthly",
    "status": "active",
    "current_period_start": "2024-11-01T00:00:00Z",
    "current_period_end": "2024-12-01T00:00:00Z",
    "rebill_id": "rb_456",
    "cancel_at_period_end": false
  }
}
```

### 3. Создать платеж для подписки
```http
POST /api/billing/subscription/create-payment
X-Company-ID: comp_123
```

**Body:**
```json
{
  "plan_id": "startup_plan",
  "billing_cycle": "monthly"
}
```

**Response:**
```json
{
  "payment_url": "https://securepay.tinkoff.ru/...",
  "payment_id": "12345678",
  "order_id": "SUB_comp_123_abc123",
  "amount": 5990
}
```

### 4. Webhook от Tinkoff (вызывается автоматически)
```http
POST /api/billing/webhook/tinkoff
```

**Body (от Tinkoff):**
```json
{
  "TerminalKey": "...",
  "OrderId": "SUB_comp_123_abc123",
  "Success": true,
  "Status": "CONFIRMED",
  "PaymentId": "12345678",
  "Amount": 599000,
  "RebillId": "rb_789",
  "Token": "signature_hash"
}
```

---

## 🔗 INTEGRATIONS API

### 1. Получить список интеграций
```http
GET /api/integrations
X-Company-ID: comp_123
```

**Response:**
```json
{
  "integrations": [
    {
      "id": "int_123",
      "name": "sCloud Accounting",
      "type": "accounting",
      "provider": "scloud",
      "status": "active",
      "is_enabled": true,
      "last_sync": "2024-11-19T10:00:00Z",
      "created_at": "2024-11-01T10:00:00Z"
    }
  ]
}
```

### 2. Начать OAuth flow для sCloud
```http
GET /api/integrations/scloud/authorize
X-Company-ID: comp_123
```

**Response:**
```json
{
  "authorization_url": "https://scloud.live/oauth/authorize?...",
  "state": "random_state_token"
}
```

### 3. OAuth callback (автоматический)
```http
GET /api/integrations/scloud/callback?code=...&state=...
```

### 4. Запустить синхронизацию
```http
POST /api/integrations/scloud/{integration_id}/sync
X-Company-ID: comp_123
```

**Response:**
```json
{
  "message": "Sync completed successfully",
  "invoices_synced": 15,
  "transactions_synced": 42,
  "log_id": "log_789"
}
```

### 5. Логи интеграций
```http
GET /api/integrations/{integration_id}/logs
X-Company-ID: comp_123
```

**Response:**
```json
{
  "logs": [
    {
      "id": "log_789",
      "sync_type": "manual",
      "started_at": "2024-11-19T10:00:00Z",
      "completed_at": "2024-11-19T10:05:00Z",
      "status": "completed",
      "records_processed": 57,
      "errors": []
    }
  ]
}
```

---

## 📄 INVOICES API

### 1. Список счетов
```http
GET /api/invoices
X-Company-ID: comp_123
```

**Query Parameters:**
- `status`: draft, sent, paid, overdue, cancelled
- `client_id`: фильтр по клиенту

**Response:**
```json
{
  "invoices": [
    {
      "id": "inv_789",
      "tenant_id": "comp_123",
      "invoice_number": "INV-2024-001",
      "client_id": "client_456",
      "client_name": "ООО Клиент",
      "amount": 250000,
      "status": "paid",
      "date": "2024-11-01",
      "due_date": "2024-11-15",
      "paid_date": "2024-11-10",
      "created_at": "2024-11-01T10:00:00Z"
    }
  ]
}
```

### 2. Создать счет
```http
POST /api/invoices
X-Company-ID: comp_123
```

**Body:**
```json
{
  "client_id": "client_456",
  "invoice_number": "INV-2024-002",
  "amount": 350000,
  "date": "2024-11-19",
  "due_date": "2024-12-03",
  "description": "Разработка сайта - этап 1",
  "status": "sent"
}
```

---

## 💸 PAYMENTS API

### 1. Список платежей
```http
GET /api/payments
X-Company-ID: comp_123
```

**Response:**
```json
{
  "payments": [
    {
      "id": "pay_555",
      "tenant_id": "comp_123",
      "invoice_id": "inv_789",
      "client_id": "client_456",
      "amount": 250000,
      "payment_date": "2024-11-10",
      "payment_method": "bank_transfer",
      "status": "completed",
      "created_at": "2024-11-10T15:30:00Z"
    }
  ]
}
```

### 2. Создать платеж
```http
POST /api/payments
X-Company-ID: comp_123
```

**Body:**
```json
{
  "invoice_id": "inv_789",
  "amount": 250000,
  "payment_date": "2024-11-19",
  "payment_method": "bank_transfer",
  "notes": "Оплата по договору №123"
}
```

---

## ⚙️ КОДЫ ОШИБОК

| Код | Описание |
|-----|----------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - неверные данные |
| 401 | Unauthorized - нет токена или он недействителен |
| 403 | Forbidden - нет прав доступа |
| 404 | Not Found - ресурс не найден |
| 409 | Conflict - дублирование данных |
| 422 | Unprocessable Entity - ошибка валидации |
| 429 | Too Many Requests - превышен лимит запросов |
| 500 | Internal Server Error |

**Формат ошибки:**
```json
{
  "detail": "Описание ошибки",
  "error_code": "INVALID_CLIENT_ID"
}
```

---

## 📝 ПРИМЕЧАНИЯ

### Rate Limiting:
- **Default:** 1000 запросов в час на компанию
- **Burst:** до 100 запросов в минуту

### Pagination:
Для списков используйте параметры:
- `limit`: количество записей (default: 50, max: 100)
- `offset`: смещение (default: 0)

### Date Format:
Все даты в формате ISO 8601: `YYYY-MM-DDTHH:MM:SSZ` (UTC)

### Tenant Isolation:
Все запросы автоматически фильтруются по `tenant_id` из header `X-Company-ID`

---

**Документация обновлена:** 19.11.2024  
**Контакты:** support@agencyops.com
