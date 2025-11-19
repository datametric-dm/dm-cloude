"""
Billing API - subscription management (without real payment processing)
"""
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import uuid4

from database.base import (
    subscription_plans_collection,
    subscriptions_collection,
    payment_methods_collection,
    billing_transactions_collection,
    billing_invoices_collection,
    companies_collection
)
from routers.auth_mongo import get_current_user

router = APIRouter(tags=["billing"], prefix="/billing")


# ============= Subscription Plans =============

@router.get("/plans")
async def get_subscription_plans():
    """Get all available subscription plans"""
    plans = list(subscription_plans_collection.find({"is_active": True}))
    
    for plan in plans:
        plan.pop("_id", None)
    
    # If no plans exist, create default ones
    if len(plans) == 0:
        default_plans = [
            {
                "id": "free_plan",
                "name": "Free",
                "plan_type": "free",
                "description": "Бесплатный тариф для начала работы",
                "monthly_price": 0,
                "quarterly_price": 0,
                "yearly_price": 0,
                "currency": "RUB",
                "max_users": 2,
                "max_projects": 5,
                "max_storage_gb": 1,
                "features": ["Базовые отчеты", "Email поддержка"],
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": "starter_plan",
                "name": "Starter",
                "plan_type": "starter",
                "description": "Для малых команд",
                "monthly_price": 2990,
                "quarterly_price": 8070,
                "yearly_price": 29900,
                "currency": "RUB",
                "max_users": 5,
                "max_projects": 20,
                "max_storage_gb": 10,
                "features": ["Все возможности Free", "CRM интеграции", "Базовые автоматизации"],
                "has_integrations": True,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": "professional_plan",
                "name": "Professional",
                "plan_type": "professional",
                "description": "Для растущих агентств",
                "monthly_price": 9990,
                "quarterly_price": 26970,
                "yearly_price": 99900,
                "currency": "RUB",
                "max_users": 20,
                "max_projects": 100,
                "max_storage_gb": 50,
                "features": [
                    "Все возможности Starter",
                    "Расширенная аналитика",
                    "AI анализ рисков",
                    "Бухгалтерские интеграции",
                    "API доступ"
                ],
                "has_api_access": True,
                "has_integrations": True,
                "has_advanced_reports": True,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": "enterprise_plan",
                "name": "Enterprise",
                "plan_type": "enterprise",
                "description": "Для крупных агентств",
                "monthly_price": 29990,
                "quarterly_price": 80970,
                "yearly_price": 299900,
                "currency": "RUB",
                "max_users": 100,
                "max_projects": 1000,
                "max_storage_gb": 500,
                "features": [
                    "Все возможности Professional",
                    "Приоритетная поддержка",
                    "Персональный менеджер",
                    "Кастомизация",
                    "SLA 99.9%"
                ],
                "has_api_access": True,
                "has_integrations": True,
                "has_advanced_reports": True,
                "has_priority_support": True,
                "is_active": True,
                "created_at": datetime.utcnow()
            }
        ]
        
        subscription_plans_collection.insert_many(default_plans)
        plans = default_plans
    
    return {"plans": plans}


# ============= Company Subscription =============

