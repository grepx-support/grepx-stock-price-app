"""Task queue interfaces - abstractions for task execution."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ITaskQueue(ABC):
    """Interface for task queue operations."""

    @abstractmethod
    def send_task(self, task_name: str, args: tuple = (), kwargs: Dict[str, Any] = None) -> str:
        """Send a task to the queue. Returns task ID."""
        pass

    @abstractmethod
    def get_task_result(self, task_id: str, timeout: Optional[int] = None) -> Any:
        """Get result of a task by ID."""
        pass

    @abstractmethod
    def get_task_status(self, task_id: str) -> str:
        """Get status of a task (PENDING, SUCCESS, FAILURE, etc.)."""
        pass

