from fastapi import FastAPI
from routers.auth_mongo import router as auth_router
from starlette.middleware.cors import CORSMiddleware

# Import only Mongo-based routers
def try_import(path):
    try:
        module = __import__(path, fromlist=['router'])
        return getattr(module, 'router', None)
    except Exception:
        return None

app = FastAPI(title="DataMetrics Cloud — Mongo Stack")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = [
    try_import("routers.auth_mongo"),
    try_import("routers.companies_mongo"),
    try_import("routers.team_mongo"),
    try_import("routers.clients_mongo"),
    try_import("routers.projects_mongo"),
    try_import("routers.services_mongo"),
    try_import("routers.invoices_mongo"),
    try_import("routers.payments_mongo"),
    try_import("routers.reports_mongo"),
    try_import("routers.files_mongo"),
    try_import("routers.telegram_mongo"),
]

for r in routers:
    if r is not None:
        app.include_router(r, prefix="/api")

from routers.health_mongo import router as health_router
from routers.auth_mongo import router as auth_router

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")