@router.get("/subscription")
async def get_company_subscription(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get company subscription"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    subscription = subscriptions_collection.find_one({"tenant_id": x_company_id})
    
    if subscription:
        subscription.pop("_id", None)
    else:
        # Create default free subscription
        subscription = {
            "id": uuid4().hex,
            "tenant_id": x_company_id,
            "plan_id": "free_plan",
            "plan_type": "free",
            "billing_cycle": "monthly",
            "status": "trial",
            "trial_start": datetime.utcnow(),
            "trial_end": datetime.utcnow() + timedelta(days=14),
            "amount": 0,
            "currency": "RUB",
            "auto_renew": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        subscriptions_collection.insert_one(subscription)
        subscription.pop("_id", None)
    
    return {"subscription": subscription}


class SubscriptionUpdate(BaseModel):
    plan_id: str
    billing_cycle: Optional[str] = "monthly"


@router.put("/subscription")
async def update_subscription(
    update_data: SubscriptionUpdate,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Update company subscription (upgrade/downgrade)"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Get plan
    plan = subscription_plans_collection.find_one({"id": update_data.plan_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Calculate amount based on billing cycle
    if update_data.billing_cycle == "monthly":
        amount = plan.get("monthly_price", 0)
    elif update_data.billing_cycle == "quarterly":
        amount = plan.get("quarterly_price", 0)
    else:  # yearly
        amount = plan.get("yearly_price", 0)
    
    # Update subscription
    now = datetime.utcnow()
    next_billing = now + timedelta(days=30 if update_data.billing_cycle == "monthly" else 90 if update_data.billing_cycle == "quarterly" else 365)
    
    subscription_update = {
        "plan_id": update_data.plan_id,
        "plan_type": plan.get("plan_type"),
        "billing_cycle": update_data.billing_cycle,
        "status": "active",
        "amount": amount,
        "current_period_start": now,
        "current_period_end": next_billing,
        "next_billing_date": next_billing,
        "updated_at": now
    }
    
    result = subscriptions_collection.update_one(
        {"tenant_id": x_company_id},
        {"$set": subscription_update}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Update company limits
    companies_collection.update_one(
        {"id": x_company_id},
        {
            "$set": {
                "subscription_plan": plan.get("plan_type"),
                "max_users": plan.get("max_users"),
                "max_projects": plan.get("max_projects"),
                "updated_at": now
            }
        }
    )
    
    return {"message": "Subscription updated", "next_billing_date": next_billing.isoformat()}


# ============= Payment Methods =============

class PaymentMethodCreate(BaseModel):
    type: str  # credit_card, bank_transfer
    card_last4: Optional[str] = None
    card_brand: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    gateway_payment_method_id: Optional[str] = None


@router.post("/payment-methods")
async def add_payment_method(
    method_data: PaymentMethodCreate,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Add payment method (NOTE: This is a placeholder - real payment processing requires Tinkoff integration)"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    method_dict = method_data.dict()
    method_dict.update({
        "id": uuid4().hex,
        "tenant_id": x_company_id,
        "gateway": "tinkoff",
        "is_default": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    payment_methods_collection.insert_one(method_dict)
    method_dict.pop("_id", None)
    
    return {"message": "Payment method added (DEMO MODE - no real card charged)", "method": method_dict}


@router.get("/payment-methods")
async def get_payment_methods(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get payment methods"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    methods = list(payment_methods_collection.find({
        "tenant_id": x_company_id,
        "is_active": True
    }))
    
    for method in methods:
        method.pop("_id", None)
    
    return {"methods": methods}


# ============= Billing History =============

@router.get("/transactions")
async def get_billing_transactions(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get billing transaction history"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    transactions = list(billing_transactions_collection.find({
        "tenant_id": x_company_id
    }).sort("created_at", -1))
    
    for tx in transactions:
        tx.pop("_id", None)
    
    return {"transactions": transactions, "count": len(transactions)}


@router.get("/invoices")
async def get_billing_invoices(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get billing invoices"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    invoices = list(billing_invoices_collection.find({
        "tenant_id": x_company_id
    }).sort("created_at", -1))
    
    for inv in invoices:
        inv.pop("_id", None)
    
    return {"invoices": invoices, "count": len(invoices)}


# ============= Subscription Actions =============

@router.post("/subscription/cancel")
async def cancel_subscription(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Cancel subscription"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    result = subscriptions_collection.update_one(
        {"tenant_id": x_company_id},
        {
            "$set": {
                "status": "cancelled",
                "cancelled_at": datetime.utcnow(),
                "auto_renew": False,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return {"message": "Subscription cancelled"}


@router.post("/subscription/reactivate")
async def reactivate_subscription(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Reactivate cancelled subscription"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    result = subscriptions_collection.update_one(
        {"tenant_id": x_company_id},
        {
            "$set": {
                "status": "active",
                "cancelled_at": None,
                "auto_renew": True,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return {"message": "Subscription reactivated"}


# ============= Usage & Limits =============

@router.get("/usage")
async def get_usage_stats(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get current usage vs limits"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    from database.base import user_company_roles_collection, projects_collection
    
    # Get current usage
    current_users = user_company_roles_collection.count_documents({
        "company_id": x_company_id,
        "is_active": True
    })
    
    current_projects = projects_collection.count_documents({
        "tenant_id": x_company_id
    })
    
    # Get limits from company
    company = companies_collection.find_one({"id": x_company_id})
    max_users = company.get("max_users", 5)
    max_projects = company.get("max_projects", 10)
    
    usage = {
        "users": {
            "current": current_users,
            "limit": max_users,
            "percentage": (current_users / max_users * 100) if max_users > 0 else 0
        },
        "projects": {
            "current": current_projects,
            "limit": max_projects,
            "percentage": (current_projects / max_projects * 100) if max_projects > 0 else 0
        }
    }
    
    return {"usage": usage}
