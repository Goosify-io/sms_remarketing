from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from ..models.message import MessageStatus


class SendSMSRequest(BaseModel):
    lead_id: int
    template_id: Optional[int] = None
    content: Optional[str] = None
    variables: Optional[Dict[str, Any]] = {}


class MessageResponse(BaseModel):
    id: int
    client_id: int
    lead_id: int
    template_id: Optional[int] = None
    to_number: str
    content: str
    status: MessageStatus
    twilio_sid: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True
