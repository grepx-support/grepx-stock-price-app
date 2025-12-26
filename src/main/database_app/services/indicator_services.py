"""Indicator services - refactored to be concise and maintainable."""
from typing import Dict, List
import polars as pl
import pandas as pd
import asyncio
import logging
from servers.factors.calculation import FACTORS
from servers.factors.types import MissingValueConfig
from servers.factors.config import cfg
from database_app.database_helpers import get_or_create_loop, get_sqlite_session, get_postgresql_session, create_table_if_needed

logger = logging.getLogger(__name__)
MISSING_VALUE = MissingValueConfig(text=cfg.factors.missing_value.text, numeric=cfg.factors.missing_value.numeric)


def compute_single_factor(symbol: str, factor: str, records: List[Dict], indicator_config=None) -> List[Dict]:
    """Compute single factor with Polars"""
    if not records or factor not in FACTORS:
        return []

    df = pl.DataFrame(records).with_columns(pl.col('date').cast(pl.Date)).sort('date')
    factor_cols = FACTORS[factor](df.to_pandas())
    factor_col_names = list(factor_cols.keys())

    for col_name, col_data in factor_cols.items():
        df = df.with_columns(pl.Series(col_name, col_data))

    for col in factor_col_names:
        df = df.with_columns(pl.when(pl.col(col).is_null() | pl.col(col).is_nan()).then(pl.lit(MISSING_VALUE.text)).otherwise(pl.col(col).cast(pl.Utf8)).alias(col))

    df = df.with_columns([pl.lit(symbol).alias('symbol'), pl.lit(factor).alias('factor'), pl.col('date').cast(pl.Utf8)])
    return df.select(['symbol', 'date'] + factor_col_names + ['factor']).to_dicts()


class RecordModel:
    """Simple model for bulk upsert operations."""
    _table_name = None

    def __init__(self, data, table_name=None):
        self.data = data
        if table_name:
            RecordModel._table_name = table_name

    @classmethod
    def get_table_name(cls):
        return cls._table_name

    def to_dict(self):
        return self.data


async def _store_async(records: List[Dict], session, db_name: str, collection_name: str, key_fields: List[str] = None) -> int:
    """Store records using ORM's bulk_upsert (database-agnostic)"""
    if not records or key_fields is None:
        key_fields = ['symbol', 'date', 'factor']

    backend = session.backend
    sqlite_session = postgres_session = None

    try:
        if hasattr(backend, 'backend_name'):
            if backend.backend_name == 'sqlite':
                sqlite_session = await get_sqlite_session(db_name)
                session, backend = sqlite_session, sqlite_session.backend
                await create_table_if_needed(backend, collection_name, records, True)
            elif backend.backend_name == 'mongodb' and hasattr(backend, 'client'):
                backend.database = backend.client[db_name]
            elif backend.backend_name == 'postgresql':
                postgres_session = await get_postgresql_session(db_name)
                session, backend = postgres_session, postgres_session.backend
                await create_table_if_needed(backend, collection_name, records)

        # Set table name on model before bulk_upsert
        RecordModel._table_name = collection_name
        inserted = await session.bulk_upsert(RecordModel, records, key_fields=key_fields, batch_size=100)
        return inserted
    except Exception as e:
        logger.error(f"Failed to bulk upsert: {e}")
        return 0
    finally:
        for s in [sqlite_session, postgres_session]:
            if s:
                try:
                    await s.__aexit__(None, None, None)
                except:
                    pass


def store_single_factor(factor_data: List[Dict], session, db_name: str, collection_name: str) -> Dict:
    """Store factor data synchronously"""
    if not factor_data:
        return {"status": "no_data", "stored": 0}

    try:
        stored = get_or_create_loop().run_until_complete(_store_async(factor_data, session, db_name, collection_name))
        return {"status": "success", "stored": stored, "total": len(factor_data)}
    except Exception as e:
        logger.error(f"Error storing factor data: {str(e)}")
        return {"status": "failed", "stored": 0, "error": str(e)}
