# HuggingFace Deployment (DEPRECATED)

**Status**: ❌ No longer in use as of October 2025
**Replacement**: Railway (https://cidadao-api-production.up.railway.app)
**Date Deprecated**: 2025-10-07

---

## Historical Context

The Cidadão.AI backend was initially deployed on HuggingFace Spaces during early development phases. This deployment method served well for:
- Initial prototyping and testing
- Public API exposure without complex setup
- Zero-cost hosting during development

## Why We Migrated

**Migration to Railway completed on October 7, 2025** for the following reasons:

### Technical Limitations
1. **Limited Persistence**: HuggingFace Spaces had limited database options
2. **Resource Constraints**: Insufficient CPU/memory for multi-agent system
3. **Cold Starts**: Frequent container restarts affected availability
4. **No Built-in Redis**: Required separate hosting for cache layer

### Production Requirements
1. **PostgreSQL Integration**: Native database support on Railway
2. **Redis Availability**: Built-in Redis for caching
3. **24/7 Uptime**: Railway provides 99.9% SLA
4. **Celery Workers**: Background task processing support
5. **Environment Variables**: Secure secrets management

## Current Production Setup

**Platform**: Railway
**URL**: https://cidadao-api-production.up.railway.app
**Infrastructure**:
- PostgreSQL database
- Redis cache
- Celery workers for background tasks
- Celery Beat for scheduled jobs

**See**:
- `docs/deployment/railway.md` - Current deployment guide
- `docs/deployment/DEPLOYMENT_GUIDE.md` - General deployment overview

## Historical Deployment Files

Archived documentation available at:
- `docs/archive/2025-10-deployment/huggingface/` - Original deployment docs
- `docs/troubleshooting/FIX_HUGGINGFACE_DEPLOYMENT.md` - Historical troubleshooting

## For Reference Only

The following information is preserved for historical reference:

### Old HuggingFace URLs
- API: ~~https://neural-thinker-cidadao-ai-backend.hf.space~~ (no longer active)
- Docs: ~~https://neural-thinker-cidadao-ai-backend.hf.space/docs~~ (no longer active)

### Entry Point
HuggingFace deployments used a simplified `app.py` in root directory with:
- Limited agent support
- No database persistence
- In-memory caching only

## Migration Notes

If you need to reference the old deployment:
1. All functionality is available on Railway
2. API endpoints remain the same (just different domain)
3. Authentication and API keys work identically
4. No breaking changes to client integrations

---

**Last Updated**: 2025-10-24
**Maintained By**: DevOps Team
**Questions**: See Railway deployment documentation or contact team
