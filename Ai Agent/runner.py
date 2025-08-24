#!/usr/bin/env python3
"""
Runner script for the AI Email Marketing Agent - Audience Segmentation Module.
This script provides a unified interface to run different components of the system.
"""

import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AudienceSegmentationRunner:
    """Runner class for the audience segmentation module."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / ".env"
        self.env_example = self.project_root / "env_example.txt"
    
    def check_dependencies(self):
        """Check if all required dependencies are installed."""
        try:
            import pymongo
            import pandas
            import pydantic
            import fastapi
            import uvicorn
            import email_validator
            import dotenv
            import apscheduler
            import google.auth
            import googleapiclient
            logger.info("✓ All dependencies are installed")
            return True
        except ImportError as e:
            logger.error(f"✗ Missing dependency: {e}")
            logger.info("Please run: pip install -r requirements.txt")
            return False
    
    def check_environment(self):
        """Check if environment variables are configured."""
        if not self.env_file.exists():
            logger.warning("⚠ .env file not found")
            if self.env_example.exists():
                logger.info("Please copy env_example.txt to .env and configure your MongoDB Atlas connection")
            return False
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv(self.env_file)
        
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            logger.error("✗ MONGODB_URI not configured in .env file")
            return False
        
        logger.info("✓ Environment variables configured")
        return True
    
    def run_cli(self, args):
        """Run the CLI interface."""
        logger.info("CLI interface removed - use campaign or workflow-cli commands instead")
        return False
    
    def run_api(self, host=None, port=None):
        """Run the FastAPI server."""
        logger.info("Starting FastAPI server...")
        
        api_script = self.project_root / "api" / "main.py"
        if not api_script.exists():
            logger.error(f"API script not found: {api_script}")
            return False
        
        # Set environment variables for API
        env = os.environ.copy()
        if host:
            env['API_HOST'] = host
        if port:
            env['API_PORT'] = str(port)
        
        try:
            logger.info(f"Starting API server on {env.get('API_HOST', '0.0.0.0')}:{env.get('API_PORT', '8000')}")
            logger.info("API documentation will be available at: http://localhost:8000/docs")
            
            result = subprocess.run([sys.executable, str(api_script)], env=env)
            return result.returncode == 0
        except KeyboardInterrupt:
            logger.info("API server stopped")
            return True
        except Exception as e:
            logger.error(f"API server failed: {e}")
            return False
    
    def run_demo(self):
        """Run the demonstration script."""
        logger.info("Demo script removed - use workflow-demo instead")
        return False
    
    def run_phidata(self):
        """Run the Phidata agent."""
        logger.info("Starting Phidata agent...")
        
        workspace_script = self.project_root / "workspace.py"
        if not workspace_script.exists():
            logger.error(f"Workspace script not found: {workspace_script}")
            return False
        
        try:
            # Import and run the workspace
            sys.path.insert(0, str(self.project_root))
            from workspace import workspace
            
            logger.info("Phidata agent started. Use Ctrl+C to stop.")
            workspace.run()
            return True
        except ImportError as e:
            logger.error(f"Failed to import workspace: {e}")
            return False
        except KeyboardInterrupt:
            logger.info("Phidata agent stopped")
            return True
        except Exception as e:
            logger.error(f"Phidata agent failed: {e}")
            return False
    
    def run_workflow_demo(self):
        """Run the workflow automation demo."""
        logger.info("Workflow demo script removed - use dashboard or workflow-cli instead")
        return False
    
    def run_dashboard(self, host=None, port=None):
        """Run the dashboard server."""
        logger.info("Starting dashboard server...")
        
        dashboard_script = self.project_root / "api" / "dashboard.py"
        if not dashboard_script.exists():
            logger.error(f"Dashboard script not found: {dashboard_script}")
            return False
        
        # Set environment variables for dashboard
        env = os.environ.copy()
        if host:
            env['API_HOST'] = host
        if port:
            env['API_PORT'] = str(port)
        
        # Build dashboard command
        cmd = [sys.executable, str(dashboard_script)]
        
        try:
            logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, env=env, check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            logger.error(f"Dashboard execution failed: {e}")
            return False
        except KeyboardInterrupt:
            logger.info("Dashboard execution interrupted")
            return True
    
    def run_workflow_cli(self, args):
        """Run the workflow CLI interface."""
        logger.info("Starting workflow CLI interface...")
        
        cli_script = self.project_root / "cli" / "workflow_cli.py"
        if not cli_script.exists():
            logger.error(f"Workflow CLI script not found: {cli_script}")
            return False
        
        # Build CLI command
        cmd = [sys.executable, str(cli_script)] + args
        
        try:
            logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            logger.error(f"Workflow CLI execution failed: {e}")
            return False
        except KeyboardInterrupt:
            logger.info("Workflow CLI execution interrupted")
            return True
    
    def run_gmail_test(self):
        """Run Gmail service account test."""
        logger.info("Gmail test removed - using SMTP instead")
        return False
    
    def run_campaign_management(self, args):
        """Run campaign management commands."""
        logger.info("Starting campaign management...")
        
        campaign_script = self.project_root / "cli" / "campaign_manager.py"
        if not campaign_script.exists():
            logger.error(f"Campaign manager script not found: {campaign_script}")
            return False
        
        # Build command
        cmd = [sys.executable, str(campaign_script)] + args
        
        try:
            logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            logger.error(f"Campaign management execution failed: {e}")
            return False
        except KeyboardInterrupt:
            logger.info("Campaign management execution interrupted")
            return True
    
    def run_agent(self):
        """Run the continuous AI agent with dashboard."""
        logger.info("Starting AI Email Marketing Agent...")
        
        agent_script = self.project_root / "agent_runner.py"
        if not agent_script.exists():
            logger.error(f"Agent runner script not found: {agent_script}")
            return False
        
        try:
            logger.info("Starting continuous AI agent with dashboard...")
            logger.info("This will start the web dashboard and keep it running continuously")
            logger.info("Dashboard will be available at: http://localhost:8001")
            logger.info("Press Ctrl+C to stop the agent")
            
            result = subprocess.run([sys.executable, str(agent_script)], check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            logger.error(f"Agent execution failed: {e}")
            return False
        except KeyboardInterrupt:
            logger.info("Agent execution interrupted")
            return True
    
    def setup_environment(self):
        """Set up the environment by copying example file."""
        if self.env_file.exists():
            logger.info("✓ .env file already exists")
            return True
        
        if not self.env_example.exists():
            logger.error("env_example.txt not found")
            return False
        
        try:
            import shutil
            shutil.copy(self.env_example, self.env_file)
            logger.info("✓ Created .env file from env_example.txt")
            logger.info("⚠ Please edit .env file with your MongoDB Atlas credentials")
            return True
        except Exception as e:
            logger.error(f"Failed to create .env file: {e}")
            return False
    
    def install_dependencies(self):
        """Install required dependencies."""
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            logger.error("requirements.txt not found")
            return False
        
        try:
            logger.info("Installing dependencies...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            logger.info("✓ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def show_status(self):
        """Show the current status of the system."""
        print("\n" + "="*60)
        print("AI Email Marketing Agent - Audience Segmentation")
        print("="*60)
        
        # Check dependencies
        deps_ok = self.check_dependencies()
        print(f"Dependencies: {'✓' if deps_ok else '✗'}")
        
        # Check environment
        env_ok = self.check_environment()
        print(f"Environment: {'✓' if env_ok else '✗'}")
        
        # Check files
        files_to_check = [
            ("API", "api/main.py"),
            ("Campaign Manager", "cli/campaign_manager.py"),
            ("Workflow CLI", "cli/workflow_cli.py"),
            ("Dashboard", "api/dashboard.py"),
            ("Phidata", "workspace.py"),
            ("Sample Data", "sample_data/school_contacts.csv")
        ]
        
        for name, file_path in files_to_check:
            exists = (self.project_root / file_path).exists()
            print(f"{name}: {'✓' if exists else '✗'}")
        
        print("="*60)
        
        if not deps_ok:
            print("\nTo install dependencies: python runner.py install")
        if not env_ok:
            print("\nTo setup environment: python runner.py setup")
        
        return deps_ok and env_ok

def main():
    """Main entry point for the runner."""
    parser = argparse.ArgumentParser(
        description="AI Email Marketing Agent - Audience Segmentation Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python runner.py status                    # Check system status
  python runner.py setup                     # Setup environment
  python runner.py install                   # Install dependencies
  python runner.py api                       # Start API server
     python runner.py dashboard                 # Start dashboard server
   python runner.py agent                     # Start continuous AI agent with dashboard
   python runner.py campaign list             # List campaigns
   python runner.py campaign create           # Create new campaign
   python runner.py campaign show SustainSpark8  # Show campaign details
   python runner.py workflow-cli list         # Run workflow CLI commands
   python runner.py workflow-cli schedule --name "TestCampaign" --invite "2025-08-20T09:00:00"
   python runner.py phidata                   # Start Phidata agent
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup environment')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install dependencies')
    

    
    # API command
    api_parser = subparsers.add_parser('api', help='Start API server')
    api_parser.add_argument('--host', help='API host (default: 0.0.0.0)')
    api_parser.add_argument('--port', type=int, help='API port (default: 8000)')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Start dashboard server')
    dashboard_parser.add_argument('--host', help='Dashboard host (default: 0.0.0.0)')
    dashboard_parser.add_argument('--port', type=int, help='Dashboard port (default: 8001)')
    

    
    # Workflow CLI command
    workflow_cli_parser = subparsers.add_parser('workflow-cli', help='Run workflow CLI commands')
    workflow_cli_parser.add_argument('args', nargs=argparse.REMAINDER, help='Workflow CLI arguments')
    
    # Gmail test command
    gmail_test_parser = subparsers.add_parser('test-gmail', help='Test Gmail service account setup')

    # Campaign management commands
    campaign_parser = subparsers.add_parser('campaign', help='Manage campaigns')
    campaign_parser.add_argument('args', nargs=argparse.REMAINDER, help='Campaign management arguments')

    # Agent command
    agent_parser = subparsers.add_parser('agent', help='Start continuous AI agent with dashboard')

    # Phidata command
    phidata_parser = subparsers.add_parser('phidata', help='Start Phidata agent')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1
    
    runner = AudienceSegmentationRunner()
    
    try:
        if args.command == 'status':
            runner.show_status()
            return 0
        
        elif args.command == 'setup':
            print("Running environment setup...")
            setup_script = runner.project_root / "setup_env.py"
            if setup_script.exists():
                try:
                    import subprocess
                    result = subprocess.run([sys.executable, str(setup_script)], check=True)
                    return result.returncode
                except subprocess.CalledProcessError as e:
                    print(f"Setup failed: {e}")
                    return 1
            else:
                if runner.setup_environment():
                    print("✓ Environment setup completed")
                    print("⚠ Please edit .env file with your MongoDB Atlas credentials")
                    return 0
                else:
                    print("✗ Environment setup failed")
                    return 1
        
        elif args.command == 'install':
            if runner.install_dependencies():
                return 0
            else:
                return 1
        

        
        elif args.command == 'api':
            if not runner.check_dependencies():
                print("Please install dependencies first: python runner.py install")
                return 1
            
            if not runner.check_environment():
                print("Please setup environment first: python runner.py setup")
                return 1
            
            if runner.run_api(args.host, args.port):
                return 0
            else:
                return 1
        
        elif args.command == 'dashboard':
            if not runner.check_dependencies():
                print("Please install dependencies first: python runner.py install")
                return 1
            
            if not runner.check_environment():
                print("Please setup environment first: python runner.py setup")
                return 1
            
            if runner.run_dashboard(args.host, args.port):
                return 0
            else:
                return 1
        

        
        elif args.command == 'workflow-cli':
            if not runner.check_dependencies():
                print("Please install dependencies first: python runner.py install")
                return 1
            
            if not runner.check_environment():
                print("Please setup environment first: python runner.py setup")
                return 1
            
            if runner.run_workflow_cli(args.args):
                return 0
            else:
                return 1
        
        elif args.command == 'test-gmail':
            if not runner.check_dependencies():
                print("Please install dependencies first: python runner.py install")
                return 1
            
            if runner.run_gmail_test():
                return 0
            else:
                return 1
        
        elif args.command == 'campaign':
            if not runner.check_dependencies():
                print("Please install dependencies first: python runner.py install")
                return 1
            
            if runner.run_campaign_management(args.args):
                return 0
            else:
                return 1
        
        elif args.command == 'agent':
            if not runner.check_dependencies():
                print("Please install dependencies first: python runner.py install")
                return 1
            
            if not runner.check_environment():
                print("Please setup environment first: python runner.py setup")
                return 1
            
            if runner.run_agent():
                return 0
            else:
                return 1
        
        elif args.command == 'phidata':
            if not runner.check_dependencies():
                print("Please install dependencies first: python runner.py install")
                return 1
            
            if not runner.check_environment():
                print("Please setup environment first: python runner.py setup")
                return 1
            
            if runner.run_phidata():
                return 0
            else:
                return 1
        
        else:
            print(f"Unknown command: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Runner error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
