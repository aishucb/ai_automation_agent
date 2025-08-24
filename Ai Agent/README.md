# AI Email Marketing Agent

A comprehensive AI-powered email marketing system built with Python, Phidata framework, MongoDB Atlas, and SMTP for automated email campaigns.

## Features

- **Audience Management**: CSV contact ingestion with email validation and duplicate prevention
- **AI Content Generation**: Google Gemini-powered email content creation and refinement
- **Campaign Automation**: Scheduled email workflows with SMTP delivery
- **Engagement Tracking**: Track email opens, clicks, and replies with dynamic segmentation
- **Web Dashboard**: Real-time campaign monitoring and analytics
- **Campaign Management**: Interactive CLI for creating and managing campaigns
- **SMTP Integration**: Reliable email delivery via HostGator SMTP

## Architecture

```
├── database/
│   └── mongodb_client.py      # MongoDB connection and configuration
├── models/
│   ├── contact.py            # Contact data models
│   ├── campaign.py           # Campaign data models
│   └── workflow.py           # Workflow data models
├── services/
│   ├── contact_service.py    # Contact management logic
│   ├── campaign_service.py   # Campaign management logic
│   ├── gemini_service.py     # AI content generation
│   ├── smtp_service.py       # Email delivery via SMTP
│   └── workflow_service.py   # Workflow automation
├── api/
│   ├── main.py              # REST API endpoints
│   └── dashboard.py         # Web dashboard
├── cli/
│   ├── campaign_manager.py  # Campaign management CLI
│   └── workflow_cli.py      # Workflow CLI
├── campaigns/
│   ├── campaign_template.json  # Campaign template
│   └── SustainSpark8/         # Example campaign
├── sample_data/
│   └── school_contacts.csv    # Sample contact data
├── workspace.py             # Phidata workspace configuration
├── runner.py                # Unified runner script
├── requirements.txt         # Python dependencies
└── env_example.txt         # Environment variables template
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `env_example.txt` to `.env` and configure your settings:

```bash
cp env_example.txt .env
```

Required environment variables:
- `MONGODB_URI`: Your MongoDB Atlas connection string
- `GEMINI_API_KEY`: Your Google Gemini API key
- `SMTP_*`: SMTP configuration (pre-configured for HostGator)

### 3. Check System Status

```bash
python runner.py status
```

### 4. Start the AI Agent (Recommended)

**Option A: Simple Start**
```bash
python start_agent.py
```

**Option B: Using Runner**
```bash
python runner.py agent
```

This starts the **complete AI Email Marketing Agent** with:
- 🌐 **Web Dashboard** at http://localhost:8001
- 📊 **Real-time Analytics**
- 📧 **Email Campaign Management**
- 👥 **Contact Management**
- ⚙️ **Workflow Automation**
- 🤖 **Continuous Operation**

### 5. Alternative: Individual Components

```bash
# Start just the dashboard
python runner.py dashboard

# Start demo dashboard (no MongoDB required)
python demo_dashboard.py

# Create campaigns via CLI
python runner.py campaign create

# Manage workflows via CLI
python runner.py workflow-cli list
```

## Available Commands

### 🚀 Start AI Agent (Recommended)

```bash
# Start complete AI agent with dashboard
python runner.py agent
```

### Campaign Management

```bash
# List all campaigns
python runner.py campaign list

# Create new campaign (interactive)
python runner.py campaign create

# Show campaign details
python runner.py campaign show SustainSpark8
```

### Workflow Management

```bash
# List workflows
python runner.py workflow-cli list

# Schedule campaign
python runner.py workflow-cli schedule --name "MyCampaign" --invite "2025-08-20T09:00:00"

# Check campaign status
python runner.py workflow-cli status --name "MyCampaign"
```

### System Management

```bash
# Check system status
python runner.py status

# Setup environment
python runner.py setup

# Install dependencies
python runner.py install

# Start API server
python runner.py api

# Start dashboard only
python runner.py dashboard

