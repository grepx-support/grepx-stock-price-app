"""Queue connection factory."""

from typing import Dict, Any
import logging
from omegaconf import OmegaConf, DictConfig
from celery_framework import create_app as create_celery_app

logger = logging.getLogger(__name__)


class QueueFactory:
    """Factory for creating queue connections."""

    @staticmethod
    def create_celery_app(config: Dict[str, Any]):
        """
        Create a Celery application.
        
        Args:
            config: Configuration dictionary (will be converted to DictConfig)
        
        Returns:
            Celery application instance
        """
        try:
            # Convert dict to DictConfig if needed (celery_framework expects DictConfig)
            if isinstance(config, dict):
                config = OmegaConf.create(config)
            
            celery_app = create_celery_app(config)
            return celery_app.app
        except Exception as e:
            logger.error(f"Error creating Celery app: {e}")
            raise

