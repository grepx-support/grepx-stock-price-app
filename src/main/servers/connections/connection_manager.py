"""Connection manager using registry pattern."""

from .connection_registry import ConnectionRegistry
from .database_connection import DatabaseConnection
from .celery_connection import CeleryConnection
from .dagster_connection import DagsterConnection


class ConnectionManager:
    """Manages all application connections using registry."""
    
    def __init__(self, config, config_dir):
        """Initialize connection manager."""
        self.config = config
        self.config_dir = config_dir
        self.registry = ConnectionRegistry()
    
    def get_database(self) -> DatabaseConnection:
        """Get or create database connection."""
        if not self.registry.has('database'):
            db = DatabaseConnection(self.config)
            db.connect()
            self.registry.register('database', db)
        return self.registry.get('database')
    
    def get_celery(self) -> CeleryConnection:
        """Get or create Celery connection."""
        if not self.registry.has('celery'):
            celery = CeleryConnection(self.config)
            celery.connect()
            self.registry.register('celery', celery)
        return self.registry.get('celery')
    
    def get_dagster(self) -> DagsterConnection:
        """Get or create Dagster connection."""
        if not self.registry.has('dagster'):
            dagster = DagsterConnection(self.config, self.config_dir)
            dagster.connect()
            self.registry.register('dagster', dagster)
        return self.registry.get('dagster')
    
    def disconnect_all(self) -> None:
        """Disconnect all connections."""
        if self.registry.has('database'):
            self.registry.get('database').disconnect()
        if self.registry.has('celery'):
            self.registry.get('celery').disconnect()
        if self.registry.has('dagster'):
            self.registry.get('dagster').disconnect()
        self.registry.clear()
