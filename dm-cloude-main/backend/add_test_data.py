"""
Скрипт для добавления тестовых данных в базу
"""
from database.base import (
    clients_collection, 
    projects_collection, 
    services_collection,
    invoices_collection, 
    payments_collection
)
from datetime import datetime, timedelta
import uuid
import random

def clear_all_data():
    """Очистка всех коллекций"""
    print("🧹 Очистка существующих данных...")
    clients_collection.delete_many({})
    projects_collection.delete_many({})
    services_collection.delete_many({})
    invoices_collection.delete_many({})
    payments_collection.delete_many({})
    print("✅ Данные очищены")

def add_clients():
    """Добавление тестовых клиентов"""
    print("\n👥 Добавление клиентов...")
    
    clients = [
        {
            "id": str(uuid.uuid4()),
            "name": "ООО Рога и Копыта",
            "email": "roga@kopyta.ru",
            "phone": "+7 (495) 123-45-67",
            "address": "г. Москва, ул. Ленина, д. 1",
            "inn": "7707123456",
            "kpp": "770701001",
            "ogrn": "1037739123456",
            "contact_person": "Иванов Иван Иванович",
            "contact_position": "Генеральный директор",
            "notes": "Крупный клиент, работаем с 2020 года",
            "created_at": datetime.utcnow() - timedelta(days=365)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "ИП Петров П.П.",
            "email": "petrov@mail.ru",
            "phone": "+7 (499) 234-56-78",
            "address": "г. Санкт-Петербург, Невский пр., д. 50",
            "inn": "780512345678",
            "kpp": None,
            "ogrn": "304780512345678",
            "contact_person": "Петров Петр Петрович",
            "contact_position": "Индивидуальный предприниматель",
            "notes": "Малый бизнес",
            "created_at": datetime.utcnow() - timedelta(days=180)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "АО ТехноСфера",
            "email": "info@technosfera.com",
            "phone": "+7 (812) 345-67-89",
            "address": "г. Новосибирск, пр. Карла Маркса, д. 25",
            "inn": "5402123456",
            "kpp": "540201001",
            "ogrn": "1025402123456",
            "contact_person": "Сидорова Анна Васильевна",
            "contact_position": "Финансовый директор",
            "notes": "IT компания, перспективный клиент",
            "created_at": datetime.utcnow() - timedelta(days=90)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "ООО СтройКомплекс",
            "email": "zakaz@stroycomplex.ru",
            "phone": "+7 (343) 456-78-90",
            "address": "г. Екатеринбург, ул. Малышева, д. 101",
            "inn": "6671234567",
            "kpp": "667101001",
            "ogrn": "1026671234567",
            "contact_person": "Кузнецов Алексей Сергеевич",
            "contact_position": "Коммерческий директор",
            "notes": "Строительная компания",
            "created_at": datetime.utcnow() - timedelta(days=200)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "ООО Весна",
            "email": "contact@vesna.org",
            "phone": "+7 (861) 567-89-01",
            "address": "г. Краснодар, ул. Красная, д. 15",
            "inn": "2312123456",
            "kpp": "231201001",
            "ogrn": "1022312123456",
            "contact_person": "Морозова Елена Игоревна",
            "contact_position": "Директор по закупкам",
            "notes": "Торговая сеть",
            "created_at": datetime.utcnow() - timedelta(days=45)
        }
    ]
    
    clients_collection.insert_many(clients)
    print(f"✅ Добавлено {len(clients)} клиентов")
    return clients

def add_projects(clients):
    """Добавление тестовых проектов"""
    print("\n📁 Добавление проектов...")
    
    statuses = ["planning", "in_progress", "completed", "cancelled"]
    projects = []
    
    for i, client in enumerate(clients[:4]):  # Создаем проекты для первых 4 клиентов
        status = statuses[i % len(statuses)]
        
        project = {
            "id": str(uuid.uuid4()),
            "name": f"Проект {i+1} - {client['name']}",
            "client_id": client["id"],
            "description": f"Разработка системы управления для {client['name']}",
            "status": status,
            "start_date": datetime.utcnow() - timedelta(days=random.randint(30, 180)),
            "end_date": datetime.utcnow() + timedelta(days=random.randint(30, 90)),
            "budget": random.randint(100000, 1000000),
            "notes": f"Важный проект для клиента {client['name']}",
            "created_at": datetime.utcnow() - timedelta(days=random.randint(30, 180))
        }
        projects.append(project)
    
    # Добавляем еще несколько проектов
    extra_projects = [
        {
            "id": str(uuid.uuid4()),
            "name": "Внедрение CRM системы",
            "client_id": clients[0]["id"],
            "description": "Внедрение и настройка CRM для отдела продаж",
            "status": "in_progress",
            "start_date": datetime.utcnow() - timedelta(days=45),
            "end_date": datetime.utcnow() + timedelta(days=60),
            "budget": 350000,
            "notes": "Этап 2 из 3",
            "created_at": datetime.utcnow() - timedelta(days=45)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Разработка мобильного приложения",
            "client_id": clients[2]["id"],
            "description": "iOS и Android приложение для клиентов",
            "status": "in_progress",
            "start_date": datetime.utcnow() - timedelta(days=90),
            "end_date": datetime.utcnow() + timedelta(days=120),
            "budget": 850000,
            "notes": "Приоритетный проект",
            "created_at": datetime.utcnow() - timedelta(days=90)
        }
    ]
    
    projects.extend(extra_projects)
    projects_collection.insert_many(projects)
    print(f"✅ Добавлено {len(projects)} проектов")
    return projects

