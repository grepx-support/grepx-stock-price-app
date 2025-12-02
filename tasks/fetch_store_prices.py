from celery_framework.tasks.decorators import task
import logging
import pandas as pd

from db.MongoDBConnection import MongoDBConnection
from db.MongoDBManager import MongoDBManager
from utils import load_data_source, fetch_price_data, get_collection_name, clean_rows

logger = logging.getLogger(__name__)

MongoDBConnection.connect()
MongoDBManager.create_indexes()


@task(name="tasks.fetch_store_prices")
def fetch_store_prices(symbol: str, start_date: str, end_date: str | None, source: str):
    """Generic multi-source fetch + store task."""

    logger.info(f"[Celery] Fetching {symbol} from {source}")

    # Load Data Source
    try:
        api_class = load_data_source(source)
        api = api_class(symbol)
    except ValueError as e:
        logger.error(str(e))
        return {"status": "error", "symbol": symbol}

    # Fetch data
    df: pd.DataFrame = fetch_price_data(api, symbol, start_date, end_date)

    if df.empty:
        logger.warning(f"No data returned for {symbol}")
        return {"status": "no_data", "symbol": symbol}

    # Store in MongoDB
    collection = get_collection_name(symbol)
    logger.info(f"Storing rows in collection: {collection}")

    rows = df.to_dict("records")
    cleaned_rows = clean_rows(rows, symbol, source)
    success = MongoDBManager.bulk_insert(collection, cleaned_rows)

    return {
        "status": "success" if success else "error",
        "symbol": symbol,
        "rows": len(rows),
        "collection": collection
    }