"""
Скрипт для загрузки тестовых данных в MongoDB
По 3 записи для каждого раздела: клиенты, проекты, счета, платежи
"""
import sys
from datetime import datetime, timedelta
from uuid import uuid4

# Добавляем путь для импорта
sys.path.append('/app/backend')

from database.base import (
    clients_collection, 
    projects_collection,
    invoices_collection,
    payments_collection
)

def clear_collections():
    """Очистить все коллекции перед загрузкой"""
    print("🗑️  Очистка коллекций...")
    clients_collection.delete_many({})
    projects_collection.delete_many({})
    invoices_collection.delete_many({})
    payments_collection.delete_many({})
    print("✅ Коллекции очищены")

def load_clients():
    """Загрузить тестовых клиентов"""
    print("\n👥 Загрузка клиентов...")
    
    clients = [
        {
            "id": str(uuid4()),
            "name": "ООО «Технологии Будущего»",
            "email": "info@techfuture.ru",
            "phone": "+7 (495) 123-45-67",
            "address": "Москва, ул. Ленина, д. 10",
            "inn": "7701234567",
            "kpp": "770101001",
            "ogrn": "1027700123456",
            "contact_person": "Иванов Иван Иванович",
            "contact_position": "Генеральный директор",
            "notes": "Крупный клиент, работаем с 2020 года",
            "created_at": datetime.utcnow(),
            "updated_at": None
        },
        {
            "id": str(uuid4()),
            "name": "ИП Петров Петр Петрович",
            "email": "petrov@example.com",
            "phone": "+7 (905) 777-88-99",
            "address": "Санкт-Петербург, Невский проспект, 50",
            "inn": "780123456789",
            "kpp": None,
            "ogrn": "304780123456789",
            "contact_person": "Петров Петр Петрович",
            "contact_position": "Индивидуальный предприниматель",
            "notes": "Малый бизнес, быстрые платежи",
            "created_at": datetime.utcnow(),
            "updated_at": None
        },
        {
            "id": str(uuid4()),
            "name": "АО «МегаСтрой»",
            "email": "contracts@megastroy.ru",
            "phone": "+7 (812) 555-12-34",
            "address": "Екатеринбург, пр. Ленина, 101",
            "inn": "6601987654",
            "kpp": "660101001",
            "ogrn": "1026600987654",
            "contact_person": "Сидорова Анна Васильевна",
            "contact_position": "Финансовый директор",
            "notes": "Строительная компания, долгосрочные контракты",
            "created_at": datetime.utcnow(),
            "updated_at": None
        }
    ]
    
    clients_collection.insert_many(clients)
    print(f"✅ Загружено клиентов: {len(clients)}")
    return clients

def load_projects(clients):
    """Загрузить тестовые проекты"""
    print("\n📁 Загрузка проектов...")
    
    today = datetime.utcnow()
    
    projects = [
        {
            "id": str(uuid4()),
            "name": "Разработка корпоративного сайта",
            "client_id": clients[0]["id"],
            "description": "Создание современного корпоративного веб-сайта с адаптивным дизайном",
            "status": "in_progress",
            "start_date": today - timedelta(days=30),
            "end_date": today + timedelta(days=30),
            "budget": 500000.00,
            "notes": "Проект идет по плану",
            "created_at": today - timedelta(days=30),
            "updated_at": today - timedelta(days=5)
        },
        {
            "id": str(uuid4()),
            "name": "Внедрение CRM системы",
            "client_id": clients[1]["id"],
            "description": "Настройка и внедрение CRM для управления клиентами",
            "status": "planning",
            "start_date": today + timedelta(days=7),
            "end_date": today + timedelta(days=60),
            "budget": 250000.00,
            "notes": "Ожидаем подписания договора",
            "created_at": today - timedelta(days=10),
            "updated_at": None
        },
        {
            "id": str(uuid4()),
            "name": "Модернизация IT-инфраструктуры",
            "client_id": clients[2]["id"],
            "description": "Обновление серверного оборудования и настройка сетевой инфраструктуры",
            "status": "completed",
            "start_date": today - timedelta(days=90),
            "end_date": today - timedelta(days=10),
            "budget": 1200000.00,
            "notes": "Проект успешно завершен, клиент доволен",
            "created_at": today - timedelta(days=90),
            "updated_at": today - timedelta(days=10)
        }
    ]
    
    projects_collection.insert_many(projects)
    print(f"✅ Загружено проектов: {len(projects)}")
    return projects

