# ⚡ Быстрый старт - DataMetrics Cloud MVP

## 📥 После скачивания с GitHub

После клонирования репозитория или распаковки архива, .env файлы отсутствуют (по соображениям безопасности).

### Автоматическая настройка (рекомендуется)

Запустите скрипт для автоматического создания всех .env файлов:

```bash
chmod +x setup-env.sh
./setup-env.sh
```

Скрипт спросит:
- **1** - для Docker развертывания (создаст .env с postgres:5432)
- **2** - для локального развертывания (создаст .env с localhost:5432)

---

### Ручная настройка

Если предпочитаете настроить вручную:

#### Для Docker:

```bash
# 1. Корневой .env для docker-compose
cp .env.production .env

# 2. Frontend .env (опционально, если нужно изменить URL)
cp frontend/.env.example frontend/.env
```

#### Для локального запуска:

```bash
# 1. Backend .env
cp backend/.env.example backend/.env

# 2. Отредактируйте backend/.env - убедитесь что используется localhost:
DATABASE_URL=postgresql://dm_user:dm_secure_password_2025@localhost:5432/dm_cloud_mvp

# 3. Frontend .env
cp frontend/.env.example frontend/.env
```

---

## 🚀 Запуск

### Docker (Production)

```bash
# 1. Настроить .env
./setup-env.sh  # выберите опцию 1

# 2. Запустить контейнеры
docker compose -f docker-compose.production.yml up -d --build

# 3. Применить миграции
docker compose exec backend alembic upgrade head

# 4. Создать тестовые данные
docker compose exec backend python create_test_data.py

# 5. Открыть в браузере
http://localhost
```

### Локальное развертывание (Emergent/Development)

```bash
# 1. Настроить .env
./setup-env.sh  # выберите опцию 2

# 2. Запустить PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib
pg_ctlcluster 15 main start

# 3. Создать базу данных
sudo -u postgres psql -c "CREATE USER dm_user WITH PASSWORD 'dm_secure_password_2025';"
sudo -u postgres psql -c "CREATE DATABASE dm_cloud_mvp OWNER dm_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dm_cloud_mvp TO dm_user;"

# 4. Установить зависимости
cd backend
pip install -r requirements.txt

cd ../frontend
yarn install

# 5. Применить миграции
cd ../backend
alembic upgrade head

# 6. Создать тестовые данные
python3 create_test_data.py

# 7. Запустить сервисы
cd ..
sudo supervisorctl restart all

# Или запустить вручную:
# Terminal 1: cd backend && uvicorn server:app --host 0.0.0.0 --port 8001
# Terminal 2: cd frontend && yarn start
```

---

## 🔑 Учетные данные

После создания тестовых данных:

- **Email:** `admin@test.com`
- **Пароль:** `admin123`

---

## 📁 Структура .env файлов

```
/app/
├── .env.example             # Пример (в Git ✅)
├── .env.production          # Шаблон production (в Git ✅)
├── .env                     # Создается скриптом (НЕ в Git ❌)
├── backend/
│   ├── .env.example        # Пример (в Git ✅)
│   ├── .env.docker         # Для Docker (в Git ✅)
│   └── .env                # Создается скриптом (НЕ в Git ❌)
└── frontend/
    ├── .env.example        # Пример (в Git ✅)
    └── .env                # Создается скриптом (НЕ в Git ❌)
```

**В Git включены только шаблоны (.example, .production, .docker)**
**Реальные .env файлы создаются локально через setup-env.sh**

---

## ⚠️ Важные настройки безопасности

Перед production развертыванием **обязательно** измените:

### 1. Пароль базы данных

В `.env`:
```env
DB_PASSWORD=your_very_secure_random_password_123!@#$
```

### 2. Secret key для JWT

В `.env`:
```env
SECRET_KEY=generate_random_32_char_key_use_command_below
```

Генерация безопасных ключей:
```bash
# SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# DB_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

### 3. CORS Origins

В `.env`:
```env
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

---

## 📚 Дополнительная документация

- 📖 [README.md](./README.md) - Общая информация
- 🚀 [DEPLOYMENT.md](./DEPLOYMENT.md) - Подробное руководство по развертыванию
- 🔐 [ENV_FILES_GUIDE.md](./ENV_FILES_GUIDE.md) - Детальное описание всех .env файлов

---

## 🆘 Проблемы?

### Нет .env файлов после клонирования

Это нормально! Запустите:
```bash
./setup-env.sh
```

### Ошибка подключения к базе

Проверьте:
1. PostgreSQL запущен: `pg_isready`
2. Правильный хост в DATABASE_URL:
   - `localhost:5432` - для локального
   - `postgres:5432` - для Docker

### Ошибка "REACT_APP_BACKEND_URL не определен"

Создайте `frontend/.env`:
```bash
cp frontend/.env.example frontend/.env
```

---

**DataMetrics Cloud MVP v2.0** 
*Ready to deploy! 🚀*
