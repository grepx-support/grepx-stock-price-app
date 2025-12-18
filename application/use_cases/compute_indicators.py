"""Use case: Compute indicators from price data."""

from typing import List, Dict, Any
from application.dto import IndicatorResultDTO
from application.ports.repositories import IPriceRepository
from domain.services.indicator_calculator import IndicatorCalculator


class ComputeIndicatorsUseCase:
    """Use case for computing technical indicators."""

    def __init__(
        self,
        price_repository: IPriceRepository,
        missing_value_text: str = "no data available"
    ):
        self.price_repository = price_repository
        self.missing_value_text = missing_value_text

    async def execute(
        self,
        symbol: str,
        indicator_name: str,
        parameters: Dict[str, Any],
        start_date: str = None,
        end_date: str = None
    ) -> IndicatorResultDTO:
        """
        Compute indicator for a symbol.
        
        Args:
            symbol: Symbol to compute indicator for
            indicator_name: Name of the indicator (SMA, EMA, RSI, etc.)
            parameters: Indicator-specific parameters
            start_date: Start date for price data (optional)
            end_date: End date for price data (optional)
        
        Returns:
            IndicatorResultDTO with computed values
        """
        # Fetch price data
        price_records = await self.price_repository.get_prices(symbol, start_date, end_date)
        
        if not price_records:
            return IndicatorResultDTO(
                symbol=symbol,
                factor=indicator_name,
                records=[],
                count=0
            )
        
        # Compute indicator
        results = IndicatorCalculator.compute_indicator(
            symbol=symbol,
            indicator_name=indicator_name,
            price_records=price_records,
            parameters=parameters,
            missing_value_text=self.missing_value_text
        )
        
        return IndicatorResultDTO(
            symbol=symbol,
            factor=indicator_name,
            records=results,
            count=len(results)
        )

    def execute_from_records(
        self,
        symbol: str,
        indicator_name: str,
        price_records: List[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> IndicatorResultDTO:
        """
        Compute indicator directly from price records (no repository fetch).
        
        Args:
            symbol: Symbol name
            indicator_name: Name of the indicator
            price_records: List of price records
            parameters: Indicator-specific parameters
        
        Returns:
            IndicatorResultDTO with computed values
        """
        results = IndicatorCalculator.compute_indicator(
            symbol=symbol,
            indicator_name=indicator_name,
            price_records=price_records,
            parameters=parameters,
            missing_value_text=self.missing_value_text
        )
        
        return IndicatorResultDTO(
            symbol=symbol,
            factor=indicator_name,
            records=results,
            count=len(results)
        )

