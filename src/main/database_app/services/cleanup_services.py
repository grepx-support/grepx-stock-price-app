import logging
from core import Session
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


async def cleanup_collections(
    backend_name: str,
    connection_params: dict,
    collection_names: list[str] | None = None,
) -> dict:
    """Delete specific collections/tables or all of them"""
    async with Session.from_backend_name(
        backend_name,
        **connection_params
    ) as session:
        backend = session.backend
        
        if collection_names is None:
            tables = await backend.list_tables()
        else:
            tables = collection_names
        
        deleted, failed = 0, []
        for table in tables:
            try:
                await backend.drop_table_by_name(table)
                deleted += 1
                logger.info(f"Deleted {backend_name} table: {table}")
            except Exception as e:
                failed.append(table)
                logger.error(f"Failed to delete {table}: {str(e)}")
        
        return {
            "backend": backend_name,
            "requested": len(tables),
            "deleted": deleted,
            "failed": failed,
        }

async def cleanup_mongodb_databases(connection_string: str, databases_to_delete: list[str], backend_name) -> dict:
    """Delete entire MongoDB databases"""
    client = AsyncIOMotorClient(connection_string)  
    deleted = []
    failed = []

    try:
        for db_name in databases_to_delete:
            try:
                await client.drop_database(db_name)
                deleted.append(db_name)
                logger.info(f"Deleted MongoDB database: {db_name}")
            except Exception as e:
                failed.append(db_name)
                logger.error(f"Failed to delete database {db_name}: {str(e)}")
    finally:
        client.close()  

    return {
        "backend": backend_name,
        "requested": len(databases_to_delete),
        "deleted": len(deleted),
        "failed_count": len(failed),
        "deleted_databases": deleted,
        "failed_databases": failed,
    }
