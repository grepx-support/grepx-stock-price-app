"""Dagster connection."""

from servers.connections import ConnectionBase


class DagsterConnection(ConnectionBase):
    """Dagster connection using dagster_framework."""
    
    def __init__(self, config, config_dir):
        super().__init__(config)
        self.config_dir = config_dir
    
    def connect(self) -> None:
        if self._client is None:
            from dagster_framework import create_app
            
            self._client = create_app(config_path=str(self.config_dir))
    
    def disconnect(self) -> None:
        self._client = None
    
    def get_definitions(self):
        return self.get_client()
