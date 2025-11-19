import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "dm_cloud_mvp")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Определяем коллекции
users_collection = db["users"]
companies_collection = db["companies"]
user_company_roles_collection = db["user_company_roles"]
clients_collection = db["clients"]
projects_collection = db["projects"]
services_collection = db["services"]
invoices_collection = db["invoices"]
payments_collection = db["payments"]
files_collection = db["files"]
project_stages_collection = db["project_stages"]
kanban_columns_collection = db["kanban_columns"]
financial_records_collection = db["financial_records"]
cash_flow_forecasts_collection = db["cash_flow_forecasts"]
weekly_summaries_collection = db["weekly_summaries"]
work_time_records_collection = db["work_time_records"]
user_workloads_collection = db["user_workloads"]
department_workloads_collection = db["department_workloads"]
task_assignments_collection = db["task_assignments"]
workload_forecasts_collection = db["workload_forecasts"]

# Функция для зависимости FastAPI
def get_db():
    """Возвращает экземпляр базы данных"""
    return db
