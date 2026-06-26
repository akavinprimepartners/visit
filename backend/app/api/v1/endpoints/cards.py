"""
Business Card Endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, status
from typing import List, Optional
import os
import shutil
from datetime import datetime
import uuid

from app.services.ocr_service import ocr_service
from app.services.image_service import image_service
from app.models.card import Card, CardCreate
from app.schemas.card import CardResponse, CardOCRResult
from app.core.dependencies import get_current_user
from app.models.user import User
from app.core.database import Database

router = APIRouter(prefix="/cards", tags=["Business Cards"])
db = Database()

@router.post("/upload", response_model=CardResponse)
async def upload_card(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and process a business card"""
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        filepath = os.path.join(settings.STORAGE_PATH, "cards", filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save file
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process with OCR
        ocr_result = ocr_service.extract_text(filepath)
        
        if ocr_result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OCR failed: {ocr_result['error']}"
            )
        
        # Extract fields
        fields = ocr_service.extract_fields(ocr_result.get("text", ""))
        
        # Enhance image
        enhanced_path = image_service.enhance_image(filepath)
        
        # Create card record
        card_data = CardCreate(
            filename=filename,
            filepath=filepath,
            enhanced_path=enhanced_path,
            user_id=current_user._id,
            ocr_text=ocr_result.get("text", ""),
            ocr_confidence=ocr_result.get("confidence", 0),
            extracted_fields=fields,
            metadata={
                "file_size": os.path.getsize(filepath),
                "content_type": file.content_type
            }
        )
        
        # Save to database
        card_dict = card_data.dict()
        card_dict["_id"] = str(uuid.uuid4())
        card_dict["created_at"] = datetime.utcnow().isoformat()
        card_dict["updated_at"] = datetime.utcnow().isoformat()
        
        db.insert("cards", card_dict)
        
        return CardResponse(**card_dict)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@router.post("/batch-upload", response_model=List[CardResponse])
async def batch_upload_cards(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload multiple business cards"""
    results = []
    for file in files:
        try:
            result = await upload_card(file, current_user)
            results.append(result)
        except Exception as e:
            # Log error but continue with other cards
            print(f"Error processing {file.filename}: {str(e)}")
    
    return results

@router.get("/", response_model=List[CardResponse])
async def get_cards(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get all cards for current user"""
    cards = db.find("cards", {"user_id": current_user._id})
    return cards[skip:skip + limit]

@router.get("/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific card"""
    card = db.find_one("cards", {"_id": card_id, "user_id": current_user._id})
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    return CardResponse(**card)

@router.delete("/{card_id}")
async def delete_card(
    card_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a card"""
    card = db.find_one("cards", {"_id": card_id, "user_id": current_user._id})
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Delete files
    if card.get("filepath") and os.path.exists(card["filepath"]):
        os.remove(card["filepath"])
    if card.get("enhanced_path") and os.path.exists(card["enhanced_path"]):
        os.remove(card["enhanced_path"])
    
    db.delete("cards", {"_id": card_id})
    
    return {"message": "Card deleted successfully"}

@router.post("/{card_id}/ocr", response_model=CardOCRResult)
async def process_ocr(
    card_id: str,
    current_user: User = Depends(get_current_user)
):
    """Re-process OCR for a card"""
    card = db.find_one("cards", {"_id": card_id, "user_id": current_user._id})
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Process OCR
    ocr_result = ocr_service.extract_text(card["filepath"])
    
    if ocr_result.get("error"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR failed: {ocr_result['error']}"
        )
    
    # Extract fields
    fields = ocr_service.extract_fields(ocr_result.get("text", ""))
    
    # Update card
    db.update(
        "cards",
        {"_id": card_id},
        {
            "ocr_text": ocr_result.get("text", ""),
            "ocr_confidence": ocr_result.get("confidence", 0),
            "extracted_fields": fields,
            "updated_at": datetime.utcnow().isoformat()
        }
    )
    
    return CardOCRResult(
        text=ocr_result.get("text", ""),
        confidence=ocr_result.get("confidence", 0),
        fields=fields,
        engine=ocr_result.get("engine", "unknown")
    )
