"""Celery implementation of task queue."""

from typing import Any, Dict, Optional
import logging
from application.ports.task_queue import ITaskQueue

logger = logging.getLogger(__name__)


class CeleryTaskQueue(ITaskQueue):
    """Celery implementation of task queue."""

    def __init__(self, celery_app):
        """
        Initialize with Celery app instance.
        
        Args:
            celery_app: Celery application instance
        """
        self.celery_app = celery_app

    def send_task(self, task_name: str, args: tuple = (), kwargs: Dict[str, Any] = None) -> str:
        """Send a task to the queue. Returns task ID."""
        if kwargs is None:
            kwargs = {}
        
        try:
            result = self.celery_app.send_task(task_name, args=args, kwargs=kwargs)
            return result.id
        except Exception as e:
            logger.error(f"Error sending task {task_name}: {e}")
            raise

    def get_task_result(self, task_id: str, timeout: Optional[int] = None) -> Any:
        """Get result of a task by ID."""
        try:
            async_result = self.celery_app.AsyncResult(task_id)
            if timeout:
                return async_result.get(timeout=timeout)
            else:
                return async_result.get()
        except Exception as e:
            logger.error(f"Error getting task result for {task_id}: {e}")
            raise

    def get_task_status(self, task_id: str) -> str:
        """Get status of a task."""
        try:
            async_result = self.celery_app.AsyncResult(task_id)
            return async_result.status
        except Exception as e:
            logger.error(f"Error getting task status for {task_id}: {e}")
            return "UNKNOWN"

