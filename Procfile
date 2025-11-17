# Procfile for Railway/Render deployment
# Author: Anderson Henrique da Silva
# Date: 2025-10-07 18:30:00
#
# Railway will automatically create separate services from this file

# Run database migrations before deploying
# DISABLED: Railway release phase runs BEFORE runtime network is available
# Migrations now run during app startup (see src/api/app.py lifespan function)
# release: python -m alembic upgrade head

# Main API server
# PYTHONDONTWRITEBYTECODE=1 prevents .pyc caching issues
web: PYTHONDONTWRITEBYTECODE=1 uvicorn src.api.app:app --host 0.0.0.0 --port $PORT --reload

# Celery worker for background tasks
worker: celery -A src.infrastructure.queue.celery_app worker --loglevel=info --queues=critical,high,default,low,background --concurrency=4

# Celery beat for scheduled tasks (24/7 auto-investigations)
beat: celery -A src.infrastructure.queue.celery_app beat --loglevel=info

# Optional: Flower for monitoring (uncomment to enable)
# flower: celery -A src.infrastructure.queue.celery_app flower --port=5555
