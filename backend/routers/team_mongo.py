"""
Team management endpoints - managing users in companies
"""
from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

from database.base import user_company_roles_collection, users_collection, companies_collection
from models.user_company import UserRole, get_default_permissions

router = APIRouter(tags=["team"], prefix="/companies/{company_id}/team")


class InviteUser(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.OBSERVER
    full_name: Optional[str] = None


class UpdateUserRole(BaseModel):
    role: UserRole


class UpdatePermissions(BaseModel):
    can_create_projects: Optional[bool] = None
    can_edit_projects: Optional[bool] = None
    can_delete_projects: Optional[bool] = None
    can_manage_clients: Optional[bool] = None
    can_manage_team: Optional[bool] = None
    can_view_financials: Optional[bool] = None
    can_edit_financials: Optional[bool] = None
    can_access_reports: Optional[bool] = None
    can_manage_integrations: Optional[bool] = None


def verify_team_management_access(user_id: str, company_id: str):
    """Verify user can manage team"""
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
    
    if not user_company.get("can_manage_team", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage team"
        )
    
    return user_company


@router.post("/invite", status_code=status.HTTP_201_CREATED)
async def invite_user_to_company(
    company_id: str,
    invite_data: InviteUser,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Invite user to company
    Creates user if doesn't exist
    Only users with can_manage_team permission can invite
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required"
        )
    
    # Verify inviter has permission
    inviter = verify_team_management_access(x_user_id, company_id)
    
    # Check company exists
    company = companies_collection.find_one({"id": company_id, "is_active": True})
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check user limit
    current_users = user_company_roles_collection.count_documents({
        "company_id": company_id,
        "is_active": True
    })
    
    max_users = company.get("max_users", 5)
    if current_users >= max_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company has reached maximum users limit ({max_users})"
        )
    
    # Find or create user
    user = users_collection.find_one({"email": invite_data.email})
    
    if not user:
        # Create new user (with temporary password)
        user_id = uuid4().hex
        temp_password = uuid4().hex[:12]  # Generate temporary password
        
        from routers.auth_mongo import get_password_hash
        
        user_doc = {
            "id": user_id,
            "email": invite_data.email,
            "hashed_password": get_password_hash(temp_password),
            "full_name": invite_data.full_name,
            "is_active": True,
            "created_at": datetime.utcnow(),
        }
        users_collection.insert_one(user_doc)
        user = user_doc
    else:
        user_id = user["id"]
    
    # Check if user already in company
    existing = user_company_roles_collection.find_one({
        "user_id": user_id,
        "company_id": company_id
    })
    
    if existing:
        if existing.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this company"
            )
        else:
            # Reactivate
            user_company_roles_collection.update_one(
                {"user_id": user_id, "company_id": company_id},
                {
                    "$set": {
                        "is_active": True,
                        "role": invite_data.role.value,
                        "invited_by": x_user_id,
                        "invited_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return {"message": "User reactivated in company"}
    
    # Add user to company
    permissions = get_default_permissions(invite_data.role)
    user_company_doc = {
        "id": uuid4().hex,
        "user_id": user_id,
        "company_id": company_id,
        "role": invite_data.role.value,
        "is_active": True,
        "invited_by": x_user_id,
        "invited_at": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        **permissions
    }
    
    user_company_roles_collection.insert_one(user_company_doc)
    
    return {
        "message": "User invited successfully",
        "user": {
            "id": user_id,
            "email": user["email"],
            "full_name": user.get("full_name"),
            "role": invite_data.role.value
        }
    }


@router.get("")
async def get_team_members(
    company_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Get all team members in company
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
    
    # Get all team members
    team_members = list(user_company_roles_collection.find({
        "company_id": company_id,
        "is_active": True
    }))
    
    # Get user details
    user_ids = [tm["user_id"] for tm in team_members]
    users = list(users_collection.find({"id": {"$in": user_ids}}))
    user_map = {u["id"]: u for u in users}
    
    # Combine data
    result = []
    for tm in team_members:
        user = user_map.get(tm["user_id"], {})
        result.append({
            "user_id": tm["user_id"],
            "email": user.get("email"),
            "full_name": user.get("full_name"),
            "role": tm.get("role"),
            "is_active": tm.get("is_active", True),
            "joined_at": tm.get("joined_at"),
            "last_accessed_at": tm.get("last_accessed_at"),
            "permissions": {
                "can_create_projects": tm.get("can_create_projects", False),
                "can_edit_projects": tm.get("can_edit_projects", False),
                "can_delete_projects": tm.get("can_delete_projects", False),
                "can_manage_clients": tm.get("can_manage_clients", False),
                "can_manage_team": tm.get("can_manage_team", False),
                "can_view_financials": tm.get("can_view_financials", False),
                "can_edit_financials": tm.get("can_edit_financials", False),
                "can_access_reports": tm.get("can_access_reports", False),
                "can_manage_integrations": tm.get("can_manage_integrations", False),
            }
        })
    
    return {"team_members": result}


@router.put("/{user_id}/role")
async def update_user_role(
    company_id: str,
    user_id: str,
    role_data: UpdateUserRole,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Update user role in company
    Only users with can_manage_team permission
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required"
        )
    
    # Verify permission
    verify_team_management_access(x_user_id, company_id)
    
    # Cannot change own role
    if user_id == x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role"
        )
    
    # Get default permissions for new role
    permissions = get_default_permissions(role_data.role)
    
    # Update role
    result = user_company_roles_collection.update_one(
        {
            "user_id": user_id,
            "company_id": company_id,
            "is_active": True
        },
        {
            "$set": {
                "role": role_data.role.value,
                "updated_at": datetime.utcnow(),
                **permissions
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in company"
        )
    
    return {"message": "User role updated successfully"}


@router.put("/{user_id}/permissions")
async def update_user_permissions(
    company_id: str,
    user_id: str,
    permissions_data: UpdatePermissions,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Update user permissions (granular control)
    Only OWNER and ADMIN can update permissions
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required"
        )
    
    # Verify user is OWNER or ADMIN
    admin = user_company_roles_collection.find_one({
        "user_id": x_user_id,
        "company_id": company_id,
        "is_active": True
    })
    
    if not admin or admin.get("role") not in [UserRole.OWNER.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only OWNER and ADMIN can update permissions"
        )
    
    # Update permissions
    update_data = {k: v for k, v in permissions_data.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No permissions to update"
        )
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = user_company_roles_collection.update_one(
        {
            "user_id": user_id,
            "company_id": company_id,
            "is_active": True
        },
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in company"
        )
    
    return {"message": "User permissions updated successfully"}


@router.delete("/{user_id}")
async def remove_user_from_company(
    company_id: str,
    user_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Remove user from company (soft delete)
    Only users with can_manage_team permission
    Cannot remove self
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required"
        )
    
    # Verify permission
    verify_team_management_access(x_user_id, company_id)
    
    # Cannot remove self
    if user_id == x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove yourself from the company"
        )
    
    # Soft delete
    result = user_company_roles_collection.update_one(
        {
            "user_id": user_id,
            "company_id": company_id,
            "is_active": True
        },
        {
            "$set": {
                "is_active": False,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in company"
        )
    
    return {"message": "User removed from company successfully"}
