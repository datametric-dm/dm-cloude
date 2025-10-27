from sqlalchemy import Column, String, Text, DateTime, Boolean, Float, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime
import enum

class PaymentStatus(str, enum.Enum):
    PLANNED = "planned"
    RECEIVED = "received"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class PaymentType(str, enum.Enum):
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CARD = "card"
    OTHER = "other"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Связи
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=True)
    
    # Основные данные
    amount = Column(Float, nullable=False)
    payment_date_planned = Column(DateTime, nullable=False)
    payment_date_actual = Column(DateTime, nullable=True)
    
    # Статус и тип
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PLANNED)
    payment_type = Column(SQLEnum(PaymentType), nullable=True)
    
    # Дополнительная информация
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True)  # Номер транзакции
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    client = relationship("Client", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")
