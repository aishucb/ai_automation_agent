from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class CampaignContext(BaseModel):
    """Campaign context data structure."""
    title: str = Field(..., description="Campaign title")
    objective: str = Field(..., description="Campaign objective")
    date: str = Field(..., description="Event date")
    location: str = Field(..., description="Event location")
    target_audience: List[str] = Field(..., description="Target audience segments")
    key_points: List[str] = Field(..., description="Key campaign points")
    call_to_action: str = Field(..., description="Call to action text")
    registration_link: Optional[str] = Field(default=None, description="Registration link")

class EmailContent(BaseModel):
    """Email content structure."""
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content (HTML)")
    audience_segment: str = Field(..., description="Target audience segment")
    email_type: str = Field(..., description="Type of email (invite, reminder, etc.)")
    version: str = Field(default="v1", description="Content version")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    placeholders: List[str] = Field(default_factory=list, description="Available placeholders")

class EmailPerformance(BaseModel):
    """Email performance metrics."""
    campaign_name: str = Field(..., description="Campaign name")
    email_type: str = Field(..., description="Email type")
    audience_segment: str = Field(..., description="Target audience")
    version: str = Field(..., description="Content version")
    sent_count: int = Field(default=0, description="Number of emails sent")
    open_count: int = Field(default=0, description="Number of emails opened")
    click_count: int = Field(default=0, description="Number of clicks")
    reply_count: int = Field(default=0, description="Number of replies")
    open_rate: float = Field(default=0.0, description="Open rate percentage")
    click_rate: float = Field(default=0.0, description="Click rate percentage")
    reply_rate: float = Field(default=0.0, description="Reply rate percentage")
    sent_at: datetime = Field(default_factory=datetime.utcnow, description="Sent timestamp")
    performance_data: Dict[str, Any] = Field(default_factory=dict, description="Additional performance data")

class ContentGenerationRequest(BaseModel):
    """Request for content generation."""
    campaign_name: str = Field(..., description="Campaign name")
    audience_segment: str = Field(..., description="Target audience segment")
    email_type: str = Field(..., description="Email type")
    tone: Optional[str] = Field(default="professional", description="Content tone")
    custom_instructions: Optional[str] = Field(default=None, description="Custom generation instructions")

class ContentRefinementRequest(BaseModel):
    """Request for content refinement."""
    campaign_name: str = Field(..., description="Campaign name")
    email_type: str = Field(..., description="Email type to refine")
    audience_segment: Optional[str] = Field(default=None, description="Specific audience segment")
    performance_threshold: float = Field(default=0.1, description="Minimum performance improvement threshold")
