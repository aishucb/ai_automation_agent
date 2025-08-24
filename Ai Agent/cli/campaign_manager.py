#!/usr/bin/env python3
"""
Campaign Manager CLI - Create and manage email marketing campaigns.
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

def create_campaign_directory(campaign_name: str) -> Path:
    """Create campaign directory structure."""
    campaign_dir = Path("campaigns") / campaign_name
    campaign_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (campaign_dir / "drafts").mkdir(exist_ok=True)
    (campaign_dir / "assets").mkdir(exist_ok=True)
    
    return campaign_dir

def create_campaign_context(campaign_name: str, details: Dict[str, Any]) -> Path:
    """Create campaign context file."""
    campaign_dir = create_campaign_directory(campaign_name)
    context_file = campaign_dir / "context.json"
    
    # Add creation timestamp
    details["created_at"] = datetime.utcnow().isoformat()
    details["campaign_name"] = campaign_name
    
    with open(context_file, 'w') as f:
        json.dump(details, f, indent=2)
    
    return context_file

def interactive_campaign_creation():
    """Interactive campaign creation wizard."""
    print("🎯 Campaign Creation Wizard")
    print("=" * 40)
    
    # Get basic campaign info
    campaign_name = input("Campaign name (e.g., SustainSpark8): ").strip()
    if not campaign_name:
        print("❌ Campaign name is required!")
        return
    
    title = input("Campaign title: ").strip()
    objective = input("Campaign objective: ").strip()
    date = input("Event date (YYYY-MM-DD): ").strip()
    time = input("Event time (e.g., 10:00 AM - 4:00 PM): ").strip()
    location = input("Event location: ").strip()
    
    # Get target audience
    print("\nTarget audience (comma-separated):")
    audience_input = input("e.g., school principals, youth leaders, teachers: ").strip()
    target_audience = [a.strip() for a in audience_input.split(",") if a.strip()]
    
    # Get key points
    print("\nKey points (one per line, press Enter twice when done):")
    key_points = []
    while True:
        point = input("Key point: ").strip()
        if not point:
            break
        key_points.append(point)
    
    # Get call to action
    call_to_action = input("\nCall to action: ").strip()
    registration_link = input("Registration link: ").strip()
    contact_email = input("Contact email: ").strip()
    website = input("Website (optional): ").strip()
    
    # Build campaign details
    campaign_details = {
        "title": title,
        "objective": objective,
        "date": date,
        "time": time,
        "location": location,
        "target_audience": target_audience,
        "key_points": key_points,
        "call_to_action": call_to_action,
        "registration_link": registration_link,
        "contact_email": contact_email
    }
    
    if website:
        campaign_details["website"] = website
    
    # Create the campaign
    try:
        context_file = create_campaign_context(campaign_name, campaign_details)
        print(f"\n✅ Campaign '{campaign_name}' created successfully!")
        print(f"📁 Location: {context_file}")
        print(f"\n📝 Next steps:")
        print(f"   1. Edit {context_file} to add more details")
        print(f"   2. Run: python runner.py workflow-demo")
        print(f"   3. Start dashboard: python runner.py dashboard")
        
    except Exception as e:
        print(f"❌ Error creating campaign: {e}")

def list_campaigns():
    """List all available campaigns."""
    campaigns_dir = Path("campaigns")
    if not campaigns_dir.exists():
        print("❌ No campaigns directory found!")
        return
    
    campaigns = []
    for campaign_dir in campaigns_dir.iterdir():
        if campaign_dir.is_dir() and campaign_dir.name != "__pycache__":
            context_file = campaign_dir / "context.json"
            if context_file.exists():
                try:
                    with open(context_file, 'r') as f:
                        context = json.load(f)
                    campaigns.append({
                        'name': campaign_dir.name,
                        'title': context.get('title', 'No title'),
                        'date': context.get('date', 'No date'),
                        'created_at': context.get('created_at', 'Unknown')
                    })
                except Exception as e:
                    print(f"⚠️  Error reading {context_file}: {e}")
    
    if not campaigns:
        print("📭 No campaigns found!")
        print("💡 Create your first campaign with: python cli/campaign_manager.py create")
        return
    
    print("📋 Available Campaigns:")
    print("=" * 50)
    for campaign in campaigns:
        print(f"🎯 {campaign['name']}")
        print(f"   Title: {campaign['title']}")
        print(f"   Date: {campaign['date']}")
        print(f"   Created: {campaign['created_at']}")
        print()

def show_campaign(campaign_name: str):
    """Show details of a specific campaign."""
    context_file = Path("campaigns") / campaign_name / "context.json"
    
    if not context_file.exists():
        print(f"❌ Campaign '{campaign_name}' not found!")
        return
    
    try:
        with open(context_file, 'r') as f:
            context = json.load(f)
        
        print(f"🎯 Campaign: {campaign_name}")
        print("=" * 50)
        print(f"Title: {context.get('title', 'No title')}")
        print(f"Objective: {context.get('objective', 'No objective')}")
        print(f"Date: {context.get('date', 'No date')}")
        print(f"Time: {context.get('time', 'No time')}")
        print(f"Location: {context.get('location', 'No location')}")
        print(f"Contact: {context.get('contact_email', 'No contact')}")
        print(f"Website: {context.get('website', 'No website')}")
        
        print(f"\nTarget Audience:")
        for audience in context.get('target_audience', []):
            print(f"  • {audience}")
        
        print(f"\nKey Points:")
        for point in context.get('key_points', []):
            print(f"  • {point}")
        
        print(f"\nCall to Action: {context.get('call_to_action', 'No CTA')}")
        print(f"Registration Link: {context.get('registration_link', 'No link')}")
        
    except Exception as e:
        print(f"❌ Error reading campaign: {e}")

def main():
    parser = argparse.ArgumentParser(description="Campaign Manager CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create campaign command
    create_parser = subparsers.add_parser('create', help='Create a new campaign')
    
    # List campaigns command
    list_parser = subparsers.add_parser('list', help='List all campaigns')
    
    # Show campaign command
    show_parser = subparsers.add_parser('show', help='Show campaign details')
    show_parser.add_argument('campaign_name', help='Name of the campaign to show')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        interactive_campaign_creation()
    elif args.command == 'list':
        list_campaigns()
    elif args.command == 'show':
        show_campaign(args.campaign_name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
