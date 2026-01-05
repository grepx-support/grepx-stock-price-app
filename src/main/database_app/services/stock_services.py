"""Stock services - refactored to be concise and maintainable."""
import yfinance as yf
from datetime import datetime
from typing import Dict
import logging
from database_app.database_helpers import get_or_create_loop, get_sqlite_session, get_postgresql_session, create_table_if_needed

logger = logging.getLogger(__name__)


def fetch_stock_price_data(symbol: str, start_date: str = None, end_date: str = None) -> Dict:
    """Fetch stock prices from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(start=start_date, end=end_date)
        records = [{
            "symbol": symbol,
            "date": str(date.date()),
            "open": float(row['Open']),
            "high": float(row['High']),
            "low": float(row['Low']),
            "close": float(row['Close']),
            "volume": int(row['Volume']),
            "fetched_at": datetime.now().isoformat(),
        } for date, row in data.iterrows()]
        return {"symbol": symbol, "records": records, "count": len(records), "status": "success"}
    except Exception as e:
        return {"symbol": symbol, "records": [], "count": 0, "status": "error", "error": str(e)}


class PriceModel:
    """Simple model for bulk upsert operations."""
    _table_name = None

    def __init__(self, data, table_name=None):
        self.data = data
        if table_name:
            PriceModel._table_name = table_name

    @classmethod
    def get_table_name(cls):
        return cls._table_name

    def to_dict(self):
        return self.data


async def _store_records_async(symbol: str, records: list, session, db_name: str, collection_name: str) -> Dict:
    """Async helper to store records using ORM's database-agnostic bulk_upsert"""
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
        PriceModel._table_name = collection_name
        inserted = await session.bulk_upsert(PriceModel, records, key_fields=['symbol', 'date'], batch_size=100)
        logger.info(f"[STORE] Bulk upsert completed: {inserted}/{len(records)} records stored to {db_name}.{collection_name}")
        return {"symbol": symbol, "status": "success", "stored": inserted, "total": len(records)}
    except Exception as e:
        logger.error(f"Error storing price records for {symbol}: {e}")
        return {"symbol": symbol, "status": "error", "stored": 0, "total": len(records), "error": str(e)}
    finally:
        for s in [sqlite_session, postgres_session]:
            if s:
                try:
                    await s.__aexit__(None, None, None)
                except:
                    pass


def store_stock_price_data(price_data: Dict, session, db_name: str, collection_name: str) -> Dict:
    """Store stock prices using ORM's database-agnostic bulk_upsert"""
    symbol = price_data.get("symbol", "UNKNOWN")

    if price_data.get("status") != "success":
        return {"symbol": symbol, "status": "skipped", "stored": 0, "reason": price_data.get("status")}

    records = price_data.get("records", [])
    if not records:
        return {"symbol": symbol, "status": "no_records", "stored": 0}

    try:
        stored = get_or_create_loop().run_until_complete(_store_records_async(symbol, records, session, db_name, collection_name))
        return stored
    except Exception as e:
        logger.error(f"Error storing stock data for {symbol}: {str(e)}")
        return {"symbol": symbol, "status": "failed", "stored": 0, "error": str(e)}
