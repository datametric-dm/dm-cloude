from sqlalchemy import Column, String, Text, DateTime, Boolean, Float, Integer
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    
    # Реквизиты
    inn = Column(String(20), nullable=True)
    kpp = Column(String(20), nullable=True)
    ogrn = Column(String(20), nullable=True)
    bank_name = Column(String(255), nullable=True)
    bank_account = Column(String(50), nullable=True)
    bank_bik = Column(String(20), nullable=True)
    
    # Контактные лица
    contact_person = Column(String(255), nullable=True)
    contact_position = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(255), nullable=True)
    
    # Дополнительная информация
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    projects = relationship("Project", back_populates="client")
    invoices = relationship("Invoice", back_populates="client")
    payments = relationship("Payment", back_populates="client")
