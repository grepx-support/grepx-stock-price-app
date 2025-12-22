"""Celery entry point.

Usage: celery -A celery_main:app worker
"""
# Import apps to register connection types
import database_app
import celery_app

from main import get_connection
from servers.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Initializing Celery application...")
try:
    app = get_connection("primary_celery").get_client()
    logger.info("Celery application initialized successfully")
    logger.debug(f"Celery app name: {app.main}")
except Exception as e:
    logger.error(f"Failed to initialize Celery application: {e}", exc_info=True)
    raise
