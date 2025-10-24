# HuggingFace Spaces Deployment (ARCHIVED)

## Status: ARCHIVED - Pre v1.0
**Note:** This deployment method was used during development but was replaced by Railway before the v1.0 launch. This documentation is kept for historical reference only.

**Current Production:** https://cidadao-api-production.up.railway.app/

---

## Historical Information

### Previous Deployment Details
- **Platform**: HuggingFace Spaces
- **URL**: https://neural-thinker-cidadao-ai-backend.hf.space (NO LONGER ACTIVE)
- **Period**: Development phase (2024-2025)
- **Replaced By**: Railway deployment before v1.0 launch
- **Reason for Migration**: Better scalability, PostgreSQL support, and production features

### HuggingFace Configuration (Historical)

#### Entry Point
The deployment used `src/api/app.py` directly (note: there was never an `app.py` in root).

#### Space Configuration
```yaml
title: Cidadao AI Backend
emoji: 🇧🇷
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 8000
```

#### Limitations Encountered
1. **Database**: Only in-memory SQLite (no PostgreSQL)
2. **Redis**: Not available (memory caching only)
3. **Workers**: No Celery support
4. **Storage**: Ephemeral (resets on restart)
5. **Resources**: Limited to 2 vCPU, 16GB RAM

### Migration to Railway

#### Timeline
- Development started on HuggingFace Spaces
- Issues with scalability and persistence identified
- Railway evaluation completed
- Migration executed before v1.0 release
- Production launched on Railway

#### Improvements with Railway
1. **Full PostgreSQL support**
2. **Redis for caching**
3. **Celery workers for async tasks**
4. **Persistent storage**
5. **Better scalability**
6. **Custom domains**
7. **Environment variables management**
8. **Automatic deployments from GitHub**

### Legacy Commands (No Longer Used)

```bash
# These commands are archived - DO NOT USE
# huggingface-cli login
# git clone https://huggingface.co/spaces/neural-thinker/cidadao.ai-backend
# git push origin main
```

### Lessons Learned

1. **Start with production-ready infrastructure**: Railway provided better production features from the start
2. **Database persistence is critical**: In-memory databases are only suitable for demos
3. **Scalability planning**: Consider resource limits early in development
4. **Migration complexity**: Moving from one platform to another requires careful planning

## Current Production

All production deployments now use Railway:
- **URL**: https://cidadao-api-production.up.railway.app/
- **Documentation**: See main README.md and CLAUDE.md for current deployment instructions

## References

- Current deployment docs: `/docs/deployment/RAILWAY.md`
- Migration notes: Internal team documentation
- Railway configuration: `railway.toml` in project root

---

*This document is maintained for historical reference only. For current deployment information, please refer to the main documentation.*
