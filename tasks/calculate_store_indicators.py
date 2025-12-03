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
    symbol: str,
    indicator_name: str,
    source: str,
):
    """
    Calculate and store ONE indicator for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        indicator_name: Single indicator name (ATR, EMA, SMA, etc.)
        source: Data source name
    """
    try:
        logger.info(f"[Celery] Calculating {indicator_name} for {symbol}")

        # Get price data from MongoDB
        clean = clean_symbol(symbol)
        price_collection = f"{clean}_prices"

        logger.debug(f"Fetching prices from {price_collection}")
        prices = MongoDBManager.find_all(price_collection)

        if not prices:
            logger.warning(f"No price data found for {symbol}")
            return {
                "status": "no_data",
                "symbol": symbol,
                "indicator": indicator_name
            }

        # Convert to DataFrame
        price_df = pd.DataFrame(prices)
        logger.debug(f"Loaded {len(price_df)} price records")

        # Process SINGLE indicator
        indicator_results = process_indicators_for_symbol(
            symbol,
            price_df,
            source=source,
            indicators=[indicator_name]  # Pass as list
        )

        if not indicator_results:
            logger.error(f"No {indicator_name} processed for {symbol}")
            return {
                "status": "error",
                "symbol": symbol,
                "indicator": indicator_name,
                "error": "No indicators processed"
            }

        # Store indicator
        write_success = store_indicators(indicator_results, symbol, source)
        if not write_success:
            logger.error(f"Failed to store {indicator_name} for {symbol}")
            return {
            "status": "error",
            "symbol": symbol,
            "indicator": indicator_name,
            "error": "DB write failed"
            }
        
        rows = len(indicator_results.get(indicator_name, []))

        logger.info(f"✓ {indicator_name} stored for {symbol} ({rows} rows)")

        return {
            "status": "success",
            "symbol": symbol,
            "indicator": indicator_name,
            "rows": rows,
            "collection": f"{clean}_{indicator_name.lower()}"
        }

    except Exception as e:
        logger.error(f"Failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "symbol": symbol,
            "indicator": indicator_name,
            "error": str(e)
        }
