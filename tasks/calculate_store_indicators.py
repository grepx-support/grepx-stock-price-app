"""Task to calculate and store technical indicators."""
from celery_framework.tasks.decorators import task
import logging
import pandas as pd

from db.MongoDBConnection import MongoDBConnection
from db.MongoDBManager import MongoDBManager
from utils.indicator_processor import process_indicators_for_symbol
from utils.indicator_storage import store_indicators
from utils import clean_symbol

logger = logging.getLogger(__name__)

MongoDBConnection.connect()


@task(name="tasks.calculate_store_indicators")
def calculate_store_indicators(
    symbol: str, source: str = "default", indicators: list = None
):
    """
    Calculate and store technical indicators for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        source: Data source name
        indicators: List of indicator names. If None, uses all enabled indicators.
    """
    try:
        logger.info(f"[Celery] Calculating indicators for {symbol}")

        # Get price data from MongoDB
        clean = clean_symbol(symbol)
        price_collection = f"{clean}_prices"

        logger.debug(f"Fetching prices from {price_collection}")
        prices = MongoDBManager.find_all(price_collection)

        if not prices:
            logger.warning(f"No price data found for {symbol}")
            return {"status": "no_data", "symbol": symbol}

        # Convert to DataFrame
        price_df = pd.DataFrame(prices)

        # Process indicators
        indicator_results = process_indicators_for_symbol(symbol, price_df, indicators)

        if not indicator_results:
            logger.error(f"No indicators processed for {symbol}")
            return {"status": "error", "symbol": symbol, "error": "No indicators processed"}

        # Store indicators
        store_indicators(indicator_results, symbol, source)

        return {
            "status": "success",
            "symbol": symbol,
            "indicators_calculated": list(indicator_results.keys()),
        }

    except Exception as e:
        logger.error(f"Failed to calculate indicators for {symbol}", exc_info=True)
        return {"status": "error", "symbol": symbol, "error": str(e)}