#!/usr/bin/env python3
"""
AI Email Marketing Agent - Quick Start
Simple script to start the AI agent with a user-friendly interface.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print the agent banner."""
    print("=" * 70)
    print("🤖 AI Email Marketing Agent")
    print("=" * 70)
    print("Complete email marketing automation with AI-powered content generation")
    print("=" * 70)

def check_environment():
    """Check if environment is properly configured."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please run: python runner.py setup")
        return False
    
    # Check for required variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['MONGODB_URI', 'GEMINI_API_KEY', 'SMTP_SERVER']
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("Please check your .env file")
        return False
    
    print("✅ Environment configured")
    return True

def main():
    """Main function."""
    print_banner()
    
    # Check environment
    if not check_environment():
        print("\n💡 To setup your environment:")
        print("   1. Run: python runner.py setup")
        print("   2. Edit .env file with your credentials")
        print("   3. Run this script again")
        return
    
    print("\n🚀 Starting AI Email Marketing Agent...")
    print("\nThis will start:")
    print("   🌐 Web Dashboard at http://localhost:8001")
    print("   📊 Real-time analytics and monitoring")
    print("   📧 Campaign management interface")
    print("   👥 Contact management system")
    print("   ⚙️ Automated workflow scheduler")
    
    print("\nPress Ctrl+C to stop the agent")
    print("=" * 70)
    
    try:
        # Start the agent
        subprocess.run([sys.executable, "agent_runner.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Agent stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting agent: {e}")
    except FileNotFoundError:
        print("\n❌ agent_runner.py not found!")
        print("Please make sure you're in the correct directory")

if __name__ == "__main__":
    main()
