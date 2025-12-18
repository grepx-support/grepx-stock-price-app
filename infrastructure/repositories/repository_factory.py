"""Factory for creating repository instances - Strategy pattern."""

from typing import Dict, Any, Optional
from application.ports.repositories import IPriceRepository, IIndicatorRepository
from infrastructure.repositories.mongo_price_repo import MongoPriceRepository
from infrastructure.repositories.mongo_indicator_repo import MongoIndicatorRepository
from infrastructure.services.naming_service import naming_service
import logging

logger = logging.getLogger(__name__)


class RepositoryFactory:
    """Factory for creating repository instances."""

    @staticmethod
    def create_price_repository(
        collection,
        repository_type: str = "mongo"
    ) -> IPriceRepository:
        """
        Create a price repository instance.
        
        Args:
            collection: Database collection object
            repository_type: Type of repository ("mongo", "postgres", etc.)
        
        Returns:
            IPriceRepository instance
        """
        if repository_type.lower() == "mongo":
            return MongoPriceRepository(collection)
        else:
            raise ValueError(f"Unknown repository type: {repository_type}")

    @staticmethod
    def create_indicator_repository(
        collection,
        repository_type: str = "mongo"
    ) -> IIndicatorRepository:
        """
        Create an indicator repository instance.
        
        Args:
            collection: Database collection object
            repository_type: Type of repository ("mongo", "postgres", etc.)
        
        Returns:
            IIndicatorRepository instance
        """
        if repository_type.lower() == "mongo":
            return MongoIndicatorRepository(collection)
        else:
            raise ValueError(f"Unknown repository type: {repository_type}")

    @staticmethod
    def create_price_repository_for_asset(
        database,
        asset_type: str,
        symbol: str,
        repository_type: str = "mongo"
    ) -> IPriceRepository:
        """
        Create a price repository for a specific asset.
        
        Args:
            database: Database object
            asset_type: Asset type (stocks, indices, futures)
            symbol: Symbol name
            repository_type: Type of repository
        
        Returns:
            IPriceRepository instance
        """
        db_name = naming_service.get_analysis_db_name(asset_type)
        collection_name = naming_service.get_price_collection_name(asset_type, symbol)
        collection = database[db_name][collection_name]
        return RepositoryFactory.create_price_repository(collection, repository_type)

    @staticmethod
    def create_indicator_repository_for_asset(
        database,
        asset_type: str,
        symbol: str,
        factor: str,
        repository_type: str = "mongo"
    ) -> IIndicatorRepository:
        """
        Create an indicator repository for a specific asset and factor.
        
        Args:
            database: Database object
            asset_type: Asset type (stocks, indices, futures)
            symbol: Symbol name
            factor: Indicator factor name
            repository_type: Type of repository
        
        Returns:
            IIndicatorRepository instance
        """
        db_name = naming_service.get_analysis_db_name(asset_type)
        collection_name = naming_service.get_indicator_collection_name(asset_type, symbol, factor)
        collection = database[db_name][collection_name]
        return RepositoryFactory.create_indicator_repository(collection, repository_type)

