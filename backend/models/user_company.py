"""
User-Company relationship model with roles for multi-tenancy
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class UserRole(str, Enum):
    """User roles in company"""
    OWNER = "owner"  # Full access, billing, can delete company
    ADMIN = "admin"  # Full access except billing and company deletion
    MANAGER = "manager"  # Can manage projects, clients, team
    OBSERVER = "observer"  # Read-only access


class UserCompanyRole(BaseModel):
    """User-Company relationship with role"""
    id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    user_id: str = Field(..., description="User ID")
    company_id: str = Field(..., description="Company (Tenant) ID")
    role: UserRole = Field(default=UserRole.OBSERVER, description="User role in company")
    
    # Permissions override (optional, for granular control)
    can_create_projects: bool = True
    can_edit_projects: bool = True
    can_delete_projects: bool = False
    can_manage_clients: bool = True
    can_manage_team: bool = False
    can_view_financials: bool = True
    can_edit_financials: bool = False
    can_access_reports: bool = True
    can_manage_integrations: bool = False
    
    # Metadata
    is_active: bool = True
    invited_by: Optional[str] = None  # User ID who invited
    invited_at: datetime = Field(default_factory=datetime.utcnow)
    joined_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "company_id": "company456",
                "role": "manager",
                "is_active": True
            }
        }


def get_default_permissions(role: UserRole) -> dict:
    """Get default permissions for a role"""
    permissions = {
        UserRole.OWNER: {
            "can_create_projects": True,
            "can_edit_projects": True,
            "can_delete_projects": True,
            "can_manage_clients": True,
            "can_manage_team": True,
            "can_view_financials": True,
            "can_edit_financials": True,
            "can_access_reports": True,
            "can_manage_integrations": True,
        },
        UserRole.ADMIN: {
            "can_create_projects": True,
            "can_edit_projects": True,
            "can_delete_projects": True,
            "can_manage_clients": True,
            "can_manage_team": True,
            "can_view_financials": True,
            "can_edit_financials": True,
            "can_access_reports": True,
            "can_manage_integrations": True,
        },
        UserRole.MANAGER: {
            "can_create_projects": True,
            "can_edit_projects": True,
            "can_delete_projects": False,
            "can_manage_clients": True,
            "can_manage_team": True,
            "can_view_financials": True,
            "can_edit_financials": False,
            "can_access_reports": True,
            "can_manage_integrations": False,
        },
        UserRole.OBSERVER: {
            "can_create_projects": False,
            "can_edit_projects": False,
            "can_delete_projects": False,
            "can_manage_clients": False,
            "can_manage_team": False,
            "can_view_financials": True,
            "can_edit_financials": False,
            "can_access_reports": True,
            "can_manage_integrations": False,
        },
    }
    return permissions.get(role, permissions[UserRole.OBSERVER])
