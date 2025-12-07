from dagster import asset, Failure
from omegaconf import OmegaConf
from config.paths import DAGSTER_CONFIG
from app.main import app as celery_app
import logging

logger = logging.getLogger(__name__)

_cfg = OmegaConf.load(DAGSTER_CONFIG)
conf = _cfg.assets.config.price_ingestion

SYMBOLS = conf.symbols
START = conf.start_date
END = conf.end_date
SOURCE = conf.source
TASK_NAME = conf.celery_task
TIMEOUT = conf.timeout


@asset(group_name="stock_data")
def price_ingestion():
    """Submit multi-source ingestion tasks to Celery."""
    results = []

    for symbol in SYMBOLS:
        print(f"Submitting ingestion task for {symbol} from {SOURCE}")

        task = celery_app.send_task(
            TASK_NAME,
            args=[symbol, START, END, SOURCE]
        )
        result = task.get(TIMEOUT)
        if result["status"] != "success":
            logger.warning(f"Celery task failed for {symbol}: {result}")
        else:
            logger.info(f"Celery task succeeded for {symbol}: {result}")

        results.append(result)

    return {
        "total_symbols": len(SYMBOLS),
        "results": results,
        "source": SOURCE
    }
