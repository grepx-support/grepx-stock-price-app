# # servers/services/stock_service.py (BUSINESS LOGIC)
import yfinance as yf
from datetime import datetime
from typing import Dict
import asyncio

_event_loop = None

def fetch_stock_price_data(symbol: str, start_date: str = None, end_date: str = None) -> Dict:
    """Fetch stock prices from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(start=start_date, end=end_date)

        records = []
        for date, row in data.iterrows():
            records.append({
                "symbol": symbol,
                "date": str(date.date()),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume']),
                "fetched_at": datetime.now().isoformat(),
            })

        return { "symbol": symbol, "records": records, "count": len(records), "status": "success" }

    except Exception as e:
        return { "symbol": symbol, "records": [], "count": 0, "status": "error", "error": str(e) }

def _get_event_loop():
    """Get or create event loop for the worker process"""
    global _event_loop
    try:
        _event_loop = asyncio.get_running_loop()
    except RuntimeError:
        if _event_loop is None or _event_loop.is_closed():
            _event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_event_loop)
    return _event_loop

def store_stock_price_data(price_data: Dict, session, db_name: str, collection_name: str) -> Dict:
    """Store stock prices using ORM's database-agnostic bulk_upsert"""
    symbol = price_data.get("symbol", "UNKNOWN")

    if price_data.get("status") != "success":
        return {"symbol": symbol, "status": "skipped", "stored": 0, "reason": price_data.get("status")}

    records = price_data.get("records", [])
    if not records:
        return {"symbol": symbol, "status": "no_records", "stored": 0}
    try:
        loop = _get_event_loop()
        result = loop.run_until_complete(_store_records_async(symbol, records, session, db_name, collection_name))
        return result

    except Exception as e:
        return {"symbol": symbol, "status": "error", "stored": 0, "error": str(e)}

async def _store_records_async(symbol: str, records: list, session, db_name: str, collection_name: str) -> Dict:
    """Async helper to store records using ORM's database-agnostic bulk_upsert"""
    import logging
    logger = logging.getLogger(__name__)

    sqlite_session = None
    postgres_session = None
    try:
        # For SQLite, create separate connections per database
        backend = session.backend
        logger.info(f"[STORE] Backend type check: hasattr={hasattr(backend, 'backend_name')}, backend={backend}, type={type(backend)}")
        if hasattr(backend, 'backend_name'):
            logger.info(f"[STORE] Backend name: {backend.backend_name}")

        if hasattr(backend, 'backend_name') and backend.backend_name == 'sqlite':
            logger.info(f"[STORE] SQLite detected! Creating session for {db_name}.{collection_name}")
            # Create/connect to database-specific SQLite file
            sqlite_session = await _get_sqlite_session_for_db(db_name)
            session = sqlite_session
            backend = session.backend
            logger.info(f"[STORE] New session created for {db_name}")
            await _create_sqlite_price_table_if_needed(backend, collection_name, records)
        else:
            logger.info(f"[STORE] Non-SQLite backend: using default session for {db_name}.{collection_name}")

        # Create a simple model class for bulk upsert using actual collection name
        class PriceModel:
            def __init__(self, record_data):
                self.data = record_data

            @staticmethod
            def get_table_name():
                return collection_name

            def to_dict(self):
                return self.data

        # Use ORM's bulk_upsert which is database-agnostic
        # For MongoDB, we need to switch to the correct database
        if hasattr(backend, 'backend_name') and backend.backend_name == 'mongodb':
            logger.info(f"[STORE] MongoDB: Switching to database {db_name}")
            # MongoDB: Switch the backend's database reference directly
            if hasattr(backend, 'client'):
                backend.database = backend.client[db_name]
                logger.info(f"[STORE] MongoDB: Backend database switched to {db_name}")
        elif hasattr(backend, 'backend_name') and backend.backend_name == 'postgresql':
            logger.info(f"[STORE] PostgreSQL detected! Creating session for {db_name}.{collection_name}")
            # PostgreSQL: Create/connect to database-specific session
            postgres_session = await _get_postgresql_session_for_db(db_name)
            session = postgres_session
            backend = session.backend
            logger.info(f"[STORE] PostgreSQL session created for {db_name}")
            # PostgreSQL: Create table if it doesn't exist
            await _create_postgresql_price_table_if_needed(backend, collection_name, records)

        inserted = await session.bulk_upsert(
            PriceModel,
            records,
            key_fields=['symbol', 'date'],
            batch_size=100
        )
        logger.info(f"[STORE] Bulk upsert completed: {inserted}/{len(records)} records stored to {db_name}.{collection_name}")
        return {"symbol": symbol, "status": "success", "stored": inserted, "total": len(records)}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error storing price records for {symbol}: {e}")
        return {"symbol": symbol, "status": "error", "stored": 0, "total": len(records), "error": str(e)}
    finally:
        # Close SQLite session if it was created
        if sqlite_session is not None:
            try:
                await sqlite_session.__aexit__(None, None, None)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error closing SQLite session: {e}")
        # Close PostgreSQL session if it was created
        if postgres_session is not None:
            try:
                await postgres_session.__aexit__(None, None, None)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error closing PostgreSQL session: {e}")


