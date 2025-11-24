"""
Скрипт для наполнения БД тестовыми данными
Создает 2 компании с полным набором данных
"""
import random
from datetime import datetime, timedelta
from uuid import uuid4
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Подключение к MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "test_database")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Генераторы случайных данных
FIRST_NAMES = ["Алексей", "Дмитрий", "Елена", "Ирина", "Максим", "Ольга", "Сергей", "Анна", "Владимир", "Мария"]
LAST_NAMES = ["Иванов", "Петров", "Сидоров", "Козлов", "Морозов", "Соколов", "Лебедев", "Новиков", "Волков", "Федоров"]

COMPANY_NAMES = [
    "ООО Альфа Технологии",
    "ИП Бета Консалтинг",
    "ООО Гамма Инвест",
    "ООО Дельта Строй",
    "ИП Омега Трейд",
    "ООО Сигма Групп",
    "ООО Вектор Девелопмент",
    "ИП Импульс Медиа"
]

PROJECT_TYPES = [
    "Разработка сайта",
    "Продвижение в соцсетях",
    "SEO оптимизация",
    "Контекстная реклама",
    "Брендинг",
    "Дизайн логотипа",
    "Email маркетинг",
    "Комплексное продвижение"
]

CITIES = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань"]

def generate_email(name):
    """Генерация email"""
    domains = ["example.com", "test.ru", "mail.com", "gmail.com"]
    return f"{name.lower().replace(' ', '.')}@{random.choice(domains)}"

def generate_phone():
    """Генерация телефона"""
    return f"+7 {random.randint(900, 999)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"

def random_date(start_days_ago, end_days_ago=0):
    """Генерация случайной даты"""
    start = datetime.utcnow() - timedelta(days=start_days_ago)
    end = datetime.utcnow() - timedelta(days=end_days_ago)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

async def clear_test_data():
    """Очистка старых тестовых данных"""
    print("🧹 Очистка старых данных...")
    
    collections = [
        "companies", "user_company_roles", "clients", "projects", 
        "invoices", "payments", "project_flow_columns", "project_flow_stages"
    ]
    
    for collection_name in collections:
        result = await db[collection_name].delete_many({})
        print(f"  Удалено {result.deleted_count} записей из {collection_name}")

async def create_companies():
    """Создание 2 тестовых компаний"""
    print("\n🏢 Создание компаний...")
    
    companies = [
        {
            "id": "comp_001",
            "name": "Агентство Digital Pro",
            "legal_name": "ООО Агентство Digital Pro",
            "inn": "7701234567",
            "address": "г. Москва, ул. Тверская, д. 10",
            "subscription_status": "active",
            "subscription_plan": "business",
            "max_users": 50,
            "max_projects": 200,
            "created_at": datetime.utcnow() - timedelta(days=180)
        },
        {
            "id": "comp_002",
            "name": "Маркетинговое бюро",
            "legal_name": "ООО Маркетинговое бюро",
            "inn": "7702345678",
            "address": "г. Санкт-Петербург, Невский пр., д. 50",
            "subscription_status": "active",
            "subscription_plan": "startup",
            "max_users": 15,
            "max_projects": 50,
            "created_at": datetime.utcnow() - timedelta(days=90)
        }
    ]
    
    await db.companies.insert_many(companies)
    print(f"  ✅ Создано {len(companies)} компаний")
    return companies

async def create_clients(company_id, count=8):
    """Создание клиентов для компании"""
    print(f"\n👥 Создание {count} клиентов для {company_id}...")
    
    clients = []
    for i in range(count):
        company_name = random.choice(COMPANY_NAMES)
        contact_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        
        client = {
            "id": f"client_{company_id}_{i+1:03d}",
            "tenant_id": company_id,
            "name": company_name,
            "email": generate_email(company_name.split()[1]),
            "phone": generate_phone(),
            "address": f"г. {random.choice(CITIES)}",
            "inn": f"{random.randint(1000000000, 9999999999)}",
            "contact_person": contact_name,
            "status": random.choice(["active", "active", "active", "inactive"]),
            "created_at": random_date(150, 30)
        }
        clients.append(client)
    
    await db.clients.insert_many(clients)
    print(f"  ✅ Создано {len(clients)} клиентов")
    return clients

