#!/usr/bin/env python3
"""
Test script to verify that the AI Email Marketing Agent can start without MongoDB.
This script tests the startup process and database connection handling.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection handling."""
    print("🔍 Testing database connection handling...")
    
    try:
        # Add project root to path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # Test MongoDB client initialization
        from database.mongodb_client import MongoDBClient
        
        try:
            client = MongoDBClient()
            print("✅ MongoDB connection successful")
            return True
        except Exception as e:
            print(f"⚠️ MongoDB connection failed (expected if no .env file): {e}")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_workflow_service():
    """Test workflow service initialization."""
    print("\n🔍 Testing workflow service initialization...")
    
    try:
        from services.workflow_service import WorkflowService
        
        try:
            service = WorkflowService()
            print("✅ Workflow service initialized successfully")
            return True
        except Exception as e:
            print(f"⚠️ Workflow service initialization failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Workflow service test failed: {e}")
        return False

def test_environment_check():
    """Test environment variable checking."""
    print("\n🔍 Testing environment variable checking...")
    
    try:
        from agent_runner import AIEmailMarketingAgent
        
        agent = AIEmailMarketingAgent()
        result = agent.check_environment()
        
        if result:
            print("✅ Environment check passed")
        else:
            print("⚠️ Environment check failed (missing required variables)")
        
        return result
        
    except Exception as e:
        print(f"❌ Environment check test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 AI Email Marketing Agent - Startup Test")
    print("=" * 50)
    
    # Test database connection
    db_ok = test_database_connection()
    
    # Test workflow service
    workflow_ok = test_workflow_service()
    
    # Test environment check
    env_ok = test_environment_check()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Database Connection: {'✅' if db_ok else '⚠️'}")
    print(f"   Workflow Service: {'✅' if workflow_ok else '⚠️'}")
    print(f"   Environment Check: {'✅' if env_ok else '⚠️'}")
    
    if workflow_ok:
        print("\n✅ Application can start successfully!")
        print("🚀 You can now run: python runner.py agent")
    else:
        print("\n⚠️ Some components failed to initialize")
        print("💡 Try running: python runner.py setup")
    
    return 0 if workflow_ok else 1

if __name__ == "__main__":
    sys.exit(main())
