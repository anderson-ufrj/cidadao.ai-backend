# Transparency Coverage Map - Deployment Status

**Date**: 2025-10-23
**Status**: ⚠️ Requires Manual Migration in Railway
**Endpoint**: `/api/v1/transparency/coverage/map`

---

## 🎯 Current Situation

### ✅ Fixed Issues
1. **SQLAlchemy 1.x → 2.x Migration**: COMPLETE
   - Migrated from deprecated `session.query()` to modern `select()` pattern
   - Fixed AsyncSession usage with proper `await` statements
   - All code changes deployed successfully

2. **Code Quality**: COMPLETE
   - 14 tests passing
   - Linting and formatting OK
   - 3 commits pushed to main branch

### ⚠️ Pending Issue
**Database Migration Not Applied in Railway**

The transparency coverage table (`transparency_coverage_snapshots`) exists in code and migrations, but Railway hasn't applied the migration yet.

---

## 📊 Migration Status

### Railway Current State
```
✅ 002_entity_graph
✅ 003_performance_indexes
❌ 004_investigation_metadata (pending)
❌ 005... (pending)
❌ ... (pending)
❌ 97f22967055b - transparency_coverage_snapshots (pending) ← TARGET
```

### Error in Production
```
relation "transparency_coverage_snapshots" does not exist
```

---

## 🔧 Solutions

### Option 1: Wait for Automatic Migration (Recommended)
Railway should automatically apply pending migrations on next deploy. The startup logs show Alembic runs:

```bash
INFO [alembic.runtime.migration] Running upgrade ...
```

**Action**: Force a redeploy in Railway dashboard:
1. Go to Railway project
2. Click "Deploy" → "Redeploy"
3. Watch logs for migration application
4. Verify all migrations apply to head `97f22967055b`

### Option 2: Manual Migration via Railway CLI
If automatic migration doesn't work, apply manually:

```bash
# Connect to Railway
railway link

# Run migration script
railway run python scripts/deployment/apply_pending_migrations.py

# Or run Alembic directly
railway run venv/bin/alembic upgrade head

# Verify
railway run venv/bin/alembic current
# Should show: 97f22967055b (head)
```

### Option 3: Railway Console
Use Railway's web console:

1. Open Railway project
2. Go to "Deployments" → Click running deployment
3. Click "Console" tab
4. Run: `alembic upgrade head`

---

## 📋 Migration File Details

**File**: `alembic/versions/20251023_1247_add_transparency_coverage_snapshots_.py`
**Revision**: `97f22967055b`
**Down Revision**: `77f2e2dbf0ba`

**Creates**:
- Table: `transparency_coverage_snapshots`
- Columns:
  - `id` (Integer, PK)
  - `snapshot_date` (DateTime)
  - `coverage_data` (JSON)
  - `summary_stats` (JSON)
  - `state_code` (String)
  - `state_status` (String)
  - `coverage_percentage` (Float)

**Indexes**:
- `idx_snapshot_date_desc` (for latest queries)
- `idx_state_coverage` (for state queries)
- `idx_state_date` (for historical queries)

---

## 🧪 Testing After Migration

Once the migration is applied, test the endpoint:

```bash
# Test main endpoint
curl https://cidadao-api-production.up.railway.app/api/v1/transparency/coverage/map \
  | jq '.summary'

# Expected response (first call - cold start ~30s):
{
  "total_states": 27,
  "states_with_apis": 10,
  "states_working": 10,
  "overall_coverage_percentage": 37.0,
  "total_apis": 13
}

# Test stats endpoint (fast)
curl https://cidadao-api-production.up.railway.app/api/v1/transparency/coverage/stats

# Test state-specific (example: São Paulo)
curl https://cidadao-api-production.up.railway.app/api/v1/transparency/coverage/state/SP
```

---

## 🎯 Expected Behavior After Fix

### First Request (Cold Start)
- **Duration**: 30-60 seconds
- **Action**: Generates coverage snapshot on-demand
- **Saves**: Snapshot to database for caching

### Subsequent Requests
- **Duration**: <100ms (cached)
- **Data**: Returns cached snapshot
- **Update**: Background job updates every 6 hours (Celery Beat)

---

## 📚 Related Documentation

- **Migration Guide**: `docs/technical/SQLALCHEMY_2X_MIGRATION_2025_10_23.md`
- **Coverage Tasks**: `src/infrastructure/queue/tasks/coverage_tasks.py`
- **Health Monitor**: `src/services/transparency_apis/health_check.py`
- **Model**: `src/models/transparency_coverage.py`

---

## 🔍 Troubleshooting

### Check Migration Status
```bash
railway run venv/bin/alembic current
railway run venv/bin/alembic heads
```

### View Migration History
```bash
railway run venv/bin/alembic history
```

### Check Database Tables
```bash
railway run python -c "
from src.db.session import get_engine
from sqlalchemy import inspect
engine = get_engine()
inspector = inspect(engine)
tables = inspector.get_table_names()
print('transparency_coverage_snapshots' in tables)
"
```

---

## ✅ Success Criteria

Migration is successful when:

1. **Alembic Head**: `97f22967055b`
2. **Table Exists**: `transparency_coverage_snapshots` in database
3. **Endpoint Works**: `/api/v1/transparency/coverage/map` returns 200
4. **No Errors**: No "relation does not exist" errors in logs

---

## 📝 Next Steps for Frontend

**After migration is applied**:

1. **Remove mock data** from transparency map component
2. **Update API calls** to use real endpoint
3. **Test coverage visualization** with 10 states
4. **Implement automatic refresh** (poll every 6 hours)
5. **Add loading states** for cold start (first 30-60s)

**Frontend Integration Guide**: `docs/FRONTEND-BACKEND-INTEGRATION-STATUS.md`

---

## 🤝 Support

If migrations still don't apply after these steps:

1. Check Railway environment variables (DATABASE_URL present?)
2. Review Railway logs for migration errors
3. Contact backend team with specific error messages
4. Consider manual SQL execution as last resort

---

**Status**: Ready for deployment once migrations are applied
**Backend Code**: ✅ Complete and tested
**Database Schema**: ⏳ Waiting for Railway migration
**Frontend Integration**: 🚀 Ready to implement
