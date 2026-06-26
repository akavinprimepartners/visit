"""
Card Schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime

class CardResponse(BaseModel):
    """Card response"""
    _id: str
    filename: str
    filepath: str
    enhanced_path: Optional[str]
    thumbnail_path: Optional[str]
    user_id: str
    ocr_text: Optional[str]
    ocr_confidence: Optional[float]
    extracted_fields: Dict[str, Any]
    metadata: Dict[str, Any]
    tags: List[str]
    notes: Optional[str]
    created_at: str
    updated_at: str

class CardOCRResult(BaseModel):
    """OCR result"""
    text: str
    confidence: float
    fields: Dict[str, Any]
    engine: str

class CardUploadResponse(BaseModel):
    """Card upload response"""
    id: str
    filename: str
    status: str
    message: str
    ocr_confidence: Optional[float] = None
    extracted_fields: Optional[Dict[str, Any]] = None
