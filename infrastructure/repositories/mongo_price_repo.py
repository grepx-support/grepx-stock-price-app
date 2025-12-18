"""MongoDB implementation of price repository."""

from typing import List, Dict, Any, Optional
import logging
from application.ports.repositories import IPriceRepository

logger = logging.getLogger(__name__)


class MongoPriceRepository(IPriceRepository):
    """MongoDB implementation of price repository."""

    def __init__(self, collection):
        """
        Initialize repository with a MongoDB collection.
        
        Args:
            collection: MongoDB collection object
        """
        self.collection = collection

    async def save_price(self, symbol: str, date: str, price_data: Dict[str, Any]) -> bool:
        """Save a single price record."""
        try:
            await self.collection.update_one(
                {"symbol": symbol, "date": date},
                {"$set": price_data},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error saving price for {symbol} on {date}: {e}")
            return False

    async def save_prices(self, price_records: List[Dict[str, Any]]) -> int:
        """Save multiple price records."""
        if not price_records:
            return 0
        
        inserted = 0
        for record in price_records:
            try:
                symbol = record.get("symbol", "UNKNOWN")
                date = record.get("date", "")
                await self.collection.update_one(
                    {"symbol": symbol, "date": date},
                    {"$set": record},
                    upsert=True
                )
                inserted += 1
            except Exception as e:
                logger.warning(f"Failed to store price record: {e}")
                continue
        
        return inserted

    async def get_prices(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get price records for a symbol."""
        query = {"symbol": symbol}
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            if date_query:
                query["date"] = date_query
        
        try:
            cursor = self.collection.find(query).sort("date", 1)
            records = await cursor.to_list(length=None)
            # Convert ObjectId to string for JSON serialization
            for record in records:
                if '_id' in record:
                    record['_id'] = str(record['_id'])
            return records
        except Exception as e:
            logger.error(f"Error getting prices for {symbol}: {e}")
            return []

