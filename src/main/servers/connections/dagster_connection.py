"""Dagster connection using dagster_framework."""

from .connection_base import ConnectionBase


class DagsterConnection(ConnectionBase):
    """Dagster connection using dagster_framework."""
    
    def __init__(self, config, config_dir):
        super().__init__(config)
        self.config_dir = config_dir
    
    def connect(self) -> None:
        """Initialize Dagster using dagster_framework."""
        if self._client is None:
            from dagster_framework.main import create_app
            
            self._client = create_app(config_path=str(self.config_dir))
    
    def disconnect(self) -> None:
        """Close Dagster connection."""
        self._client = None
    
    def get_definitions(self):
        """Get Dagster definitions."""
        return self.get_client()
