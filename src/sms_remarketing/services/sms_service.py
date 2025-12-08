from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import logging
from ..models import Client, Lead, Template, Message
from ..models.message import MessageStatus
from .twilio_service import twilio_service

logger = logging.getLogger(__name__)


class SMSService:
    """Service for managing SMS sending with credit management"""

    @staticmethod
    def send_sms(
        db: Session,
        client: Client,
        lead: Lead,
        content: str,
        template: Optional[Template] = None,
        async_send: bool = True,
    ) -> Message:
        """
        Send an SMS message to a lead.
        Handles credit deduction, message creation, and SMS sending (async or sync).

        Args:
            db: Database session
            client: The client sending the message
            lead: The lead to send to
            content: The message content
            template: Optional template used
            async_send: If True, queue for async sending (default). If False, send immediately.

        Returns:
            Message object

        Raises:
            ValueError: If client has insufficient credits
        """
        # Check credits
        if not client.has_credits(1):
            raise ValueError("Insufficient credits")

        # Create message record
        message = Message(
            client_id=client.id,
            lead_id=lead.id,
            template_id=template.id if template else None,
            to_number=lead.phone_number,
            content=content,
            status=MessageStatus.PENDING,
        )
        db.add(message)
        db.flush()

        # Deduct credit
        client.deduct_credits(1)

        # Queue for async sending or send immediately

        # Send synchronously (either requested or Redis unavailable)
        success, twilio_sid, error_message = twilio_service.send_sms(
            to=lead.phone_number, body=content
        )

        # Update message status
        if success:
            message.status = MessageStatus.SENT
            message.twilio_sid = twilio_sid
            message.sent_at = datetime.utcnow()
            logger.info(f"Message {message.id} sent synchronously (SID: {twilio_sid})")
        else:
            message.status = MessageStatus.FAILED
            message.error_message = error_message
            logger.error(f"Message {message.id} failed: {error_message}")

        db.commit()
        db.refresh(message)

        return message


sms_service = SMSService()
