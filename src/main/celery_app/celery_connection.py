"""Celery connection using celery_framework."""
from celery_framework import create_app
from servers.connections.connection_base import ConnectionBase
class CeleryConnection(ConnectionBase):
    """Celery connection using celery_framework."""
    def connect(self) -> None:
        """Initialize Celery app using celery_framework."""
        if self._client is None:
            celery_app_wrapper = create_app(self.config)
            self._client = celery_app_wrapper.app
    
    def disconnect(self) -> None:
        """Close Celery connection."""
        self._client = None
