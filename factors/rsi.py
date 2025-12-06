"""Relative Strength Index (RSI) indicator."""
import logging
from dagster_framework.converters import dataframe_operations, series_operations
from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class RSI(BaseIndicator):
    """Calculate Relative Strength Index."""

    def __init__(self, symbol: str, config: dict):
        super().__init__(symbol, "RSI", config)

    def calculate(self, df):
        """Calculate RSI for specified periods."""
        try:
            result = dataframe_operations.clone_dataframe(df)
            periods = self.config.get("periods", [14])

            logger.info(f"Calculating RSI with periods: {periods}")

            # Calculate price changes
            delta = series_operations.difference(result["close"])

            # Separate gains and losses (replace negative with 0)
            gain_series = series_operations.clip_at_min(delta, 0)
            loss_series = series_operations.clip_at_min(-delta, 0)

            gain = series_operations.rolling_mean(gain_series, 1)
            loss = series_operations.rolling_mean(loss_series, 1)

            for period in periods:
                rsi_col = f"rsi_{period}"

                # Calculate average gain and loss
                avg_gain = series_operations.rolling_mean(gain, period)
                avg_loss = series_operations.rolling_mean(loss, period)

                # Calculate RS and RSI
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                result = result.with_columns(rsi.alias(rsi_col))

                logger.debug(f"Calculated {rsi_col}")

            # Keep only necessary columns
            keep_cols = ["date"] + [f"rsi_{p}" for p in periods]
            result = dataframe_operations.select_columns(result, keep_cols)

            logger.info(f"RSI calculation completed")
            return result

        except Exception as e:
            logger.error(f"RSI calculation failed: {str(e)}", exc_info=True)
            raise