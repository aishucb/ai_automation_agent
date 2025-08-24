#!/usr/bin/env python3
"""
Command-line interface for Workflow Automation Module.
"""

import argparse
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

# Add the current directory to Python path
sys.path.append('.')

from services.workflow_service import WorkflowService
from models.workflow import WorkflowPlan, CampaignTargets, CampaignStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def schedule_campaign_command(args):
    """Schedule a new campaign workflow."""
    try:
        workflow_service = WorkflowService()
        
        # Create workflow plan
        workflow_plan = WorkflowPlan(
            invite=datetime.fromisoformat(args.invite) if args.invite else None,
            reminder=datetime.fromisoformat(args.reminder) if args.reminder else None,
            thank_you=datetime.fromisoformat(args.thank_you) if args.thank_you else None,
            follow_up=datetime.fromisoformat(args.follow_up) if args.follow_up else None
        )
        
        # Create targets
        targets = CampaignTargets(
            total_registrations=args.registrations,
            total_emails_sent=args.emails,
            open_rate_target=args.open_rate,
            click_rate_target=args.click_rate
        )
        
        # Schedule campaign
        success = workflow_service.schedule_campaign(
            campaign_name=args.name,
            workflow_plan=workflow_plan,
            targets=targets,
            audience_segments=args.segments
        )
        
        if success:
            print(f"✅ Campaign '{args.name}' scheduled successfully!")
            print(f"📅 Workflow Plan:")
            if workflow_plan.invite:
                print(f"   • Invite: {workflow_plan.invite}")
            if workflow_plan.reminder:
                print(f"   • Reminder: {workflow_plan.reminder}")
            if workflow_plan.thank_you:
                print(f"   • Thank You: {workflow_plan.thank_you}")
            if workflow_plan.follow_up:
                print(f"   • Follow Up: {workflow_plan.follow_up}")
            print(f"🎯 Targets: {targets.total_registrations} registrations, {targets.total_emails_sent} emails")
        else:
            print(f"❌ Failed to schedule campaign '{args.name}'")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error scheduling campaign: {e}")
        sys.exit(1)

def list_campaigns_command(args):
    """List all campaigns."""
    try:
        workflow_service = WorkflowService()
        campaigns = workflow_service.get_all_campaigns()
        
        if not campaigns:
            print("📭 No campaigns found.")
            return
        
        print(f"📋 Found {len(campaigns)} campaigns:")
        print("-" * 80)
        
        for campaign in campaigns:
            print(f"🎯 {campaign.name}")
            print(f"   Title: {campaign.title}")
            print(f"   Status: {campaign.status}")
            print(f"   Created: {campaign.created_at}")
            print(f"   Targets: {campaign.targets.total_registrations} registrations")
            print("-" * 80)
            
    except Exception as e:
        print(f"❌ Error listing campaigns: {e}")
        sys.exit(1)

def campaign_status_command(args):
    """Get detailed campaign status."""
    try:
        workflow_service = WorkflowService()
        status = workflow_service.get_campaign_status(args.name)
        
        if not status:
            print(f"❌ Campaign '{args.name}' not found")
            sys.exit(1)
        
        print(f"📊 Campaign Status: {status.campaign_name}")
        print("=" * 50)
        print(f"Status: {status.status}")
        print(f"Progress: {status.progress_percentage:.1f}%")
        print(f"Emails Sent: {status.total_emails_sent}")
        print(f"Emails Pending: {status.total_emails_pending}")
        print(f"Open Rate: {status.open_rate:.1%}")
        print(f"Click Rate: {status.click_rate:.1%}")
        print(f"Registrations: {status.registration_count}")
        
        if status.next_scheduled_action:
            print(f"Next Action: {status.next_scheduled_action}")
        
        print("\n🎯 Targets:")
        print(f"   • Registrations: {status.targets.total_registrations}")
        print(f"   • Emails: {status.targets.total_emails_sent}")
        print(f"   • Open Rate: {status.targets.open_rate_target:.1%}")
        print(f"   • Click Rate: {status.targets.click_rate_target:.1%}")
        
    except Exception as e:
        print(f"❌ Error getting campaign status: {e}")
        sys.exit(1)

def pause_campaign_command(args):
    """Pause a campaign workflow."""
    try:
        workflow_service = WorkflowService()
        success = workflow_service.pause_campaign(args.name)
        
        if success:
            print(f"⏸️  Campaign '{args.name}' paused successfully!")
        else:
            print(f"❌ Failed to pause campaign '{args.name}'")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error pausing campaign: {e}")
        sys.exit(1)

def resume_campaign_command(args):
    """Resume a paused campaign workflow."""
    try:
        workflow_service = WorkflowService()
        success = workflow_service.resume_campaign(args.name)
        
        if success:
            print(f"▶️  Campaign '{args.name}' resumed successfully!")
        else:
            print(f"❌ Failed to resume campaign '{args.name}'")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error resuming campaign: {e}")
        sys.exit(1)

