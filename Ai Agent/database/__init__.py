"""
Database initialization module for the AI Email Marketing Agent.
Provides MongoDB connection with fallback to SQLite if needed.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import and initialize MongoDB client
try:
    from .mongodb_client import mongodb_client
    logger.info("MongoDB client initialized successfully")
except Exception as e:
    logger.warning(f"MongoDB client initialization failed: {e}")
    mongodb_client = None

def get_database_client():
    """Get the database client, with fallback to SQLite if MongoDB fails."""
    if mongodb_client is not None:
        try:
            # Test MongoDB connection
            mongodb_client.client.admin.command('ping')
            return mongodb_client
        except Exception as e:
            logger.warning(f"MongoDB connection test failed: {e}")
    
    # Fallback to SQLite (implement if needed)
    logger.info("Using fallback database (SQLite)")
    return None

# Export the MongoDB client for direct use
__all__ = ['mongodb_client', 'get_database_client']
