import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from database.mongodb_client import mongodb_client
from services.gemini_service import GeminiService
from models.campaign import (
    CampaignContext, EmailContent, EmailPerformance, 
    ContentGenerationRequest, ContentRefinementRequest
)

logger = logging.getLogger(__name__)

class CampaignService:
    """Service for managing campaigns, content generation, and performance tracking."""
    
    def __init__(self):
        self.campaigns_dir = Path("campaigns")
        self.campaigns_dir.mkdir(exist_ok=True)
        
        # Initialize services
        self.gemini_service = GeminiService()
        self.performance_collection = mongodb_client.client["email_agent"]["email_performance"]
        
        logger.info("Campaign service initialized successfully")
    
    def _get_campaign_dir(self, campaign_name: str) -> Path:
        """Get campaign directory path."""
        return self.campaigns_dir / campaign_name
    
    def _get_context_file(self, campaign_name: str) -> Path:
        """Get campaign context file path."""
        return self._get_campaign_dir(campaign_name) / "context.json"
    
    def _get_drafts_dir(self, campaign_name: str) -> Path:
        """Get campaign drafts directory path."""
        drafts_dir = self._get_campaign_dir(campaign_name) / "drafts"
        drafts_dir.mkdir(exist_ok=True)
        return drafts_dir
    
    def create_campaign(self, campaign_name: str, context: CampaignContext) -> bool:
        """Create a new campaign with context."""
        try:
            campaign_dir = self._get_campaign_dir(campaign_name)
            campaign_dir.mkdir(exist_ok=True)
            
            # Save context
            context_file = self._get_context_file(campaign_name)
            with open(context_file, 'w') as f:
                json.dump(context.dict(), f, indent=2, default=str)
            
            # Create drafts directory
            self._get_drafts_dir(campaign_name)
            
            logger.info(f"Campaign '{campaign_name}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating campaign '{campaign_name}': {e}")
            return False
    
    def load_campaign_context(self, campaign_name: str) -> Optional[CampaignContext]:
        """Load campaign context from file."""
        try:
            context_file = self._get_context_file(campaign_name)
            
            if not context_file.exists():
                logger.error(f"Campaign context file not found: {context_file}")
                return None
            
            with open(context_file, 'r') as f:
                context_data = json.load(f)
            
            return CampaignContext(**context_data)
            
        except Exception as e:
            logger.error(f"Error loading campaign context for '{campaign_name}': {e}")
            return None
    
    def save_email_content(self, campaign_name: str, content: EmailContent) -> bool:
        """Save email content to drafts directory."""
        try:
            drafts_dir = self._get_drafts_dir(campaign_name)
            
            # Create filename based on audience segment and email type
            filename = f"{content.audience_segment}_{content.email_type}_{content.version}.json"
            content_file = drafts_dir / filename
            
            # Save content
            with open(content_file, 'w') as f:
                json.dump(content.dict(), f, indent=2, default=str)
            
            logger.info(f"Email content saved: {content_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving email content: {e}")
            return False
    
    def load_email_content(self, campaign_name: str, audience_segment: str, 
                          email_type: str, version: str = "v1") -> Optional[EmailContent]:
        """Load email content from drafts directory."""
        try:
            drafts_dir = self._get_drafts_dir(campaign_name)
            filename = f"{audience_segment}_{email_type}_{version}.json"
            content_file = drafts_dir / filename
            
            if not content_file.exists():
                logger.warning(f"Email content file not found: {content_file}")
                return None
            
            with open(content_file, 'r') as f:
                content_data = json.load(f)
            
            return EmailContent(**content_data)
            
        except Exception as e:
            logger.error(f"Error loading email content: {e}")
            return None
    
    def generate_email(self, campaign_name: str, audience_segment: str, 
                      email_type: str, tone: str = "professional") -> Optional[EmailContent]:
        """Generate email content for a campaign."""
        try:
            # Load campaign context
            context = self.load_campaign_context(campaign_name)
            if not context:
                raise ValueError(f"Campaign context not found for '{campaign_name}'")
            
            # Generate content using Gemini
            content = self.gemini_service.generate_email_content(
                context, audience_segment, email_type, tone
            )
            
            # Save content
            if self.save_email_content(campaign_name, content):
                logger.info(f"Generated email for {campaign_name}: {content.subject}")
                return content
            else:
                raise ValueError("Failed to save generated content")
            
        except Exception as e:
            logger.error(f"Error generating email: {e}")
            return None
    
    def record_email_performance(self, performance: EmailPerformance) -> bool:
        """Record email performance metrics in MongoDB."""
        try:
            # Calculate rates
            if performance.sent_count > 0:
                performance.open_rate = performance.open_count / performance.sent_count
                performance.click_rate = performance.click_count / performance.sent_count
                performance.reply_rate = performance.reply_count / performance.sent_count
            
            # Insert into MongoDB
            result = self.performance_collection.insert_one(performance.dict())
            
            logger.info(f"Performance recorded for {performance.campaign_name}: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording performance: {e}")
            return False
    
    def get_performance_data(self, campaign_name: str, email_type: Optional[str] = None,
                           audience_segment: Optional[str] = None) -> List[EmailPerformance]:
        """Get performance data from MongoDB."""
        try:
            # Build query
            query = {"campaign_name": campaign_name}
            if email_type:
                query["email_type"] = email_type
            if audience_segment:
                query["audience_segment"] = audience_segment
            
            # Get performance data
            cursor = self.performance_collection.find(query).sort("sent_at", -1)
            performance_data = []
            
            for doc in cursor:
                # Remove MongoDB _id field
                doc.pop("_id", None)
                performance_data.append(EmailPerformance(**doc))
            
            logger.info(f"Retrieved {len(performance_data)} performance records for '{campaign_name}'")
            return performance_data
            
        except Exception as e:
            logger.error(f"Error getting performance data: {e}")
            return []
    
    def refine_email_content(self, campaign_name: str, email_type: str,
                           audience_segment: Optional[str] = None) -> Optional[EmailContent]:
        """Refine email content based on performance data."""
        try:
            # Load campaign context
            context = self.load_campaign_context(campaign_name)
            if not context:
                raise ValueError(f"Campaign context not found for '{campaign_name}'")
            
            # Get current content
            current_content = self.load_email_content(campaign_name, audience_segment or "all", email_type)
            if not current_content:
                raise ValueError(f"Current email content not found for {email_type}")
            
            # Get performance data
            performance_data = self.get_performance_data(campaign_name, email_type, audience_segment)
            
            if not performance_data:
                logger.warning("No performance data available for refinement")
                return current_content
            
            # Refine content using Gemini
            refined_content = self.gemini_service.refine_email_content(
                context, current_content, performance_data, audience_segment or "all"
            )
            
            # Save refined content
            if self.save_email_content(campaign_name, refined_content):
                logger.info(f"Refined email content for {campaign_name}: {refined_content.subject}")
                return refined_content
            else:
                raise ValueError("Failed to save refined content")
            
        except Exception as e:
            logger.error(f"Error refining email content: {e}")
            return None
    
    def get_campaign_summary(self, campaign_name: str) -> Dict[str, Any]:
        """Get comprehensive campaign summary."""
        try:
            # Load context
            context = self.load_campaign_context(campaign_name)
            if not context:
                return {"error": f"Campaign '{campaign_name}' not found"}
            
            # Get performance data
            performance_data = self.get_performance_data(campaign_name)
            
            # Analyze performance
            analysis = self.gemini_service.analyze_performance_trends(performance_data)
            
            # Get available content versions
            drafts_dir = self._get_drafts_dir(campaign_name)
            content_files = list(drafts_dir.glob("*.json"))
            
            summary = {
                "campaign_name": campaign_name,
                "context": context.dict(),
                "performance_analysis": analysis,
                "content_versions": len(content_files),
                "total_performance_records": len(performance_data),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting campaign summary: {e}")
            return {"error": str(e)}
    
    def list_campaigns(self) -> List[str]:
        """List all available campaigns."""
        try:
            campaigns = []
            for campaign_dir in self.campaigns_dir.iterdir():
                if campaign_dir.is_dir():
                    context_file = campaign_dir / "context.json"
                    if context_file.exists():
                        campaigns.append(campaign_dir.name)
            
            return campaigns
            
        except Exception as e:
            logger.error(f"Error listing campaigns: {e}")
            return []
    
    def delete_campaign(self, campaign_name: str) -> bool:
        """Delete a campaign and all its data."""
        try:
            campaign_dir = self._get_campaign_dir(campaign_name)
            
            if not campaign_dir.exists():
                logger.warning(f"Campaign directory not found: {campaign_dir}")
                return False
            
            # Remove campaign directory
            import shutil
            shutil.rmtree(campaign_dir)
            
            # Remove performance data from MongoDB
            self.performance_collection.delete_many({"campaign_name": campaign_name})
            
            logger.info(f"Campaign '{campaign_name}' deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting campaign '{campaign_name}': {e}")
            return False
