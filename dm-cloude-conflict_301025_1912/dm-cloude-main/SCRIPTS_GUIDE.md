# 🛠️ Руководство по скриптам управления

## 📋 Доступные скрипты

### 1️⃣ check.sh - Проверка системы
**Назначение:** Комплексная проверка состояния системы

**Использование:**
```bash
./check.sh
```

**Что проверяет:**
- ✅ Наличие Docker и Docker Compose
- ✅ Структуру проекта (директории и файлы)
- ✅ Python зависимости (requirements.txt)
- ✅ Node.js зависимости (node_modules)
- ✅ Работу сервисов (Backend на 8001, Frontend на 3000)
- ✅ Подключение к MongoDB
- ✅ Наличие пользователей и данных в БД

**Результат:**
- 0 ошибок, 0 предупреждений = ✅ Всё отлично
- Есть предупреждения = ⚠️ Система может работать
- Есть ошибки = ❌ Нужно исправить

---

### 2️⃣ start.sh - Запуск системы
**Назначение:** Автоматический запуск всех компонентов системы

**Использование:**
```bash
./start.sh
```

**Что делает:**
1. Проверяет и запускает MongoDB
2. Устанавливает Python зависимости (если нужно)
3. Устанавливает Node.js зависимости (если нужно)
4. Применяет миграции БД
5. Создает тестовые данные (если их нет)
6. Запускает Backend (порт 8001)
7. Запускает Frontend (порт 3000)
8. Проверяет статус сервисов

**Результат:**
```
✅ Backend запущен на http://localhost:8001
✅ Frontend запущен на http://localhost:3000
✅ API Docs: http://localhost:8001/docs

🔑 Учетные данные:
   Email:    adminDM@test.com
   Пароль:   adminDM4321!
```

**Логи сохраняются в:**
- `logs/backend.log`
- `logs/frontend.log`

**PID файлы:**
- `logs/backend.pid`
- `logs/frontend.pid`

---

### 3️⃣ stop.sh - Остановка системы
**Назначение:** Корректная остановка всех сервисов

**Использование:**
```bash
./stop.sh
```

**Что делает:**
1. Останавливает Backend (по PID и по порту)
2. Останавливает Frontend (по PID и по порту)
3. Освобождает порты 8001 и 3000
4. Сохраняет логи

**Результат:**
```
✅ Все сервисы остановлены
📝 Логи сохранены в директории logs/
```

---

### 4️⃣ fix.sh - Исправление ошибок
**Назначение:** Интерактивное исправление типичных проблем

**Использование:**
```bash
./fix.sh
```

**Доступные исправления:**

#### 1) Backend не запускается
- Останавливает старые процессы
- Пересоздает виртуальное окружение Python
- Переустанавливает зависимости
- Проверяет конфигурацию
- Запускает Backend заново

#### 2) Frontend не запускается
- Останавливает старые процессы
- Очищает node_modules
- Переустанавливает зависимости
- Очищает кэш сборки
- Запускает Frontend заново

#### 3) Ошибка подключения к MongoDB
- Проверяет установку MongoDB
- Пытается запустить через systemd
- Пытается запустить через Docker
- Тестирует подключение

#### 4) Порты заняты
- Проверяет порты 8001, 3000, 27017
- Освобождает занятые порты
- Останавливает конфликтующие процессы

#### 5) Нет тестовых данных
- Создает администратора (adminDM@test.com)
- Добавляет 5 клиентов
- Добавляет 6 проектов
- Добавляет 10 счетов
- Добавляет 5 платежей
- Добавляет 5 услуг

#### 6) Переустановка зависимостей
- Полная очистка backend/.venv
- Полная очистка frontend/node_modules
- Переустановка всех зависимостей

#### 7) Полный сброс и перезапуск
- Останавливает все сервисы
- Очищает все зависимости
- Очищает логи
- Переустанавливает всё
- Перезапускает систему

