"""Application initialization and connections setup."""
import sys
import os
from pathlib import Path
from typing import Optional
from omegaconf import OmegaConf, DictConfig
# Lazy import to avoid circular dependency
from servers.connections.connection_manager import ConnectionManager

# Prefect app import
from price_app.src.main.prefect_app.prefect_app import load_prefect_flows

class AppContext:
    """
    Singleton application context manager.
    Handles configuration loading and connection management.
    """
    _instance: Optional['AppContext'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the application context (called only once)."""
        if not self._initialized:
            self._setup_paths()
            self._load_config()
            self._initialize_connections()
            AppContext._initialized = True

    def _setup_paths(self) -> None:
        """Setup project paths and add required directories to sys.path."""
        self.root = Path(__file__).parent.parent.parent
        self.config_dir = self.root / "resources"
        self.config_file = self.config_dir / "app.yaml"

        # Set environment variable
        os.environ["PROJECT_ROOT"] = str(self.root)

        # Add ormlib to path
        ormlib_path = self.root.parent / "libs" / "py-orm-libs"
        if str(ormlib_path) not in sys.path:
            sys.path.insert(0, str(ormlib_path))

    def _load_config(self) -> None:
        """Load application configuration."""
        self.config: DictConfig = OmegaConf.load(self.config_file)

    def _initialize_connections(self) -> None:
        """Initialize connection manager."""
        self.connections = ConnectionManager(self.config, self.config_dir)
        # Load Prefect flows
        self.prefect_flows = load_prefect_flows()

    @classmethod
    def get_instance(cls) -> 'AppContext':
        """Get the singleton instance of AppContext."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_config(cls) -> DictConfig:
        """Get application configuration."""
        return cls.get_instance().config

    @classmethod
    def get_connections(cls) -> ConnectionManager:
        """Get connection manager."""
        return cls.get_instance().connections

    @classmethod
    def get_database(cls, db_name: Optional[str] = None):
        """
        Get database client or specific database.

        Args:
            db_name: Optional database name. If provided, returns specific database.
                    If None, returns the database client.

        Returns:
            Database client or specific database instance.
        """
        db = cls.get_connections().get_database()
        return db.get_database(db_name) if db_name else db.get_client()

    @classmethod
    def get_collection(cls, db_name: str, collection_name: str):
        """
        Get specific collection from database.

        Args:
            db_name: Database name
            collection_name: Collection name

        Returns:
            Collection instance
        """
        return cls.get_connections().get_database().get_collection(
            db_name, collection_name
        )

    @classmethod
    def get_celery_app(cls):
        """
        Get Celery application instance.

        Returns:
            Celery app client
        """
        return cls.get_connections().get_celery().get_client()

    @classmethod
    def get_dagster_defs(cls):
        """
        Get Dagster definitions.

        Returns:
            Dagster definitions
        """
        return cls.get_connections().get_dagster().get_definitions()

    @classmethod
    def get_prefect_flows(cls):
        """
        Get Prefect flows.

        Returns:
            Dictionary of Prefect flows
        """
        return cls.get_instance().prefect_flows

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
        cls._initialized = False