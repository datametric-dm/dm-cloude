"""
Скрипт миграции: переименование полей issue_date -> date_issued и due_date -> date_due
"""
import sys
sys.path.append('/app/backend')

from database.base import invoices_collection

print("🔄 Миграция полей счетов...")

# Обновляем все счета
result = invoices_collection.update_many(
    {},
    {
        "$rename": {
            "issue_date": "date_issued",
            "due_date": "date_due"
        }
    }
)

print(f"✅ Обновлено счетов: {result.modified_count}")
print(f"📊 Всего счетов в базе: {invoices_collection.count_documents({})}")
