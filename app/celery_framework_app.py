from omegaconf import OmegaConf
from celery_framework import create_app
from config.paths import CELERY_CONFIG

# Load YAML config
cfg = OmegaConf.load(CELERY_CONFIG)

celery_framework_app = create_app(cfg)

# Expose the celery instance
app = celery_framework_app.app

# For debugging
print("Loaded tasks:", celery_framework_app.list_tasks())
