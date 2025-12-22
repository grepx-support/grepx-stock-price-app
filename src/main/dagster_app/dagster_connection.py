"""DagsterConnection - Dagster resource wrapper.

File name matches class name (dagster_connection.py).
"""

from grepx_connection_registry import ConnectionBase


class DagsterConnection(ConnectionBase):
    """Dagster connection - lightweight wrapper for consistency.
    
    Note: Dagster doesn't need a traditional connection.
    This exists for consistent interface in connection registry.
    """
    
    def __init__(self, config, config_dir):
        super().__init__(config)
        self.config_dir = config_dir
    
    def connect(self) -> None:
        """Connect (no-op for Dagster)."""
        if self._client is None:
            self._client = {"config": self.config, "config_dir": self.config_dir}
    
    def disconnect(self) -> None:
        """Disconnect."""
        self._client = None
