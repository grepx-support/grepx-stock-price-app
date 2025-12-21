"""Database app."""

from .database_connection import DatabaseConnection
from servers.connections import ConnectionFactory

ConnectionFactory.register('database', DatabaseConnection)

__all__ = ["DatabaseConnection"]
