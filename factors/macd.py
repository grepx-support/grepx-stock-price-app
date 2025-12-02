"""MACD (Moving Average Convergence Divergence) indicator."""
import logging
import pandas as pd
from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class MACD(BaseIndicator):
    """Calculate MACD."""

    def __init__(self, symbol: str, config: dict):
        super().__init__(symbol, "MACD", config)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD."""
        try:
            result = df.copy()
            fast = self.config.get("fast_period", 12)
            slow = self.config.get("slow_period", 26)
            signal = self.config.get("signal_period", 9)

            logger.info(f"Calculating MACD ({fast}, {slow}, {signal})")

            # Calculate MACD line
            ema_fast = result["close"].ewm(span=fast, adjust=False).mean()
            ema_slow = result["close"].ewm(span=slow, adjust=False).mean()
            result["macd"] = ema_fast - ema_slow

            # Calculate Signal line
            result["macd_signal"] = result["macd"].ewm(span=signal, adjust=False).mean()

            # Calculate Histogram
            result["macd_histogram"] = result["macd"] - result["macd_signal"]

            logger.debug("MACD components calculated")

            # Keep only necessary columns
            keep_cols = ["date", "macd", "macd_signal", "macd_histogram"]
            result = result[[col for col in keep_cols if col in result.columns]]

            logger.info(f"MACD calculation completed")
            return result

        except Exception as e:
            logger.error(f"MACD calculation failed: {str(e)}", exc_info=True)
            raise