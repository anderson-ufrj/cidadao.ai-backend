#!/bin/bash
set -e

# Docker entrypoint script for Cidadão.AI

echo "🚀 Starting Cidadão.AI..."

# Wait for database
echo "⏳ Waiting for database..."
while ! nc -z ${POSTGRES_HOST:-postgres} ${POSTGRES_PORT:-5432}; do
  sleep 1
done
echo "✅ Database is ready!"

# Wait for Redis
echo "⏳ Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-redis-node-1} ${REDIS_PORT:-7000}; do
  sleep 1
done
echo "✅ Redis is ready!"

# Run database migrations if needed
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "🔄 Running database migrations..."
    python -m src.core.database.migrations
fi

# Initialize system components
if [ "$INITIALIZE_SYSTEM" = "true" ]; then
    echo "🔧 Initializing system components..."
    python -c "
import asyncio
from src.infrastructure.orchestrator import initialize_system
asyncio.run(initialize_system())
"
fi

# Execute the main command
echo "▶️ Starting application: $@"
exec "$@"