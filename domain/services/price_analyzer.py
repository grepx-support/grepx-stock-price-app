"""Price analysis business rules."""

from typing import List
from domain.models.price import PriceData
from domain.exceptions import InvalidPriceDataError


class PriceAnalyzer:
    """Business rules for price analysis."""

    @staticmethod
    def validate_price_data(price_data: PriceData) -> bool:
        """Validate price data according to business rules."""
        if not price_data.symbol:
            raise InvalidPriceDataError("Symbol is required")
        if price_data.ohlcv.volume < 0:
            raise InvalidPriceDataError("Volume cannot be negative")
        return True

    @staticmethod
    def calculate_price_change(current: PriceData, previous: PriceData) -> float:
        """Calculate percentage price change."""
        if current.symbol != previous.symbol:
            raise InvalidPriceDataError("Cannot compare prices from different symbols")
        if previous.ohlcv.close == 0:
            raise InvalidPriceDataError("Previous close price cannot be zero")
        return ((current.ohlcv.close - previous.ohlcv.close) / previous.ohlcv.close) * 100

    @staticmethod
    def is_valid_price_sequence(prices: List[PriceData]) -> bool:
        """Validate that prices are in chronological order."""
        if len(prices) < 2:
            return True
        
        for i in range(1, len(prices)):
            if prices[i].date < prices[i-1].date:
                return False
        return True

