"""Indicator-related Celery tasks - thin wrappers around use cases."""

from celery import shared_task
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, name="adapters.tasks.indicator_tasks.compute_indicator")
def compute_indicator_task(self, symbol: str, factor: str, price_records: List[Dict[str, Any]], indicator_config: Dict[str, Any]):
    """
    Compute indicator for a symbol.
    
    This is a thin wrapper that will be injected with use cases at runtime.
    """
    try:
        # Import here to avoid circular dependencies
        from main import get_compute_indicators_use_case
        
        use_case = get_compute_indicators_use_case()
        result = use_case.execute_from_records(symbol, factor, price_records, indicator_config)
        
        logger.info(f"Computed {factor} for {symbol}: {result.count} records")
        return result.records
    except Exception as e:
        logger.error(f"Compute error for {symbol}_{factor}: {e}")
        raise self.retry(exc=e, countdown=10)


@shared_task(bind=True, max_retries=2, name="adapters.tasks.indicator_tasks.store_indicator")
def store_indicator_task(self, symbol: str, factor: str, factor_data: List[Dict[str, Any]], asset_type: str = "stocks"):
    """
    Store indicator data.
    
    This is a thin wrapper that will be injected with use cases at runtime.
    """
    try:
        # Import here to avoid circular dependencies
        from main import get_store_data_use_case
        import asyncio
        
        use_case = get_store_data_use_case(asset_type, symbol, factor)
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(use_case.store_indicators(factor_data))
        
        logger.info(f"Stored {factor} for {symbol}: {result.stored} records")
        return {
            "symbol": symbol,
            "factor": factor,
            "status": result.status,
            "stored": result.stored,
            "total": result.total,
            "error": result.error
        }
    except Exception as e:
        logger.error(f"Indicator store error for {symbol}_{factor}: {e}")
        raise self.retry(exc=e, countdown=5)

