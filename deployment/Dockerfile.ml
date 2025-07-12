# Multi-stage Dockerfile for ML Training Service
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies including CUDA support
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy requirements
COPY deployment/requirements-prod.txt ./

# Install Python dependencies with ML extras
RUN pip install --no-cache-dir -r requirements-prod.txt && \
    pip install --no-cache-dir \
    mlflow>=2.8.0 \
    wandb>=0.16.0 \
    jupyter>=1.0.0 \
    matplotlib>=3.7.0 \
    seaborn>=0.12.0 \
    plotly>=5.17.0

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY deployment/docker-entrypoint.sh ./
COPY deployment/requirements-prod.txt ./

# Create necessary directories
RUN mkdir -p logs models data experiments

# Change ownership to app user
RUN chown -R app:app /app

# Switch to app user
USER app

# Health check
HEALTHCHECK --interval=60s --timeout=15s --start-period=30s --retries=3 \
    CMD python -c "from src.ml.advanced_pipeline import get_ml_pipeline_manager; import asyncio; asyncio.run(get_ml_pipeline_manager())" || exit 1

# Expose MLflow port
EXPOSE 5000

# Run ML training service
CMD ["./docker-entrypoint.sh", "python", "-m", "src.ml.advanced_pipeline"]