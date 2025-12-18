"""Task adapters - thin wrappers for task queues."""

from .price_tasks import (
    fetch_price_task,
    store_price_task,
)
from .indicator_tasks import (
    compute_indicator_task,
    store_indicator_task,
)

__all__ = [
    "fetch_price_task",
    "store_price_task",
    "compute_indicator_task",
    "store_indicator_task",
]

