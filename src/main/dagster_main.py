"""Dagster entry point.

Usage: dagster dev -m dagster_main
"""

# Import apps to register connection types
import database_app
from dagster import Definitions, load_assets_from_modules
from dagster_app.assets.stocks import stocks_assets
from dagster_app.assets.indices import indices_assets
from dagster_app.assets.futures import futures_assets
from servers.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Initializing Dagster application...")

try:
    logger.debug("Loading assets from modules...")
    
    # Load assets from all asset modules
    all_assets = load_assets_from_modules([
        stocks_assets,
        indices_assets,
        futures_assets
    ])
    logger.info(f"Loaded {len(all_assets)} assets")
    
    logger.debug("Creating database resource...")
    from main import get_connection
    database_resource = get_connection("primary_db")
    
    logger.debug("Creating Dagster Definitions...")
    defs = Definitions(
        assets=all_assets,
        resources={"database": database_resource}
    )
    logger.info("Dagster application initialized successfully")
    logger.debug(f"Definitions created with {len(all_assets)} assets")
    
except Exception as e:
    logger.error(f"Failed to initialize Dagster application: {e}", exc_info=True)
    # Create empty definitions as fallback so Dagster can still load the module
    # This allows Dagster UI to show the error instead of failing to load entirely
    logger.warning("Creating empty Definitions as fallback due to initialization error")
    defs = Definitions(assets=[], resources={})
    # Don't raise - let Dagster UI show the error through logs
