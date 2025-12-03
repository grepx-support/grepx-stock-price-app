"""Utility to store indicators in database."""
import logging
from db.MongoDBManager import MongoDBManager
from utils.indicator_factory import create_indicator

logger = logging.getLogger(__name__)


def store_indicators(indicator_results: dict, symbol: str, source: str):
    """
    Store indicator results in MongoDB.
    
    Args:
        indicator_results: Dict from process_indicators_for_symbol
        symbol: Stock symbol
        source: Data source name
    """
    try:
        all_success = True
        logger.info(f"Storing indicators for {symbol}")

        for indicator_name, result_df in indicator_results.items():
            try:
                if result_df.empty:
                    logger.warning(f"Empty result for {indicator_name}, skipping")
                    continue

                # Get collection name from first row (added by indicator)
                indicator = create_indicator(indicator_name, symbol)
                collection = indicator.get_collection_name()

                # Convert to records
                records = result_df.to_dict("records")

                # Store
                success = MongoDBManager.bulk_upsert_indicators(collection, records)

                if success:
                    logger.info(
                        f"Stored {len(records)} {indicator_name} records in {collection}"
                    )
                else:
                    all_success = False
                    logger.error(f"Failed to store {indicator_name} in {collection}")
                return all_success

            except Exception as e:
                all_success = False
                logger.error(
                    f"Failed to store {indicator_name}: {str(e)}", exc_info=True
                )

    except Exception as e:
        logger.error(f"Failed to store indicators for {symbol}: {str(e)}", exc_info=True)
        raise