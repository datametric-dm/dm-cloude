#!/bin/bash

# Скрипт исправления типичных ошибок

set -e

echo "═══════════════════════════════════════════════════════════"
echo "🔧 ИСПРАВЛЕНИЕ ОШИБОК DataMetrics Cloud MVP"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "Выберите проблему для исправления:"
echo ""
echo "1) Backend не запускается"
echo "2) Frontend не запускается"
echo "3) Ошибка подключения к MongoDB"
echo "4) Порты заняты"
echo "5) Нет тестовых данных"
echo "6) Переустановка зависимостей"
echo "7) Полный сброс и перезапуск"
echo "8) Проверить логи"
echo "0) Выход"
echo ""
read -p "Введите номер (0-8): " choice

case $choice in
    1)
        echo ""
        echo "🔧 Исправление Backend..."
        echo ""
        
        # Остановка
        lsof -ti :8001 | xargs kill -9 2>/dev/null || true
        
        # Проверка Python
        if ! command -v python3 &> /dev/null; then
            echo "❌ Python3 не установлен!"
            exit 1
        fi
        
        # Переустановка зависимостей
        echo "📦 Переустановка зависимостей..."
        cd backend
        rm -rf .venv
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -q --upgrade pip
        pip install -q -r requirements.txt
        
        # Проверка конфига
        if [ ! -f "config.py" ]; then
            echo "❌ config.py не найден!"
            exit 1
        fi
        
        # Запуск
        echo "🚀 Запуск Backend..."
        nohup uvicorn server:app --host 0.0.0.0 --port 8001 > ../logs/backend.log 2>&1 &
        echo $! > ../logs/backend.pid
        cd ..
        
        sleep 5
        
        if curl -s http://localhost:8001/healthz > /dev/null 2>&1; then
            echo "✅ Backend запущен успешно!"
            echo "📝 Логи: tail -f logs/backend.log"
        else
            echo "❌ Backend не запустился. Проверьте логи: cat logs/backend.log"
        fi
        ;;
        
    2)
        echo ""
        echo "🔧 Исправление Frontend..."
        echo ""
        
        # Остановка
        lsof -ti :3000 | xargs kill -9 2>/dev/null || true
        
        # Проверка Node.js
        if ! command -v node &> /dev/null; then
            echo "❌ Node.js не установлен!"
            exit 1
        fi
        
        if ! command -v yarn &> /dev/null; then
            echo "❌ Yarn не установлен! Устанавливаем..."
            npm install -g yarn
        fi
        
        # Очистка и переустановка
        echo "📦 Очистка и переустановка зависимостей..."
        cd frontend
        rm -rf node_modules package-lock.json yarn.lock
        yarn install
        
        # Очистка кэша
        rm -rf .cache build
        
        # Запуск
        echo "🚀 Запуск Frontend..."
        nohup yarn start > ../logs/frontend.log 2>&1 &
        echo $! > ../logs/frontend.pid
        cd ..
        
        echo "⏳ Ожидание запуска (30 секунд)..."
        sleep 30
        
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo "✅ Frontend запущен успешно!"
            echo "📝 Логи: tail -f logs/frontend.log"
        else
            echo "⚠️  Frontend еще запускается. Проверьте через минуту."
            echo "📝 Логи: tail -f logs/frontend.log"
        fi
        ;;
        
    3)
        echo ""
        echo "🔧 Исправление MongoDB..."
        echo ""
        
        # Проверка установки
        if command -v mongod &> /dev/null; then
            echo "✅ MongoDB установлен"
            
            # Попытка запустить
            if systemctl is-active --quiet mongod; then
                echo "✅ MongoDB уже запущен"
            else
                echo "🚀 Запуск MongoDB..."
                sudo systemctl start mongod
                sudo systemctl enable mongod
                echo "✅ MongoDB запущен"
            fi
        elif command -v docker &> /dev/null; then
            echo "🐳 Запуск MongoDB через Docker..."
            docker rm -f dm_mongo 2>/dev/null || true
            docker run -d --name dm_mongo \
                -p 27017:27017 \
                -v dm_mongo_data:/data/db \
                mongo:latest
            
            sleep 5
            echo "✅ MongoDB запущен в Docker"
        else
            echo "❌ MongoDB не установлен и Docker не доступен!"
            echo "Установите MongoDB: https://docs.mongodb.com/manual/installation/"
            exit 1
        fi
        
        # Тест подключения
        sleep 3
        python3 -c "
import pymongo
try:
    client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    client.server_info()
    print('✅ Подключение к MongoDB успешно!')
