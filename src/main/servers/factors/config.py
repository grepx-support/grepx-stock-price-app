from omegaconf import OmegaConf
from pathlib import Path

# Load asset configuration which contains all factor/asset-related configurations
asset_config_path = Path(__file__).parent.parent.parent / "resources" / "asset.yaml"
cfg = OmegaConf.load(str(asset_config_path))

# Column names from config
high = cfg.columns.high
low = cfg.columns.low
close = cfg.columns.close
open = cfg.columns.open
volume = cfg.columns.volume
