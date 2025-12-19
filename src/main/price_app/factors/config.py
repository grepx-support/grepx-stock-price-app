from omegaconf import OmegaConf

cfg = OmegaConf.load("resources/resources.yaml")

# Column names from resources
high = cfg.columns.high
low = cfg.columns.low
close = cfg.columns.close
open = cfg.columns.open
volume = cfg.columns.volume
