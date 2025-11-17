#!/bin/bash
# Railway Migration Application Script
# Applies pending Alembic migrations to Railway PostgreSQL database

set -e

echo "=================================="
echo "Railway Migration Application"
echo "=================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found"
    echo ""
    echo "Install it with:"
    echo "  npm install -g @railway/cli"
    echo ""
    exit 1
fi

echo "✅ Railway CLI found"
echo ""

# Check if project is linked
if ! railway status &> /dev/null; then
    echo "❌ Not linked to a Railway project"
    echo ""
    echo "Link your project with:"
    echo "  railway link"
    echo ""
    exit 1
fi

echo "✅ Project linked"
echo ""

# Show current migration status
echo "📋 Current migration status:"
echo ""
railway run alembic current
echo ""

# Show pending migrations
echo "📋 Migration history:"
echo ""
railway run alembic history | head -10
echo ""

# Ask for confirmation
read -p "Apply pending migrations? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Migration cancelled"
    exit 0
fi

echo ""
echo "🚀 Applying migrations..."
echo ""

# Apply migrations
railway run alembic upgrade head

echo ""
echo "✅ Migrations applied successfully!"
echo ""

# Verify
echo "📋 New migration status:"
echo ""
railway run alembic current
echo ""

# Check if investigations table exists
echo "🔍 Verifying investigations table..."
echo ""
railway run python -c "
from src.infrastructure.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
if 'investigations' in tables:
    print('✅ investigations table exists')
    print('')
    # Get column count
    columns = inspector.get_columns('investigations')
    print(f'   Columns: {len(columns)}')
    print('   Fields:', ', '.join([c['name'] for c in columns[:5]]), '...')
else:
    print('❌ investigations table NOT found')
    print('   Available tables:', ', '.join(tables))
" 2>/dev/null || echo "⚠️  Could not verify (run this locally to test)"

echo ""
echo "=================================="
echo "Migration Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Run: python test_production_chat.py"
echo "2. Verify Zumbi returns real data (not R\$ 0.00)"
echo "3. Check Railway logs for any errors"
echo ""
