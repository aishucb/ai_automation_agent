import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

from models.campaign import CampaignContext, EmailContent, EmailPerformance

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for Google Gemini LLM integration for content generation."""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Try different model names - the API has evolved
        try:
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        except Exception as e:
            try:
                self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
            except Exception as e2:
                try:
                    self.model = genai.GenerativeModel('gemini-2.0-flash')
                except Exception as e3:
                    logger.error(f"Failed to initialize Gemini model. Tried gemini-1.5-pro, gemini-1.5-pro-latest, and gemini-2.0-flash")
                    logger.error(f"Errors: {e}, {e2}, {e3}")
                    raise ValueError("Could not initialize any Gemini model. Please check your API key and model availability.")
        
        logger.info("Gemini service initialized successfully")
    
    def list_available_models(self) -> List[str]:
        """List available Gemini models."""
        try:
            models = genai.list_models()
            available_models = []
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
            return available_models
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def _create_email_generation_prompt(self, context: CampaignContext, audience_segment: str, 
                                       email_type: str, tone: str = "professional") -> str:
        """Create a detailed prompt for email generation."""
        
        tone_instructions = {
            "professional": "Use a formal, business-like tone suitable for school administrators and principals.",
            "friendly": "Use a warm, approachable tone that builds rapport with the audience.",
            "inspiring": "Use an enthusiastic, motivational tone that inspires action and participation.",
            "urgent": "Use a compelling, time-sensitive tone that creates urgency for registration."
        }
        
        email_type_instructions = {
            "invite": "Create an initial invitation email that introduces the event and encourages registration.",
            "reminder": "Create a follow-up reminder email for those who haven't registered yet.",
            "thank_you": "Create a thank you email for those who have registered.",
            "follow_up": "Create a follow-up email with additional event details and next steps."
        }
        
        prompt = f"""
You are an expert email marketing copywriter for educational events. Generate compelling email content for the following campaign:

CAMPAIGN CONTEXT:
- Title: {context.title}
- Objective: {context.objective}
- Date: {context.date}
- Location: {context.location}
- Key Points: {', '.join(context.key_points)}
- Call to Action: {context.call_to_action}

AUDIENCE: {audience_segment}
EMAIL TYPE: {email_type_instructions.get(email_type, email_type)}
TONE: {tone_instructions.get(tone, tone)}

REQUIREMENTS:
1. Create a compelling subject line (max 60 characters)
2. Create HTML email body content
3. Include personalization placeholders: {{school_name}}, {{principal_name}}, {{contact_name}}
4. Make the content engaging and action-oriented
5. Include the call to action prominently
6. Keep the email concise but informative

OUTPUT FORMAT:
Return a JSON object with:
{{
    "subject": "Subject line here",
    "body": "<html>Email body content here</html>",
    "placeholders": ["school_name", "principal_name", "contact_name"]
}}

Focus on creating content that will maximize participation and engagement for this educational event.
"""
        return prompt
    
    def _create_refinement_prompt(self, context: CampaignContext, current_content: EmailContent, 
                                 performance_data: List[EmailPerformance], audience_segment: str) -> str:
        """Create a prompt for content refinement based on performance data."""
        
        # Calculate average performance metrics
        avg_open_rate = sum(p.open_rate for p in performance_data) / len(performance_data) if performance_data else 0
        avg_click_rate = sum(p.click_rate for p in performance_data) / len(performance_data) if performance_data else 0
        
        prompt = f"""
You are an expert email marketing optimization specialist. Analyze the current email performance and suggest improvements.

CAMPAIGN CONTEXT:
- Title: {context.title}
- Objective: {context.objective}
- Key Points: {', '.join(context.key_points)}

CURRENT EMAIL CONTENT:
Subject: {current_content.subject}
Body: {current_content.body[:500]}...

PERFORMANCE DATA:
- Average Open Rate: {avg_open_rate:.2%}
- Average Click Rate: {avg_click_rate:.2%}
- Number of Performance Records: {len(performance_data)}

AUDIENCE: {audience_segment}

TASK: Generate an improved version of this email content that should:
1. Increase open rates (more compelling subject line)
2. Increase click rates (better call-to-action placement and wording)
3. Maintain the same professional tone
4. Keep all personalization placeholders
5. Focus on the key campaign benefits

