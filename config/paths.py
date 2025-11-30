from pathlib import Path

def get_project_root() -> Path:
    """
    ALWAYS returns the root directory of the project,
    whether running locally, in Docker, or on a server.
    """
    return Path(__file__).resolve().parents[2]


ROOT = get_project_root()

# --- Module roots ---
LIBS = ROOT / "libs"
PRICE_APP = ROOT / "price_app"

# --- Configs ---
CELERY_CONFIG = PRICE_APP / "config" / "celery_config.yaml"
DAGSTER_CONFIG = PRICE_APP / "config" / "dagster_config.yaml"

__all__ = [
    "ROOT",
    "PRICE_APP",
    "LIBS",
    "CELERY_CONFIG",
    "DAGSTER_CONFIG",
    "DAGSTER_HOME",
]