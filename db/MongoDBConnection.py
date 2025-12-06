"""MongoDB connection handler using py-mongo-libs."""
import logging
# py-mongo-libs editable install maps src as top-level package
from src.core.connection import connect
from db.mongo_config import MongoConfig

logger = logging.getLogger(__name__)


class MongoDBConnection:
    """Manages MongoDB connection."""

    _conn = None

    @classmethod
    def connect(cls):
        """Establish MongoDB connection."""
        if cls._conn is None:
            try:
                cls._conn = connect(
                    dsn=MongoConfig.get_connection_uri(),
                    database=MongoConfig.DATABASE
                )
                logger.info("MongoDB connected")
            except Exception as e:
                logger.error(f"MongoDB connection failed: {e}")
                raise

    @classmethod
    def get_connection(cls):
        """Get MongoDB connection instance."""
        if cls._conn is None:
            cls.connect()
        return cls._conn

    @classmethod
    def close(cls):
        """Close MongoDB connection."""
        if cls._conn:
            cls._conn.close()
            cls._conn = None
            logger.info("MongoDB connection closed")
