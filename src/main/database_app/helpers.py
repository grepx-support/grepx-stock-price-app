"""Database app helper functions."""

from servers.app import get_connection, conn_config


def get_database(db_name: str = None, conn_id: str = None):
    """Get database connection."""
    conn_id = conn_id or conn_config.database
    db = get_connection(conn_id)
    return db.get_database(db_name) if db_name else db.get_client()


def get_collection(db_name: str, collection_name: str, conn_id: str = None):
    """Get collection from database."""
    conn_id = conn_id or conn_config.database
    return get_connection(conn_id).get_collection(db_name, collection_name)
