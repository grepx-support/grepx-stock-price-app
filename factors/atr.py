"""Average True Range (ATR) indicator."""
import logging
import pandas as pd
from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class ATR(BaseIndicator):
    """Calculate Average True Range."""

    def __init__(self, symbol: str, config: dict):
        super().__init__(symbol, "ATR", config)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate ATR for specified periods."""
        try:
            result = df.copy()
            periods = self.config.get("periods", [14])

            logger.info(f"Calculating ATR with periods: {periods}")

            # Calculate True Range
            result["hl"] = result["high"] - result["low"]
            result["hc"] = abs(result["high"] - result["close"].shift())
            result["lc"] = abs(result["low"] - result["close"].shift())
            result["tr"] = result[["hl", "hc", "lc"]].max(axis=1)

            # Calculate ATR for each period
            for period in periods:
                atr_col = f"atr_{period}"
                result[atr_col] = result["tr"].rolling(window=period).mean()
                logger.debug(f"Calculated {atr_col}")

            # Keep only necessary columns
            keep_cols = ["date"] + [f"atr_{p}" for p in periods]
            result = result[[col for col in keep_cols if col in result.columns]]

            logger.info(f"ATR calculation completed")
            return result

        except Exception as e:
            logger.error(f"ATR calculation failed: {str(e)}", exc_info=True)
            raise