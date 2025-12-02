"""Simple Moving Average (SMA) indicator."""
import logging
import pandas as pd
from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class SMA(BaseIndicator):
    """Calculate Simple Moving Average."""

    def __init__(self, symbol: str, config: dict):
        super().__init__(symbol, "SMA", config)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate SMA for specified periods."""
        try:
            result = df.copy()
            periods = self.config.get("periods", [10, 20, 50])

            logger.info(f"Calculating SMA with periods: {periods}")

            for period in periods:
                sma_col = f"sma_{period}"
                result[sma_col] = result["close"].rolling(window=period).mean()
                logger.debug(f"Calculated {sma_col}")

            # Keep only necessary columns
            keep_cols = ["date"] + [f"sma_{p}" for p in periods]
            result = result[[col for col in keep_cols if col in result.columns]]

            logger.info(f"SMA calculation completed")
            return result

        except Exception as e:
            logger.error(f"SMA calculation failed: {str(e)}", exc_info=True)
            raise