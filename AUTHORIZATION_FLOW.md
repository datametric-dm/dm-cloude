# 🔐 АВТОРИЗАЦИЯ И MULTI-TENANCY
## Полная схема работы системы разделения данных

**Version:** 1.0.0  
**Updated:** 19.11.2024

---

## 📋 СОДЕРЖАНИЕ

1. [Общая концепция](#общая-концепция)
2. [Регистрация нового пользователя](#регистрация-нового-пользователя)
3. [Создание/выбор компании](#создание-выбор-компании)
4. [Изоляция данных](#изоляция-данных)
5. [Права доступа](#права-доступа)
6. [Приглашение в компанию](#приглашение-в-компанию)
7. [FAQ](#faq)

---

## 🎯 ОБЩАЯ КОНЦЕПЦИЯ

### Multi-Tenancy Architecture

AgencyOps использует **полную изоляцию данных на уровне компании (tenant)**.

```
┌─────────────────────────────────────────────────┐
│              AgencyOps Platform                  │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  Company A   │  │  Company B   │            │
│  │  (tenant_id) │  │  (tenant_id) │            │
│  │              │  │              │            │
│  │ • Users      │  │ • Users      │            │
│  │ • Clients    │  │ • Clients    │            │
│  │ • Projects   │  │ • Projects   │            │
│  │ • Invoices   │  │ • Invoices   │            │
│  │              │  │              │            │
│  │ ❌ ИЗОЛЯЦИЯ  │  │ ❌ ИЗОЛЯЦИЯ  │            │
│  └──────────────┘  └──────────────┘            │
│         │                  │                     │
│         └──────────────────┘                     │
│         НЕ ВИДЯТ ДАННЫЕ ДРУГ ДРУГА              │
└─────────────────────────────────────────────────┘
```

### Ключевые принципы:

1. **Один пользователь = несколько компаний**
   - Пользователь может быть членом разных компаний
   - В каждой компании - своя роль

2. **Полная изоляция данных**
   - Данные одной компании НИКОГДА не видны другой
   - Все запросы фильтруются по `tenant_id`

3. **Контекст компании**
   - Пользователь выбирает активную компанию при входе
   - Все операции выполняются в контексте выбранной компании

---

## 👤 РЕГИСТРАЦИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ

### Шаг 1: Регистрация аккаунта

**UI Flow:**
```
Страница /register
    ↓
Форма регистрации:
- Email
- Пароль
- Имя
    ↓
POST /api/auth/register
    ↓
Создание пользователя в БД
```

**API Request:**
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "ivan@example.com",
  "password": "SecurePassword123",
  "name": "Иван Петров"
}
```

**Response:**
```json
{
  "id": "user_abc123",
  "email": "ivan@example.com",
  "name": "Иван Петров",
  "created_at": "2024-11-19T10:00:00Z"
}
```

**Что происходит в БД:**
```javascript
// users collection
{
  "id": "user_abc123",
  "email": "ivan@example.com",
  "password_hash": "hashed_password",
  "name": "Иван Петров",
  "created_at": "2024-11-19T10:00:00Z"
}
```

### Шаг 2: Первый вход

**UI Flow:**
```
Страница /login
    ↓
Форма входа:
- Email: ivan@example.com
- Password: SecurePassword123
    ↓
POST /api/auth/login
    ↓
Получение JWT токена
    ↓
Сохранение в localStorage
    ↓
Редирект на /companies (выбор компании)
```

**API Request:**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "ivan@example.com",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user_abc123",
    "email": "ivan@example.com",
    "name": "Иван Петров"
  }
}
```

**Frontend сохраняет:**
```javascript
localStorage.setItem('token', access_token);
localStorage.setItem('user', JSON.stringify(user));
```

---

## 🏢 СОЗДАНИЕ/ВЫБОР КОМПАНИИ

### Сценарий 1: Создание новой компании

**UI Flow:**
```
Страница /companies (пустой список)
    ↓
Кнопка "Создать компанию"
    ↓
Форма создания:
- Название: "Моё Агентство"
- ИНН: 1234567890 (опционально)
- Адрес: "г. Москва" (опционально)
    ↓
POST /api/companies
    ↓
Компания создана!
    ↓
Автоматический выбор созданной компании
    ↓
Редирект на /dashboard
```

**API Request:**
```http
POST /api/companies
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "Моё Агентство",
  "legal_name": "ООО Моё Агентство",
  "inn": "1234567890",
  "address": "г. Москва, ул. Ленина, д. 1"
}
```

**Response:**
```json
{
  "id": "comp_xyz789",
  "name": "Моё Агентство",
  "subscription_status": "trial",
  "subscription_plan": "free",
  "max_users": 5,
  "max_projects": 10,
  "created_at": "2024-11-19T10:00:00Z"
}
```

**Что происходит в БД:**

```javascript
// 1. Создается компания
// companies collection
{
  "id": "comp_xyz789",
  "name": "Моё Агентство",
  "legal_name": "ООО Моё Агентство",
  "inn": "1234567890",
  "subscription_status": "trial",
  "subscription_plan": "free",
  "max_users": 5,
  "max_projects": 10,
  "created_at": "2024-11-19T10:00:00Z"
}

// 2. Создается связь пользователь-компания
// user_company_roles collection
{
  "id": "ucr_001",
  "user_id": "user_abc123",
  "company_id": "comp_xyz789",
  "role": "owner",           // ВЛАДЕЛЕЦ!
  "permissions": ["all"],
  "created_at": "2024-11-19T10:00:00Z"
}
```

**Frontend сохраняет выбранную компанию:**
```javascript
// CompanyContext
setCurrentCompany({
  id: "comp_xyz789",
  name: "Моё Агентство",
  user_role: "owner",
  permissions: ["all"]
});

localStorage.setItem('currentCompanyId', 'comp_xyz789');
```

### Сценарий 2: Выбор существующей компании

**Если пользователь уже в нескольких компаниях:**

```
Страница /companies (список компаний)
    ↓
Список:
1. Моё Агентство (owner)
2. Клиентское Агентство (manager) ← получил приглашение
    ↓
Выбор компании → клик
    ↓
Установка контекста компании
    ↓
Редирект на /dashboard
```

**API Request:**
```http
GET /api/companies/my
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "companies": [
    {
      "id": "comp_xyz789",
      "name": "Моё Агентство",
      "role": "owner",
      "permissions": ["all"]
    },
    {
      "id": "comp_abc456",
      "name": "Клиентское Агентство",
      "role": "manager",
      "permissions": ["projects:read", "projects:write", "clients:read"]
    }
  ]
}
```

---

## 🔒 ИЗОЛЯЦИЯ ДАННЫХ

### Как работает фильтрация

**При каждом запросе к API:**

```python
# backend/middleware/tenant.py

@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    # 1. Извлекаем X-Company-ID из headers
    company_id = request.headers.get("X-Company-ID")
    
    # 2. Проверяем, имеет ли пользователь доступ к этой компании
    user_id = get_current_user_id(request)
    has_access = check_user_company_access(user_id, company_id)
    
    if not has_access:
        raise HTTPException(403, "Access denied")
    
    # 3. Устанавливаем tenant_id в контекст
    tenant_context.set(company_id)
    
    response = await call_next(request)
    return response
```

**Все запросы к БД автоматически фильтруются:**

```python
# Пример: Получение клиентов
@router.get("/clients")
async def get_clients(
    x_company_id: str = Header(..., alias="X-Company-ID")
):
    # Фильтр по tenant_id добавляется автоматически
    clients = await db.clients.find({
        "tenant_id": x_company_id  # ← ИЗОЛЯЦИЯ
    }).to_list()
    
    return {"clients": clients}
```

### Пример изоляции:

**Компания A (comp_xyz789):**
```javascript
// clients collection
{
  "id": "client_001",
  "tenant_id": "comp_xyz789",  // ← Компания A
  "name": "Клиент компании A",
  "email": "client-a@example.com"
}
```

**Компания B (comp_abc456):**
```javascript
// clients collection
{
  "id": "client_002",
  "tenant_id": "comp_abc456",  // ← Компания B
  "name": "Клиент компании B",
  "email": "client-b@example.com"
}
```

**Запрос от Компании A:**
```http
GET /api/clients
Authorization: Bearer <jwt_token>
X-Company-ID: comp_xyz789
```

**Response (только данные Компании A):**
```json
{
  "clients": [
    {
      "id": "client_001",
      "name": "Клиент компании A",
      "email": "client-a@example.com"
    }
    // ❌ client_002 НЕ ВИДЕН!
  ]
}
```

**❌ Попытка получить чужие данные:**
```http
GET /api/clients/client_002
Authorization: Bearer <jwt_token>
X-Company-ID: comp_xyz789
```

**Response:**
```json
{
  "detail": "Client not found",
  "status_code": 404
}
```

---

## 👥 ПРАВА ДОСТУПА

### Роли в компании:

| Роль | Описание | Права |
|------|----------|-------|
| **owner** | Владелец | Все права, управление биллингом, удаление компании |
| **admin** | Администратор | Все права кроме биллинга и удаления |
| **manager** | Менеджер | CRUD проектов, клиентов, счетов; чтение отчетов |
| **observer** | Наблюдатель | Только чтение (read-only) |

### Матрица прав:

| Ресурс | Owner | Admin | Manager | Observer |
|--------|-------|-------|---------|----------|
| Компания (настройки) | ✅ | ✅ | ❌ | ❌ |
| Биллинг | ✅ | ❌ | ❌ | ❌ |
| Команда (добавление/удаление) | ✅ | ✅ | ❌ | ❌ |
| Клиенты (CRUD) | ✅ | ✅ | ✅ | ❌ (read-only) |
| Проекты (CRUD) | ✅ | ✅ | ✅ | ❌ (read-only) |
| Счета (CRUD) | ✅ | ✅ | ✅ | ❌ (read-only) |
| Платежи (CRUD) | ✅ | ✅ | ✅ | ❌ (read-only) |
| Отчеты (просмотр) | ✅ | ✅ | ✅ | ✅ |
| Интеграции | ✅ | ✅ | ❌ | ❌ |

### Проверка прав в API:

```python
from fastapi import Depends, HTTPException

def require_permission(permission: str):
    async def check_permission(
        current_user = Depends(get_current_user),
        x_company_id: str = Header(..., alias="X-Company-ID")
    ):
        # Получить роль пользователя в компании
        user_role = await get_user_role_in_company(
            current_user.id, 
            x_company_id
        )
        
        # Проверить права
        if not has_permission(user_role.role, permission):
            raise HTTPException(403, "Permission denied")
        
        return user_role
    
    return check_permission

# Использование
@router.post("/clients")
async def create_client(
    client_data: ClientCreate,
    user_role = Depends(require_permission("clients:write"))
):
    # Только owner, admin, manager могут создавать клиентов
    pass
```

---

## 📨 ПРИГЛАШЕНИЕ В КОМПАНИЮ

### Как пригласить нового пользователя:

**Шаг 1: Owner/Admin создает приглашение**

```
UI: Страница /team
    ↓
Кнопка "Пригласить участника"
    ↓
Форма:
- Email: developer@example.com
- Роль: manager
    ↓
POST /api/companies/{company_id}/team/invite
```

**API Request:**
```http
POST /api/companies/comp_xyz789/team/invite
Authorization: Bearer <jwt_token>
X-Company-ID: comp_xyz789
Content-Type: application/json

{
  "email": "developer@example.com",
  "role": "manager"
}
```

**Что происходит:**
```javascript
// 1. Создается приглашение
// invitations collection
{
  "id": "inv_123",
  "company_id": "comp_xyz789",
  "email": "developer@example.com",
  "role": "manager",
  "token": "secure_random_token",
  "status": "pending",
  "expires_at": "2024-11-26T10:00:00Z",
  "created_by": "user_abc123",
  "created_at": "2024-11-19T10:00:00Z"
}

// 2. Отправляется email
To: developer@example.com
Subject: Приглашение в Моё Агентство
Link: https://your-domain.com/invite/secure_random_token
```

**Шаг 2: Приглашенный пользователь регистрируется**

```
Email → клик по ссылке
    ↓
Страница /invite/secure_random_token
    ↓
Если пользователя нет → форма регистрации
Если есть → автоматический accept
    ↓
POST /api/invitations/accept
    ↓
Создается связь user_company_role
    ↓
Пользователь добавлен в компанию!
```

**API Request:**
```http
POST /api/invitations/accept
Content-Type: application/json

{
  "token": "secure_random_token",
  "user_id": "user_new789"  // если уже зарегистрирован
}
```

**Response:**
```json
{
  "company": {
    "id": "comp_xyz789",
    "name": "Моё Агентство",
    "role": "manager"
  }
}
```

**Обновление БД:**
```javascript
// user_company_roles collection
{
  "id": "ucr_002",
  "user_id": "user_new789",
  "company_id": "comp_xyz789",
  "role": "manager",
  "permissions": ["projects:read", "projects:write", "clients:read"],
  "joined_at": "2024-11-19T11:00:00Z"
}

// invitations collection - обновление статуса
{
  "id": "inv_123",
  "status": "accepted",  // ← ИЗМЕНЕНО
  "accepted_at": "2024-11-19T11:00:00Z"
}
```

**Теперь новый пользователь видит 2 компании:**

```http
GET /api/companies/my
Authorization: Bearer <jwt_token_new_user>
```

**Response:**
```json
{
  "companies": [
    {
      "id": "comp_xyz789",
      "name": "Моё Агентство",
      "role": "manager",
      "permissions": ["projects:read", "projects:write"]
    }
  ]
}
```

---

## ❓ FAQ

### Q: Может ли новый пользователь видеть проекты других компаний?

**A: НЕТ. Абсолютно невозможно.**

- Все данные фильтруются по `tenant_id`
- Middleware проверяет доступ к компании
- Даже если попытаться подделать `X-Company-ID`, система вернет 403 Forbidden

### Q: Что видит новый пользователь при первом входе?

**A: Пустой список компаний.**

1. Регистрация → вход
2. Страница `/companies` (пустая)
3. Два варианта:
   - Создать свою компанию
   - Получить приглашение от другой компании

### Q: Как переключаться между компаниями?

**A: Через селектор в сайдбаре:**

```
Sidebar → Dropdown "Текущая компания"
    ↓
Кнопка "Сменить компанию"
    ↓
Страница /companies (список всех компаний пользователя)
    ↓
Выбор компании
    ↓
Обновление CompanyContext
    ↓
Все запросы теперь используют новый X-Company-ID
```

### Q: Что происходит при создании клиента/проекта?

**A: Автоматически добавляется tenant_id:**

```python
@router.post("/clients")
async def create_client(
    client_data: ClientCreate,
    x_company_id: str = Header(..., alias="X-Company-ID")
):
    # tenant_id добавляется автоматически
    new_client = {
        "id": generate_id(),
        "tenant_id": x_company_id,  # ← ИЗ HEADER
        **client_data.dict()
    }
    
    await db.clients.insert_one(new_client)
    return new_client
```

### Q: Может ли пользователь быть в 10 компаниях?

**A: ДА. Без ограничений.**

- Один пользователь = N компаний
- В каждой компании - своя роль
- Переключение через селектор

### Q: Как работает бесплатный план?

**A: При создании компании:**

```javascript
// Автоматически
{
  "subscription_status": "trial",
  "subscription_plan": "free",
  "max_users": 5,
  "max_projects": 10,
  "trial_ends_at": "2024-12-19T00:00:00Z"  // +30 дней
}
```

После trial:
- Можно перейти на платный план через Tinkoff
- Или остаться на Free с ограничениями

### Q: Что если пользователь удален из компании?

**A: Связь разрывается:**

```python
# Удаление user_company_role
await db.user_company_roles.delete_one({
    "user_id": "user_abc123",
    "company_id": "comp_xyz789"
})
```

Результат:
- Пользователь больше не видит эту компанию в списке
- Все запросы с X-Company-ID этой компании → 403 Forbidden

### Q: Можно ли восстановить удаленную компанию?

**A: НЕТ. Только owner может удалить компанию.**

При удалении:
- Soft delete (помечается как deleted)
- Данные остаются в БД 30 дней
- После 30 дней - полное удаление (GDPR compliance)

---

## 🔐 SECURITY CHECKLIST

- ✅ JWT токены с expiration
- ✅ Проверка доступа к компании на каждый запрос
- ✅ Middleware фильтрация по tenant_id
- ✅ Rate limiting по IP и по company_id
- ✅ Приглашения с токенами и expiration
- ✅ RBAC (Role-Based Access Control)
- ✅ Audit logs для критичных операций
- ✅ Защита от CSRF
- ✅ Защита от SQL injection (NoSQL)

---

## 📊 ДИАГРАММА FLOW

```
Регистрация → Вход → Выбор/Создание компании → Dashboard
                               ↓
                    ┌──────────┴──────────┐
                    │                     │
            Своя компания         Приглашение
            (owner, admin)        (manager, observer)
                    │                     │
                    └──────────┬──────────┘
                               ↓
                    Работа в контексте компании
                    (все данные изолированы)
```

---

**Документация обновлена:** 19.11.2024  
**Вопросы?** support@agencyops.com
