from prefect import flow
import sys
from pathlib import Path

# Add the main directory to the path to import modules
main_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(main_dir))

from prefect_app.tasks.price_tasks import (
    config_prices,
    config_indicators,
    fetch_data,
    store_data,
    compute_indicators,
    store_indicators
)

from database_app.services.cleanup_services import (
    cleanup_mongodb_databases,
    cleanup_postgresql_databases,
    cleanup_sqlite_files,
)
import asyncio
from omegaconf import OmegaConf


@flow(name="Generic Asset ETL Pipeline")
def generic_asset_etl(asset_type: str = "stocks", limit: int = 100):
    """Generic ETL for stocks/futures/indices using service functions"""
    
    # Handle cleanup asset type differently
    if asset_type == "cleanup":
        # Load database configuration for cleanup
        from pathlib import Path
        import logging
        logger = logging.getLogger(__name__)
        
        resources_dir = Path(__file__).parent.parent.parent / "resources"
        database_yaml = resources_dir / "database.yaml"
        
        try:
            config = OmegaConf.load(str(database_yaml))
            database_config = config.get("database", {})
        except Exception as e:
            logger.error(f"[CLEANUP] Failed to load database.yaml: {e}")
            return {"error": f"Failed to load config: {str(e)}", "asset_type": asset_type}
        
        # Get active backend from configuration (like Dagster does)
        active_backend = database_config.get("active_backend", "postgresql")
        backend_config = database_config.get(active_backend, {})
        databases_to_cleanup = ["stocks_analysis", "indices_analysis", "futures_analysis"]
        
        results = {}
        
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
                return {"error": f"Unknown backend: {active_backend}", "asset_type": asset_type}

        except Exception as e:
            logger.error(f"[CLEANUP] Error during cleanup: {e}", exc_info=True)
            return {"error": str(e), "asset_type": asset_type}
        
        logger.info(f"[CLEANUP] SUMMARY: {results}")
        
        return {
            "asset_type": asset_type,
            "cleanup_results": results,
            "cleanup_performed": True,
            "active_backend": active_backend
        }
    
    # For other asset types (stocks, indices, futures), run the standard ETL
    else:
        # Step 1: Get configurations (equivalent to Dagster config assets)
        prices_config = config_prices(asset_type)
        indicators_config = config_indicators(asset_type)
        
        # Step 2: Fetch data (equivalent to Dagster fetch asset)
        price_data = fetch_data(prices_config)
        
        # Step 3: Store data (equivalent to Dagster store asset)
        stored_results = store_data(price_data, asset_type)
        
        # Step 4: Compute indicators (equivalent to Dagster indicator assets)
        indicator_data = compute_indicators(price_data, indicators_config, asset_type)
        
        # Step 5: Store indicators (equivalent to Dagster store indicators asset)
        indicators_stored = store_indicators(indicator_data, asset_type)
        
        return {
            "asset_type": asset_type,
            "price_data_fetched": len(price_data) if price_data else 0,
            "price_records_stored": stored_results,
            "indicator_records_stored": indicators_stored,
            "indicators_computed": len(indicator_data) if indicator_data else 0
        }


if __name__ == "__main__":
    # Run the flow locally for testing
    result = generic_asset_etl(asset_type="stocks", limit=10)
    print(f"Flow completed. Result: {result}")