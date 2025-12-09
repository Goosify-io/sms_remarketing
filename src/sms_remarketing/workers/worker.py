"""
Background worker for processing scheduled tasks.
Run this with: python -m sms_remarketing.workers.worker
"""

import time
import logging
import schedule
from .trigger_processor import process_lead_age_triggers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_lead_age_triggers():
    """Run lead age trigger processor"""
    logger.info("Processing lead age triggers...")
    try:
        process_lead_age_triggers()
        logger.info("Lead age triggers processed successfully")
    except Exception as e:
        logger.error(f"Error processing lead age triggers: {e}", exc_info=True)


def main():
    """Main worker loop"""
    logger.info("Starting SMS Remarketing Worker...")
    logger.info("Scheduling tasks...")

    # Schedule lead age triggers to run daily at 9 AM
    schedule.every().day.at("09:00").do(run_lead_age_triggers)

    # Also run immediately on startup for testing
    run_lead_age_triggers()

    logger.info("Worker running. Press Ctrl+C to stop.")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    main()
