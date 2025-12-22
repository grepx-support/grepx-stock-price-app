"""Prefect app."""

from grepx_connection_registry import ConnectionFactory
from .prefect_connection import PrefectConnection

ConnectionFactory.register('prefect', PrefectConnection)

__all__ = ["PrefectConnection"]