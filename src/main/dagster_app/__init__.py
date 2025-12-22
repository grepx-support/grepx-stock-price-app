"""Dagster app."""

from grepx_connection_registry import ConnectionFactory
from .dagster_connection import DagsterConnection

ConnectionFactory.register('dagster', DagsterConnection)

__all__ = ["DagsterConnection"]
