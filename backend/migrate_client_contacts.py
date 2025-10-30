"""
Скрипт миграции для переноса старых контактных лиц в новый формат
"""
from database.base import get_db, clients_collection
from datetime import datetime

def migrate_client_contacts():
    """Мигрирует старые контактные лица в массив contacts"""
    
    print("Начало миграции контактных лиц...")
    
    # Получаем всех клиентов
    clients = list(clients_collection.find({}))
    
    migrated_count = 0
    
    for client in clients:
        # Проверяем, есть ли старые поля контактов
        has_old_contact = any([
            client.get("contact_person"),
            client.get("contact_position"),
            client.get("contact_phone"),
            client.get("contact_email")
        ])
        
        if has_old_contact and not client.get("contacts"):
            # Создаем новый контакт из старых полей
            new_contact = {
                "name": client.get("contact_person", ""),
                "position": client.get("contact_position", ""),
                "phone": client.get("contact_phone", ""),
                "email": client.get("contact_email", "")
            }
            
            # Обновляем клиента
            update_data = {
                "contacts": [new_contact],
                "updated_at": datetime.utcnow()
            }
            
            # Удаляем старые поля
            clients_collection.update_one(
                {"_id": client["_id"]},
                {
                    "$set": update_data,
                    "$unset": {
                        "contact_person": "",
                        "contact_position": "",
                        "contact_phone": "",
                        "contact_email": ""
                    }
                }
            )
            
            migrated_count += 1
            print(f"Мигрирован клиент: {client.get('name', 'Без имени')} (ID: {client.get('id')})")
    
    print(f"\nМиграция завершена! Обработано клиентов: {migrated_count}")

if __name__ == "__main__":
    migrate_client_contacts()
