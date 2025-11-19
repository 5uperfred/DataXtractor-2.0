import os
import pytesseract
import numpy as np
import cv2
import pdfplumber
import pandas as pd
from typing import List, Dict, Union

class ExtractionUtils:
    @staticmethod
    def validate_pdf(file_path: str) -> bool:
        try:
            with pdfplumber.open(file_path) as pdf:
                return len(pdf.pages) > 0
        except Exception:
            return False

    @staticmethod
    def validate_excel(file_path: str) -> bool:
        """Validate Excel file integrity"""
        try:
            pd.read_excel(file_path, nrows=1)
            return True
        except Exception:
            return False

    @staticmethod
    def preprocess_image(image_path: str) -> np.ndarray:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        return cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

    @staticmethod
    def extract_text_with_tesseract(image_path: str, language: str = 'eng', custom_config: str = '') -> str:
        default_config = '--oem 3 --psm 6 '
        config = default_config + custom_config
        text = pytesseract.image_to_string(image_path, lang=language, config=config)
        return text.strip()

    @staticmethod
    def extract_pdf_with_plumber(file_path: str) -> str:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        return text

    @staticmethod
    def extract_excel_with_pandas(file_path: str) -> Dict[str, List[Dict]]:
        """Extracts all sheets from Excel as a dictionary of records"""
        xls = pd.ExcelFile(file_path)
        output = {}
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            # Clean NaN values to make it JSON serializable
            df = df.fillna("")
            output[sheet_name] = df.to_dict(orient='records')
        return output
