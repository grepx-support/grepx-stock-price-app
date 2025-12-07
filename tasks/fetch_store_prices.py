from celery_framework.tasks.decorators import task
import logging

from utils.db_utils import create_indexes
from utils.loaders.loaders import load_data_source
from utils.loaders.fetchers import fetch_price_data
from utils.loaders.cleaners import clean_rows, get_collection_name
from utils.helpers import store_dataframe_to_collection
from dagster_framework import PolarsConverter


logger = logging.getLogger(__name__)

# Initialize MongoDB connection and indexes
create_indexes()


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
    pandas_df = fetch_price_data(api, symbol, start_date, end_date)

    if pandas_df.empty:
        logger.warning(f"No data returned for {symbol}")
        return {"status": "no_data", "symbol": symbol}

    # Convert to Polars using framework converter
    df = PolarsConverter.from_pandas(pandas_df)

    # Clean rows
    rows = PolarsConverter.to_records(df)
    cleaned_rows = clean_rows(rows, symbol, source)
    df_cleaned = PolarsConverter.from_records(cleaned_rows)

    # Store in MongoDB
    collection = get_collection_name(symbol)
    logger.info(f"Storing {len(df_cleaned)} rows to {collection}")

    inserted = store_dataframe_to_collection(df_cleaned, collection)

    return {
        "status": "success" if inserted > 0 else "error",
        "symbol": symbol,
        "rows": inserted,
        "collection": collection
    }
