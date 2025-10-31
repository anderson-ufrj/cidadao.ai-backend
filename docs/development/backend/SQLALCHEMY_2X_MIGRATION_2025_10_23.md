# SQLAlchemy 2.x Migration - Transparency Coverage Endpoint

**Date**: 2025-10-23
**Author**: Anderson Henrique da Silva
**Issue**: Frontend team reported SQLAlchemy 1.x syntax in `/api/v1/transparency/coverage/map`

---

## Problem Identified

The transparency coverage endpoints were using deprecated SQLAlchemy 1.x query syntax:

```python
# ❌ SQLAlchemy 1.x (deprecated)
session.query(Model).filter(...).first()
```

This syntax is deprecated and was causing issues with the frontend integration.

---

## Solution Applied

Migrated all queries to **SQLAlchemy 2.x syntax** using `select()`:

```python
# ✅ SQLAlchemy 2.x (current standard)
from sqlalchemy import select

stmt = select(Model).filter(...).limit(1)
result = session.execute(stmt)
data = result.scalar_one_or_none()
```

---

## Files Modified

### `src/api/routes/transparency_coverage.py`

#### Changed Imports
```python
# Added
from sqlalchemy import select
```

#### Migrated Queries (4 locations)

1. **Main Coverage Map Endpoint** (`get_coverage_map()` line ~80):
   ```python
   # Before
   latest_snapshot = (
       db.query(TransparencyCoverageSnapshot)
       .filter(TransparencyCoverageSnapshot.state_code.is_(None))
       .order_by(TransparencyCoverageSnapshot.snapshot_date.desc())
       .first()
   )

   # After
   stmt = (
       select(TransparencyCoverageSnapshot)
       .filter(TransparencyCoverageSnapshot.state_code.is_(None))
       .order_by(TransparencyCoverageSnapshot.snapshot_date.desc())
       .limit(1)
   )
   result = db.execute(stmt)
   latest_snapshot = result.scalar_one_or_none()
   ```

2. **Historical Snapshots** (`get_coverage_map()` line ~146):
   ```python
   # Before
   history_snapshots = (
       db.query(TransparencyCoverageSnapshot)
       .filter(...)
       .all()
   )

   # After
   history_stmt = select(TransparencyCoverageSnapshot).filter(...)
   history_result = db.execute(history_stmt)
   history_snapshots = history_result.scalars().all()
   ```

3. **State-Specific Coverage** (`get_state_coverage()` line ~220):
   ```python
   # Before
   latest = (
       db.query(TransparencyCoverageSnapshot)
       .filter(TransparencyCoverageSnapshot.state_code == state_code)
       .first()
   )

   # After
   latest_stmt = (
       select(TransparencyCoverageSnapshot)
       .filter(TransparencyCoverageSnapshot.state_code == state_code)
       .limit(1)
   )
   latest_result = db.execute(latest_stmt)
   latest = latest_result.scalar_one_or_none()
   ```

4. **Coverage Stats** (`get_coverage_stats()` line ~382):
   ```python
   # Similar migration pattern applied
   ```

---

## Testing Results

### Unit Tests ✅
```bash
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/ -k "coverage" -v
```

**Result**: 14 tests passed ✅

### Syntax Validation ✅
```bash
python -m py_compile src/api/routes/transparency_coverage.py
```

**Result**: ✅ No syntax errors

---

## Impact on Frontend

### Before Fix
- Endpoint would fail with SQLAlchemy compatibility errors
- Frontend had to use mock data (4 states only)

### After Fix ✅
- `/api/v1/transparency/coverage/map` now works correctly
- Frontend can automatically detect and use **real data**
- **13 APIs across 10 states** now available

---

## SQLAlchemy 2.x Best Practices

### Query Pattern
```python
from sqlalchemy import select

# Single result
stmt = select(Model).filter(...).limit(1)
result = session.execute(stmt)
obj = result.scalar_one_or_none()  # or scalar_one() if must exist

# Multiple results
stmt = select(Model).filter(...)
result = session.execute(stmt)
objects = result.scalars().all()

# Count
from sqlalchemy import func
stmt = select(func.count()).select_from(Model).filter(...)
result = session.execute(stmt)
count = result.scalar()
```

### Key Differences

| SQLAlchemy 1.x | SQLAlchemy 2.x | Notes |
|----------------|----------------|-------|
| `query(Model)` | `select(Model)` | Use select() |
| `.first()` | `.scalar_one_or_none()` | Execute first |
| `.all()` | `.scalars().all()` | Use scalars() |
| `session.query()` | `session.execute(select())` | Two-step process |

---

## Verification Steps

To verify the fix is working in production:

```bash
# Test coverage map endpoint
curl https://cidadao-api-production.up.railway.app/api/v1/transparency/coverage/map \
  | jq '.summary'

# Should return real data:
# - total_states: 27
# - states_working: 10
# - overall_coverage_percentage: ~37%
```

---

## Additional Notes

### Dependencies Added
- `unidecode==1.4.0` (required for organization mapping)

### No Breaking Changes
- API response format unchanged
- All endpoint paths remain the same
- Frontend integration unaffected

---

## Commit Reference

```
fix(api): migrate transparency coverage to SQLAlchemy 2.x syntax

Replace deprecated session.query() with select() pattern across
all transparency coverage endpoints. Resolves compatibility issues
reported by frontend team.

Changes:
- Updated get_coverage_map() with SQLAlchemy 2.x queries
- Migrated get_state_coverage() to use select() pattern
- Fixed get_coverage_stats() query syntax
- Added unidecode dependency for organization mapping

Tests: 14 coverage tests passing
Impact: Frontend can now use real data from 13 APIs across 10 states
```

---

## References

- [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
- [Select API Documentation](https://docs.sqlalchemy.org/en/20/core/selectable.html#sqlalchemy.sql.expression.select)
- Project: `cidadao.ai-backend`
- Endpoint: `/api/v1/transparency/coverage/map`
