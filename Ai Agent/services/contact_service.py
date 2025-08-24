import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Optional
from email_validator import validate_email, EmailNotValidError
from models.contact import Contact, ContactCreate, IngestionResult

logger = logging.getLogger(__name__)

class ContactService:
    """Service for managing contacts and segmentation."""
    
    def __init__(self):
        self.collection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection with fallback."""
        try:
            from database.mongodb_client import mongodb_client
            self.collection = mongodb_client.get_collection()
            logger.info("MongoDB connection established for ContactService")
        except Exception as e:
            logger.warning(f"MongoDB connection failed for ContactService: {e}")
            logger.info("ContactService will use in-memory storage")
            self.collection = None
    
    def _normalize_email(self, email: str) -> Optional[str]:
        """Normalize and validate email address."""
        try:
            if not email or pd.isna(email):
                return None
            
            email = str(email).strip().lower()
            validated_email = validate_email(email)
            return validated_email.email
        except EmailNotValidError:
            return None
        except Exception as e:
            logger.error(f"Error validating email {email}: {e}")
            return None
    
    def _map_csv_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Map CSV columns to our contact schema."""
        column_mapping = {}
        
        # Common column name variations
        name_columns = ['name', 'school name', 'principal', 'school', 'contact name', 'full name']
        email_columns = ['email', 'email id', 'email address', 'email_address', 'emailid']
        role_columns = ['role', 'position', 'title', 'designation']
        location_columns = ['location', 'city', 'state', 'address', 'school location']
        
        # Find matching columns (case-insensitive)
        for col in df.columns:
            col_lower = col.lower().strip()
            
            if col_lower in name_columns and 'name' not in column_mapping:
                column_mapping['name'] = col
            elif col_lower in email_columns and 'email' not in column_mapping:
                column_mapping['email'] = col
            elif col_lower in role_columns and 'role' not in column_mapping:
                column_mapping['role'] = col
            elif col_lower in location_columns and 'location' not in column_mapping:
                column_mapping['location'] = col
        
        return column_mapping
    
    def ingest_csv(self, file_path: str) -> IngestionResult:
        """Ingest contacts from CSV file into MongoDB."""
        result = IngestionResult(
            total_processed=0,
            contacts_added=0,
            duplicates_skipped=0,
            invalid_emails=0
        )
        
        if not self.collection:
            logger.warning("MongoDB not available - CSV ingestion not supported")
            result.total_processed = 0
            return result
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            result.total_processed = len(df)
            
            # Map columns
            column_mapping = self._map_csv_columns(df)
            
            if 'email' not in column_mapping:
                raise ValueError("No email column found in CSV")
            
            if 'name' not in column_mapping:
                raise ValueError("No name column found in CSV")
            
            logger.info(f"Processing {len(df)} contacts from {file_path}")
            logger.info(f"Column mapping: {column_mapping}")
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    # Extract data
                    email = self._normalize_email(row[column_mapping['email']])
                    name = str(row[column_mapping['name']]).strip()
                    
                    if not email or not name:
                        result.invalid_emails += 1
                        continue
                    
                    # Determine role
                    role = "school"
                    if 'role' in column_mapping:
                        role_value = str(row[column_mapping['role']]).strip()
                        if role_value and role_value.lower() in ['principal', 'head', 'director']:
                            role = "principal"
                    
                    # Extract location
                    location = None
                    if 'location' in column_mapping:
                        location_value = str(row[column_mapping['location']]).strip()
                        if location_value and not pd.isna(location_value):
                            location = location_value
                    
                    # Create contact document
                    contact_data = {
                        "name": name,
                        "email": email,
                        "role": role,
                        "location": location,
                        "tags": [],
                        "engagement": {
                            "opened": 0,
                            "clicked": 0,
                            "replied": 0,
                            "last_activity": None
                        },
                        "created_at": datetime.utcnow()
                    }
                    
                    # Insert into MongoDB
                    self.collection.insert_one(contact_data)
                    result.contacts_added += 1
                    
                except Exception as e:
                    if "duplicate key error" in str(e).lower():
                        result.duplicates_skipped += 1
                    else:
                        result.errors.append(f"Row {index + 1}: {str(e)}")
            
            logger.info(f"CSV ingestion completed: {result.contacts_added} added, "
                       f"{result.duplicates_skipped} duplicates, {result.invalid_emails} invalid")
            
        except Exception as e:
            logger.error(f"Error ingesting CSV file {file_path}: {e}")
            result.errors.append(str(e))
        
        return result
    
    def update_contact_engagement(self, email: str, event_type: str) -> bool:
        """Update contact engagement and add appropriate tags."""
        if not self.collection:
            logger.warning("MongoDB not available - engagement update not supported")
            return False
        
        try:
            # Validate event type
            valid_events = ['opened', 'clicked', 'replied']
            if event_type not in valid_events:
                logger.error(f"Invalid event type: {event_type}")
                return False
            
            # Define tag mapping
            tag_mapping = {
                'opened': 'engaged',
                'clicked': 'high-interest',
                'replied': 'priority'
            }
            
            # Add tag if not already present
            tag_to_add = tag_mapping[event_type]
            
            # Perform update
            result = self.collection.update_one(
                {"email": email.lower()},
                {"$inc": {f"engagement.{event_type}": 1},
                 "$set": {"engagement.last_activity": datetime.utcnow()},
                 "$addToSet": {"tags": tag_to_add}}
            )
            
            if result.matched_count > 0:
                logger.info(f"Updated engagement for {email}: {event_type}")
                return True
            else:
                logger.warning(f"Contact not found: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating engagement for {email}: {e}")
            return False
    
    def get_contacts_by_tag(self, tag: str) -> List[Dict]:
        """Get all contacts with a specific tag."""
        if not self.collection:
            logger.warning("MongoDB not available - returning empty contact list")
            return []
        
        try:
            contacts = list(self.collection.find({"tags": tag}))
            logger.info(f"Found {len(contacts)} contacts with tag '{tag}'")
            return contacts
        except Exception as e:
            logger.error(f"Error fetching contacts by tag {tag}: {e}")
            return []
    
    def get_contact_counts_by_tag(self) -> Dict[str, int]:
        """Get counts of contacts for each tag."""
        if not self.collection:
            logger.warning("MongoDB not available - returning empty tag counts")
            return {'engaged': 0, 'high-interest': 0, 'priority': 0}
        
        try:
            pipeline = [
                {"$unwind": "$tags"},
                {"$group": {"_id": "$tags", "count": {"$sum": 1}}}
            ]
            
            results = list(self.collection.aggregate(pipeline))
            tag_counts = {result["_id"]: result["count"] for result in results}
            
            # Ensure all expected tags are present
            expected_tags = ['engaged', 'high-interest', 'priority']
            for tag in expected_tags:
                if tag not in tag_counts:
                    tag_counts[tag] = 0
            
            return tag_counts
            
        except Exception as e:
            logger.error(f"Error getting tag counts: {e}")
            return {'engaged': 0, 'high-interest': 0, 'priority': 0}
    
    def get_all_contacts(self, limit: int = 100) -> List[Dict]:
        """Get all contacts with optional limit."""
        try:
            contacts = list(self.collection.find().limit(limit))
            return contacts
        except Exception as e:
            logger.error(f"Error fetching contacts: {e}")
            return []
    
    def get_contact_by_email(self, email: str) -> Optional[Dict]:
        """Get a specific contact by email."""
        try:
            contact = self.collection.find_one({"email": email.lower()})
            return contact
        except Exception as e:
            logger.error(f"Error fetching contact {email}: {e}")
            return None
