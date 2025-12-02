"""Exponential Moving Average (EMA) indicator."""
import logging
import pandas as pd
from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class EMA(BaseIndicator):
    """Calculate Exponential Moving Average."""

    def __init__(self, symbol: str, config: dict):
        super().__init__(symbol, "EMA", config)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate EMA for specified periods."""
        try:
            result = df.copy()
            periods = self.config.get("periods", [12, 26])

            logger.info(f"Calculating EMA with periods: {periods}")

            for period in periods:
                ema_col = f"ema_{period}"
                result[ema_col] = result["close"].ewm(span=period, adjust=False).mean()
                logger.debug(f"Calculated {ema_col}")

            # Keep only necessary columns
            keep_cols = ["date"] + [f"ema_{p}" for p in periods]
            result = result[[col for col in keep_cols if col in result.columns]]

            logger.info(f"EMA calculation completed")
            return result

        except Exception as e:
            logger.error(f"EMA calculation failed: {str(e)}", exc_info=True)
            raise