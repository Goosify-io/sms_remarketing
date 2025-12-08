from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any


class LeadBase(BaseModel):
    phone_number: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    custom_fields: Optional[Dict[str, Any]] = {}


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    custom_fields: Optional[Dict[str, Any]] = None


class LeadResponse(LeadBase):
    id: int
    client_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