async def create_projects(company_id, clients, count=12):
    """Создание проектов для компании"""
    print(f"\n📁 Создание {count} проектов для {company_id}...")
    
    projects = []
    statuses = ["active", "active", "active", "completed", "completed", "on_hold"]
    
    for i in range(count):
        client = random.choice(clients)
        start_date = random_date(120, 10)
        duration = random.randint(30, 90)
        end_date = start_date + timedelta(days=duration)
        
        project = {
            "id": f"proj_{company_id}_{i+1:03d}",
            "tenant_id": company_id,
            "name": f"{random.choice(PROJECT_TYPES)} - {client['name']}",
            "client_id": client["id"],
            "client_name": client["name"],
            "description": f"Проект по {random.choice(PROJECT_TYPES).lower()}",
            "budget": random.randint(100000, 2000000),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "status": random.choice(statuses),
            "progress": random.randint(0, 100) if random.choice(statuses) == "active" else 100,
            "manager_id": f"user_{random.randint(1, 3)}",
            "created_at": start_date
        }
        projects.append(project)
    
    await db.projects.insert_many(projects)
    print(f"  ✅ Создано {len(projects)} проектов")
    return projects

async def create_invoices(company_id, clients, projects, count=25):
    """Создание счетов для компании"""
    print(f"\n💰 Создание {count} счетов для {company_id}...")
    
    invoices = []
    statuses = ["paid", "paid", "paid", "sent", "overdue"]
    
    for i in range(count):
        client = random.choice(clients)
        project = random.choice([p for p in projects if p["client_id"] == client["id"]]) if any(p["client_id"] == client["id"] for p in projects) else random.choice(projects)
        
        date = random_date(90, 0)
        due_date = date + timedelta(days=14)
        status = random.choice(statuses)
        
        invoice = {
            "id": f"inv_{company_id}_{i+1:03d}",
            "tenant_id": company_id,
            "invoice_number": f"INV-{date.year}-{i+1:04d}",
            "client_id": client["id"],
            "client_name": client["name"],
            "project_id": project["id"],
            "amount": random.randint(50000, 500000),
            "status": status,
            "date": date.isoformat(),
            "due_date": due_date.isoformat(),
            "paid_date": (due_date + timedelta(days=random.randint(-5, 5))).isoformat() if status == "paid" else None,
            "description": f"Счет на {project['name'][:30]}",
            "created_at": date
        }
        invoices.append(invoice)
    
    await db.invoices.insert_many(invoices)
    print(f"  ✅ Создано {len(invoices)} счетов")
    return invoices

async def create_payments(company_id, invoices, count=20):
    """Создание платежей для компании"""
    print(f"\n💳 Создание {count} платежей для {company_id}...")
    
    payments = []
    paid_invoices = [inv for inv in invoices if inv["status"] == "paid"][:count]
    
    for i, invoice in enumerate(paid_invoices):
        payment = {
            "id": f"pay_{company_id}_{i+1:03d}",
            "tenant_id": company_id,
            "invoice_id": invoice["id"],
            "client_id": invoice["client_id"],
            "amount": invoice["amount"],
            "payment_date": invoice["paid_date"],
            "payment_method": random.choice(["bank_transfer", "bank_transfer", "card", "cash"]),
            "status": "completed",
            "notes": f"Оплата по счету {invoice['invoice_number']}",
            "created_at": datetime.fromisoformat(invoice["paid_date"]) if invoice["paid_date"] else datetime.utcnow()
        }
        payments.append(payment)
    
    await db.payments.insert_many(payments)
    print(f"  ✅ Создано {len(payments)} платежей")
    return payments

