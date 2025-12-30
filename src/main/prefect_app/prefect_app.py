from prefect import flow
import sys
from pathlib import Path

# Add the main directory to the path to import modules
main_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(main_dir))

from prefect_app.flows.etl_price_flow import generic_asset_etl


def load_prefect_flows():
    """Load all Prefect flows for the application."""
    flows = {
        "generic_asset_etl": generic_asset_etl,
    }
    return flows


if __name__ == "__main__":
    # Example usage
    flows = load_prefect_flows()
    print("Available flows:", list(flows.keys()))