"""Database connection using ORM libs."""

import asyncio
import threading
from .connection_base import ConnectionBase


class DatabaseConnection(ConnectionBase):
    """Database connection using ORM libs with connection pooling."""
    
    def __init__(self, config):
        super().__init__(config)
        self._lock = threading.Lock()
        self._session = None
    
    def connect(self) -> None:
        """Establish database connection using ORM libs."""
        if self._client is None:
            with self._lock:
                if self._client is None:
                    from core import Session
                    
                    self._session = Session.from_connection_string(
                        self.config.database.connection_string
                    )
                    asyncio.run(self._session.__aenter__())
                    self._client = self._session.backend.client
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self._session:
            asyncio.run(self._session.__aexit__(None, None, None))
            self._session = None
        self._client = None
    
    def get_database(self, db_name: str):
        """Get a specific database."""
        return self.get_client()[db_name]
    
    def get_collection(self, db_name: str, collection_name: str):
        """Get a specific collection."""
        return self.get_database(db_name)[collection_name]
