from sqlalchemy import Column, String, Text, DateTime, Boolean, Float, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime
import enum

class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    number = Column(String(50), nullable=False, unique=True, index=True)
    
    # Связи
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    
    # Основные данные
    date_issued = Column(DateTime, default=datetime.utcnow)
    date_due = Column(DateTime, nullable=False)
    
    # Финансовые данные
    subtotal = Column(Float, nullable=False)
    tax_rate = Column(Float, default=20.0)  # НДС 20%
    tax_amount = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    
    # Статус
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # Дополнительная информация
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    client = relationship("Client", back_populates="invoices")
    project = relationship("Project", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")
    items = relationship("InvoiceItem", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False)
    
    description = Column(String(500), nullable=False)
    quantity = Column(Float, default=1.0)
    price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    
    # Связи
    invoice = relationship("Invoice", back_populates="items")
