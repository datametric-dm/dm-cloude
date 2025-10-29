from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import uuid4
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"id": "dummy"}

from database.base import db
users_collection = db["users"]

try:
    import bcrypt
    def get_password_hash(p: str) -> str:
        return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
    def verify_password(plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(plain.encode(), hashed.encode())
        except Exception:
            return hashed == plain
except Exception:
    import hashlib
    def get_password_hash(p: str) -> str:
        return hashlib.sha256(p.encode()).hexdigest()
    def verify_password(plain: str, hashed: str) -> bool:
        return hashed in (plain, get_password_hash(plain))

router = APIRouter(tags=["auth"])

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

def _seed_admin():
    if not users_collection.find_one({"email": "adminDM@test.com"}):
        users_collection.insert_one({
            "id": str(uuid4()),
            "email": "adminDM@test.com",
            "hashed_password": get_password_hash("adminDM4321!"),
            "full_name": "Administrator",
            "is_active": True,
            "created_at": datetime.utcnow(),
        })

try:
    _seed_admin()
except Exception:
    pass

@router.post("/auth/register")
def register(user: UserCreate):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="USER exists")
    doc = {
        "id": str(uuid4()),
        "email": user.email,
        "hashed_password": get_password_hash(user.password),
        "full_name": user.full_name,
        "is_active": True,
        "created_at": datetime.utcnow(),
    }
    users_collection.insert_one(doc)
    return {
        "id": doc["id"],
        "email": doc["email"],
        "full_name": doc.get("full_name"),
        "is_active": True,
        "created_at": doc["created_at"],
    }

@router.post("/auth/login")
def login(creds: UserLogin):
    user = users_collection.find_one({"email": creds.email, "is_active": True})
    if not user or not verify_password(creds.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="fail email"
        )
    return {
        "access_token": "dummy-token",
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user.get("full_name"),
            "is_active": user.get("is_active", True),
            "created_at": user["created_at"],
        },
    }

@router.post("/login")
def login_alias(creds: UserLogin):
    return login(creds)
