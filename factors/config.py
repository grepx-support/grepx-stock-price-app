from omegaconf import OmegaConf

cfg = OmegaConf.load("config/config.yaml")

# Column names from config
high = cfg.columns.high
low = cfg.columns.low
close = cfg.columns.close
open = cfg.columns.open
volume = cfg.columns.volume
