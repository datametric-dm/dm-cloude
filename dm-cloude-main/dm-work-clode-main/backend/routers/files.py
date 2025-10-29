from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database.base import get_db
from models.file import ProjectFile
from models.project import Project
from schemas.file import ProjectFileRead, ProjectFileList
from typing import Optional, List
import os
import uuid
import aiofiles
from pathlib import Path

router = APIRouter(prefix="/files")

# Каталог для хранения файлов
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

@router.post("/upload/{project_id}", response_model=ProjectFileRead)
async def upload_file(
    project_id: str,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Загрузка файла к проекту"""
    # Проверяем существование проекта
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Генерируем уникальное имя файла
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOADS_DIR / project_id / unique_filename
    
    # Создаём каталог проекта
    file_path.parent.mkdir(exist_ok=True)
    
    # Сохраняем файл
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Создаём запись в базе данных
    project_file = ProjectFile(
        project_id=project_id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        mime_type=file.content_type,
        description=description,
        category=category
    )
    
    db.add(project_file)
    db.commit()
    db.refresh(project_file)
    
    return project_file

@router.get("/project/{project_id}", response_model=ProjectFileList)
def get_project_files(
    project_id: str,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получение всех файлов проекта"""
    query = db.query(ProjectFile).filter(ProjectFile.project_id == project_id)
    
    if category:
        query = query.filter(ProjectFile.category == category)
    
    files = query.order_by(ProjectFile.uploaded_at.desc()).all()
    
    return ProjectFileList(files=files, total=len(files))

@router.get("/{file_id}", response_model=ProjectFileRead)
def get_file_info(file_id: str, db: Session = Depends(get_db)):
    """Получение информации о файле"""
    file_info = db.query(ProjectFile).filter(ProjectFile.id == file_id).first()
    if not file_info:
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    return file_info

@router.delete("/{file_id}")
def delete_file(file_id: str, db: Session = Depends(get_db)):
    """Удаление файла"""
    file_info = db.query(ProjectFile).filter(ProjectFile.id == file_id).first()
    if not file_info:
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    # Удаляем файл с диска
    try:
        os.remove(file_info.file_path)
    except FileNotFoundError:
        pass  # Файл уже удалён
    
    # Удаляем запись из базы
    db.delete(file_info)
    db.commit()
    
    return {"message": "Файл успешно удалён"}

@router.get("/categories/{project_id}")
def get_file_categories(project_id: str, db: Session = Depends(get_db)):
    """Получение всех категорий файлов проекта"""
    categories = db.query(ProjectFile.category).filter(
        ProjectFile.project_id == project_id,
        ProjectFile.category.isnot(None)
    ).distinct().all()
    
    return {"categories": [cat[0] for cat in categories if cat[0]]}
