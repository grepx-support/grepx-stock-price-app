"""Celery app."""

from grepx_connection_registry import ConnectionFactory
from .celery_connection import CeleryConnection

ConnectionFactory.register('celery', CeleryConnection)

__all__ = ["CeleryConnection"]
