# Dockerfile for Railway/Render - Cidadão.AI Backend
# Author: Anderson Henrique da Silva
# Date: 2025-10-07 21:35:00
#
# Full API with Celery support for production deployment

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY *.py ./

# Create necessary directories
RUN mkdir -p logs models data && \
    chown -R app:app /app

# Switch to app user
USER app

# Expose port (Railway sets PORT env var dynamically)
EXPOSE ${PORT:-8000}

# Health check - use PORT env var
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run full API application
CMD uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-8000}
