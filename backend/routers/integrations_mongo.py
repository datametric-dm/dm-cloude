'''
Integrations API - manage all integrations
'''
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
from uuid import uuid4

from database.base import (
    integrations_collection,
    integration_logs_collection,
    accounting_configs_collection,
    crm_configs_collection,
    bank_configs_collection
)
from routers.auth_mongo import get_current_user

router = APIRouter(tags=["integrations"], prefix="/integrations")


# ============= Available Integrations =============

@router.get("/available")
async def get_available_integrations(
    current_user=Depends(get_current_user)
):
    """Get list of available integrations"""
    
    available = {
        "crm": [
            {"id": "amocrm", "name": "amoCRM", "description": "Российская CRM система"},
            {"id": "bitrix24", "name": "Bitrix24", "description": "Корпоративный портал и CRM"}
        ],
        "accounting": [
            {"id": "planfact", "name": "ПланФакт", "description": "Управленческий учет"},
            {"id": "finolog", "name": "Финолог", "description": "Финансовый учет для бизнеса"},
            {"id": "kontur", "name": "Контур.Бухгалтерия", "description": "Онлайн-бухгалтерия"},
            {"id": "1c", "name": "1С", "description": "1С:Предприятие через HTTP/JSON API"},
            {"id": "my_warehouse", "name": "МойСклад", "description": "Облачный сервис учета"}
        ],
        "banks": [
            {"id": "tinkoff", "name": "Тинькофф Бизнес", "description": "Тинькофф Бизнес API"},
            {"id": "sberbank", "name": "СберБизнес", "description": "СберБизнес API"},
            {"id": "alfabank", "name": "АльфаБанк", "description": "АльфаБанк API"}
        ],
        "task_management": [
            {"id": "trello", "name": "Trello", "description": "Канбан доски"},
            {"id": "notion", "name": "Notion", "description": "Рабочее пространство"},
            {"id": "clickup", "name": "ClickUp", "description": "Управление проектами"},
            {"id": "jira", "name": "Jira", "description": "Трекер задач"},
            {"id": "planfix", "name": "Planfix", "description": "Система управления"}
        ]
    }
    
    return {"available_integrations": available}


# ============= Integration CRUD =============

class IntegrationCreate(BaseModel):
    name: str
    type: str
    provider: str
    description: Optional[str] = None
    config: Optional[Dict] = {}
    credentials: Optional[Dict] = {}
    sync_frequency: Optional[str] = "hourly"


@router.post("/")
async def create_integration(
    integration_data: IntegrationCreate,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """Create new integration"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    integration_dict = integration_data.dict()
    integration_dict.update({
        "id": uuid4().hex,
        "tenant_id": x_company_id,
        "status": "inactive",
        "is_enabled": False,
        "sync_clients": True,
        "sync_projects": True,
        "sync_invoices": True,
        "sync_payments": True,
        "error_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": x_user_id
    })
    
    integrations_collection.insert_one(integration_dict)
    integration_dict.pop("_id", None)
    
    return {"message": "Integration created", "integration": integration_dict}


@router.get("/")
async def get_integrations(
    type: Optional[str] = None,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get all company integrations"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    query = {"tenant_id": x_company_id}
    if type:
        query["type"] = type
    
    integrations = list(integrations_collection.find(query))
    for integration in integrations:
        integration.pop("_id", None)
        # Don't expose credentials in list
        integration.pop("credentials", None)
    
    return {"integrations": integrations, "count": len(integrations)}


@router.get("/{integration_id}")
async def get_integration(
    integration_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get integration details"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    integration = integrations_collection.find_one({
        "id": integration_id,
        "tenant_id": x_company_id
    })
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    integration.pop("_id", None)
    # Mask credentials
    if "credentials" in integration:
        for key in integration["credentials"]:
            if len(integration["credentials"][key]) > 4:
                integration["credentials"][key] = "***" + integration["credentials"][key][-4:]
    
    return {"integration": integration}


@router.put("/{integration_id}")
async def update_integration(
    integration_id: str,
    integration_data: IntegrationCreate,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Update integration"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    update_data = integration_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    result = integrations_collection.update_one(
        {"id": integration_id, "tenant_id": x_company_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    return {"message": "Integration updated"}


@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Delete integration"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    result = integrations_collection.delete_one({
        "id": integration_id,
        "tenant_id": x_company_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    return {"message": "Integration deleted"}


# ============= Integration Actions =============

@router.post("/{integration_id}/enable")
async def enable_integration(
    integration_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Enable integration"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    result = integrations_collection.update_one(
        {"id": integration_id, "tenant_id": x_company_id},
        {
            "$set": {
                "is_enabled": True,
                "status": "active",
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    return {"message": "Integration enabled"}


@router.post("/{integration_id}/disable")
async def disable_integration(
    integration_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Disable integration"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    result = integrations_collection.update_one(
        {"id": integration_id, "tenant_id": x_company_id},
        {
            "$set": {
                "is_enabled": False,
                "status": "inactive",
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    return {"message": "Integration disabled"}


@router.post("/{integration_id}/sync")
async def trigger_sync(
    integration_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Trigger manual sync (will be handled by Celery)"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    integration = integrations_collection.find_one({
        "id": integration_id,
        "tenant_id": x_company_id
    })
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Create log entry
    log_entry = {
        "id": uuid4().hex,
        "tenant_id": x_company_id,
        "integration_id": integration_id,
        "sync_type": "manual",
        "started_at": datetime.utcnow(),
        "status": "running",
        "records_processed": 0,
        "records_created": 0,
        "records_updated": 0,
        "records_failed": 0,
        "errors": []
    }
    
    integration_logs_collection.insert_one(log_entry)
    
    # TODO: Trigger Celery task for actual sync
    # from tasks.integrations import sync_integration
    # sync_integration.delay(integration_id, x_company_id)
    
    return {"message": "Sync triggered", "log_id": log_entry["id"]}


# ============= Integration Logs =============

@router.get("/{integration_id}/logs")
async def get_integration_logs(
    integration_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get integration sync logs"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    logs = list(integration_logs_collection.find({
        "integration_id": integration_id,
        "tenant_id": x_company_id
    }).sort("started_at", -1).limit(50))
    
    for log in logs:
        log.pop("_id", None)
    
    return {"logs": logs, "count": len(logs)}


# ============= Accounting Integration Config =============

class AccountingConfigCreate(BaseModel):
    company_id: Optional[str] = None
    organization_name: Optional[str] = None
    auto_create_invoices: bool = True
    auto_match_payments: bool = True
    vat_rate: float = 20.0
    include_vat: bool = True


@router.post("/{integration_id}/accounting-config")
async def create_accounting_config(
    integration_id: str,
    config_data: AccountingConfigCreate,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Create accounting integration config"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    config_dict = config_data.dict()
    config_dict.update({
        "id": uuid4().hex,
        "integration_id": integration_id,
        "tenant_id": x_company_id,
        "auto_create_counterparties": True,
        "export_format": "json",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    accounting_configs_collection.insert_one(config_dict)
    config_dict.pop("_id", None)
    
    return {"message": "Accounting config created", "config": config_dict}


@router.get("/{integration_id}/accounting-config")
async def get_accounting_config(
    integration_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get accounting integration config"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    config = accounting_configs_collection.find_one({
        "integration_id": integration_id,
        "tenant_id": x_company_id
    })
    
    if config:
        config.pop("_id", None)
    
    return {"config": config}
