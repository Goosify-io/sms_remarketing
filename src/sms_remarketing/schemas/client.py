from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class ClientBase(BaseModel):
    name: str
    email: EmailStr


class ClientCreate(ClientBase):
    initial_credits: int = 0


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class ClientResponse(ClientBase):
    id: int
    api_key: str
    credits: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
