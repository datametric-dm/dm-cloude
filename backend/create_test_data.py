#!/usr/bin/env python3
from database.base import SessionLocal
from models.user import User
from models.client import Client
from models.project import Project
from services.auth import get_password_hash
from datetime import datetime, timedelta

db = SessionLocal()

try:
    # Создаем пользователя
    print('👤 Создание пользователя...')
    test_user = User(
        email='admin@test.com',
        password_hash=get_password_hash('admin123'),
        full_name='Администратор',
        is_active=True,
        is_superuser=True
    )
    db.add(test_user)
    db.commit()
    print('✅ Пользователь создан: admin@test.com / admin123')

    # Создаем клиентов
    print('\n👥 Создание клиентов...')
    clients = [
        Client(
            name='ООО "Тестовая Компания"',
            company='ООО "Тестовая Компания"',
            email='test@company.ru',
            phone='+7 (999) 123-45-67',
            inn='1234567890',
            kpp='123456789',
            address='г. Москва, ул. Тестовая, д. 1',
            notes='Основной клиент',
            is_active=True
        ),
        Client(
            name='ИП Иванов Иван Иванович',
            company='ИП Иванов И.И.',
            email='ivanov@example.com',
            phone='+7 (900) 555-44-33',
            inn='9876543210',
            address='г. Санкт-Петербург, пр. Невский, д. 10',
            notes='VIP клиент',
            is_active=True
        ),
        Client(
            name='АО "Промышленный Холдинг"',
            company='АО "Промышленный Холдинг"',
            email='info@holding.ru',
            phone='+7 (495) 777-88-99',
            inn='5555666677',
            kpp='555566667',
            bank_name='Сбербанк',
            bank_account='40702810400000123456',
            bank_bik='044525225',
            address='г. Москва, ул. Промышленная, д. 25',
            notes='Крупный корпоративный клиент',
            is_active=True
        )
    ]

    for client in clients:
        db.add(client)
    db.commit()
    print(f'✅ Создано клиентов: {len(clients)}')

    # Создаем проекты
    print('\n📁 Создание проектов...')
    projects = [
        Project(
            name='Разработка веб-сайта',
            client_id=clients[0].id,
            status='in_progress',
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now() + timedelta(days=30),
            budget=500000.00,
            description='Разработка корпоративного сайта с интеграцией CRM',
            notes='Важный проект'
        ),
        Project(
            name='Мобильное приложение',
            client_id=clients[1].id,
            status='planning',
            start_date=datetime.now() + timedelta(days=7),
            end_date=datetime.now() + timedelta(days=90),
            budget=800000.00,
            description='iOS и Android приложение для доставки'
        ),
        Project(
            name='Консультационные услуги',
            client_id=clients[2].id,
            status='in_progress',
            start_date=datetime.now() - timedelta(days=15),
            end_date=datetime.now() + timedelta(days=45),
            budget=300000.00,
            description='Аудит и консультации по IT инфраструктуре'
        )
    ]

    for project in projects:
        db.add(project)
    db.commit()
    print(f'✅ Создано проектов: {len(projects)}')

    print('\n🎉 Все тестовые данные созданы успешно!')
    print('\n📊 Итого:')
    print(f'  - Пользователей: 1 (admin@test.com / admin123)')
    print(f'  - Клиентов: {len(clients)}')
    print(f'  - Проектов: {len(projects)}')

except Exception as e:
    print(f'❌ Ошибка: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
