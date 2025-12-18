"""Dependency Injection Container - Sandbox pattern."""

from pathlib import Path
import threading
from typing import Optional, Dict, Any

from .setup import setup_paths
from .factories import FrameworkFactory
from .resolvers import DependencyResolver

from application.ports.repositories import IPriceRepository, IIndicatorRepository
from application.ports.data_sources import IMarketDataSource
from application.ports.task_queue import ITaskQueue
from application.use_cases import (
    FetchPricesUseCase,
    ComputeIndicatorsUseCase,
    StoreDataUseCase,
)


class DependencyContainer:
    """
    Dependency Injection Container - Sandbox pattern.
    
    Provides a controlled environment where dependencies are registered,
    resolved, and managed with lazy loading and caching.
    """
    
    def __init__(self):
        """Initialize container with lazy loading."""
        self._lock = threading.Lock()
        self._resolver = DependencyResolver(self)
        
        # Framework instances (lazy-loaded)
        self._celery_app = None
        self._dagster_defs = None
        self._orm_session = None
        
        # Service instances (lazy-loaded)
        self._data_source = None
        self._task_queue = None
        
        # Cache for collections and repositories
        self._collections: Dict[tuple, Any] = {}
    
    # ========================================================================
    # Framework Properties (Lazy Loading)
    # ========================================================================
    
    @property
    def celery_app(self):
        """Get Celery app (lazy initialization)."""
        if self._celery_app is None:
            with self._lock:
                if self._celery_app is None:
                    self._celery_app = FrameworkFactory.create_celery_app()
        return self._celery_app
    
    @property
    def dagster_defs(self):
        """Get Dagster definitions (lazy initialization)."""
        if self._dagster_defs is None:
            with self._lock:
                if self._dagster_defs is None:
                    ROOT = Path(__file__).parent.parent
                    config_dir = ROOT / "config"
                    self._dagster_defs = FrameworkFactory.create_dagster_defs(config_dir)
        return self._dagster_defs
    
    @property
    def orm_session(self):
        """Get ORM session (lazy initialization)."""
        if self._orm_session is None:
            with self._lock:
                if self._orm_session is None:
                    self._orm_session = FrameworkFactory.create_orm_session()
        return self._orm_session
    
    # ========================================================================
    # Database Access Methods
    # ========================================================================
    
    def get_database(self, db_name: str):
        """Get a database by name."""
        client = self.orm_session.backend.client
        return client[db_name]
    
    def get_collection(self, db_name: str, collection_name: str):
        """Get a collection by database and collection name (cached)."""
        cache_key = (db_name, collection_name)
        if cache_key not in self._collections:
            db = self.get_database(db_name)
            self._collections[cache_key] = db[collection_name]
        return self._collections[cache_key]
    
    # ========================================================================
    # Service Resolution Methods
    # ========================================================================
    
    def get_data_source(self, source_type: str = "yahoo") -> IMarketDataSource:
        """Get market data source (Strategy pattern - easy to swap)."""
        if self._data_source is None:
            self._data_source = self._resolver.resolve_data_source(source_type)
        return self._data_source
    
    def get_task_queue(self, queue_type: str = "celery") -> ITaskQueue:
        """Get task queue (Strategy pattern - easy to swap Celery ↔ Prefect)."""
        if self._task_queue is None:
            self._task_queue = self._resolver.resolve_task_queue(queue_type)
        return self._task_queue
    
    # ========================================================================
    # Repository Resolution Methods
    # ========================================================================
    
    def get_price_repository(
        self,
        asset_type: str,
        symbol: str,
        repository_type: str = "mongo"
    ) -> IPriceRepository:
        """Get price repository (Strategy pattern - easy to swap MongoDB ↔ PostgreSQL)."""
        return self._resolver.resolve_price_repository(asset_type, symbol, repository_type)
    
    def get_indicator_repository(
        self,
        asset_type: str,
        symbol: str,
        factor: str,
        repository_type: str = "mongo"
    ) -> IIndicatorRepository:
        """Get indicator repository (Strategy pattern - easy to swap MongoDB ↔ PostgreSQL)."""
        return self._resolver.resolve_indicator_repository(asset_type, symbol, factor, repository_type)
    
    # ========================================================================
    # Use Case Resolution Methods
    # ========================================================================
    
    def get_fetch_prices_use_case(self) -> FetchPricesUseCase:
        """Get fetch prices use case."""
        return self._resolver.resolve_fetch_prices_use_case()
    
    def get_compute_indicators_use_case(self) -> ComputeIndicatorsUseCase:
        """Get compute indicators use case."""
        return self._resolver.resolve_compute_indicators_use_case()
    
    def get_store_data_use_case(
        self,
        asset_type: str,
        symbol: str,
        factor: Optional[str] = None
    ) -> StoreDataUseCase:
        """Get store data use case."""
        return self._resolver.resolve_store_data_use_case(asset_type, symbol, factor)


# ============================================================================
# Global Container Instance
# ============================================================================

_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get or create the global container instance (singleton)."""
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container

