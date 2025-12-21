from prefect import flow
from price_app.src.main.prefect_app.tasks.price_tasks import fetch_raw_prices, compute_indicators, store_results


@flow(name="Price ETL Flow", log_prints=True)
def price_etl_flow(limit: int = 100) -> int:
    """
    1) fetch_raw_prices(limit)
    2) compute_indicators(...)
    3) store_results(...)
    Return inserted document count.
    """
    # Step 1: Fetch raw prices
    raw_prices = fetch_raw_prices(limit)
    
    # Step 2: Compute indicators
    results = compute_indicators(raw_prices)
    
    # Step 3: Store results
    inserted_count = store_results(results)
    
    return inserted_count


if __name__ == "__main__":
    # Run the flow locally for testing
    result = price_etl_flow(limit=10)
    print(f"Flow completed. Inserted {result} documents.")