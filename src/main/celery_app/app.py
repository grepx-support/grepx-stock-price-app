"""Celery app entry point."""

from servers.app import get_connection, conn_config

app = get_connection(conn_config.celery).get_client()
