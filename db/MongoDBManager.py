"""MongoDB manager for price operations."""
import logging
from datetime import datetime
from db.MongoDBConnection import MongoDBConnection
from db.mongo_config import MongoConfig

logger = logging.getLogger(__name__)


class MongoDBManager:
    """Manages MongoDB operations."""

    @staticmethod
    def insert_price(symbol: str, close_price: float) -> bool:
        """Insert price record into MongoDB."""
        try:
            conn = MongoDBConnection.get_connection()
            document = {
                "symbol": symbol,
                "close_price": close_price,
                "date": datetime.now().date().isoformat(),
                "timestamp": datetime.now()
            }

            cursor = conn.execute(
                MongoConfig.COLLECTION,
                "insert_one",
                document
            )
            cursor.execute()

            logger.info(f"Price inserted: {symbol} = ${close_price}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert price: {e}")
            return False

    @staticmethod
    def get_prices(symbol: str = None) -> list:
        """Retrieve prices from MongoDB."""
        try:
            conn = MongoDBConnection.get_connection()
            query = {"symbol": symbol} if symbol else {}

            cursor = conn.execute(MongoConfig.COLLECTION, "find", query)
            cursor.execute()
            results = cursor.fetchall()

            for record in results:
                record.pop("_id", None)

            return results
        except Exception as e:
            logger.error(f"Failed to retrieve prices: {e}")
            return []

    @staticmethod
    def create_indexes():
        """Create MongoDB indexes."""
        try:
            conn = MongoDBConnection.get_connection()
            collection = conn.collection(MongoConfig.COLLECTION)
            collection.create_index([("symbol", 1), ("date", 1)])
            logger.info("MongoDB indexes created")
        except Exception as e:
            logger.warning(f"Index creation: {e}")
