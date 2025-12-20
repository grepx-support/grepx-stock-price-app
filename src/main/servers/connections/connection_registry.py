"""Connection registry."""

from typing import Dict, Any


class ConnectionRegistry:
    """Registry to store connections by name."""
    
    def __init__(self):
        self._connections: Dict[str, Any] = {}
    
    def register(self, name: str, connection: Any) -> None:
        """Register a connection."""
        self._connections[name] = connection
    
    def get(self, name: str) -> Any:
        """Get a connection by name."""
        return self._connections.get(name)
    
    def has(self, name: str) -> bool:
        """Check if connection exists."""
        return name in self._connections
    
    def clear(self) -> None:
        """Clear all connections."""
        self._connections.clear()
