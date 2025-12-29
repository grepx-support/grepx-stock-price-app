# price_app/src/main/prefect_app/deployments/deploy_price_flows.py

import sys
import os
from pathlib import Path

# Add the main directory to the path to import modules
main_dir = Path(__file__).parent.parent.parent  # Go to the main directory
sys.path.insert(0, str(main_dir))

from prefect_app.flows.etl_price_flow import generic_asset_etl


if __name__ == "__main__":
    generic_asset_etl.from_source(
        source=".",  # Current directory
        entrypoint="prefect_app/flows/etl_price_flow.py:generic_asset_etl",
    ).deploy(
        name="generic-asset-etl",
        work_pool_name="price-pool",
        tags=["production", "generic"],
        parameters={"asset_type": "stocks"},  # Default
    )
    
    print("Successfully deployed generic_asset_etl")