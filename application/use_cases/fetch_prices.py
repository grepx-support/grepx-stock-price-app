"""Use case: Fetch prices from market data source."""

from typing import Optional
import asyncio
from application.dto import FetchPricesResultDTO
from application.ports.data_sources import IMarketDataSource
from application.ports.repositories import IPriceRepository


class FetchPricesUseCase:
    """Use case for fetching and optionally storing prices."""

    def __init__(
        self,
        data_source: IMarketDataSource,
        price_repository: Optional[IPriceRepository] = None
    ):
        self.data_source = data_source
        self.price_repository = price_repository

    def execute(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        store: bool = False
    ) -> FetchPricesResultDTO:
        """
        Fetch prices for a symbol.
        
        Args:
            symbol: Symbol to fetch
            start_date: Start date (optional)
            end_date: End date (optional)
            store: Whether to store the fetched data
        
        Returns:
            FetchPricesResultDTO with fetched data
        """
        result = self.data_source.fetch_prices(symbol, start_date, end_date)
        
        if store and self.price_repository and result.status == "success":
            # Store asynchronously
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            loop.run_until_complete(
                self.price_repository.save_prices(result.records)
            )
        
        return result

