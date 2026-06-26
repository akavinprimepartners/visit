"""
Image Processing Service
"""

import cv2
import numpy as np
from PIL import Image
import os
from pathlib import Path
from typing import Optional, Tuple
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class ImageService:
    """Image processing service for business cards"""
    
    def __init__(self):
        self.storage_path = settings.STORAGE_PATH
        self.cards_path = self.storage_path / "cards"
        self.enhanced_path = self.storage_path / "enhanced"
        self.thumbnails_path = self.storage_path / "thumbnails"
        
        # Create directories
        self.cards_path.mkdir(parents=True, exist_ok=True)
        self.enhanced_path.mkdir(parents=True, exist_ok=True)
        self.thumbnails_path.mkdir(parents=True, exist_ok=True)
    
    def enhance_image(self, image_path: str) -> str:
        """Enhance image quality"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
            
            # Sharpen
            kernel = np.array([[-1,-1,-1],
                              [-1, 9,-1],
                              [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            
            # Save enhanced image
            filename = os.path.basename(image_path)
            enhanced_filename = f"enhanced_{filename}"
            enhanced_filepath = self.enhanced_path / enhanced_filename
            
            cv2.imwrite(str(enhanced_filepath), sharpened)
            
            # Create thumbnail
            self.create_thumbnail(str(enhanced_filepath))
            
            return str(enhanced_filepath)
            
        except Exception as e:
            logger.error(f"Image enhancement failed: {str(e)}")
            return image_path
    
    def create_thumbnail(self, image_path: str, size: Tuple[int, int] = (200, 200)) -> str:
        """Create thumbnail of image"""
        try:
            img = Image.open(image_path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            filename = os.path.basename(image_path)
            thumb_filename = f"thumb_{filename}"
            thumb_filepath = self.thumbnails_path / thumb_filename
            
            img.save(str(thumb_filepath), "JPEG", quality=85)
            return str(thumb_filepath)
            
        except Exception as e:
            logger.error(f"Thumbnail creation failed: {str(e)}")
            return image_path
    
    def detect_edges(self, image_path: str) -> np.ndarray:
        """Detect edges in image (for card detection)"""
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(img, (5, 5), 0)
        
        # Canny edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        return edges
    
    def correct_perspective(self, image_path: str, points: np.ndarray) -> str:
        """Correct perspective distortion"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Get dimensions
        height, width = img.shape[:2]
        
        # Define destination points (rectangle)
        dst_points = np.array([
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1]
        ], dtype=np.float32)
        
        # Get perspective transform matrix
        matrix = cv2.getPerspectiveTransform(points.astype(np.float32), dst_points)
        
        # Apply transformation
        corrected = cv2.warpPerspective(img, matrix, (width, height))
        
        # Save corrected image
        filename = os.path.basename(image_path)
        corrected_filename = f"corrected_{filename}"
        corrected_filepath = self.enhanced_path / corrected_filename
        
        cv2.imwrite(str(corrected_filepath), corrected)
        
        return str(corrected_filepath)
    
    def auto_crop(self, image_path: str) -> str:
        """Auto crop image to remove whitespace"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Threshold
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contours[0])
            
            # Crop
            cropped = img[y:y+h, x:x+w]
            
            # Save cropped image
            filename = os.path.basename(image_path)
            cropped_filename = f"cropped_{filename}"
            cropped_filepath = self.enhanced_path / cropped_filename
            
            cv2.imwrite(str(cropped_filepath), cropped)
            
            return str(cropped_filepath)
        
        return image_path

image_service = ImageService()
