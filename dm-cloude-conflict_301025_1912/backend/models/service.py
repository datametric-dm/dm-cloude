from sqlalchemy import Column, String, Text, DateTime, Boolean, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime

class Service(Base):
    __tablename__ = "services"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)  # час, проект, месяц и т.д.
    
    # Дополнительная информация
    category = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    project_services = relationship("ProjectService", back_populates="service")

class ProjectService(Base):
    __tablename__ = "project_services"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    service_id = Column(String, ForeignKey("services.id"), nullable=False)
    
    quantity = Column(Float, default=1.0)
    price = Column(Float, nullable=False)  # Цена на момент добавления к проекту
    total = Column(Float, nullable=False)
    
    notes = Column(Text, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    project = relationship("Project", back_populates="services")
    service = relationship("Service", back_populates="project_services")
