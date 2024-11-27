import os
import tempfile
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from .utils import ExtractionUtils
import config
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import cv2
import numpy as np
from PIL import Image
import markdown
import re

class PDFExtractor:
    @staticmethod
    @lru_cache(maxsize=100)
    def _process_page(page):
        """Process a single page with caching"""
        return page.extract_text() or ""

    @staticmethod
    def _preprocess_image(image):
        """Enhance image quality for better OCR"""
        # Convert PIL Image to OpenCV format
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Apply image preprocessing
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray)
        thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        return Image.fromarray(thresh)

    @staticmethod
    def _format_to_markdown(text, title="Extracted Text"):
        """Convert extracted text to markdown format"""
        # Clean and format the text
        text = text.strip()
        paragraphs = text.split('\n\n')
        
        md_parts = [f"# {title}\n\n"]
        
        for i, para in enumerate(paragraphs):
            if not para.strip():
                continue
            
            # Detect if paragraph looks like a header
            if len(para) < 100 and para.strip().endswith(':'):
                md_parts.append(f"## {para}\n\n")
            else:
                md_parts.append(f"{para}\n\n")
        
        return ''.join(md_parts)

    @staticmethod
    def extract_text_standard(file_path):
        """Extract text from PDF using standard method with parallel processing"""
        try:
            with pdfplumber.open(file_path) as pdf:
                pages = pdf.pages[:config.MAX_PAGES]
                
                # Process pages in parallel
                with ThreadPoolExecutor() as executor:
                    future_to_page = {executor.submit(PDFExtractor._process_page, page): i 
                                    for i, page in enumerate(pages)}
                    
                    text_parts = [""] * len(pages)
                    for future in as_completed(future_to_page):
                        page_num = future_to_page[future]
                        text_parts[page_num] = future.result()
                
                text = "\n".join(text_parts)
                
                return {
                    "success": True,
                    "text": PDFExtractor._format_to_markdown(text),
                    "pages": len(pages),
                    "format": "markdown"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"```\nError: {str(e)}\n```"
            }

    @staticmethod
    def extract_text_ocr(file_path, language='eng'):
        """Extract text from PDF using OCR with enhanced preprocessing"""
        try:
            pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
            
            # Convert PDF to images with optimal settings
            images = convert_from_path(
                file_path,
                poppler_path=config.POPPLER_PATH,
                dpi=300,
                thread_count=os.cpu_count()
            )[:config.MAX_PAGES]
            
            def process_image(image):
                # Preprocess image for better OCR accuracy
                processed_image = PDFExtractor._preprocess_image(image)
                # Configure OCR for better accuracy
                custom_config = r'--oem 3 --psm 6'
                return pytesseract.image_to_string(
                    processed_image, 
                    lang=language,
                    config=custom_config
                )
            
            # Process images in parallel
            with ThreadPoolExecutor() as executor:
                text_parts = list(executor.map(process_image, images))
            
            text = "\n".join(text_parts)
            
            return {
                "success": True,
                "text": PDFExtractor._format_to_markdown(text),
                "pages": len(images),
                "format": "markdown"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"```\nError: {str(e)}\n```"
            }

    @staticmethod
    def extract_columns(file_path, left_partition=0.4, right_partition=0.6, lang_first='eng', lang_second='eng'):
        """Extract text from PDF columns using OCR with parallel processing"""
        try:
            pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
            
            images = convert_from_path(
                file_path,
                poppler_path=config.POPPLER_PATH,
                dpi=300,
                thread_count=os.cpu_count()
            )[:config.MAX_PAGES]
            
            def process_page_columns(image):
                height = image.height
                width = image.width
                
                # Extract and process left column
                left = image.crop((0, 0, int(width * left_partition), height))
                left = PDFExtractor._preprocess_image(left)
                left_text = pytesseract.image_to_string(left, lang=lang_first)
                
                # Extract and process right column
                right = image.crop((int(width * right_partition), 0, width, height))
                right = PDFExtractor._preprocess_image(right)
                right_text = pytesseract.image_to_string(right, lang=lang_second)
                
                return left_text, right_text
            
            # Process columns in parallel
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(process_page_columns, images))
            
            left_texts, right_texts = zip(*results)
            
            return {
                "success": True,
                "left_text": PDFExtractor._format_to_markdown('\n'.join(left_texts), "Left Column"),
                "right_text": PDFExtractor._format_to_markdown('\n'.join(right_texts), "Right Column"),
                "pages": len(images),
                "format": "markdown"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"```\nError: {str(e)}\n```"
            }
