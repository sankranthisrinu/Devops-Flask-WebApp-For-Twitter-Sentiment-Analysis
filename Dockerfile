# Containerize the Flask Sentiment Analysis application
# Base image - using Python 3.9 slim as it's lighter than the full image
FROM python:3.9-slim as base

# Set environment variables
# Prevents Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Keeps Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy NLTK data for TextBlob
RUN python -m textblob.download_corpora

# Copy application code
COPY . .

# Create directory for static images if it doesn't exist
RUN mkdir -p static/images

# Make port 5000 available outside the container
EXPOSE 5000

# Set the command to run the application
CMD ["python", "app.py"]