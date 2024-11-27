import pytest
from tests.test_api import create_test_pdf

@pytest.fixture(scope="session")
def test_pdf_path():
    """Create a test PDF file and clean it up after tests"""
    pdf_path = create_test_pdf()
    yield pdf_path
    try:
        import os
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)
    except:
        pass
