import os
from omegaconf import OmegaConf

def load_prefect_flows():
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'app.yaml')
    config = OmegaConf.load(config_path)
    
    # Import and return flows
    from .flows.etl_price_flow import price_etl_flow
    return {"price_etl_flow": price_etl_flow}