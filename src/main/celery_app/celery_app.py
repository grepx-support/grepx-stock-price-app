"""Celery entry point."""
from servers.app.application import AppContext
app = AppContext().get_celery_app()

# get_database = AppContext.get_database
# get_collection = AppContext.get_collection
# get_celery_app = AppContext.get_celery_app
# get_dagster_defs = AppContext.get_dagster_defs
# # Expose for Celery CLI
# app = get_celery_app()
# # Expose for Dagster CLI
# defs = get_dagster_defs()