OUTPUT FORMAT:
Return a JSON object with:
{{
    "subject": "Improved subject line",
    "body": "<html>Improved email body</html>",
    "placeholders": ["school_name", "principal_name", "contact_name"],
    "improvement_notes": "Brief explanation of key improvements made"
}}

Focus on data-driven improvements that will increase engagement and conversion rates.
"""
        return prompt
    
    def generate_email_content(self, context: CampaignContext, audience_segment: str, 
                              email_type: str, tone: str = "professional") -> EmailContent:
        """Generate email content using Gemini LLM."""
        try:
            prompt = self._create_email_generation_prompt(context, audience_segment, email_type, tone)
            
            logger.info(f"Generating email content for {audience_segment} - {email_type}")
            
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Parse JSON response
            try:
                content_data = json.loads(response.text)
            except json.JSONDecodeError:
                # Try to extract JSON from the response if it's wrapped in markdown
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    content_data = json.loads(json_match.group())
                else:
                    raise ValueError("Invalid JSON response from Gemini API")
            
            # Create EmailContent object
            email_content = EmailContent(
                subject=content_data.get("subject", ""),
                body=content_data.get("body", ""),
                audience_segment=audience_segment,
                email_type=email_type,
                placeholders=content_data.get("placeholders", [])
            )
            
            logger.info(f"Successfully generated email content: {email_content.subject}")
            return email_content
            
        except Exception as e:
            logger.error(f"Error generating email content: {e}")
            raise
    
    def refine_email_content(self, context: CampaignContext, current_content: EmailContent,
                           performance_data: List[EmailPerformance], audience_segment: str) -> EmailContent:
        """Refine email content based on performance data."""
        try:
            prompt = self._create_refinement_prompt(context, current_content, performance_data, audience_segment)
            
            logger.info(f"Refining email content for {audience_segment} based on performance data")
            
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Parse JSON response
            try:
                content_data = json.loads(response.text)
            except json.JSONDecodeError:
                # Try to extract JSON from the response if it's wrapped in markdown
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    content_data = json.loads(json_match.group())
                else:
                    raise ValueError("Invalid JSON response from Gemini API")
            
            # Create refined EmailContent object
            refined_content = EmailContent(
                subject=content_data.get("subject", current_content.subject),
                body=content_data.get("body", current_content.body),
                audience_segment=audience_segment,
                email_type=current_content.email_type,
                placeholders=content_data.get("placeholders", current_content.placeholders),
                version=f"v{int(current_content.version[1:]) + 1}" if current_content.version.startswith('v') else "v2"
            )
            
            logger.info(f"Successfully refined email content: {refined_content.subject}")
            return refined_content
            
        except Exception as e:
            logger.error(f"Error refining email content: {e}")
            raise
    
    def analyze_performance_trends(self, performance_data: List[EmailPerformance]) -> Dict[str, Any]:
        """Analyze performance trends and provide insights."""
        try:
            if not performance_data:
                return {"insights": "No performance data available for analysis"}
            
            # Calculate trends
            total_sent = sum(p.sent_count for p in performance_data)
            total_opens = sum(p.open_count for p in performance_data)
            total_clicks = sum(p.click_count for p in performance_data)
            
            avg_open_rate = total_opens / total_sent if total_sent > 0 else 0
            avg_click_rate = total_clicks / total_sent if total_sent > 0 else 0
            
            # Group by version to see improvement trends
            version_performance = {}
            for p in performance_data:
                if p.version not in version_performance:
                    version_performance[p.version] = []
                version_performance[p.version].append(p)
            
            analysis = {
                "total_sent": total_sent,
                "total_opens": total_opens,
                "total_clicks": total_clicks,
                "average_open_rate": avg_open_rate,
                "average_click_rate": avg_click_rate,
                "version_performance": version_performance,
                "insights": []
            }
            
            # Generate insights
            if avg_open_rate < 0.2:
                analysis["insights"].append("Open rates are below industry average - consider improving subject lines")
            if avg_click_rate < 0.05:
                analysis["insights"].append("Click rates are low - review call-to-action placement and wording")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return {"error": str(e)}
