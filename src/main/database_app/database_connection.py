"""Database connection - simple ORM wrapper with extracted helper methods.

Single responsibility: Wrap ORM Session and provide database/collection access.
All connection management is handled by ConnectionBase.
"""

import asyncio
import threading
import logging
from grepx_connection_registry import ConnectionBase

logger = logging.getLogger(__name__)


class DatabaseConnection(ConnectionBase):
    """Simple database connection wrapper using ORM libs.

    Creates ONE event loop at application start and reuses it for all operations.
    This avoids "Future attached to different loop" errors in Celery.
    """

    def __init__(self, config, config_dir):
        super().__init__(config)
        self.config_dir = config_dir
        self._lock = threading.Lock()
        self._session = None
        self._loop = None
        self._connection_params = {}

    def _create_session_from_string(self, active_backend: str, connection_string: str, database_name: str):
        """Create session using connection string format."""
        from core import Session
        return Session.from_backend_name(active_backend, connection_string=connection_string, database=database_name)

    def _create_session_from_params(self, active_backend: str, host: str, port: int, username: str, password: str, database_name: str):
        """Create session using parameter-based format."""
        from core import Session
        self._connection_params = {'host': host, 'port': port, 'username': username, 'password': password, 'database': database_name}
        return Session.from_backend_name(active_backend, host=host, port=port, username=username, password=password, database=database_name)

    def _setup_event_loop(self):
        """Setup event loop with proper error handling for async contexts."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "Cannot initialize DatabaseConnection synchronously within an async context. "
                "The database connection is being created inside an async function/Dagster asset. "
                "Please refactor to make the asset/function non-async or pre-initialize the connection."
            )
        except RuntimeError as e:
            if "Cannot initialize DatabaseConnection" in str(e):
                raise
            try:
                self._loop = asyncio.get_event_loop()
                if self._loop.is_closed():
                    self._loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self._loop)
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)

    def _assign_backend_client(self):
        """Extract and assign backend client from session."""
        backend = self._session.backend
        if hasattr(backend, 'client'):
            self._client = backend.client
        elif hasattr(backend, 'connection'):
            self._client = backend.connection
        else:
            self._client = backend

    def _get_backend_data(self, obj, key):
        """Shared utility for accessing backend data with fallback."""
        if hasattr(obj, '__getitem__'):
            return obj[key]
        return self._session.backend

    def connect(self) -> None:
        """Connect using ORM Session with a single event loop."""
        if self._client is not None:
            return

        with self._lock:
            if self._client is not None:
                return

            from core import Session

            active_backend = self.config.database.get('active_backend', 'postgresql')
            backend_config = self.config.database.get(active_backend, {})

            if not backend_config:
                raise ValueError(f"Backend '{active_backend}' not configured in database.yaml")

            connection_string = backend_config.get('connection_string', None)
            database_name = backend_config.get('database', 'admin' if connection_string else 'postgres')

            if connection_string:
                self._session = self._create_session_from_string(active_backend, connection_string, database_name)
            else:
                host = backend_config.get('host', 'localhost')
                port = backend_config.get('port', 5432)
                username = backend_config.get('username', 'postgres')
                password = backend_config.get('password', '')
                self._session = self._create_session_from_params(active_backend, host, port, username, password, database_name)

            self._setup_event_loop()
            self._loop.run_until_complete(self._session.__aenter__())
            self._assign_backend_client()

    def disconnect(self) -> None:
        """Close connection cleanly."""
        if self._session:
            try:
                if self._loop:
                    self._loop.run_until_complete(self._session.__aexit__(None, None, None))
                else:
                    asyncio.run(self._session.__aexit__(None, None, None))
            except Exception as e:
                logger.warning(f"Error disconnecting database: {e}")
            finally:
                self._session = None
                self._client = None
                self._loop = None

    def get_database(self, db_name: str):
        """Get database by name.

        Args:
            db_name: Database name (e.g., 'stocks_db', 'indices_db', 'futures_db')
                    For SQLite, this is the table name prefix or ignored

        Returns:
            Database client object (varies by backend)
        """
        client = self.get_client()
        return self._get_backend_data(client, db_name)

    def get_collection(self, db_name: str, collection_name: str):
        """Get collection from database.

        Args:
            db_name: Database name (ignored for SQLite/PostgreSQL)
            collection_name: Collection/table name

        Returns:
            Collection client object
        """
        db = self.get_database(db_name)
        return self._get_backend_data(db, collection_name)
