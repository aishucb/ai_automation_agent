import os
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB Atlas connection client for the email agent."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.collection: Optional[Collection] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB Atlas."""
        try:
            # Get configuration from environment variables
            mongodb_uri = os.getenv('MONGODB_URI')
            database_name = os.getenv('MONGODB_DATABASE', 'email_agent')
            collection_name = os.getenv('MONGODB_COLLECTION', 'contacts')
            
            if not mongodb_uri:
                raise ValueError("MONGODB_URI environment variable is required")
            
            # MongoDB connection options to fix SSL issues
            connection_options = {
                'serverSelectionTimeoutMS': 5000,  # 5 second timeout
                'connectTimeoutMS': 10000,         # 10 second connection timeout
                'socketTimeoutMS': 5000,           # 5 second socket timeout
                'maxPoolSize': 10,                 # Connection pool size
                'minPoolSize': 1,                  # Minimum connections in pool
                'maxIdleTimeMS': 30000,            # Max idle time for connections
                'retryWrites': True,               # Enable retry writes
                'retryReads': True,                # Enable retry reads
                'tlsAllowInvalidCertificates': True,  # Allow invalid certificates
                'tlsAllowInvalidHostnames': True,     # Allow invalid hostnames
            }
            
            # Create MongoDB client with SSL options
            self.client = MongoClient(mongodb_uri, **connection_options)
            
            # Test connection with timeout
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas")
            
            # Get database and collection
            self.database = self.client[database_name]
            self.collection = self.database[collection_name]
            
            # Create indexes
            self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            # Try alternative connection method without SSL verification
            try:
                logger.info("Attempting alternative connection method...")
                self._connect_without_ssl_verification(mongodb_uri, database_name, collection_name)
            except Exception as alt_e:
                logger.error(f"Alternative connection also failed: {alt_e}")
                raise
    
    def _connect_without_ssl_verification(self, mongodb_uri: str, database_name: str, collection_name: str):
        """Alternative connection method with minimal SSL verification."""
        try:
            # Remove SSL parameters from URI and add them as options
            if '?' in mongodb_uri:
                base_uri = mongodb_uri.split('?')[0]
            else:
                base_uri = mongodb_uri
            
            # Add SSL parameters to URI
            if '?' in mongodb_uri:
                separator = '&'
            else:
                separator = '?'
            
            ssl_uri = f"{base_uri}{separator}tlsAllowInvalidCertificates=true&tlsAllowInvalidHostnames=true&retryWrites=true&w=majority"
            
            # Create client with minimal options
            self.client = MongoClient(
                ssl_uri,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=15000,
                socketTimeoutMS=10000
            )
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas using alternative method")
            
            # Get database and collection
            self.database = self.client[database_name]
            self.collection = self.database[collection_name]
            
            # Create indexes
            self._create_indexes()
            
        except Exception as e:
            logger.error(f"Alternative connection method failed: {e}")
            raise
    
    def _create_indexes(self):
        """Create necessary indexes for the contacts collection."""
        try:
            # Create unique index on email field to prevent duplicates
            self.collection.create_index("email", unique=True)
            
            # Create indexes for better query performance
            self.collection.create_index("tags")
            self.collection.create_index("created_at")
            self.collection.create_index("engagement.last_activity")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            # Don't raise here as indexes are not critical for basic functionality
    
    def get_collection(self) -> Collection:
        """Get the contacts collection."""
        if self.collection is None:
            raise RuntimeError("MongoDB connection not established")
        return self.collection
    
    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global MongoDB client instance
mongodb_client = MongoDBClient()