except Exception as e:
    print(f'❌ Ошибка подключения: {e}')
" 2>/dev/null || echo "❌ Не удалось проверить подключение (pymongo не установлен)"
        ;;
        
    4)
        echo ""
        echo "🔧 Освобождение портов..."
        echo ""
        
        for port in 8001 3000 27017; do
            if lsof -i :$port > /dev/null 2>&1; then
                echo "🛑 Освобождение порта $port..."
                lsof -ti :$port | xargs kill -9 2>/dev/null
                echo "✅ Порт $port свободен"
            else
                echo "ℹ️  Порт $port уже свободен"
            fi
        done
        
        echo ""
        echo "✅ Все порты освобождены"
        echo "🚀 Теперь можно запустить: ./start.sh"
        ;;
        
    5)
        echo ""
        echo "🔧 Создание тестовых данных..."
        echo ""
        
        cd backend
        source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate
        
        # Создание пользователя
        if [ -f "update_admin_user.py" ]; then
            echo "👤 Создание пользователя..."
            python update_admin_user.py
        fi
        
        # Создание тестовых данных
        if [ -f "add_test_data.py" ]; then
            echo "📊 Создание тестовых данных..."
            python add_test_data.py
        fi
        
        cd ..
        
        echo ""
        echo "✅ Тестовые данные созданы!"
        echo ""
        echo "🔑 Учетные данные:"
        echo "   Email:    adminDM@test.com"
        echo "   Пароль:   adminDM4321!"
        ;;
        
    6)
        echo ""
        echo "🔧 Переустановка всех зависимостей..."
        echo ""
        
        # Backend
        echo "📦 Backend зависимости..."
        cd backend
        rm -rf .venv
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -q --upgrade pip
        pip install -q -r requirements.txt
        cd ..
        echo "✅ Backend зависимости установлены"
        
        # Frontend
        echo "📦 Frontend зависимости..."
        cd frontend
        rm -rf node_modules yarn.lock package-lock.json
        yarn install
        cd ..
        echo "✅ Frontend зависимости установлены"
        
        echo ""
        echo "✅ Все зависимости переустановлены!"
        echo "🚀 Теперь можно запустить: ./start.sh"
        ;;
        
    7)
        echo ""
        echo "🔧 ПОЛНЫЙ СБРОС И ПЕРЕЗАПУСК"
        echo ""
        echo "⚠️  ВНИМАНИЕ: Это остановит все сервисы и переустановит зависимости!"
        read -p "Продолжить? (y/n): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Остановка
            echo "🛑 Остановка сервисов..."
            ./stop.sh 2>/dev/null || true
            
            # Освобождение портов
            echo "🧹 Освобождение портов..."
            for port in 8001 3000; do
                lsof -ti :$port | xargs kill -9 2>/dev/null || true
            done
            
            # Очистка
            echo "🧹 Очистка старых файлов..."
            rm -rf backend/.venv frontend/node_modules logs/*.log
            
            # Переустановка
            echo "📦 Переустановка зависимостей..."
            
            cd backend
            python3 -m venv .venv
            source .venv/bin/activate
            pip install -q --upgrade pip
            pip install -q -r requirements.txt
            cd ..
            
            cd frontend
            yarn install --silent
            cd ..
            
            # Запуск
            echo "🚀 Запуск системы..."
            ./start.sh
        fi
        ;;
        
    8)
        echo ""
        echo "📝 Просмотр логов"
        echo ""
        echo "Выберите лог:"
        echo "1) Backend"
        echo "2) Frontend"
        echo "3) Оба"
        echo ""
        read -p "Выбор (1-3): " log_choice
        
        case $log_choice in
            1)
                if [ -f "logs/backend.log" ]; then
                    tail -50 logs/backend.log
                else
                    echo "❌ Лог не найден"
                fi
                ;;
            2)
                if [ -f "logs/frontend.log" ]; then
                    tail -50 logs/frontend.log
                else
                    echo "❌ Лог не найден"
                fi
                ;;
            3)
                echo "=== BACKEND ==="
                tail -30 logs/backend.log 2>/dev/null || echo "Лог не найден"
                echo ""
                echo "=== FRONTEND ==="
                tail -30 logs/frontend.log 2>/dev/null || echo "Лог не найден"
                ;;
        esac
        ;;
        
    0)
        echo "Выход"
        exit 0
        ;;
        
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ ГОТОВО"
echo "═══════════════════════════════════════════════════════════"
echo ""
