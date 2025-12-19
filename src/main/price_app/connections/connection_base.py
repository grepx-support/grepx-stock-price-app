"""Base connection class."""

from typing import Optional, Any


class ConnectionBase:
    """Base class for all connections."""
    
    def __init__(self, config):
        """Initialize connection with config."""
        self.config = config
        self._client: Optional[Any] = None
    
    def connect(self) -> None:
        """Establish connection. Override in subclass."""
        raise NotImplementedError
    
    def disconnect(self) -> None:
        """Close connection. Override in subclass."""
        raise NotImplementedError
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._client is not None
    
    def get_client(self) -> Any:
        """Get client/connection object."""
        if not self.is_connected():
            self.connect()
        return self._client
