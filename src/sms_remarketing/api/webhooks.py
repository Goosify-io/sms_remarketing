from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from ..database import get_db
from ..models import Trigger, Lead, Template, Message
from ..models.trigger import TriggerType
from ..models.message import MessageStatus
from ..services import sms_service
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


class WebhookTriggerRequest(BaseModel):
    lead_id: int
    variables: Optional[Dict[str, Any]] = {}


@router.post("/trigger/{webhook_key}", status_code=status.HTTP_202_ACCEPTED)
def trigger_webhook(
    webhook_key: str,
    request: WebhookTriggerRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Trigger SMS via webhook.
    Finds active trigger with matching webhook_key and sends SMS to specified lead.
    """
    # Find trigger with matching webhook_key
    trigger = (
        db.query(Trigger)
        .filter(
            Trigger.trigger_type == TriggerType.WEBHOOK,
            Trigger.is_active == True,
        )
        .all()
    )

    # Filter by webhook_key in config
    matching_trigger = None
    for t in trigger:
        if t.config.get("webhook_key") == webhook_key:
            matching_trigger = t
            break

    if not matching_trigger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook trigger not found or inactive",
        )

    # Get lead
    lead = (
        db.query(Lead)
        .filter(
            Lead.id == request.lead_id,
            Lead.client_id == matching_trigger.client_id,
        )
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found or doesn't belong to this client",
        )

    # Get template
    template = (
        db.query(Template)
        .filter(Template.id == matching_trigger.template_id)
        .first()
    )

    if not template or not template.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or inactive",
        )

    # Prepare variables
    variables = {
        "first_name": lead.first_name or "",
        "last_name": lead.last_name or "",
        "full_name": lead.full_name,
        "phone_number": lead.phone_number,
        "email": lead.email or "",
    }
    if lead.custom_fields:
        variables.update(lead.custom_fields)
    if request.variables:
        variables.update(request.variables)

    # Render content
    content = template.render(**variables)

    # Send SMS
    try:
        message = sms_service.send_sms(
            db=db,
            client=lead.client,
            lead=lead,
            content=content,
            template=template,
        )
        logger.info(
            f"Webhook trigger {matching_trigger.id} sent SMS {message.id} to lead {lead.id}"
        )
        return {
            "status": "accepted",
            "message_id": message.id,
            "message_status": message.status,
        }
    except ValueError as e:
        logger.error(
            f"Webhook trigger {matching_trigger.id} failed for lead {lead.id}: {e}",
            exc_info=True,
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/twilio/status")
def twilio_status_webhook(
    MessageSid: str,
    MessageStatus: str,
    ErrorCode: Optional[str] = None,
    ErrorMessage: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Receive delivery status updates from Twilio.
    Configure this URL in your Twilio console as the Status Callback URL.
    """
    # Find message by Twilio SID
    message = (
        db.query(Message).filter(Message.twilio_sid == MessageSid).first()
    )

    if not message:
        logger.warning(f"Received status update for unknown message SID: {MessageSid}")
        return {"status": "ignored"}

    # Update message status
    old_status = message.status

    # Map Twilio status to our enum
    status_map = {
        "queued": MessageStatus.QUEUED,
        "sending": MessageStatus.SENT,
        "sent": MessageStatus.SENT,
        "delivered": MessageStatus.DELIVERED,
        "undelivered": MessageStatus.FAILED,
        "failed": MessageStatus.FAILED,
    }

    new_status = status_map.get(MessageStatus.lower(), message.status)
    message.status = new_status

    # Update timestamps
    if new_status == MessageStatus.DELIVERED and not message.delivered_at:
        message.delivered_at = datetime.utcnow()

    # Update error info if failed
    if new_status == MessageStatus.FAILED:
        if ErrorCode:
            message.error_message = f"Twilio Error {ErrorCode}: {ErrorMessage or 'Unknown error'}"
        elif not message.error_message:
            message.error_message = "Delivery failed"

    db.commit()

    logger.info(
        f"Updated message {message.id} status from {old_status} to {new_status} (Twilio: {MessageStatus})"
    )

    return {"status": "updated", "message_id": message.id}