async def _get_sqlite_session_for_db(db_name: str):
    """Get or create SQLite session for specific database."""
    from core import Session
    from pathlib import Path
    import os
    import logging
    logger = logging.getLogger(__name__)

    # Map database names to SQLite files - use absolute path from current working directory
    data_dir = Path(os.getcwd()) / "data"
    logger.info(f"[SQLITE] Creating session for {db_name}, cwd={os.getcwd()}, data_dir={data_dir}")
    data_dir.mkdir(exist_ok=True, parents=True)
    db_file = data_dir / f"{db_name}.db"
    logger.info(f"[SQLITE] Database file path: {db_file.absolute()}")

    # For SQLite, pass the absolute file path as the database parameter
    # aiosqlite.connect() expects the actual file path, not a connection string
    db_path = str(db_file.absolute())
    logger.info(f"[SQLITE] Database file path (for aiosqlite): {db_path}")
    session = Session.from_backend_name(
        'sqlite',
        database=db_path
    )

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    await session.__aenter__()
    return session


async def _create_sqlite_price_table_if_needed(backend, table_name: str, records: list):
    """Create SQLite table if it doesn't exist based on record structure."""
    if not records:
        return

    import logging
    logger = logging.getLogger(__name__)

    # Infer schema from first record
    first_record = records[0]
    columns = []

    for key, value in first_record.items():
        col_type = 'TEXT'
        if isinstance(value, int):
            col_type = 'INTEGER'
        elif isinstance(value, float):
            col_type = 'REAL'
        elif isinstance(value, bool):
            col_type = 'INTEGER'

        columns.append(f"{key} {col_type}")

    # Add composite primary key constraint
    composite_key = ', '.join(['symbol', 'date'])
    columns.append(f"PRIMARY KEY ({composite_key})")

    # Quote table name to handle special characters like = in futures/indices symbols
    quoted_table = f'"{table_name}"'
    create_sql = f"CREATE TABLE IF NOT EXISTS {quoted_table} ({', '.join(columns)})"

    try:
        await backend.connection.execute(create_sql)
        await backend.connection.commit()
        logger.debug(f"SQLite table '{table_name}' ready for price records")
    except Exception as e:
        logger.debug(f"SQLite table creation: {e}")


async def _get_postgresql_session_for_db(db_name: str):
    """Get or create PostgreSQL session for specific database.

    Creates the database if it doesn't exist and returns a connected session.
    """
    from core import Session
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Get connection parameters from main app config
        from main import get_app
        app = get_app()
        conn = app.get_connection('primary_db')

        # Extract connection parameters
        config = conn._connection_params if hasattr(conn, '_connection_params') else {}
        host = config.get('host', 'localhost')
        port = config.get('port', 5432)
        username = config.get('username', config.get('user', 'postgres'))
        password = config.get('password', '')

        logger.info(f"[POSTGRES] Creating session for {db_name}, host={host}, port={port}, user={username}")

        # First, create database if it doesn't exist (using postgres database)
        try:
            import asyncpg
            admin_conn = await asyncpg.connect(
                host=host,
                port=port,
                user=username,
                password=password,
                database='postgres'
            )
            # Check if database exists
            exists = await admin_conn.fetchval(
                f"SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = '{db_name}')"
            )
            if not exists:
                logger.info(f"[POSTGRES] Creating database {db_name}")
                await admin_conn.execute(f'CREATE DATABASE "{db_name}"')
            await admin_conn.close()
        except Exception as e:
            logger.warning(f"[POSTGRES] Could not create database {db_name}: {e}")

        # Now create session to the specific database
        # Use parameter-based approach (not connection string) to avoid special character issues with passwords
        session = Session.from_backend_name(
            'postgresql',
            host=host,
            port=port,
            username=username,
            password=password,
            database=db_name
        )

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        await session.__aenter__()
        logger.info(f"[POSTGRES] Session created for {db_name}")
        return session

    except Exception as e:
        logger.error(f"[POSTGRES] Error creating session for {db_name}: {e}")
        raise


async def _create_postgresql_price_table_if_needed(backend, table_name: str, records: list):
    """Create PostgreSQL table if it doesn't exist based on record structure."""
    if not records:
        return

    import logging
    logger = logging.getLogger(__name__)

    # Infer schema from first record
    first_record = records[0]
    columns = []

    for key, value in first_record.items():
        col_type = 'TEXT'
        if isinstance(value, int):
            col_type = 'INTEGER'
        elif isinstance(value, float):
            col_type = 'REAL'
        elif isinstance(value, bool):
            col_type = 'INTEGER'

        columns.append(f'"{key}" {col_type}')

    # Add composite primary key constraint
    composite_key = ', '.join(['"symbol"', '"date"'])
    columns.append(f"PRIMARY KEY ({composite_key})")

    create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(columns)})'

    try:
        await backend.connection.execute(create_sql)
        logger.debug(f"PostgreSQL table '{table_name}' ready for price records")
    except Exception as e:
        logger.debug(f"PostgreSQL table creation: {e}")
        # If table creation fails, try without quotes in case of edge cases
        try:
            create_sql_alt = f'CREATE TABLE IF NOT EXISTS {table_name} ({", ".join(columns)})'
            await backend.connection.execute(create_sql_alt)
            logger.debug(f"PostgreSQL table '{table_name}' created (alternative)")
        except Exception as e2:
            logger.warning(f"PostgreSQL table creation failed even with alternative: {e2}")
            # Last resort: try sanitizing special characters
            try:
                # Replace problematic characters with underscores for table name
                sanitized_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in table_name)
                create_sql_safe = f'CREATE TABLE IF NOT EXISTS {sanitized_name} ({", ".join(columns)})'
                await backend.connection.execute(create_sql_safe)
                logger.debug(f"PostgreSQL table '{table_name}' created (sanitized as '{sanitized_name}')")
            except Exception as e3:
                logger.error(f"PostgreSQL table creation failed after all attempts for '{table_name}': {e3}")
