"""
Скрипт для создания тестового пользователя
"""
from database.base import users_collection
from services.auth import get_password_hash
from datetime import datetime
import uuid

def create_test_user():
    # Проверяем существует ли пользователь
    existing = users_collection.find_one({"email": "admin@test.com"})
    
    if existing:
        print("✅ Тестовый пользователь уже существует")
        print(f"   Email: admin@test.com")
        print(f"   ID: {existing['id']}")
        return
    
    # Создаем тестового пользователя
    user = {
        "id": str(uuid.uuid4()),
        "email": "admin@test.com",
        "hashed_password": get_password_hash("admin123"),
        "full_name": "Администратор",
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    users_collection.insert_one(user)
    
    print("✅ Тестовый пользователь создан!")
    print(f"   Email: admin@test.com")
    print(f"   Пароль: admin123")
    print(f"   ID: {user['id']}")

if __name__ == "__main__":
    create_test_user()
