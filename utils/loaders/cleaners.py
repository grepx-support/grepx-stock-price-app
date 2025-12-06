from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


def clean_symbol(symbol: str) -> str:
    """Normalize symbol for collection naming."""
    try:
        if not isinstance(symbol, str):
            logger.error(f"Symbol must be string, got {type(symbol).__name__}")
            raise TypeError(f"Symbol must be string, got {type(symbol).__name__}")
        
        if not symbol.strip():
            logger.error("Symbol cannot be empty")
            raise ValueError("Symbol cannot be empty")
        
        cleaned = (
            symbol.replace(".NS", "")
                  .replace(".BO", "")
                  .replace(".", "_")
                  .replace("-", "_")
                  .lower()
        )
        
        logger.debug(f"Cleaned symbol: {symbol} -> {cleaned}")
        return cleaned
        
    except (TypeError, ValueError) as e:
        logger.error(f"Symbol cleaning failed: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error cleaning symbol", exc_info=True)
        raise RuntimeError(f"Symbol cleaning failed: {str(e)}") from e


def get_collection_name(symbol: str) -> str:
    """Get MongoDB collection name for symbol."""
    try:
        clean = clean_symbol(symbol)
        collection = f"{clean}_prices"
        logger.debug(f"Collection name for {symbol}: {collection}")
        return collection
        
    except Exception as e:
        logger.error(f"Failed to generate collection name for {symbol}", exc_info=True)
        raise


def clean_date(date_value) -> str | None:
    """Convert date to ISO format string."""
    try:
        if date_value is None:
            logger.debug("Date value is None, skipping conversion")
            return None
        
        if isinstance(date_value, (datetime, date)):
            iso_date = date_value.isoformat()
            logger.debug(f"Converted date: {date_value} -> {iso_date}")
            return iso_date
        
        logger.debug(f"Date value already in valid format: {date_value}")
        return date_value
        
    except Exception as e:
        logger.error(f"Failed to clean date value: {date_value}", exc_info=True)
        raise RuntimeError(f"Date cleaning failed: {str(e)}") from e


def enrich_row(row: dict, symbol: str, source: str) -> dict:
    """Add metadata to a single data row."""
    try:
        if not isinstance(row, dict):
            logger.error(f"Row must be dict, got {type(row).__name__}")
            raise TypeError(f"Row must be dict, got {type(row).__name__}")
        
        if not isinstance(symbol, str) or not symbol.strip():
            logger.error("Symbol must be non-empty string")
            raise ValueError("Symbol must be non-empty string")
        
        if not isinstance(source, str) or not source.strip():
            logger.error("Source must be non-empty string")
            raise ValueError("Source must be non-empty string")
        
        enriched = row.copy()
        enriched["symbol"] = symbol
        enriched["source"] = source
        enriched["date"] = clean_date(enriched.get("date"))
        enriched["fetched_at"] = datetime.now().isoformat()
        enriched.pop("_id", None)
        
        logger.debug(f"Row enriched for {symbol} from {source}")
        return enriched
        
    except (TypeError, ValueError) as e:
        logger.error(f"Row enrichment validation failed", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error enriching row", exc_info=True)
        raise RuntimeError(f"Row enrichment failed: {str(e)}") from e


def clean_rows(rows: list, symbol: str, source: str) -> list:
    """Clean and enrich all data rows."""
    try:
        if not isinstance(rows, list):
            logger.error(f"Rows must be list, got {type(rows).__name__}")
            raise TypeError(f"Rows must be list, got {type(rows).__name__}")
        
        if not rows:
            logger.warning("Empty rows list provided")
            return []
        
        logger.info(f"Cleaning {len(rows)} rows for {symbol} from {source}")
        
        cleaned_rows = []
        errors = 0
        
        for idx, row in enumerate(rows):
            try:
                cleaned_row = enrich_row(row, symbol, source)
                cleaned_rows.append(cleaned_row)
            except Exception as e:
                errors += 1
                logger.warning(f"Failed to clean row {idx}: {str(e)}")
                # Continue processing other rows
        
        if errors > 0:
            logger.warning(f"Cleaned {len(cleaned_rows)} rows with {errors} errors")
        else:
            logger.info(f"Successfully cleaned all {len(cleaned_rows)} rows")
        
        return cleaned_rows
        
    except TypeError as e:
        logger.error(f"Invalid input type for clean_rows", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error cleaning rows", exc_info=True)
        raise RuntimeError(f"Row cleaning failed: {str(e)}") from e