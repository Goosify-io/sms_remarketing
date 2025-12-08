from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class MessageStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)

    to_number = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(
        Enum(MessageStatus), default=MessageStatus.PENDING, nullable=False, index=True
    )

    # Twilio specific
    twilio_sid = Column(String, unique=True, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    client = relationship("Client", back_populates="messages")
    lead = relationship("Lead", back_populates="messages")
