"""Prefect app."""

from grepx_connection_registry import ConnectionFactory

try:
    from .prefect_connection import PrefectConnection
    ConnectionFactory.register('prefect', PrefectConnection)
    __all__ = ["PrefectConnection"]
except ImportError as e:
    if "prefect_framework" in str(e):
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Prefect framework not available: {e}. Prefect connection will be disabled.")
        __all__ = []
    else:
        raise