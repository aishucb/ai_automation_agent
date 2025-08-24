import os
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Dict
import uvicorn

from services.contact_service import ContactService
from models.contact import ContactUpdate, ContactResponse, IngestionResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Email Marketing Agent - Audience Segmentation",
    description="API for managing contacts and audience segmentation",
    version="1.0.0"
)

# Initialize service
contact_service = ContactService()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Email Marketing Agent - Audience Segmentation API",
        "version": "1.0.0",
        "endpoints": {
            "ingest_csv": "POST /ingest-csv",
            "update_engagement": "POST /update-engagement",
            "get_contacts_by_tag": "GET /contacts/tag/{tag}",
            "get_tag_counts": "GET /contacts/tags/counts",
            "get_all_contacts": "GET /contacts"
        }
    }

@app.post("/ingest-csv", response_model=ContactResponse)
async def ingest_csv_endpoint(file: UploadFile = File(...)):
    """Ingest contacts from uploaded CSV file."""
    try:
        # Save uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process CSV
        result = contact_service.ingest_csv(temp_file_path)
        
        # Clean up temp file
        os.remove(temp_file_path)
        
        return ContactResponse(
            success=True,
            message=f"CSV ingestion completed: {result.contacts_added} contacts added, "
                   f"{result.duplicates_skipped} duplicates skipped, "
                   f"{result.invalid_emails} invalid emails",
            data={
                "total_processed": result.total_processed,
                "contacts_added": result.contacts_added,
                "duplicates_skipped": result.duplicates_skipped,
                "invalid_emails": result.invalid_emails,
                "errors": result.errors
            }
        )
        
    except Exception as e:
        logger.error(f"Error in CSV ingestion endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-engagement", response_model=ContactResponse)
async def update_engagement_endpoint(contact_update: ContactUpdate):
    """Update contact engagement and add appropriate tags."""
    try:
        success = contact_service.update_contact_engagement(
            contact_update.email, 
            contact_update.event_type
        )
        
        if success:
            return ContactResponse(
                success=True,
                message=f"Engagement updated for {contact_update.email}: {contact_update.event_type}"
            )
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Contact not found: {contact_update.email}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating engagement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contacts/tag/{tag}", response_model=ContactResponse)
async def get_contacts_by_tag_endpoint(tag: str):
    """Get all contacts with a specific tag."""
    try:
        contacts = contact_service.get_contacts_by_tag(tag)
        
        return ContactResponse(
            success=True,
            message=f"Found {len(contacts)} contacts with tag '{tag}'",
            data={"contacts": contacts},
            count=len(contacts)
        )
        
    except Exception as e:
        logger.error(f"Error fetching contacts by tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contacts/tags/counts", response_model=ContactResponse)
async def get_tag_counts_endpoint():
    """Get counts of contacts for each tag."""
    try:
        tag_counts = contact_service.get_contact_counts_by_tag()
        
        return ContactResponse(
            success=True,
            message="Tag counts retrieved successfully",
            data={"tag_counts": tag_counts}
        )
        
    except Exception as e:
        logger.error(f"Error getting tag counts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contacts", response_model=ContactResponse)
async def get_all_contacts_endpoint(limit: int = 100):
    """Get all contacts with optional limit."""
    try:
        contacts = contact_service.get_all_contacts(limit)
        
        return ContactResponse(
            success=True,
            message=f"Retrieved {len(contacts)} contacts",
            data={"contacts": contacts},
            count=len(contacts)
        )
        
    except Exception as e:
        logger.error(f"Error fetching contacts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contacts/{email}", response_model=ContactResponse)
async def get_contact_by_email_endpoint(email: str):
    """Get a specific contact by email."""
    try:
        contact = contact_service.get_contact_by_email(email)
        
        if contact:
            return ContactResponse(
                success=True,
                message=f"Contact found: {email}",
                data={"contact": contact}
            )
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Contact not found: {email}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching contact: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