async def create_kanban_data(company_id, projects):
    """Создание Kanban досок для компании"""
    print(f"\n📋 Создание Kanban данных для {company_id}...")
    
    # Создание колонок
    columns = [
        {
            "id": f"col_{company_id}_1",
            "tenant_id": company_id,
            "name": "Backlog",
            "type": "backlog",
            "color": "#94A3B8",
            "order": 0,
            "wip_limit": None
        },
        {
            "id": f"col_{company_id}_2",
            "tenant_id": company_id,
            "name": "To Do",
            "type": "todo",
            "color": "#3B82F6",
            "order": 1,
            "wip_limit": None
        },
        {
            "id": f"col_{company_id}_3",
            "tenant_id": company_id,
            "name": "In Progress",
            "type": "in_progress",
            "color": "#F59E0B",
            "order": 2,
            "wip_limit": 5
        },
        {
            "id": f"col_{company_id}_4",
            "tenant_id": company_id,
            "name": "Review",
            "type": "review",
            "color": "#8B5CF6",
            "order": 3,
            "wip_limit": 3
        },
        {
            "id": f"col_{company_id}_5",
            "tenant_id": company_id,
            "name": "Done",
            "type": "done",
            "color": "#10B981",
            "order": 4,
            "wip_limit": None
        }
    ]
    
    await db.project_flow_columns.insert_many(columns)
    print(f"  ✅ Создано {len(columns)} колонок")
    
    # Создание этапов для активных проектов
    active_projects = [p for p in projects if p["status"] == "active"][:5]
    stages = []
    stage_types = ["task", "milestone", "deliverable"]
    
    for project in active_projects:
        # 3-5 этапов на проект
        num_stages = random.randint(3, 5)
        for i in range(num_stages):
            column = random.choice(columns[:-1])  # Не Done
            
            stage = {
                "id": f"stage_{company_id}_{project['id']}_{i+1}",
                "tenant_id": company_id,
                "project_id": project["id"],
                "name": f"Этап {i+1}: {random.choice(['Дизайн', 'Разработка', 'Тестирование', 'Запуск', 'Оптимизация'])}",
                "description": f"Описание этапа проекта {project['name'][:30]}",
                "column_id": column["id"],
                "status": column["type"],
                "stage_type": random.choice(stage_types),
                "assigned_to": f"user_{random.randint(1, 3)}",
                "due_date": (datetime.utcnow() + timedelta(days=random.randint(5, 30))).isoformat(),
                "progress": random.randint(0, 90),
                "created_at": random_date(30, 0)
            }
            stages.append(stage)
    
    if stages:
        await db.project_flow_stages.insert_many(stages)
        print(f"  ✅ Создано {len(stages)} этапов")

async def main():
    """Основная функция"""
    print("=" * 60)
    print("🚀 НАПОЛНЕНИЕ БД ТЕСТОВЫМИ ДАННЫМИ")
    print("=" * 60)
    
    try:
        # Очистка
        await clear_test_data()
        
        # Создание компаний
        companies = await create_companies()
        
        # Наполнение данными для каждой компании
        for company in companies:
            company_id = company["id"]
            print(f"\n{'='*60}")
            print(f"📊 Наполнение данных для: {company['name']}")
            print(f"{'='*60}")
            
            # Клиенты
            clients = await create_clients(company_id, count=8)
            
            # Проекты
            projects = await create_projects(company_id, clients, count=12)
            
            # Счета
            invoices = await create_invoices(company_id, clients, projects, count=25)
            
            # Платежи
            payments = await create_payments(company_id, invoices, count=20)
            
            # Kanban
            await create_kanban_data(company_id, projects)
        
        print("\n" + "=" * 60)
        print("✅ ДАННЫЕ УСПЕШНО СОЗДАНЫ!")
        print("=" * 60)
        print("\n📊 Статистика:")
        print(f"  • Компаний: {len(companies)}")
        print(f"  • Клиентов: {len(companies) * 8}")
        print(f"  • Проектов: {len(companies) * 12}")
        print(f"  • Счетов: {len(companies) * 25}")
        print(f"  • Платежей: {len(companies) * 20}")
        print("\n🎯 Тестовые компании:")
        for company in companies:
            print(f"  • {company['name']} (ID: {company['id']})")
        
        print("\n💡 Теперь войдите в систему и выберите одну из компаний!")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
