"""Data Transfer Objects for application layer."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import date


@dataclass(frozen=True)
class ColumnMappings:
    """Column name mappings for price data - ensures consistent naming across data sources."""
    open: str = "open"
    high: str = "high"
    low: str = "low"
    close: str = "close"
    volume: str = "volume"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for backward compatibility."""
        return {
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


# Default column mappings instance
DEFAULT_COLUMN_MAPPINGS = ColumnMappings()


@dataclass
class PriceDataDTO:
    """DTO for price data."""
    symbol: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    fetched_at: Optional[str] = None


@dataclass
class FetchPricesResultDTO:
    """DTO for fetch prices result."""
    symbol: str
    records: List[Dict[str, Any]]
    count: int
    status: str
    error: Optional[str] = None


@dataclass
class IndicatorResultDTO:
    """DTO for indicator calculation result."""
    symbol: str
    factor: str
    records: List[Dict[str, Any]]
    count: int


@dataclass
class StoreResultDTO:
    """DTO for store operation result."""
    status: str
    stored: int
    total: int
    error: Optional[str] = None

