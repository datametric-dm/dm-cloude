#!/bin/bash

# Скрипт запуска системы

set -e

echo "═══════════════════════════════════════════════════════════"
echo "🚀 ЗАПУСК DataMetrics Cloud MVP"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Переменные
BACKEND_PORT=8001
FRONTEND_PORT=3000
MONGO_PORT=27017

# Функция проверки порта
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":$port "; then
        return 0
    else
        return 1
    fi
}

# Функция остановки процесса на порту
kill_port() {
    local port=$1
    echo "⚠️  Порт $port занят, освобождаем..."
    lsof -ti :$port | xargs kill -9 2>/dev/null || true
    sleep 2
}

# 1. Проверка и запуск MongoDB
echo "1️⃣ Проверка MongoDB"
if systemctl is-active --quiet mongod 2>/dev/null; then
    echo "✅ MongoDB уже запущен (systemd)"
elif docker ps | grep -q mongo; then
    echo "✅ MongoDB уже запущен (Docker)"
elif check_port $MONGO_PORT; then
    echo "✅ MongoDB запущен на порту $MONGO_PORT"
else
    echo "⚠️  MongoDB не запущен, пытаемся запустить..."
    
    # Пробуем запустить через systemd
    if command -v systemctl &> /dev/null; then
        sudo systemctl start mongod 2>/dev/null && echo "✅ MongoDB запущен через systemd" || true
    fi
    
    # Если не получилось, пробуем Docker
    if ! check_port $MONGO_PORT && command -v docker &> /dev/null; then
        docker run -d --name dm_mongo -p 27017:27017 mongo:latest 2>/dev/null && echo "✅ MongoDB запущен через Docker" || true
    fi
fi
echo ""

# 2. Установка зависимостей
echo "2️⃣ Проверка и установка зависимостей"

# Backend
if [ ! -d "backend/.venv" ]; then
    echo "📦 Создание виртуального окружения Python..."
    cd backend
    python3 -m venv .venv
    cd ..
fi

echo "📦 Установка Python зависимостей..."
cd backend
source .venv/bin/activate
pip install -q -r requirements.txt
cd ..
echo "✅ Python зависимости установлены"

# Frontend
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Установка Node.js зависимостей..."
    cd frontend
    yarn install --silent
    cd ..
    echo "✅ Node.js зависимости установлены"
else
    echo "✅ Node.js зависимости уже установлены"
fi
echo ""

# 3. Применение миграций
echo "3️⃣ Применение миграций базы данных"
cd backend
source .venv/bin/activate
if [ -f "alembic.ini" ]; then
    alembic upgrade head 2>/dev/null && echo "✅ Миграции применены" || echo "⚠️  Миграции не применены (возможно, используется MongoDB без миграций)"
else
    echo "ℹ️  Миграции не требуются (MongoDB)"
fi
cd ..
echo ""

# 4. Создание тестовых данных
echo "4️⃣ Проверка тестовых данных"
cd backend
source .venv/bin/activate
python -c "
from database.base import users_collection
users = users_collection.count_documents({})
if users == 0:
    print('⚠️  Пользователи не найдены, запускаем создание тестовых данных...')
    import subprocess
    subprocess.run(['python', 'add_test_data.py'])
else:
    print(f'✅ Найдено пользователей: {users}')
" 2>/dev/null || echo "⚠️  Не удалось проверить пользователей"
cd ..
echo ""

# 5. Запуск Backend
echo "5️⃣ Запуск Backend"
if check_port $BACKEND_PORT; then
    echo "⚠️  Порт $BACKEND_PORT уже занят"
    read -p "Остановить процесс и перезапустить? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill_port $BACKEND_PORT
    fi
fi

if ! check_port $BACKEND_PORT; then
    echo "🚀 Запуск Backend на порту $BACKEND_PORT..."
    cd backend
    source .venv/bin/activate
    nohup uvicorn server:app --host 0.0.0.0 --port $BACKEND_PORT > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../logs/backend.pid
    cd ..
    sleep 3
    
    if check_port $BACKEND_PORT; then
        echo "✅ Backend запущен (PID: $BACKEND_PID)"
    else
        echo "❌ Не удалось запустить Backend"
    fi
fi
echo ""

# 6. Запуск Frontend
echo "6️⃣ Запуск Frontend"
if check_port $FRONTEND_PORT; then
    echo "⚠️  Порт $FRONTEND_PORT уже занят"
    read -p "Остановить процесс и перезапустить? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill_port $FRONTEND_PORT
    fi
fi

if ! check_port $FRONTEND_PORT; then
    echo "🚀 Запуск Frontend на порту $FRONTEND_PORT..."
    cd frontend
    nohup yarn start > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    cd ..
    echo "⏳ Ожидание запуска Frontend (это может занять 30-60 секунд)..."
    sleep 30
    
    if check_port $FRONTEND_PORT; then
        echo "✅ Frontend запущен (PID: $FRONTEND_PID)"
    else
        echo "⚠️  Frontend еще запускается..."
    fi
fi
echo ""

# 7. Проверка статуса
echo "7️⃣ Проверка статуса сервисов"
sleep 5

if curl -s http://localhost:$BACKEND_PORT/healthz > /dev/null 2>&1; then
    echo "✅ Backend отвечает на http://localhost:$BACKEND_PORT"
else
    echo "❌ Backend не отвечает"
fi

if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
    echo "✅ Frontend отвечает на http://localhost:$FRONTEND_PORT"
else
    echo "⚠️  Frontend еще запускается..."
fi
echo ""

# Итоги
echo "═══════════════════════════════════════════════════════════"
echo "🎉 ЗАПУСК ЗАВЕРШЕН"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📍 Доступ к приложению:"
echo "   Frontend: http://localhost:$FRONTEND_PORT"
echo "   Backend:  http://localhost:$BACKEND_PORT"
echo "   API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "🔑 Учетные данные:"
echo "   Email:    adminDM@test.com"
echo "   Пароль:   adminDM4321!"
echo ""
echo "📝 Логи:"
echo "   Backend:  tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo ""
echo "🛑 Остановка:"
echo "   ./stop.sh"
echo ""
