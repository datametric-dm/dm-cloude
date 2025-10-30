from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError
from database.base import db  # expects database/base.py to expose `db`

router = APIRouter(tags=["health"])

@router.get("/healthz")
def healthz():
    try:
        db.command("ping")
        return {"status": "OK"}
    except PyMongoError as e:
        raise HTTPException(status_code=503, detail=f"Mongo not healthy: {e}")
