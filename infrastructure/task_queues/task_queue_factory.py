"""Factory for creating task queue instances - Strategy pattern."""

from typing import Dict, Any
from application.ports.task_queue import ITaskQueue
from infrastructure.task_queues.celery_queue import CeleryTaskQueue
from infrastructure.task_queues.prefect_queue import PrefectTaskQueue
import logging

logger = logging.getLogger(__name__)


class TaskQueueFactory:
    """Factory for creating task queue instances."""

    @staticmethod
    def create(queue_type: str = "celery", config: Dict[str, Any] = None) -> ITaskQueue:
        """
        Create a task queue instance.
        
        Args:
            queue_type: Type of queue ("celery" or "prefect")
            config: Configuration dictionary
        
        Returns:
            ITaskQueue instance
        
        Raises:
            ValueError: If queue_type is not supported
        """
        if queue_type.lower() == "celery":
            if not config or "celery_app" not in config:
                raise ValueError("Celery queue requires 'celery_app' in config")
            return CeleryTaskQueue(config["celery_app"])
        
        elif queue_type.lower() == "prefect":
            prefect_client = config.get("prefect_client") if config else None
            return PrefectTaskQueue(prefect_client)
        
        else:
            raise ValueError(f"Unknown queue type: {queue_type}. Available: ['celery', 'prefect']")

