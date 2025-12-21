"""Connection manager."""

from .connection_registry import ConnectionRegistry


class ConnectionManager:
    """Manages connections via registry."""
    
    def __init__(self, config, config_dir):
        self.registry = ConnectionRegistry(config, config_dir)
    
    def get(self, conn_id: str):
        return self.registry.get(conn_id)
    
    def has(self, conn_id: str) -> bool:
        return self.registry.has(conn_id)
    
    def disconnect_all(self):
        self.registry.disconnect_all()
