import os
import sys
import tempfile
import requests
from fpdf import FPDF
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from tests import test_config as config

# Create the tests directory if it doesn't exist
Path("tests").mkdir(exist_ok=True)

def create_test_pdf():
    """Create a test PDF with English and Spanish text"""
    pdf = FPDF()
    pdf.add_page()
    
    # Add English text
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Hello, this is a test document.", ln=True, align='L')
    pdf.cell(200, 10, txt="It contains both English and Spanish text.", ln=True, align='L')
    
    # Add Spanish text
    pdf.cell(200, 10, txt="Hola, este es un documento de prueba.", ln=True, align='L')
    pdf.cell(200, 10, txt="Contiene texto en inglés y español.", ln=True, align='L')
    
    # Save to temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
    os.close(temp_fd)
    pdf.output(temp_path)
    return temp_path

def test_standard_extraction(test_pdf_path):
    """Test standard text extraction endpoint"""
    print("\n=== Standard Extraction Test ===")
    url = f"http://{config.HOST}:{config.PORT}{config.API_V1_STR}/extract"
    
    with open(test_pdf_path, 'rb') as f:
        files = {'file': ('test.pdf', f, 'application/pdf')}
        response = requests.post(url, files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_ocr_extraction(test_pdf_path):
    """Test OCR-based text extraction endpoint"""
    print("\n=== OCR Extraction Test ===")
    url = f"http://{config.HOST}:{config.PORT}{config.API_V1_STR}/extract/ocr"
    
    with open(test_pdf_path, 'rb') as f:
        files = {'file': ('test.pdf', f, 'application/pdf')}
        data = {'language': 'eng'}
        response = requests.post(url, files=files, data=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_column_extraction(test_pdf_path):
    """Test column-based text extraction endpoint"""
    print("\n=== Column Extraction Test ===")
    url = f"http://{config.HOST}:{config.PORT}{config.API_V1_STR}/extract/columns"
    
    with open(test_pdf_path, 'rb') as f:
        files = {'file': ('test.pdf', f, 'application/pdf')}
        data = {
            'left_partition': '0.4',
            'right_partition': '0.6',
            'lang_first': 'eng',
            'lang_second': 'spa'
        }
        response = requests.post(url, files=files, data=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def main():
    print("Testing DataXtractor API...")
    
    # Create test PDF
    test_pdf_path = create_test_pdf()
    
    try:
        # Run tests
        test_standard_extraction(test_pdf_path)
        test_ocr_extraction(test_pdf_path)
        test_column_extraction(test_pdf_path)
        
    finally:
        # Clean up test PDF
        if test_pdf_path and os.path.exists(test_pdf_path):
            try:
                os.unlink(test_pdf_path)
            except:
                pass

if __name__ == "__main__":
    main()