#### 8) Проверить логи
- Просмотр логов Backend
- Просмотр логов Frontend
- Просмотр обоих логов

---

## 🚀 Типичные сценарии использования

### Первый запуск на новом сервере

```bash
# 1. Проверка системы
./check.sh

# 2. Запуск
./start.sh

# 3. Открыть в браузере
# http://your-server-ip:3000
```

### Что-то не работает

```bash
# 1. Остановить всё
./stop.sh

# 2. Исправить проблему
./fix.sh
# Выберите нужный вариант

# 3. Запустить снова
./start.sh
```

### Перезапуск после изменений в коде

```bash
# Быстрый перезапуск
./stop.sh
./start.sh
```

### Проблемы с зависимостями

```bash
./fix.sh
# Выберите "6) Переустановка зависимостей"
```

### Очистка и полный сброс

```bash
./fix.sh
# Выберите "7) Полный сброс и перезапуск"
```

---

## 📊 Структура логов

После запуска создается директория `logs/` с файлами:

```
logs/
├── backend.log      # Логи FastAPI backend
├── backend.pid      # PID процесса backend
├── frontend.log     # Логи React frontend
└── frontend.pid     # PID процесса frontend
```

**Просмотр логов в реальном времени:**
```bash
# Backend
tail -f logs/backend.log

# Frontend
tail -f logs/frontend.log

# Оба
tail -f logs/*.log
```

---

## 🔍 Диагностика проблем

### Backend не запускается

**Проверка:**
```bash
cat logs/backend.log | tail -50
```

**Типичные проблемы:**
- Не установлены зависимости → `./fix.sh` → вариант 1 или 6
- Порт занят → `./fix.sh` → вариант 4
- MongoDB недоступен → `./fix.sh` → вариант 3

### Frontend не запускается

**Проверка:**
```bash
cat logs/frontend.log | tail -50
```

**Типичные проблемы:**
- Не установлены зависимости → `./fix.sh` → вариант 2 или 6
- Порт занят → `./fix.sh` → вариант 4
- Ошибки компиляции → проверьте код

### MongoDB недоступен

**Проверка:**
```bash
# Через systemd
systemctl status mongod

# Через Docker
docker ps | grep mongo

# Тест подключения
mongo --eval "db.version()"
# ИЛИ
mongosh --eval "db.version()"
```

**Решение:**
```bash
./fix.sh
# Выберите "3) Ошибка подключения к MongoDB"
```

---

## 🎯 Быстрые команды

### Проверка состояния
```bash
./check.sh
```

### Запуск
```bash
./start.sh
```

### Остановка
```bash
./stop.sh
```

### Перезапуск
```bash
./stop.sh && ./start.sh
```

### Проверка портов
```bash
lsof -i :8001  # Backend
lsof -i :3000  # Frontend
lsof -i :27017 # MongoDB
```

### Просмотр процессов
```bash
ps aux | grep uvicorn  # Backend
ps aux | grep node     # Frontend
```

### Освобождение портов вручную
```bash
# Backend
lsof -ti :8001 | xargs kill -9

# Frontend
lsof -ti :3000 | xargs kill -9
```

---

## 🔧 Дополнительные инструменты

### Создание тестовых данных
```bash
cd backend
source .venv/bin/activate
python add_test_data.py
```

### Создание нового пользователя
```bash
cd backend
source .venv/bin/activate
python update_admin_user.py
```

### Проверка API
```bash
# Health check
curl http://localhost:8001/healthz

# Dashboard stats
curl http://localhost:8001/api/reports/dashboard

# Login test
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "adminDM@test.com", "password": "adminDM4321!"}'
```

---

## 📝 Решение проблем

### Проблема: "Port already in use"

**Решение:**
```bash
./fix.sh
# Выберите "4) Порты заняты"
```

### Проблема: "Module not found"

**Решение:**
```bash
./fix.sh
# Выберите "6) Переустановка зависимостей"
```

### Проблема: "Cannot connect to MongoDB"

