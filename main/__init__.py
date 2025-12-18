"""Main package - Composition Root and Dependency Injection."""

# Setup paths FIRST before any other imports
from .setup import setup_paths
setup_paths()

# Now import everything else
from .container import DependencyContainer, get_container
from .exports import (
    app,
    defs,
    orm_app,
    get_fetch_prices_use_case,
    get_compute_indicators_use_case,
    get_store_data_use_case,
)

__all__ = [
    "DependencyContainer",
    "get_container",
    "app",
    "defs",
    "orm_app",
    "get_fetch_prices_use_case",
    "get_compute_indicators_use_case",
    "get_store_data_use_case",
]

