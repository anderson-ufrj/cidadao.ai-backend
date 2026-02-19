# Dockerfile for Railway/Render - Cidadão.AI Backend
# Author: Anderson Henrique da Silva
# Multi-stage build for smaller production images

# --- Stage 1: Build dependencies ---
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2: Production image ---
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# Copy pre-built Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY src/ ./src/
COPY *.py ./
COPY alembic.ini ./
COPY alembic/ ./alembic/

# Create necessary directories
RUN mkdir -p logs models data && \
    chown -R app:app /app

# Switch to app user
USER app

# Expose port (Railway sets PORT env var dynamically)
EXPOSE ${PORT:-8000}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run full API application
CMD uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-8000}
