"""Celery app."""

from servers.connections import ConnectionFactory
from .celery_connection import CeleryConnection

ConnectionFactory.register('celery', CeleryConnection)

__all__ = ["CeleryConnection"]
