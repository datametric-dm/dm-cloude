from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from database.base import get_db, clients_collection
from routers.auth_mongo import get_current_user
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import os
import shutil

router = APIRouter(prefix="/files")

# Директория для хранения файлов
UPLOAD_DIR = "/app/backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class FileInfo(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    entity_type: str  # client, project, invoice
    entity_id: str
    uploaded_at: datetime
    uploaded_by: Optional[str] = None

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    entity_type: str = "client",
    entity_id: str = "",
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Загрузка файла"""
    
    # Генерируем уникальное имя файла
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    stored_filename = f"{file_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)
    
    # Сохраняем файл на диск
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {str(e)}")
    finally:
        file.file.close()
    
    # Получаем размер файла
    file_size = os.path.getsize(file_path)
    
    # Создаем запись о файле
    file_info = {
        "id": file_id,
        "filename": stored_filename,
        "original_filename": file.filename,
        "file_type": file.content_type or "application/octet-stream",
        "file_size": file_size,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "uploaded_at": datetime.utcnow(),
        "uploaded_by": current_user.get("email") if isinstance(current_user, dict) else None
    }
    
    # Если это файл клиента, добавляем ссылку в документ клиента
    if entity_type == "client" and entity_id:
        client = clients_collection.find_one({"id": entity_id})
        if client:
            contracts = client.get("contracts", [])
            contracts.append(file_info)
            clients_collection.update_one(
                {"id": entity_id},
                {"$set": {"contracts": contracts, "updated_at": datetime.utcnow()}}
            )
    
    return file_info

@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Скачивание файла"""
    
    # Ищем файл в клиентах
    client = clients_collection.find_one({"contracts.id": file_id})
    
    if not client:
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    # Находим информацию о файле
    file_info = None
    for contract in client.get("contracts", []):
        if contract.get("id") == file_id:
            file_info = contract
            break
    
    if not file_info:
        raise HTTPException(status_code=404, detail="Информация о файле не найдена")
    
    file_path = os.path.join(UPLOAD_DIR, file_info["filename"])
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден на диске")
    
    return FileResponse(
        path=file_path,
        filename=file_info["original_filename"],
        media_type=file_info["file_type"]
    )

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Удаление файла"""
    
    # Ищем файл в клиентах
    client = clients_collection.find_one({"contracts.id": file_id})
    
    if not client:
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    # Находим информацию о файле
    file_info = None
    for contract in client.get("contracts", []):
        if contract.get("id") == file_id:
            file_info = contract
            break
    
    if not file_info:
        raise HTTPException(status_code=404, detail="Информация о файле не найдена")
    
    # Удаляем файл с диска
    file_path = os.path.join(UPLOAD_DIR, file_info["filename"])
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Удаляем запись из базы данных
    updated_contracts = [c for c in client.get("contracts", []) if c.get("id") != file_id]
    clients_collection.update_one(
        {"id": client["id"]},
        {"$set": {"contracts": updated_contracts, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Файл удален"}

@router.get("/list/{entity_type}/{entity_id}")
async def list_files(
    entity_type: str,
    entity_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Список файлов для сущности"""
    
    if entity_type == "client":
        client = clients_collection.find_one({"id": entity_id})
        if client:
            return {"files": client.get("contracts", [])}
    
    return {"files": []}
