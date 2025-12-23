"""Database connection - simple ORM wrapper.

Single responsibility: Wrap ORM Session and provide database/collection access.
All connection management is handled by ConnectionBase.
"""

import asyncio
import threading
from grepx_connection_registry import ConnectionBase


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
        self._connection_params = {}  # Store connection parameters for accessing later

    def connect(self) -> None:
        """Connect using ORM Session with a single event loop."""
        if self._client is not None:
            return  # Already connected

        with self._lock:
            if self._client is not None:
                return  # Double-check after lock

            from core import Session

            # Get active backend from config
            active_backend = self.config.database.get('active_backend', 'postgresql')
            backend_config = self.config.database.get(active_backend, {})

            if not backend_config:
                raise ValueError(f"Backend '{active_backend}' not configured in database.yaml")

            # Support both connection_string and individual parameters
            connection_string = backend_config.get('connection_string', None)

            if connection_string:
                # Using connection_string format
                database_name = backend_config.get('database', 'admin')

                # Create session with connection string
                self._session = Session.from_backend_name(
                    active_backend,
                    connection_string=connection_string,
                    database=database_name
                )
            else:
                # Using individual parameters format (for PostgreSQL)
                host = backend_config.get('host', 'localhost')
                port = backend_config.get('port', 5432)
                username = backend_config.get('username', 'postgres')
                password = backend_config.get('password', '')
                database_name = backend_config.get('database', 'postgres')

                # Store connection parameters for later use (e.g., in PostgreSQL helper functions)
                self._connection_params = {
                    'host': host,
                    'port': port,
                    'username': username,
                    'password': password,
                    'database': database_name
                }

                # Create session with parameters
                self._session = Session.from_backend_name(
                    active_backend,
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    database=database_name
                )

            # Create event loop ONCE and reuse it
            # First, check if there's already a running loop
            try:
                current_loop = asyncio.get_running_loop()
                # If we got here, there IS a running loop (Dagster, async context, etc.)
                # We're already in an async context, so we cannot call sync code that tries to
                # run async operations. We need to raise an error and let the caller handle it.
                # The connection should be lazy-loaded or the caller should handle async properly.
                raise RuntimeError(
                    "Cannot initialize DatabaseConnection synchronously within an async context. "
                    "The database connection is being created inside an async function/Dagster asset. "
                    "Please refactor to make the asset/function non-async or pre-initialize the connection."
                )
            except RuntimeError as e:
                if "Cannot initialize DatabaseConnection" in str(e):
                    raise
                # No running loop, safe to create and manage our own
                try:
                    self._loop = asyncio.get_event_loop()
                    if self._loop.is_closed():
                        self._loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(self._loop)
                except RuntimeError:
                    # No event loop in current thread
                    self._loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self._loop)

                # Now we have a safe loop to use
                self._loop.run_until_complete(self._session.__aenter__())
            # Store backend client/connection (different backends use different names)
            if hasattr(self._session.backend, 'client'):
                self._client = self._session.backend.client
            elif hasattr(self._session.backend, 'connection'):
                self._client = self._session.backend.connection
            else:
                self._client = self._session.backend

    def disconnect(self) -> None:
        """Close connection cleanly."""
        if self._session:
            try:
                # Check if we have a loop to use
                if self._loop:
                    self._loop.run_until_complete(self._session.__aexit__(None, None, None))
                else:
                    # No loop stored (was using asyncio.run), use it again
                    asyncio.run(self._session.__aexit__(None, None, None))
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
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
        # For MongoDB, use subscript notation
        # For SQLite/PostgreSQL, this may not apply, so return client
        if hasattr(client, '__getitem__'):
            return client[db_name]
        return client

    def get_collection(self, db_name: str, collection_name: str):
        """Get collection from database.

        Args:
            db_name: Database name (ignored for SQLite/PostgreSQL)
            collection_name: Collection/table name

        Returns:
            Collection client object
        """
        db = self.get_database(db_name)
        # For MongoDB, use subscript notation on database
        # For SQLite/PostgreSQL, return the collection/table directly via session
        if hasattr(db, '__getitem__'):
            return db[collection_name]
        # For other backends, return the session's backend
        return self._session.backend
