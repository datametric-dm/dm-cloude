# 🔐 Руководство по .env файлам

## 📁 Структура .env файлов

В проекте используются несколько .env файлов для разных окружений:

```
/app/
├── .env                    # Основной для Docker Compose
├── .env.production         # Шаблон для production
├── .env.example            # Пример конфигурации
├── backend/
│   ├── .env               # Для локального запуска (localhost)
│   └── .env.docker        # Для Docker (postgres host)
└── frontend/
    └── .env               # URL бэкенда
```

---

## 1️⃣ /app/.env (Основной для Docker)

**Назначение:** Используется Docker Compose для настройки всех сервисов

**Содержимое:**
```env
# Database Configuration
DB_PASSWORD=dm_secure_password_2025
DATABASE_URL=postgresql://dm_user:dm_secure_password_2025@postgres:5432/dm_cloud_mvp

# Application Settings
APP_ENV=production
SECRET_KEY=your_actual_secure_secret_key_here_change_this_2025
CORS_ORIGINS=*

# Telegram Bot (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# File Upload Settings
MAX_FILE_SIZE=10485760
UPLOAD_PATH=/app/uploads

# API Configuration
API_VERSION_STR=/api
```

**Когда использовать:**
- ✅ При развертывании через Docker Compose
- ✅ Production окружение

---

## 2️⃣ /app/backend/.env (Для локального запуска)

**Назначение:** Используется при локальном запуске backend через supervisor

**Содержимое:**
```env
# Database Configuration for Local Development
# For local PostgreSQL on localhost:5432
DATABASE_URL=postgresql://dm_user:dm_secure_password_2025@localhost:5432/dm_cloud_mvp

# Application Settings
APP_ENV=production
SECRET_KEY=your_actual_secure_secret_key_here_change_this_2025
CORS_ORIGINS=*

# Telegram Bot (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# File Upload Settings
MAX_FILE_SIZE=10485760
UPLOAD_PATH=/app/uploads

# API Configuration
API_VERSION_STR=/api
```

**Ключевое отличие:**
- 🔑 `DATABASE_URL` использует `localhost:5432` (не `postgres:5432`)

**Когда использовать:**
- ✅ При локальном запуске на Emergent
- ✅ При разработке на локальной машине
- ✅ При запуске через supervisor

---

## 3️⃣ /app/backend/.env.docker (Для Docker)

**Назначение:** Используется backend контейнером в Docker

**Содержимое:**
```env
# Database Configuration for Docker
DATABASE_URL=postgresql://dm_user:dm_secure_password_2025@postgres:5432/dm_cloud_mvp

# Application Settings
APP_ENV=production
SECRET_KEY=your_actual_secure_secret_key_here_change_this_2025
CORS_ORIGINS=*

# Telegram Bot (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# File Upload Settings
MAX_FILE_SIZE=10485760
UPLOAD_PATH=/app/uploads

# API Configuration
API_VERSION_STR=/api
```

**Ключевое отличие:**
- 🔑 `DATABASE_URL` использует `postgres:5432` (Docker service name)

**Когда использовать:**
- ✅ Автоматически в Docker контейнере
- ✅ Production Docker окружение

---

## 4️⃣ /app/frontend/.env

**Назначение:** Настройка URL бэкенда для React приложения

**Содержимое:**
```env
REACT_APP_BACKEND_URL=https://saasagency.preview.emergentagent.com
WDS_SOCKET_PORT=443
```

**Для локальной разработки:**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

**Для Docker:**
```env
REACT_APP_BACKEND_URL=http://localhost
```

---

## 🔧 Настройка для разных окружений

### Локальное развертывание (Emergent/Supervisor)

1. Используйте `/app/backend/.env` как есть
2. Убедитесь что PostgreSQL запущен на localhost:5432
3. Frontend автоматически использует свой .env

### Docker развертывание

1. Скопируйте `.env.production` в `.env`:
   ```bash
   cp .env.production .env
   ```

2. Измените пароли при необходимости:
   ```bash
   nano .env
   ```

3. Запустите Docker Compose:
   ```bash
   docker compose -f docker-compose.production.yml up -d
   ```

---

## 🔐 Безопасность

### ⚠️ Важно изменить перед production:

1. **DB_PASSWORD** - пароль базы данных
   ```env
   DB_PASSWORD=your_very_secure_password_here_123!@#
   ```

2. **SECRET_KEY** - ключ для JWT токенов (минимум 32 символа)
   ```env
   SECRET_KEY=generate_random_secure_key_min_32_chars_12345678
   ```

3. **CORS_ORIGINS** - ограничить домены
   ```env
   CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
   ```

### Генерация безопасных ключей:

```bash
# Генерация SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Генерация DB_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

---

## 📊 Сводная таблица

| Файл | Окружение | DATABASE_URL host | Использование |
|------|-----------|-------------------|---------------|
| `/app/.env` | Docker Compose | `postgres` | Docker развертывание |
| `/app/backend/.env` | Локальное | `localhost` | Emergent/Supervisor |
| `/app/backend/.env.docker` | Docker Container | `postgres` | Внутри Docker |
| `/app/frontend/.env` | Frontend | - | React URL бэкенда |

---

## ❓ FAQ

**Q: Какой .env использовать для локального запуска?**
A: `/app/backend/.env` с `localhost:5432`

**Q: Какой .env использовать для Docker?**
A: `/app/.env` с `postgres:5432`

**Q: Нужно ли изменять .env.docker вручную?**
A: Нет, он используется автоматически в Docker контейнере

**Q: Почему два разных DATABASE_URL?**
A: `localhost` - для локального PostgreSQL, `postgres` - для Docker service name

---

**DataMetrics Cloud MVP v2.0**
