import importlib
import logging

logger = logging.getLogger(__name__)


def load_data_source(source: str):
    """Load and instantiate data source API by name."""
    try:
        logger.debug(f"Attempting to load data source: {source}")
        
        module = importlib.import_module(f"data_sources.{source}")
        logger.debug(f"Module loaded successfully: data_sources.{source}")
        
        api_classes = [x for x in dir(module) if x.endswith("API")]
        if not api_classes:
            logger.error(f"No API class found in data_sources.{source}")
            raise ValueError(f"No API class found in module: data_sources.{source}")
        
        api_class = getattr(module, api_classes[0])
        logger.info(f"Data source '{source}' loaded successfully: {api_class.__name__}")
        return api_class
        
    except ModuleNotFoundError as e:
        logger.error(f"Data source module not found: {source}", exc_info=True)
        raise ValueError(f"Data source '{source}' does not exist") from e
    except AttributeError as e:
        logger.error(f"Failed to get API class from module: {source}", exc_info=True)
        raise ValueError(f"Invalid API class in data source '{source}'") from e
    except Exception as e:
        logger.error(f"Unexpected error loading data source '{source}'", exc_info=True)
        raise ValueError(f"Failed to load data source '{source}': {str(e)}") from e