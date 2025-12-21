"""Main entry point - imports apps and exposes connections."""

import database_app
import celery_app
import dagster_app

from servers.app import get_connection, conn_config

# For Celery CLI
app = get_connection(conn_config.celery).get_client()

# For Dagster CLI
defs = get_connection(conn_config.dagster).get_definitions()
