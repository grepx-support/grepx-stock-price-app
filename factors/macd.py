"""MACD (Moving Average Convergence Divergence) indicator."""
import logging
from dagster_framework.converters import dataframe_operations, series_operations
from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class MACD(BaseIndicator):
    """Calculate MACD."""

    def __init__(self, symbol: str, config: dict):
        super().__init__(symbol, "MACD", config)

    def calculate(self, df):
        """Calculate MACD."""
        try:
            result = dataframe_operations.clone_dataframe(df)
            fast = self.config.get("fast_period", 12)
            slow = self.config.get("slow_period", 26)
            signal = self.config.get("signal_period", 9)

            logger.info(f"Calculating MACD ({fast}, {slow}, {signal})")

            # Calculate MACD line
            ema_fast = series_operations.exponential_weighted_mean(result["close"], span=fast, adjust=False)
            ema_slow = series_operations.exponential_weighted_mean(result["close"], span=slow, adjust=False)
            macd_line = ema_fast - ema_slow
            result = result.with_columns(macd_line.alias("macd"))

            # Calculate Signal line
            macd_signal = series_operations.exponential_weighted_mean(result["macd"], span=signal, adjust=False)
            result = result.with_columns(macd_signal.alias("macd_signal"))

            # Calculate Histogram
            histogram = result["macd"] - result["macd_signal"]
            result = result.with_columns(histogram.alias("macd_histogram"))

            logger.debug("MACD components calculated")

            # Keep only necessary columns
            keep_cols = ["date", "macd", "macd_signal", "macd_histogram"]
            result = dataframe_operations.select_columns(result, keep_cols)

            logger.info(f"MACD calculation completed")
            return result

        except Exception as e:
            logger.error(f"MACD calculation failed: {str(e)}", exc_info=True)
            raise