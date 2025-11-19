# 🏢 Multi-Tenancy Implementation Guide

## Обзор

Система теперь поддерживает **multi-tenancy** архитектуру, которая позволяет:
- Разделять данные между компаниями (tenants)
- Управлять пользователями и их ролями в компаниях
- Контролировать доступ к данным на уровне компании
- Поддерживать подписочную модель

## 🎯 Реализованные компоненты

### Backend

#### 1. Модели

**Company (models/company.py)**
- Представляет компанию (tenant)
- Поля: name, legal_name, inn, kpp, subscription_plan, subscription_status
- Статусы подписки: trial, active, suspended, cancelled, frozen
- Тарифные планы: free, starter, professional, enterprise

**UserCompanyRole (models/user_company.py)**
- Связывает пользователя с компанией
- Роли: owner, admin, manager, observer
- Гранулярные права доступа для каждой роли

**Роли и права доступа:**

| Роль | Описание | Права |
|------|----------|-------|
| **Owner** | Владелец | Полный доступ, включая биллинг и удаление компании |
| **Admin** | Администратор | Полный доступ, кроме биллинга и удаления компании |
| **Manager** | Менеджер | Управление проектами, клиентами, командой; просмотр финансов |
| **Observer** | Наблюдатель | Только просмотр данных |

#### 2. API Endpoints

**Companies Management** (`/api/companies`)
```
POST   /api/companies              - Создать компанию
GET    /api/companies/my           - Получить мои компании
GET    /api/companies/{id}         - Получить компанию
PUT    /api/companies/{id}         - Обновить компанию
DELETE /api/companies/{id}         - Удалить компанию (soft delete)
GET    /api/companies/{id}/stats   - Получить статистику компании
```

**Team Management** (`/api/companies/{company_id}/team`)
```
POST   /team/invite                - Пригласить пользователя
GET    /team                       - Получить список команды
PUT    /team/{user_id}/role        - Обновить роль
PUT    /team/{user_id}/permissions - Обновить права доступа
DELETE /team/{user_id}             - Удалить из команды
```

#### 3. Headers для Multi-tenancy

Все запросы к API должны включать:
```
X-Company-ID: {company_id}  - ID текущей компании
X-User-ID: {user_id}        - ID текущего пользователя
```

API автоматически добавляет эти заголовки через interceptor в `lib/api.js`.

#### 4. Фильтрация данных

Все существующие эндпоинты (клиенты, проекты, счета, платежи) обновлены для поддержки `tenant_id`:
- При создании записи автоматически добавляется `tenant_id`
- При выборке данных фильтрация по `tenant_id`
- Пользователь видит только данные своей компании

### Frontend

#### 1. Context

**CompanyContext** (`contexts/CompanyContext.jsx`)
- Управляет текущей выбранной компанией
- Хранит список доступных компаний
- Сохраняет выбор в localStorage

```jsx
import { useCompany } from '../contexts/CompanyContext';

const { currentCompany, selectCompany, clearCompany } = useCompany();
```

#### 2. Новые страницы

**CompanySelect** (`pages/CompanySelect.jsx`)
- Страница выбора/создания компании
- Отображает все компании, к которым у пользователя есть доступ
- Возможность создать новую компанию

**TeamManagement** (`pages/TeamManagement.jsx`)
- Управление командой текущей компании
- Приглашение новых пользователей
- Управление ролями и правами доступа
- Удаление пользователей

#### 3. Обновленные компоненты

**Layout**
- Добавлен переключатель компаний в сайдбаре
- Отображение текущей компании и роли
- Новый пункт меню "Команда"

**PrivateRoute**
- Проверка аутентификации
- Редирект на `/companies` если компания не выбрана
- Разрешает доступ к `/companies` без выбранной компании

**API Client** (`lib/api.js`)
- Автоматическое добавление `X-Company-ID` и `X-User-ID` в заголовки
- Новые API методы для компаний и команды

## 🚀 Workflow пользователя

1. **Регистрация/Вход**
   ```
   Пользователь входит → Перенаправление на /companies
   ```

2. **Выбор/Создание компании**
   ```
   /companies → Выбор существующей или создание новой компании
   → Перенаправление на /dashboard
   ```

3. **Работа в системе**
   ```
   Все действия выполняются в контексте выбранной компании
   Данные автоматически фильтруются по tenant_id
   ```

4. **Переключение компаний**
   ```
   Клик на переключатель в сайдбаре → /companies
   → Выбор другой компании → Обновление контекста
   ```

5. **Управление командой**
   ```
   /team → Просмотр членов команды
   → Приглашение новых пользователей (email)
   → Управление ролями и правами
   ```

## 📊 База данных

### Коллекции

**companies** - Компании
```json
{
  "id": "uuid",
  "name": "Company Name",
  "subscription_plan": "professional",
  "subscription_status": "active",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00"
}
```

**user_company_roles** - Связи пользователь-компания
```json
{
  "id": "uuid",
  "user_id": "user_uuid",
  "company_id": "company_uuid",
  "role": "manager",
  "can_create_projects": true,
  "can_edit_projects": true,
  "is_active": true
}
```

**Все остальные коллекции** (clients, projects, invoices, payments, etc.)
```json
{
  "id": "uuid",
  "tenant_id": "company_uuid",  // <- Добавлено
  "...": "..."
}
```

## 🔧 Миграция данных

Запущена миграция для добавления `tenant_id` к существующим данным:

```bash
cd /app/backend
python migrations/add_tenant_id.py
```

Миграция создает "Default Company" и привязывает к ней все существующие данные.

## 🔐 Безопасность

1. **Изоляция данных**
   - Все запросы фильтруются по `tenant_id`
   - Пользователь не может получить доступ к данным другой компании

2. **Проверка прав доступа**
   - Каждый endpoint проверяет права пользователя в компании
   - Действия ограничены в соответствии с ролью

3. **Audit Trail**
   - Все создания/изменения записывают `created_by`, `invited_by`
   - Timestamp для всех операций

## 🧪 Тестирование

### Создание компании
```bash
curl -X POST http://localhost:8001/api/companies \
  -H "X-User-ID: user_id" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Company", "email": "test@company.com"}'
```

### Получение моих компаний
```bash
curl -X GET http://localhost:8001/api/companies/my \
  -H "X-User-ID: user_id"
```

### Приглашение пользователя
```bash
curl -X POST http://localhost:8001/api/companies/{company_id}/team/invite \
  -H "X-User-ID: user_id" \
  -H "X-Company-ID: company_id" \
  -H "Content-Type: application/json" \
  -d '{"email": "newuser@example.com", "role": "manager"}'
```

## 📝 Следующие шаги

1. ✅ Multi-tenancy архитектура реализована
2. ✅ Система ролей и прав доступа
3. ✅ Управление компаниями
4. ✅ Управление командой
5. ⏳ Биллинг и подписки (следующий этап)
6. ⏳ Интеграции (CRM, банки, бухгалтерия)
7. ⏳ Остальные модули (Project Flow, Financial Flow, Team Load, etc.)

## 🎉 Готово к использованию!

Система теперь полностью поддерживает multi-tenancy и готова к добавлению остальных модулей SaaS-платформы.
