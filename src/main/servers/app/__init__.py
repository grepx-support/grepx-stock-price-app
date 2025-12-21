"""App package - completely generic."""

from .application import (
    get_connection,
    connections,
    config,
    conn_config,
)
from .connection_config import ConnectionConfig

__all__ = [
    "get_connection",
    "connections",
    "config",
    "conn_config",
    "ConnectionConfig",
]
