# Railway: Procfile vs railway.json

**Author**: Anderson Henrique da Silva
**Date**: 2025-10-13

---

## 🎯 Understanding Railway Configuration

Railway supports multiple ways to configure deployments. This document explains how **Procfile** and **railway.json** work together.

---

## 📋 Procfile (Process Type Declaration)

### What is Procfile?

A file that declares your application's process types and their startup commands.

**Location**: `/Procfile` (root directory)

**Format**:
```
<process_type>: <command>
```

### Your Current Procfile

```bash
# Database migrations (runs before deployment)
release: python -m alembic upgrade head

# Main API server (creates cidadao-api service)
web: uvicorn src.api.app:app --host 0.0.0.0 --port $PORT

# Celery worker (creates cidadao.ai-worker service)
worker: celery -A src.infrastructure.queue.celery_app worker --loglevel=info --queues=critical,high,default,low,background --concurrency=4

# Celery beat (creates cidadao.ai-beat service)
beat: celery -A src.infrastructure.queue.celery_app beat --loglevel=info
```

### Process Types

| Type | Railway Behavior | Your Service |
|------|-----------------|--------------|
| `web` | Creates HTTP service with public URL | cidadao-api |
| `worker` | Creates background worker | cidadao.ai-worker |
| `beat` | Creates scheduler | cidadao.ai-beat |
| `release` | Runs ONCE before deployment | Migration job |

---

## ⚙️ railway.json (Deployment Configuration)

### What is railway.json?

Global configuration file for build and deployment settings.

**Location**: `/railway.json` (root directory)

### Your Current Configuration

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Configuration Breakdown

#### Build Section

```json
"build": {
  "builder": "NIXPACKS"
}
```

**NIXPACKS**: Auto-detects Python, installs dependencies, builds project
- ✅ Reads `requirements.txt` or `pyproject.toml`
- ✅ Sets up Python environment
- ✅ Installs all dependencies
- ✅ Configures runtime

#### Deploy Section

```json
"deploy": {
  "restartPolicyType": "ON_FAILURE",
  "restartPolicyMaxRetries": 10
}
```

**Restart Policy**:
- `ON_FAILURE`: Only restart if service crashes
- `Max 10 retries`: Prevents infinite crash loops

---

## 🔄 How They Work Together

### Priority Order

1. **Railway looks for Procfile** ✅
   - If found, creates services from process types
   - Each process type becomes a separate service

2. **Railway reads railway.json** ✅
   - Applies global settings to ALL services
   - Build settings apply once
   - Deploy settings apply to each service

3. **Start Command Priority**:
   ```
   Procfile > railway.json > Default detection
   ```

### Your Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Railway Project: cidadao.ai                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Build Phase (railway.json)                              │
│     ├── Use NIXPACKS builder                                │
│     ├── Install requirements.txt                            │
│     └── Build application                                   │
│                                                              │
│  2. Release Phase (Procfile)                                │
│     └── Run: python -m alembic upgrade head                 │
│                                                              │
│  3. Deploy Phase (Procfile + railway.json)                  │
│     ├── Service: cidadao-api (web)                          │
│     │   ├── Command: uvicorn src.api.app:app...            │
│     │   └── Policy: Restart on failure (max 10)            │
│     │                                                        │
│     ├── Service: cidadao.ai-worker (worker)                │
│     │   ├── Command: celery -A src.infrastructure...       │
│     │   └── Policy: Restart on failure (max 10)            │
│     │                                                        │
│     └── Service: cidadao.ai-beat (beat)                    │
│         ├── Command: celery -A src.infrastructure...       │
│         └── Policy: Restart on failure (max 10)            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚠️ Important Notes

### Removed startCommand from railway.json

**Before** (Conflicting):
```json
"deploy": {
  "startCommand": "bash start.sh",  // ❌ Conflicts with Procfile
  "restartPolicyType": "ON_FAILURE",
  "restartPolicyMaxRetries": 10
}
```

**After** (Correct):
```json
"deploy": {
  "restartPolicyType": "ON_FAILURE",  // ✅ Applied to all services
  "restartPolicyMaxRetries": 10
}
```

**Why?**
- When Procfile exists, Railway uses it for startup commands
- `startCommand` in railway.json would conflict
- Procfile takes precedence anyway

### start.sh is Deprecated

The `start.sh` script is no longer used because:
1. Procfile `release` phase handles migrations
2. Procfile `web` command starts API directly
3. No need for intermediate shell script

**Keep start.sh** for local development or Docker, but Railway doesn't use it.

---

## 🔧 Configuration Options

### railway.json Full Options

```json
{
  "$schema": "https://railway.app/railway.schema.json",

  "build": {
    "builder": "NIXPACKS",           // or DOCKERFILE
    "buildCommand": "make build",    // Optional custom build
    "watchPatterns": ["src/**"]      // Trigger rebuild on changes
  },

  "deploy": {
    "startCommand": "...",           // Only if NO Procfile
    "restartPolicyType": "ON_FAILURE", // or ALWAYS, NEVER
    "restartPolicyMaxRetries": 10,
    "healthcheckPath": "/health",    // Per-service in dashboard
    "healthcheckTimeout": 300,
    "numReplicas": 1                 // Horizontal scaling
  }
}
```

### Procfile Full Options

```bash
# Process types available:

web: <command>          # HTTP service, gets public URL
worker: <command>       # Background worker
beat: <command>         # Scheduler
release: <command>      # Pre-deployment task

# Custom process types:
custom: <command>       # Any name, creates service
```

