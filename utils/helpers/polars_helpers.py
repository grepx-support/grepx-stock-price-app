"""Polars DataFrame helper functions for price_app."""

import logging
from typing import Any
from utils.db_utils import find_all, bulk_upsert
from dagster_framework import PolarsConverter

logger = logging.getLogger(__name__)


def fetch_collection_as_dataframe(
    collection: str,
    lazy: bool = False
) -> Any:
    """Fetch MongoDB collection as Polars DataFrame.

    Args:
        collection: Collection name.
        lazy: Return LazyFrame for lazy evaluation.

    Returns:
        Polars DataFrame or LazyFrame.

    Raises:
        ValueError: If collection is empty.
    """
    documents = find_all(collection)

    if not documents:
        raise ValueError(f"No documents found in collection: {collection}")

    df = PolarsConverter.from_records(documents)
    df = PolarsConverter.remove_id_field(df)

    logger.debug(f"Fetched {len(df)} rows from {collection}")

    if lazy:
        return df.lazy()

    return df


def store_dataframe_to_collection(
    df: Any,
    collection: str
) -> int:
    """Store Polars DataFrame to MongoDB collection.

    Args:
        df: Polars DataFrame or LazyFrame.
        collection: Collection name.

    Returns:
        Number of inserted documents.
    """
    if hasattr(df, 'collect'):
        df = df.collect()

    records = PolarsConverter.to_records(df)
    inserted_count = bulk_upsert(collection, records)

    logger.info(f"Stored {inserted_count} rows to {collection}")
    return inserted_count


def merge_dataframes(
    left: Any,
    right: Any,
    on: str,
    how: str = "inner"
) -> Any:
    """Merge two DataFrames on a key.

    Args:
        left: Left DataFrame.
        right: Right DataFrame.
        on: Join key column name.
        how: Join type (inner, left, right, outer).

    Returns:
        Merged DataFrame.
    """
    result = left.join(right, on=on, how=how)
    logger.debug(f"Merged DataFrames on {on} with {how} join")
    return result
