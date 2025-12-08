from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TemplateBase(BaseModel):
    name: str
    content: str


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None


class TemplateResponse(TemplateBase):
    id: int
    client_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
