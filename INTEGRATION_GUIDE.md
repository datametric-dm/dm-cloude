# 🔗 INTEGRATION GUIDE
## Полное руководство по интеграциям AgencyOps

**Version:** 1.0.0  
**Updated:** 19.11.2024

---

## 📋 СОДЕРЖАНИЕ

1. [Общая архитектура интеграций](#общая-архитектура)
2. [Tinkoff Acquiring (Billing)](#tinkoff-acquiring)
3. [sCloud.ru (Accounting)](#scloudru)
4. [amoCRM (CRM)](#amocrm)
5. [Bitrix24 (CRM)](#bitrix24)
6. [Webhook endpoints](#webhook-endpoints)
7. [Data Mapping](#data-mapping)

---

## 🏗️ ОБЩАЯ АРХИТЕКТУРА

### Типы интеграций:

```
┌─────────────────────────────────────────────┐
│         AgencyOps Platform                   │
│                                              │
│  ┌────────────┐  ┌────────────┐            │
│  │  Backend   │  │  Frontend  │            │
│  │   API      │  │     UI     │            │
│  └─────┬──────┘  └────────────┘            │
│        │                                     │
│  ┌─────▼─────────────────────┐             │
│  │  Integration Services      │             │
│  │  - TinkoffService         │             │
│  │  - SCloudService          │             │
│  │  - AmoCRMService          │             │
│  │  - Bitrix24Service        │             │
│  └─────┬─────────────────────┘             │
└────────┼─────────────────────────────────┘
         │
    ┌────▼────┐
    │ External│
    │   APIs  │
    └─────────┘
```

### Направления данных:

**Входящие (Pull):**
- CRM (amoCRM, Bitrix24) → Clients, Projects
- Accounting (sCloud) → Invoices, Payments
- Bank APIs → Payments, Transactions

**Исходящие (Push):**
- Clients → CRM
- Invoices → Accounting
- Projects → Task Managers

**Двунаправленные (Sync):**
- Billing ↔ Tinkoff Acquiring (webhooks)

---

## 💳 TINKOFF ACQUIRING

### Назначение:
Обработка платежей по подпискам с автоматическим списанием (recurring)

### Credentials:
```bash
TINKOFF_TERMINAL_KEY="your_terminal_key"
TINKOFF_TERMINAL_PASSWORD="your_terminal_password"
TINKOFF_DEBUG_MODE="false"  # true для тестового окружения
```

**Как получить:**
1. Зарегистрироваться на https://business.tinkoff.ru
2. Подключить интернет-эквайринг
3. Получить Terminal Key и Password в личном кабинете
4. Настроить webhook URL: `https://your-domain.com/api/billing/webhook/tinkoff`

### API Flow:

#### 1. Создание платежа (Init):

**AgencyOps → Tinkoff:**
```python
# backend/services/tinkoff_service.py
await tinkoff_service.init_payment(
    amount=599000,  # в копейках (5990 руб)
    order_id="SUB_comp_123_abc",
    customer_key="COMPANY_comp_123",
    description="Подписка Startup - Моё Агентство",
    email="owner@myagency.com",
    recurrent=True  # для recurring платежей
)
```

**Response от Tinkoff:**
```json
{
  "Success": true,
  "PaymentId": "12345678",
  "PaymentURL": "https://securepay.tinkoff.ru/...",
  "Status": "NEW"
}
```

#### 2. Пользователь оплачивает:
- Переход по `PaymentURL`
- Ввод данных карты
- 3D-Secure подтверждение

#### 3. Webhook от Tinkoff:

**Tinkoff → AgencyOps:**
```http
POST https://your-domain.com/api/billing/webhook/tinkoff
Content-Type: application/json

{
  "TerminalKey": "your_terminal_key",
  "OrderId": "SUB_comp_123_abc",
  "Success": true,
  "Status": "CONFIRMED",
  "PaymentId": "12345678",
  "Amount": 599000,
  "RebillId": "rb_789",
  "Token": "HMAC-SHA256_signature",
  "CardId": "card_456",
  "Pan": "430000******0777"
}
```

**Обработка в AgencyOps:**
```python
# Проверка подписи
is_valid = tinkoff_service.validate_webhook_signature(
    webhook_data, 
    provided_signature
)

# Активация подписки
if status == "CONFIRMED":
    - Обновить subscription.status = "active"
    - Сохранить rebill_id для recurring
    - Обновить company.subscription_plan
    - Установить current_period_end = +30 дней
```

#### 4. Recurring платеж (автосписание):

**Celery Task (ежедневно):**
```python
# Найти подписки с истекающим периодом
subscriptions = find_expiring_subscriptions(days=3)

for sub in subscriptions:
    # Автоматическое списание
    result = await tinkoff_service.charge_recurring(
        payment_id=sub.last_payment_id,
        rebill_id=sub.rebill_id,
        amount=sub.plan_amount
    )
```

### Маппинг данных:

| AgencyOps Field | Tinkoff Field | Type | Notes |
|----------------|---------------|------|-------|
| subscription.id | OrderId | string | Префикс SUB_ |
| company.id | CustomerKey | string | Префикс COMPANY_ |
| plan.monthly_price * 100 | Amount | integer | В копейках |
| user.email | Email | string | Для чека |
| subscription.rebill_id | RebillId | string | Для recurring |
| billing_transaction.payment_id | PaymentId | string | ID платежа |

### Error Handling:

```python
# Обработка ошибок
if response.get("ErrorCode"):
    errors = {
        "3": "Карта не найдена",
        "6": "Операция отклонена",
        "9": "Недостаточно средств",
        "99": "Ошибка банка"
    }
```

---

## 🧾 SCLOUD.RU

### Назначение:
Синхронизация финансовых данных (счета, транзакции)

### Credentials:
```bash
SCLOUD_CLIENT_ID="your_client_id"
SCLOUD_CLIENT_SECRET="your_client_secret"
SCLOUD_REDIRECT_URI="https://your-domain.com/api/integrations/scloud/callback"
```

**Как получить:**
1. Регистрация на https://developers.scloud.live
2. Создать приложение
3. Получить Client ID и Secret
4. Настроить Redirect URI

### OAuth 2.0 Flow:

#### 1. Инициация авторизации:

**AgencyOps → User:**
```http
GET /api/integrations/scloud/authorize
X-Company-ID: comp_123

Response:
{
  "authorization_url": "https://scloud.live/oauth/authorize?client_id=...&state=...",
  "state": "random_secure_token"
}
```

#### 2. Пользователь авторизуется в sCloud

#### 3. Callback с кодом:

**sCloud → AgencyOps:**
```http
GET /api/integrations/scloud/callback?code=AUTH_CODE&state=random_secure_token
```

**AgencyOps обменивает код на токены:**
```python
token_response = await scloud_client.exchange_code_for_token(code)
# {
#   "access_token": "...",
#   "refresh_token": "...",
#   "expires_in": 3600
# }

# Сохранить в integrations_collection
```

#### 4. Синхронизация данных:

**Manual Sync:**
```http
POST /api/integrations/scloud/{integration_id}/sync
X-Company-ID: comp_123
```

**Automatic Sync (Celery):**
```python
# Каждые 6 часов
@celery.task
def sync_scloud_data():
    integrations = find_active_integrations(provider="scloud")
    
    for integration in integrations:
        # Синхронизация счетов
        invoices = await scloud_client.sync_invoices(
            company_id=integration.tenant_id,
            since_date=last_sync_date
        )
        
        # Создать/обновить счета в AgencyOps
        for invoice in invoices.get("items", []):
            upsert_invoice(map_scloud_invoice(invoice))
        
        # Синхронизация транзакций
        transactions = await scloud_client.sync_transactions(
            company_id=integration.tenant_id,
            start_date=last_sync_date
        )
        
        # Создать платежи
        for transaction in transactions.get("items", []):
            upsert_payment(map_scloud_transaction(transaction))
```

### Маппинг данных:

#### Invoices (sCloud → AgencyOps):

| sCloud Field | AgencyOps Field | Transform |
|-------------|-----------------|-----------|
| id | external_id | string |
| number | invoice_number | string |
| amount | amount | float |
| currency | - | Всегда RUB |
| date | date | ISO date |
| due_date | due_date | ISO date |
| status | status | Map: new→draft, sent→sent, paid→paid |
| client.name | client_name | string (найти client_id по имени) |
| items[] | line_items | array |

**Mapping Function:**
```python
def map_scloud_invoice(scloud_invoice):
    # Найти клиента по имени или создать нового
    client = find_or_create_client(
        name=scloud_invoice["client"]["name"],
        email=scloud_invoice["client"]["email"]
    )
    
    return {
        "tenant_id": company_id,
        "external_id": scloud_invoice["id"],
        "external_source": "scloud",
        "invoice_number": scloud_invoice["number"],
        "client_id": client["id"],
        "amount": float(scloud_invoice["amount"]),
        "date": parse_date(scloud_invoice["date"]),
        "due_date": parse_date(scloud_invoice["due_date"]),
        "status": map_status(scloud_invoice["status"]),
        "synced_at": datetime.utcnow()
    }
```

#### Transactions (sCloud → AgencyOps):

| sCloud Field | AgencyOps Field | Transform |
|-------------|-----------------|-----------|
| id | external_id | string |
| amount | amount | float |
| date | payment_date | ISO date |
| type | payment_method | Map: bank→bank_transfer, card→card |
| description | notes | string |
| invoice_id | invoice_id | Найти по external_id |

### Token Refresh:

```python
# Автоматическое обновление токена
async def ensure_valid_token():
    if token_expiry <= datetime.utcnow():
        new_tokens = await scloud_client.refresh_access_token()
        # Обновить в БД
        update_integration_tokens(integration_id, new_tokens)
```

---

## 📞 AMOCRM

### Назначение:
Синхронизация клиентов и сделок (двунаправленная)

### Credentials (потребуется):
```bash
AMOCRM_SUBDOMAIN="your_subdomain"  # например: mycompany
AMOCRM_CLIENT_ID="your_client_id"
AMOCRM_CLIENT_SECRET="your_client_secret"
AMOCRM_REDIRECT_URI="https://your-domain.com/api/integrations/amocrm/callback"
```

**Как получить:**
1. https://www.amocrm.ru/developers/content/oauth/step-by-step
2. Создать интеграцию
3. Получить Client ID и Secret
4. Настроить Redirect URI и права доступа (scopes)

### OAuth Flow (аналогично sCloud)

### Webhook Setup:

**Регистрация webhook в amoCRM:**
```python
# После OAuth авторизации
await amocrm_client.register_webhook(
    url="https://your-domain.com/api/integrations/amocrm/webhook",
    events=["add_lead", "update_lead", "add_contact", "update_contact"]
)
```

### Data Sync Flow:

#### 1. Входящие (amoCRM → AgencyOps):

**Webhook от amoCRM:**
```http
POST /api/integrations/amocrm/webhook
Content-Type: application/json

{
  "leads": {
    "add": [
      {
        "id": 123456,
        "name": "Новая сделка",
        "price": 500000,
        "status_id": 142,
        "pipeline_id": 1,
        "responsible_user_id": 789,
        "created_at": 1700400000,
        "updated_at": 1700400000,
        "custom_fields": [
          {
            "id": 111,
            "name": "Email",
            "values": [{"value": "client@example.com"}]
          }
        ],
        "_embedded": {
          "contacts": [
            {
              "id": 654321,
              "name": "Иван Петров"
            }
          ]
        }
      }
    ]
  }
}
```

**Обработка в AgencyOps:**
```python
async def handle_amocrm_webhook(data):
    for lead in data.get("leads", {}).get("add", []):
        # Маппинг amoCRM lead → AgencyOps project
        
        # 1. Найти или создать клиента
        contact = lead["_embedded"]["contacts"][0]
        client = await find_or_create_client({
            "external_id": str(contact["id"]),
            "external_source": "amocrm",
            "name": contact["name"],
            "email": extract_custom_field(lead, "Email")
        })
        
        # 2. Создать проект
        project = await create_project({
            "external_id": str(lead["id"]),
            "external_source": "amocrm",
            "name": lead["name"],
            "client_id": client["id"],
            "budget": lead["price"],
            "status": map_amocrm_status(lead["status_id"]),
            "manager_id": map_user(lead["responsible_user_id"])
        })
```

### Маппинг данных:

#### Leads → Projects:

| amoCRM Field | AgencyOps Field | Notes |
|-------------|-----------------|-------|
| id | external_id | string |
| name | name | string |
| price | budget | float |
| status_id | status | Нужна таблица соответствия |
| pipeline_id | - | Игнорируем или используем для категоризации |
| responsible_user_id | manager_id | Маппинг пользователей |
| created_at | created_at | Unix timestamp → ISO |
| custom_fields[email] | - | Для контакта |
| custom_fields[phone] | - | Для контакта |

**Status Mapping:**
```python
AMOCRM_STATUS_MAP = {
    "142": "active",      # Первичный контакт
    "143": "active",      # Переговоры
    "144": "active",      # Принимают решение
    "145": "on_hold",     # Отложено
    "146": "completed",   # Успешно реализовано
    "147": "cancelled"    # Закрыто и не реализовано
}
```

#### Contacts → Clients:

| amoCRM Field | AgencyOps Field | Notes |
|-------------|-----------------|-------|
| id | external_id | string |
| name | name | string |
| custom_fields[email] | email | Custom field |
| custom_fields[phone] | phone | Custom field |
| custom_fields[position] | contact_person | Custom field |
| company_name | - | Использовать как часть name |

#### 2. Исходящие (AgencyOps → amoCRM):

**При создании клиента в AgencyOps:**
```python
async def sync_client_to_amocrm(client):
    # Создать контакт в amoCRM
    amocrm_contact = await amocrm_client.create_contact({
        "name": client["name"],
        "custom_fields_values": [
            {
                "field_id": 111,  # Email
                "values": [{"value": client["email"]}]
            },
            {
                "field_id": 112,  # Phone
                "values": [{"value": client["phone"]}]
            }
        ]
    })
    
    # Сохранить связку
    await update_client(client["id"], {
        "external_id": amocrm_contact["id"],
        "external_source": "amocrm"
    })
```

**При создании проекта в AgencyOps:**
```python
async def sync_project_to_amocrm(project):
    # Создать сделку в amoCRM
    amocrm_lead = await amocrm_client.create_lead({
        "name": project["name"],
        "price": project["budget"],
        "status_id": reverse_map_status(project["status"]),
        "pipeline_id": 1,  # Default pipeline
        "_embedded": {
            "contacts": [
                {
                    "id": project["client"]["external_id"]
                }
            ]
        }
    })
    
    # Сохранить связку
    await update_project(project["id"], {
        "external_id": amocrm_lead["id"],
        "external_source": "amocrm"
    })
```

---

## 🔷 BITRIX24

### Назначение:
Синхронизация CRM данных (сделки, контакты, компании)

### Credentials (потребуется):
```bash
BITRIX24_DOMAIN="your_domain.bitrix24.ru"
BITRIX24_CLIENT_ID="your_client_id"
BITRIX24_CLIENT_SECRET="your_client_secret"
BITRIX24_REDIRECT_URI="https://your-domain.com/api/integrations/bitrix24/callback"
```

**Как получить:**
1. https://www.bitrix24.ru/apps/
2. Создать приложение
3. Получить Client ID и Secret

### REST API Methods:

#### Получение сделок:
```python
# crm.deal.list
response = await bitrix24_client.call_method(
    "crm.deal.list",
    params={
        "select": ["ID", "TITLE", "OPPORTUNITY", "STAGE_ID", "ASSIGNED_BY_ID"],
        "filter": {
            ">=DATE_CREATE": "2024-01-01T00:00:00"
        }
    }
)
```

#### Создание контакта:
```python
# crm.contact.add
response = await bitrix24_client.call_method(
    "crm.contact.add",
    params={
        "fields": {
            "NAME": "Иван",
            "LAST_NAME": "Петров",
            "EMAIL": [{"VALUE": "ivan@example.com", "VALUE_TYPE": "WORK"}],
            "PHONE": [{"VALUE": "+7 999 123-45-67", "VALUE_TYPE": "WORK"}]
        }
    }
)
```

### Webhook Setup:

**Регистрация webhook:**
```python
await bitrix24_client.call_method(
    "event.bind",
    params={
        "event": "ONCRMDEALADD",
        "handler": "https://your-domain.com/api/integrations/bitrix24/webhook"
    }
)

# Аналогично для других событий:
# - ONCRMDEALUPDATE
# - ONCRMCONTACTADD
# - ONCRMCONTACTUPDATE
```

### Маппинг данных:

#### Deals → Projects:

| Bitrix24 Field | AgencyOps Field | Notes |
|---------------|-----------------|-------|
| ID | external_id | string |
| TITLE | name | string |
| OPPORTUNITY | budget | float |
| STAGE_ID | status | Маппинг статусов |
| ASSIGNED_BY_ID | manager_id | Маппинг пользователей |
| DATE_CREATE | created_at | ISO date |
| CONTACT_ID | client_id | Найти по external_id |
| COMMENTS | description | string |

**Stage Mapping:**
```python
BITRIX24_STAGE_MAP = {
    "NEW": "active",           # Новая сделка
    "PREPARATION": "active",   # Подготовка
    "EXECUTING": "active",     # В работе
    "FINAL_INVOICE": "active", # Финальный счет
    "WON": "completed",        # Сделка выиграна
    "LOSE": "cancelled"        # Сделка проиграна
}
```

#### Contacts → Clients:

| Bitrix24 Field | AgencyOps Field | Notes |
|---------------|-----------------|-------|
| ID | external_id | string |
| NAME + LAST_NAME | name | Concatenate |
| EMAIL[0].VALUE | email | First email |
| PHONE[0].VALUE | phone | First phone |
| COMPANY_ID | - | Link to company |
| ADDRESS | address | string |

---

## 🔔 WEBHOOK ENDPOINTS

### Общая структура:

```python
@router.post("/integrations/{provider}/webhook")
async def handle_webhook(
    provider: str,
    request: Request,
    x_company_id: str = Header(None, alias="X-Company-ID")
):
    # 1. Получить данные
    data = await request.json()
    
    # 2. Валидация подписи (если есть)
    if provider == "tinkoff":
        signature = data.get("Token")
        if not validate_tinkoff_signature(data, signature):
            raise HTTPException(status_code=400, detail="Invalid signature")
    
    # 3. Обработка по типу события
    handler = WEBHOOK_HANDLERS.get(provider)
    result = await handler(data, x_company_id)
    
    # 4. Логирование
    log_webhook_event(provider, data, result)
    
    return {"status": "ok"}
```

### Security:

1. **Tinkoff**: HMAC-SHA256 signature validation
2. **amoCRM**: Secret key validation
3. **Bitrix24**: IP whitelist + secret validation
4. **sCloud**: OAuth token validation

---

## 📊 DATA MAPPING STRATEGY

### Принципы:

1. **Двунаправленная синхронизация:**
   - Храним `external_id` и `external_source` для каждой сущности
   - Отслеживаем `last_synced_at` для избежания конфликтов

2. **Conflict Resolution:**
   ```python
   if local_updated_at > external_updated_at:
       # Push local changes
       sync_to_external(entity)
   else:
       # Pull external changes
       sync_from_external(entity)
   ```

3. **Field Mapping Tables:**
   ```python
   FIELD_MAPPINGS = {
       "amocrm": {
           "leads": {
               "id": "external_id",
               "name": "name",
               "price": "budget",
               # ...
           }
       },
       "bitrix24": {
           "deals": {
               # ...
           }
       }
   }
   ```

4. **Custom Field Handling:**
   ```python
   # Для custom fields создаем маппинг по company
   custom_field_mappings = {
       "comp_123": {
           "amocrm": {
               "111": "email",  # amoCRM field_id → AgencyOps field
               "112": "phone"
           }
       }
   }
   ```

### Database Schema для интеграций:

```python
# integrations collection
{
    "id": "int_123",
    "tenant_id": "comp_123",
    "provider": "amocrm",
    "status": "active",
    "credentials": {
        "access_token": "encrypted_token",
        "refresh_token": "encrypted_token",
        "token_expiry": "2024-11-19T10:00:00Z"
    },
    "settings": {
        "sync_interval": 3600,  # seconds
        "sync_direction": "bidirectional",  # pull, push, bidirectional
        "auto_create_clients": true,
        "auto_create_projects": true
    },
    "field_mappings": {
        "lead_to_project": {
            "name": "name",
            "price": "budget"
        }
    },
    "last_sync": "2024-11-19T09:00:00Z"
}

# integration_logs collection
{
    "id": "log_456",
    "integration_id": "int_123",
    "sync_type": "auto",
    "direction": "pull",
    "started_at": "2024-11-19T10:00:00Z",
    "completed_at": "2024-11-19T10:05:00Z",
    "status": "completed",
    "records_processed": 42,
    "records_created": 5,
    "records_updated": 37,
    "errors": []
}
```

---

## 🔄 SYNC STRATEGIES

### 1. Real-time (Webhook-based):
- Используется для: Tinkoff, amoCRM, Bitrix24
- Latency: < 1 second
- Best for: Critical updates (payments, new leads)

### 2. Scheduled (Polling):
- Используется для: sCloud, Bank APIs
- Frequency: Every 1-6 hours
- Best for: Bulk data (invoices, transactions)

### 3. Manual (On-demand):
- Trigger: User clicks "Sync now"
- Use case: First-time setup, troubleshooting

### Celery Tasks:

```python
# Scheduled sync tasks
@celery.task
def sync_all_integrations():
    integrations = get_active_integrations()
    
    for integration in integrations:
        if integration.provider == "scloud":
            sync_scloud_data.delay(integration.id)
        elif integration.provider == "amocrm":
            sync_amocrm_data.delay(integration.id)
        # ...

# Retry logic
@celery.task(bind=True, max_retries=3)
def sync_scloud_data(self, integration_id):
    try:
        # Sync logic
        pass
    except Exception as exc:
        # Exponential backoff
        self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

---

## 🛠️ TROUBLESHOOTING

### Common Issues:

**1. Token Expired:**
```python
if response.status_code == 401:
    # Refresh token
    new_tokens = await refresh_access_token(integration_id)
    # Retry request
```

**2. Rate Limiting:**
```python
if response.status_code == 429:
    retry_after = response.headers.get("Retry-After", 60)
    await asyncio.sleep(int(retry_after))
    # Retry
```

**3. Data Conflicts:**
```python
# Last-write-wins strategy
if conflict_detected:
    if prefer_external:
        overwrite_local(external_data)
    else:
        overwrite_external(local_data)
```

**4. Field Mapping Errors:**
```python
# Graceful degradation
try:
    mapped_value = field_mappings[external_field]
except KeyError:
    logger.warning(f"Unknown field: {external_field}")
    # Skip or use default value
```

---

## 📝 IMPLEMENTATION CHECKLIST

### Для каждой новой интеграции:

- [ ] Получить credentials (Client ID, Secret)
- [ ] Реализовать OAuth flow (если требуется)
- [ ] Создать service class (`XxxService`)
- [ ] Реализовать token management (refresh, storage)
- [ ] Создать webhook endpoint
- [ ] Реализовать webhook signature validation
- [ ] Создать маппинг полей (таблицы соответствия)
- [ ] Реализовать pull sync (External → AgencyOps)
- [ ] Реализовать push sync (AgencyOps → External)
- [ ] Добавить Celery tasks для scheduled sync
- [ ] Добавить error handling и retry logic
- [ ] Создать integration logs
- [ ] Добавить UI для настройки в frontend
- [ ] Написать документацию
- [ ] Протестировать с реальными данными

---

## 🎯 NEXT STEPS

### Приоритетные интеграции для реализации:

1. **amoCRM** (высокий приоритет)
   - Самая популярная CRM в России
   - Двунаправленная синхронизация клиентов и проектов

2. **Bitrix24** (высокий приоритет)
   - Альтернатива amoCRM
   - Более сложный API, но широкие возможности

3. **Tinkoff Business API** (средний приоритет)
   - Автоматическая загрузка выписок
   - Сверка платежей

4. **Сбербизнес API** (средний приоритет)
   - Аналогично Tinkoff Business

5. **Task Managers** (низкий приоритет)
   - Trello, Notion, ClickUp
   - Для синхронизации задач из Project Flow

---

**Документация обновлена:** 19.11.2024  
**Требуется помощь?** support@agencyops.com
