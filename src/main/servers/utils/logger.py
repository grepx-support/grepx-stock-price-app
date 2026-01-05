# """Logging singleton - configured from app.yaml."""

# import logging
# import sys
# import os
# from pathlib import Path
# from typing import Optional

# class AppLogger:
#     _instance: Optional['AppLogger'] = None
#     _initialized = False
#     _logger: Optional[logging.Logger] = None

#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#         return cls._instance

#     def initialize(self, log_level: str = "INFO", log_dir: Optional[Path] = None,
#                    log_file: Optional[str] = None, format_string: Optional[str] = None):
#         if self._initialized:
#             return

#         numeric_level = getattr(logging, log_level.upper(), logging.INFO)

#         formatter = logging.Formatter(
#             format_string or '[%(asctime)s] [%(levelname)-8s] [%(name)-20s] %(message)s',
#             datefmt='%Y-%m-%d %H:%M:%S'
#         )

#         root_logger = logging.getLogger()
#         root_logger.setLevel(numeric_level)
#         root_logger.handlers.clear()

#         # Always add console handler (safe and always works)
#         console_handler = logging.StreamHandler(sys.stdout)
#         console_handler.setLevel(numeric_level)
#         console_handler.setFormatter(formatter)
#         root_logger.addHandler(console_handler)

#         # NEVER add file handler in Airflow (prevents crashes)
#         if 'AIRFLOW_CTX_DAG_ID' in os.environ:
#             print("[LOGGER] Airflow detected - using CONSOLE-ONLY logging (file disabled)", file=sys.stderr)
#         else:
#             # Only attempt file logging outside Airflow
#             try:
#                 if log_dir is None:
#                     log_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "logs"
#                 log_dir.mkdir(parents=True, exist_ok=True)

#                 log_path = (log_dir / (log_file or "price_app.log"))
#                 file_handler = logging.FileHandler(log_path, encoding='utf-8')
#                 file_handler.setLevel(numeric_level)
#                 file_handler.setFormatter(formatter)
#                 root_logger.addHandler(file_handler)
#                 print(f"[LOGGER] File handler added: {log_path}", file=sys.stderr)
#             except Exception as e:
#                 print(f"[LOGGER] Failed to add file handler: {e} - falling back to console", file=sys.stderr)

#         self._logger = logging.getLogger("price_app")
#         self._logger.setLevel(numeric_level)
#         self._initialized = True

#         self._logger.info(f"Logger initialized: level={log_level} (console + {'file' if root_logger.handlers[-1].__class__.__name__ != 'StreamHandler' else 'console only'})")

#     def get_logger(self, name: str = "price_app") -> logging.Logger:
#         if not self._initialized:
#             self.initialize()
#         return logging.getLogger(name)

#     @classmethod
#     def from_config(cls, config) -> logging.Logger:
#         instance = cls()
#         log_config = getattr(config.app, 'logging', {})
#         instance.initialize(
#             log_level=log_config.get('level', 'INFO'),
#             log_file=log_config.get('file', 'price_app.log'),
#             format_string=log_config.get('format', None)
#         )
#         return instance.get_logger()

# # Convenience
# def get_logger(name: str = "price_app") -> logging.Logger:
#     return AppLogger().get_logger(name)


"""
Logging singleton - configured from app.yaml.
SAFE VERSION: No Prefect/network calls during initialization.
"""

import logging
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

