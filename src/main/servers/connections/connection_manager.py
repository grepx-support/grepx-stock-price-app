"""Connection manager."""

from .connection_registry import ConnectionRegistry
from servers.utils.logger import get_logger


class ConnectionManager:
    """Manages connections via registry."""
    
    def __init__(self, config, config_dir):
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing ConnectionManager")
        self.registry = ConnectionRegistry(config, config_dir)
        self.logger.info("ConnectionManager initialized successfully")
    
    def get(self, conn_id: str):
        self.logger.debug(f"Getting connection: {conn_id}")
        try:
            conn = self.registry.get(conn_id)
            self.logger.debug(f"Connection '{conn_id}' retrieved successfully")
            return conn
        except Exception as e:
            self.logger.error(f"Failed to get connection '{conn_id}': {e}", exc_info=True)
            raise
    
    def has(self, conn_id: str) -> bool:
        has_conn = self.registry.has(conn_id)
        self.logger.debug(f"Connection '{conn_id}' exists: {has_conn}")
        return has_conn
    
    def disconnect_all(self):
        self.logger.info("Disconnecting all connections...")
        try:
            self.registry.disconnect_all()
            self.logger.info("All connections disconnected successfully")
        except Exception as e:
            self.logger.error(f"Error disconnecting connections: {e}", exc_info=True)
            raise
