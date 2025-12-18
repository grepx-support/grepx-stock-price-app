"""Price data value objects."""

from dataclasses import dataclass
from datetime import date
from typing import Optional
from domain.exceptions import InvalidPriceDataError


@dataclass(frozen=True)
class OHLCV:
    """OHLCV value object - immutable price data."""
    open: float
    high: float
    low: float
    close: float
    volume: int

    def __post_init__(self):
        """Validate OHLCV data."""
        if self.high < self.low:
            raise InvalidPriceDataError("High cannot be less than low")
        if self.close < self.low or self.close > self.high:
            raise InvalidPriceDataError("Close must be between low and high")
        if self.open < self.low or self.open > self.high:
            raise InvalidPriceDataError("Open must be between low and high")
        if self.volume < 0:
            raise InvalidPriceDataError("Volume cannot be negative")


@dataclass(frozen=True)
class PriceData:
    """Price data value object for a specific date."""
    symbol: str
    date: date
    ohlcv: OHLCV
    fetched_at: Optional[str] = None

    def __post_init__(self):
        """Validate price data."""
        if not self.symbol or not self.symbol.strip():
            raise InvalidPriceDataError("Symbol cannot be empty")

