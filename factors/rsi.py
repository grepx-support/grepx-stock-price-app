"""Relative Strength Index (RSI) indicator."""
import logging
import pandas as pd
from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class RSI(BaseIndicator):
    """Calculate Relative Strength Index."""

    def __init__(self, symbol: str, config: dict):
        super().__init__(symbol, "RSI", config)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI for specified periods."""
        try:
            result = df.copy()
            periods = self.config.get("periods", [14])

            logger.info(f"Calculating RSI with periods: {periods}")

            # Calculate price changes
            delta = result["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=1).mean()

            for period in periods:
                rsi_col = f"rsi_{period}"

                # Calculate average gain and loss
                avg_gain = gain.rolling(window=period).mean()
                avg_loss = loss.rolling(window=period).mean()

                # Calculate RS and RSI
                rs = avg_gain / avg_loss
                result[rsi_col] = 100 - (100 / (1 + rs))

                logger.debug(f"Calculated {rsi_col}")

            # Keep only necessary columns
            keep_cols = ["date"] + [f"rsi_{p}" for p in periods]
            result = result[[col for col in keep_cols if col in result.columns]]

            logger.info(f"RSI calculation completed")
            return result

        except Exception as e:
            logger.error(f"RSI calculation failed: {str(e)}", exc_info=True)
            raise