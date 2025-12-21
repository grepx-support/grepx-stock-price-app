import logging
from dagster import asset

logger = logging.getLogger(__name__)


@asset(
    name="cleanup_all_collections",
    description="Delete all collections from stocks, futures, and indices databases",
    tags={"kind": "utility", "team": "data-engineering"}
)
async def cleanup_all_collections():
    from servers.app.application import AppContext

    target_databases = [
        "stocks_analysis",
        "futures_analysis",
        "indices_analysis",
    ]

    summary = {}

    for db_name in target_databases:
        db = AppContext.get_database(db_name)
        collections = await db.list_collection_names()

        logger.info(f"Database '{db_name}': {len(collections)} collections found")

        deleted = 0
        for name in collections:
            try:
                await db[name].drop()
                deleted += 1
                logger.info(f"[{db_name}] ✓ Dropped {name}")
            except Exception as e:
                logger.error(f"[{db_name}] ✗ Failed to drop {name}: {e}")

        summary[db_name] = {
            "collections_deleted": deleted,
            "total_collections": len(collections),
        }

    logger.warning(f"CLEANUP SUMMARY: {summary}")
    return summary

async def cleanup_specific_collections(context) -> dict:
    """
    Delete specific collections from the database.

    Config example:
    ops:
      cleanup_specific_collections:
        config:
          collection_names: ["stocks_sma_indicator", "stocks_ema_indicator"]
    """
    from servers.app.application import AppContext

    collection_names = context.op_config["collection_names"]

    db_name = "stock_analysis"
    db = AppContext.get_database(db_name)

    deleted_count = 0
    failed = []

    logger.info(f"Starting cleanup of {len(collection_names)} specific collections")

    for collection_name in collection_names:
        try:
            await db[collection_name].drop()
            logger.info(f"✓ Deleted collection: {collection_name}")
            deleted_count += 1
        except Exception as e:
            logger.error(f"✗ Failed to delete collection {collection_name}: {str(e)}")
            failed.append(collection_name)

    result = {
        "database": db_name,
        "collections_deleted": deleted_count,
        "collections_requested": len(collection_names),
        "failed": failed
    }

    logger.info(f"Cleanup complete: {deleted_count}/{len(collection_names)} collections deleted")

    return result

# __all__ = [
#     "cleanup_all_collections",
# ]