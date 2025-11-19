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
client_interactions_collection = db["client_interactions"]
client_health_scores_collection = db["client_health_scores"]
client_timelines_collection = db["client_timelines"]
risks_collection = db["risks"]
project_risk_analyses_collection = db["project_risk_analyses"]
team_risk_analyses_collection = db["team_risk_analyses"]
client_churn_risks_collection = db["client_churn_risks"]
subscription_plans_collection = db["subscription_plans"]
subscriptions_collection = db["subscriptions"]
payment_methods_collection = db["payment_methods"]
billing_transactions_collection = db["billing_transactions"]
billing_invoices_collection = db["billing_invoices"]
integrations_collection = db["integrations"]
integration_logs_collection = db["integration_logs"]
integration_mappings_collection = db["integration_mappings"]
accounting_configs_collection = db["accounting_configs"]
crm_configs_collection = db["crm_configs"]
bank_configs_collection = db["bank_configs"]

# Функция для зависимости FastAPI
def get_db():
    """Возвращает экземпляр базы данных"""
    return db
