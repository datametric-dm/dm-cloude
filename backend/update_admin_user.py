"""
Скрипт для обновления учетных данных администратора
"""
from database.base import users_collection
from services.auth import get_password_hash
from datetime import datetime
import uuid

def update_admin_user():
    # Удаляем старого пользователя
    old_user = users_collection.find_one({"email": "admin@test.com"})
    if old_user:
        users_collection.delete_one({"email": "admin@test.com"})
        print("✅ Старый пользователь удален")
    
    # Проверяем существует ли новый пользователь
    existing = users_collection.find_one({"email": "adminDM@test.com"})
    
    if existing:
        print("✅ Пользователь adminDM@test.com уже существует")
        print(f"   ID: {existing['id']}")
        return
    
    # Создаем нового пользователя с новыми данными
    user = {
        "id": str(uuid.uuid4()),
        "email": "adminDM@test.com",
        "hashed_password": get_password_hash("adminDM4321!"),
        "full_name": "Администратор DM",
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    users_collection.insert_one(user)
    
    print("=" * 60)
    print("✅ НОВЫЙ ПОЛЬЗОВАТЕЛЬ СОЗДАН!")
    print("=" * 60)
    print(f"   Email:    adminDM@test.com")
    print(f"   Пароль:   adminDM4321!")
    print(f"   ID:       {user['id']}")
    print(f"   Имя:      {user['full_name']}")
    print("=" * 60)

if __name__ == "__main__":
    update_admin_user()
