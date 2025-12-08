from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from ..config import settings
from typing import Optional, Tuple


class TwilioService:
    """Service for sending SMS messages via Twilio"""

    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.from_number = settings.twilio_phone_number

    def send_sms(self, to: str, body: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Send an SMS message via Twilio.

        Args:
            to: Recipient phone number (E.164 format recommended)
            body: Message content

        Returns:
            Tuple of (success: bool, twilio_sid: str, error_message: str)
        """
        try:
            message = self.client.messages.create(
                body=body, from_=self.from_number, to=to
            )
            return True, message.sid, None
        except TwilioRestException as e:
            error_msg = f"Twilio error: {e.msg}"
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            return False, None, error_msg


# Singleton instance
twilio_service = TwilioService()
