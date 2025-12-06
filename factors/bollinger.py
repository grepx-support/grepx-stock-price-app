"""Bollinger Bands indicator."""
import logging
from dagster_framework.converters import dataframe_operations, series_operations
from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class BOLLINGER(BaseIndicator):
    """Calculate Bollinger Bands."""

    def __init__(self, symbol: str, config: dict):
        super().__init__(symbol, "BOLLINGER", config)

    def calculate(self, df):
        """Calculate Bollinger Bands for specified periods."""
        try:
            result = dataframe_operations.clone_dataframe(df)
            periods = self.config.get("periods", [20])
            std_devs = self.config.get("std_dev", [2])

            logger.info(f"Calculating Bollinger Bands with periods: {periods}")

            for period in periods:
                sma = series_operations.rolling_mean(result["close"], period)
                std = series_operations.rolling_std(result["close"], period)

                for std_dev in std_devs:
                    upper_col = f"bb_upper_{period}_{std_dev}"
                    lower_col = f"bb_lower_{period}_{std_dev}"
                    middle_col = f"bb_middle_{period}"

                    result = result.with_columns(
                        (sma + (std * std_dev)).alias(upper_col),
                        (sma - (std * std_dev)).alias(lower_col),
                        sma.alias(middle_col)
                    )

                    logger.debug(f"Calculated {upper_col}, {lower_col}")

            # Keep only necessary columns
            bb_cols = [col for col in result.columns if col.startswith("bb_")]
            keep_cols = ["date"] + bb_cols
            result = dataframe_operations.select_columns(result, keep_cols)

            logger.info(f"Bollinger Bands calculation completed")
            return result

        except Exception as e:
            logger.error(f"Bollinger Bands calculation failed: {str(e)}", exc_info=True)
            raise