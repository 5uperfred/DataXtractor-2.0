import os
import cv2
import numpy as np
import pytesseract
import config

class ExtractionUtils:
    @staticmethod
    def validate_pdf(file_path):
        """Validate PDF file"""
        if not os.path.exists(file_path):
            return False
        if not file_path.lower().endswith('.pdf'):
            return False
        return True

    @staticmethod
    def preprocess_image(image):
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        
        # Apply thresholding to preprocess the image
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Apply dilation to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        gray = cv2.dilate(gray, kernel, iterations=1)
        
        return gray

    @staticmethod
    def extract_text_with_tesseract(image_path, language='eng'):
        """Extract text from image using Tesseract OCR"""
        # Set Tesseract path
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
        
        # Read image
        image = cv2.imread(image_path)
        
        # Preprocess image
        preprocessed = ExtractionUtils.preprocess_image(image)
        
        # Extract text
        text = pytesseract.image_to_string(preprocessed, lang=language)
        return text
