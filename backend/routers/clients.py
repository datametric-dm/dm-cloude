from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database.base import get_db
from models.client import Client
from schemas.client import ClientCreate, ClientUpdate, ClientRead, ClientList
from typing import Optional

router = APIRouter(prefix="/clients")

@router.post("/", response_model=ClientRead)
def create_client(client_data: ClientCreate, db: Session = Depends(get_db)):
    """Создание нового клиента"""
    client = Client(**client_data.dict())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

@router.get("/", response_model=ClientList)
def get_clients(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=1000, description="Количество записей на странице"),
    search: Optional[str] = Query(None, description="Поиск по имени, компании или email"),
    active_only: bool = Query(True, description="Показывать только активных клиентов"),
    db: Session = Depends(get_db)
):
    """Получение списка клиентов с поиском и пагинацией"""
    query = db.query(Client)
    
    if active_only:
        query = query.filter(Client.is_active == True)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Client.name.ilike(search_term),
                Client.company.ilike(search_term),
                Client.email.ilike(search_term)
            )
        )
    
    total = query.count()
    clients = query.order_by(Client.created_at.desc()).offset(skip).limit(limit).all()
    
    return ClientList(
        clients=clients,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/{client_id}", response_model=ClientRead)
def get_client(client_id: str, db: Session = Depends(get_db)):
    """Получение клиента по ID"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return client

@router.put("/{client_id}", response_model=ClientRead)
def update_client(client_id: str, client_data: ClientUpdate, db: Session = Depends(get_db)):
    """Обновление данных клиента"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    update_data = client_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    return client

@router.delete("/{client_id}")
def delete_client(client_id: str, db: Session = Depends(get_db)):
    """Мягкое удаление клиента (отмечаем как неактивный)"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    client.is_active = False
    db.commit()
    
    return {"message": "Клиент успешно деактивирован"}
