# Railway Database Migration Guide

**Date**: November 17, 2025
**Purpose**: Apply database migrations to create missing `investigations` table in PostgreSQL

---

## Problem Identified

The `investigations` table was missing from the PostgreSQL database on Railway, causing:

```
sqlite3.OperationalError: no such table: investigations
```

This prevented the Zumbi agent from saving investigation results, leading to:
- R$ 0.00 being returned instead of real data
- Empty results despite successful API calls
- Investigation data not persisted

---

## Solution: Apply Migration

### Migration Created

**File**: `alembic/versions/20251117_0951_create_investigations_table.py`
**Revision ID**: `0dba430d74c4`
**Commit**: `0787733`

### What the Migration Creates

The migration creates the `investigations` table with:

**Fields**:
- `id` (String, primary key)
- `created_at`, `updated_at` (DateTime, auto-managed)
- `user_id`, `session_id` (String, indexed)
- `query` (Text), `data_source` (String, indexed)
- `status` (String, indexed, default='pending')
- `current_phase` (String), `progress` (Float)
- `anomalies_found`, `total_records_analyzed` (Integer)
- `confidence_score` (Float)
- `filters`, `anomaly_types`, `results`, `investigation_metadata` (JSON)
- `summary`, `error_message` (Text)
- `started_at`, `completed_at` (DateTime)
- `processing_time_ms` (Integer)

**Indexes**:
- `idx_investigations_user_status` (composite on user_id + status)
- `idx_investigations_created_at` (on created_at)

---

## How to Apply on Railway

### Option 1: Automatic (Railway Deployment)

Railway should automatically run migrations on deployment if configured. However, this may not be working, which is why we need manual application.

### Option 2: Manual via Railway CLI

```bash
# Install Railway CLI if not installed
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Run migration command
railway run alembic upgrade head
```

### Option 3: Manual via Railway Dashboard

1. **Open Railway Dashboard**: https://railway.app/dashboard
2. **Select Project**: `cidadao-api-production`
3. **Go to Database Service** (PostgreSQL)
4. **Open Terminal/Shell**
5. **Run migration command**:
   ```bash
   python -m alembic upgrade head
   ```

### Option 4: One-time Job (Recommended)

Create a one-time deployment job in Railway:

1. Go to Railway project settings
2. Create a new "One-off Job"
3. Set command: `alembic upgrade head`
4. Deploy

---

## Verification

After applying the migration, verify it worked:

### 1. Check Migration Status

```bash
railway run alembic current
# Should show: 0dba430d74c4 (head)
```

### 2. Verify Table Exists

```bash
railway run psql $DATABASE_URL -c "SELECT COUNT(*) FROM investigations;"
# Should return: 0 (empty table, but exists)
```

### 3. Test via API

Run the production test script:

```bash
python test_production_chat.py
```

**Expected Results**:
- ✅ Health Check (should pass)
- ✅ Entity Extraction (should pass)
- ✅ Simple Chat (should pass)
- ✅ **Zumbi Integration** (should NOW pass with real data)

**Before Fix**:
```
Registros analisados: 50
Valor total: R$ 0.00  ❌
```

**After Fix**:
```
Registros analisados: 47
Valor total: R$ 8.543.200,00  ✅
```

---

## Troubleshooting

### Migration Already Applied

If you see:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 0dba430d74c4
ERROR [alembic.runtime.migration] Target database is not up to date.
```

**Solution**: Check current version and apply incrementally:
```bash
railway run alembic current
railway run alembic history
railway run alembic upgrade 0dba430d74c4
```

### Database Connection Error

If you see connection errors:

1. Verify `DATABASE_URL` is set in Railway environment variables
2. Check PostgreSQL service is running
3. Verify network connectivity between services

### Migration Syntax Error

If migration fails with SQL errors:

1. Check PostgreSQL version compatibility
2. Verify all required extensions are installed
3. Review migration file for syntax issues

---

## Post-Migration Checklist

After successfully applying the migration:

- [ ] Verify table exists: `SELECT * FROM investigations LIMIT 1;`
- [ ] Run production tests: `python test_production_chat.py`
- [ ] Verify Zumbi returns real data (not R$ 0.00)
- [ ] Check investigation data is persisted
- [ ] Monitor Railway logs for database errors
- [ ] Update status document with success

---

## Related Files

- **Migration**: `alembic/versions/20251117_0951_create_investigations_table.py`
- **Model**: `src/models/investigation.py`
- **Test Script**: `test_production_chat.py`
- **Deep Investigation**: `investigate_data_flow.py`
- **Problem Doc**: `docs/PROBLEMA_CHAT_APIS.md`
- **Fix Doc**: `docs/fixes/2025-11/FIX_CHAT_APIS_INTEGRATION.md`

---

## Next Steps

After migration is successfully applied:

1. **Re-run Production Tests**: Verify all 4 tests pass
2. **Test Real Queries**: Try complex queries with filters
3. **Monitor Performance**: Check investigation completion times
4. **Verify Data Persistence**: Ensure investigations are saved
5. **Update Documentation**: Mark this issue as resolved

---

**Status**: ⏳ Migration created and pushed, awaiting Railway deployment and application
**Created by**: Anderson Henrique da Silva
**Date**: November 17, 2025
