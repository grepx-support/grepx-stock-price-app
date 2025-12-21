"""Celery app."""

from .celery_connection import CeleryConnection
from servers.connections import ConnectionFactory

ConnectionFactory.register('celery', CeleryConnection)

__all__ = ["CeleryConnection"]
