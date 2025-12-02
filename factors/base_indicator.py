"""Base class for all technical indicators."""
import logging
from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)


class BaseIndicator(ABC):
    """Abstract base class for all indicators."""

    def __init__(self, symbol: str, indicator_name: str, config: dict):
        """
        Initialize indicator.
        
        Args:
            symbol: Stock ticker symbol
            indicator_name: Name of the indicator
            config: Configuration dict with parameters
        """
        self.symbol = symbol
        self.indicator_name = indicator_name
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{indicator_name}")

    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validate if data meets minimum requirements."""
        try:
            required_columns = self.config.get("required_columns", [])
            min_data_points = self.config.get("min_data_points", 1)

            # Check required columns
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                self.logger.error(f"Missing columns: {missing_cols}")
                return False

            # Check minimum data points
            if len(df) < min_data_points:
                self.logger.error(
                    f"Insufficient data: {len(df)} < {min_data_points} required"
                )
                return False

            self.logger.debug(f"Data validation passed for {self.symbol}")
            return True

        except Exception as e:
            self.logger.error(f"Data validation failed: {str(e)}", exc_info=True)
            return False

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate indicator values. Must be implemented by subclasses."""
        pass

    def _add_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add metadata columns to result."""
        try:
            df["symbol"] = self.symbol
            df["indicator"] = self.indicator_name
            df["fetched_at"] = datetime.now().isoformat()
            return df
        except Exception as e:
            self.logger.error(f"Failed to add metadata: {str(e)}", exc_info=True)
            raise

    def get_collection_name(self) -> str:
        """Generate MongoDB collection name."""
        try:
            clean_symbol = (
                self.symbol.replace(".NS", "")
                .replace(".BO", "")
                .replace(".", "_")
                .replace("-", "_")
                .lower()
            )
            collection = f"{clean_symbol}_{self.indicator_name.lower()}"
            self.logger.debug(f"Collection name: {collection}")
            return collection
        except Exception as e:
            self.logger.error(f"Failed to generate collection name: {str(e)}", exc_info=True)
            raise

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """Main processing pipeline."""
        try:
            self.logger.info(f"Processing {self.indicator_name} for {self.symbol}")

            if not self.validate_data(df):
                raise ValueError(f"Data validation failed for {self.symbol}")

            # Calculate indicator
            result_df = self.calculate(df)

            # Add metadata
            result_df = self._add_metadata(result_df)

            self.logger.info(f"Successfully processed {self.indicator_name}")
            return result_df

        except Exception as e:
            self.logger.error(
                f"Failed to process {self.indicator_name}: {str(e)}", exc_info=True
            )
            raise