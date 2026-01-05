import logging
import sys
from pathlib import Path

# Ensure src/main is in path for Celery worker import context
src_main_path = Path(__file__).resolve().parent.parent.parent
if str(src_main_path) not in sys.path:
    sys.path.insert(0, str(src_main_path))

# Ensure ORM library is in path BEFORE importing anything that uses it
orm_path = src_main_path.parent.parent / "libs" / "grepx-orm-libs" / "src"
if str(orm_path) not in sys.path:
    sys.path.insert(0, str(orm_path))

from celery import shared_task

logger = logging.getLogger(__name__)

class TaskFactory:
    """Factory to create fetch/store/compute/store indicator tasks"""
    
    @staticmethod
    def create_fetch_task(service_func, asset_type: str):
        """Create a fetch task"""
        def fetch_task(self, symbol, start_date=None, end_date=None):
            try:
                logger.info(f"[{asset_type.upper()}] Fetching {symbol}")
                result = service_func(symbol, start_date, end_date)
                logger.info(f"[{asset_type.upper()}] Fetched {symbol}: {len(result.get('records', []))} records")
                return result
            except Exception as exc:
                logger.error(f"[{asset_type.upper()}] Fetch error for {symbol}: {exc}")
                raise self.retry(exc=exc, countdown=2 ** self.request.retries)
        
        return fetch_task
    
    @staticmethod
    def create_store_task(service_func, asset_type: str):
        """Create a store price task"""
        def store_task(self, price_data, symbol):
            try:
                from main import get_app
                from database_app.services.naming import naming

                db_name = naming.get_analysis_db_name(asset_type)
                if not db_name or db_name.strip() == "":
                    raise ValueError(f"Database name is empty for asset_type: {asset_type}")

                collection_name = naming.get_price_collection_name(asset_type, symbol)
                if not collection_name or collection_name.strip() == "":
                    raise ValueError(f"Collection name is empty for symbol: {symbol}")

                logger.debug(f"[{asset_type.upper()}] Getting session for: {db_name}.{collection_name}")

                # Get the application and its ORM session
                app = get_app()
                conn = app.get_connection('primary_db')
                session = conn._session

                logger.info(f"[{asset_type.upper()}] Storing {symbol} to {db_name}.{collection_name}")
                # Pass session, db_name, and collection_name for proper database routing
                result = service_func(price_data, session, db_name, collection_name)
                logger.info(f"[{asset_type.upper()}] Stored {symbol}: {result.get('stored', 0)} records")
                return result
            except Exception as exc:
                logger.error(f"[{asset_type.upper()}] Store error for {symbol}: {exc}", exc_info=True)
                raise self.retry(exc=exc, countdown=2 ** self.request.retries)

        return store_task
    
    @staticmethod
    def create_compute_task(service_func, asset_type: str):
        """Create a compute indicator task"""
        def compute_task(self, symbol, factor, price_records, indicator_config):
            try:
                logger.info(f"[{asset_type.upper()}] Computing {factor} for {symbol}")
                result = service_func(symbol, factor, price_records, indicator_config)
                logger.info(f"[{asset_type.upper()}] Computed {factor} for {symbol}: {len(result)} records")
                return result
            except Exception as e:
                logger.error(f"[{asset_type.upper()}] Compute error for {symbol}_{factor}: {e}")
                raise self.retry(exc=e, countdown=10)
        
        return compute_task
    
    @staticmethod
    def create_store_indicator_task(service_func, asset_type: str):
        def store_task(self, symbol, factor, factor_data):
            try:
                from main import get_app
                from database_app.services.naming import naming
                from core import Session

                db_name = naming.get_analysis_db_name(asset_type)
                if not db_name or db_name.strip() == "":
                    raise ValueError(f"Database name is empty for asset_type: {asset_type}")

                collection_name = naming.get_indicator_collection_name(asset_type, symbol, factor)
                if not collection_name or collection_name.strip() == "":
                    raise ValueError(f"Collection name is empty for {symbol}/{factor}")

                logger.debug(f"[{asset_type.upper()}] Getting session for: {db_name}.{collection_name}")

                # Get the application and its ORM session
                app = get_app()
                conn = app.get_connection('primary_db')
                session = conn._session

                logger.info(f"[{asset_type.upper()}] Storing {factor} for {symbol} → {db_name}.{collection_name}")

                # Pass session, db_name, and collection_name for proper database routing
                result = service_func(factor_data, session, db_name, collection_name)
                logger.info(f"[{asset_type.upper()}] Stored {factor} for {symbol}: {result.get('stored', 0)}")
                return result
            except Exception as e:
                logger.error(f"[{asset_type.upper()}] Indicator store error for {symbol}_{factor}: {e}", exc_info=True)
                raise self.retry(exc=e, countdown=5)

        return store_task