**Решение:**
```bash
./fix.sh
# Выберите "3) Ошибка подключения к MongoDB"
```

### Проблема: "Нет данных в системе"

**Решение:**
```bash
./fix.sh
# Выберите "5) Нет тестовых данных"
```

### Проблема: "Не могу войти в систему"

**Решения:**

1. Проверьте что Backend работает:
```bash
curl http://localhost:8001/healthz
```

2. Проверьте учетные данные:
```bash
cd backend
source .venv/bin/activate
python -c "
from database.base import users_collection
users = list(users_collection.find())
for u in users:
    print(f\"Email: {u.get('email')}\")
"
```

3. Пересоздайте пользователя:
```bash
./fix.sh
# Выберите "5) Нет тестовых данных"
```

4. Проверьте логи Frontend:
```bash
tail -f logs/frontend.log
```

---

## 🎓 Установка на новый сервер

### Шаг 1: Установка зависимостей

**Ubuntu/Debian:**
```bash
# Python 3.11+
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Yarn
npm install -g yarn

# MongoDB
# См. https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/
```

### Шаг 2: Копирование проекта

```bash
# Копируйте архив на сервер
scp dm-cloud.zip user@server:/home/user/

# Распакуйте
cd /home/user
unzip dm-cloud.zip
cd dm-cloud
```

### Шаг 3: Настройка прав

```bash
chmod +x *.sh
```

### Шаг 4: Первый запуск

```bash
./check.sh    # Проверка
./start.sh    # Запуск
```

---

## 🌐 Доступ через домен

Если вы хотите настроить доступ через домен (например, datametrics.com):

### 1. Установите Nginx

```bash
sudo apt install nginx
```

### 2. Создайте конфигурацию

```bash
sudo nano /etc/nginx/sites-available/datametrics
```

Вставьте:
```nginx
server {
    listen 80;
    server_name datametrics.com www.datametrics.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 3. Активируйте конфигурацию

```bash
sudo ln -s /etc/nginx/sites-available/datametrics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Установите SSL (опционально)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d datametrics.com -d www.datametrics.com
```

---

## 🔐 Безопасность для Production

Перед развертыванием в production обязательно измените:

### 1. Пароль администратора

```bash
cd backend
source .venv/bin/activate
python -c "
from database.base import users_collection
from services.auth import get_password_hash

users_collection.update_one(
    {'email': 'adminDM@test.com'},
    {'\$set': {'hashed_password': get_password_hash('YOUR_STRONG_PASSWORD')}}
)
print('Пароль изменен!')
"
```

### 2. SECRET_KEY в config.py

```bash
nano backend/config.py
# Измените SECRET_KEY на уникальный ключ
```

Генерация ключа:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. CORS разрешения

```bash
nano backend/config.py
# Измените CORS_ORIGINS на конкретные домены
```

---

## 📞 Поддержка

При возникновении проблем:

1. **Запустите проверку:**
   ```bash
   ./check.sh
   ```

2. **Посмотрите логи:**
   ```bash
   ./fix.sh
   # Выберите "8) Проверить логи"
   ```

3. **Попробуйте исправить:**
   ```bash
   ./fix.sh
   # Выберите подходящий вариант
   ```

4. **Полный сброс (крайний случай):**
   ```bash
   ./fix.sh
   # Выберите "7) Полный сброс и перезапуск"
   ```

---

## ✅ Контрольный список

Перед запуском убедитесь:

- [ ] Python 3.11+ установлен
- [ ] Node.js 18+ установлен
- [ ] Yarn установлен
- [ ] MongoDB установлен и запущен
- [ ] Порты 8001, 3000, 27017 свободны
- [ ] Все скрипты имеют права на выполнение (`chmod +x *.sh`)

**Команда для установки прав:**
```bash
chmod +x check.sh start.sh stop.sh fix.sh
```

---

**✨ Готово! Используйте скрипты для управления системой!**