---

## 🚀 Deployment Flow

### Step 1: Git Push

```bash
git push origin main
```

### Step 2: Railway Detection

```
Railway detects:
├── Procfile ✅
├── railway.json ✅
├── requirements.txt ✅
└── Python project ✅
```

### Step 3: Build Phase

```
Using NIXPACKS:
├── Detect Python 3.13
├── Install dependencies from requirements.txt
├── Set up virtual environment
└── Build complete
```

### Step 4: Release Phase

```
Running release command:
└── python -m alembic upgrade head
    ├── Check DATABASE_URL
    ├── Run pending migrations
    └── ✅ Complete
```

### Step 5: Deploy Services

```
Creating services from Procfile:

┌─────────────────┐
│  cidadao-api    │ ← web: uvicorn ...
└─────────────────┘

┌─────────────────┐
│ .ai-worker      │ ← worker: celery worker ...
└─────────────────┘

┌─────────────────┐
│ .ai-beat        │ ← beat: celery beat ...
└─────────────────┘

Each service:
├── Restarts on failure
├── Max 10 restart attempts
└── Independent scaling
```

---

## 📊 Service-Specific Overrides

### Via Railway Dashboard

Each service can override settings:

**cidadao-api**:
```
Settings → Deploy
├── Health Check: /health (5s timeout)
├── Replicas: 2 (horizontal scaling)
└── Resources: 1GB RAM, 1 vCPU
```

**cidadao.ai-worker**:
```
Settings → Deploy
├── Health Check: DISABLED
├── Replicas: 3 (scale workers)
└── Resources: 2GB RAM, 2 vCPU
```

**cidadao.ai-beat**:
```
Settings → Deploy
├── Health Check: DISABLED
├── Replicas: 1 (NEVER scale beat!)
└── Resources: 512MB RAM, 0.5 vCPU
```

---

## 🔍 Debugging Configuration

### Check Active Configuration

```bash
# View applied build/deploy config
railway logs --tail 10 | grep -i "build\|deploy"

# Check which command is running
railway logs --service cidadao-api | grep "Starting"
railway logs --service cidadao.ai-worker | grep "Starting"
```

### Verify Procfile is Used

Look for in deployment logs:
```
Procfile detected
Creating service from process type: web
Creating service from process type: worker
Creating service from process type: beat
```

### Test Locally with Procfile

```bash
# Install foreman (Procfile runner)
pip install honcho

# Run all processes locally
honcho start

# Run specific process
honcho start web
honcho start worker
```

---

## 📝 Best Practices

### DO ✅

1. **Use Procfile for multi-service apps**
   - Clear service definitions
   - Easy to understand
   - Railway native support

2. **Keep railway.json minimal**
   - Only global settings
   - Build configuration
   - Shared deploy policies

3. **Use release for migrations**
   ```
   release: python -m alembic upgrade head
   ```

4. **Separate concerns**
   - Web: HTTP traffic
   - Worker: Background tasks
   - Beat: Scheduled jobs

### DON'T ❌

1. **Don't put startCommand in railway.json when using Procfile**
   - Causes conflicts
   - Procfile takes precedence anyway

2. **Don't scale beat scheduler**
   - Always keep replicas = 1
   - Multiple beats = duplicate tasks

3. **Don't use shell scripts as intermediaries**
   - Procfile commands should be direct
   - Shell scripts complicate debugging

4. **Don't hardcode ports**
   - Always use `$PORT` variable
   - Railway assigns ports dynamically

---

## 🔄 Migration Guide

### From start.sh to Procfile

**Old Way** (single service):
```json
// railway.json
{
  "deploy": {
    "startCommand": "bash start.sh"
  }
}
```

```bash
# start.sh
python -m alembic upgrade head
uvicorn src.api.app:app --host 0.0.0.0 --port $PORT
```

**New Way** (multi-service):
```bash
# Procfile
release: python -m alembic upgrade head
web: uvicorn src.api.app:app --host 0.0.0.0 --port $PORT
worker: celery -A src.infrastructure.queue.celery_app worker
beat: celery -A src.infrastructure.queue.celery_app beat
```

```json
// railway.json (simplified)
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Benefits**:
- ✅ Separate services for API, workers, beat
- ✅ Independent scaling
- ✅ Better observability
- ✅ Cleaner architecture

---

## 📚 Related Documentation

- **Multi-Service Guide**: `docs/deployment/RAILWAY_MULTI_SERVICE_GUIDE.md`
- **Health Checks**: `RAILWAY_SERVICE_HEALTH_CHECKS.md`
- **Procfile**: `/Procfile`
- **Railway Config**: `/railway.json`

---

## 🆘 Troubleshooting

### Services not created from Procfile

**Check**:
```bash
# Verify Procfile exists in root
ls -la Procfile

# Check Procfile format (no tabs, only spaces)
cat -A Procfile
```

**Fix**:
```bash
# Ensure proper format
# Use spaces, not tabs
# Use Unix line endings (LF, not CRLF)
```

### railway.json being ignored

**Cause**: Syntax error in JSON

**Fix**:
```bash
# Validate JSON
python -m json.tool railway.json

# Or use online validator
# https://jsonlint.com
```

### Commands not working

**Check environment**:
```bash
# Test commands locally
honcho start web
honcho start worker

# Or individually
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
celery -A src.infrastructure.queue.celery_app worker
```

---

**Last Updated**: 2025-10-13
**Status**: Production configuration updated
**Maintainer**: Anderson Henrique da Silva
