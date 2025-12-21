"""Dagster app."""

from servers.connections import ConnectionFactory
from .dagster_connection import DagsterConnection

ConnectionFactory.register('dagster', DagsterConnection)

__all__ = ["DagsterConnection"]
