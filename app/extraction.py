import os
import tempfile
from typing import Tuple, Dict, List, Any
from pdf2image import convert_from_path
import pdfplumber
import cv2
from .utils import ExtractionUtils
from config import settings

class PDFExtractor:
    @classmethod
    def extract_text_standard(cls, pdf_path: str) -> str:
        return ExtractionUtils.extract_pdf_with_plumber(pdf_path)

    @classmethod
    def extract_excel(cls, file_path: str) -> Dict[str, Any]:
        return ExtractionUtils.extract_excel_with_pandas(file_path)

    @classmethod
    def extract_text_ocr(cls, pdf_path: str, language: str = 'eng') -> str:
        extracted_text = ""
        
        # Optimization: Use plumber to get page count fast, don't render images yet
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            
        pages_to_process = min(settings.MAX_PAGES, total_pages)
        
        # Convert only the necessary pages
        images = convert_from_path(pdf_path, first_page=1, last_page=pages_to_process)
        
        for image in images:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                image_path = temp_file.name
                image.save(image_path, "JPEG")
                
                processed_image = ExtractionUtils.preprocess_image(image_path)
                cv2.imwrite(image_path, processed_image)
                
                page_text = ExtractionUtils.extract_text_with_tesseract(
                    image_path, language=language
                )
                extracted_text += page_text + "\n"
                os.unlink(image_path)
        
        return extracted_text

    @classmethod
    def extract_columns(cls, pdf_path: str, left_partition: float = 0.4, right_partition: float = 0.6) -> Tuple[str, str]:
        # Optimization: Get page count efficiently
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)

        pages_to_process = min(settings.MAX_PAGES, total_pages)
        images = convert_from_path(pdf_path, first_page=1, last_page=pages_to_process)
        
        col1_text = ""
        col2_text = ""
        
        for image in images:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                image_path = temp_file.name
                image.save(image_path, "JPEG")
                
                img = cv2.imread(image_path)
                h, w, _ = img.shape
                left_cut = int(w * left_partition)
                right_cut = int(w * right_partition)
                
                # Process left column
                col1_img_path = f"{temp_file.name}_left.jpg"
                cv2.imwrite(col1_img_path, img[:, :left_cut])
                col1_text += ExtractionUtils.extract_text_with_tesseract(col1_img_path) + "\n"
                
                # Process right column
                col2_img_path = f"{temp_file.name}_right.jpg"
                cv2.imwrite(col2_img_path, img[:, left_cut:right_cut])
                col2_text += ExtractionUtils.extract_text_with_tesseract(col2_img_path) + "\n"
                
                # Cleanup
                for p in [image_path, col1_img_path, col2_img_path]:
                    if os.path.exists(p): os.unlink(p)
        
        return col1_text, col2_text
