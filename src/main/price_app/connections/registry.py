"""Connection registry for managing multiple connections."""

from typing import Dict, Optional, Any


class ConnectionRegistry:
    """Registry to store and manage connections."""
    
    def __init__(self):
        self._connections: Dict[str, Any] = {}
    
    def register(self, name: str, connection: Any) -> None:
        """Register a connection."""
        if name in self._connections:
            raise ValueError(f"Connection '{name}' already registered")
        self._connections[name] = connection
    
    def get(self, name: str) -> Optional[Any]:
        """Get a connection by name."""
        return self._connections.get(name)
    
    def unregister(self, name: str) -> None:
        """Unregister a connection."""
        if name in self._connections:
            del self._connections[name]
    
    def get_all(self) -> Dict[str, Any]:
        """Get all registered connections."""
        return self._connections.copy()
    
    def clear(self) -> None:
        """Clear all connections."""
        self._connections.clear()
    
    def list_names(self) -> list[str]:
        """List all registered connection names."""
        return list(self._connections.keys())
