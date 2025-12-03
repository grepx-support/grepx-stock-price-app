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

HOST = _cfg.host
PORT = int(_cfg.port)
DATABASE = _cfg.database
USERNAME = _cfg.username
PASSWORD = _cfg.password
COLLECTION = _cfg.collection
AUTH_SOURCE = _cfg.auth_source


class MongoConfig:
    """MongoDB connection configuration."""

    HOST = HOST
    PORT = PORT
    DATABASE = DATABASE
    USERNAME = USERNAME
    PASSWORD = PASSWORD
    COLLECTION = COLLECTION
    AUTH_SOURCE = AUTH_SOURCE

    @classmethod
    def get_connection_uri(cls) -> str:
        """Build MongoDB connection URI."""
        return (
            f"mongodb://{cls.USERNAME}:{cls.PASSWORD}"
            f"@{cls.HOST}:{cls.PORT}/{cls.DATABASE}"
            f"?authSource={cls.AUTH_SOURCE}"
        )
