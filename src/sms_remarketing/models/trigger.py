from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Enum,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class TriggerType(str, enum.Enum):
    NEW_LEAD = "new_lead"  # Trigger when new lead is created
    LEAD_AGE = "lead_age"  # Trigger after X days from lead creation
    WEBHOOK = "webhook"  # Trigger via webhook call


class Trigger(Base):
    __tablename__ = "triggers"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)

    name = Column(String, nullable=False)
    trigger_type = Column(Enum(TriggerType), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Configuration for different trigger types
    config = Column(JSON, default={})
    # For LEAD_AGE: {"days": 7}
    # For WEBHOOK: {"webhook_key": "unique_key"}
    # For NEW_LEAD: {} (no config needed)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="triggers")
    template = relationship("Template")
