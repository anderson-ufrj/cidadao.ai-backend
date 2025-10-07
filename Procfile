# Procfile for Railway/Render deployment
# Author: Anderson Henrique da Silva
# Date: 2025-10-07 18:30:00
#
# Railway will automatically create separate services from this file

# Main API server
web: uvicorn src.api.app:app --host 0.0.0.0 --port $PORT

# Celery worker for background tasks
worker: celery -A src.infrastructure.queue.celery_app worker --loglevel=info --queues=critical,high,default,low,background --concurrency=4

# Celery beat for scheduled tasks (24/7 auto-investigations)
beat: celery -A src.infrastructure.queue.celery_app beat --loglevel=info

# Optional: Flower for monitoring (uncomment to enable)
# flower: celery -A src.infrastructure.queue.celery_app flower --port=5555
