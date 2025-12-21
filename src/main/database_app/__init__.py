"""Database app."""

from servers.connections import ConnectionFactory
from .database_connection import DatabaseConnection

ConnectionFactory.register('database', DatabaseConnection)

__all__ = ["DatabaseConnection"]
