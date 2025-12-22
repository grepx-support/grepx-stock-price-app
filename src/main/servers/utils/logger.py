"""Logging singleton - configured from app.yaml.

Single responsibility: Provide centralized logging configuration.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


class AppLogger:
    """Singleton logger that loads configuration from app.yaml."""
    
    _instance: Optional['AppLogger'] = None
    _initialized = False
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, log_level: str = "INFO", log_dir: Optional[Path] = None, 
                   log_file: Optional[str] = None, format_string: Optional[str] = None):
        """Initialize logger configuration.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files (default: project_root/logs)
            log_file: Log file name (default: price_app.log)
            format_string: Custom format string for log messages
        """
        if self._initialized:
            return
        
        # Convert string level to logging constant
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Default log directory
        if log_dir is None:
            # Assume we're in servers/utils, go up to project root
            log_dir = Path(__file__).parent.parent.parent.parent.parent / "logs"
        
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Default log file
        if log_file is None:
            log_file = "price_app.log"
        
        log_path = log_dir / log_file
        
        # Default format
        if format_string is None:
            format_string = (
                '[%(asctime)s] [%(levelname)-8s] [%(name)-20s] '
                '[%(filename)s:%(lineno)d] %(message)s'
            )
        
        # Create formatter
        formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')
        
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Console handler (always add) - use UTF-8 encoding for Windows compatibility
        console_handler = logging.StreamHandler(sys.stdout)
        # Set UTF-8 encoding for Windows compatibility
        if hasattr(console_handler.stream, 'reconfigure'):
            try:
                console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                pass  # If reconfigure fails, continue with default
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (rotating)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Create application logger
        self._logger = logging.getLogger("price_app")
        self._logger.setLevel(numeric_level)
        
        self._initialized = True
        
        # Log initialization
        self._logger.info(f"Logger initialized: level={log_level}, file={log_path}")
    
    def get_logger(self, name: str = "price_app") -> logging.Logger:
        """Get a logger instance.
        
        Args:
            name: Logger name (typically __name__)
            
        Returns:
            Logger instance
        """
        if not self._initialized:
            # Initialize with defaults if not already initialized
            self.initialize()
        
        return logging.getLogger(name)
    
    @classmethod
    def from_config(cls, config) -> logging.Logger:
        """Initialize logger from app config and return logger instance.
        
        Args:
            config: App configuration object (OmegaConf DictConfig)
            
        Returns:
            Logger instance
        """
        instance = cls()
        
        # Get logging config from app.yaml
        log_config = getattr(config.app, 'logging', {})
        log_level = log_config.get('level', 'INFO')
        log_file = log_config.get('file', 'price_app.log')
        log_format = log_config.get('format', None)
        
        instance.initialize(
            log_level=log_level,
            log_file=log_file,
            format_string=log_format
        )
        
        return instance.get_logger()


# Convenience function for getting logger
def get_logger(name: str = "price_app") -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    logger = AppLogger()
    if not logger._initialized:
        logger.initialize()
    return logger.get_logger(name)

