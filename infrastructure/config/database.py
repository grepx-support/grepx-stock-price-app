"""Database connection factory."""

from typing import Optional
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from src.core import Session

logger = logging.getLogger(__name__)


class DatabaseFactory:
    """Factory for creating database connections."""

    @staticmethod
    def create_mongo_collection(connection_string: str, db_name: str, collection_name: str) -> AsyncIOMotorCollection:
        """
        Create a MongoDB collection.
        
        Args:
            connection_string: MongoDB connection string
            db_name: Database name
            collection_name: Collection name
        
        Returns:
            MongoDB collection object
        """
        try:
            client = AsyncIOMotorClient(connection_string)
            db = client[db_name]
            collection = db[collection_name]
            return collection
        except Exception as e:
            logger.error(f"Error creating MongoDB collection: {e}")
            raise

    @staticmethod
    def create_orm_session(connection_string: str) -> Session:
        """
        Create an ORM session.
        
        Args:
            connection_string: Database connection string
        
        Returns:
            ORM session
        """
        try:
            session = Session.from_connection_string(connection_string)
            return session
        except Exception as e:
            logger.error(f"Error creating ORM session: {e}")
            raise

