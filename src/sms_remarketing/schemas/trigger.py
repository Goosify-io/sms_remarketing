from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from ..models.trigger import TriggerType


class TriggerBase(BaseModel):
    name: str
    template_id: int
    trigger_type: TriggerType
    config: Dict[str, Any] = {}


class TriggerCreate(TriggerBase):
    pass


class TriggerUpdate(BaseModel):
    name: Optional[str] = None
    template_id: Optional[int] = None
    trigger_type: Optional[TriggerType] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class TriggerResponse(TriggerBase):
    id: int
    client_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
