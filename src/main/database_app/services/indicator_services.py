from datetime import datetime
from typing import Dict, List
import polars as pl
import pandas as pd
import asyncio
import logging
from factors.calculation import FACTORS
from factors.types import MissingValueConfig
from factors.config import cfg

logger = logging.getLogger(__name__)


MISSING_VALUE = MissingValueConfig(
    text=cfg.factors.missing_value.text,
    numeric=cfg.factors.missing_value.numeric
)

def compute_single_factor(symbol: str, factor: str, records: List[Dict],  indicator_config=None) -> List[Dict]:
    """Compute single factor with Polars"""
    if not records or factor not in FACTORS:
        logger.warning(f"Invalid input for {symbol}_{factor}")
        return []
    try:
        df = pl.DataFrame(records)
        df = df.with_columns(pl.col('date').cast(pl.Date)).sort('date')

        df_pandas = df.to_pandas()
        factor_cols = FACTORS[factor](df_pandas)
        factor_col_names = list(factor_cols.keys())

        for col_name, col_data in factor_cols.items():
            df = df.with_columns(pl.Series(col_name, col_data))

        for col in factor_col_names:
            df = df.with_columns(
                pl.when(pl.col(col).is_null() | pl.col(col).is_nan()).then(pl.lit(MISSING_VALUE.text)).otherwise(pl.col(col).cast(pl.Utf8)).alias(col)
            )
        df = df.with_columns([
            pl.lit(symbol).alias('symbol'),
            pl.lit(factor).alias('factor'),
            pl.col('date').cast(pl.Utf8).alias('date')
        ])

        results = df.select(['symbol', 'date'] + factor_col_names + ['factor']).to_dicts()
        logger.info(f"Computed {factor} for {symbol}: {len(results)} records")
        return results
    except Exception as e:
        logger.error(f"Error computing {factor} for {symbol}: {str(e)}")
        raise

async def _store_async(records: List[Dict], collection) -> int:
    inserted = 0
    for rec in records:
        try:
            await collection.update_one({"symbol": rec["symbol"], "date": rec["date"]}, {"$set": rec}, upsert=True)
            inserted += 1
        except Exception as e:
            logger.warning(f"Failed to store {rec.get('symbol')}_{rec.get('date')}: {e}")
    return inserted

def store_single_factor(factor_data: List[Dict], collection) -> Dict:
    if not factor_data:
        return {"status": "no_data", "stored": 0}
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        stored = loop.run_until_complete(_store_async(factor_data, collection))
        return {"status": "success", "stored": stored, "total": len(factor_data)}
    except Exception as e:
        logger.error(f"Error storing factor data: {str(e)}")
        return {"status": "failed", "stored": 0, "error": str(e)}