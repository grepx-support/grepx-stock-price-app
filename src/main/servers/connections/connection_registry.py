"""Connection registry."""

from typing import Dict, Any, Optional
from .connection_factory import ConnectionFactory


class ConnectionRegistry:
    """Registry for managing connection instances."""
    
    def __init__(self, config, config_dir):
        self.config = config
        self.config_dir = config_dir
        self._connections: Dict[str, Any] = {}
    
    def get(self, conn_id: str) -> Optional[Any]:
        if conn_id in self._connections:
            return self._connections[conn_id]
        
        if not hasattr(self.config, 'connections'):
            raise ValueError("No connections configured")
        
        for conn_config in self.config.connections:
            if conn_config.id == conn_id and conn_config.get('enabled', True):
                conn = ConnectionFactory.create(conn_config.type, self.config, self.config_dir)
                self._connections[conn_id] = conn
                return conn
        
        raise ValueError(f"Connection '{conn_id}' not found or disabled")
    
    def has(self, conn_id: str) -> bool:
        if conn_id in self._connections:
            return True
        
        if hasattr(self.config, 'connections'):
            for conn in self.config.connections:
                if conn.id == conn_id and conn.get('enabled', True):
                    return True
        return False
    
    def disconnect_all(self) -> None:
        for conn in self._connections.values():
            if hasattr(conn, 'disconnect'):
                conn.disconnect()
        self._connections.clear()
