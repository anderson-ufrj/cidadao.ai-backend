#!/bin/bash
#
# Apply Pending Migrations to Railway Database
#
# This script connects directly to Railway's PostgreSQL database
# and applies all pending Alembic migrations.
#
# Usage:
#   ./scripts/deployment/apply_migrations_railway.sh
#

set -e

echo "🚀 Applying migrations to Railway database..."
echo ""

# Check if DATABASE_URL is set (should be from Railway)
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL not found"
    echo ""
    echo "To get DATABASE_URL from Railway:"
    echo "  railway variables get DATABASE_URL"
    echo ""
    echo "Then run:"
    echo "  DATABASE_URL='postgresql://...' ./scripts/deployment/apply_migrations_railway.sh"
    exit 1
fi

# Show masked DATABASE_URL for verification
MASKED_URL=$(echo $DATABASE_URL | sed -E 's/(postgresql:\/\/[^:]+:)[^@]+(@.+)/\1****\2/')
echo "📊 Database: $MASKED_URL"
echo ""

# Apply migrations
echo "🔄 Running alembic upgrade head..."
JWT_SECRET_KEY=temp SECRET_KEY=temp venv/bin/alembic upgrade head

echo ""
echo "✅ Migrations applied successfully!"
echo ""

# Show current migration state
echo "📋 Current migration head:"
JWT_SECRET_KEY=temp SECRET_KEY=temp venv/bin/alembic current

echo ""
echo "🎯 Expected: 97f22967055b (head)"
