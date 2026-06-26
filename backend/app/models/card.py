"""
Card Models
"""

from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime

class Card(BaseModel):
    """Business Card Model"""
    _id: Optional[str] = None
    filename: str
    filepath: str
    enhanced_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    user_id: str
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = 0.0
    extracted_fields: Optional[Dict[str, Any]] = {}
    metadata: Optional[Dict[str, Any]] = {}
    tags: List[str] = []
    notes: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class CardCreate(BaseModel):
    """Card creation model"""
    filename: str
    filepath: str
    enhanced_path: Optional[str] = None
    user_id: str
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = 0.0
    extracted_fields: Optional[Dict[str, Any]] = {}
    metadata: Optional[Dict[str, Any]] = {}
    tags: List[str] = []

class CardUpdate(BaseModel):
    """Card update model"""
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    extracted_fields: Optional[Dict[str, Any]] = None
