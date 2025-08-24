from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class CampaignStatus(str, Enum):
    """Campaign status enumeration."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EmailStatus(str, Enum):
    """Email delivery status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"
    OPENED = "opened"
    CLICKED = "clicked"
    REPLIED = "replied"

class WorkflowPlan(BaseModel):
    """Workflow plan with scheduled dates for different email types."""
    invite: Optional[datetime] = Field(None, description="Invite email schedule date")
    reminder: Optional[datetime] = Field(None, description="Reminder email schedule date")
    thank_you: Optional[datetime] = Field(None, description="Thank you email schedule date")
    follow_up: Optional[datetime] = Field(None, description="Follow up email schedule date")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class CampaignTargets(BaseModel):
    """Campaign targets and goals."""
    total_registrations: int = Field(0, description="Target number of registrations")
    total_emails_sent: int = Field(0, description="Target number of emails to send")
    open_rate_target: float = Field(0.25, description="Target open rate (0.0-1.0)")
    click_rate_target: float = Field(0.05, description="Target click rate (0.0-1.0)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_registrations": 1000,
                "total_emails_sent": 5000,
                "open_rate_target": 0.25,
                "click_rate_target": 0.05
            }
        }

class Campaign(BaseModel):
    """Campaign model for workflow automation."""
    name: str = Field(..., description="Campaign name")
    title: str = Field(..., description="Campaign title")
    description: Optional[str] = Field(None, description="Campaign description")
    status: CampaignStatus = Field(CampaignStatus.DRAFT, description="Current campaign status")
    workflow_plan: WorkflowPlan = Field(..., description="Workflow schedule")
    targets: CampaignTargets = Field(..., description="Campaign targets")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="Campaign creator")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EmailLog(BaseModel):
    """Email delivery log entry."""
    campaign_name: str = Field(..., description="Campaign name")
    email: str = Field(..., description="Recipient email")
    email_type: str = Field(..., description="Type of email (invite, reminder, etc.)")
    status: EmailStatus = Field(EmailStatus.PENDING, description="Email status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Log timestamp")
    message_id: Optional[str] = Field(None, description="Gmail message ID")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: int = Field(0, description="Number of retry attempts")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CampaignStatusResponse(BaseModel):
    """Campaign status response for dashboard."""
    campaign_name: str
    status: CampaignStatus
    targets: CampaignTargets
    current_metrics: Dict[str, Any]
    progress_percentage: float
    next_scheduled_action: Optional[datetime]
    total_emails_sent: int
    total_emails_pending: int
    open_rate: float
    click_rate: float
    registration_count: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class WorkflowScheduleRequest(BaseModel):
    """Request model for scheduling a campaign workflow."""
    campaign_name: str
    workflow_plan: WorkflowPlan
    targets: CampaignTargets
    audience_segments: List[str] = Field(default_factory=list, description="Target audience segments")

class DashboardMetrics(BaseModel):
    """Dashboard metrics summary."""
    total_campaigns: int
    active_campaigns: int
    total_emails_sent: int
    total_emails_pending: int
    average_open_rate: float
    average_click_rate: float
    total_registrations: int
    campaigns_by_status: Dict[str, int]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_campaigns": 5,
                "active_campaigns": 2,
                "total_emails_sent": 1500,
                "total_emails_pending": 300,
                "average_open_rate": 0.28,
                "average_click_rate": 0.06,
                "total_registrations": 450,
                "campaigns_by_status": {
                    "active": 2,
                    "paused": 1,
                    "completed": 2
                }
            }
        }
