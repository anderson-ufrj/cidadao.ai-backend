# 🚂 Railway Configuration Guide

## Critical Environment Variables for Railway

### ⚠️ IMPORTANT: LLM Provider Configuration

The system was failing because it was trying to use GROQ by default, but you're using Maritaca/Claude.

### Required Variables (Copy these to Railway Dashboard)

```bash
# ===== CORE SECURITY (REQUIRED) =====
SECRET_KEY=<your-secret-key>
JWT_SECRET_KEY=<your-jwt-secret-key>

# ===== LLM PROVIDER (CRITICAL - WAS MISSING!) =====
LLM_PROVIDER=maritaca  # <-- THIS IS CRITICAL! Was defaulting to 'groq'

# ===== MARITACA AI (Primary Provider) =====
MARITACA_API_KEY=<your-maritaca-api-key>
MARITACA_MODEL=sabia-3  # Options: sabiazinho-3, sabia-3, sabia-3-medium, sabia-3-large

# ===== ANTHROPIC CLAUDE (Backup Provider) =====
ANTHROPIC_API_KEY=<your-anthropic-api-key>
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# ===== DATABASE (Railway provides this) =====
# DATABASE_URL is automatically provided by Railway
# Our fix will auto-convert it to use asyncpg driver

# ===== OPTIONAL BUT RECOMMENDED =====
TRANSPARENCY_API_KEY=<portal-api-key-if-you-have>
APP_ENV=production
LOG_LEVEL=INFO
```

## 🔧 How to Configure in Railway

1. **Go to your Railway project**
2. **Click on your service (cidadao-api-production)**
3. **Go to Variables tab**
4. **Add/Update these variables:**
   - `LLM_PROVIDER` = `maritaca` (CRITICAL!)
   - `MARITACA_API_KEY` = (your actual key)
   - `MARITACA_MODEL` = `sabia-3`
   - `ANTHROPIC_API_KEY` = (your actual key as backup)

## ✅ What Was Fixed

### 1. **AgentContext Parameter Error**
- Fixed incorrect parameters (`conversation_id` → `investigation_id`)
- Fixed `session_data` → `metadata`
- Files: `investigations.py`, `analysis.py`, `reports.py`

### 2. **Async PostgreSQL Driver**
- Railway's DATABASE_URL uses `postgresql://` which defaults to sync driver
- Added automatic conversion to `postgresql+asyncpg://`
- File: `src/db/simple_session.py`

### 3. **LLM Provider Selection**
- System was defaulting to GROQ instead of reading from environment
- Fixed to use `settings.llm_provider` from environment
- File: `src/llm/services.py`

## 🧪 Testing the Fix

After setting the variables in Railway:

1. **Wait for deployment** (2-3 minutes)
2. **Check health**:
   ```bash
   curl https://cidadao-api-production.up.railway.app/health/
   ```
3. **Test investigation**:
   ```bash
   python3 test_single_investigation.py
   ```

## 📊 Expected Results

After proper configuration:
- ✅ Cache warming will work (rotates through 10 ministries)
- ✅ Investigations will process successfully
- ✅ Agents will use Maritaca AI for Portuguese analysis
- ✅ Fallback to Claude if Maritaca fails

## 🚨 Common Issues

### Issue: Investigation still failing
**Check**: Railway logs for "LLM provider not configured" or similar
**Fix**: Ensure `LLM_PROVIDER=maritaca` is set in Railway

### Issue: "API key not found"
**Check**: Railway variables for typos
**Fix**: Ensure `MARITACA_API_KEY` has actual key, not placeholder

### Issue: Database errors
**Check**: DATABASE_URL format
**Fix**: Our code now auto-converts to async driver

## 📝 Verification Script

Run locally to verify configuration:
```bash
python3 check_llm_config.py
```

This will show:
- Current LLM provider
- Available API keys
- Configuration status
