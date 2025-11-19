"""
Helper functions for multi-tenancy support
"""
from fastapi import Header, HTTPException, status
from typing import Optional
from database.base import user_company_roles_collection


def build_tenant_query(base_query: dict, tenant_id: Optional[str]) -> dict:
    """
    Add tenant_id to query if provided
    """
    if tenant_id:
        base_query["tenant_id"] = tenant_id
    return base_query


async def verify_company_access(
    user_id: Optional[str],
    company_id: Optional[str],
    require_permission: Optional[str] = None
) -> dict:
    """
    Verify user has access to company and optionally check permission
    Returns user_company document
    """
    if not user_id or not company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User and Company authentication required"
        )
    
    user_company = user_company_roles_collection.find_one({
        "user_id": user_id,
        "company_id": company_id,
        "is_active": True
    })
    
    if not user_company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )
    
    # Check specific permission if required
    if require_permission:
        if not user_company.get(require_permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {require_permission}"
            )
    
    return user_company
