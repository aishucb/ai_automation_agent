"""
AI Email Marketing Agent - Audience Segmentation Module

A comprehensive audience segmentation module built with Python, Phidata framework, 
and MongoDB Atlas for managing email marketing contacts and engagement tracking.
"""

__version__ = "1.0.0"
__author__ = "AI Email Marketing Agent Team"
__description__ = "Audience segmentation module for email marketing campaigns"

from .services.contact_service import ContactService
from .models.contact import Contact, ContactCreate, ContactUpdate, ContactResponse, IngestionResult

__all__ = [
    "ContactService",
    "Contact", 
    "ContactCreate",
    "ContactUpdate",
    "ContactResponse",
    "IngestionResult"
]
