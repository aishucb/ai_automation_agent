#!/usr/bin/env python3
"""
Environment setup script for AI Email Marketing Agent.
This script helps you configure the .env file with your credentials.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with user input."""
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        print("⚠ .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return False
    
    print("\n" + "="*60)
    print("AI Email Marketing Agent - Environment Setup")
    print("="*60)
    print("\nThis script will help you configure your .env file.")
    print("You can skip optional variables by pressing Enter.\n")
    
    # Required variables
    print("📧 SMTP Configuration (Required):")
    smtp_server = input("SMTP Server (e.g., gator3064.hostgator.com): ").strip()
    smtp_port = input("SMTP Port (e.g., 465): ").strip() or "465"
    smtp_username = input("SMTP Username (e.g., ash@a4gcollab.org): ").strip()
    smtp_password = input("SMTP Password: ").strip()
    smtp_sender = input("Sender Email (e.g., ash@a4gcollab.org): ").strip()
    
    # Optional variables
    print("\n🗄️ MongoDB Configuration (Optional):")
    print("Note: If you don't have MongoDB Atlas, you can skip this section.")
    mongodb_uri = input("MongoDB URI (mongodb+srv://...): ").strip()
    mongodb_database = input("MongoDB Database name (default: email_agent): ").strip() or "email_agent"
    mongodb_collection = input("MongoDB Collection name (default: contacts): ").strip() or "contacts"
    
    print("\n🤖 AI Configuration (Optional):")
    print("Note: If you don't have Google Gemini API, you can skip this section.")
    gemini_api_key = input("Google Gemini API Key: ").strip()
    
    # Application configuration
    print("\n⚙️ Application Configuration:")
    log_level = input("Log Level (default: INFO): ").strip() or "INFO"
    api_host = input("API Host (default: 0.0.0.0): ").strip() or "0.0.0.0"
    api_port = input("API Port (default: 8001): ").strip() or "8001"
    
    # Create .env content
    env_content = f"""# MongoDB Atlas Configuration
MONGODB_URI={mongodb_uri}
MONGODB_DATABASE={mongodb_database}
MONGODB_COLLECTION={mongodb_collection}

# Google Gemini API Configuration
GEMINI_API_KEY={gemini_api_key}

# Application Configuration
LOG_LEVEL={log_level}
API_HOST={api_host}
API_PORT={api_port}

# SMTP Configuration
SMTP_SERVER={smtp_server}
SMTP_PORT={smtp_port}
SMTP_USERNAME={smtp_username}
SMTP_PASSWORD={smtp_password}
SMTP_SENDER={smtp_sender}

# Gmail Configuration (Service Account) - Alternative
GMAIL_SENDER={smtp_sender}
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ .env file created successfully at: {env_file}")
        print("\n📋 Configuration Summary:")
        print(f"   SMTP Server: {smtp_server}")
        print(f"   SMTP Username: {smtp_username}")
        print(f"   API Port: {api_port}")
        
        if mongodb_uri:
            print(f"   MongoDB: Configured")
        else:
            print(f"   MongoDB: Not configured (some features will be limited)")
        
        if gemini_api_key:
            print(f"   Gemini API: Configured")
        else:
            print(f"   Gemini API: Not configured (AI features will be limited)")
        
        print(f"\n🚀 You can now run the agent with: python runner.py agent")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def main():
    """Main function."""
    try:
        if create_env_file():
            print("\n✅ Environment setup completed successfully!")
        else:
            print("\n❌ Environment setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
