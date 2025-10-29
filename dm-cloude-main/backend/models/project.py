from sqlalchemy import Column, String, Text, DateTime, Boolean, Float, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime
import enum

class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Связь с клиентом
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    
    # Статус и даты
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.PLANNING)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    
    # Финансовые данные
    budget = Column(Float, nullable=True)
    actual_cost = Column(Float, default=0.0)
    
    # Бриф проекта
    brief = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    deliverables = Column(Text, nullable=True)
    
    # Дополнительная информация
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    client = relationship("Client", back_populates="projects")
    services = relationship("ProjectService", back_populates="project")
    invoices = relationship("Invoice", back_populates="project")
    files = relationship("ProjectFile", back_populates="project")
