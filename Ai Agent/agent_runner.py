#!/usr/bin/env python3
"""
AI Email Marketing Agent - Continuous Runner
Starts and maintains the dashboard with all functionality running continuously.
"""

import os
import sys
import time
import signal
import logging
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIEmailMarketingAgent:
    """Main agent class that manages all services and keeps them running."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dashboard_process = None
        self.workflow_process = None
        self.running = False
        self.services = {}
        
        # Check environment
        self.check_environment()
        
    def check_environment(self):
        """Check if all required environment variables are set."""
        # Required variables (application will fail without these)
        required_vars = [
            'SMTP_SERVER',
            'SMTP_USERNAME',
            'SMTP_PASSWORD'
        ]
        
        # Optional variables (application can run without these)
        optional_vars = [
            'MONGODB_URI',
            'GEMINI_API_KEY'
        ]
        
        missing_required = []
        missing_optional = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_required.append(var)
        
        for var in optional_vars:
            if not os.getenv(var):
                missing_optional.append(var)
        
        if missing_required:
            logger.error(f"Missing required environment variables: {', '.join(missing_required)}")
            logger.error("Please check your .env file")
            return False
        
        if missing_optional:
            logger.warning(f"Missing optional environment variables: {', '.join(missing_optional)}")
            logger.warning("Some features may be limited without these variables")
            logger.info("Required features: SMTP configuration")
            logger.info("Optional features: MongoDB database, AI content generation")
        
        logger.info("Environment variables configured")
        return True
    
    def start_dashboard(self):
        """Start the web dashboard."""
        try:
            logger.info("Starting AI Email Marketing Agent Dashboard...")
            
            # Start dashboard on port 8001
            dashboard_script = self.project_root / "api" / "dashboard.py"
            if not dashboard_script.exists():
                logger.error(f"Dashboard script not found: {dashboard_script}")
                return False
            
            # Set environment variables for dashboard
            env = os.environ.copy()
            env['API_HOST'] = '0.0.0.0'
            env['API_PORT'] = '8001'
            
            # Start dashboard process
            self.dashboard_process = subprocess.Popen(
                [sys.executable, str(dashboard_script)],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for the server to start
            time.sleep(3)
            
            if self.dashboard_process.poll() is None:
                logger.info("Dashboard started successfully!")
                logger.info("Dashboard URL: http://localhost:8001")
                logger.info("API Documentation: http://localhost:8001/docs")
                return True
            else:
                logger.error("Dashboard failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Error starting dashboard: {e}")
            return False
    
    def start_workflow_scheduler(self):
        """Start the workflow scheduler service."""
        try:
            logger.info("Starting workflow scheduler...")
            
            # Import and initialize workflow service
            sys.path.insert(0, str(self.project_root))
            from services.workflow_service import WorkflowService
            
            try:
                workflow_service = WorkflowService()
                logger.info("Workflow scheduler initialized successfully")
            except Exception as e:
                logger.warning(f"Workflow service initialization failed: {e}")
                logger.info("Continuing without workflow scheduler - some features may be limited")
                return True  # Don't fail the entire startup
            
            # Start scheduler in a separate thread
            def run_scheduler():
                try:
                    logger.info("Workflow scheduler running...")
                    while self.running:
                        time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Workflow scheduler error: {e}")
            
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
            
            self.services['workflow_scheduler'] = workflow_service
            logger.info("Workflow scheduler started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting workflow scheduler: {e}")
            logger.info("Continuing without workflow scheduler - some features may be limited")
            return True  # Don't fail the entire startup
    
    def start_services(self):
        """Start all required services."""
        logger.info("Starting AI Email Marketing Agent services...")
        
        # Start dashboard
        if not self.start_dashboard():
            logger.error("Failed to start dashboard")
            return False
        
        # Start workflow scheduler
        if not self.start_workflow_scheduler():
            logger.error("Failed to start workflow scheduler")
            return False
        
        logger.info("All services started successfully!")
        return True
    
    def stop_services(self):
        """Stop all running services."""
        logger.info("Stopping AI Email Marketing Agent services...")
        
        self.running = False
        
        # Stop dashboard
        if self.dashboard_process and self.dashboard_process.poll() is None:
            logger.info("Stopping dashboard...")
            self.dashboard_process.terminate()
            try:
                self.dashboard_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.dashboard_process.kill()
        
        # Stop workflow scheduler
        if 'workflow_scheduler' in self.services:
            logger.info("Stopping workflow scheduler...")
            try:
                self.services['workflow_scheduler'].shutdown()
            except Exception as e:
                logger.error(f"Error stopping workflow scheduler: {e}")
        
        logger.info("All services stopped")
    
    def monitor_services(self):
        """Monitor running services and restart if needed."""
        while self.running:
            try:
                # Check dashboard
                if self.dashboard_process and self.dashboard_process.poll() is not None:
                    logger.warning("Dashboard process stopped, restarting...")
                    if not self.start_dashboard():
                        logger.error("Failed to restart dashboard")
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Error in service monitor: {e}")
                time.sleep(10)
    
    def show_status(self):
        """Show current status of all services."""
        print("\n" + "="*60)
        print("🤖 AI Email Marketing Agent Status")
        print("="*60)
        
        # Dashboard status
        dashboard_status = "🟢 Running" if (self.dashboard_process and self.dashboard_process.poll() is None) else "🔴 Stopped"
        print(f"Dashboard: {dashboard_status}")
        
        # Workflow scheduler status
        scheduler_status = "🟢 Running" if 'workflow_scheduler' in self.services else "🔴 Stopped"
        print(f"Workflow Scheduler: {scheduler_status}")
        
        # Agent status
        agent_status = "🟢 Active" if self.running else "🔴 Inactive"
        print(f"Agent Status: {agent_status}")
        
        print("="*60)
        
        if self.running:
            print("\n🌐 Dashboard URL: http://localhost:8001")
            print("📊 API Documentation: http://localhost:8001/docs")
            print("\n💡 Available Features:")
            print("   • Upload CSV contacts")
            print("   • Create and manage campaigns")
            print("   • Schedule email workflows")
            print("   • View analytics and reports")
            print("   • Monitor campaign performance")
        
        print("\nPress Ctrl+C to stop the agent")
    
    def run(self):
        """Main run method - starts and maintains the agent."""
        try:
            logger.info("Starting AI Email Marketing Agent...")
            
            # Start all services
            if not self.start_services():
                logger.error("Failed to start services")
                return False
            
            self.running = True
            
            # Show status
            self.show_status()
            
            # Start monitoring
            self.monitor_services()
            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            logger.error(f"Agent error: {e}")
        finally:
            self.stop_services()
            logger.info("AI Email Marketing Agent stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run agent
    agent = AIEmailMarketingAgent()
    agent.run()

if __name__ == "__main__":
    main()
