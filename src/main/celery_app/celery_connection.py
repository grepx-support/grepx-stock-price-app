"""Celery connection."""

from servers.connections import ConnectionBase


class CeleryConnection(ConnectionBase):
    """Celery connection using celery_framework."""
    
    def __init__(self, config, config_dir):
        super().__init__(config)
        self.config_dir = config_dir
    
    def connect(self) -> None:
        if self._client is None:
            from celery_framework import create_app
            
            celery_app_wrapper = create_app(self.config)
            self._client = celery_app_wrapper.app
    
    def disconnect(self) -> None:
        self._client = None
