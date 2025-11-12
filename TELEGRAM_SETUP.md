# Настройка Telegram Bot для отчетов

## Шаг 1: Создание бота

1. Откройте Telegram и найдите @BotFather
2. Отправьте команду `/newbot`
3. Введите название бота (например, "CRM Reports Bot")
4. Введите username бота (например, "my_crm_reports_bot")
5. BotFather пришлет вам токен в формате: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

## Шаг 2: Получение Chat ID

### Вариант 1: Личные сообщения
1. Напишите вашему боту любое сообщение
2. Откройте в браузере: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Найдите в ответе `"chat":{"id":123456789}`
4. Это ваш TELEGRAM_CHAT_ID

### Вариант 2: Групповой чат
1. Создайте группу и добавьте туда бота
2. Напишите в группе любое сообщение
3. Откройте в браузере: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Найдите в ответе `"chat":{"id":-1001234567890}` (обратите внимание на минус!)
5. Это ваш TELEGRAM_CHAT_ID для группы

## Шаг 3: Настройка переменных окружения

Добавьте в файл `/app/backend/.env`:

```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

## Шаг 4: Перезапуск backend

```bash
sudo supervisorctl restart backend
```

## Шаг 5: Тестирование

### Через API:
```bash
curl -X GET http://localhost:8001/api/telegram/test \
  -H "Authorization: Bearer <your-token>"
```

### Через интерфейс:
1. Откройте раздел "Отчеты"
2. Нажмите кнопку "Отправить отчёт в Telegram"
3. Проверьте Telegram - должно прийти сообщение с отчетом

## Доступные endpoints:

- `GET /api/telegram/test` - Тест подключения
- `POST /api/telegram/daily-report` - Отправка ежедневного отчета
- `POST /api/telegram/notify-overdue` - Уведомление о просроченных платежах
- `POST /api/telegram/send-message` - Отправка произвольного сообщения

## Формат ежедневного отчета:

📅 Ежедневный отчёт - [Дата]

👥 Всего клиентов: X
📁 Всего проектов: X
🔄 Активные проекты: X

💰 Выручка за сегодня: X ₽
✅ Оплачено счетов сегодня: X
📝 Неоплаченные счета: X
⚠️ Просроченные счета: X
