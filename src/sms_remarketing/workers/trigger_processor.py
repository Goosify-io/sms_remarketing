from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from ..database import SessionLocal
from ..models import Trigger, Lead, Template
from ..models.trigger import TriggerType
from ..services import sms_service

logger = logging.getLogger(__name__)


def process_new_lead_triggers(lead_id: int):
    """
    Process NEW_LEAD triggers for a newly created lead.
    This should be called right after a lead is created.
    """
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return

        # Find all active NEW_LEAD triggers for this client
        triggers = (
            db.query(Trigger)
            .filter(
                Trigger.client_id == lead.client_id,
                Trigger.trigger_type == TriggerType.NEW_LEAD,
                Trigger.is_active == True,
            )
            .all()
        )

        for trigger in triggers:
            template = (
                db.query(Template).filter(Template.id == trigger.template_id).first()
            )

            if template and template.is_active:
                # Prepare variables for template
                variables = {
                    "first_name": lead.first_name or "",
                    "last_name": lead.last_name or "",
                    "full_name": lead.full_name,
                    "phone_number": lead.phone_number,
                    "email": lead.email or "",
                }
                # Add custom fields
                if lead.custom_fields:
                    variables.update(lead.custom_fields)

                # Render content
                content = template.render(**variables)

                # Send SMS (synchronously, we're already in a background job)
                try:
                    message = sms_service.send_sms(
                        db=db,
                        client=lead.client,
                        lead=lead,
                        content=content,
                        template=template,
                        
                    )
                    logger.info(
                        f"NEW_LEAD trigger {trigger.id} sent message {message.id} to lead {lead.id}"
                    )
                except ValueError as e:
                    logger.error(
                        f"NEW_LEAD trigger {trigger.id} failed for lead {lead.id}: {e}",
                        exc_info=True,
                    )

    finally:
        db.close()


def process_lead_age_triggers():
    """
    Process LEAD_AGE triggers.
    This should be run periodically (e.g., daily via cron).
    Finds leads that match the age criteria and sends messages.
    """
    db = SessionLocal()
    try:
        # Get all active LEAD_AGE triggers
        triggers = (
            db.query(Trigger)
            .filter(
                Trigger.trigger_type == TriggerType.LEAD_AGE, Trigger.is_active == True
            )
            .all()
        )

        for trigger in triggers:
            # Get days from config
            days = trigger.config.get("days", 0)
            if days <= 0:
                continue

            # Calculate target date
            target_date = datetime.utcnow() - timedelta(days=days)
            date_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)

            # Find leads created on that specific day for this client
            leads = (
                db.query(Lead)
                .filter(
                    Lead.client_id == trigger.client_id,
                    Lead.created_at >= date_start,
                    Lead.created_at < date_end,
                )
                .all()
            )

            template = (
                db.query(Template).filter(Template.id == trigger.template_id).first()
            )

            if not template or not template.is_active:
                continue

            for lead in leads:
                # Prepare variables
                variables = {
                    "first_name": lead.first_name or "",
                    "last_name": lead.last_name or "",
                    "full_name": lead.full_name,
                    "phone_number": lead.phone_number,
                    "email": lead.email or "",
                    "days_since_signup": days,
                }
                if lead.custom_fields:
                    variables.update(lead.custom_fields)

                content = template.render(**variables)

                # Send SMS (synchronously, we're already in a background job)
                try:
                    message = sms_service.send_sms(
                        db=db,
                        client=lead.client,
                        lead=lead,
                        content=content,
                        template=template,
                        
                    )
                    logger.info(
                        f"LEAD_AGE trigger {trigger.id} sent message {message.id} to lead {lead.id} ({days} days old)"
                    )
                except ValueError as e:
                    logger.error(
                        f"LEAD_AGE trigger {trigger.id} failed for lead {lead.id}: {e}",
                        exc_info=True,
                    )

    finally:
        db.close()
