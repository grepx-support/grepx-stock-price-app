"""Cleanup assets for managing database collections and tables."""

import logging
from dagster import asset
from omegaconf import OmegaConf
from pathlib import Path

logger = logging.getLogger(__name__)


@asset(
    name="cleanup_databases",
    description="Cleanup selected databases based on database.yaml config",
    tags={"kind": "utility"},
)
def cleanup_databases():
    """Cleanup databases based on configuration - synchronous version for Dagster compatibility.

    This asset cleans up databases specified in the database.yaml configuration.
    It handles MongoDB (drops entire databases), PostgreSQL (drops databases),
    and SQLite (deletes database files).
    """
    from database_app.services.cleanup_services import (
        cleanup_mongodb_databases,
        cleanup_postgresql_databases,
        cleanup_sqlite_files,
    )
    import asyncio

    # Load configuration
    asset_file = Path(__file__)
    resources_dir = asset_file.parent.parent.parent / "resources"
    database_yaml = resources_dir / "database.yaml"

    try:
        config = OmegaConf.load(str(database_yaml))
        database_config = config.get("database", {})
    except Exception as e:
        logger.error(f"[CLEANUP] Failed to load database.yaml: {e}")
        return {"error": f"Failed to load config: {str(e)}"}

    results = {}

    # Get active backend from configuration
    active_backend = database_config.get("active_backend", "postgresql")
    backend_config = database_config.get(active_backend, {})
    databases_to_cleanup = ["stocks_analysis", "indices_analysis", "futures_analysis"]

    try:
        if active_backend == "mongodb":
            logger.info("[CLEANUP] MongoDB backend detected")
            connection_string = backend_config.get("connection_string", "mongodb://localhost:27017/")
            result = asyncio.run(
                cleanup_mongodb_databases(
                    connection_string=connection_string,
                    databases_to_delete=databases_to_cleanup,
                )
            )
            results["mongodb"] = result

        elif active_backend == "postgresql":
            logger.info("[CLEANUP] PostgreSQL backend detected")
            # Get connection parameters
            host = backend_config.get("host", "localhost")
            port = backend_config.get("port", 5432)
            username = backend_config.get("username", "postgres")
            password = backend_config.get("password", "")

            result = asyncio.run(
                cleanup_postgresql_databases(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    databases_to_delete=databases_to_cleanup,
                )
            )
            results["postgresql"] = result

        elif active_backend == "sqlite":
            logger.info("[CLEANUP] SQLite backend detected")
            result = asyncio.run(
                cleanup_sqlite_files(databases_to_delete=databases_to_cleanup)
            )
            results["sqlite"] = result

        else:
            logger.warning(f"[CLEANUP] Unknown backend: {active_backend}")
            return {"error": f"Unknown backend: {active_backend}"}

    except Exception as e:
        logger.error(f"[CLEANUP] Error during cleanup: {e}", exc_info=True)
        return {"error": str(e)}

    logger.warning(f"[CLEANUP] SUMMARY: {results}")
    return results
