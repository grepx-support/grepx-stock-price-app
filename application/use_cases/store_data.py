"""Use case: Store price and indicator data."""

from typing import List, Dict, Any
from application.dto import StoreResultDTO
from application.ports.repositories import IPriceRepository, IIndicatorRepository


class StoreDataUseCase:
    """Use case for storing data."""

    def __init__(
        self,
        price_repository: IPriceRepository = None,
        indicator_repository: IIndicatorRepository = None
    ):
        self.price_repository = price_repository
        self.indicator_repository = indicator_repository

    async def store_prices(self, price_records: List[Dict[str, Any]]) -> StoreResultDTO:
        """
        Store price records.
        
        Args:
            price_records: List of price records to store
        
        Returns:
            StoreResultDTO with store operation result
        """
        if not self.price_repository:
            return StoreResultDTO(
                status="failed",
                stored=0,
                total=len(price_records),
                error="Price repository not configured"
            )
        
        if not price_records:
            return StoreResultDTO(status="no_data", stored=0, total=0)
        
        try:
            stored = await self.price_repository.save_prices(price_records)
            return StoreResultDTO(
                status="success",
                stored=stored,
                total=len(price_records)
            )
        except Exception as e:
            return StoreResultDTO(
                status="failed",
                stored=0,
                total=len(price_records),
                error=str(e)
            )

    async def store_indicators(self, indicator_records: List[Dict[str, Any]]) -> StoreResultDTO:
        """
        Store indicator records.
        
        Args:
            indicator_records: List of indicator records to store
        
        Returns:
            StoreResultDTO with store operation result
        """
        if not self.indicator_repository:
            return StoreResultDTO(
                status="failed",
                stored=0,
                total=len(indicator_records),
                error="Indicator repository not configured"
            )
        
        if not indicator_records:
            return StoreResultDTO(status="no_data", stored=0, total=0)
        
        try:
            stored = await self.indicator_repository.save_indicators(indicator_records)
            return StoreResultDTO(
                status="success",
                stored=stored,
                total=len(indicator_records)
            )
        except Exception as e:
            return StoreResultDTO(
                status="failed",
                stored=0,
                total=len(indicator_records),
                error=str(e)
            )

