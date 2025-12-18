"""Factory methods for creating framework instances."""

from pathlib import Path
import asyncio
from typing import Dict, Any

from celery_framework import create_app as create_celery_app
from src.core import Session
from dagster_framework.main import create_app as create_dagster_app

from config.settings import settings
from infrastructure.config.database import DatabaseFactory
from infrastructure.config.queue import QueueFactory


class FrameworkFactory:
    """Factory for creating framework instances (Celery, Dagster, ORM)."""
    
    @staticmethod
    def create_celery_app() -> Any:
        """Create Celery application instance."""
        # Pass the OmegaConf DictConfig directly instead of converting to dict
        infra_config = settings.infrastructure_config
        return QueueFactory.create_celery_app(infra_config)
    
    @staticmethod
    def create_dagster_defs(config_dir: Path) -> Any:
        """Create Dagster definitions."""
        return create_dagster_app(config_path=str(config_dir))
    
    @staticmethod
    def create_orm_session() -> Session:
        """Create ORM session with async initialization."""
        connection_string = settings.get_infrastructure("database.connection_string")
        session = DatabaseFactory.create_orm_session(connection_string)
        
        # Initialize async connection
        try:
            asyncio.run(session.__aenter__())
        except RuntimeError:
            # If event loop is already running, skip initialization
            pass
        
        return session

