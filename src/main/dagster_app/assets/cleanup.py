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

    # Detect backend type from configuration
    connection_string = database_config.get("connection_string", "")
    host = database_config.get("host")
    port = database_config.get("port")
    username = database_config.get("username")
    password = database_config.get("password")
    databases_to_cleanup = ["stocks_analysis", "indices_analysis", "futures_analysis"]

    try:
        # Determine which backend is configured
        if connection_string:
            if "mongodb" in connection_string.lower():
                logger.info("[CLEANUP] MongoDB backend detected")
                result = asyncio.run(
                    cleanup_mongodb_databases(
                        connection_string=connection_string,
                        databases_to_delete=databases_to_cleanup,
                    )
                )
                results["mongodb"] = result
            elif "postgresql" in connection_string.lower():
                logger.info("[CLEANUP] PostgreSQL backend detected")
                # Parse connection string or use parameters
                result = asyncio.run(
                    cleanup_postgresql_databases(
                        host=host or "localhost",
                        port=port or 5432,
                        username=username or "postgres",
                        password=password or "",
                        databases_to_delete=databases_to_cleanup,
                    )
                )
                results["postgresql"] = result
            elif "sqlite" in connection_string.lower():
                logger.info("[CLEANUP] SQLite backend detected")
                result = asyncio.run(
                    cleanup_sqlite_files(databases_to_delete=databases_to_cleanup)
                )
                results["sqlite"] = result
        elif host and port and username:
            # Parameters-based config (PostgreSQL)
            logger.info("[CLEANUP] PostgreSQL backend detected (parameter-based)")
            result = asyncio.run(
                cleanup_postgresql_databases(
                    host=host,
                    port=port,
                    username=username,
                    password=password or "",
                    databases_to_delete=databases_to_cleanup,
                )
            )
            results["postgresql"] = result
        else:
            logger.warning("[CLEANUP] No database backend configuration found")
            return {"error": "No database configuration found in database.yaml"}

    except Exception as e:
        logger.error(f"[CLEANUP] Error during cleanup: {e}", exc_info=True)
        return {"error": str(e)}

    logger.warning(f"[CLEANUP] SUMMARY: {results}")
    return results
