"""Exponential Moving Average (EMA) indicator."""
import logging
from dagster_framework.converters import dataframe_operations, series_operations
from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class EMA(BaseIndicator):
    """Calculate Exponential Moving Average."""

    def __init__(self, symbol: str, config: dict):
        super().__init__(symbol, "EMA", config)

    def calculate(self, df):
        """Calculate EMA for specified periods."""
        try:
            result = dataframe_operations.clone_dataframe(df)
            periods = self.config.get("periods", [12, 26])

            logger.info(f"Calculating EMA with periods: {periods}")

            for period in periods:
                ema_col = f"ema_{period}"
                ema_values = series_operations.exponential_weighted_mean(result["close"], span=period, adjust=False)
                result = result.with_columns(ema_values.alias(ema_col))
                logger.debug(f"Calculated {ema_col}")

            # Keep only necessary columns
            keep_cols = ["date"] + [f"ema_{p}" for p in periods]
            result = dataframe_operations.select_columns(result, keep_cols)

            logger.info(f"EMA calculation completed")
            return result

        except Exception as e:
            logger.error(f"EMA calculation failed: {str(e)}", exc_info=True)
            raise