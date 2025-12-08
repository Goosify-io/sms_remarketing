from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import re
from ..database import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="templates")

    def render(self, **variables) -> str:
        """
        Render template with variables.
        Variables in template should be in format: {{variable_name}}
        """
        content = self.content
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        return content

    def get_variables(self) -> list[str]:
        """Extract variable names from template"""
        pattern = r"\{\{(\w+)\}\}"
        return re.findall(pattern, self.content)
