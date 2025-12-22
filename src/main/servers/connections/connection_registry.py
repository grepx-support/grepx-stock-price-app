"""Connection registry."""

from typing import Dict, Any, Optional
from .connection_factory import ConnectionFactory
from servers.utils.logger import get_logger


class ConnectionRegistry:
    """Registry for managing connection instances."""
    
    def __init__(self, config, config_dir):
        self.config = config
        self.config_dir = config_dir
        self._connections: Dict[str, Any] = {}
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing ConnectionRegistry")
    
    def get(self, conn_id: str) -> Optional[Any]:
        # Check if connection already exists
        if conn_id in self._connections:
            self.logger.debug(f"Returning cached connection: {conn_id}")
            return self._connections[conn_id]
        
        self.logger.info(f"Creating new connection: {conn_id}")
        
        if not hasattr(self.config, 'connections'):
            self.logger.error("No connections configured in config")
            raise ValueError("No connections configured")
        
        # Find connection config
        for conn_config in self.config.connections:
            if conn_config.id == conn_id and conn_config.get('enabled', True):
                self.logger.debug(f"Found connection config: {conn_id}, type: {conn_config.type}")
                try:
                    conn = ConnectionFactory.create(conn_config.type, self.config, self.config_dir)
                    self._connections[conn_id] = conn
                    self.logger.info(f"Connection '{conn_id}' created and cached successfully")
                    return conn
                except Exception as e:
                    self.logger.error(f"Failed to create connection '{conn_id}': {e}", exc_info=True)
                    raise
        
        self.logger.warning(f"Connection '{conn_id}' not found or disabled")
        raise ValueError(f"Connection '{conn_id}' not found or disabled")
    
    def has(self, conn_id: str) -> bool:
        if conn_id in self._connections:
            self.logger.debug(f"Connection '{conn_id}' exists in cache")
            return True
        
        if hasattr(self.config, 'connections'):
            for conn in self.config.connections:
                if conn.id == conn_id and conn.get('enabled', True):
                    self.logger.debug(f"Connection '{conn_id}' found in config (not yet created)")
                    return True
        
        self.logger.debug(f"Connection '{conn_id}' does not exist")
        return False
    
    def disconnect_all(self) -> None:
        self.logger.info(f"Disconnecting {len(self._connections)} connections...")
        disconnected = 0
        for conn_id, conn in self._connections.items():
            try:
                if hasattr(conn, 'disconnect'):
                    self.logger.debug(f"Disconnecting: {conn_id}")
                    conn.disconnect()
                    disconnected += 1
                else:
                    self.logger.warning(f"Connection '{conn_id}' has no disconnect method")
            except Exception as e:
                self.logger.error(f"Error disconnecting '{conn_id}': {e}", exc_info=True)
        
        self._connections.clear()
        self.logger.info(f"Disconnected {disconnected} connections")
