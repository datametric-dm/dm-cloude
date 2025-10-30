#!/bin/bash

# 🔍 Скрипт проверки конфигурации БЕЗ .env файлов

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Проверка конфигурации проекта"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ERRORS=0
WARNINGS=0

# Функция проверки
check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
    else
        echo "❌ ОТСУТСТВУЕТ: $1"
        ((ERRORS++))
    fi
}

check_config() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo "✅ $1 содержит $2"
    else
        echo "⚠️  $1 НЕ содержит $2"
        ((WARNINGS++))
    fi
}

echo "📂 Проверка структуры файлов..."
echo ""

# Backend
echo "Backend:"
check_file "backend/config.py"
check_file "backend/server.py"
check_file "backend/database/base.py"
check_file "backend/requirements.txt"
check_file "backend/Dockerfile"
echo ""

# Frontend
echo "Frontend:"
check_file "frontend/src/config.js"
check_file "frontend/src/lib/api.js"
check_file "frontend/Dockerfile"
check_file "frontend/package.json"
echo ""

# Docker
echo "Docker:"
check_file "docker-compose.yml"
check_file "nginx/nginx.conf"
echo ""

# Документация
echo "Документация:"
check_file "README.md"
check_file "READY_TO_USE.md"
check_file "CHANGES.md"
check_file "start.sh"
echo ""

echo "🔍 Проверка содержимого конфигураций..."
echo ""

# Проверка backend/config.py
echo "Backend Config:"
check_config "backend/config.py" "class Settings"
check_config "backend/config.py" "DATABASE_URL"
check_config "backend/config.py" "SECRET_KEY"
check_config "backend/config.py" "CORS_ORIGINS"
echo ""

# Проверка frontend/src/config.js
echo "Frontend Config:"
check_config "frontend/src/config.js" "BACKEND_URL"
check_config "frontend/src/config.js" "API_BASE"
check_config "frontend/src/config.js" "endpoints"
echo ""

# Проверка database/base.py
echo "Database Config:"
check_config "backend/database/base.py" "from config import settings"
if grep -q "load_dotenv" "backend/database/base.py" 2>/dev/null; then
    echo "⚠️  backend/database/base.py всё ещё использует load_dotenv!"
    ((WARNINGS++))
else
    echo "✅ backend/database/base.py НЕ использует .env"
fi
echo ""

# Проверка server.py
echo "Server Config:"
check_config "backend/server.py" "from config import settings"
if grep -q "load_dotenv" "backend/server.py" 2>/dev/null; then
    echo "⚠️  backend/server.py всё ещё использует load_dotenv!"
    ((WARNINGS++))
else
    echo "✅ backend/server.py НЕ использует .env"
fi
echo ""

# Проверка api.js
echo "API Config:"
check_config "frontend/src/lib/api.js" "import config from"
if grep -q "process.env.REACT_APP_BACKEND_URL" "frontend/src/lib/api.js" 2>/dev/null; then
    echo "⚠️  api.js всё ещё использует process.env!"
    ((WARNINGS++))
else
    echo "✅ api.js НЕ использует process.env"
fi
echo ""

# Проверка docker-compose.yml
echo "Docker Compose:"
if grep -q "dm_password_2024" "docker-compose.yml" 2>/dev/null; then
    echo "✅ docker-compose.yml содержит дефолтный пароль"
else
    echo "⚠️  docker-compose.yml не содержит пароля"
    ((WARNINGS++))
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Результаты проверки"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "🎉 ВСЁ ОТЛИЧНО!"
    echo "✅ Проект готов к использованию без .env файлов"
    echo ""
    echo "Запустите:"
    echo "  ./start.sh"
    echo "  или"
    echo "  docker-compose up -d"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Есть предупреждения: $WARNINGS"
    echo "Проект должен работать, но проверьте предупреждения выше"
    exit 0
else
    echo "❌ ОШИБКИ: $ERRORS"
    echo "⚠️  ПРЕДУПРЕЖДЕНИЯ: $WARNINGS"
    echo "Исправьте ошибки перед запуском"
    exit 1
fi
