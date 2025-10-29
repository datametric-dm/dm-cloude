# 🎉 DataMetrics Cloud - Готов к использованию!

## ✨ Версия БЕЗ .env файлов

Этот проект **полностью готов к использованию** без настройки .env файлов!
Все конфигурации зашиты напрямую в код для максимальной простоты.

---

## 🚀 Быстрый старт (3 команды)

```bash
# 1. Перейдите в директорию проекта
cd /app

# 2. Запустите все сервисы
docker-compose up -d

# 3. Откройте браузер
http://localhost
```

**Готово! 🎯** Система работает!

---

## 📊 Что запустится?

После команды `docker-compose up -d` автоматически запускаются:

| Сервис | Порт | Описание | URL |
|--------|------|----------|-----|
| 🌐 **Nginx** | 80 | Главная точка входа | http://localhost |
| 🎨 **Frontend** | 3000 | React интерфейс | (через nginx) |
| ⚙️ **Backend** | 8001 | FastAPI API | http://localhost/api |
| 💾 **PostgreSQL** | 5432 | База данных | postgres://dm_user:dm_password_2024@localhost:5432/dm_cloud_mvp |
| 🗄️ **Adminer** | 8080 | Управление БД | http://localhost:8080 |

---

## 🎯 Как использовать интерфейс

### 1. Откройте браузер
```
http://localhost
```

### 2. Войдите в систему
- Если база пустая, создайте первого пользователя через `/register`
- Если есть тестовые данные, используйте учетные данные из `backend/create_test_data.py`

### 3. Работайте с данными

**Доступные разделы:**

📊 **Dashboard** - главная панель с аналитикой
- Статистика по проектам
- Сводка по платежам
- Просроченные счета
- Графики доходов

👥 **Клиенты** (Clients)
- ➕ Добавить нового клиента
- ✏️ Редактировать информацию
- 🗑️ Удалить клиента
- 🔍 Поиск и фильтрация

📁 **Проекты** (Projects)
- ➕ Создать проект
- ✏️ Изменить статус (В работе, Завершен, Отменен)
- 💰 Привязать к клиенту
- 📊 Отслеживание прогресса

🛠️ **Услуги** (Services)
- ➕ Добавить услугу
- 💵 Указать стоимость
- 📝 Описание и категория

📄 **Счета** (Invoices)
- ➕ Создать счет
- 📅 Указать срок оплаты
- ✅ Отметить оплаченным
- ⚠️ Просроченные счета

💳 **Платежи** (Payments)
- ➕ Зарегистрировать платеж
- 📊 История платежей
- 💰 Сумма и дата
- 🔗 Привязка к счетам

📈 **Отчеты** (Reports)
- 📊 Ежемесячная выручка
- 👥 Доходы по клиентам
- 📁 Распределение проектов
- ⚠️ Просроченные платежи

---

## 💾 База данных

### Автоматическое создание

При первом запуске:
1. ✅ PostgreSQL автоматически создается
2. ✅ База данных `dm_cloud_mvp` инициализируется
3. ✅ Все таблицы создаются через Alembic миграции

### Учетные данные БД

```
Host:     localhost (или postgres внутри Docker)
Port:     5432
Database: dm_cloud_mvp
User:     dm_user
Password: dm_password_2024
```

### Доступ к БД через Adminer

```
http://localhost:8080
```

Введите учетные данные выше для подключения.

---

## 🔧 Дополнительные команды

### Просмотр логов
```bash
# Все сервисы
docker-compose logs -f

# Только backend
docker-compose logs -f backend

# Только frontend
docker-compose logs -f frontend
```

### Проверка статуса
```bash
docker-compose ps
```

### Остановка сервисов
```bash
docker-compose down
```

### Перезапуск
```bash
docker-compose restart
```

### Полная очистка (удаление данных БД)
```bash
docker-compose down -v
```

---

## 🌐 Доступ через домен

### Локальная сеть

Если вы хотите открыть доступ другим устройствам в локальной сети:

1. Узнайте свой IP:
```bash
hostname -I  # Linux
ipconfig     # Windows
```

2. Откройте на другом устройстве:
```
http://YOUR_IP_ADDRESS
```

Например: `http://192.168.1.100`

### Production домен

Для использования с реальным доменом (например, `datametrics.com`):

