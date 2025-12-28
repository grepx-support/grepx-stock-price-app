"""Database helper utilities for schema management and backend operations."""
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def infer_schema(record: Dict[str, Any]) -> List[str]:
    """Infer column definitions from a record."""
    columns = []
    for key, value in record.items():
        col_type = 'TEXT'
        if isinstance(value, bool):
            col_type = 'INTEGER'
        elif isinstance(value, int):
            # Use BIGINT for volume and large numbers, INTEGER for others
            if key == 'volume' or (isinstance(value, int) and value > 2147483647):
                col_type = 'BIGINT'
            else:
                col_type = 'INTEGER'
        elif isinstance(value, float):
            col_type = 'REAL'
        columns.append(f'"{key}" {col_type}')
    return columns


def get_or_create_loop() -> asyncio.AbstractEventLoop:
    """Get existing event loop or create new one."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


async def get_sqlite_session(db_name: str):
    """Get or create SQLite session for specific database."""
    from core import Session

    current_file = Path(__file__)
    database_app_dir = current_file.parent
    data_dir = database_app_dir / "data"
    data_dir.mkdir(exist_ok=True, parents=True)

    db_file = data_dir / f"{db_name}.db"
    db_path = str(db_file.absolute())

    session = Session.from_backend_name('sqlite', database=db_path)
    await session.__aenter__()
    return session


async def get_postgresql_session(db_name: str):
    """Get or create PostgreSQL session for specific database."""
    from core import Session
    from main import get_app

    if not db_name or not all(c.isalnum() or c in ('_', '-') for c in db_name):
        raise ValueError(f"Invalid database name: {db_name}")

    app = get_app()
    conn = app.get_connection('primary_db')
    config = conn._connection_params if hasattr(conn, '_connection_params') else {}

    import asyncpg
    admin_conn = await asyncpg.connect(
        host=config.get('host', 'localhost'),
        port=config.get('port', 5432),
        user=config.get('username', 'postgres'),
        password=config.get('password', ''),
        database='postgres'
    )

    exists = await admin_conn.fetchval(
        "SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = $1)",
        db_name
    )
    if not exists:
        await admin_conn.execute(f'CREATE DATABASE "{db_name}"')
    await admin_conn.close()

    session = Session.from_backend_name(
        'postgresql',
        host=config.get('host', 'localhost'),
        port=config.get('port', 5432),
        username=config.get('username', 'postgres'),
        password=config.get('password', ''),
        database=db_name
    )
    await session.__aenter__()
    return session


async def create_table_if_needed(backend, table_name: str, records: List[Dict], is_sqlite: bool = False, key_fields: List[str] = None):
    """Create table if it doesn't exist."""
    if not records:
        return

    # Default key fields based on table type
    if key_fields is None:
        # Check if this looks like an indicator table (has 'factor' field)
        if 'factor' in records[0]:
            key_fields = ['symbol', 'date', 'factor']
        else:
            # Price table
            key_fields = ['symbol', 'date']

    columns = infer_schema(records[0])
    pk_str = ', '.join([f'"{f}"' for f in key_fields])
    columns.append(f"PRIMARY KEY ({pk_str})")

    quoted_table = f'"{table_name}"'
    sql = f"CREATE TABLE IF NOT EXISTS {quoted_table} ({', '.join(columns)})"

    try:
        await backend.connection.execute(sql)
        if is_sqlite:
            await backend.connection.commit()
        logger.debug(f"Table '{table_name}' ready")
    except Exception as e:
        logger.debug(f"Table creation: {e}")
