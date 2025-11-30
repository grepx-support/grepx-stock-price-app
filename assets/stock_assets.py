"""Dagster asset for close price download orchestration."""

from dagster import asset
from omegaconf import OmegaConf
from price_app.config.paths import DAGSTER_CONFIG
from app.celery_framework_app import app as celery_app


_cfg = OmegaConf.load(DAGSTER_CONFIG)

SYMBOLS = _cfg.assets.config.close_price_download.symbols
TASK_NAME = _cfg.assets.config.close_price_download.celery_task
TIMEOUT = _cfg.assets.config.close_price_download.timeout

@asset(group_name="stock_data")
def close_price_download():
    """
    Dagster asset that triggers Celery tasks dynamically based on config.
    """
    results = []

    for symbol in SYMBOLS:
        task = celery_app.send_task(TASK_NAME, args=[symbol])
        result = task.get(TIMEOUT)
        results.append(result)

    return {
        "downloaded": len(results),
        "data": results,
    }