def load_invoices(clients, projects):
    """Загрузить тестовые счета"""
    print("\n📄 Загрузка счетов...")
    
    today = datetime.utcnow()
    
    invoices = [
        {
            "id": str(uuid4()),
            "project_id": projects[0]["id"],
            "client_id": clients[0]["id"],
            "number": "INV-2024-001",
            "amount": 250000.00,
            "status": "sent",
            "date_issued": today - timedelta(days=15),
            "date_due": today + timedelta(days=15),
            "description": "Аванс 50% за разработку сайта",
            "notes": "Счет отправлен на email клиента",
            "created_at": today - timedelta(days=15)
        },
        {
            "id": str(uuid4()),
            "project_id": projects[1]["id"],
            "client_id": clients[1]["id"],
            "number": "INV-2024-002",
            "amount": 125000.00,
            "status": "draft",
            "date_issued": today,
            "date_due": today + timedelta(days=30),
            "description": "Аванс 50% за внедрение CRM",
            "notes": "Черновик счета, ожидает согласования",
            "created_at": today
        },
        {
            "id": str(uuid4()),
            "project_id": projects[2]["id"],
            "client_id": clients[2]["id"],
            "number": "INV-2024-003",
            "amount": 1200000.00,
            "status": "paid",
            "date_issued": today - timedelta(days=100),
            "date_due": today - timedelta(days=70),
            "description": "Полная стоимость модернизации IT-инфраструктуры",
            "notes": "Оплачено полностью, проект завершен",
            "created_at": today - timedelta(days=100)
        }
    ]
    
    invoices_collection.insert_many(invoices)
    print(f"✅ Загружено счетов: {len(invoices)}")
    return invoices

def load_payments(clients, invoices):
    """Загрузить тестовые платежи"""
    print("\n💳 Загрузка платежей...")
    
    today = datetime.utcnow()
    
    payments = [
        {
            "id": str(uuid4()),
            "invoice_id": invoices[2]["id"],
            "client_id": clients[2]["id"],
            "amount": 600000.00,
            "payment_date": today - timedelta(days=95),
            "payment_method": "bank_transfer",
            "status": "completed",
            "description": "Аванс 50% по договору",
            "notes": "Получено на расчетный счет",
            "created_at": today - timedelta(days=95)
        },
        {
            "id": str(uuid4()),
            "invoice_id": invoices[2]["id"],
            "client_id": clients[2]["id"],
            "amount": 600000.00,
            "payment_date": today - timedelta(days=20),
            "payment_method": "bank_transfer",
            "status": "completed",
            "description": "Окончательный расчет по договору",
            "notes": "Проект полностью оплачен",
            "created_at": today - timedelta(days=20)
        },
        {
            "id": str(uuid4()),
            "invoice_id": invoices[0]["id"],
            "client_id": clients[0]["id"],
            "amount": 250000.00,
            "payment_date": today - timedelta(days=10),
            "payment_method": "bank_transfer",
            "status": "completed",
            "description": "Аванс за разработку сайта",
            "notes": "Платеж получен, работа начата",
            "created_at": today - timedelta(days=10)
        }
    ]
    
    payments_collection.insert_many(payments)
    print(f"✅ Загружено платежей: {len(payments)}")
    return payments

def main():
    """Основная функция загрузки данных"""
    print("=" * 60)
    print("🚀 ЗАГРУЗКА ТЕСТОВЫХ ДАННЫХ В MongoDB")
    print("=" * 60)
    
    try:
        # Очищаем коллекции
        clear_collections()
        
        # Загружаем данные последовательно
        clients = load_clients()
        projects = load_projects(clients)
        invoices = load_invoices(clients, projects)
        payments = load_payments(clients, invoices)
        
        print("\n" + "=" * 60)
        print("✅ ВСЕ ТЕСТОВЫЕ ДАННЫЕ УСПЕШНО ЗАГРУЖЕНЫ!")
        print("=" * 60)
        print(f"\n📊 Итого загружено:")
        print(f"   • Клиентов: {len(clients)}")
        print(f"   • Проектов: {len(projects)}")
        print(f"   • Счетов: {len(invoices)}")
        print(f"   • Платежей: {len(payments)}")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ ОШИБКА при загрузке данных: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
