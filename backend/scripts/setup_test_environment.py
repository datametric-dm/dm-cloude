"""
Полная настройка тестового окружения
"""
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URL"))
db = client[os.getenv("DB_NAME")]

def setup():
    print("=" * 60)
    print("🚀 НАСТРОЙКА ТЕСТОВОГО ОКРУЖЕНИЯ")
    print("=" * 60)
    
    # 1. Найти существующего пользователя adminDM
    print("\n1️⃣ Поиск пользователя adminDM@test.com...")
    admin_user = db.users.find_one({"email": "adminDM@test.com"})
    
    if not admin_user:
        print("  ❌ Пользователь adminDM@test.com не найден!")
        return
    
    user_id = admin_user["id"]
    print(f"  ✅ Найден: {admin_user['email']} (ID: {user_id})")
    
    # 2. Удалить старые связи этого пользователя
    print("\n2️⃣ Очистка старых связей пользователя...")
    result = db.user_company_roles.delete_many({"user_id": user_id})
    print(f"  🗑️  Удалено {result.deleted_count} старых связей")
    
    # 3. Удалить старую компанию Data metrics
    print("\n3️⃣ Удаление старой компании Data metrics...")
    old_company = db.companies.find_one({"name": "Data metrics"})
    if old_company:
        old_company_id = old_company["id"]
        # Удалить все данные старой компании
        db.companies.delete_one({"id": old_company_id})
        db.clients.delete_many({"tenant_id": old_company_id})
        db.projects.delete_many({"tenant_id": old_company_id})
        db.invoices.delete_many({"tenant_id": old_company_id})
        db.payments.delete_many({"tenant_id": old_company_id})
        db.project_flow_columns.delete_many({"tenant_id": old_company_id})
        db.project_flow_stages.delete_many({"tenant_id": old_company_id})
        print(f"  🗑️  Удалена компания: Data metrics")
    
    # 4. Проверить наличие тестовых компаний
    print("\n4️⃣ Проверка тестовых компаний...")
    comp_001 = db.companies.find_one({"id": "comp_001"})
    comp_002 = db.companies.find_one({"id": "comp_002"})
    
    if not comp_001 or not comp_002:
        print("  ❌ Тестовые компании не найдены! Запустите seed_test_data.py")
        return
    
    print(f"  ✅ {comp_001['name']}")
    print(f"  ✅ {comp_002['name']}")
    
    # 5. Создать связи пользователя с компаниями
    print("\n5️⃣ Создание связей пользователя с компаниями...")
    
    roles = [
        {
            "id": f"ucr_comp_001_{user_id}",
            "user_id": user_id,
            "company_id": "comp_001",
            "role": "owner",
            "permissions": ["all"],
            "joined_at": "2024-11-19T10:00:00Z"
        },
        {
            "id": f"ucr_comp_002_{user_id}",
            "user_id": user_id,
            "company_id": "comp_002",
            "role": "owner",
            "permissions": ["all"],
            "joined_at": "2024-11-19T10:00:00Z"
        }
    ]
    
    db.user_company_roles.insert_many(roles)
    print("  ✅ Пользователь связан с обеими компаниями (owner)")
    
    # 6. Удалить других пользователей (demo, test, manager)
    print("\n6️⃣ Очистка других тестовых пользователей...")
    other_users = ["demo@test.com", "test@company.ru", "manager@testagency.com"]
    for email in other_users:
        result = db.users.delete_one({"email": email})
        if result.deleted_count > 0:
            print(f"  🗑️  Удален: {email}")
    
    # 7. Финальная проверка
    print("\n7️⃣ Финальная проверка...")
    print("\n📊 Итоговое состояние:")
    print(f"  Пользователей: {db.users.count_documents({})}")
    print(f"  Компаний: {db.companies.count_documents({})}")
    print(f"  Связей: {db.user_company_roles.count_documents({})}")
    
    companies = list(db.companies.find({}))
    for company in companies:
        client_count = db.clients.count_documents({"tenant_id": company["id"]})
        project_count = db.projects.count_documents({"tenant_id": company["id"]})
        invoice_count = db.invoices.count_documents({"tenant_id": company["id"]})
        print(f"\n  🏢 {company['name']}:")
        print(f"     • Клиентов: {client_count}")
        print(f"     • Проектов: {project_count}")
        print(f"     • Счетов: {invoice_count}")
    
    print("\n" + "=" * 60)
    print("✅ ГОТОВО!")
    print("=" * 60)
    print("\n🔑 Данные для входа:")
    print(f"  Email: {admin_user['email']}")
    print("  Пароль: adminDM43211")
    print("\n💡 После входа выберите одну из двух компаний!")
    
    client.close()

if __name__ == "__main__":
    setup()
