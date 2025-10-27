#!/bin/bash

echo "🔧 Настройка .env файлов для DataMetrics Cloud MVP"
echo "================================================"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка типа развертывания
echo ""
echo "Выберите тип развертывания:"
echo "1) Docker (для production с docker-compose)"
echo "2) Локальное (для разработки или Emergent supervisor)"
echo ""
read -p "Ваш выбор (1 или 2): " deployment_type

# Функция для создания /app/.env (Docker)
create_root_env_docker() {
    cat > /app/.env << 'EOF'
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
EOF
    echo -e "${GREEN}✅ Создан /app/.env для Docker${NC}"
}

# Функция для создания backend/.env (локально)
create_backend_env_local() {
    cat > /app/backend/.env << 'EOF'
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
EOF
    echo -e "${GREEN}✅ Создан /app/backend/.env для localhost${NC}"
}

# Функция для создания backend/.env.docker
create_backend_env_docker() {
    cat > /app/backend/.env.docker << 'EOF'
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
EOF
    echo -e "${GREEN}✅ Создан /app/backend/.env.docker${NC}"
}

# Функция для создания frontend/.env
create_frontend_env() {
    local backend_url=$1
    cat > /app/frontend/.env << EOF
REACT_APP_BACKEND_URL=${backend_url}
EOF
    echo -e "${GREEN}✅ Создан /app/frontend/.env${NC}"
}

echo ""
if [ "$deployment_type" == "1" ]; then
    echo "📦 Настройка для Docker развертывания..."
    echo ""
    
    create_root_env_docker
    create_backend_env_docker
    create_frontend_env "http://localhost"
    
    echo ""
    echo -e "${YELLOW}⚠️  ВАЖНО: Измените следующие значения в .env файлах перед запуском:${NC}"
    echo "   - DB_PASSWORD в /app/.env"
    echo "   - SECRET_KEY в /app/.env"
    echo ""
    echo "Для запуска выполните:"
    echo "   docker compose -f docker-compose.production.yml up -d --build"
    
elif [ "$deployment_type" == "2" ]; then
    echo "🏠 Настройка для локального развертывания..."
    echo ""
    
    create_backend_env_local
    
    read -p "Введите URL бэкенда для frontend (например http://localhost:8001): " backend_url
    if [ -z "$backend_url" ]; then
        backend_url="http://localhost:8001"
    fi
    create_frontend_env "$backend_url"
    
    echo ""
    echo -e "${YELLOW}⚠️  Не забудьте:${NC}"
    echo "   1. Запустить PostgreSQL:"
    echo "      pg_ctlcluster 15 main start"
    echo ""
    echo "   2. Создать базу данных:"
    echo "      sudo -u postgres psql -c \"CREATE USER dm_user WITH PASSWORD 'dm_secure_password_2025';\""
    echo "      sudo -u postgres psql -c \"CREATE DATABASE dm_cloud_mvp OWNER dm_user;\""
    echo ""
    echo "   3. Применить миграции:"
    echo "      cd backend && alembic upgrade head"
    echo ""
    echo "   4. Создать данные:"
    echo "      python3 create_test_data.py"
    echo ""
    echo "   5. Перезапустить сервисы:"
    echo "      sudo supervisorctl restart all"
    
else
    echo -e "${YELLOW}⚠️  Неверный выбор. Используйте 1 или 2${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Настройка .env файлов завершена!${NC}"
echo ""
echo "📚 Подробнее о .env файлах: см. ENV_FILES_GUIDE.md"
