"""Bollinger Bands indicator."""
import logging
import pandas as pd
from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class BOLLINGER(BaseIndicator):
    """Calculate Bollinger Bands."""

    def __init__(self, symbol: str, config: dict):
        super().__init__(symbol, "BOLLINGER", config)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands for specified periods."""
        try:
            result = df.copy()
            periods = self.config.get("periods", [20])
            std_devs = self.config.get("std_dev", [2])

            logger.info(f"Calculating Bollinger Bands with periods: {periods}")

            for period in periods:
                sma = result["close"].rolling(window=period).mean()
                std = result["close"].rolling(window=period).std()

                for std_dev in std_devs:
                    upper_col = f"bb_upper_{period}_{std_dev}"
                    lower_col = f"bb_lower_{period}_{std_dev}"
                    middle_col = f"bb_middle_{period}"

                    result[upper_col] = sma + (std * std_dev)
                    result[lower_col] = sma - (std * std_dev)
                    result[middle_col] = sma

                    logger.debug(f"Calculated {upper_col}, {lower_col}")

            # Keep only necessary columns
            keep_cols = ["date"]
            keep_cols += [col for col in result.columns if col.startswith("bb_")]
            result = result[[col for col in keep_cols if col in result.columns]]

            logger.info(f"Bollinger Bands calculation completed")
            return result

        except Exception as e:
            logger.error(f"Bollinger Bands calculation failed: {str(e)}", exc_info=True)
            raise