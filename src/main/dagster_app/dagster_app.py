"""Dagster entry point."""
from servers.app.application import AppContext
defs = AppContext.get_dagster_defs()