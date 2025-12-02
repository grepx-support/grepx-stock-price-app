"""Factory for creating indicator assets."""
from dagster import asset, AssetIn, Failure
import logging
import pandas as pd
from utils.indicator_factory import create_indicator
from utils.indicator_storage import store_indicators
from utils.cleaners import clean_symbol
from db.MongoDBManager import MongoDBManager

logger = logging.getLogger(__name__)


def _process_indicator(symbol: str, indicator_name: str) -> dict:
    """Helper to fetch prices and calculate indicator."""
    try:
        clean = clean_symbol(symbol)
        price_collection = f"{clean}_prices"
        
        prices = MongoDBManager.find_all(price_collection)
        if not prices:
            raise ValueError(f"No prices in {price_collection}")
        
        price_df = pd.DataFrame(prices)
        indicator = create_indicator(indicator_name, symbol)
        result_df = indicator.process(price_df)
        
        if result_df.empty:
            raise ValueError(f"Empty result from {indicator_name}")
        
        store_indicators({indicator_name: result_df}, symbol, source="dagster")
        
        return {
            "symbol": symbol,
            "indicator": indicator_name,
            "rows": len(result_df),
            "collection": indicator.get_collection_name(),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed {indicator_name} for {symbol}: {str(e)}", exc_info=True)
        raise


def create_indicator_asset(indicator_name: str):
    """Factory function to create indicator assets."""
    
    @asset(
        name=f"{indicator_name.lower()}_indicator",
        description=f"Calculate {indicator_name} for all symbols",
        group_name="stock_indicators",
        ins={"price_ingestion": AssetIn("price_ingestion")}
    )
    def indicator_asset(price_ingestion):
        try:
            results = price_ingestion["results"]
            symbols = [r["symbol"] for r in results if r["status"] == "success"]
            
            if not symbols:
                logger.warning(f"No symbols for {indicator_name}")
                return {"indicator": indicator_name, "status": "no_data", "results": []}
            
            logger.info(f"Calculating {indicator_name} for {len(symbols)} symbols")
            
            indicator_results = []
            for symbol in symbols:
                try:
                    result = _process_indicator(symbol, indicator_name)
                    indicator_results.append(result)
                    logger.info(f"✓ {indicator_name} for {symbol}")
                except Exception as e:
                    indicator_results.append({
                        "symbol": symbol,
                        "indicator": indicator_name,
                        "status": "error",
                        "error": str(e)
                    })
            
            successful = sum(1 for r in indicator_results if r.get("status") == "success")
            return {
                "indicator": indicator_name,
                "total_symbols": len(symbols),
                "successful": successful,
                "results": indicator_results
            }
            
        except Exception as e:
            logger.error(f"{indicator_name} pipeline failed: {str(e)}", exc_info=True)
            raise Failure(f"{indicator_name} pipeline failed")
    
    return indicator_asset


# Create all indicator assets
atr_indicator = create_indicator_asset("ATR")
ema_indicator = create_indicator_asset("EMA")
sma_indicator = create_indicator_asset("SMA")
bollinger_indicator = create_indicator_asset("BOLLINGER")
macd_indicator = create_indicator_asset("MACD")
rsi_indicator = create_indicator_asset("RSI")