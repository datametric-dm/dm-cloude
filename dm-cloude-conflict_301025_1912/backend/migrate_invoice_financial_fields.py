"""
Скрипт миграции: добавление полей subtotal, tax_rate, tax_amount, total в счета
"""
import sys
sys.path.append('/app/backend')

from database.base import invoices_collection

print("🔄 Миграция полей счетов - добавление финансовых полей...")

# Обновляем все счета, добавляя недостающие поля
# Если total отсутствует, берем из amount
result = invoices_collection.update_many(
    {},
    [{
        "$set": {
            "subtotal": {"$ifNull": ["$subtotal", "$amount"]},
            "tax_rate": {"$ifNull": ["$tax_rate", 0.0]},
            "tax_amount": {"$ifNull": ["$tax_amount", 0.0]},
            "total": {"$ifNull": ["$total", "$amount"]}
        }
    }]
)

print(f"✅ Обновлено счетов: {result.modified_count}")
print(f"📊 Всего счетов в базе: {invoices_collection.count_documents({})}")

# Проверим результат
print("\n📋 Пример счета после миграции:")
invoice = invoices_collection.find_one()
if invoice:
    print(f"  ID: {invoice.get('id')}")
    print(f"  Number: {invoice.get('number')}")
    print(f"  Amount: {invoice.get('amount')}")
    print(f"  Subtotal: {invoice.get('subtotal')}")
    print(f"  Tax Rate: {invoice.get('tax_rate')}")
    print(f"  Tax Amount: {invoice.get('tax_amount')}")
    print(f"  Total: {invoice.get('total')}")