1. Настройте DNS записи A на ваш сервер
2. Измените `server_name` в `nginx/nginx.conf`:
```nginx
server_name datametrics.com www.datametrics.com;
```
3. Добавьте SSL сертификат (Let's Encrypt):
```bash
# Установите certbot
sudo apt install certbot python3-certbot-nginx

# Получите сертификат
sudo certbot --nginx -d datametrics.com -d www.datametrics.com
```

---

## 🔒 Безопасность

### ⚠️ Важно для Production!

Текущие настройки **оптимизированы для простоты использования**.

Перед развертыванием в production **обязательно измените**:

1. **Пароль БД** в `docker-compose.yml`:
```yaml
POSTGRES_PASSWORD: your_strong_password_here
DATABASE_URL: postgresql://dm_user:your_strong_password_here@postgres:5432/dm_cloud_mvp
```

2. **SECRET_KEY** в `backend/config.py`:
```python
SECRET_KEY: str = "your_unique_secret_key_min_32_characters"
```

3. **CORS разрешения** в `backend/config.py`:
```python
CORS_ORIGINS: List[str] = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

### Генерация секретного ключа
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32
```

---

## 📂 Структура проекта

```
/app/
├── backend/              # FastAPI Backend
│   ├── config.py        # 🔧 Конфигурация (без .env)
│   ├── server.py        # FastAPI приложение
│   ├── database/        # Подключение к БД
│   ├── models/          # SQLAlchemy модели
│   ├── routers/         # API endpoints
│   ├── schemas/         # Pydantic схемы
│   └── services/        # Бизнес-логика
│
├── frontend/            # React Frontend
│   ├── src/
│   │   ├── config.js   # 🔧 Конфигурация (без .env)
│   │   ├── App.js      # Главный компонент
│   │   ├── pages/      # Страницы
│   │   ├── components/ # React компоненты
│   │   └── lib/        # API клиент
│   └── public/         # Статика
│
├── nginx/              # Nginx конфигурация
│   └── nginx.conf     # Reverse proxy
│
└── docker-compose.yml # 🚀 Запуск всего проекта
```

---

## 🆘 Решение проблем

### Проблема: Порт уже занят
```
Error: Bind for 0.0.0.0:80 failed: port is already allocated
```

**Решение**: Остановите другие сервисы или измените порт:
```yaml
# В docker-compose.yml
nginx:
  ports:
    - "8080:80"  # Вместо 80:80
```

### Проблема: Backend не запускается
```bash
# Проверьте логи
docker-compose logs backend

# Пересоздайте контейнер
docker-compose up -d --force-recreate backend
```

### Проблема: БД не подключается
```bash
# Проверьте статус PostgreSQL
docker-compose ps postgres

# Проверьте логи
docker-compose logs postgres

# Пересоздайте с чистой БД
docker-compose down -v
docker-compose up -d
```

### Проблема: Frontend показывает ошибки API
```bash
# Проверьте что backend запущен
curl http://localhost:8001/healthz

# Проверьте nginx конфигурацию
docker-compose exec nginx nginx -t

# Перезапустите nginx
docker-compose restart nginx
```

---

## 🎓 API Документация

### Swagger UI
```
http://localhost/docs
```

### OpenAPI Spec
```
http://localhost/openapi.json
```

### Примеры запросов

**Получить список клиентов:**
```bash
curl http://localhost/api/clients/
```

**Создать нового клиента:**
```bash
curl -X POST http://localhost/api/clients/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ООО Компания",
    "email": "info@company.com",
    "phone": "+7 (999) 123-45-67",
    "address": "Москва, ул. Примерная, д. 1"
  }'
```

---

## 📊 Тестовые данные

Для быстрого тестирования создайте тестовые данные:

```bash
# Войдите в контейнер backend
docker-compose exec backend bash

# Запустите скрипт создания тестовых данных
python create_test_data.py
```

Это создаст:
- ✅ Тестового пользователя
- ✅ Несколько клиентов
- ✅ Проекты
- ✅ Услуги
- ✅ Счета и платежи

---

## 🔄 Миграции базы данных

Проект использует **Alembic** для управления схемой БД.

### Применить миграции
```bash
docker-compose exec backend alembic upgrade head
```

### Создать новую миграцию
```bash
docker-compose exec backend alembic revision --autogenerate -m "Описание изменений"
```

### История миграций
```bash
docker-compose exec backend alembic history
```

---

## 💡 Дополнительные возможности

### Telegram уведомления (опционально)

Если хотите получать уведомления в Telegram:

1. Создайте бота через [@BotFather](https://t.me/botfather)
2. Получите токен бота
3. Добавьте в `backend/config.py`:
```python
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

### Загрузка файлов

Файлы автоматически сохраняются в `backend/uploads/`

Настройки в `backend/config.py`:
- MAX_FILE_SIZE: 10 MB
- Разрешенные форматы: pdf, doc, docx, xls, xlsx, jpg, png, zip

---

## 📈 Производительность

### Рекомендуемые ресурсы

**Минимальные:**
- CPU: 1 core
- RAM: 1 GB
- Disk: 5 GB

**Рекомендуемые:**
- CPU: 2 cores
- RAM: 2 GB
- Disk: 20 GB

### Оптимизация

Для высоконагруженных систем:
1. Увеличьте пул соединений БД в `backend/database/base.py`
2. Добавьте Redis для кэширования
3. Настройте горизонтальное масштабирование backend

---

## 🎯 Готово к использованию!

Проект полностью настроен и готов к работе.

**Команды для запуска:**
```bash
docker-compose up -d
```

**Откройте браузер:**
```
http://localhost
```

**Начните работать с данными!** 🚀

---

## 📞 Поддержка

Если возникли вопросы:
1. Проверьте раздел "Решение проблем" выше
2. Посмотрите логи: `docker-compose logs`
3. Проверьте документацию API: http://localhost/docs

---

**✨ Приятной работы с DataMetrics Cloud!**
