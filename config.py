"""Application configuration settings"""

# Project info
PROJECT_NAME = "DataXtractor"
VERSION = "2.0"
DESCRIPTION = "PDF Text Extraction API"

# API settings
API_V1_STR = "/api/v1"
HOST = "127.0.0.1"
PORT = 8000
DEBUG = True

# OCR settings
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"c:\Users\fredd\DataXtractor 2.0\poppler\poppler-24.08.0\Library\bin"
SUPPORTED_LANGUAGES = ["eng", "spa"]
MAX_PAGES = 50
