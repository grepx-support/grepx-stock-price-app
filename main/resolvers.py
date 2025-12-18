"""Dependency resolvers - create and wire dependencies."""

from typing import Optional

from application.use_cases import (
    FetchPricesUseCase,
    ComputeIndicatorsUseCase,
    StoreDataUseCase,
)
from application.ports.repositories import IPriceRepository, IIndicatorRepository
from application.ports.data_sources import IMarketDataSource
from application.ports.task_queue import ITaskQueue

from infrastructure.data_sources.data_source_factory import DataSourceFactory
from infrastructure.task_queues.task_queue_factory import TaskQueueFactory
from infrastructure.repositories.repository_factory import RepositoryFactory
from infrastructure.services.naming_service import naming_service

from config.settings import settings


class DependencyResolver:
    """Resolves dependencies using factories and services."""
    
    def __init__(self, container):
        """Initialize with container reference."""
        self.container = container
    
    def resolve_data_source(self, source_type: str = "yahoo") -> IMarketDataSource:
        """Resolve market data source."""
        return DataSourceFactory.create(source_type)
    
    def resolve_task_queue(self, queue_type: str = "celery") -> ITaskQueue:
        """Resolve task queue."""
        config = {"celery_app": self.container.celery_app} if queue_type == "celery" else {}
        return TaskQueueFactory.create(queue_type, config)
    
    def resolve_price_repository(
        self,
        asset_type: str,
        symbol: str,
        repository_type: str = "mongo"
    ) -> IPriceRepository:
        """Resolve price repository."""
        db_name = naming_service.get_analysis_db_name(asset_type)
        collection_name = naming_service.get_price_collection_name(asset_type, symbol)
        collection = self.container.get_collection(db_name, collection_name)
        return RepositoryFactory.create_price_repository(collection, repository_type)
    
    def resolve_indicator_repository(
        self,
        asset_type: str,
        symbol: str,
        factor: str,
        repository_type: str = "mongo"
    ) -> IIndicatorRepository:
        """Resolve indicator repository."""
        db_name = naming_service.get_analysis_db_name(asset_type)
        collection_name = naming_service.get_indicator_collection_name(asset_type, symbol, factor)
        collection = self.container.get_collection(db_name, collection_name)
        return RepositoryFactory.create_indicator_repository(collection, repository_type)
    
    def resolve_fetch_prices_use_case(self) -> FetchPricesUseCase:
        """Resolve fetch prices use case."""
        data_source = self.container.get_data_source()
        return FetchPricesUseCase(data_source)
    
    def resolve_compute_indicators_use_case(self) -> ComputeIndicatorsUseCase:
        """Resolve compute indicators use case."""
        missing_value_text = settings.get_domain("factors.missing_value.text", "no data available")
        return ComputeIndicatorsUseCase(
            price_repository=None,  # Not needed for execute_from_records
            missing_value_text=missing_value_text
        )
    
    def resolve_store_data_use_case(
        self,
        asset_type: str,
        symbol: str,
        factor: Optional[str] = None
    ) -> StoreDataUseCase:
        """Resolve store data use case."""
        price_repo = self.container.get_price_repository(asset_type, symbol)
        indicator_repo = None
        if factor:
            indicator_repo = self.container.get_indicator_repository(asset_type, symbol, factor)
        return StoreDataUseCase(price_repository=price_repo, indicator_repository=indicator_repo)