# Start Phidata agent
python runner.py phidata
```

## Campaign Structure

Campaigns are stored in the `campaigns/` directory with the following structure:

```
campaigns/
├── campaign_template.json          # Template for new campaigns
├── SustainSpark8/                  # Example campaign
│   ├── context.json               # Campaign details
│   ├── drafts/                    # Email drafts (auto-created)
│   └── assets/                    # Campaign assets (auto-created)
└── YourCampaign/                  # Your new campaign
    ├── context.json
    ├── drafts/
    └── assets/
```

### Campaign Context Fields

**Required:**
- `title`: Campaign title
- `objective`: Campaign goal
- `date`: Event date (YYYY-MM-DD)
- `target_audience`: List of audience segments
- `key_points`: Main benefits/features
- `call_to_action`: Action to take
- `registration_link`: Registration URL

**Optional:**
- `time`: Event time
- `location`: Event location
- `contact_email`: Contact information
- `website`: Campaign website
- `social_media`: Social media handles
- `sponsors`: List of sponsors
- `speakers`: List of speakers
- `agenda`: Event agenda

## Email Delivery

The system uses SMTP (HostGator) for reliable email delivery:

- **Server**: `gator3064.hostgator.com:465`
- **Authentication**: SSL/TLS
- **Sender**: `ash@a4gcollab.org`

## AI Content Generation

Powered by Google Gemini API for:
- Email subject line generation
- Email body content creation
- Content refinement based on performance
- Personalized messaging

## 🌐 Web Dashboard Features

### 📊 **Overview Dashboard**
- Real-time metrics and KPIs
- Quick action buttons
- Recent campaign overview
- System status monitoring

### 👥 **Contact Management**
- **CSV Upload**: Drag & drop contact files
- **Contact List**: View all contacts with search
- **Engagement Tracking**: Update open/click/reply events
- **Tag Management**: Automatic segmentation

### 📧 **Campaign Management**
- **Create Campaigns**: Interactive form with all fields
- **Campaign List**: View all campaigns with status
- **Schedule Workflows**: One-click campaign scheduling
- **Campaign Control**: Pause/resume campaigns

### 📈 **Analytics & Reports**
- **Performance Metrics**: Open rates, click rates, engagement
- **Campaign Analytics**: Detailed campaign performance
- **Visual Charts**: Interactive charts and graphs
- **Real-time Updates**: Live data refresh

### ⚙️ **Workflow Management**
- **Active Workflows**: View running campaigns
- **Scheduler Status**: Monitor automated processes
- **Workflow Control**: Manage campaign automation

## API Endpoints

- `GET /contacts` - List all contacts
- `POST /contacts/ingest` - Ingest CSV contacts
- `GET /contacts/tags/{tag}` - Get contacts by tag
- `GET /campaigns` - List campaigns
- `POST /campaigns/schedule` - Schedule campaign
- `GET /dashboard/metrics` - Get dashboard metrics

## Development

### Project Structure

- **Core Logic**: `services/` directory
- **Data Models**: `models/` directory
- **API Layer**: `api/` directory
- **CLI Tools**: `cli/` directory
- **Database**: `database/` directory

### Adding New Features

1. Create data models in `models/`
2. Implement business logic in `services/`
3. Add API endpoints in `api/`
4. Create CLI commands in `cli/`
5. Update `runner.py` for new commands

## Troubleshooting

### Common Issues

1. **MongoDB Connection**: Check your `MONGODB_URI` in `.env`
   - **SSL Issues**: If you encounter SSL handshake errors on Windows, try using the demo dashboard: `python demo_dashboard.py`
2. **Gemini API**: Verify your `GEMINI_API_KEY` is valid
3. **SMTP Issues**: Check SMTP credentials in `.env`
4. **Missing Dependencies**: Run `python runner.py install`

### Demo Mode

If you're experiencing MongoDB connection issues or want to see the dashboard functionality without setting up a database:

```bash
python demo_dashboard.py
```

This starts a demonstration version with:
- ✅ **Full UI functionality**
- ✅ **Simulated data**
- ✅ **All features working**
- ✅ **No database required**

### Getting Help

1. Check system status: `python runner.py status`
2. Review logs for error messages
3. Verify environment variables are set correctly
4. Ensure all dependencies are installed

## License

This project is licensed under the MIT License.
