from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    phone_number = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    custom_fields = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="leads")
    messages = relationship(
        "Message", back_populates="lead", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        """Get full name of lead"""
        parts = [self.first_name, self.last_name]
        return " ".join(filter(None, parts)) or "Unknown"
