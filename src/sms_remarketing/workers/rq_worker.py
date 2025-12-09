"""
RQ Worker for processing background SMS jobs.
Run this with: python -m sms_remarketing.workers.rq_worker
"""
import logging
from redis import Redis
from rq import Worker
from ..config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Start the RQ worker"""
    logger.info("Starting RQ worker for SMS queue...")

    try:
        redis_conn = Redis.from_url(settings.redis_url)

        # Test connection
        redis_conn.ping()
        logger.info(f"Connected to Redis at {settings.redis_url}")

        # Create worker
        worker = Worker(
            ["sms"],  # Queue names to listen to
            connection=redis_conn,
        )

        logger.info("RQ worker ready. Listening for jobs on 'sms' queue...")
        logger.info("Press Ctrl+C to stop")

        # Start working
        worker.work(with_scheduler=True)

    except Exception as e:
        logger.error(f"Failed to start RQ worker: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
