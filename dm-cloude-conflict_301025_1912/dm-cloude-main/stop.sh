#!/bin/bash

# Скрипт остановки системы

echo "═══════════════════════════════════════════════════════════"
echo "🛑 ОСТАНОВКА DataMetrics Cloud MVP"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Функция остановки процесса
stop_service() {
    local name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        PID=$(cat $pid_file)
        if ps -p $PID > /dev/null 2>&1; then
            echo "🛑 Остановка $name (PID: $PID)..."
            kill $PID 2>/dev/null
            sleep 2
            
            if ps -p $PID > /dev/null 2>&1; then
                echo "⚠️  Принудительная остановка $name..."
                kill -9 $PID 2>/dev/null
            fi
            
            rm $pid_file
            echo "✅ $name остановлен"
        else
            echo "ℹ️  $name не запущен"
            rm $pid_file
        fi
    else
        echo "ℹ️  PID файл $name не найден"
    fi
}

# Функция остановки по порту
stop_port() {
    local name=$1
    local port=$2
    
    if lsof -i :$port > /dev/null 2>&1; then
        echo "🛑 Остановка процессов на порту $port ($name)..."
        lsof -ti :$port | xargs kill -9 2>/dev/null
        echo "✅ Процессы на порту $port остановлены"
    else
        echo "ℹ️  Порт $port свободен"
    fi
}

# Создаем директорию для логов если нет
mkdir -p logs

# Остановка по PID файлам
stop_service "Backend" "logs/backend.pid"
stop_service "Frontend" "logs/frontend.pid"

echo ""

# Остановка по портам (на случай если PID файлы потерялись)
stop_port "Backend" "8001"
stop_port "Frontend" "3000"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ ВСЕ СЕРВИСЫ ОСТАНОВЛЕНЫ"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📝 Логи сохранены в директории logs/"
echo "🚀 Для запуска используйте: ./start.sh"
echo ""
