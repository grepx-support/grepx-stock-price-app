"""Average True Range (ATR) indicator."""
import logging
from dagster_framework.converters import dataframe_operations, series_operations, aggregation
from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class ATR(BaseIndicator):
    """Calculate Average True Range."""

    def __init__(self, symbol: str, config: dict):
        super().__init__(symbol, "ATR", config)

    def calculate(self, df):
        """Calculate ATR for specified periods."""
        try:
            result = dataframe_operations.clone_dataframe(df)
            periods = self.config.get("periods", [14])

            logger.info(f"Calculating ATR with periods: {periods}")

            # Calculate True Range components
            result = result.with_columns([
                (result["high"] - result["low"]).alias("hl"),
                ((result["high"] - series_operations.shift_column(result, "close")).abs()).alias("hc"),
                ((result["low"] - series_operations.shift_column(result, "close")).abs()).alias("lc"),
            ])
            result = result.with_columns(
                aggregation.max_horizontal(result, ["hl", "hc", "lc"]).alias("tr")
            )

            # Calculate ATR for each period
            for period in periods:
                atr_col = f"atr_{period}"
                atr_values = series_operations.rolling_mean(result["tr"], period)
                result = result.with_columns(atr_values.alias(atr_col))
                logger.debug(f"Calculated {atr_col}")

            # Keep only necessary columns
            keep_cols = ["date"] + [f"atr_{p}" for p in periods]
            result = dataframe_operations.select_columns(result, keep_cols)

            logger.info(f"ATR calculation completed")
            return result

        except Exception as e:
            logger.error(f"ATR calculation failed: {str(e)}", exc_info=True)
            raise