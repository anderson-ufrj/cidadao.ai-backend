# Dockerfile for Hugging Face Spaces
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements-hf.txt ./
RUN pip install --no-cache-dir -r requirements-hf.txt

# Copy application code
COPY app.py ./

# Create necessary directories
RUN mkdir -p logs models data

# Change ownership to app user
RUN chown -R app:app /app

# Switch to app user
USER app

# Expose HF Spaces port
EXPOSE 7860

# Run application
CMD ["python", "app.py"]