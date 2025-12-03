import logging
import pandas as pd

logger = logging.getLogger(__name__)


def fetch_price_data(api, symbol: str, start_date: str, end_date: str | None) -> pd.DataFrame:
    """Fetch historical price data from API."""
    try:
        logger.info(f"Fetching {symbol} from {api.__class__.__name__}")
        logger.debug(f"Date range: {start_date} to {end_date}")
        
        df = api.fetch_historical_prices(start_date, end_date)
        
        if not isinstance(df, pd.DataFrame):
            logger.error(f"API returned non-DataFrame object: {type(df).__name__}")
            raise TypeError(f"Expected DataFrame, got {type(df).__name__}")
        
        logger.info(f"Successfully fetched {len(df)} rows for {symbol}")
        return df
        
    except AttributeError as e:
        logger.error(f"API object missing 'fetch_historical_prices' method", exc_info=True)
        raise AttributeError(f"Invalid API object structure") from e
    except TypeError as e:
        logger.error(f"Invalid date format or API response type", exc_info=True)
        raise TypeError(f"Data fetch failed: {str(e)}") from e
    except Exception as e:
        logger.error(f"Failed to fetch data for {symbol}", exc_info=True)
        raise RuntimeError(f"API fetch failed for {symbol}: {str(e)}") from e