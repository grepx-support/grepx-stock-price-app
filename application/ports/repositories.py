"""Repository interfaces - abstractions for data persistence."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class IPriceRepository(ABC):
    """Interface for price data repository."""

    @abstractmethod
    async def save_price(self, symbol: str, date: str, price_data: Dict[str, Any]) -> bool:
        """Save a single price record."""
        pass

    @abstractmethod
    async def save_prices(self, price_records: List[Dict[str, Any]]) -> int:
        """Save multiple price records. Returns count of saved records."""
        pass

    @abstractmethod
    async def get_prices(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get price records for a symbol."""
        pass


class IIndicatorRepository(ABC):
    """Interface for indicator data repository."""

    @abstractmethod
    async def save_indicator(self, symbol: str, factor: str, date: str, indicator_data: Dict[str, Any]) -> bool:
        """Save a single indicator record."""
        pass

    @abstractmethod
    async def save_indicators(self, indicator_records: List[Dict[str, Any]]) -> int:
        """Save multiple indicator records. Returns count of saved records."""
        pass

    @abstractmethod
    async def get_indicators(self, symbol: str, factor: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get indicator records for a symbol and factor."""
        pass

