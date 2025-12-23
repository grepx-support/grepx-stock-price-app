from dagster import asset
from omegaconf import OmegaConf
from pathlib import Path
from database_app.services.cleanup_services import cleanup_collections, cleanup_mongodb_databases
from urllib.parse import urlparse

@asset(
    name="cleanup_databases",
    description="Cleanup selected databases based on database.yaml config",
    tags={"kind": "utility"},
)
async def cleanup_databases():
    
    """
    Dagster asset to clean up databases or tables based on configuration.

    Reads 'resources/database.yaml' for backend-specific cleanup instructions,
    then asynchronously deletes the specified MongoDB databases, SQLite tables,
    and PostgreSQL tables.

    Returns:
        dict: A dictionary with cleanup results per backend, including:
              - 'requested': number of items intended for deletion
              - 'deleted': number of items successfully deleted
              - 'failed': number of items that failed to delete
              - 'deleted_items': list of successfully deleted items
              - 'failed_items': list of items that failed deletion
    """

    asset_file = Path(__file__)
    resources_dir = asset_file.parents[2] / "resources"
    config_path = resources_dir / "database.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(
        f"Database configuration file not found at '{config_path}'. "
        "Ensure that 'database.yaml' exists in the resources directory."
    )
    try:
        config = OmegaConf.load(str(config_path))
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load or parse database configuration from '{config_path}': {exc}"
        ) from exc
        
    backends_config = config.backends
    
    results = {}
    
    # Process MongoDB
    if backends_config.mongodb.enabled:
        mongo_config = backends_config.mongodb
        results["mongodb"] = await cleanup_mongodb_databases(
            connection_string=mongo_config.connection_string,
            databases_to_delete=list(mongo_config.databases_to_delete),
            backend_name="mongodb"
        )
    
    # Process SQLite
    if backends_config.sqlite.enabled:
        sqlite_config = backends_config.sqlite
        parsed = urlparse(sqlite_config.connection_string)
        if parsed.scheme != "sqlite":
            raise ValueError(f"Expected a sqlite connection string, got {sqlite_config.connection_string}")
        db_path = parsed.path
        results["sqlite"] = await cleanup_collections(
            backend_name="sqlite",
            connection_params={
                "database": db_path
            },
            collection_names=list(sqlite_config.tables_to_delete) if sqlite_config.tables_to_delete else None,
        )
    
    # Process PostgreSQL
    if backends_config.postgresql.enabled:
        postgresql_config = backends_config.postgresql
        conn_str = postgresql_config.connection_string
        results["postgresql"] = await cleanup_collections(
            backend_name="postgresql",
            connection_params={"connection_string": conn_str},
            collection_names=list(postgresql_config.tables_to_delete) if postgresql_config.tables_to_delete else None,
        )
    
    return results