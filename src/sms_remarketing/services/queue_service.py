from redis import Redis
from rq import Queue
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class QueueService:
    """Service for managing background job queues"""

    def __init__(self):
        try:
            self.redis_conn = Redis.from_url(
                settings.redis_url,
                decode_responses=False,
            )
            self.queue = Queue("sms", connection=self.redis_conn)
            logger.info("Redis queue service initialized")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Jobs will run synchronously.")
            self.redis_conn = None
            self.queue = None

    def enqueue_sms(self, message_id: int) -> str:
        """
        Enqueue an SMS message for async sending.

        Args:
            message_id: The message ID to send

        Returns:
            Job ID if queued, or "sync" if running synchronously
        """
        if self.queue is None:
            logger.warning(f"Redis unavailable, sending message {message_id} synchronously")
            return "sync"

        from ..workers.jobs import send_sms_job

        job = self.queue.enqueue(
            send_sms_job,
            message_id,
            retry=3,
            job_timeout="5m",
        )
        logger.info(f"Enqueued SMS job {job.id} for message {message_id}")
        return job.id

    def is_available(self) -> bool:
        """Check if Redis queue is available"""
        return self.queue is not None


# Singleton instance
queue_service = QueueService()
