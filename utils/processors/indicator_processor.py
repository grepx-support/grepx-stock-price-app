"""Utility to process indicators for symbols."""
import logging
from typing import Any
from utils.processors.indicator_factory import create_indicator
from dagster_framework.converters import dataframe_operations

logger = logging.getLogger(__name__)


def process_indicators_for_symbol(
    symbol: str, price_df: Any, source: str, indicators: list = None
) -> dict:
    """
    Process multiple indicators for a symbol.

    Args:
        symbol: Stock ticker symbol
        price_df: Polars DataFrame with OHLC data
        indicators: List of indicator names to calculate. If None, uses all enabled.

    Returns:
        Dict with indicator_name: Polars DataFrame
    """
    try:
        if indicators is None:
            from repos.price_app.assets.indicator_assets import get_enabled_indicators
            indicators = get_enabled_indicators()

        logger.info(f"Processing {len(indicators)} indicators for {symbol}")

        results = {}
        errors = []

        for indicator_name in indicators:
            try:
                logger.debug(f"Processing {indicator_name} for {symbol}")

                indicator = create_indicator(indicator_name, symbol)
                result_df = indicator.process(price_df)
                result_df = dataframe_operations.add_column(result_df, "source", source)
                if result_df is None or result_df.is_empty():
                    logger.warning(f"{indicator_name} returned empty df")
                    continue
                results[indicator_name] = result_df
                logger.info(f"Successfully processed {indicator_name} for {symbol}")

            except Exception as e:
                error_msg = f"Failed to process {indicator_name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)

        if errors:
            logger.warning(f"Completed with {len(errors)} errors")

        return results

    except Exception as e:
        logger.error(f"Failed to process indicators for {symbol}: {str(e)}", exc_info=True)
        raise