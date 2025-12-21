"""Dagster app entry point."""

from servers.app import get_connection, conn_config

defs = get_connection(conn_config.dagster).get_definitions()
