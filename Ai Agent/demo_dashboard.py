#!/usr/bin/env python3
"""
AI Email Marketing Agent - Demo Dashboard
A demonstration version that works without MongoDB for showcasing the UI.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI Email Marketing Agent - Demo Dashboard", version="1.0.0")

# Create templates directory and HTML template
templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)

# Create static directory for CSS/JS
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create templates
templates = Jinja2Templates(directory="templates")

# Demo data
demo_contacts = [
    {
        "name": "John Smith",
        "email": "john.smith@school.edu",
        "role": "Principal",
        "tags": ["engaged", "high-interest"],
        "engagement": {"opened": 3, "clicked": 2, "replied": 1}
    },
    {
        "name": "Sarah Johnson",
        "email": "sarah.johnson@academy.edu",
        "role": "Principal",
        "tags": ["engaged"],
        "engagement": {"opened": 2, "clicked": 1, "replied": 0}
    },
    {
        "name": "Michael Brown",
        "email": "michael.brown@institute.edu",
        "role": "Principal",
        "tags": ["priority"],
        "engagement": {"opened": 5, "clicked": 3, "replied": 2}
    }
]

demo_campaigns = [
    {
        "name": "SustainSpark8",
        "title": "SustainSpark8 Youth Climate Event",
        "objective": "Maximize participation from schools and youth leaders",
        "date": "2025-09-20",
        "status": "active"
    },
    {
        "name": "TechEdu2025",
        "title": "Technology in Education Conference 2025",
        "objective": "Promote technology integration in schools",
        "date": "2025-10-15",
        "status": "draft"
    }
]

demo_metrics = {
    "total_contacts": 150,
    "active_campaigns": 2,
    "total_emails_sent": 450,
    "average_open_rate": 0.28,
    "average_click_rate": 0.08
}

# Create the main dashboard HTML template
dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Email Marketing Agent - Demo Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background: #2c3e50; }
        .sidebar .nav-link { color: #ecf0f1; }
        .sidebar .nav-link:hover { background: #34495e; }
        .sidebar .nav-link.active { background: #3498db; }
        .main-content { padding: 20px; }
        .card { margin-bottom: 20px; }
        .metric-card { text-align: center; padding: 20px; }
        .metric-value { font-size: 2em; font-weight: bold; color: #3498db; }
        .upload-area { border: 2px dashed #bdc3c7; padding: 40px; text-align: center; }
        .upload-area:hover { border-color: #3498db; }
        .campaign-card { border-left: 4px solid #3498db; }
        .status-active { color: #27ae60; }
        .status-paused { color: #f39c12; }
        .status-completed { color: #95a5a6; }
        .demo-banner { background: #f39c12; color: white; padding: 10px; text-align: center; }
    </style>
</head>
<body>
    <div class="demo-banner">
        <strong>DEMO MODE</strong> - This is a demonstration dashboard. All data is simulated.
    </div>
    
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <div class="position-sticky pt-3">
                    <div class="text-center mb-4">
                        <h4 class="text-white">AI Email Marketing Agent</h4>
                        <small class="text-muted">Demo Mode</small>
                    </div>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link active" href="#" onclick="showSection('overview')">
                                <i class="fas fa-tachometer-alt"></i> Overview
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="showSection('contacts')">
                                <i class="fas fa-users"></i> Contacts
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="showSection('campaigns')">
                                <i class="fas fa-bullhorn"></i> Campaigns
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="showSection('analytics')">
                                <i class="fas fa-chart-bar"></i> Analytics
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="showSection('workflows')">
                                <i class="fas fa-cogs"></i> Workflows
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Main content -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                <!-- Overview Section -->
                <div id="overview-section" class="section">
                    <h2><i class="fas fa-tachometer-alt"></i> Dashboard Overview</h2>
                    <div class="row">
                        <div class="col-md-3">
                            <div class="card metric-card">
                                <div class="metric-value" id="total-contacts">150</div>
                                <div>Total Contacts</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card metric-card">
                                <div class="metric-value" id="active-campaigns">2</div>
                                <div>Active Campaigns</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card metric-card">
                                <div class="metric-value" id="emails-sent">450</div>
                                <div>Emails Sent</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card metric-card">
                                <div class="metric-value" id="avg-open-rate">28.0%</div>
                                <div>Avg Open Rate</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5>Recent Campaigns</h5>
                                </div>
                                <div class="card-body" id="recent-campaigns">
                                    <div class="d-flex justify-content-between align-items-center mb-2">
                                        <div>
                                            <strong>SustainSpark8 Youth Climate Event</strong><br>
                                            <small class="text-muted">2025-09-20</small>
                                        </div>
                                        <span class="badge bg-success">active</span>
                                    </div>
                                    <div class="d-flex justify-content-between align-items-center mb-2">
                                        <div>
                                            <strong>Technology in Education Conference 2025</strong><br>
                                            <small class="text-muted">2025-10-15</small>
                                        </div>
                                        <span class="badge bg-secondary">draft</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5>Quick Actions</h5>
                                </div>
                                <div class="card-body">
                                    <button class="btn btn-primary mb-2 w-100" onclick="showSection('contacts')">
                                        <i class="fas fa-upload"></i> Upload Contacts
                                    </button>
                                    <button class="btn btn-success mb-2 w-100" onclick="showSection('campaigns')">
                                        <i class="fas fa-plus"></i> Create Campaign
                                    </button>
                                    <button class="btn btn-info mb-2 w-100" onclick="showSection('analytics')">
                                        <i class="fas fa-chart-line"></i> View Analytics
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Contacts Section -->
                <div id="contacts-section" class="section" style="display: none;">
                    <h2><i class="fas fa-users"></i> Contact Management</h2>
                    
                    <!-- Upload CSV -->
                    <div class="card">
                        <div class="card-header">
                            <h5>Upload Contact CSV</h5>
                        </div>
                        <div class="card-body">
                            <form id="upload-form" enctype="multipart/form-data">
                                <div class="upload-area" id="upload-area">
                                    <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                                    <p>Drag and drop your CSV file here or click to browse</p>
                                    <input type="file" id="csv-file" name="file" accept=".csv" style="display: none;">
                                    <button type="button" class="btn btn-outline-primary" onclick="document.getElementById('csv-file').click()">
                                        Choose File
                                    </button>
                                </div>
                                <div class="mt-3">
                                    <button type="submit" class="btn btn-primary">
                                        <i class="fas fa-upload"></i> Upload and Process
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>

                    <!-- Contact List -->
                    <div class="card mt-4">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5>Contact List</h5>
                            <div>
                                <input type="text" class="form-control" id="contact-search" placeholder="Search contacts...">
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Name</th>
                                            <th>Email</th>
                                            <th>Role</th>
                                            <th>Tags</th>
                                            <th>Engagement</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody id="contacts-table">
                                        <tr>
                                            <td>John Smith</td>
                                            <td>john.smith@school.edu</td>
                                            <td>Principal</td>
                                            <td><span class="badge bg-info">engaged</span> <span class="badge bg-warning">high-interest</span></td>
                                            <td>
                                                <small>
                                                    Opens: 3<br>
                                                    Clicks: 2<br>
                                                    Replies: 1
                                                </small>
                                            </td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary" onclick="updateEngagement('john.smith@school.edu', 'opened')">
                                                    <i class="fas fa-eye"></i>
                                                </button>
                                                <button class="btn btn-sm btn-outline-success" onclick="updateEngagement('john.smith@school.edu', 'clicked')">
                                                    <i class="fas fa-mouse-pointer"></i>
                                                </button>
                                                <button class="btn btn-sm btn-outline-warning" onclick="updateEngagement('john.smith@school.edu', 'replied')">
                                                    <i class="fas fa-reply"></i>
                                                </button>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>Sarah Johnson</td>
                                            <td>sarah.johnson@academy.edu</td>
                                            <td>Principal</td>
                                            <td><span class="badge bg-info">engaged</span></td>
                                            <td>
                                                <small>
                                                    Opens: 2<br>
                                                    Clicks: 1<br>
                                                    Replies: 0
                                                </small>
                                            </td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary" onclick="updateEngagement('sarah.johnson@academy.edu', 'opened')">
                                                    <i class="fas fa-eye"></i>
                                                </button>
                                                <button class="btn btn-sm btn-outline-success" onclick="updateEngagement('sarah.johnson@academy.edu', 'clicked')">
                                                    <i class="fas fa-mouse-pointer"></i>
                                                </button>
                                                <button class="btn btn-sm btn-outline-warning" onclick="updateEngagement('sarah.johnson@academy.edu', 'replied')">
                                                    <i class="fas fa-reply"></i>
                                                </button>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>Michael Brown</td>
                                            <td>michael.brown@institute.edu</td>
                                            <td>Principal</td>
                                            <td><span class="badge bg-danger">priority</span></td>
                                            <td>
                                                <small>
                                                    Opens: 5<br>
                                                    Clicks: 3<br>
                                                    Replies: 2
                                                </small>
                                            </td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary" onclick="updateEngagement('michael.brown@institute.edu', 'opened')">
                                                    <i class="fas fa-eye"></i>
                                                </button>
                                                <button class="btn btn-sm btn-outline-success" onclick="updateEngagement('michael.brown@institute.edu', 'clicked')">
                                                    <i class="fas fa-mouse-pointer"></i>
                                                </button>
                                                <button class="btn btn-sm btn-outline-warning" onclick="updateEngagement('michael.brown@institute.edu', 'replied')">
                                                    <i class="fas fa-reply"></i>
                                                </button>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Campaigns Section -->
                <div id="campaigns-section" class="section" style="display: none;">
                    <h2><i class="fas fa-bullhorn"></i> Campaign Management</h2>
                    
                    <!-- Create Campaign -->
                    <div class="card">
                        <div class="card-header">
                            <h5>Create New Campaign</h5>
                        </div>
                        <div class="card-body">
                            <form id="campaign-form">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Campaign Name</label>
                                            <input type="text" class="form-control" id="campaign-name" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Campaign Title</label>
                                            <input type="text" class="form-control" id="campaign-title" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Objective</label>
                                            <textarea class="form-control" id="campaign-objective" rows="3" required></textarea>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Event Date</label>
                                            <input type="date" class="form-control" id="campaign-date" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Target Audience</label>
                                            <input type="text" class="form-control" id="target-audience" placeholder="school principals, youth leaders">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Key Points (one per line)</label>
                                            <textarea class="form-control" id="key-points" rows="3" placeholder="Hands-on workshops&#10;Expert speakers&#10;Certification"></textarea>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Call to Action</label>
                                            <input type="text" class="form-control" id="call-to-action" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Registration Link</label>
                                            <input type="url" class="form-control" id="registration-link" required>
                                        </div>
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save"></i> Create Campaign
                                </button>
                            </form>
                        </div>
                    </div>

                    <!-- Campaign List -->
                    <div class="card mt-4">
                        <div class="card-header">
                            <h5>Your Campaigns</h5>
                        </div>
                        <div class="card-body" id="campaigns-list">
                            <div class="card campaign-card mb-3">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between align-items-start">
                                        <div>
                                            <h5 class="card-title">SustainSpark8 Youth Climate Event</h5>
                                            <p class="card-text">Maximize participation from schools and youth leaders</p>
                                            <small class="text-muted">Date: 2025-09-20</small>
                                        </div>
                                        <div class="text-end">
                                            <span class="badge bg-success">active</span>
                                            <br>
                                            <button class="btn btn-sm btn-primary mt-2" onclick="scheduleCampaign('SustainSpark8')">
                                                <i class="fas fa-play"></i> Schedule
                                            </button>
                                            <button class="btn btn-sm btn-warning mt-2" onclick="pauseCampaign('SustainSpark8')">
                                                <i class="fas fa-pause"></i> Pause
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="card campaign-card mb-3">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between align-items-start">
                                        <div>
                                            <h5 class="card-title">Technology in Education Conference 2025</h5>
                                            <p class="card-text">Promote technology integration in schools</p>
                                            <small class="text-muted">Date: 2025-10-15</small>
                                        </div>
                                        <div class="text-end">
                                            <span class="badge bg-secondary">draft</span>
                                            <br>
                                            <button class="btn btn-sm btn-primary mt-2" onclick="scheduleCampaign('TechEdu2025')">
                                                <i class="fas fa-play"></i> Schedule
                                            </button>
                                            <button class="btn btn-sm btn-warning mt-2" onclick="pauseCampaign('TechEdu2025')">
                                                <i class="fas fa-pause"></i> Pause
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Analytics Section -->
                <div id="analytics-section" class="section" style="display: none;">
                    <h2><i class="fas fa-chart-bar"></i> Analytics & Reports</h2>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5>Engagement Overview</h5>
                                </div>
                                <div class="card-body">
                                    <canvas id="engagement-chart"></canvas>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5>Campaign Performance</h5>
                                </div>
                                <div class="card-body">
                                    <canvas id="performance-chart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="card mt-4">
                        <div class="card-header">
                            <h5>Detailed Analytics</h5>
                        </div>
                        <div class="card-body" id="detailed-analytics">
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="card text-center">
                                        <div class="card-body">
                                            <h3 class="text-primary">150</h3>
                                            <p>Total Contacts</p>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card text-center">
                                        <div class="card-body">
                                            <h3 class="text-success">450</h3>
                                            <p>Emails Sent</p>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card text-center">
                                        <div class="card-body">
                                            <h3 class="text-info">28.0%</h3>
                                            <p>Open Rate</p>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card text-center">
                                        <div class="card-body">
                                            <h3 class="text-warning">8.0%</h3>
                                            <p>Click Rate</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Workflows Section -->
                <div id="workflows-section" class="section" style="display: none;">
                    <h2><i class="fas fa-cogs"></i> Workflow Management</h2>
                    
                    <div class="card">
                        <div class="card-header">
                            <h5>Active Workflows</h5>
                        </div>
                        <div class="card-body" id="workflows-list">
                            <div class="card mb-3">
                                <div class="card-body">
                                    <h5>SustainSpark8</h5>
                                    <p>Status: <span class="badge bg-success">active</span></p>
                                    <p>Next Run: 2025-08-16 14:00:00</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <script>
        // Dashboard JavaScript functionality
        let currentSection = 'overview';
        
        // Navigation
        function showSection(section) {
            // Hide all sections
            document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
            // Show selected section
            document.getElementById(section + '-section').style.display = 'block';
            // Update navigation
            document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
            event.target.classList.add('active');
            currentSection = section;
        }
        
        // Update engagement (demo)
        function updateEngagement(email, eventType) {
            alert(`Demo: Updated ${eventType} for ${email}`);
        }
        
        // Schedule campaign (demo)
        function scheduleCampaign(campaignName) {
            alert(`Demo: Scheduled campaign ${campaignName}`);
        }
        
        // Pause campaign (demo)
        function pauseCampaign(campaignName) {
            alert(`Demo: Paused campaign ${campaignName}`);
        }
        
        // File upload handling (demo)
        document.getElementById('csv-file').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('upload-area').innerHTML = `
                    <i class="fas fa-file-csv fa-3x text-success mb-3"></i>
                    <p>Selected: ${file.name}</p>
                    <button type="button" class="btn btn-outline-primary" onclick="document.getElementById('csv-file').click()">
                        Change File
                    </button>
                `;
            }
        });
        
        // CSV upload form (demo)
        document.getElementById('upload-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            alert('Demo: CSV file would be processed here');
        });
        
        // Campaign form (demo)
        document.getElementById('campaign-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            alert('Demo: Campaign would be created here');
            document.getElementById('campaign-form').reset();
        });
        
        // Search functionality
        document.getElementById('contact-search').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#contacts-table tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    </script>
</body>
</html>
"""

# Write the HTML template to file
with open(templates_dir / "dashboard.html", "w", encoding="utf-8") as f:
    f.write(dashboard_html)

# API Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Demo API endpoints
@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Get demo dashboard metrics."""
    return JSONResponse(content=demo_metrics)

@app.get("/api/contacts")
async def get_contacts():
    """Get demo contacts."""
    return JSONResponse(content=demo_contacts)

@app.get("/api/campaigns")
async def get_campaigns():
    """Get demo campaigns."""
    return JSONResponse(content=demo_campaigns)

@app.get("/api/workflows")
async def get_workflows():
    """Get demo workflows."""
    workflows = [
        {
            "campaign_name": "SustainSpark8",
            "status": "active",
            "next_run": "2025-08-16T14:00:00"
        }
    ]
    return JSONResponse(content=workflows)

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8001"))
    
    logger.info(f"Starting AI Email Marketing Agent Demo Dashboard on {host}:{port}")
    logger.info(f"Dashboard URL: http://localhost:{port}")
    logger.info("This is a DEMO version - all data is simulated")
    
    # Start the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=True
    )
