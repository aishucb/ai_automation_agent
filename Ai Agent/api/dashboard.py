#!/usr/bin/env python3
"""
Comprehensive AI Email Marketing Agent Dashboard
Provides full UI for all functionality including CSV upload, campaign management, and analytics.
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

# Add project root to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our services
from services.contact_service import ContactService
from services.campaign_service import CampaignService
from services.workflow_service import WorkflowService
from services.smtp_service import SMTPService
from models.contact import ContactCreate, ContactUpdate
from models.campaign import CampaignContext, EmailContent
from models.workflow import WorkflowPlan, CampaignTargets

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI Email Marketing Agent Dashboard", version="1.0.0")

# Initialize services
contact_service = ContactService()
campaign_service = CampaignService()
workflow_service = WorkflowService()
smtp_service = SMTPService()

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

# Create the main dashboard HTML template
dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Email Marketing Agent Dashboard</title>
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
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <div class="position-sticky pt-3">
                    <div class="text-center mb-4">
                        <h4 class="text-white">AI Email Marketing Agent</h4>
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
                                <div class="metric-value" id="total-contacts">-</div>
                                <div>Total Contacts</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card metric-card">
                                <div class="metric-value" id="active-campaigns">-</div>
                                <div>Active Campaigns</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card metric-card">
                                <div class="metric-value" id="emails-sent">-</div>
                                <div>Emails Sent</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card metric-card">
                                <div class="metric-value" id="avg-open-rate">-</div>
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
                                    <p class="text-muted">Loading...</p>
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
                                        <tr><td colspan="6" class="text-center">Loading contacts...</td></tr>
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
                            <p class="text-muted">Loading campaigns...</p>
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
                            <p class="text-muted">Loading analytics...</p>
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
                            <p class="text-muted">Loading workflows...</p>
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
            
            // Load section data
            loadSectionData(section);
        }
        
        // Load data for each section
        async function loadSectionData(section) {
            switch(section) {
                case 'overview':
                    await loadOverviewData();
                    break;
                case 'contacts':
                    await loadContactsData();
                    break;
                case 'campaigns':
                    await loadCampaignsData();
                    break;
                case 'analytics':
                    await loadAnalyticsData();
                    break;
                case 'workflows':
                    await loadWorkflowsData();
                    break;
            }
        }
        
        // Overview data
        async function loadOverviewData() {
            try {
                const response = await fetch('/api/dashboard/metrics');
                const data = await response.json();
                
                document.getElementById('total-contacts').textContent = data.total_contacts || 0;
                document.getElementById('active-campaigns').textContent = data.active_campaigns || 0;
                document.getElementById('emails-sent').textContent = data.total_emails_sent || 0;
                document.getElementById('avg-open-rate').textContent = ((data.average_open_rate || 0) * 100).toFixed(1) + '%';
                
                // Load recent campaigns
                const campaignsResponse = await fetch('/api/campaigns');
                const campaigns = await campaignsResponse.json();
                displayRecentCampaigns(campaigns.slice(0, 5));
                
            } catch (error) {
                console.error('Error loading overview data:', error);
            }
        }
        
        // Display recent campaigns
        function displayRecentCampaigns(campaigns) {
            const container = document.getElementById('recent-campaigns');
            if (campaigns.length === 0) {
                container.innerHTML = '<p class="text-muted">No campaigns yet</p>';
                return;
            }
            
            container.innerHTML = campaigns.map(campaign => `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                        <strong>${campaign.title}</strong><br>
                        <small class="text-muted">${campaign.date}</small>
                    </div>
                    <span class="badge bg-${campaign.status === 'active' ? 'success' : 'secondary'}">${campaign.status}</span>
                </div>
            `).join('');
        }
        
        // Contacts data
        async function loadContactsData() {
            try {
                const response = await fetch('/api/contacts');
                const contacts = await response.json();
                displayContacts(contacts);
            } catch (error) {
                console.error('Error loading contacts:', error);
            }
        }
        
        // Display contacts
        function displayContacts(contacts) {
            const tbody = document.getElementById('contacts-table');
            if (contacts.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">No contacts found</td></tr>';
                return;
            }
            
            tbody.innerHTML = contacts.map(contact => `
                <tr>
                    <td>${contact.name}</td>
                    <td>${contact.email}</td>
                    <td>${contact.role || '-'}</td>
                    <td>${contact.tags.map(tag => `<span class="badge bg-info">${tag}</span>`).join(' ')}</td>
                    <td>
                        <small>
                            Opens: ${contact.engagement.opened}<br>
                            Clicks: ${contact.engagement.clicked}<br>
                            Replies: ${contact.engagement.replied}
                        </small>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="updateEngagement('${contact.email}', 'opened')">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="updateEngagement('${contact.email}', 'clicked')">
                            <i class="fas fa-mouse-pointer"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning" onclick="updateEngagement('${contact.email}', 'replied')">
                            <i class="fas fa-reply"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
        // Update engagement
        async function updateEngagement(email, eventType) {
            try {
                const response = await fetch('/api/contacts/engagement', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, event_type: eventType })
                });
                
                if (response.ok) {
                    await loadContactsData();
                    await loadOverviewData();
                }
            } catch (error) {
                console.error('Error updating engagement:', error);
            }
        }
        
        // Campaigns data
        async function loadCampaignsData() {
            try {
                const response = await fetch('/api/campaigns');
                const campaigns = await response.json();
                displayCampaigns(campaigns);
            } catch (error) {
                console.error('Error loading campaigns:', error);
            }
        }
        
        // Display campaigns
        function displayCampaigns(campaigns) {
            const container = document.getElementById('campaigns-list');
            if (campaigns.length === 0) {
                container.innerHTML = '<p class="text-muted">No campaigns yet</p>';
                return;
            }
            
            container.innerHTML = campaigns.map(campaign => `
                <div class="card campaign-card mb-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h5 class="card-title">${campaign.title}</h5>
                                <p class="card-text">${campaign.objective}</p>
                                <small class="text-muted">Date: ${campaign.date}</small>
                            </div>
                            <div class="text-end">
                                <span class="badge bg-${campaign.status === 'active' ? 'success' : 'secondary'}">${campaign.status}</span>
                                <br>
                                <button class="btn btn-sm btn-primary mt-2" onclick="scheduleCampaign('${campaign.name}')">
                                    <i class="fas fa-play"></i> Schedule
                                </button>
                                <button class="btn btn-sm btn-warning mt-2" onclick="pauseCampaign('${campaign.name}')">
                                    <i class="fas fa-pause"></i> Pause
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        // Analytics data
        async function loadAnalyticsData() {
            try {
                const response = await fetch('/api/dashboard/metrics');
                const data = await response.json();
                displayAnalytics(data);
            } catch (error) {
                console.error('Error loading analytics:', error);
            }
        }
        
        // Display analytics
        function displayAnalytics(data) {
            const container = document.getElementById('detailed-analytics');
            container.innerHTML = `
                <div class="row">
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h3 class="text-primary">${data.total_contacts || 0}</h3>
                                <p>Total Contacts</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h3 class="text-success">${data.total_emails_sent || 0}</h3>
                                <p>Emails Sent</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h3 class="text-info">${((data.average_open_rate || 0) * 100).toFixed(1)}%</h3>
                                <p>Open Rate</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h3 class="text-warning">${((data.average_click_rate || 0) * 100).toFixed(1)}%</h3>
                                <p>Click Rate</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Workflows data
        async function loadWorkflowsData() {
            try {
                const response = await fetch('/api/workflows');
                const workflows = await response.json();
                displayWorkflows(workflows);
            } catch (error) {
                console.error('Error loading workflows:', error);
            }
        }
        
        // Display workflows
        function displayWorkflows(workflows) {
            const container = document.getElementById('workflows-list');
            if (workflows.length === 0) {
                container.innerHTML = '<p class="text-muted">No active workflows</p>';
                return;
            }
            
            container.innerHTML = workflows.map(workflow => `
                <div class="card mb-3">
                    <div class="card-body">
                        <h5>${workflow.campaign_name}</h5>
                        <p>Status: <span class="badge bg-${workflow.status === 'active' ? 'success' : 'secondary'}">${workflow.status}</span></p>
                        <p>Next Run: ${workflow.next_run || 'N/A'}</p>
                    </div>
                </div>
            `).join('');
        }
        
        // File upload handling
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
        
        // CSV upload form
        document.getElementById('upload-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('csv-file');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a CSV file');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/api/contacts/ingest', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert(`Successfully uploaded ${result.contacts_added} contacts`);
                    await loadContactsData();
                    await loadOverviewData();
                } else {
                    alert('Error uploading file: ' + result.detail);
                }
            } catch (error) {
                console.error('Error uploading file:', error);
                alert('Error uploading file');
            }
        });
        
        // Campaign form
        document.getElementById('campaign-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('campaign-name').value,
                title: document.getElementById('campaign-title').value,
                objective: document.getElementById('campaign-objective').value,
                date: document.getElementById('campaign-date').value,
                target_audience: document.getElementById('target-audience').value.split(',').map(s => s.trim()),
                key_points: document.getElementById('key-points').value.split('\\n').filter(s => s.trim()),
                call_to_action: document.getElementById('call-to-action').value,
                registration_link: document.getElementById('registration-link').value
            };
            
            try {
                const response = await fetch('/api/campaigns', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert('Campaign created successfully!');
                    document.getElementById('campaign-form').reset();
                    await loadCampaignsData();
                    await loadOverviewData();
                } else {
                    alert('Error creating campaign: ' + result.detail);
                }
            } catch (error) {
                console.error('Error creating campaign:', error);
                alert('Error creating campaign');
            }
        });
        
        // Schedule campaign
        async function scheduleCampaign(campaignName) {
            try {
                const response = await fetch('/api/workflows/schedule', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        campaign_name: campaignName,
                        workflow_plan: {
                            invite: new Date(Date.now() + 60000).toISOString(), // 1 minute from now
                            reminder: new Date(Date.now() + 86400000).toISOString(), // 1 day from now
                            thank_you: new Date(Date.now() + 172800000).toISOString(), // 2 days from now
                            follow_up: new Date(Date.now() + 259200000).toISOString() // 3 days from now
                        },
                        targets: {
                            total_emails_sent: 100,
                            target_open_rate: 0.25,
                            target_click_rate: 0.05
                        }
                    })
                });
                
                if (response.ok) {
                    alert('Campaign scheduled successfully!');
                    await loadWorkflowsData();
                } else {
                    alert('Error scheduling campaign');
                }
            } catch (error) {
                console.error('Error scheduling campaign:', error);
                alert('Error scheduling campaign');
            }
        }
        
        // Pause campaign
        async function pauseCampaign(campaignName) {
            try {
                const response = await fetch(`/api/workflows/${campaignName}/pause`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    alert('Campaign paused successfully!');
                    await loadCampaignsData();
                    await loadWorkflowsData();
                } else {
                    alert('Error pausing campaign');
                }
            } catch (error) {
                console.error('Error pausing campaign:', error);
                alert('Error pausing campaign');
            }
        }
        
        // Search functionality
        document.getElementById('contact-search').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#contacts-table tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadOverviewData();
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

# Dashboard metrics
@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Get dashboard metrics."""
    try:
        metrics = workflow_service.get_dashboard_metrics()
        return JSONResponse(content=metrics.model_dump())
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        return JSONResponse(
            content={"error": "Failed to get metrics"},
            status_code=500
        )

