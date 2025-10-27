from sqlalchemy import Column, String, Text, DateTime, Boolean, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime

class ProjectFile(Base):
    __tablename__ = "project_files"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    
    # Информация о файле
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # в байтах
    mime_type = Column(String(100), nullable=True)
    
    # Дополнительная информация
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # brief, contract, report и т.д.
    
    # Временные метки
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    project = relationship("Project", back_populates="files")