def add_services():
    """Добавление тестовых услуг"""
    print("\n🛠️ Добавление услуг...")
    
    services = [
        {
            "id": str(uuid.uuid4()),
            "name": "Разработка веб-сайта",
            "description": "Создание корпоративного сайта",
            "price": 150000,
            "category": "Веб-разработка",
            "unit": "шт",
            "created_at": datetime.utcnow() - timedelta(days=300)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Техническая поддержка",
            "description": "Ежемесячная техническая поддержка",
            "price": 25000,
            "category": "Поддержка",
            "unit": "мес",
            "created_at": datetime.utcnow() - timedelta(days=300)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "SEO оптимизация",
            "description": "Поисковая оптимизация сайта",
            "price": 45000,
            "category": "Маркетинг",
            "unit": "мес",
            "created_at": datetime.utcnow() - timedelta(days=250)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Дизайн интерфейса",
            "description": "UI/UX дизайн приложения",
            "price": 80000,
            "category": "Дизайн",
            "unit": "шт",
            "created_at": datetime.utcnow() - timedelta(days=200)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Настройка сервера",
            "description": "Настройка и конфигурация сервера",
            "price": 35000,
            "category": "DevOps",
            "unit": "шт",
            "created_at": datetime.utcnow() - timedelta(days=280)
        }
    ]
    
    services_collection.insert_many(services)
    print(f"✅ Добавлено {len(services)} услуг")
    return services

def add_invoices(clients, projects):
    """Добавление тестовых счетов"""
    print("\n📄 Добавление счетов...")
    
    statuses = ["draft", "sent", "paid", "overdue"]
    invoices = []
    
    for i in range(10):
        client = random.choice(clients)
        project = random.choice([p for p in projects if p["client_id"] == client["id"]] or projects[:1])
        
        issue_date = datetime.utcnow() - timedelta(days=random.randint(1, 90))
        due_date = issue_date + timedelta(days=random.randint(14, 30))
        
        invoice = {
            "id": str(uuid.uuid4()),
            "project_id": project["id"],
            "client_id": client["id"],
            "number": f"INV-2025-{1000+i}",
            "amount": random.randint(50000, 500000),
            "status": random.choice(statuses),
            "issue_date": issue_date,
            "due_date": due_date,
            "description": f"Счет на оплату работ по проекту {project['name'][:30]}",
            "notes": f"Оплата в течение {(due_date - issue_date).days} дней",
            "created_at": issue_date
        }
        invoices.append(invoice)
    
    invoices_collection.insert_many(invoices)
    print(f"✅ Добавлено {len(invoices)} счетов")
    return invoices

def add_payments(clients, invoices):
    """Добавление тестовых платежей"""
    print("\n💳 Добавление платежей...")
    
    payment_methods = ["bank_transfer", "cash", "card"]
    statuses = ["pending", "completed", "failed"]
    payments = []
    
    # Создаем платежи для оплаченных счетов
    paid_invoices = [inv for inv in invoices if inv["status"] == "paid"]
    
    for invoice in paid_invoices:
        payment = {
            "id": str(uuid.uuid4()),
            "invoice_id": invoice["id"],
            "client_id": invoice["client_id"],
            "amount": invoice["amount"],
            "payment_date": invoice["due_date"] - timedelta(days=random.randint(1, 5)),
            "payment_method": random.choice(payment_methods),
            "status": "completed",
            "description": f"Оплата по счету {invoice['number']}",
            "notes": "Оплачено вовремя",
            "created_at": invoice["due_date"] - timedelta(days=random.randint(1, 5))
        }
        payments.append(payment)
    
    # Добавляем еще несколько платежей без привязки к счетам
    for i in range(5):
        client = random.choice(clients)
        payment_date = datetime.utcnow() - timedelta(days=random.randint(1, 60))
        
        payment = {
            "id": str(uuid.uuid4()),
            "invoice_id": None,
            "client_id": client["id"],
            "amount": random.randint(10000, 100000),
            "payment_date": payment_date,
            "payment_method": random.choice(payment_methods),
            "status": random.choice(statuses),
            "description": f"Авансовый платеж от {client['name']}",
            "notes": "Предоплата за услуги",
            "created_at": payment_date
        }
        payments.append(payment)
    
    payments_collection.insert_many(payments)
    print(f"✅ Добавлено {len(payments)} платежей")
    return payments

def main():
    """Главная функция"""
    print("=" * 60)
    print("🚀 Добавление тестовых данных в DataMetrics Cloud MVP")
    print("=" * 60)
    
    # Очищаем старые данные
    clear_all_data()
    
    # Добавляем новые данные
    clients = add_clients()
    projects = add_projects(clients)
    services = add_services()
    invoices = add_invoices(clients, projects)
    payments = add_payments(clients, invoices)
    
    # Итоговая статистика
    print("\n" + "=" * 60)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 60)
    print(f"👥 Клиентов: {len(clients)}")
    print(f"📁 Проектов: {len(projects)}")
    print(f"🛠️ Услуг: {len(services)}")
    print(f"📄 Счетов: {len(invoices)}")
    print(f"💳 Платежей: {len(payments)}")
    print("=" * 60)
    print("✅ Тестовые данные успешно добавлены!")
    print("=" * 60)

if __name__ == "__main__":
    main()
