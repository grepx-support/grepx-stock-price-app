from datetime import datetime
from typing import Dict, List
import pandas as pd
import asyncio
import logging
from factors.calculation import FACTORS
from omegaconf import OmegaConf

logger = logging.getLogger(__name__)
cfg = OmegaConf.load("config/config.yaml")

def compute_single_factor(symbol: str, factor: str, records: List[Dict]) -> List[Dict]:
    if not records or factor not in FACTORS:
        logger.warning(f"Invalid input for {symbol}_{factor}")
        return []
    try:
        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date']).dt.date
        df = df.sort_values('date').reset_index(drop=True)
        
        factor_cols = FACTORS[factor](df)
        for col_name, col_data in factor_cols.items():
            df[col_name] = col_data
        
        results = [{
            "symbol": symbol,
            "date": str(row['date']),
            "factor": factor,
            **{k: (float(row[k]) if pd.notna(row[k]) else "no data available") for k in factor_cols.keys()}
        } for _, row in df.iterrows()]
        
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