FROM python:3.9-slim-buster

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Use gunicorn for production with 300s timeout (5 mins) and 4 workers
CMD ["gunicorn", "--workers", "4", "--timeout", "300", "--bind", "0.0.0.0:8000", "run:app"]