class AppLogger:
    """Singleton logger that's safe for Airflow/Celery environments"""
    
    _instance: Optional['AppLogger'] = None
    _initialized = False
    _logger: Optional[logging.Logger] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(
        self, 
        log_level: str = "INFO", 
        log_dir: Optional[Path] = None,
        log_file: Optional[str] = None, 
        format_string: Optional[str] = None
    ):
        """Initialize logger (safe to call multiple times)"""
        if self._initialized:
            return

        try:
            # Determine log level
            numeric_level = getattr(logging, log_level.upper(), logging.INFO)
            
            # Setup formatter
            formatter = logging.Formatter(
                format_string or '[%(asctime)s] [%(levelname)-8s] [%(name)-20s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # Get root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(numeric_level)
            root_logger.handlers.clear()

            # === ALWAYS ADD CONSOLE HANDLER ===
            # This is SAFE and works everywhere
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(numeric_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
            
            print(f"[LOGGER] Console handler added (level={log_level})", file=sys.stderr)

            # === ONLY ADD FILE HANDLER OUTSIDE AIRFLOW ===
            # Airflow has its own logging, adding files causes issues
            is_airflow = 'AIRFLOW_CTX_DAG_ID' in os.environ
            
            if is_airflow:
                print("[LOGGER] Airflow environment detected - file logging disabled", file=sys.stderr)
            else:
                try:
                    # Create log directory
                    if log_dir is None:
                        log_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "logs"
                    
                    log_dir.mkdir(parents=True, exist_ok=True)
                    log_path = log_dir / (log_file or "price_app.log")
                    
                    # Add file handler
                    file_handler = logging.FileHandler(log_path, encoding='utf-8')
                    file_handler.setLevel(numeric_level)
                    file_handler.setFormatter(formatter)
                    root_logger.addHandler(file_handler)
                    
                    print(f"[LOGGER] File handler added: {log_path}", file=sys.stderr)
                    
                except Exception as e:
                    print(f"[LOGGER] Warning: Could not add file handler: {e}", file=sys.stderr)
                    print(f"[LOGGER] Continuing with console-only logging", file=sys.stderr)

            # Setup instance logger
            self._logger = logging.getLogger("price_app")
            self._logger.setLevel(numeric_level)
            self._initialized = True
            
            self._logger.info(f"✓ Logger initialized (level={log_level}, mode={'console+file' if not is_airflow else 'console-only'})")

        except Exception as e:
            print(f"[LOGGER] FATAL ERROR during initialization: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise

    def get_logger(self, name: str = "price_app") -> logging.Logger:
        """Get a logger instance"""
        if not self._initialized:
            self.initialize()
        return logging.getLogger(name)

    @classmethod
    def from_config(cls, config) -> logging.Logger:
        """
        Create logger from configuration object.
        SAFE: Handles missing/malformed config gracefully.
        """
        instance = cls()
        
        try:
            # === SAFELY extract logging config ===
            log_config = {}
            
            # Try to get logging config from config object
            if hasattr(config, 'app'):
                if hasattr(config.app, 'logging'):
                    # Handle both dict and OmegaConf
                    log_section = config.app.logging
                    if isinstance(log_section, dict):
                        log_config = log_section
                    else:
                        # OmegaConf - convert to dict
                        try:
                            from omegaconf import OmegaConf
                            log_config = OmegaConf.to_container(log_section, resolve=True)
                        except:
                            log_config = {}
            
            # Extract values with safe defaults
            log_level = log_config.get('level', 'INFO') if log_config else 'INFO'
            log_file = log_config.get('file', 'price_app.log') if log_config else 'price_app.log'
            format_string = log_config.get('format', None) if log_config else None
            
            print(f"[LOGGER] Config extracted: level={log_level}, file={log_file}", file=sys.stderr)
            
            # Initialize with safe config
            instance.initialize(
                log_level=log_level,
                log_file=log_file,
                format_string=format_string
            )
            
            return instance.get_logger()
            
        except Exception as e:
            print(f"[LOGGER] Error in from_config: {e} - using defaults", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            
            # Fallback: initialize with defaults
            instance.initialize(log_level='INFO', log_file='price_app.log')
            return instance.get_logger()


# Module-level convenience function
def get_logger(name: str = "price_app") -> logging.Logger:
    """Get a logger instance (convenience function)"""
    return AppLogger().get_logger(name)