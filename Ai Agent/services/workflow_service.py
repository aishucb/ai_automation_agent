import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from pymongo import MongoClient
from dotenv import load_dotenv

from models.workflow import (
    Campaign, CampaignStatus, WorkflowPlan, CampaignTargets, 
    EmailLog, EmailStatus, CampaignStatusResponse, DashboardMetrics
)
from models.campaign import CampaignContext
from services.smtp_service import SMTPService
from services.gemini_service import GeminiService
from services.contact_service import ContactService
from database.mongodb_client import MongoDBClient

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class WorkflowService:
    """Service for workflow automation and campaign management."""
    
    def __init__(self):
        self.mongodb_client = None
        self.smtp_service = SMTPService()
        self.gemini_service = GeminiService()
        self.contact_service = ContactService()
        
        # Try to initialize MongoDB client
        try:
            self.mongodb_client = MongoDBClient()
            logger.info("MongoDB client initialized successfully")
        except Exception as e:
            logger.warning(f"MongoDB client initialization failed: {e}")
            self.mongodb_client = None
        
        # Initialize scheduler with fallback job store
        self._initialize_scheduler()
        
        # Start the scheduler
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Workflow scheduler started")
    
    def _initialize_scheduler(self):
        """Initialize the scheduler with appropriate job store."""
        try:
            if self.mongodb_client and self.mongodb_client.client:
                # Try to use MongoDB job store
                from apscheduler.jobstores.mongodb import MongoDBJobStore
                jobstores = {
                    'default': MongoDBJobStore(
                        database=os.getenv('MONGODB_DATABASE', 'email_agent'),
                        collection='scheduler_jobs',
                        client=self.mongodb_client.client
                    )
                }
                logger.info("Using MongoDB job store for scheduler")
            else:
                # Fallback to memory job store
                jobstores = {
                    'default': MemoryJobStore()
                }
                logger.info("Using memory job store for scheduler (MongoDB unavailable)")
        except Exception as e:
            logger.warning(f"MongoDB job store initialization failed: {e}")
            # Fallback to memory job store
            jobstores = {
                'default': MemoryJobStore()
            }
            logger.info("Using memory job store for scheduler (fallback)")
        
        executors = {
            'default': ThreadPoolExecutor(20),
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )
    
    def schedule_campaign(self, campaign_name: str, workflow_plan: WorkflowPlan, 
                         targets: CampaignTargets, audience_segments: List[str] = None) -> bool:
        """Schedule a campaign workflow."""
        try:
            # Create campaign record
            campaign = Campaign(
                name=campaign_name,
                title=campaign_name,
                status=CampaignStatus.SCHEDULED,
                workflow_plan=workflow_plan,
                targets=targets,
                created_by="system"
            )
            
            # Save campaign to MongoDB if available
            if self.mongodb_client:
                try:
                    campaigns_collection = self.mongodb_client.get_collection('campaigns')
                    campaigns_collection.replace_one(
                        {'name': campaign_name},
                        campaign.model_dump(),
                        upsert=True
                    )
                    logger.info(f"Campaign {campaign_name} saved to MongoDB")
                except Exception as e:
                    logger.warning(f"Failed to save campaign to MongoDB: {e}")
            else:
                logger.warning("MongoDB not available - campaign not persisted")
            
            # Schedule jobs for each email type
            scheduled_jobs = []
            
            if workflow_plan.invite:
                job_id = f"{campaign_name}_invite"
                self.scheduler.add_job(
                    func=self._send_campaign_emails,
                    trigger='date',
                    run_date=workflow_plan.invite,
                    args=[campaign_name, 'invite', audience_segments],
                    id=job_id,
                    replace_existing=True
                )
                scheduled_jobs.append(job_id)
            
            if workflow_plan.reminder:
                job_id = f"{campaign_name}_reminder"
                self.scheduler.add_job(
                    func=self._send_campaign_emails,
                    trigger='date',
                    run_date=workflow_plan.reminder,
                    args=[campaign_name, 'reminder', audience_segments],
                    id=job_id,
                    replace_existing=True
                )
                scheduled_jobs.append(job_id)
            
            if workflow_plan.thank_you:
                job_id = f"{campaign_name}_thank_you"
                self.scheduler.add_job(
                    func=self._send_campaign_emails,
                    trigger='date',
                    run_date=workflow_plan.thank_you,
                    args=[campaign_name, 'thank_you', audience_segments],
                    id=job_id,
                    replace_existing=True
                )
                scheduled_jobs.append(job_id)
            
            if workflow_plan.follow_up:
                job_id = f"{campaign_name}_follow_up"
                self.scheduler.add_job(
                    func=self._send_campaign_emails,
                    trigger='date',
                    run_date=workflow_plan.follow_up,
                    args=[campaign_name, 'follow_up', audience_segments],
                    id=job_id,
                    replace_existing=True
                )
                scheduled_jobs.append(job_id)
            
            logger.info(f"Campaign '{campaign_name}' scheduled with {len(scheduled_jobs)} jobs")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling campaign '{campaign_name}': {e}")
            return False
    
    def pause_campaign(self, campaign_name: str) -> bool:
        """Pause a campaign workflow."""
        try:
            # Update campaign status
            campaigns_collection = self.mongodb_client.get_collection('campaigns')
            campaigns_collection.update_one(
                {'name': campaign_name},
                {
                    '$set': {
                        'status': CampaignStatus.PAUSED,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            # Pause all jobs for this campaign
            jobs = self.scheduler.get_jobs()
            for job in jobs:
                if job.id.startswith(f"{campaign_name}_"):
                    job.pause()
            
            logger.info(f"Campaign '{campaign_name}' paused")
            return True
            
        except Exception as e:
            logger.error(f"Error pausing campaign '{campaign_name}': {e}")
            return False
    
    def resume_campaign(self, campaign_name: str) -> bool:
        """Resume a paused campaign workflow."""
        try:
            # Update campaign status
            campaigns_collection = self.mongodb_client.get_collection('campaigns')
            campaigns_collection.update_one(
                {'name': campaign_name},
                {
                    '$set': {
                        'status': CampaignStatus.ACTIVE,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            # Resume all jobs for this campaign
            jobs = self.scheduler.get_jobs()
            for job in jobs:
                if job.id.startswith(f"{campaign_name}_"):
                    job.resume()
            
            logger.info(f"Campaign '{campaign_name}' resumed")
            return True
            
        except Exception as e:
            logger.error(f"Error resuming campaign '{campaign_name}': {e}")
            return False
    
    def get_campaign_status(self, campaign_name: str) -> Optional[CampaignStatusResponse]:
        """Get detailed campaign status and metrics."""
        try:
            # Get campaign info
            campaigns_collection = self.mongodb_client.get_collection('campaigns')
            campaign_data = campaigns_collection.find_one({'name': campaign_name})
            
            if not campaign_data:
                return None
            
            campaign = Campaign(**campaign_data)
            
            # Get email logs for this campaign
            email_logs_collection = self.mongodb_client.get_collection('email_logs')
            email_logs = list(email_logs_collection.find({'campaign_name': campaign_name}))
            
            # Calculate metrics
            total_sent = len([log for log in email_logs if log['status'] == EmailStatus.SENT])
            total_failed = len([log for log in email_logs if log['status'] == EmailStatus.FAILED])
            total_pending = len([log for log in email_logs if log['status'] == EmailStatus.PENDING])
            
            # Calculate engagement rates (simplified - would need real tracking)
            opened_count = len([log for log in email_logs if log.get('opened', False)])
            clicked_count = len([log for log in email_logs if log.get('clicked', False)])
            
            open_rate = opened_count / total_sent if total_sent > 0 else 0.0
            click_rate = clicked_count / total_sent if total_sent > 0 else 0.0
            
            # Calculate progress percentage
            progress_percentage = (total_sent / campaign.targets.total_emails_sent * 100) if campaign.targets.total_emails_sent > 0 else 0.0
            
            # Get next scheduled action
            next_scheduled_action = None
            jobs = self.scheduler.get_jobs()
            for job in jobs:
                if job.id.startswith(f"{campaign_name}_") and job.next_run_time:
                    if not next_scheduled_action or job.next_run_time < next_scheduled_action:
                        next_scheduled_action = job.next_run_time
            
            # Get registration count (simplified - would need real tracking)
            registration_count = 0  # This would come from actual registration tracking
            
            current_metrics = {
                'total_sent': total_sent,
                'total_failed': total_failed,
                'total_pending': total_pending,
                'opened_count': opened_count,
                'clicked_count': clicked_count,
                'open_rate': open_rate,
                'click_rate': click_rate
            }
            
            return CampaignStatusResponse(
                campaign_name=campaign_name,
                status=campaign.status,
                targets=campaign.targets,
                current_metrics=current_metrics,
                progress_percentage=progress_percentage,
                next_scheduled_action=next_scheduled_action,
                total_emails_sent=total_sent,
                total_emails_pending=total_pending,
                open_rate=open_rate,
                click_rate=click_rate,
                registration_count=registration_count
            )
            
        except Exception as e:
            logger.error(f"Error getting campaign status for '{campaign_name}': {e}")
            return None
    
    def _send_campaign_emails(self, campaign_name: str, email_type: str, 
                             audience_segments: List[str] = None):
        """Send emails for a specific campaign and email type."""
        try:
            logger.info(f"Sending {email_type} emails for campaign '{campaign_name}'")
            
            # Get campaign context
            campaigns_collection = self.mongodb_client.get_collection('campaigns')
            campaign_data = campaigns_collection.find_one({'name': campaign_name})
            
            if not campaign_data:
                logger.error(f"Campaign '{campaign_name}' not found")
                return
            
            campaign = Campaign(**campaign_data)
            
            # Get contacts based on audience segments
            contacts = []
            if audience_segments:
                for segment in audience_segments:
                    segment_contacts = self.contact_service.get_contacts_by_tag(segment)
                    contacts.extend(segment_contacts)
            else:
                # Get all contacts if no segments specified
                contacts = self.contact_service.get_all_contacts()
            
            if not contacts:
                logger.warning(f"No contacts found for campaign '{campaign_name}'")
                return
            
            # Generate email content for each audience segment
            email_batches = []
            
            for contact in contacts:
                try:
                    # Create campaign context for content generation
                    context = CampaignContext(
                        title=campaign.title,
                        objective="Maximize participation",
                        date="2025-09-20",  # This would come from campaign data
                        location="Online + Regional Hubs",
                        target_audience=[contact.get('role', 'general')],
                        key_points=["Hands-on workshops", "Expert speakers", "Certification"],
                        call_to_action="Register now",
                        registration_link="https://example.com/register"
                    )
                    
                    # Generate email content
                    email_content = self.gemini_service.generate_email_content(
                        context=context,
                        audience_segment=contact.get('role', 'general'),
                        email_type=email_type,
                        tone="professional"
                    )
                    
                    if email_content:
                        # Personalize content
                        personalized_body = email_content.body
                        if contact.get('name'):
                            personalized_body = personalized_body.replace('{contact_name}', contact['name'])
                        if contact.get('school_name'):
                            personalized_body = personalized_body.replace('{school_name}', contact['school_name'])
                        
                        email_batches.append({
                            'to': contact['email'],
                            'subject': email_content.subject,
                            'body': personalized_body,
                            'campaign_name': campaign_name,
                            'email_type': email_type
                        })
                    
                except Exception as e:
                    logger.error(f"Error generating email for {contact.get('email')}: {e}")
                    continue
            
            # Send emails in batches
            if email_batches:
                email_logs = self.smtp_service.send_bulk_emails(email_batches)
                
                # Save email logs to MongoDB
                email_logs_collection = self.mongodb_client.get_collection('email_logs')
                for log in email_logs:
                    email_logs_collection.insert_one(log.model_dump())
                
                logger.info(f"Sent {len(email_logs)} {email_type} emails for campaign '{campaign_name}'")
            
        except Exception as e:
            logger.error(f"Error sending campaign emails for '{campaign_name}': {e}")
    
    def get_dashboard_metrics(self) -> DashboardMetrics:
        """Get overall dashboard metrics."""
        try:
            campaigns_collection = self.mongodb_client.get_collection('campaigns')
            email_logs_collection = self.mongodb_client.get_collection('email_logs')
            
            # Get campaign counts
            total_campaigns = campaigns_collection.count_documents({})
            active_campaigns = campaigns_collection.count_documents({'status': CampaignStatus.ACTIVE})
            
            # Get email metrics
            total_emails_sent = email_logs_collection.count_documents({'status': EmailStatus.SENT})
            total_emails_pending = email_logs_collection.count_documents({'status': EmailStatus.PENDING})
            
            # Calculate average rates
            sent_logs = list(email_logs_collection.find({'status': EmailStatus.SENT}))
            opened_count = len([log for log in sent_logs if log.get('opened', False)])
            clicked_count = len([log for log in sent_logs if log.get('clicked', False)])
            
            average_open_rate = opened_count / total_emails_sent if total_emails_sent > 0 else 0.0
            average_click_rate = clicked_count / total_emails_sent if total_emails_sent > 0 else 0.0
            
            # Get campaigns by status
            pipeline = [
                {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
            ]
            status_counts = list(campaigns_collection.aggregate(pipeline))
            campaigns_by_status = {item['_id']: item['count'] for item in status_counts}
            
            return DashboardMetrics(
                total_campaigns=total_campaigns,
                active_campaigns=active_campaigns,
                total_emails_sent=total_emails_sent,
                total_emails_pending=total_emails_pending,
                average_open_rate=average_open_rate,
                average_click_rate=average_click_rate,
                total_registrations=0,  # Would need real tracking
                campaigns_by_status=campaigns_by_status
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {e}")
            return DashboardMetrics(
                total_campaigns=0,
                active_campaigns=0,
                total_emails_sent=0,
                total_emails_pending=0,
                average_open_rate=0.0,
                average_click_rate=0.0,
                total_registrations=0,
                campaigns_by_status={}
            )
    
    def update_campaign_targets(self, campaign_name: str, targets: CampaignTargets) -> bool:
        """Update campaign targets."""
        try:
            campaigns_collection = self.mongodb_client.get_collection('campaigns')
            result = campaigns_collection.update_one(
                {'name': campaign_name},
                {
                    '$set': {
                        'targets': targets.model_dump(),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated targets for campaign '{campaign_name}'")
                return True
            else:
                logger.warning(f"Campaign '{campaign_name}' not found for target update")
                return False
                
        except Exception as e:
            logger.error(f"Error updating targets for campaign '{campaign_name}': {e}")
            return False
    
    def get_all_campaigns(self) -> List[Campaign]:
        """Get all campaigns."""
        try:
            campaigns_collection = self.mongodb_client.get_collection('campaigns')
            campaign_data = list(campaigns_collection.find({}))
            return [Campaign(**data) for data in campaign_data]
        except Exception as e:
            logger.error(f"Error getting all campaigns: {e}")
            return []
    
    def shutdown(self):
        """Shutdown the workflow service."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Workflow scheduler shutdown")
