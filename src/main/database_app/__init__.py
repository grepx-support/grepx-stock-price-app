"""Database app."""

from grepx_connection_registry import ConnectionFactory
from .database_connection import DatabaseConnection

ConnectionFactory.register('database', DatabaseConnection)

__all__ = ["DatabaseConnection"]
