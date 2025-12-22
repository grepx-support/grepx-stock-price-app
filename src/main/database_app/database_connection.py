"""Database connection."""

import asyncio
import threading
from grepx_connection_registry import ConnectionBase


class DatabaseConnection(ConnectionBase):
    """Database connection using ORM libs."""
    
    def __init__(self, config, config_dir):
        super().__init__(config)
        self.config_dir = config_dir
        self._lock = threading.Lock()
        self._session = None
    
    def connect(self) -> None:
        if self._client is None:
            with self._lock:
                if self._client is None:
                    from core import Session
                    
                    connection_string = self.config.database.connection_string
                    
                    self._session = Session.from_connection_string(connection_string)
                    asyncio.run(self._session.__aenter__())
                    self._client = self._session.backend.client
    
    def disconnect(self) -> None:
        if self._session:
            asyncio.run(self._session.__aexit__(None, None, None))
            self._session = None
        self._client = None
    
    def get_database(self, db_name: str):
        return self.get_client()[db_name]
    
    def get_collection(self, db_name: str, collection_name: str):
        return self.get_database(db_name)[collection_name]
