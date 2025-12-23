"""Application - Core application singleton.

Single responsibility:
1. Load configuration once
2. Register connection types with factory
3. Create and manage connection manager
4. Provide convenient access to connections
"""

import sys
import logging
from pathlib import Path
from servers.config import ConfigLoader
from grepx_connection_registry import ConnectionManager, ConnectionFactory
from servers.utils.logger import AppLogger
# Prefect app import
from prefect_app.prefect_app import load_prefect_flows


logger = logging.getLogger(__name__)


class Application:
    """Application singleton - loads config and manages connections once.

    Uses connection factory pattern for extensibility:
    - Register custom connection types
    - Connections are cached and reused
    - Single event loop for all async operations
    """

    _instance = None
    _initialized = False


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self):
        """Initialize application (only once)."""
        if self._initialized:
            return

        # Setup paths
        self.root = Path(__file__).parent.parent.parent
        self.config_dir = self.root / "resources"

        # Add ORM libs to path
        ormlib_path = self.root.parent / "libs" / "grepx-orm-libs" / "src"
        if str(ormlib_path) not in sys.path:
            sys.path.insert(0, str(ormlib_path))

        # Add connection registry libs to path
        connection_registry_path = self.root.parent / "libs" / "grepx-connection-registry" / "src"
        if str(connection_registry_path) not in sys.path:
            sys.path.insert(0, str(connection_registry_path))
        
        # Add Prefect framework to path
        prefect_framework_path = self.root.parent / "libs" / "prefect_framework" / "src"
        if str(prefect_framework_path) not in sys.path:
            sys.path.insert(0, str(prefect_framework_path))
        

        # Load configuration
        try:
            loader = ConfigLoader(self.config_dir)
            self.config = loader.load_all()
        except Exception as e:
            print(f"ERROR: Failed to load configuration: {e}")
            raise

        # Initialize logging from config
        self.logger = AppLogger.from_config(self.config)
        self.logger.info("Application configuration loaded successfully")
        self.logger.debug(f"Configuration directory: {self.config_dir}")
        self.logger.debug(f"Environment: {getattr(self.config.app, 'environment', 'unknown')}")

        # Register connection types with factory
        self._register_connections()

        # Create connection manager
        try:
            self.logger.debug("Creating connection manager...")
            self.connections = ConnectionManager(self.config, self.config_dir)
            self.logger.info("Connection manager created successfully")
        except Exception as e:
            self.logger.error(f"Failed to create connection manager: {e}", exc_info=True)
            raise

        Application._initialized = True

    def _register_connections(self):
        """Register connection types with the factory."""
        try:
            from database_app.database_connection import DatabaseConnection

            ConnectionFactory.register("database", DatabaseConnection)
            self.logger.info("DatabaseConnection registered with factory")

            # Register other connection types as needed
            # from celery_app.celery_connection import CeleryConnection
            # ConnectionFactory.register("celery", CeleryConnection)

        except Exception as e:
            self.logger.error(f"Failed to register connections: {e}", exc_info=True)
            raise

    def get_connection(self, conn_id: str):
        """Get a connection by ID.

        Args:
            conn_id: Connection identifier (e.g., 'primary_db')

        Returns:
            Connection object

        Example:
            db_conn = app.get_connection("primary_db")
        """
        try:
            self.logger.debug(f"Getting connection: {conn_id}")
            conn = self.connections.get(conn_id)
            self.logger.debug(f"Connection '{conn_id}' retrieved successfully")
            return conn
        except Exception as e:
            self.logger.error(f"Failed to get connection '{conn_id}': {e}", exc_info=True)
            raise

    def get_database(self, db_name: str):
        """Get database by name.

        Args:
            db_name: Database name (e.g., 'stocks_db', 'indices_db', 'futures_db')

        Returns:
            Database client object

        Example:
            db = app.get_database("stocks_db")
        """
        try:
            self.logger.debug(f"Getting database: {db_name}")
            db_conn = self.get_connection("primary_db")
            db = db_conn.get_database(db_name)
            self.logger.debug(f"Database '{db_name}' retrieved successfully")
            return db
        except Exception as e:
            self.logger.error(f"Failed to get database '{db_name}': {e}", exc_info=True)
            raise

    def get_collection(self, db_name: str, collection_name: str):
        """Get collection from database.

        Args:
            db_name: Database name
            collection_name: Collection name

        Returns:
            Collection client object for direct MongoDB operations

        Example:
            collection = app.get_collection("stocks_db", "prices")
            collection.insert_one({"symbol": "AAPL", "price": 150})
        """
        try:
            self.logger.debug(f"Getting collection: {db_name}.{collection_name}")
            db_conn = self.get_connection("primary_db")
            collection = db_conn.get_collection(db_name, collection_name)
            self.logger.debug(
                f"Collection '{db_name}.{collection_name}' retrieved successfully"
            )
            return collection
        except Exception as e:
            self.logger.error(
                f"Failed to get collection '{db_name}.{collection_name}': {e}",
                exc_info=True,
            )
            raise
    
    def get_prefect_flows(self):
        """Get Prefect flows through connection manager."""
        try:
            self.logger.debug("Getting Prefect flows through connection manager...")
            prefect_conn = self.get_connection("prefect_flows")
            flows = prefect_conn.get_flows()
            self.logger.info(f"Retrieved {len(flows)} Prefect flows successfully")
            return flows
        except Exception as e:
            self.logger.error(f"Failed to get Prefect flows: {e}", exc_info=True)
            raise
    
    def get_prefect_flow(self, flow_name: str):
        """Get a specific Prefect flow by name."""
        try:
            self.logger.debug(f"Getting Prefect flow: {flow_name}")
            prefect_conn = self.get_connection("prefect_flows")
            flow = prefect_conn.get_flow(flow_name)
            if flow is None:
                self.logger.warning(f"Prefect flow '{flow_name}' not found")
            else:
                self.logger.debug(f"Prefect flow '{flow_name}' retrieved successfully")
            return flow
        except Exception as e:
            self.logger.error(f"Failed to get Prefect flow '{flow_name}': {e}", exc_info=True)
            raise