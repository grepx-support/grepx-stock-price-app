# # price_app/tasks/indicator_tasks.py
# from celery import shared_task
# from services.indicator_services import compute_all_indicators
# import logging
# import asyncio

# logger = logging.getLogger(__name__)

# @shared_task(name="tasks.indicator_tasks.compute_indicators", bind=True, max_retries=2)
# def compute_indicators_task(self, symbol: str, price_records: list):
#     try:
#         return compute_all_indicators(symbol, price_records)
#     except Exception as e:
#         logger.error(f"Indicator computation failed for {symbol}: {e}")
#         raise self.retry(exc=e, countdown=10)

# @shared_task(name="tasks.indicator_tasks.store_indicators", bind=True)
# def store_indicators_task(self, indicator_data: list, collection_name: str):
#     try:
#         from app.main import orm_app
#         collection = orm_app.get_collection(collection_name)
        
#         async def _store():
#             for record in indicator_data:
#                 await collection.update_one(
#                     {"symbol": record["symbol"], "date": record["date"]},
#                     {"$set": record},
#                     upsert=True
#                 )
        
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(_store())
#         return {"status": "success", "stored": len(indicator_data)}
#     except Exception as e:
#         raise self.retry(exc=e)

# price_app/tasks/indicator_tasks.py
from celery import shared_task
from services.indicator_services import compute_single_factor, store_single_factor
import logging

logger = logging.getLogger(__name__)

@shared_task(name="tasks.indicator_tasks.compute", bind=True, max_retries=2)
def compute(self, symbol, factor, price_records):
    """Compute single factor for symbol"""
    try:
        logger.info(f"Computing {factor} for {symbol}")
        result = compute_single_factor(symbol, factor, price_records)
        logger.info(f"Computed {factor} for {symbol}: {len(result)} records")
        return result
    except Exception as e:
        logger.error(f"Error computing {factor} for {symbol}: {e}")
        raise self.retry(exc=e, countdown=10)

@shared_task(name="tasks.indicator_tasks.store", bind=True, max_retries=2)
def store(self, symbol, factor, factor_data):
    """Store computed factor data to MongoDB"""
    try:
        from app.main import orm_app
        collection = orm_app.get_collection(f"{symbol.lower()}_{factor.lower()}")
        logger.info(f"Storing {factor} for {symbol}")
        result = store_single_factor(factor_data, collection)
        logger.info(f"Stored {factor} for {symbol}: {result['stored']} records")
        return result
    except Exception as e:
        logger.error(f"Error storing {factor} for {symbol}: {e}")
        raise self.retry(exc=e, countdown=5)