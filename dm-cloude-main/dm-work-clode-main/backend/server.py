import os
from fastapi import FastAPI, APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import logging

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import routers (we'll create them soon)
from routers.health import router as health_router
from routers.auth import router as auth_router
from routers.clients import router as clients_router
from routers.projects import router as projects_router
from routers.services import router as services_router
from routers.invoices import router as invoices_router
from routers.payments import router as payments_router
from routers.reports import router as reports_router
from routers.files import router as files_router
from routers.telegram import router as telegram_router

app = FastAPI(
    title="DataMetrics Cloud MVP",
    version="2.0.0",
    description="Современный сервис для управления проектами, клиентами, счетами, платежами и отчётами.",
    docs_url="/docs",
    openapi_url="/openapi.json",
    openapi_version="3.0.3",
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Include all routers
api_router.include_router(health_router, tags=["Система"])
api_router.include_router(auth_router, tags=["Аутентификация"])
api_router.include_router(clients_router, tags=["Клиенты"])
api_router.include_router(projects_router, tags=["Проекты"])
api_router.include_router(services_router, tags=["Услуги"])
api_router.include_router(invoices_router, tags=["Счета"])
api_router.include_router(payments_router, tags=["Платежи"])
api_router.include_router(reports_router, tags=["Отчеты"])
api_router.include_router(files_router, tags=["Файлы"])
api_router.include_router(telegram_router, tags=["Telegram"])

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "service": "DataMetrics Cloud MVP", 
        "version": "2.0.0",
        "description": "Система управления проектами",
        "env": os.getenv("APP_ENV", "production")
    }

@app.get("/healthz")
def healthz():
    """Simple health check for Docker"""
    return {"status": "OK"}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 DataMetrics Cloud MVP запускается...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🔄 DataMetrics Cloud MVP завершает работу...")
