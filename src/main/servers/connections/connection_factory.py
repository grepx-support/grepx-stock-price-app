"""Connection factory."""

from typing import Dict, Type, Any
from .connection_base import ConnectionBase


class ConnectionFactory:
    """Factory for creating connections dynamically."""
    
    _registry: Dict[str, Type[ConnectionBase]] = {}
    
    @classmethod
    def register(cls, conn_type: str, connection_class: Type[ConnectionBase]):
        cls._registry[conn_type] = connection_class
    
    @classmethod
    def create(cls, conn_type: str, config: Any, config_dir: Any) -> ConnectionBase:
        if conn_type not in cls._registry:
            raise ValueError(f"Unknown connection type: {conn_type}")
        
        connection_class = cls._registry[conn_type]
        conn = connection_class(config, config_dir)
        conn.connect()
        return conn
    
    @classmethod
    def is_registered(cls, conn_type: str) -> bool:
        return conn_type in cls._registry
