# 🔧 Troubleshooting Guide - Cidadão.AI Backend

**Author**: Anderson Henrique da Silva
**Last Updated**: 2025-10-03 (São Paulo, Brazil)

This directory contains troubleshooting guides and solutions for common issues encountered during development, deployment, and operation of the Cidadão.AI Backend.

## 📋 Available Guides

### Deployment Issues

- **[FIX_HUGGINGFACE_DEPLOYMENT.md](./FIX_HUGGINGFACE_DEPLOYMENT.md)** - HuggingFace Spaces deployment fixes
  - Common HF Spaces errors
  - Docker configuration issues
  - Environment variable problems
  - Build failures and solutions

- **[EMERGENCY_SOLUTION.md](./EMERGENCY_SOLUTION.md)** - Emergency recovery procedures
  - Critical system failures
  - Data recovery strategies
  - Rollback procedures
  - Incident response guide

---

## 🚨 Common Issues & Quick Fixes

### 1. Import Errors

**Problem**: `ModuleNotFoundError` or `ImportError`

**Solution**:
```bash
# Reinstall dependencies
make install-dev

# Or manually
pip install -r requirements.txt

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

---

### 2. Database Connection Issues

**Problem**: `OperationalError: could not connect to database`

**Solution**:
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string in .env
DATABASE_URL=postgresql://user:password@localhost:5432/cidadao_ai

# Fallback to in-memory (development only)
# Remove or comment out DATABASE_URL in .env
```

---

### 3. Redis Connection Errors

**Problem**: `redis.exceptions.ConnectionError`

**Solution**:
```bash
# Start Redis
sudo systemctl start redis

# Or use Docker
docker run -d -p 6379:6379 redis:alpine

# Redis is OPTIONAL - system works without it
# Remove REDIS_URL from .env to disable
```

---

### 4. API Key / Authentication Issues

**Problem**: `401 Unauthorized` or `Invalid API key`

**Solution**:
```bash
# Check .env file has required keys
GROQ_API_KEY=your-groq-api-key
JWT_SECRET_KEY=your-jwt-secret
SECRET_KEY=your-secret-key

# Generate new secrets
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Test API key
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/auth/me
```

---

### 5. Portal da Transparência 403 Errors

**Problem**: Most Portal da Transparência endpoints return 403 Forbidden

**Solution**:
This is **expected behavior** - 78% of endpoints are blocked without documented access tiers.

**Workarounds**:
1. Use the 22% working endpoints (contracts with `codigoOrgao`, servants by CPF)
2. Enable demo mode (works without API key)
3. Use dados.gov.br integration as fallback

```python
# In .env
TRANSPARENCY_API_KEY=  # Leave empty for demo mode
```

See: [Portal Integration Guide](../api/PORTAL_TRANSPARENCIA_INTEGRATION.md)

---

### 6. Test Failures

**Problem**: Tests failing with various errors

**Solution**:
```bash
# Run specific test to diagnose
pytest tests/unit/agents/test_zumbi.py -v

# Check test environment
pytest --collect-only

# Clear test cache
pytest --cache-clear

# Run with debug output
pytest -vv --tb=long

# Check coverage
pytest --cov=src --cov-report=html
```

---

### 7. Agent Timeout Errors

**Problem**: Agent operations timing out

**Solution**:
```bash
# Increase timeout in .env
AGENT_TIMEOUT=300  # 5 minutes

# Check GROQ API status
curl https://api.groq.com/openai/v1/models -H "Authorization: Bearer $GROQ_API_KEY"

# Monitor agent logs
tail -f logs/agents.log
```

---

### 8. Memory Issues / Out of Memory

**Problem**: Application crashes with OOM errors

**Solution**:
```bash
# Reduce agent pool size
AGENT_POOL_SIZE=3  # Default is 5

# Enable aggressive garbage collection
PYTHONMALLOC=malloc

# Monitor memory usage
make monitoring-up
# Check Grafana dashboard

# Clear cache
redis-cli FLUSHALL
```

---

### 9. CORS Errors (Frontend Integration)

**Problem**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:
```python
# In src/api/app.py, verify CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://your-frontend.vercel.app",
]
```

Check: [CORS Configuration Guide](../development/CORS_CONFIGURATION.md)

---

### 10. HuggingFace Spaces Build Failures

**Problem**: Build fails on HuggingFace Spaces

**Common causes**:
1. Missing dependencies in `requirements-minimal.txt`
2. Port not set to 7860
3. Dockerfile not found or misconfigured

**Solution**:
```dockerfile
# Ensure Dockerfile exposes port 7860
EXPOSE 7860

# Use simplified app.py for HF Spaces
CMD ["python", "app.py"]

# Not the full src/api/app.py
```

