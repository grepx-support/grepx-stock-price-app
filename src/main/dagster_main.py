from servers.utils.logger import get_logger
from main import get_connection
from dagster import Definitions
from dagster_framework.dagster_app import DagsterApp

logger = get_logger(__name__)
logger.info("Initializing Dagster application...")

try:
    app_config = get_connection("primary_dagster").get_client()

    # Initialize your DagsterApp using the config
    dagster_app = DagsterApp(config=app_config['config']['dagster'])

    # Get Dagster definitions
    defs = dagster_app.definitions

    logger.info("Dagster application initialized successfully")
    logger.debug(f"Loaded {len(defs.assets)} assets and {len(defs.jobs)} jobs")

except Exception as e:
    logger.error(f"Failed to initialize Dagster application: {e}", exc_info=True)
    defs = Definitions()  # fallback
