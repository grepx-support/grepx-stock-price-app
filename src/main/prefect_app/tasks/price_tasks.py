import os
from typing import Dict, List
from prefect import task
from pathlib import Path
from omegaconf import OmegaConf


@task(name="config_prices")
def config_prices(asset_type: str = "stocks") -> Dict:
    """
    Get price fetching configuration from asset.yaml
    """
    # Load configuration from asset.yaml
    config_dir = Path(__file__).parent.parent.parent / "resources"
    config_path = config_dir / "asset.yaml"
    config = OmegaConf.load(config_path)
    
    # Extract the configuration for the specified asset type
    asset_config = config.asset_types.get(asset_type, {})
    symbols = asset_config.get("symbols", [])
    
    # Get date range from config
    start_date = config.get("start_date", "2021-01-01")
    end_date = config.get("end_date", "2025-12-01")
    
    return {
        "symbols": symbols,
        "start_date": start_date,
        "end_date": end_date,
        "fetch_timeout": asset_config.get("fetch_timeout", 120),
        "asset_type": asset_type
    }


@task(name="config_indicators")
def config_indicators(asset_type: str = "stocks") -> Dict:
    """
    Get indicator computation configuration from asset.yaml
    """
    # Load configuration from asset.yaml
    config_dir = Path(__file__).parent.parent.parent / "resources"
    config_path = config_dir / "asset.yaml"
    config = OmegaConf.load(config_path)
    
    # Return the indicators configuration
    indicators_config = OmegaConf.to_container(config.indicators, resolve=True)
    
    return {
        "indicators": indicators_config,
        "asset_type": asset_type
    }


@task(name="fetch_data")
def fetch_data(config_data: Dict) -> List[Dict]:
    """
    Fetch data using database_app services
    """
    from database_app.services.stock_services import fetch_stock_price_data
    from servers.utils.logger import get_logger
    
    logger = get_logger(__name__)
    
    symbols = config_data["symbols"]
    start_date = config_data["start_date"]
    end_date = config_data["end_date"]
    
    all_records = []
    for symbol in symbols:
        result = fetch_stock_price_data(symbol, start_date, end_date)
        if result["status"] == "success" and result["records"]:
            all_records.extend(result["records"])
        else:
            logger.warning(f"No data from service for {symbol}, skipping this symbol")
    
    logger.info(f"Fetched {len(all_records)} records for {len(symbols)} symbols")
    return all_records


@task(name="store_data")
def store_data(price_data: List[Dict], asset_type: str = "stocks") -> int:
    """
    Store data using database_app services
    """
    if not price_data:
        print("No results to store")
        return 0
    from database_app.services.stock_services import store_stock_price_data
    from database_app.services.naming import naming
    from main import get_collection
    from servers.utils.logger import get_logger
    logger = get_logger(__name__)

    # Get collection using the get_collection function
    db_name = naming.get_analysis_db_name(asset_type)

    # Group data by symbol to store each symbol in its own table
    data_by_symbol = {}
    for record in price_data:
        symbol = record.get("symbol", "DEFAULT")
        if symbol not in data_by_symbol:
            data_by_symbol[symbol] = []
        data_by_symbol[symbol].append(record)

    total_stored = 0
    for symbol, symbol_data in data_by_symbol.items():
        # Get collection name using naming convention
        collection_name = naming.get_price_collection_name(asset_type, symbol)

        try:
            # Format data as expected by the service function
            formatted_data = {
                "symbol": symbol,
                "records": symbol_data,
                "status": "success",
                "count": len(symbol_data)
            }

            # Get the appropriate collection
            collection = get_collection(db_name, collection_name)
            
            # Use the existing service function to store the data
            result = store_stock_price_data(formatted_data, collection)

            stored_count = result.get("count", 0) if result.get("status") == "success" else 0
            logger.info(f"Stored {stored_count} price records in collection '{collection_name}'")
            total_stored += stored_count

        except Exception as e:
            logger.error(f"Error storing price data for {symbol}: {str(e)}")

    return total_stored


@task(name="compute_indicators")
def compute_indicators(price_data: List[Dict], indicators_config: Dict, asset_type: str = "stocks") -> List[Dict]:
    """
    Compute indicators using database_app services
    """
    if not price_data:
        return []

    from database_app.services.indicator_services import compute_single_factor
    from servers.utils.logger import get_logger
    logger = get_logger(__name__)
    # Get indicators to compute
    indicators = indicators_config.get("indicators", {})

    # Group data by symbol to compute indicators for each symbol separately
    data_by_symbol = {}
    for record in price_data:
        symbol = record.get("symbol", "DEFAULT")
        if symbol not in data_by_symbol:
            data_by_symbol[symbol] = []
        data_by_symbol[symbol].append(record)

    results = []
    for symbol, symbol_data in data_by_symbol.items():
        for indicator_name in indicators.keys():
            # Compute indicator using the service
            indicator_config = indicators.get(indicator_name, {})
            indicator_results = compute_single_factor(symbol, indicator_name, symbol_data, indicator_config)
            logger.info(f"Computed {indicator_name} for {symbol}: {len(indicator_results)} records")
            # Add indicator name to results for tracking
            for result in indicator_results:
                result["indicator_type"] = indicator_name
                results.append(result)

    return results


@task(name="store_indicators")
def store_indicators(indicator_data: List[Dict], asset_type: str = "stocks") -> int:
    """
    Store indicators using database_app services
    """
    if not indicator_data:
        print("No indicator results to store")
        return 0
    
    from database_app.services.indicator_services import store_single_factor
    from database_app.services.naming import naming
    from main import get_collection
    from servers.utils.logger import get_logger
    logger = get_logger(__name__)
    # Group by symbol and indicator type to store each combination separately
    indicators_by_symbol_and_type = {}
    for item in indicator_data:
        symbol = item.get("symbol", "DEFAULT")
        indicator_type = item.get("indicator_type", "unknown")
        key = f"{symbol}_{indicator_type}"

        if key not in indicators_by_symbol_and_type:
            indicators_by_symbol_and_type[key] = {
                "symbol": symbol,
                "indicator_type": indicator_type,
                "data": []
            }
        indicators_by_symbol_and_type[key]["data"].append(item)

    db_name = naming.get_analysis_db_name(asset_type)

    total_stored = 0
    for key, item_info in indicators_by_symbol_and_type.items():
        symbol = item_info["symbol"]
        indicator_type = item_info["indicator_type"]
        data = item_info["data"]

        if not data:
            continue
        # Get collection name using naming convention
        collection_name = naming.get_indicator_collection_name(asset_type, symbol, indicator_type)
        try:
            # Get the appropriate collection
            collection = get_collection(db_name, collection_name)
            
            # Use the existing service function to store the indicators
            result = store_single_factor(data, collection)
            stored_count = result.get("count", 0) if result.get("status") == "success" else 0
            logger.info(f"Stored {stored_count} {indicator_type} indicator records in collection '{collection_name}'")
            total_stored += stored_count
        except Exception as e:
            logger.error(f"Error storing {indicator_type} indicators for {symbol}: {e}")
    
    return total_stored