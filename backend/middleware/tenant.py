"""
Tenant middleware for multi-tenancy support
Automatically filters data by tenant_id (company_id)
"""
from fastapi import Request, HTTPException, status
from typing import Optional
from database.base import user_company_roles_collection


async def get_current_company_id(request: Request) -> Optional[str]:
    """
    Extract company_id from request headers or query params
    Header: X-Company-ID
    Query: company_id
    """
    # Try header first
    company_id = request.headers.get("X-Company-ID")
    
    # Try query param
    if not company_id:
        company_id = request.query_params.get("company_id")
    
    return company_id


async def verify_tenant_access(user_id: str, company_id: str) -> dict:
    """
    Verify that user has access to the company
    Returns user-company role document
    """
    if not user_id or not company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID and Company ID are required"
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
    
    return user_company


def check_permission(user_company: dict, permission: str) -> bool:
    """
    Check if user has specific permission
    """
    return user_company.get(permission, False)


def require_permission(permission: str):
    """
    Decorator to require specific permission
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get user_company from kwargs
            user_company = kwargs.get('user_company')
            if not user_company:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission check failed: no user_company context"
                )
            
            if not check_permission(user_company, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
