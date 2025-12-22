"""Application - Core application singleton.

Single responsibility: Load config once, manage connections.
File name matches class name.
"""

import sys
from pathlib import Path
from servers.config import ConfigLoader
from servers.connections import ConnectionManager
from servers.utils.logger import AppLogger


class Application:
    """Application singleton - loads config and manages connections once."""
    
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
        
        # Create connection manager
        try:
            self.logger.debug("Creating connection manager...")
            self.connections = ConnectionManager(self.config, self.config_dir)
            self.logger.info("Connection manager created successfully")
        except Exception as e:
            self.logger.error(f"Failed to create connection manager: {e}", exc_info=True)
            raise
        
        Application._initialized = True
    
    def get_connection(self, conn_id: str):
        """Get a connection by ID."""
        try:
            self.logger.debug(f"Getting connection: {conn_id}")
            conn = self.connections.get(conn_id)
            self.logger.debug(f"Connection '{conn_id}' retrieved successfully")
            return conn
        except Exception as e:
            self.logger.error(f"Failed to get connection '{conn_id}': {e}", exc_info=True)
            raise
    
    def get_database(self, db_name: str):
        """Get database by name."""
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
        """Get collection."""
        try:
            self.logger.debug(f"Getting collection: {db_name}.{collection_name}")
            db_conn = self.get_connection("primary_db")
            collection = db_conn.get_collection(db_name, collection_name)
            self.logger.debug(f"Collection '{db_name}.{collection_name}' retrieved successfully")
            return collection
        except Exception as e:
            self.logger.error(f"Failed to get collection '{db_name}.{collection_name}': {e}", exc_info=True)
            raise


