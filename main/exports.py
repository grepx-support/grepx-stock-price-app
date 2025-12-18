"""Backward compatibility exports and convenience functions."""

from typing import Optional

from .container import get_container
from application.use_cases import (
    FetchPricesUseCase,
    ComputeIndicatorsUseCase,
    StoreDataUseCase,
)


# ============================================================================
# Framework Exports (for Celery, Dagster CLI)
# ============================================================================

# Get container instance
_container_instance = get_container()

# Expose for Celery CLI - must be the actual Celery app instance
# Celery CLI requires direct access to the app, not a proxy
app = _container_instance.celery_app

# Expose for Dagster (lazy-loaded property)
class _DagsterDefsProxy:
    """Proxy for Dagster defs to enable lazy loading."""
    def __getattr__(self, name):
        return getattr(_container_instance.dagster_defs, name)

defs = _DagsterDefsProxy()


# ============================================================================
# ORM App Wrapper (Backward Compatibility)
# ============================================================================

class ORMApp:
    """Backward compatibility wrapper for ORM access."""
    
    def get_database(self, db_name: str):
        """Get a database by name."""
        return _container_instance.get_database(db_name)
    
    def get_collection(self, db_name: str, collection_name: str):
        """Get a collection by database and collection name."""
        return _container_instance.get_collection(db_name, collection_name)


orm_app = ORMApp()


# ============================================================================
# Convenience Functions for Task Adapters
# ============================================================================

def get_fetch_prices_use_case() -> FetchPricesUseCase:
    """Get fetch prices use case (for task adapters)."""
    return _container_instance.get_fetch_prices_use_case()


def get_compute_indicators_use_case() -> ComputeIndicatorsUseCase:
    """Get compute indicators use case (for task adapters)."""
    return _container_instance.get_compute_indicators_use_case()


def get_store_data_use_case(
    asset_type: str = "stocks",
    symbol: str = "",
    factor: Optional[str] = None
) -> StoreDataUseCase:
    """Get store data use case (for task adapters)."""
    # For backward compatibility, if symbol is empty, create a default one
    if not symbol:
        symbol = "PLACEHOLDER"
    return _container_instance.get_store_data_use_case(asset_type, symbol, factor)

