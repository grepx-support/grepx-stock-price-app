
# airflow_app/utils/config_loader.py
"""
Configuration loader for asset types and indicators
"""
from servers.factors.config import cfg
from typing import List, Dict
from omegaconf import OmegaConf
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Load and cache configuration"""
    
    _config_cache = None
    
    @staticmethod
    def get_asset_symbols(asset_type: str) -> List[str]:
        """Get symbols for an asset type"""
        try:
            return cfg.asset_types[asset_type].symbols
        except Exception as e:
            logger.error(f"Failed to load symbols for {asset_type}: {e}")
            return []
    
    @staticmethod
    def get_indicators() -> Dict:
        """Get all indicators configuration"""
        try:
            return OmegaConf.to_container(cfg.indicators, resolve=True)
        except Exception as e:
            logger.error(f"Failed to load indicators config: {e}")
            return {}
    
    @staticmethod
    def get_indicator_names() -> List[str]:
        """Get list of all indicator names"""
        indicators = ConfigLoader.get_indicators()
        return list(indicators.keys())
    
    @staticmethod
    def get_date_range() -> Dict[str, str]:
        """Get start and end dates"""
        return {
            'start_date': cfg.start_date,
            'end_date': cfg.end_date,
        }
    
    @staticmethod
    def get_all_asset_types() -> List[str]:
        """Get all available asset types"""
        try:
            return list(cfg.asset_types.keys())
        except Exception as e:
            logger.error(f"Failed to load asset types: {e}")
            return []

