# DataXtractor API

DataXtractor is a powerful OCR and text extraction API that supports multiple languages and advanced extraction features.

## Features

- PDF text extraction (standard and OCR-based)
- Multi-language support
- Column-based text extraction
- Image preprocessing for better OCR accuracy
- Support for multiple file formats

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR:
- Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr`
- Mac: `brew install tesseract`

3. Set environment variables:
```bash
export TESSERACT_PATH=/path/to/tesseract  # Adjust based on your installation
```

## Running the API

```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /api/v1/extract/standard`: Standard PDF text extraction
- `POST /api/v1/extract/ocr`: OCR-based text extraction
- `POST /api/v1/extract/columns`: Column-based text extraction

## Deployment

The API is configured for deployment on DigitalOcean using Docker. See deployment instructions in the documentation.

## License

MIT License
