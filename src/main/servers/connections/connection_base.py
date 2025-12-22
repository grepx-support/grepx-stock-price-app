"""Base connection class."""

from typing import Optional, Any
from servers.utils.logger import get_logger


class ConnectionBase:
    """Base class for all connections."""
    
    def __init__(self, config):
        """Initialize connection with config."""
        self.config = config
        self._client: Optional[Any] = None
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug(f"Initializing {self.__class__.__name__} connection")
    
    def connect(self) -> None:
        """Establish connection. Override in subclass."""
        self.logger.warning("connect() method not implemented in subclass")
        raise NotImplementedError
    
    def disconnect(self) -> None:
        """Close connection. Override in subclass."""
        if self._client is not None:
            self.logger.debug("Disconnecting...")
        self.logger.warning("disconnect() method not implemented in subclass")
        raise NotImplementedError
    
    def is_connected(self) -> bool:
        """Check if connected."""
        connected = self._client is not None
        self.logger.debug(f"Connection status: {connected}")
        return connected
    
    def get_client(self) -> Any:
        """Get client/connection object."""
        if not self.is_connected():
            self.logger.info("Client not connected, establishing connection...")
            self.connect()
            self.logger.info("Connection established successfully")
        else:
            self.logger.debug("Using existing connection")
        return self._client
