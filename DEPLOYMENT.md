# 🚀 DataMetrics Cloud MVP - Руководство по развертыванию

## 📋 Два способа развертывания

### 1️⃣ Локальное развертывание (Emergent / Supervisor)

Для локального развертывания на сервере Emergent с использованием supervisor.

#### Требования:
- PostgreSQL 15+
- Python 3.11+
- Node.js 20+
- Yarn

#### Шаги:

```bash
# 1. Установить PostgreSQL
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib

# 2. Запустить PostgreSQL
pg_ctlcluster 15 main start

# 3. Создать базу данных и пользователя
sudo -u postgres psql -c "CREATE USER dm_user WITH PASSWORD 'dm_secure_password_2025';"
sudo -u postgres psql -c "CREATE DATABASE dm_cloud_mvp OWNER dm_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dm_cloud_mvp TO dm_user;"

# 4. Настроить backend
cd /app/backend

# Backend .env уже настроен для localhost
# Убедитесь что DATABASE_URL использует localhost:5432

# 5. Установить Python зависимости
pip install -r requirements.txt

# 6. Применить миграции Alembic
alembic upgrade head

# 7. Создать тестовые данные (опционально)
python3 create_test_data.py

# 8. Настроить frontend
cd /app/frontend
yarn install

# 9. Перезапустить сервисы через supervisor
sudo supervisorctl restart all

# 10. Проверить здоровье системы
curl http://localhost:8001/api/health
```

**Учетные данные для входа:**
- Email: `admin@test.com`
- Пароль: `admin123`

---

### 2️⃣ Docker развертывание (Production)

Для развертывания с использованием Docker Compose.

#### Требования:
- Docker 20.10+
- Docker Compose 2.0+

#### Шаги:

```bash
# 1. Скопировать .env.production в .env
cp .env.production .env

# 2. (Опционально) Изменить пароли в .env
nano .env
# Измените DB_PASSWORD и SECRET_KEY на свои значения

# 3. Запустить контейнеры
docker compose -f docker-compose.production.yml up -d --build

# 4. Проверить статус контейнеров
docker compose -f docker-compose.production.yml ps

# 5. Применить миграции (первый запуск)
docker compose -f docker-compose.production.yml exec backend alembic upgrade head

# 6. Создать тестового пользователя (первый запуск)
docker compose -f docker-compose.production.yml exec backend python create_test_data.py

# 7. Проверить логи
docker compose -f docker-compose.production.yml logs -f backend
docker compose -f docker-compose.production.yml logs -f frontend

# 8. Доступ к приложению
# Frontend: http://localhost
# API: http://localhost/api
# API Docs: http://localhost/docs
# Adminer (DB UI): http://localhost:8080
```

**Учетные данные для входа:**
- Email: `admin@test.com`
- Пароль: `admin123`

---

## 🔧 Настройка переменных окружения

### Корневой .env (для Docker)
Файл `.env.production` содержит настройки для Docker окружения:
- `DB_PASSWORD` - пароль для PostgreSQL
- `DATABASE_URL` - подключение к базе (хост: `postgres`)
- `SECRET_KEY` - секретный ключ для JWT

### Backend .env
Для локального запуска:
- `DATABASE_URL` использует `localhost:5432`

Для Docker:
- Используется `.env.docker` с хостом `postgres:5432`

---

## 📊 Структура проекта

```
/app
├── .env.production          # Настройки для Docker
├── .env.example             # Пример настроек
├── docker-compose.production.yml
├── backend/
│   ├── .env                 # Для локального запуска (localhost)
│   ├── .env.docker          # Для Docker (postgres)
│   ├── alembic/             # Миграции базы данных
│   ├── models/              # SQLAlchemy модели
│   ├── routers/             # FastAPI роутеры
│   ├── schemas/             # Pydantic схемы
│   ├── services/            # Бизнес-логика
│   ├── server.py            # Точка входа FastAPI
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/          # React страницы
│   │   ├── components/     # React компоненты
│   │   └── lib/            # Утилиты и API
│   ├── package.json
│   └── tailwind.config.js
└── scripts/                 # Утилитные скрипты
```

---

## 🔍 Troubleshooting

### PostgreSQL не запускается
```bash
# Проверить статус
pg_isready

# Запустить вручную
pg_ctlcluster 15 main start
```

### Ошибка подключения к базе
```bash
# Проверить что PostgreSQL запущен
pg_isready

# Проверить DATABASE_URL в .env
cat /app/backend/.env
```

### Docker контейнеры не запускаются
```bash
# Проверить логи
docker compose -f docker-compose.production.yml logs

# Пересоздать контейнеры
docker compose -f docker-compose.production.yml down -v
docker compose -f docker-compose.production.yml up -d --build
```

### Нет данных в базе
```bash
# Локальное развертывание
cd /app/backend && python3 create_test_data.py

# Docker
docker compose exec backend python create_test_data.py
```

---

## 📞 Поддержка

- 📧 Email: support@datametrics.cloud
- 📖 Документация: http://localhost:8001/docs
- 🐛 Issues: GitHub Issues

---

**DataMetrics Cloud MVP v2.0**
*Создано для эффективного управления проектами*
