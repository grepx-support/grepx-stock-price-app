from prefect import flow
import sys
import os
from pathlib import Path

# Add the main directory to the path to import modules
main_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(main_dir))

from prefect_app.tasks.price_tasks import fetch_raw_prices, compute_indicators, store_results


@flow(name="Generic Asset ETL Pipeline")
def generic_asset_etl(asset_type: str = "stocks", limit: int = 100):
    """Generic ETL for stocks/futures/indices"""
    raw_data = fetch_raw_prices(asset_type, limit)  # Parameterized service
    indicators = compute_indicators(raw_data)  # Generic service
    count = store_results(indicators)  # Parameterized service
    return {"asset_type": asset_type, "records_processed": count}


if __name__ == "__main__":
    # Run the flow locally for testing
    result = generic_asset_etl(asset_type="stocks", limit=10)
    print(f"Flow completed. Result: {result}")