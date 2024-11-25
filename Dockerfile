FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV TESSERACT_PATH=/usr/bin/tesseract

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "run:app"]
