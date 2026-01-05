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
    
    # Deploy 4 different deployments matching Dagster jobs EXACTLY
    deployments = [
        {
            "name": "deploy-cleanup-etl",
            "description": "Cleanup ETL Pipeline using Prefect native workers and service functions",
            "parameters": {"asset_type": "cleanup", "limit": 100}
        },
        {
            "name": "deploy-stocks-etl",
            "description": "Stocks ETL Pipeline using Prefect native workers and service functions",
            "parameters": {"asset_type": "stocks", "limit": 100}
        },
        {
            "name": "deploy-indices-etl",
            "description": "Indices ETL Pipeline using Prefect native workers and service functions",
            "parameters": {"asset_type": "indices", "limit": 100}
        },
        {
            "name": "deploy-futures-etl",
            "description": "Futures ETL Pipeline using Prefect native workers and service functions",
            "parameters": {"asset_type": "futures", "limit": 100}
        }
    ]
    
    for deployment in deployments:
        generic_asset_etl.from_source(
            source=".",
            entrypoint="prefect_app/flows/etl_price_flow.py:generic_asset_etl",
        ).deploy(
            name=deployment["name"],
            work_pool_name="price-pool",
            tags=["production", "etl", "prefect-native"],
            description=deployment["description"],
            parameters=deployment["parameters"],
        )
        print(f"Successfully deployed {deployment['name']}")
    
    print("All 4 deployments created successfully")