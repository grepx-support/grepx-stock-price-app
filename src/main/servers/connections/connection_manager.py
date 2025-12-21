"""Connection manager using registry pattern."""

from .connection_registry import ConnectionRegistry
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database_app.database_connection import DatabaseConnection
    from celery_app.celery_connection import CeleryConnection
    from dagster_app.dagster_connection import DagsterConnection
    from prefect_app.prefect_app import load_prefect_flows


class ConnectionManager:
    """Manages all application connections using registry."""
    
    def __init__(self, config, config_dir):
        """Initialize connection manager."""
        self.config = config
        self.config_dir = config_dir
        self.registry = ConnectionRegistry()
    
    def get_database(self):
        """Get or create database connection."""
        # Lazy import to avoid circular dependency
        from database_app.database_connection import DatabaseConnection
        
        if not self.registry.has('database'):
            db = DatabaseConnection(self.config)
            db.connect()
            self.registry.register('database', db)
        return self.registry.get('database')
    
    def get_celery(self):
        """Get or create Celery connection."""
        # Lazy import to avoid circular dependency
        from celery_app.celery_connection import CeleryConnection
        
        if not self.registry.has('celery'):
            celery = CeleryConnection(self.config)
            celery.connect()
            self.registry.register('celery', celery)
        return self.registry.get('celery')
    
    def get_dagster(self):
        """Get or create Dagster connection."""
        # Lazy import to avoid circular dependency
        from dagster_app.dagster_connection import DagsterConnection
        
        if not self.registry.has('dagster'):
            dagster = DagsterConnection(self.config, self.config_dir)
            dagster.connect()
            self.registry.register('dagster', dagster)
        return self.registry.get('dagster')
    
    def get_prefect_flows(self):
        """Get Prefect flows."""
        # Lazy import to avoid circular dependency
        from price_app.src.main.prefect_app.prefect_app import load_prefect_flows
        return load_prefect_flows()
    
    def disconnect_all(self) -> None:
        """Disconnect all connections."""
        if self.registry.has('database'):
            self.registry.get('database').disconnect()
        if self.registry.has('celery'):
            self.registry.get('celery').disconnect()
        if self.registry.has('dagster'):
            self.registry.get('dagster').disconnect()
        self.registry.clear()
