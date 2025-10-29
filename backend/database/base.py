import os
from pymongo import MongoClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "dm_cloud_mvp")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Определяем коллекции
users_collection = db["users"]
clients_collection = db["clients"]
projects_collection = db["projects"]
services_collection = db["services"]
invoices_collection = db["invoices"]
payments_collection = db["payments"]
files_collection = db["files"]

# Функция для зависимости FastAPI
def get_db():
    """Возвращает экземпляр базы данных"""
    return db
