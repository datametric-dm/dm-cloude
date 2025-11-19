"""
Companies (Tenants) management endpoints
"""
from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import uuid4

from database.base import companies_collection, user_company_roles_collection, users_collection
from models.company import Company, SubscriptionStatus, SubscriptionPlan
from models.user_company import UserRole, get_default_permissions

router = APIRouter(tags=["companies"], prefix="/companies")


class CompanyCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    legal_name: Optional[str] = None
    inn: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    legal_name: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    ogrn: Optional[str] = None
    legal_address: Optional[str] = None
    actual_address: Optional[str] = None


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Create a new company (tenant)
    User who creates becomes the OWNER
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required"
        )
    
    # Verify user exists
    user = users_collection.find_one({"id": x_user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create company
    company_id = uuid4().hex
    trial_ends = datetime.utcnow() + timedelta(days=14)
    
    company_doc = {
        "id": company_id,
        "name": company_data.name,
        "email": company_data.email,
        "phone": company_data.phone,
        "legal_name": company_data.legal_name,
        "inn": company_data.inn,
        "subscription_plan": SubscriptionPlan.FREE.value,
        "subscription_status": SubscriptionStatus.TRIAL.value,
        "trial_ends_at": trial_ends,
        "is_active": True,
        "max_users": 5,
        "max_projects": 10,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": x_user_id,
    }
    
    companies_collection.insert_one(company_doc)
    
    # Add creator as OWNER
    owner_permissions = get_default_permissions(UserRole.OWNER)
    user_company_doc = {
        "id": uuid4().hex,
        "user_id": x_user_id,
        "company_id": company_id,
        "role": UserRole.OWNER.value,
        "is_active": True,
        "joined_at": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        **owner_permissions
    }
    
    user_company_roles_collection.insert_one(user_company_doc)
    
    # Remove MongoDB _id
    company_doc.pop("_id", None)
    
    return {
        "message": "Company created successfully",
        "company": company_doc,
        "role": UserRole.OWNER.value
    }


@router.get("/my")
async def get_my_companies(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Get all companies user has access to
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required"
        )
    
    # Find all user-company relationships
    user_companies = list(user_company_roles_collection.find({
        "user_id": x_user_id,
        "is_active": True
    }))
    
    if not user_companies:
        return {"companies": []}
    
    # Get company details
    company_ids = [uc["company_id"] for uc in user_companies]
    companies = list(companies_collection.find({
        "id": {"$in": company_ids},
        "is_active": True
    }))
    
    # Combine company data with user role
    result = []
    for company in companies:
        company.pop("_id", None)
        user_company = next(
            (uc for uc in user_companies if uc["company_id"] == company["id"]),
            None
        )
        result.append({
            **company,
            "user_role": user_company.get("role") if user_company else None
        })
    
    return {"companies": result}


@router.get("/{company_id}")
async def get_company(
    company_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Get company details
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required"
        )
    
    # Verify access
    user_company = user_company_roles_collection.find_one({
        "user_id": x_user_id,
        "company_id": company_id,
        "is_active": True
    })
    
    if not user_company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )
    
    company = companies_collection.find_one({"id": company_id})
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    company.pop("_id", None)
    return {
        "company": company,
        "user_role": user_company.get("role")
    }


@router.put("/{company_id}")
async def update_company(
    company_id: str,
    company_data: CompanyUpdate,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Update company details
    Only OWNER and ADMIN can update
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required"
        )
    
    # Verify access and role
    user_company = user_company_roles_collection.find_one({
        "user_id": x_user_id,
        "company_id": company_id,
        "is_active": True
    })
    
    if not user_company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )
    
    if user_company.get("role") not in [UserRole.OWNER.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only OWNER and ADMIN can update company details"
        )
    
    # Update company
    update_data = {k: v for k, v in company_data.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update"
        )
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = companies_collection.update_one(
        {"id": company_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    updated_company = companies_collection.find_one({"id": company_id})
    updated_company.pop("_id", None)
    
    return {
        "message": "Company updated successfully",
        "company": updated_company
    }


@router.delete("/{company_id}")
async def delete_company(
    company_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Delete company (soft delete)
    Only OWNER can delete
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required"
        )
    
    # Verify access and role
    user_company = user_company_roles_collection.find_one({
        "user_id": x_user_id,
        "company_id": company_id,
        "is_active": True
    })
    
    if not user_company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )
    
    if user_company.get("role") != UserRole.OWNER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only OWNER can delete company"
        )
    
    # Soft delete
    result = companies_collection.update_one(
        {"id": company_id},
        {
            "$set": {
                "is_active": False,
                "subscription_status": SubscriptionStatus.CANCELLED.value,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return {"message": "Company deleted successfully"}


@router.get("/{company_id}/stats")
async def get_company_stats(
    company_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Get company statistics
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required"
        )
    
    # Verify access
    user_company = user_company_roles_collection.find_one({
        "user_id": x_user_id,
        "company_id": company_id,
        "is_active": True
    })
    
    if not user_company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )
    
    # Get stats from other collections
    from database.base import (
        clients_collection, projects_collection, 
        invoices_collection, payments_collection
    )
    
    total_users = user_company_roles_collection.count_documents({
        "company_id": company_id,
        "is_active": True
    })
    
    total_clients = clients_collection.count_documents({
        "tenant_id": company_id,
        "is_active": True
    })
    
    total_projects = projects_collection.count_documents({
        "tenant_id": company_id
    })
    
    active_projects = projects_collection.count_documents({
        "tenant_id": company_id,
        "status": {"$in": ["planning", "in_progress", "review"]}
    })
    
    total_invoices = invoices_collection.count_documents({
        "tenant_id": company_id
    })
    
    total_payments = payments_collection.count_documents({
        "tenant_id": company_id
    })
    
    return {
        "company_id": company_id,
        "stats": {
            "total_users": total_users,
            "total_clients": total_clients,
            "total_projects": total_projects,
            "active_projects": active_projects,
            "total_invoices": total_invoices,
            "total_payments": total_payments
        }
    }