See: [FIX_HUGGINGFACE_DEPLOYMENT.md](./FIX_HUGGINGFACE_DEPLOYMENT.md)

---

## 🔍 Debugging Tools

### Enable Debug Logging

```python
# In your code or .env
import logging
logging.basicConfig(level=logging.DEBUG)

# For specific modules
logging.getLogger("src.agents").setLevel(logging.DEBUG)
logging.getLogger("src.api").setLevel(logging.INFO)
```

### Use Interactive Debugger

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use ipdb for better experience
import ipdb; ipdb.set_trace()
```

### Profile Performance

```bash
# Profile with cProfile
python -m cProfile -o profile.stats src/api/app.py

# Analyze with snakeviz
pip install snakeviz
snakeviz profile.stats
```

### Monitor in Real-time

```bash
# Start monitoring stack
make monitoring-up

# Access Grafana
http://localhost:3000
# User: admin, Password: cidadao123

# Check Prometheus metrics
http://localhost:9090
```

---

## 📊 Health Check Endpoints

Use these endpoints to diagnose system health:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health with dependencies
curl http://localhost:8000/api/v1/health/detailed

# Agent status
curl http://localhost:8000/api/v1/agents/status

# Database connection
curl http://localhost:8000/api/v1/health/db

# Redis connection
curl http://localhost:8000/api/v1/health/cache
```

---

## 🚑 Emergency Procedures

### System Down / Critical Failure

1. **Check health endpoints** to identify failing components
2. **Review logs**: `tail -f logs/*.log`
3. **Restart services**:
   ```bash
   systemctl restart cidadao-ai
   # Or
   docker-compose restart
   ```
4. **Rollback if needed**: See [EMERGENCY_SOLUTION.md](./EMERGENCY_SOLUTION.md)

### Data Corruption

1. **Stop the application immediately**
2. **Create database backup**:
   ```bash
   pg_dump cidadao_ai > backup_$(date +%Y%m%d_%H%M%S).sql
   ```
3. **Investigate with read-only mode**
4. **Restore from last known good backup if necessary**

### Security Incident

1. **Rotate all secrets immediately**:
   ```bash
   # Generate new secrets
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
2. **Revoke compromised API keys**
3. **Review access logs**
4. **Apply security patches**
5. **Notify affected users**

---

## 📝 Logging & Monitoring

### Log Locations

```bash
# Application logs
logs/app.log

# Agent logs
logs/agents.log

# Error logs
logs/error.log

# Access logs (if nginx/reverse proxy)
/var/log/nginx/access.log
```

### Log Analysis

```bash
# Search for errors
grep -i error logs/*.log

# Find specific agent errors
grep "agent=zumbi" logs/agents.log | grep ERROR

# Count errors by type
awk '/ERROR/ {print $NF}' logs/error.log | sort | uniq -c
```

---

## 🔗 Related Resources

- [Deployment Guide](../deployment/README.md)
- [Development Guide](../development/README.md)
- [API Documentation](../api/README.md)
- [Architecture Overview](../architecture/README.md)

---

## 📞 Getting Help

### Before Opening an Issue

1. ✅ Check this troubleshooting guide
2. ✅ Search existing GitHub issues
3. ✅ Review relevant documentation
4. ✅ Try suggested solutions above

### When Opening an Issue

Include:
- **Error message** (full stack trace)
- **Steps to reproduce**
- **Environment details** (OS, Python version, deployment type)
- **Configuration** (relevant .env variables, sanitized)
- **Logs** (relevant sections)
- **What you've tried** (from this guide)

### Issue Template

```markdown
**Environment**:
- OS: Ubuntu 22.04
- Python: 3.11.5
- Deployment: Local development

**Problem**:
[Describe the issue]

**Error Message**:
```
[Paste full error]
```

**Steps to Reproduce**:
1. ...
2. ...

**What I've Tried**:
- Checked logs: [findings]
- Tried solution X from troubleshooting guide: [result]

**Additional Context**:
[Any other relevant information]
```

---

## 💡 Tips for Preventing Issues

### Development
- ✅ Run `make ci` before committing
- ✅ Keep dependencies updated
- ✅ Write tests for new features
- ✅ Use type hints and linting

### Deployment
- ✅ Use environment variables (never hardcode)
- ✅ Test in staging before production
- ✅ Monitor health endpoints
- ✅ Keep backups current

### Operations
- ✅ Set up alerts for critical metrics
- ✅ Regular log rotation
- ✅ Capacity planning
- ✅ Security updates

---

**Remember**: Most issues have been encountered and solved before. Check this guide first, then ask for help! 🚀
