# Railway Deployment Guide - Cidadão.AI Backend

**Author**: Anderson Henrique da Silva
**Date**: 2025-10-13
**Status**: Production Deployment Analysis

## Overview

This guide documents the Railway deployment process, common issues, and solutions for the Cidadão.AI backend application.

---

## Table of Contents

1. [Railway CLI Setup](#railway-cli-setup)
2. [Project Configuration](#project-configuration)
3. [Deployment Analysis](#deployment-analysis)
4. [Common Issues & Solutions](#common-issues--solutions)
5. [Environment Variables](#environment-variables)
6. [Health Check Configuration](#health-check-configuration)

---

## Railway CLI Setup

### Installation

Railway CLI is already installed and configured with project token authentication.

### Authentication

The project uses a **Project Token** for authentication, configured in `~/.bashrc`:

```bash
# Railway CLI - Project Token (cidadao.ai)
export RAILWAY_TOKEN=d2d7c6a7-e999-4d3e-b11d-67b76e4e5678
```

### Essential Commands

#### Project Information
```bash
# Check project status
railway status

# Open Railway dashboard in browser
railway open

# Check current authentication
railway whoami
```

#### Deployment
```bash
# Deploy local code
railway up

# Redeploy last version
railway redeploy

# Remove last deployment
railway down
```

#### Logs & Monitoring
```bash
# View logs (requires service selection)
railway logs --tail 100

# View logs from specific service
railway logs --environment production --service <service-name>

# Follow logs in real-time
railway logs --tail 100 --follow
```

#### Variables & Configuration
```bash
# View environment variables
railway variables

# Run command with Railway environment
railway run <command>

# Open shell with Railway environment
railway shell
```

#### Service Management
```bash
# Select service (interactive)
railway service

# Add new service
railway add
```

#### Domain Management
```bash
# Manage domains
railway domain
```

### Important Notes

- Some commands require explicit service specification when using Project Token:
  ```bash
  railway <command> --service <service-name>
  ```
- The Project Token provides limited access compared to user authentication
- Always check service name before running service-specific commands

---

## Project Configuration

### railway.json

The project is configured to use Nixpacks builder with custom startup script:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "bash start.sh",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Configuration Details:**
- **Builder**: Nixpacks (automatic Python environment detection)
- **Start Command**: `bash start.sh` (includes database migrations)
- **Restart Policy**: Restart on failure, max 10 retries
- **Port**: Detected from `$PORT` environment variable (default 8080)

### start.sh

The startup script handles database migrations before starting the server:

```bash
#!/bin/bash
set -e  # Exit on error

echo "🔄 Running database migrations..."
python -m alembic upgrade head

echo "✅ Migrations completed successfully"
echo "🚀 Starting Uvicorn server..."

exec uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-8080}
```

**Startup Flow:**
1. Run Alembic migrations (gracefully skips if DATABASE_URL not available)
2. Start Uvicorn server on port 8080 (or $PORT if set)
3. Use `exec` to replace shell process with Uvicorn (proper signal handling)

---

## Deployment Analysis

### Current Deployment Logs (2025-10-13)

#### Startup Sequence

```
12:31:07 [inf] Starting Container
12:31:08 [inf] 🔄 Running database migrations...
12:31:08 [inf] ⚠️  WARNING: No valid DATABASE_URL found. Skipping migrations.
12:31:08 [inf] To enable migrations:
              1. Add PostgreSQL database in Railway dashboard
              2. DATABASE_URL will be automatically provided by Railway
              3. Redeploy the application
12:31:08 [inf] ✅ Migrations completed successfully
12:31:08 [inf] 🚀 Starting Uvicorn server...
```

**Status**: ✅ **Normal** - Application gracefully handles missing DATABASE_URL

#### Application Startup

```
12:31:13 [inf] 🚀 Using Supabase REST service for investigations (Railway/VPS)
12:31:13 [inf] === CHAT.PY LOADING - VERSION 13:45:00 ===
12:31:14 [err] INFO: Started server process [1]
12:31:14 [err] INFO: Waiting for application startup.
12:31:14 [inf] Cidadão.AI API started (env: production)
12:31:14 [err] INFO: Application startup complete.
12:31:14 [err] INFO: Uvicorn running on http://0.0.0.0:8080
```

**Status**: ✅ **Healthy** - Server started successfully on port 8080

#### Post-Startup (5 Minutes Later)

```
12:36:15 [wrn] [Multiple warning/error logs]
12:36:15 [err] [Connection/request errors]
```

**Status**: ⚠️ **Issue Detected** - Potential health check failures

### Problem Diagnosis

#### Symptoms
1. Application starts successfully
2. After ~5 minutes, warning/error logs appear
3. Pattern suggests health check failures or timeouts

#### Root Causes

**1. Health Check Timeout**

Railway performs health checks on deployed services. The `/ready` endpoint in `src/api/routes/health.py` makes a **real HTTP request** to Portal da Transparência:

```python
@router.get("/ready")
async def readiness_probe():
    transparency_status = await _check_transparency_api()
    if transparency_status["status"] == "healthy":
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")
```

**Issues:**
- External API calls in health checks can be slow or fail
- Portal da Transparência has 78% of endpoints returning 403
- Health checks should be fast (<1s) and not depend on external services

**2. Database Connection Check**

The health check also attempts to verify database connectivity, which may fail if DATABASE_URL is not configured properly.

**3. Railway Health Check Configuration**

Railway default health check settings:
- **Initial Delay**: 0 seconds (starts immediately)
- **Timeout**: 10 seconds per check
- **Failure Threshold**: 3 consecutive failures
- **Interval**: Every 30 seconds

If health checks fail for 5 minutes (10 consecutive failures), Railway may:
- Mark the service as unhealthy
- Restart the container
- Return 503 errors to clients

---

## Common Issues & Solutions

### Issue 1: Database Migration Warnings

**Symptom:**
```
⚠️  WARNING: No valid DATABASE_URL found. Skipping migrations.
```

**Solution:**

This is **expected behavior** when PostgreSQL is not configured. The application works with Supabase REST API for investigations.

**To Enable PostgreSQL (Optional):**

1. Add PostgreSQL database in Railway dashboard:
   ```bash
   railway add
   # Select PostgreSQL from list
   ```

2. Railway automatically provides `DATABASE_URL` environment variable

3. Redeploy application:
   ```bash
   railway redeploy
   ```

4. Verify migrations ran:
   ```bash
   railway logs --tail 50 | grep -i migration
   ```

### Issue 2: Health Check Failures

**Symptom:**
```
[wrn] Health check failed
[err] Connection timeout
```

**Solution:**

Create a lightweight health check endpoint that doesn't depend on external services.

**Recommended Implementation:**

```python
@router.get("/health")
async def simple_health():
    """Ultra-fast health check for Railway."""
    return {"status": "ok", "timestamp": datetime.utcnow()}
```

**Railway Configuration:**

Configure Railway to use the simple endpoint:
1. Go to Railway dashboard → Service Settings
2. Set **Health Check Path**: `/health`
3. Set **Initial Delay**: 10 seconds (allow startup time)
4. Set **Timeout**: 5 seconds

### Issue 3: Port Binding Issues

**Symptom:**
```
[err] Port 8080 already in use
[err] Failed to bind to 0.0.0.0:8080
```

**Solution:**

Ensure application uses `$PORT` environment variable:

```python
# In start.sh
exec uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-8080}
```

Railway automatically sets `$PORT` - never hardcode port numbers.

### Issue 4: CLI Authentication Errors

**Symptom:**
```
Project Token not found
Unauthorized. Please login with `railway login`
```

**Solution:**

1. Verify token is set:
   ```bash
   echo $RAILWAY_TOKEN
   ```

2. If not set, load from .bashrc:
   ```bash
   source ~/.bashrc
   ```

3. Verify authentication:
   ```bash
   railway whoami
   ```

4. If still failing, the token may have expired. Generate new token:
   - Go to Railway dashboard
   - Project Settings → Tokens
   - Generate new Project Token
   - Update `~/.bashrc`

---

## Environment Variables

### Required Variables

```bash
# LLM Provider
GROQ_API_KEY=your-groq-api-key

# Security
JWT_SECRET_KEY=your-jwt-secret-key
SECRET_KEY=your-app-secret-key
API_SECRET_KEY=your-api-secret-key

# Portal da Transparência (Optional)
TRANSPARENCY_API_KEY=your-transparency-api-key

# Supabase (For investigations)
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

### Optional Variables

```bash
# Database (PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:port/db

# Cache (Redis)
REDIS_URL=redis://host:port

# Application
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
```

### Managing Variables in Railway

```bash
# View all variables
railway variables

# Set a variable (interactive)
railway variables set

# Set via command line
railway run --env production env VAR_NAME=value

# View specific variable
railway variables get VAR_NAME
```

---

## Health Check Configuration

### Current Implementation

The application has three health check endpoints:

1. **`/health`** - Basic health check (recommended for Railway)
2. **`/health/detailed`** - Comprehensive system check
3. **`/health/ready`** - Kubernetes-style readiness probe (slow)

### Recommended Railway Configuration

#### Railway Dashboard Settings

1. **Health Check Path**: `/health/live`
2. **Initial Delay**: 15 seconds
3. **Timeout**: 5 seconds
4. **Interval**: 30 seconds
5. **Failure Threshold**: 3

#### Application Code

Ensure `/health/live` is ultra-fast and doesn't check external dependencies:

```python
@router.get("/live")
async def liveness_probe():
    """Simple liveness check - no external dependencies."""
    return {"status": "alive", "timestamp": datetime.utcnow()}
```

### Testing Health Checks Locally

```bash
# Test basic health
curl http://localhost:8080/health/live

# Test detailed health
curl http://localhost:8080/health/detailed

# Test readiness (may be slow)
curl http://localhost:8080/health/ready
```

---

## Next Steps

### Immediate Actions

1. **Fix Health Check** ✅
   - Implement lightweight `/health/live` endpoint
   - Update Railway health check configuration
   - Remove external API calls from critical health checks

2. **Configure Database** (Optional)
   - Add PostgreSQL service in Railway
   - Verify migrations run successfully
   - Test application with PostgreSQL

3. **Monitor Deployment**
   - Watch logs after redeploy
   - Verify no health check failures
   - Confirm uptime > 5 minutes without errors

### Long-term Improvements

1. **Implement Proper Database**
   - PostgreSQL for persistent storage
   - Connection pooling
   - Backup/recovery strategy

2. **Add Redis Cache**
   - Reduce API calls to Portal da Transparência
   - Improve response times
   - Implement distributed caching

3. **Set Up Monitoring**
   - Grafana dashboards for Railway metrics
   - Alert on health check failures
   - Track API response times

4. **CI/CD Pipeline**
   - Automated testing before deployment
   - Staging environment for testing
   - Automated rollback on failures

---

## Useful Resources

- **Railway Documentation**: https://docs.railway.app
- **Railway CLI GitHub**: https://github.com/railwayapp/cli
- **Nixpacks Documentation**: https://nixpacks.com/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/

---

## Troubleshooting Checklist

When deployment fails, check in order:

- [ ] Verify RAILWAY_TOKEN is set: `echo $RAILWAY_TOKEN`
- [ ] Check Railway service status: `railway status`
- [ ] View recent logs: `railway logs --tail 100`
- [ ] Test health endpoint locally: `curl localhost:8080/health/live`
- [ ] Verify environment variables: `railway variables`
- [ ] Check build logs in Railway dashboard
- [ ] Confirm port binding uses $PORT variable
- [ ] Review Alembic migration logs
- [ ] Test external API connectivity
- [ ] Check Railway resource limits (CPU/Memory)

---

## Contact & Support

For issues specific to this deployment:
- **Repository**: https://github.com/anderson-ufrj/cidadao.ai-backend
- **Author**: Anderson Henrique da Silva
- **Location**: Minas Gerais, Brasil

For Railway platform issues:
- **Railway Support**: https://railway.app/help
- **Community Discord**: https://discord.gg/railway
