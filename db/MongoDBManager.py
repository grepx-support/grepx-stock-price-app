import logging
from datetime import datetime
from db.MongoDBConnection import MongoDBConnection
from db.mongo_config import MongoConfig

logger = logging.getLogger(__name__)


class MongoDBManager:
    """Manages MongoDB operations."""

    @staticmethod
    def insert_price(symbol: str, close_price: float) -> bool:
        """Insert a single price record."""
        try:
            conn = MongoDBConnection.get_connection()

            document = {
                "symbol": symbol,
                "close_price": close_price,
                "date": datetime.now().date().isoformat(),
                "timestamp": datetime.utcnow(),
            }

            cursor = conn.execute(
                MongoConfig.COLLECTION,
                "insert_one",
                document,
            )
            cursor.execute()

            return True
        except Exception as e:
            logger.error(f"Insert failed: {e}")
            return False

    @staticmethod
    def get_prices(symbol: str = None) -> list:
        """Retrieve prices."""
        try:
            conn = MongoDBConnection.get_connection()
            query = {"symbol": symbol} if symbol else {}

            cursor = conn.execute(
                MongoConfig.COLLECTION,
                "find",
                query,
            )
            cursor.execute()
            results = cursor.fetchall()

            for r in results:
                r.pop("_id", None)

            return results

        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            return []
        
    @staticmethod
    def find_all(collection_name: str) -> list:
        """Return all documents from a given collection."""
        try:
            conn = MongoDBConnection.get_connection()

            cursor = conn.execute(
                collection_name,
                "find",
                {}
            )
            cursor.execute()

            results = cursor.fetchall()

            # remove object IDs
            for r in results:
                r.pop("_id", None)

            return results

        except Exception as e:
            logger.error(f"find_all failed for {collection_name}: {e}")
            return []


    @staticmethod
    def bulk_insert(collection_name: str, rows: list[dict]) -> bool:
        """Bulk insert using execute_many (correct for py-mongo-libs)."""
        try:
            conn = MongoDBConnection.get_connection()

            for row in rows:
                row.pop("_id", None)  # Defensive cleanup

            cursor = conn.execute(
                collection_name,
                "insert_many",
                rows,
            )
            cursor.execute()

            return True
        except Exception as e:
            logger.error(f"Bulk insert failed for {collection_name}: {e}")
            return False
 

    @staticmethod
    def create_indexes():
        """Create indexes on symbol+date."""
        try:
            conn = MongoDBConnection.get_connection()
            collection = conn.collection(MongoConfig.COLLECTION)

            collection.create_index([("symbol", 1), ("date", 1)])

            logger.info("Indexes created")
        except Exception as e:
            logger.warning(f"Index creation failed: {e}")