def dashboard_metrics_command(args):
    """Show dashboard metrics."""
    try:
        workflow_service = WorkflowService()
        metrics = workflow_service.get_dashboard_metrics()
        
        print("📊 Dashboard Metrics")
        print("=" * 30)
        print(f"Total Campaigns: {metrics.total_campaigns}")
        print(f"Active Campaigns: {metrics.active_campaigns}")
        print(f"Emails Sent: {metrics.total_emails_sent}")
        print(f"Emails Pending: {metrics.total_emails_pending}")
        print(f"Average Open Rate: {metrics.average_open_rate:.1%}")
        print(f"Average Click Rate: {metrics.average_click_rate:.1%}")
        print(f"Total Registrations: {metrics.total_registrations}")
        
        print("\n📈 Campaigns by Status:")
        for status, count in metrics.campaigns_by_status.items():
            print(f"   • {status}: {count}")
            
    except Exception as e:
        print(f"❌ Error getting dashboard metrics: {e}")
        sys.exit(1)

def update_targets_command(args):
    """Update campaign targets."""
    try:
        workflow_service = WorkflowService()
        
        # Create new targets
        targets = CampaignTargets(
            total_registrations=args.registrations,
            total_emails_sent=args.emails,
            open_rate_target=args.open_rate,
            click_rate_target=args.click_rate
        )
        
        success = workflow_service.update_campaign_targets(args.name, targets)
        
        if success:
            print(f"✅ Targets updated for campaign '{args.name}'")
            print(f"🎯 New targets: {targets.total_registrations} registrations, {targets.total_emails_sent} emails")
        else:
            print(f"❌ Failed to update targets for campaign '{args.name}'")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error updating targets: {e}")
        sys.exit(1)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Email Marketing Agent - Workflow Automation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Schedule a new campaign
  python cli/workflow_cli.py schedule --name "SustainSpark8" --invite "2025-08-20T09:00:00" --reminder "2025-09-15T09:00:00" --registrations 1000 --emails 5000

  # List all campaigns
  python cli/workflow_cli.py list

  # Get campaign status
  python cli/workflow_cli.py status --name "SustainSpark8"

  # Pause a campaign
  python cli/workflow_cli.py pause --name "SustainSpark8"

  # Show dashboard metrics
  python cli/workflow_cli.py metrics
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Schedule a new campaign')
    schedule_parser.add_argument('--name', required=True, help='Campaign name')
    schedule_parser.add_argument('--invite', help='Invite email date (ISO format)')
    schedule_parser.add_argument('--reminder', help='Reminder email date (ISO format)')
    schedule_parser.add_argument('--thank-you', help='Thank you email date (ISO format)')
    schedule_parser.add_argument('--follow-up', help='Follow up email date (ISO format)')
    schedule_parser.add_argument('--registrations', type=int, default=1000, help='Target registrations')
    schedule_parser.add_argument('--emails', type=int, default=5000, help='Target emails to send')
    schedule_parser.add_argument('--open-rate', type=float, default=0.25, help='Target open rate (0.0-1.0)')
    schedule_parser.add_argument('--click-rate', type=float, default=0.05, help='Target click rate (0.0-1.0)')
    schedule_parser.add_argument('--segments', nargs='*', help='Target audience segments')
    schedule_parser.set_defaults(func=schedule_campaign_command)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all campaigns')
    list_parser.set_defaults(func=list_campaigns_command)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get campaign status')
    status_parser.add_argument('--name', required=True, help='Campaign name')
    status_parser.set_defaults(func=campaign_status_command)
    
    # Pause command
    pause_parser = subparsers.add_parser('pause', help='Pause a campaign')
    pause_parser.add_argument('--name', required=True, help='Campaign name')
    pause_parser.set_defaults(func=pause_campaign_command)
    
    # Resume command
    resume_parser = subparsers.add_parser('resume', help='Resume a campaign')
    resume_parser.add_argument('--name', required=True, help='Campaign name')
    resume_parser.set_defaults(func=resume_campaign_command)
    
    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Show dashboard metrics')
    metrics_parser.set_defaults(func=dashboard_metrics_command)
    
    # Update targets command
    update_parser = subparsers.add_parser('update-targets', help='Update campaign targets')
    update_parser.add_argument('--name', required=True, help='Campaign name')
    update_parser.add_argument('--registrations', type=int, required=True, help='New target registrations')
    update_parser.add_argument('--emails', type=int, required=True, help='New target emails')
    update_parser.add_argument('--open-rate', type=float, default=0.25, help='New target open rate')
    update_parser.add_argument('--click-rate', type=float, default=0.05, help='New target click rate')
    update_parser.set_defaults(func=update_targets_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)

if __name__ == "__main__":
    main()