# Contacts API
@app.get("/api/contacts")
async def get_contacts():
    """Get all contacts."""
    try:
        contacts = contact_service.get_all_contacts()
        return JSONResponse(content=contacts)
    except Exception as e:
        logger.error(f"Error getting contacts: {e}")
        return JSONResponse(
            content={"error": "Failed to get contacts"},
            status_code=500
        )

@app.post("/api/contacts/ingest")
async def ingest_csv(file: UploadFile = File(...)):
    """Upload and ingest CSV file."""
    try:
        # Save uploaded file temporarily
        temp_file = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(temp_file, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the file
        result = contact_service.ingest_csv(temp_file)
        
        # Clean up temp file
        os.remove(temp_file)
        
        return JSONResponse(content=result.model_dump())
    except Exception as e:
        logger.error(f"Error ingesting CSV: {e}")
        return JSONResponse(
            content={"error": f"Failed to ingest CSV: {str(e)}"},
            status_code=500
        )

@app.post("/api/contacts/engagement")
async def update_engagement(request: Request):
    """Update contact engagement."""
    try:
        data = await request.json()
        email = data.get("email")
        event_type = data.get("event_type")
        
        if not email or not event_type:
            return JSONResponse(
                content={"error": "Email and event_type are required"},
                status_code=400
            )
        
        contact_service.update_contact_engagement(email, event_type)
        return JSONResponse(content={"message": "Engagement updated successfully"})
    except Exception as e:
        logger.error(f"Error updating engagement: {e}")
        return JSONResponse(
            content={"error": f"Failed to update engagement: {str(e)}"},
            status_code=500
        )

# Campaigns API
@app.get("/api/campaigns")
async def get_campaigns():
    """Get all campaigns."""
    try:
        campaigns = campaign_service.get_all_campaigns()
        return JSONResponse(content=[campaign.model_dump() for campaign in campaigns])
    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        return JSONResponse(
            content={"error": "Failed to get campaigns"},
            status_code=500
        )

@app.post("/api/campaigns")
async def create_campaign(request: Request):
    """Create a new campaign."""
    try:
        data = await request.json()
        
        # Create campaign context
        context = CampaignContext(
            title=data["title"],
            objective=data["objective"],
            date=data["date"],
            target_audience=data.get("target_audience", []),
            key_points=data.get("key_points", []),
            call_to_action=data["call_to_action"],
            registration_link=data["registration_link"]
        )
        
        # Save campaign
        campaign_service.save_campaign_context(data["name"], context)
        
        return JSONResponse(content={"message": "Campaign created successfully"})
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        return JSONResponse(
            content={"error": f"Failed to create campaign: {str(e)}"},
            status_code=500
        )

# Workflows API
@app.get("/api/workflows")
async def get_workflows():
    """Get all workflows."""
    try:
        campaigns = workflow_service.get_all_campaigns()
        workflows = []
        
        for campaign in campaigns:
            status = workflow_service.get_campaign_status(campaign.name)
            if status:
                workflows.append({
                    "campaign_name": campaign.name,
                    "status": campaign.status,
                    "next_run": status.next_scheduled_action.isoformat() if status.next_scheduled_action else None
                })
        
        return JSONResponse(content=workflows)
    except Exception as e:
        logger.error(f"Error getting workflows: {e}")
        return JSONResponse(
            content={"error": "Failed to get workflows"},
            status_code=500
        )

@app.post("/api/workflows/schedule")
async def schedule_workflow(request: Request):
    """Schedule a workflow."""
    try:
        data = await request.json()
        
        workflow_plan = WorkflowPlan(**data["workflow_plan"])
        targets = CampaignTargets(**data["targets"])
        
        success = workflow_service.schedule_campaign(
            data["campaign_name"],
            workflow_plan,
            targets
        )
        
        if success:
            return JSONResponse(content={"message": "Workflow scheduled successfully"})
        else:
            return JSONResponse(
                content={"error": "Failed to schedule workflow"},
                status_code=500
            )
    except Exception as e:
        logger.error(f"Error scheduling workflow: {e}")
        return JSONResponse(
            content={"error": f"Failed to schedule workflow: {str(e)}"},
            status_code=500
        )

@app.post("/api/workflows/{campaign_name}/pause")
async def pause_workflow(campaign_name: str):
    """Pause a workflow."""
    try:
        success = workflow_service.pause_campaign(campaign_name)
        
        if success:
            return JSONResponse(content={"message": "Workflow paused successfully"})
        else:
            return JSONResponse(
                content={"error": "Failed to pause workflow"},
                status_code=500
            )
    except Exception as e:
        logger.error(f"Error pausing workflow: {e}")
        return JSONResponse(
            content={"error": f"Failed to pause workflow: {str(e)}"},
            status_code=500
        )

@app.post("/api/workflows/{campaign_name}/resume")
async def resume_workflow(campaign_name: str):
    """Resume a workflow."""
    try:
        success = workflow_service.resume_campaign(campaign_name)
        
        if success:
            return JSONResponse(content={"message": "Workflow resumed successfully"})
        else:
            return JSONResponse(
                content={"error": "Failed to resume workflow"},
                status_code=500
            )
    except Exception as e:
        logger.error(f"Error resuming workflow: {e}")
        return JSONResponse(
            content={"error": f"Failed to resume workflow: {str(e)}"},
            status_code=500
        )

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8001"))
    
    logger.info(f"Starting AI Email Marketing Agent Dashboard on {host}:{port}")
    logger.info(f"Dashboard URL: http://localhost:{port}")
    
    # Start the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=True
    )
