"""
Background jobs for RQ workers.
These functions are executed by the RQ worker process.
"""
import logging
from datetime import datetime
from ..database import SessionLocal
from ..models import Message
from ..models.message import MessageStatus
from ..services.twilio_service import twilio_service

logger = logging.getLogger(__name__)


def send_sms_job(message_id: int):
    """
    Background job to send an SMS message via Twilio.

    Args:
        message_id: The ID of the message to send

    This job is executed by the RQ worker.
    """
    db = SessionLocal()
    try:
        # Get message
        message = db.query(Message).filter(Message.id == message_id).first()

        if not message:
            logger.error(f"Message {message_id} not found in database")
            return {"status": "error", "message": "Message not found"}

        if message.status != MessageStatus.QUEUED:
            logger.warning(
                f"Message {message_id} has status {message.status}, skipping send"
            )
            return {"status": "skipped", "message": f"Message status is {message.status}"}

        # Send via Twilio
        logger.info(f"Sending SMS {message_id} to {message.to_number}")
        success, twilio_sid, error_message = twilio_service.send_sms(
            to=message.to_number, body=message.content
        )

        # Update message status
        if success:
            message.status = MessageStatus.SENT
            message.twilio_sid = twilio_sid
            message.sent_at = datetime.utcnow()
            logger.info(f"SMS {message_id} sent successfully (SID: {twilio_sid})")
        else:
            message.status = MessageStatus.FAILED
            message.error_message = error_message
            logger.error(f"SMS {message_id} failed: {error_message}")

        db.commit()

        return {
            "status": "success" if success else "failed",
            "message_id": message_id,
            "twilio_sid": twilio_sid,
            "error": error_message,
        }

    except Exception as e:
        logger.error(f"Error sending SMS {message_id}: {e}", exc_info=True)

        # Try to update message status to failed
        try:
            message = db.query(Message).filter(Message.id == message_id).first()
            if message:
                message.status = MessageStatus.FAILED
                message.error_message = f"Job error: {str(e)}"
                db.commit()
        except:
            pass

        raise

    finally:
        db.close()
