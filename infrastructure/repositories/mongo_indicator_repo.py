"""MongoDB implementation of indicator repository."""

from typing import List, Dict, Any, Optional
import logging
from application.ports.repositories import IIndicatorRepository

logger = logging.getLogger(__name__)


class MongoIndicatorRepository(IIndicatorRepository):
    """MongoDB implementation of indicator repository."""

    def __init__(self, collection):
        """
        Initialize repository with a MongoDB collection.
        
        Args:
            collection: MongoDB collection object
        """
        self.collection = collection

    async def save_indicator(self, symbol: str, factor: str, date: str, indicator_data: Dict[str, Any]) -> bool:
        """Save a single indicator record."""
        try:
            await self.collection.update_one(
                {"symbol": symbol, "date": date, "factor": factor},
                {"$set": indicator_data},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error saving indicator {factor} for {symbol} on {date}: {e}")
            return False

    async def save_indicators(self, indicator_records: List[Dict[str, Any]]) -> int:
        """Save multiple indicator records."""
        if not indicator_records:
            return 0
        
        inserted = 0
        for record in indicator_records:
            try:
                symbol = record.get("symbol", "UNKNOWN")
                date = record.get("date", "")
                factor = record.get("factor", "")
                await self.collection.update_one(
                    {"symbol": symbol, "date": date, "factor": factor},
                    {"$set": record},
                    upsert=True
                )
                inserted += 1
            except Exception as e:
                logger.warning(f"Failed to store indicator record: {e}")
                continue
        
        return inserted

    async def get_indicators(self, symbol: str, factor: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get indicator records for a symbol and factor."""
        query = {"symbol": symbol, "factor": factor}
        
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
            logger.error(f"Error getting indicators for {symbol}/{factor}: {e}")
            return []

