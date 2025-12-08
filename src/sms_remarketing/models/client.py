from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import secrets
from ..database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    api_key = Column(String, unique=True, nullable=False, index=True)
    credits = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    leads = relationship("Lead", back_populates="client", cascade="all, delete-orphan")
    templates = relationship(
        "Template", back_populates="client", cascade="all, delete-orphan"
    )
    messages = relationship(
        "Message", back_populates="client", cascade="all, delete-orphan"
    )
    triggers = relationship(
        "Trigger", back_populates="client", cascade="all, delete-orphan"
    )

    @staticmethod
    def generate_api_key():
        """Generate a secure API key"""
        return f"sk_{secrets.token_urlsafe(32)}"

    def has_credits(self, count: int = 1) -> bool:
        """Check if client has enough credits"""
        return self.credits >= count

    def deduct_credits(self, count: int = 1) -> bool:
        """Deduct credits from client account. Returns True if successful."""
        if self.has_credits(count):
            self.credits -= count
            return True
        return False
