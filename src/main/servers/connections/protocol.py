"""Connection protocol definition."""

from typing import Protocol, Any, Optional


class Connection(Protocol):
    """Protocol for all connection types."""
    
    def connect(self) -> None:
        """Establish connection."""
        ...
    
    def disconnect(self) -> None:
        """Close connection."""
        ...
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        ...
    
    def get_client(self) -> Any:
        """Get the underlying client/connection object."""
        ...
    
    def health_check(self) -> bool:
        """Check connection health."""
        ...
