# 📦 Archive - Cidadão.AI Backend Documentation

**Purpose**: Historical documentation and deprecated deployment guides
**Last Updated**: 2025-10-24

---

## 📂 Archive Structure

### 1. `2025-01-historical/`
Historical documentation from January 2025 and earlier.

**Contents**:
- Agent status reports (historical)
- Test coverage analysis (historical)
- Old architecture documentation
- See `2025-01-historical/ARCHIVE_INDEX.md` for complete index

**Date Range**: Up to January 2025

---

### 2. `2025-10-deployment/`
Deployment documentation archived in October 2025 after migration to Railway.

#### `2025-10-deployment/huggingface/`
**Deprecated**: HuggingFace Spaces deployment (replaced by Railway on 07/10/2025)

**Files**:
- `HUGGINGFACE_DEPLOYMENT.md` - Complete HuggingFace deployment guide
- `HUGGINGFACE_DEPLOYMENT_ARCHIVED.md` - Shortened archived version

**Status**: ❌ No longer in use
**Replacement**: Railway deployment (see `docs/deployment/railway/`)
**Archive Date**: 2025-10-24

#### `2025-10-deployment/railway/`
**Historical**: Railway deployment troubleshooting and fixes (October 2025)

**Files**:
- `COMO_VER_LOGS_RAILWAY.md` - How to view Railway logs
- `RAILWAY_CONFIGURAR_VARIAVEIS_DASHBOARD.md` - Configure variables in dashboard
- `RAILWAY_DATABASE_URL_FIX.md` - Database URL configuration fix
- `RAILWAY_DEPLOYMENT_FIX_2025-10-16.md` - Deployment fixes (Oct 16)
- `RAILWAY_NEXT_STEPS.md` - Next steps after deployment
- `RAILWAY_POSTGRESQL_SETUP.md` - PostgreSQL setup guide

**Status**: ✅ Resolved, kept for reference
**Current Documentation**: `docs/deployment/railway/` (updated guides)
**Archive Date**: 2025-10-24

---

## 🔍 How to Use This Archive

### Finding Historical Information

**Looking for old deployment docs?**
→ Check `2025-10-deployment/`

**Need historical project status?**
→ Check `2025-01-historical/project/`

**Want to see how agents evolved?**
→ Compare `2025-01-historical/` with current `docs/agents/`

**Researching Railway migration?**
→ See `2025-10-deployment/railway/` for migration fixes

---

## ⚠️ Important Notes

1. **Do NOT use archived docs for current development**
   - These documents are historical references only
   - Always use current documentation in main `docs/` folders

2. **HuggingFace deployment is NO LONGER ACTIVE**
   - Production moved to Railway on 07/10/2025
   - HuggingFace guides are for historical reference only

3. **Railway deployment issues are RESOLVED**
   - Current guides in `docs/deployment/railway/` are up-to-date
   - Archived railway docs show historical troubleshooting

4. **Archive organization**
   - Files organized by date and topic
   - Each subdirectory has its own context

---

## 📅 Archive Timeline

| Date | Event | Location |
|------|-------|----------|
| Up to 2025-01 | Historical documentation | `2025-01-historical/` |
| 2025-10-07 | Migration HuggingFace → Railway | Production change |
| 2025-10-16 | Railway deployment fixes | `2025-10-deployment/railway/` |
| 2025-10-24 | Archive consolidation | This structure created |

---

## 🗂️ Maintenance Policy

**When to Archive**:
- Documentation replaced by newer versions
- Deployment platforms no longer in use
- Troubleshooting guides for resolved issues
- Historical status reports superseded by current analysis

**Archive Frequency**: As needed when docs become outdated

**Retention Policy**: Indefinite (historical reference)

---

## 📞 Questions?

If you need information not found in current documentation:

1. **Check this archive** for historical context
2. **Consult main docs** for current information
3. **See** `docs/COMPREHENSIVE_REPOSITORY_ANALYSIS_2025_10_24.md` for latest analysis

---

**Archive Curator**: Anderson Henrique da Silva
**Contact**: andersonhs27@gmail.com
**Last Reorganization**: 2025-10-24
