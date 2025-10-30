#!/bin/bash

# Скрипт проверки системы

set -e

echo "═══════════════════════════════════════════════════════════"
echo "🔍 ПРОВЕРКА СИСТЕМЫ DataMetrics Cloud MVP"
echo "═══════════════════════════════════════════════════════════"
echo ""

ERRORS=0
WARNINGS=0

# Функция проверки
check_service() {
    local service=$1
    local port=$2
    
    if curl -s http://localhost:$port > /dev/null 2>&1; then
        echo "✅ $service (порт $port): Работает"
    else
        echo "❌ $service (порт $port): НЕ РАБОТАЕТ"
        ((ERRORS++))
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo "✅ Файл существует: $1"
    else
        echo "❌ Файл отсутствует: $1"
        ((ERRORS++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo "✅ Директория существует: $1"
    else
        echo "❌ Директория отсутствует: $1"
        ((ERRORS++))
    fi
}

# 1. Проверка Docker
echo "1️⃣ Проверка Docker"
if command -v docker &> /dev/null; then
    echo "✅ Docker установлен: $(docker --version)"
else
    echo "❌ Docker не установлен"
    ((ERRORS++))
fi

if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose установлен: $(docker-compose --version)"
else
    echo "⚠️  Docker Compose не установлен (опционально)"
    ((WARNINGS++))
fi
echo ""

# 2. Проверка структуры проекта
echo "2️⃣ Проверка структуры проекта"
check_dir "backend"
check_dir "frontend"
check_file "backend/server.py"
check_file "backend/config.py"
check_file "frontend/package.json"
check_file "docker-compose.yml"
echo ""

# 3. Проверка зависимостей Python
echo "3️⃣ Проверка Python зависимостей"
if [ -f "backend/requirements.txt" ]; then
    echo "✅ requirements.txt найден"
    echo "   Зависимостей: $(wc -l < backend/requirements.txt | tr -d ' ')"
fi
echo ""

# 4. Проверка зависимостей Node.js
echo "4️⃣ Проверка Node.js зависимостей"
if [ -f "frontend/package.json" ]; then
    echo "✅ package.json найден"
    if [ -d "frontend/node_modules" ]; then
        echo "✅ node_modules установлен"
    else
        echo "⚠️  node_modules не установлен (запустите yarn install)"
        ((WARNINGS++))
    fi
fi
echo ""

# 5. Проверка сервисов (если запущены)
echo "5️⃣ Проверка запущенных сервисов"
check_service "Backend" "8001"
check_service "Frontend" "3000"
echo ""

# 6. Проверка базы данных
echo "6️⃣ Проверка MongoDB"
if command -v mongo &> /dev/null || command -v mongosh &> /dev/null; then
    echo "✅ MongoDB клиент установлен"
else
    echo "⚠️  MongoDB клиент не установлен (опционально)"
    ((WARNINGS++))
fi

if systemctl is-active --quiet mongod 2>/dev/null; then
    echo "✅ MongoDB сервис запущен"
elif docker ps | grep -q mongo; then
    echo "✅ MongoDB запущен в Docker"
else
    echo "⚠️  MongoDB не запущен"
    ((WARNINGS++))
fi
echo ""

# 7. Проверка портов
echo "7️⃣ Проверка доступности портов"
for port in 8001 3000 27017; do
    if lsof -i :$port > /dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo "✅ Порт $port: используется"
    else
        echo "⚠️  Порт $port: свободен (сервис не запущен)"
    fi
done
echo ""

# 8. Проверка конфигурации
echo "8️⃣ Проверка конфигурации"
if grep -q "MONGO_URL" backend/config.py; then
    echo "✅ MONGO_URL настроен в config.py"
fi

if grep -q "SECRET_KEY" backend/config.py; then
    echo "✅ SECRET_KEY настроен в config.py"
fi

if [ -f "frontend/.env" ]; then
    echo "✅ Frontend .env найден"
fi
echo ""

# 9. Проверка пользователя в БД
echo "9️⃣ Проверка тестовых данных"
if [ -f "backend/database/base.py" ]; then
    python3 -c "
import sys
sys.path.insert(0, 'backend')
try:
    from database.base import users_collection, clients_collection
    users_count = users_collection.count_documents({})
    clients_count = clients_collection.count_documents({})
    print(f'✅ Пользователей в БД: {users_count}')
    print(f'✅ Клиентов в БД: {clients_count}')
except Exception as e:
    print(f'⚠️  Не удалось подключиться к БД: {str(e)}')
" 2>/dev/null || echo "⚠️  Не удалось проверить данные в БД"
fi
echo ""

# Итоги
echo "═══════════════════════════════════════════════════════════"
echo "📊 ИТОГИ ПРОВЕРКИ"
echo "═══════════════════════════════════════════════════════════"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ ВСЁ ОТЛИЧНО! Система готова к работе."
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Есть предупреждения: $WARNINGS"
    echo "Система может работать, но рекомендуется проверить предупреждения."
    exit 0
else
    echo "❌ Обнаружены ошибки: $ERRORS"
    echo "⚠️  Предупреждения: $WARNINGS"
    echo "Необходимо исправить ошибки перед запуском."
    exit 1
fi
