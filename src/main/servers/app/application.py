"""Application - Core application singleton."""

import sys
import os
from pathlib import Path
import traceback
import logging
from logging.handlers import RotatingFileHandler

class SimpleAppLogger:
    """Lightweight logger that doesn't block or require config files"""
    
    def __init__(self, name: str = "app"):
        self.logger = logging.getLogger(name)
        
        # Only configure if not already configured
        if not self.logger.handlers:
            # Console handler only (no file I/O that could block)
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter(
                '[%(levelname)s] %(name)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)
    
    def info(self, msg): self.logger.info(msg)
    def debug(self, msg): self.logger.debug(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg, exc_info=False): self.logger.error(msg, exc_info=exc_info)
    def critical(self, msg, exc_info=False): self.logger.critical(msg, exc_info=exc_info)


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
        if self._initialized:
            return

        print("[APP] Application.__init__ STARTED", file=sys.stderr)
        self.logger = SimpleAppLogger("app")

        try:
            # === STEP 1: Root path calculation ===
            print("[APP] Step 1: Calculating root path...", file=sys.stderr)
            self.root = Path(__file__).resolve().parent.parent.parent
            print(f"[APP] root = {self.root}", file=sys.stderr)

            self.config_dir = self.root / "resources"
            print(f"[APP] config_dir = {self.config_dir}", file=sys.stderr)

            if not self.config_dir.exists():
                raise FileNotFoundError(f"Config directory missing: {self.config_dir}")

            # === STEP 2: Add library paths (only if they exist) ===
            print("[APP] Step 2: Adding library paths...", file=sys.stderr)
            paths_to_add = [
                self.root.parent / "libs" / "grepx-orm-libs" / "src",
                self.root.parent / "libs" / "grepx-connection-registry" / "src",
                self.root.parent / "libs" / "prefect_framework" / "src"
            ]

            missing_paths = []
            for p in paths_to_add:
                sp = str(p)
                if not p.exists():
                    missing_paths.append(sp)
                    print(f"[APP] ⚠️  MISSING: {sp}", file=sys.stderr)
                elif sp not in sys.path:
                    sys.path.insert(0, sp)
                    print(f"[APP] ✓ Added to sys.path: {sp}", file=sys.stderr)

            if missing_paths:
                self.logger.warning(f"Missing library paths (will try to proceed): {missing_paths}")

            # === STEP 3: Load configuration (with timeout protection) ===
            print("[APP] Step 3: Loading configuration...", file=sys.stderr)
            try:
                from servers.config import ConfigLoader
                loader = ConfigLoader(self.config_dir)
                self.config = loader.load_all()
                print("[APP] ✓ Configuration loaded successfully", file=sys.stderr)
            except ImportError as e:
                print(f"[APP] ⚠️  ConfigLoader import failed: {e}", file=sys.stderr)
                # Create minimal config fallback
                from types import SimpleNamespace
                self.config = SimpleNamespace(
                    app=SimpleNamespace(environment="development"),
                    database={},
                    celery={}
                )
                self.logger.warning(f"Using fallback config: {e}")
            except Exception as e:
                print(f"[APP] ❌ Configuration loading failed: {type(e).__name__}: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                raise

            self.logger.info("Application configuration loaded successfully")

            # === STEP 4: Setup connection manager (gracefully handle missing modules) ===
            print("[APP] Step 4: Setting up connection manager...", file=sys.stderr)
            try:
                from grepx_connection_registry import ConnectionManager
                from grepx_connection_registry.connection_factory import ConnectionFactory
                
                # Register connection types - skip if module is missing
                connections_registered = []
                connections_failed = []

                # Try Celery
                try:
                    from celery_app.celery_connection import CeleryConnection
                    ConnectionFactory.register("celery", CeleryConnection)
                    connections_registered.append("celery")
                    print(f"[APP] ✓ Registered: CeleryConnection", file=sys.stderr)
                except ImportError as e:
                    connections_failed.append(f"celery: {e}")
                    print(f"[APP] ⚠️  Could not register celery: {e}", file=sys.stderr)

                # Try Database
                try:
                    from database_app.database_connection import DatabaseConnection
                    ConnectionFactory.register("database", DatabaseConnection)
                    connections_registered.append("database")
                    print(f"[APP] ✓ Registered: DatabaseConnection", file=sys.stderr)
                except ImportError as e:
                    connections_failed.append(f"database: {e}")
                    print(f"[APP] ⚠️  Could not register database: {e}", file=sys.stderr)

                # Try Dagster
                try:
                    from dagster_app.dagster_connection import DagsterConnection
                    ConnectionFactory.register("dagster", DagsterConnection)
                    connections_registered.append("dagster")
                    print(f"[APP] ✓ Registered: DagsterConnection", file=sys.stderr)
                except ImportError as e:
                    connections_failed.append(f"dagster: {e}")
                    print(f"[APP] ⚠️  Could not register dagster: {e}", file=sys.stderr)

                # Try Prefect
                try:
                    from prefect_app.prefect_connection import PrefectConnection
                    ConnectionFactory.register("prefect", PrefectConnection)
                    connections_registered.append("prefect")
                    print(f"[APP] ✓ Registered: PrefectConnection", file=sys.stderr)
                except ImportError as e:
                    connections_failed.append(f"prefect: {e}")
                    print(f"[APP] ⚠️  Could not register prefect: {e}", file=sys.stderr)

                print(f"[APP] Registered {len(connections_registered)} connection types", file=sys.stderr)
                
                if connections_failed:
                    self.logger.warning(f"Failed to register: {connections_failed}")

                # Initialize connection manager
                self.connections = ConnectionManager(self.config, self.config_dir)
                self.logger.info("Connection manager created successfully")
                print("[APP] ✓ Connection manager initialized", file=sys.stderr)

            except ImportError as e:
                print(f"[APP] ❌ ConnectionManager import failed: {e}", file=sys.stderr)
                # Create a stub connection manager
                self.connections = type('StubConnectionManager', (), {
                    'get': lambda self, conn_id: None
                })()
                self.logger.error(f"Using stub connection manager: {e}")
                raise
            except Exception as e:
                print(f"[APP] ❌ Connection manager setup failed: {type(e).__name__}: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                raise

            self.logger.info("Application initialized successfully")
            print("[APP] ✓✓✓ INITIALIZATION COMPLETE ✓✓✓", file=sys.stderr)

        except Exception as e:
            print(f"[APP] ❌ FATAL ERROR in Application.__init__: {type(e).__name__}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise

        finally:
            self._initialized = True
            print("[APP] Application.__init__ FINISHED", file=sys.stderr)

    def get_connection(self, conn_id: str):
        """Get a connection by ID"""
        try:
            self.logger.debug(f"Getting connection: {conn_id}")
            conn = self.connections.get(conn_id)
            if conn is None:
                raise ConnectionError(f"Connection '{conn_id}' not found or not initialized")
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