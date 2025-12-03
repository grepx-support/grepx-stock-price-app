"""Utility to store indicators in database."""
import logging
from db.MongoDBManager import MongoDBManager
from utils.processors.indicator_factory import create_indicator

logger = logging.getLogger(__name__)


def store_indicators(indicator_results: dict, symbol: str, source: str):
    """
    Store indicator results in MongoDB.

    Args:
        indicator_results: Dict from process_indicators_for_symbol
        symbol: Stock symbol
        source: Data source name

    Returns:
        True if all indicators stored successfully, False otherwise
    """
    try:
        all_success = True
        logger.info(f"Storing indicators for {symbol}")

        for indicator_name, result_df in indicator_results.items():
            try:
                if result_df.is_empty():
                    logger.warning(f"Empty result for {indicator_name}, skipping")
                    continue

                # Get collection name from first row (added by indicator)
                indicator = create_indicator(indicator_name, symbol)
                collection = indicator.get_collection_name()

                # Convert to records (Polars DataFrame)
                records = result_df.to_dicts()

                # Store
                success = MongoDBManager.bulk_insert(collection, records)

                if success:
                    logger.info(
                        f"Stored {len(records)} {indicator_name} records in {collection}"
                    )
                else:
                    all_success = False
                    logger.error(f"Failed to store {indicator_name} in {collection}")

            except Exception as e:
                all_success = False
                logger.error(
                    f"Failed to store {indicator_name}: {str(e)}", exc_info=True
                )

        return all_success

    except Exception as e:
        logger.error(f"Failed to store indicators for {symbol}: {str(e)}", exc_info=True)
        return False