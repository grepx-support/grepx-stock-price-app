from prefect import flow
import sys
from pathlib import Path

# Add the main directory to the path to import modules
main_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(main_dir))

from prefect_app.tasks.price_tasks import (
    config_prices,
    config_indicators,
    fetch_data,
    store_data,
    compute_indicators,
    store_indicators
)


@flow(name="Generic Asset ETL Pipeline")
def generic_asset_etl(asset_type: str = "stocks", limit: int = 100):
    """Generic ETL for stocks/futures/indices using service functions"""
    # Step 1: Get configurations
    prices_config = config_prices(asset_type)
    indicators_config = config_indicators(asset_type)
    
    # Step 2: Fetch and store data
    price_data = fetch_data(prices_config)
    stored_count = store_data(price_data, asset_type)
    
    # Step 3: Compute and store indicators
    indicator_data = compute_indicators(price_data, indicators_config, asset_type)
    indicators_stored = store_indicators(indicator_data, asset_type)
    
    return {
        "asset_type": asset_type,
        "price_records_stored": stored_count,
        "indicator_records_stored": indicators_stored,
        "total_records_processed": len(price_data) if price_data else 0
    }


if __name__ == "__main__":
    # Run the flow locally for testing
    result = generic_asset_etl(asset_type="stocks", limit=10)
    print(f"Flow completed. Result: {result}")