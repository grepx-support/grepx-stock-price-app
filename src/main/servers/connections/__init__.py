"""Connection management for servers."""

from .connection_protocol import Connection
from .connection_registry import ConnectionRegistry
from .connection_base import ConnectionBase
from .connection_manager import ConnectionManager

# Connection classes moved to their respective app directories:
# - DatabaseConnection -> database_app.database_connection
# - CeleryConnection -> celery_app.celery_connection
# - DagsterConnection -> dagster_app.dagster_connection

__all__ = [
    "Connection",
    "ConnectionRegistry",
    "ConnectionBase",
    "ConnectionManager",
]
