#!/bin/bash
# Railway Start Script with Migrations
# Author: Anderson Henrique da Silva
# Date: 2025-10-13
#
# This script ensures database migrations run before starting the server

set -e  # Exit on error

echo "🔄 Running database migrations..."
python -m alembic upgrade head

echo "✅ Migrations completed successfully"
echo "🚀 Starting Uvicorn server..."

# Start the server
exec uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-8080}
