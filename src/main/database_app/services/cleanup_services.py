"""Database cleanup services for all backends (MongoDB, PostgreSQL, SQLite)."""

import logging
from typing import Dict, List, Optional
import asyncio

logger = logging.getLogger(__name__)


async def cleanup_mongodb_databases(
    connection_string: str,
    databases_to_delete: List[str],
) -> dict:
    """Delete entire MongoDB databases.

    Args:
        connection_string: MongoDB connection string
        databases_to_delete: List of database names to delete

    Returns:
        Dict with deletion results
    """
    try:
        from motor.motor_asyncio import AsyncIOMotorClient

        client = AsyncIOMotorClient(connection_string)
        deleted = []
        failed = []

        try:
            for db_name in databases_to_delete:
                try:
                    await client.drop_database(db_name)
                    deleted.append(db_name)
                    logger.info(f"[CLEANUP] Deleted MongoDB database: {db_name}")
                except Exception as e:
                    failed.append(db_name)
                    logger.error(f"[CLEANUP] Failed to delete database {db_name}: {str(e)}")
        finally:
            client.close()

        return {
            "backend": "mongodb",
            "requested": len(databases_to_delete),
            "deleted": len(deleted),
            "failed": len(failed),
            "deleted_databases": deleted,
            "failed_databases": failed,
        }
    except Exception as e:
        logger.error(f"[CLEANUP] MongoDB cleanup error: {str(e)}")
        return {
            "backend": "mongodb",
            "error": str(e),
            "deleted": 0,
        }


async def cleanup_postgresql_databases(
    host: str,
    port: int,
    username: str,
    password: str,
    databases_to_delete: List[str],
) -> dict:
    """Delete entire PostgreSQL databases.

    Args:
        host: PostgreSQL host
        port: PostgreSQL port
        username: Username
        password: Password
        databases_to_delete: List of database names to delete

    Returns:
        Dict with deletion results
    """
    try:
        import asyncpg

        admin_conn = await asyncpg.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database='postgres'
        )

        deleted = []
        failed = []

        try:
            for db_name in databases_to_delete:
                try:
                    # Terminate existing connections to the database
                    await admin_conn.execute(
                        f"""
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE datname = '{db_name}' AND pid <> pg_backend_pid();
                        """
                    )
                    # Drop the database
                    await admin_conn.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
                    deleted.append(db_name)
                    logger.info(f"[CLEANUP] Deleted PostgreSQL database: {db_name}")
                except Exception as e:
                    failed.append(db_name)
                    logger.error(f"[CLEANUP] Failed to delete PostgreSQL database {db_name}: {str(e)}")
        finally:
            await admin_conn.close()

        return {
            "backend": "postgresql",
            "requested": len(databases_to_delete),
            "deleted": len(deleted),
            "failed": len(failed),
            "deleted_databases": deleted,
            "failed_databases": failed,
        }
    except Exception as e:
        logger.error(f"[CLEANUP] PostgreSQL cleanup error: {str(e)}")
        return {
            "backend": "postgresql",
            "error": str(e),
            "deleted": 0,
        }


async def cleanup_sqlite_files(
    databases_to_delete: List[str],
) -> dict:
    """Delete SQLite database files.

    Uses the same data directory as database_helpers.py: database_app/data

    Args:
        databases_to_delete: List of database file names (without .db extension) to delete

    Returns:
        Dict with deletion results
    """
    from pathlib import Path

    deleted = []
    failed = []

    # Use the same path as database_helpers.py: database_app/data
    # Navigate from this file: database_app/services/cleanup_services.py
    current_file = Path(__file__)
    database_app_dir = current_file.parent.parent  # Go up to database_app
    data_dir = database_app_dir / "data"

    logger.info(f"[CLEANUP] Looking for SQLite databases in: {data_dir.absolute()}")

    try:
        for db_name in databases_to_delete:
            try:
                # If it's just a name, construct the full path
                if not db_name.endswith('.db'):
                    db_path = data_dir / f"{db_name}.db"
                else:
                    db_path = data_dir / db_name

                logger.debug(f"[CLEANUP] Attempting to delete: {db_path.absolute()}")

                if db_path.exists():
                    db_path.unlink()
                    deleted.append(str(db_path))
                    logger.info(f"[CLEANUP] Deleted SQLite database file: {db_path}")
                else:
                    logger.warning(f"[CLEANUP] SQLite database file not found: {db_path}")
                    # Still count it as a success since it's already gone
                    deleted.append(str(db_path))
            except Exception as e:
                failed.append(db_name)
                logger.error(f"[CLEANUP] Failed to delete SQLite database {db_name}: {str(e)}")

        return {
            "backend": "sqlite",
            "requested": len(databases_to_delete),
            "deleted": len(deleted),
            "failed": len(failed),
            "deleted_files": deleted,
            "failed_files": failed,
        }
    except Exception as e:
        logger.error(f"[CLEANUP] SQLite cleanup error: {str(e)}")
        return {
            "backend": "sqlite",
            "error": str(e),
            "deleted": 0,
        }
