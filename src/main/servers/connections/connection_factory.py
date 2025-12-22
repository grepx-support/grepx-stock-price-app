"""Connection factory."""

from typing import Dict, Type, Any
from .connection_base import ConnectionBase
from servers.utils.logger import get_logger


class ConnectionFactory:
    """Factory for creating connections dynamically."""
    
    _registry: Dict[str, Type[ConnectionBase]] = {}
    logger = get_logger(__name__)
    
    @classmethod
    def register(cls, conn_type: str, connection_class: Type[ConnectionBase]):
        """Register a connection type with the factory."""
        cls.logger.info(f"Registering connection type: {conn_type} -> {connection_class.__name__}")
        cls._registry[conn_type] = connection_class
        cls.logger.debug(f"Connection type '{conn_type}' registered successfully")
    
    @classmethod
    def create(cls, conn_type: str, config: Any, config_dir: Any) -> ConnectionBase:
        """Create a connection instance."""
        cls.logger.debug(f"Creating connection of type: {conn_type}")
        
        if conn_type not in cls._registry:
            cls.logger.error(f"Unknown connection type: {conn_type}. Registered types: {list(cls._registry.keys())}")
            raise ValueError(f"Unknown connection type: {conn_type}")
        
        try:
            connection_class = cls._registry[conn_type]
            cls.logger.debug(f"Using connection class: {connection_class.__name__}")
            
            conn = connection_class(config, config_dir)
            cls.logger.debug(f"Connection instance created, establishing connection...")
            
            conn.connect()
            cls.logger.info(f"Connection '{conn_type}' created and connected successfully")
            
            return conn
        except Exception as e:
            cls.logger.error(f"Failed to create connection '{conn_type}': {e}", exc_info=True)
            raise
    
    @classmethod
    def is_registered(cls, conn_type: str) -> bool:
        """Check if a connection type is registered."""
        is_reg = conn_type in cls._registry
        cls.logger.debug(f"Connection type '{conn_type}' registered: {is_reg}")
        return is_reg
