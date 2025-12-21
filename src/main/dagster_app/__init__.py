"""Dagster app."""

from .dagster_connection import DagsterConnection
from servers.connections import ConnectionFactory

ConnectionFactory.register('dagster', DagsterConnection)

__all__ = ["DagsterConnection"]
