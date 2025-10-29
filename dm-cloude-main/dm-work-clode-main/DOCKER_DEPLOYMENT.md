# 🚀 Docker развертывание DataMetrics Cloud MVP

## 📋 Быстрый старт для production сервера

### Предварительные требования:
- Docker 20.10+
- Docker Compose 2.0+
- Открытые порты: 80, 8001, 5432

---

## 🔧 Шаг 1: Подготовка проекта

```bash
# Клонируйте репозиторий или распакуйте архив
cd /path/to/project

# Создайте .env файл из шаблона
cp .env.production .env
```

---

## 🔐 Шаг 2: Настройка .env файла

**ВАЖНО:** Перед запуском обязательно измените пароли!

```bash
nano .env
```

Измените следующие значения:

```env
# Database Configuration
DB_PASSWORD=ваш_супер_секретный_пароль_123

# Application Settings
SECRET_KEY=сгенерируйте_32_символьный_ключ
```

**Генерация безопасных ключей:**
```bash
# SECRET_KEY (минимум 32 символа)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# DB_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

---

## 🚀 Шаг 3: Запуск контейнеров

```bash
# Запуск всех сервисов
docker compose -f docker-compose.production.yml up -d --build

# Проверка статуса
docker compose -f docker-compose.production.yml ps
```

Вы должны увидеть:
```
NAME          IMAGE               STATUS          PORTS
dm_postgres   postgres:15-alpine  Up (healthy)    0.0.0.0:5432->5432/tcp
dm_backend    ...                 Up (healthy)    0.0.0.0:8001->8001/tcp
dm_frontend   ...                 Up              0.0.0.0:3000->3000/tcp
dm_nginx      nginx:alpine        Up              0.0.0.0:80->80/tcp
dm_adminer    adminer:latest      Up              0.0.0.0:8080->8080/tcp
```

---

## 🗄️ Шаг 4: Инициализация базы данных

```bash
# Применить миграции Alembic
docker compose -f docker-compose.production.yml exec backend alembic upgrade head

# Создать тестовые данные (опционально)
docker compose -f docker-compose.production.yml exec backend python create_test_data.py
```

---

## ✅ Шаг 5: Проверка развертывания

### Проверка API:
```bash
# Health check
curl http://217.198.9.199/api/health

# Должно вернуть:
# {"status": "OK", "database": "OK", ...}
```

### Доступ к интерфейсам:

| Сервис | URL | Описание |
|--------|-----|----------|
| **Frontend** | http://217.198.9.199:80 | Основной UI |
| **API** | http://217.198.9.199/api | REST API |
| **API Docs** | http://217.198.9.199/docs | Swagger документация |
| **Adminer** | http://217.198.9.199:8080 | Управление БД |

---

## 🔑 Учетные данные

После создания тестовых данных:

**Вход в приложение:**
- Email: `admin@test.com`
- Пароль: `admin123`

**Adminer (управление БД):**
- Система: `PostgreSQL`
- Сервер: `postgres`
- Пользователь: `dm_user`
- Пароль: `dm_secure_password_2025` (или ваш из .env)
- База данных: `dm_cloud_mvp`

---

## 📊 Управление контейнерами

### Просмотр логов:
```bash
# Все сервисы
docker compose -f docker-compose.production.yml logs -f

# Конкретный сервис
docker compose -f docker-compose.production.yml logs -f backend
docker compose -f docker-compose.production.yml logs -f frontend
docker compose -f docker-compose.production.yml logs -f postgres
```

### Перезапуск сервисов:
```bash
# Все сервисы
docker compose -f docker-compose.production.yml restart

# Конкретный сервис
docker compose -f docker-compose.production.yml restart backend
```

### Остановка:
```bash
# Остановить все контейнеры
docker compose -f docker-compose.production.yml stop

# Остановить и удалить контейнеры (данные БД сохранятся)
docker compose -f docker-compose.production.yml down

# Удалить всё включая данные БД
docker compose -f docker-compose.production.yml down -v
```

---

## 🔧 Обновление приложения

```bash
# 1. Остановить контейнеры
docker compose -f docker-compose.production.yml down

# 2. Обновить код (git pull или новый архив)

# 3. Пересобрать и запустить
docker compose -f docker-compose.production.yml up -d --build

# 4. Применить новые миграции если есть
docker compose -f docker-compose.production.yml exec backend alembic upgrade head
```

---

## 🐛 Troubleshooting

### Ошибка: "password authentication failed for user 'dm_user'"

**Причина:** Пароль в .env не совпадает с тем что ожидает PostgreSQL

**Решение:**
```bash
# 1. Удалить данные PostgreSQL
docker compose -f docker-compose.production.yml down -v

# 2. Проверить .env файл
cat .env | grep DB_PASSWORD

# 3. Запустить заново
docker compose -f docker-compose.production.yml up -d --build
```

### Ошибка: "table users does not exist"

**Причина:** Миграции не применены

**Решение:**
```bash
docker compose -f docker-compose.production.yml exec backend alembic upgrade head
```

### Backend не стартует

**Проверить логи:**
```bash
docker compose -f docker-compose.production.yml logs backend
```

**Проверить что PostgreSQL healthy:**
```bash
docker compose -f docker-compose.production.yml ps postgres
```

### Frontend не отображает данные

**Причина:** Неправильный REACT_APP_BACKEND_URL при сборке

**Решение:**
```bash
# Пересобрать frontend с правильным URL
docker compose -f docker-compose.production.yml build --no-cache frontend
docker compose -f docker-compose.production.yml up -d frontend
```

---

## 📈 Monitoring

### Проверка здоровья сервисов:
```bash
# Health check всех сервисов
docker compose -f docker-compose.production.yml exec backend curl -f http://localhost:8001/api/health
```

### Использование ресурсов:
```bash
docker stats
```

---

## 🔒 Безопасность для Production

1. **Измените все пароли в .env**
2. **Настройте CORS_ORIGINS на конкретные домены**
   ```env
   CORS_ORIGINS=http://217.198.9.199,https://yourdomain.com
   ```
3. **Используйте HTTPS с SSL сертификатами**
4. **Закройте ненужные порты в firewall**
5. **Регулярно обновляйте Docker образы**
6. **Настройте бэкапы PostgreSQL**

---

## 📦 Бэкап базы данных

```bash
# Создать бэкап
docker compose -f docker-compose.production.yml exec postgres pg_dump -U dm_user dm_cloud_mvp > backup_$(date +%Y%m%d).sql

# Восстановить из бэкапа
cat backup_20240101.sql | docker compose -f docker-compose.production.yml exec -T postgres psql -U dm_user dm_cloud_mvp
```

---

**DataMetrics Cloud MVP v2.0**
*Production Ready! 🚀*
