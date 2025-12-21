"""Database connection using ORM libs."""

import asyncio
import threading
import sys
from pathlib import Path

# Add ORM library to path if not already there
# Navigate from database_app/database_connection.py -> src/main -> grepx-orchestrator -> libs/grepx-orm-libs/src
orm_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "libs" / "grepx-orm-libs" / "src"
if str(orm_path) not in sys.path:
    sys.path.insert(0, str(orm_path))

from servers.connections.connection_base import ConnectionBase
from core import Session


class DatabaseConnection(ConnectionBase):
    """Database connection using ORM libs with connection pooling."""

    def __init__(self, config):
        super().__init__(config)
        self._lock = threading.Lock()
        self._session = None

    def _run_async(self, coro):
        """Run async code handling both running and non-running event loops."""
        try:
            # If there's a running event loop, we can't use asyncio.run()
            loop = asyncio.get_running_loop()
            # Use nest_asyncio to allow nested loops
            import nest_asyncio
            nest_asyncio.apply()
            return asyncio.run(coro)
        except RuntimeError:
            # No running event loop, safe to use asyncio.run()
            return asyncio.run(coro)

    def connect(self) -> None:
        """Establish database connection using ORM libs."""
        if self._client is None:
            with self._lock:
                if self._client is None:
                    self._session = Session.from_connection_string(
                        self.config.database.connection_string
                    )
                    self._run_async(self._session.__aenter__())
                    self._client = self._session.backend.client

    def disconnect(self) -> None:
        """Close database connection."""
        if self._session:
            self._run_async(self._session.__aexit__(None, None, None))
            self._session = None
        self._client = None
    
    def get_database(self, db_name: str):
        """Get a specific database."""
        return self.get_client()[db_name]
    
    def get_collection(self, db_name: str, collection_name: str):
        """Get a specific collection."""
        return self.get_database(db_name)[collection_name]
