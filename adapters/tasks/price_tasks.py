"""Price-related Celery tasks - thin wrappers around use cases."""

from celery import shared_task
import logging
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)


def _get_event_loop():
    """Get or create event loop for the worker process."""
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


@shared_task(bind=True, max_retries=3, name="adapters.tasks.price_tasks.fetch_price")
def fetch_price_task(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Fetch price data for a symbol.
    
    This is a thin wrapper that will be injected with use cases at runtime.
    """
    try:
        # Import here to avoid circular dependencies
        from main import get_fetch_prices_use_case
        
        use_case = get_fetch_prices_use_case()
        result = use_case.execute(symbol, start_date, end_date, store=False)
        
        logger.info(f"Fetched {symbol}: {result.count} records")
        return {
            "symbol": result.symbol,
            "records": result.records,
            "count": result.count,
            "status": result.status,
            "error": result.error
        }
    except Exception as exc:
        logger.error(f"Fetch error for {symbol}: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@shared_task(bind=True, max_retries=2, name="adapters.tasks.price_tasks.store_price")
def store_price_task(self, price_data: dict, symbol: str, asset_type: str = "stocks"):
    """
    Store price data.
    
    This is a thin wrapper that will be injected with use cases at runtime.
    """
    try:
        # Import here to avoid circular dependencies
        from main import get_store_data_use_case
        
        use_case = get_store_data_use_case(asset_type, symbol)
        records = price_data.get("records", [])
        
        loop = _get_event_loop()
        result = loop.run_until_complete(use_case.store_prices(records))
        
        logger.info(f"Stored {symbol}: {result.stored} records")
        return {
            "symbol": symbol,
            "status": result.status,
            "stored": result.stored,
            "total": result.total,
            "error": result.error
        }
    except Exception as exc:
        logger.error(f"Store error for {symbol}: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

