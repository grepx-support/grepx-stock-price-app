"""Connection protocol."""

from typing import Protocol, Any


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
        """Get the underlying client."""
        ...
