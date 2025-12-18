"""Data source interfaces - abstractions for external data providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from application.dto import FetchPricesResultDTO


class IMarketDataSource(ABC):
    """Interface for market data sources."""

    @abstractmethod
    def fetch_prices(self, symbol: str, start_date: str = None, end_date: str = None) -> FetchPricesResultDTO:
        """Fetch price data for a symbol."""
        pass

    @abstractmethod
    def fetch_multiple_prices(self, symbols: List[str], start_date: str = None, end_date: str = None) -> Dict[str, FetchPricesResultDTO]:
        """Fetch price data for multiple symbols."""
        pass

