import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP_SSL, SMTPException
from dotenv import load_dotenv

from models.workflow import EmailLog, EmailStatus

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SMTPService:
    """Service for sending emails via SMTP using HostGator credentials."""
    
    def __init__(self):
        self.smtp_server = 'gator3064.hostgator.com'
        self.smtp_port = 465
        self.username = 'ash@a4gcollab.org'
        self.password = 'T%)+PFIy$vM4'
        self.sender_email = 'ash@a4gcollab.org'
        
        # Override with environment variables if set
        self.smtp_server = os.getenv('SMTP_SERVER', self.smtp_server)
        self.smtp_port = int(os.getenv('SMTP_PORT', self.smtp_port))
        self.username = os.getenv('SMTP_USERNAME', self.username)
        self.password = os.getenv('SMTP_PASSWORD', self.password)
        self.sender_email = os.getenv('SMTP_SENDER', self.sender_email)
        
        self.connection = None
        self._test_connection()
    
    def _test_connection(self):
        """Test SMTP connection."""
        try:
            self.connection = SMTP_SSL(self.smtp_server, self.smtp_port)
            self.connection.login(self.username, self.password)
            logger.info(f"SMTP connection established to {self.smtp_server}:{self.smtp_port}")
            self.connection.quit()
        except Exception as e:
            logger.error(f"SMTP connection failed: {e}")
            raise
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   from_email: Optional[str] = None) -> Optional[str]:
        """Send an email via SMTP."""
        try:
            # Use default sender if not specified
            if not from_email:
                from_email = self.sender_email
            
            # Create message
            message = MIMEMultipart('alternative')
            message['to'] = to_email
            message['from'] = from_email
            message['subject'] = subject
            
            # Add HTML body
            html_part = MIMEText(body, 'html')
            message.attach(html_part)
            
            # Send email
            with SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.username, self.password)
                server.send_message(message)
            
            # Generate a simple message ID for tracking
            message_id = f"smpt_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(to_email)}"
            
            logger.info(f"Email sent successfully to {to_email}, message ID: {message_id}")
            return message_id
            
        except SMTPException as error:
            logger.error(f"SMTP error sending email to {to_email}: {error}")
            return None
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return None
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Get the status of a sent message (basic implementation)."""
        try:
            # For SMTP, we can only track if the email was sent
            # We can't check if it was delivered or opened
            status_info = {
                'message_id': message_id,
                'status': 'SENT',
                'timestamp': datetime.utcnow().isoformat(),
                'note': 'SMTP delivery - cannot track delivery status'
            }
            
            return status_info
            
        except Exception as e:
            logger.error(f"Error getting message status for {message_id}: {e}")
            return {}
    
    def check_email_engagement(self, message_id: str) -> Dict[str, Any]:
        """Check if email was opened/clicked (not available with SMTP)."""
        try:
            # SMTP doesn't provide engagement tracking
            engagement_data = {
                'message_id': message_id,
                'is_read': False,  # Cannot determine with SMTP
                'is_clicked': False,  # Cannot determine with SMTP
                'timestamp': datetime.utcnow().isoformat(),
                'note': 'Engagement tracking not available with SMTP'
            }
            
            return engagement_data
            
        except Exception as e:
            logger.error(f"Error checking email engagement for {message_id}: {e}")
            return {}
    
    def send_bulk_emails(self, email_list: List[Dict[str, str]]) -> List[EmailLog]:
        """Send multiple emails and return log entries."""
        logs = []
        
        for email_data in email_list:
            try:
                message_id = self.send_email(
                    to_email=email_data['to'],
                    subject=email_data['subject'],
                    body=email_data['body'],
                    from_email=email_data.get('from')
                )
                
                # Create log entry
                log_entry = EmailLog(
                    campaign_name=email_data.get('campaign_name', ''),
                    email=email_data['to'],
                    email_type=email_data.get('email_type', ''),
                    status=EmailStatus.SENT if message_id else EmailStatus.FAILED,
                    message_id=message_id,
                    error_message=None if message_id else "Failed to send email"
                )
                
                logs.append(log_entry)
                
            except Exception as e:
                logger.error(f"Error in bulk email send: {e}")
                log_entry = EmailLog(
                    campaign_name=email_data.get('campaign_name', ''),
                    email=email_data['to'],
                    email_type=email_data.get('email_type', ''),
                    status=EmailStatus.FAILED,
                    error_message=str(e)
                )
                logs.append(log_entry)
        
        return logs
    
    def validate_credentials(self) -> bool:
        """Validate that SMTP credentials are working."""
        try:
            with SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.username, self.password)
                logger.info(f"SMTP credentials validated for: {self.username}")
                return True
                
        except Exception as e:
            logger.error(f"SMTP credentials validation failed: {e}")
            return False
