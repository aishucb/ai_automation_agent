from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class Engagement(BaseModel):
    """Engagement tracking model."""
    opened: int = Field(default=0, description="Number of times email was opened")
    clicked: int = Field(default=0, description="Number of times links were clicked")
    replied: int = Field(default=0, description="Number of times user replied")
    last_activity: Optional[datetime] = Field(default=None, description="Last activity timestamp")

class Contact(BaseModel):
    """Contact model for storing in MongoDB."""
    name: str = Field(..., description="School or principal name")
    email: EmailStr = Field(..., description="Validated email address")
    role: str = Field(..., description="Role (school/principal)")
    location: Optional[str] = Field(default=None, description="Location if provided")
    tags: List[str] = Field(default_factory=list, description="Segmentation tags")
    engagement: Engagement = Field(default_factory=Engagement, description="Engagement tracking")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

class ContactCreate(BaseModel):
    """Model for creating new contacts."""
    name: str
    email: EmailStr
    role: str
    location: Optional[str] = None

class ContactUpdate(BaseModel):
    """Model for updating contact engagement."""
    email: EmailStr
    event_type: str = Field(..., description="Type of engagement event (opened, clicked, replied)")

class ContactResponse(BaseModel):
    """Model for API responses."""
    success: bool
    message: str
    data: Optional[dict] = None
    count: Optional[int] = None

class IngestionResult(BaseModel):
    """Model for CSV ingestion results."""
    total_processed: int
    contacts_added: int
    duplicates_skipped: int
    invalid_emails: int
    errors: List[str] = Field(default_factory=list)
