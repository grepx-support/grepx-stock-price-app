import sys
import os
from pathlib import Path

# Add the main directory to Python path
main_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(main_dir))

# Change working directory to main
os.chdir(main_dir)

if __name__ == "__main__":
    # Import after setting up the path
    from prefect_app.flows.etl_price_flow import generic_asset_etl
    
    # Deploy using serve method directly which is the Prefect 3 way
    # This creates a deployment that runs from the local source
    generic_asset_etl.from_source(
        source=".",
        entrypoint="prefect_app/flows/etl_price_flow.py:generic_asset_etl",
    ).deploy(
        name="generic-asset-etl",
        work_pool_name="price-pool",
        tags=["production", "generic", "celery-coordination"],
        description="Generic ETL Pipeline for stocks, futures, and indices using configuration and Celery coordination",
        parameters={"asset_type": "stocks", "limit": 100},
    )
    
    print("Successfully deployed generic_asset_etl from local source")