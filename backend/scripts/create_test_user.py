"""
Создание тестового пользователя и связывание с компаниями
"""
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Подключение к MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "test_database")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    """Создание тестового пользователя"""
    print("👤 Создание тестового пользователя...")
    
    # Проверка существования
    existing_user = db.users.find_one({"email": "demo@test.com"})
    if existing_user:
        print("  ℹ️  Пользователь demo@test.com уже существует")
        user_id = existing_user["id"]
    else:
        user = {
            "id": "user_demo_001",
            "email": "demo@test.com",
            "password_hash": pwd_context.hash("demo123"),
            "name": "Демо Пользователь",
            "created_at": "2024-11-19T10:00:00Z"
        }
        db.users.insert_one(user)
        user_id = user["id"]
        print(f"  ✅ Пользователь создан: {user['email']}")
    
    return user_id

def link_user_to_companies(user_id):
    """Связывание пользователя с компаниями"""
    print(f"\n🔗 Связывание пользователя с компаниями...")
    
    # Получить все компании
    companies = list(db.companies.find({}))
    
    for company in companies:
        # Проверка существования связи
        existing = db.user_company_roles.find_one({
            "user_id": user_id,
            "company_id": company["id"]
        })
        
        if existing:
            print(f"  ℹ️  Связь уже существует для {company['name']}")
            continue
        
        # Создание связи
        role = {
            "id": f"ucr_{company['id']}_{user_id}",
            "user_id": user_id,
            "company_id": company["id"],
            "role": "owner",  # Полный доступ для демо
            "permissions": ["all"],
            "joined_at": "2024-11-19T10:00:00Z"
        }
        
        db.user_company_roles.insert_one(role)
        print(f"  ✅ Связан с: {company['name']} (роль: owner)")

def main():
    print("=" * 60)
    print("👤 СОЗДАНИЕ ТЕСТОВОГО ПОЛЬЗОВАТЕЛЯ")
    print("=" * 60)
    
    try:
        user_id = create_test_user()
        link_user_to_companies(user_id)
        
        print("\n" + "=" * 60)
        print("✅ ГОТОВО!")
        print("=" * 60)
        print("\n🔑 Данные для входа:")
        print("  Email: demo@test.com")
        print("  Пароль: demo123")
        print("\n💡 После входа выберите одну из двух компаний!")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    main()
