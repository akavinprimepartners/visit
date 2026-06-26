"""
OCR Service - Handles text extraction from business cards
"""

import os
import re
import cv2
import numpy as np
from PIL import Image
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class OCRService:
    """OCR service for business card text extraction"""
    
    def __init__(self):
        self.engine = settings.OCR_ENGINE
        self.language = settings.OCR_LANGUAGE
        self._init_engine()
    
    def _init_engine(self):
        """Initialize OCR engine"""
        if self.engine == "paddleocr":
            try:
                from paddleocr import PaddleOCR
                self.ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang=self.language,
                    show_log=False
                )
                logger.info("✅ PaddleOCR initialized")
            except ImportError:
                logger.warning("PaddleOCR not installed, falling back to Tesseract")
                self.engine = "tesseract"
                self._init_tesseract()
        elif self.engine == "tesseract":
            self._init_tesseract()
        else:
            self._init_tesseract()
    
    def _init_tesseract(self):
        """Initialize Tesseract OCR"""
        try:
            import pytesseract
            self.ocr = pytesseract
            logger.info("✅ Tesseract initialized")
        except ImportError:
            logger.error("No OCR engine available. Install PaddleOCR or Tesseract.")
            self.ocr = None
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        # Sharpen
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        return sharpened
    
    def extract_text(self, image_path: str) -> Dict[str, Any]:
        """Extract text from image"""
        if self.ocr is None:
            return {"text": "", "error": "OCR engine not available"}
        
        try:
            # Preprocess image
            processed = self.preprocess_image(image_path)
            
            # Save processed image temporarily
            temp_path = "/tmp/processed_card.jpg"
            cv2.imwrite(temp_path, processed)
            
            # Extract text
            if self.engine == "paddleocr":
                result = self.ocr.ocr(temp_path, cls=True)
                text_lines = []
                confidence_scores = []
                
                for line in result:
                    for item in line:
                        text_lines.append(item[1][0])
                        confidence_scores.append(item[1][1])
                
                text = "\n".join(text_lines)
                avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
                
                return {
                    "text": text,
                    "confidence": avg_confidence,
                    "lines": text_lines,
                    "engine": self.engine
                }
            
            elif self.engine == "tesseract":
                # Configure Tesseract
                custom_config = r'--oem 3 --psm 6'
                text = self.ocr.image_to_string(
                    Image.open(temp_path),
                    config=custom_config,
                    lang=self.language
                )
                
                # Get confidence data
                confidence_data = self.ocr.image_to_data(
                    Image.open(temp_path),
                    config=custom_config,
                    lang=self.language,
                    output_type='dict'
                )
                
                # Calculate average confidence
                confidences = [int(c) for c in confidence_data.get('conf', []) if int(c) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                return {
                    "text": text.strip(),
                    "confidence": avg_confidence,
                    "lines": [line.strip() for line in text.strip().split('\n') if line.strip()],
                    "engine": self.engine
                }
            
            # Clean up
            os.remove(temp_path)
            
            return {"text": "", "error": "OCR processing failed"}
            
        except Exception as e:
            logger.error(f"OCR Error: {str(e)}")
            return {"text": "", "error": str(e)}
    
    def extract_fields(self, text: str) -> Dict[str, Any]:
        """Extract structured fields from OCR text"""
        fields = {
            "name": "",
            "company": "",
            "designation": "",
            "phone": [],
            "email": "",
            "website": "",
            "address": "",
            "social": {}
        }
        
        lines = text.split('\n')
        
        # Patterns
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        phone_pattern = r'(\+?\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}'
        url_pattern = r'(https?://)?(www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/\S*)?'
        
        # Extract email
        for line in lines:
            emails = re.findall(email_pattern, line)
            if emails and not fields["email"]:
                fields["email"] = emails[0]
        
        # Extract phone numbers
        phone_numbers = []
        for line in lines:
            phones = re.findall(phone_pattern, line)
            phone_numbers.extend(phones)
        fields["phone"] = list(set(phone_numbers))
        
        # Extract website
        for line in lines:
            urls = re.findall(url_pattern, line)
            if urls:
                url = urls[0]
                if isinstance(url, tuple):
                    url = url[0] or url[1] or url[2]
                if url and not fields["website"]:
                    fields["website"] = url
        
        # Heuristic for name, company, designation
        # Name: Usually first line, 2-3 words
        if lines and len(lines[0].split()) <= 5:
            fields["name"] = lines[0].strip()
        
        # Company: Usually second line or contains "Inc", "Ltd", "LLC", etc.
        company_patterns = r'(Inc|Ltd|LLC|Corp|Corporation|Company|Co\.|Pvt|Private)'
        for line in lines[1:5] if len(lines) > 1 else []:
            if re.search(company_patterns, line, re.IGNORECASE):
                fields["company"] = line.strip()
                break
        
        # Designation: Contains keywords like "Manager", "Director", "CEO", etc.
        designation_patterns = r'(Manager|Director|CEO|CFO|CTO|President|VP|Head|Lead|Engineer|Architect|Developer|Consultant|Analyst)'
        for line in lines[1:5] if len(lines) > 1 else []:
            if re.search(designation_patterns, line, re.IGNORECASE):
                if line != fields["company"] and line != fields["name"]:
                    fields["designation"] = line.strip()
                    break
        
        return fields

# Singleton instance
ocr_service = OCRService()
