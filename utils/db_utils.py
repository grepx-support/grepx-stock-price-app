"""MongoDB utility functions using MongoApp from app.main."""

import logging
from typing import List, Dict, Any
from app.main import mongo_app

logger = logging.getLogger(__name__)


def get_collection(collection_name: str):
    """Get a MongoDB collection."""
    return mongo_app.instance.connection.collection(collection_name)


def create_indexes():
    """Create indexes for collections."""
    try:
        db = mongo_app.instance.db
        
        logger.info("Creating MongoDB indexes...")
        # You can add specific index creation logic here
        logger.info("MongoDB indexes created")
    except Exception as e:
        logger.warning(f"Failed to create indexes: {e}")


def find_all(collection_name: str) -> List[Dict[str, Any]]:
    """
    Find all documents in a collection.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        List of documents as dictionaries
    """
    try:
        collection = get_collection(collection_name)
        cursor = collection.find({})
        documents = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        
        return documents
    except Exception as e:
        logger.error(f"Failed to find documents in {collection_name}: {e}", exc_info=True)
        return []


def bulk_upsert(collection_name: str, records: List[Dict[str, Any]]) -> int:
    """
    Bulk upsert records into a collection.
    Uses date as the unique key for upsert.
    
    Args:
        collection_name: Name of the collection
        records: List of record dictionaries
        
    Returns:
        Number of documents inserted/updated
    """
    if not records:
        return 0
    
    try:
        collection = get_collection(collection_name)
        inserted_count = 0
        
        for record in records:
            # Use date as unique identifier for upsert
            filter_doc = {'date': record.get('date')}
            if filter_doc['date'] is None:
                # If no date, insert as new document
                result = collection.insert_one(record)
                if result.inserted_id:
                    inserted_count += 1
            else:
                # Upsert based on date
                result = collection.update_one(
                    filter_doc,
                    {'$set': record},
                    upsert=True
                )
                if result.upserted_id or result.modified_count > 0:
                    inserted_count += 1
        
        logger.debug(f"Upserted {inserted_count} documents to {collection_name}")
        return inserted_count
        
    except Exception as e:
        logger.error(f"Failed to bulk upsert to {collection_name}: {e}", exc_info=True)
        return 0


def bulk_upsert_indicators(collection_name: str, records: List[Dict[str, Any]]) -> bool:
    """
    Bulk upsert indicator records into a collection.
    Uses date as the unique key for upsert.
    
    Args:
        collection_name: Name of the collection
        records: List of indicator record dictionaries
        
    Returns:
        True if successful, False otherwise
    """
    if not records:
        logger.warning(f"No records to upsert to {collection_name}")
        return False
    
    try:
        collection = get_collection(collection_name)
        inserted_count = 0
        
        for record in records:
            # Use date as unique identifier for upsert
            filter_doc = {'date': record.get('date')}
            if filter_doc['date'] is None:
                # If no date, insert as new document
                result = collection.insert_one(record)
                if result.inserted_id:
                    inserted_count += 1
            else:
                # Upsert based on date
                result = collection.update_one(
                    filter_doc,
                    {'$set': record},
                    upsert=True
                )
                if result.upserted_id or result.modified_count > 0:
                    inserted_count += 1
        
        logger.debug(f"Upserted {inserted_count} indicator documents to {collection_name}")
        return inserted_count > 0
        
    except Exception as e:
        logger.error(f"Failed to bulk upsert indicators to {collection_name}: {e}", exc_info=True)
        return False

