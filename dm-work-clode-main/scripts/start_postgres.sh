#!/bin/bash
# Скрипт для запуска PostgreSQL

echo "🔍 Проверка PostgreSQL..."
if pg_isready &> /dev/null; then
    echo "✅ PostgreSQL уже запущен"
else
    echo "🚀 Запуск PostgreSQL..."
    pg_ctlcluster 15 main start
    sleep 2
    
    if pg_isready &> /dev/null; then
        echo "✅ PostgreSQL успешно запущен"
    else
        echo "❌ Ошибка запуска PostgreSQL"
        exit 1
    fi
fi
