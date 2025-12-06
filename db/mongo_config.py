"""MongoDB configuration."""
from omegaconf import OmegaConf
from pathlib import Path


def _load_db_config():
    """Load database config from YAML file."""
    config_file = Path(__file__).parent.parent / "config" / "database_config.yaml"
    if not config_file.exists():
        raise FileNotFoundError(f"database_config.yaml not found at {config_file}")
    cfg = OmegaConf.load(str(config_file))
    return cfg.mongodb


_cfg = _load_db_config()

# Get connection type (local or atlas)
CONNECTION_TYPE = _cfg.connection_type
DATABASE = _cfg.database
COLLECTION = _cfg.collection


class MongoConfig:
    """MongoDB connection configuration."""

    CONNECTION_TYPE = CONNECTION_TYPE
    DATABASE = DATABASE
    COLLECTION = COLLECTION

    # Local MongoDB config
    HOST = _cfg.local.host if CONNECTION_TYPE == "local" else None
    PORT = int(_cfg.local.port) if CONNECTION_TYPE == "local" else None
    USERNAME = _cfg.local.username if CONNECTION_TYPE == "local" else None
    PASSWORD = _cfg.local.password if CONNECTION_TYPE == "local" else None
    AUTH_SOURCE = _cfg.local.auth_source if CONNECTION_TYPE == "local" else None

    # Atlas MongoDB config
    ATLAS_CONNECTION_STRING = _cfg.atlas.connection_string if CONNECTION_TYPE == "atlas" else None

    @classmethod
    def get_connection_uri(cls) -> str:
        """Build MongoDB connection URI based on connection type."""
        if cls.CONNECTION_TYPE == "atlas":
            return cls.ATLAS_CONNECTION_STRING
        else:  # local
            return (
                f"mongodb://{cls.USERNAME}:{cls.PASSWORD}"
                f"@{cls.HOST}:{cls.PORT}/{cls.DATABASE}"
                f"?authSource={cls.AUTH_SOURCE}"
            )
