"""Factory for creating data source instances - Strategy pattern."""

from typing import Dict, Any
from application.ports.data_sources import IMarketDataSource
from infrastructure.data_sources.yahoo_finance_source import YahooFinanceDataSource
import logging

logger = logging.getLogger(__name__)


class DataSourceFactory:
    """Factory for creating market data source instances."""

    _sources = {
        "yahoo": YahooFinanceDataSource,
        # Future: Add more sources here
        # "alpha_vantage": AlphaVantageDataSource,
        # "polygon": PolygonDataSource,
    }

    @classmethod
    def create(cls, source_type: str = "yahoo", config: Dict[str, Any] = None) -> IMarketDataSource:
        """
        Create a data source instance.
        
        Args:
            source_type: Type of data source ("yahoo", "alpha_vantage", etc.)
            config: Optional configuration for the data source
        
        Returns:
            IMarketDataSource instance
        
        Raises:
            ValueError: If source_type is not supported
        """
        source_class = cls._sources.get(source_type.lower())
        if not source_class:
            raise ValueError(f"Unknown data source type: {source_type}. Available: {list(cls._sources.keys())}")
        
        try:
            if config:
                return source_class(**config)
            return source_class()
        except Exception as e:
            logger.error(f"Error creating data source {source_type}: {e}")
            raise

    @classmethod
    def register_source(cls, name: str, source_class: type):
        """
        Register a new data source type.
        
        Args:
            name: Name of the data source
            source_class: Class implementing IMarketDataSource
        """
        cls._sources[name.lower()] = source_class
        logger.info(f"Registered data source: {name}")

