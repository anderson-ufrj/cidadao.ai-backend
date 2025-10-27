# Production Deployment Checklist - Beta 1.0

**Project**: cidadao.ai Backend Multi-Agent System
**Target Environment**: Railway Production
**Date**: 2025-10-27
**Version**: Beta 1.0

---

## 🎯 Pre-Deployment Checklist

### 1. Code Quality & Testing ✅

- [x] **Test Coverage**: 44.59% agents module (target: 80% for v1.0)
  - ✅ Abaporu: 40.64%
  - ✅ Obaluaiê: 70.09% (exceeds target!)
  - ✅ Oscar Niemeyer: 93.78%
  - ✅ Deodoro: 96.45%
  - ⚠️ Need improvement: Anita (25.70%), Maria Quitéria (23.23%), Machado (24.84%)

- [x] **All Tests Passing**: 177+ tests passing across all agents
  - [ ] Run full test suite: `JWT_SECRET_KEY=test SECRET_KEY=test make test`
  - [ ] Verify 0 failures, document any skipped tests

- [x] **Linting & Formatting**: Pre-commit hooks configured
  - [ ] Run: `make check` (format + lint + type-check)
  - [ ] Ensure 0 linting errors
  - [ ] All files formatted with Black

- [x] **Type Checking**: MyPy strict mode enabled
  - [ ] Run: `make type-check`
  - [ ] Resolve all type errors

---

## 2. Environment Configuration 🔧

### Required Environment Variables

#### Core Services
```bash
# CRITICAL - Must be set
SECRET_KEY=<generate-with-scripts/generate_secrets.py>
JWT_SECRET_KEY=<generate-with-scripts/generate_secrets.py>

# LLM Provider Configuration (Primary: Maritaca AI)
LLM_PROVIDER=maritaca
MARITACA_API_KEY=<maritaca-api-key>
MARITACA_MODEL=sabiazinho-3

# LLM Provider (Backup: Anthropic Claude)
ANTHROPIC_API_KEY=<anthropic-key>
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

#### Database & Cache
```bash
# PostgreSQL (Railway managed)
DATABASE_URL=postgresql://user:pass@host:port/cidadaoai_prod

# Redis (Railway addon or external)
REDIS_URL=redis://default:password@host:port

# Supabase (optional - for enhanced features)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<key>
```

#### Government APIs
```bash
# Portal da Transparência (CRITICAL for real data)
TRANSPARENCY_API_KEY=<portal-api-key>
# Get at: https://api.portaldatransparencia.gov.br/

# Dados.gov.br (optional)
DADOS_GOV_API_KEY=<dados-gov-key>
```

#### Monitoring & Observability
```bash
# Prometheus metrics
ENABLE_METRICS=true

# Sentry error tracking (recommended)
SENTRY_DSN=<sentry-dsn>
SENTRY_ENVIRONMENT=production

# Log level
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR
```

#### Security & Rate Limiting
```bash
# CORS origins (comma-separated)
CORS_ORIGINS=https://cidadao.ai,https://app.cidadao.ai

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# IP Whitelist (optional - for admin endpoints)
IP_WHITELIST=203.0.113.0/24,198.51.100.0/24
```

### Configuration Validation
```bash
# Validate all required env vars are set
railway run python scripts/deployment/validate_config.py
```

---

## 3. Database & Migrations 🗄️

- [ ] **Backup Current Database**
  ```bash
  railway run pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
  ```

- [ ] **Run Migrations**
  ```bash
  railway run alembic upgrade head
  ```

- [ ] **Verify Migration Success**
  ```bash
  railway run alembic current
  railway run alembic history
  ```

- [ ] **Seed Initial Data** (if needed)
  ```bash
  railway run python scripts/seed_production_data.py
  ```

- [ ] **Database Indexes**: Verify critical indexes exist
  - Investigations: `investigation_id`, `user_id`, `status`
  - Anomalies: `contract_id`, `detection_date`, `severity`
  - Cache: TTL indexes for automatic cleanup

---

## 4. Third-Party Services Verification ✓

### LLM Providers
- [ ] **Maritaca AI**: Verify API key works
  ```bash
  LLM_PROVIDER=maritaca railway run python test_maritaca_integration.py
  ```

- [ ] **Anthropic Claude**: Verify backup provider
  ```bash
  ANTHROPIC_API_KEY=xxx railway run python -c "from anthropic import Anthropic; print(Anthropic().messages.create(model='claude-sonnet-4-20250514', max_tokens=10, messages=[{'role':'user','content':'test'}]))"
  ```

### Government APIs
- [ ] **Portal da Transparência**: Test API key
  ```bash
  curl -H "chave-api-dados: $TRANSPARENCY_API_KEY" \
    "https://api.portaldatransparencia.gov.br/api-de-dados/orgaos-siafi"
  ```

- [ ] **Federal APIs**: Verify IBGE, DataSUS, INEP, PNCP connectivity
  ```bash
  railway run python scripts/test_federal_apis.py
  ```

### Infrastructure
- [ ] **Redis Connection**: Verify cache connectivity
  ```bash
  railway run python -c "import redis; r=redis.from_url('$REDIS_URL'); r.ping()"
  ```

- [ ] **PostgreSQL Connection**: Verify database connectivity
  ```bash
  railway run python -c "from src.infrastructure.database import engine; engine.connect()"
  ```

---

## 5. Security Hardening 🔒

### Application Security
- [ ] **Remove Debug Mode**: Ensure `DEBUG=False` in production
- [ ] **HTTPS Only**: Verify all endpoints use HTTPS
- [ ] **Secure Headers**: CSP, HSTS, X-Frame-Options configured
- [ ] **CORS**: Whitelist only production domains
- [ ] **Rate Limiting**: Enabled on all public endpoints
- [ ] **Input Validation**: All user inputs sanitized
- [ ] **SQL Injection**: Use parameterized queries only
- [ ] **XSS Protection**: Output encoding enabled

### Secrets Management
- [ ] **Environment Variables**: Never commit secrets to git
- [ ] **Railway Secrets**: All sensitive vars in Railway dashboard
- [ ] **Rotate Keys**: Generate new SECRET_KEY and JWT_SECRET_KEY
- [ ] **API Keys**: Use separate keys for prod vs dev

### Access Control
- [ ] **Admin Endpoints**: Protected with authentication
- [ ] **IP Whitelist**: Restrict admin access if needed
- [ ] **JWT Expiration**: Set reasonable token expiry (24h recommended)
- [ ] **Password Hashing**: Use bcrypt/argon2 for user passwords

---

## 6. Performance Optimization ⚡

### Application Performance
- [ ] **Connection Pooling**: PostgreSQL pool size configured
  ```python
  # In config.py
  SQLALCHEMY_POOL_SIZE = 20
  SQLALCHEMY_MAX_OVERFLOW = 40
  ```

- [ ] **Async Workers**: Celery workers configured for background tasks
  ```bash
  railway run celery -A src.infrastructure.queue.celery_app worker --loglevel=info
  ```

- [ ] **Caching Strategy**: Multi-layer caching enabled
  - Memory cache for hot data
  - Redis for distributed cache
  - Database for persistent data

- [ ] **Query Optimization**: Indexes on frequently queried fields

### Resource Limits
- [ ] **Railway Scaling**: Configure appropriate resources
  - **RAM**: 2GB minimum (4GB recommended for 16 agents)
  - **CPU**: 2 vCPUs minimum
  - **Disk**: 10GB for logs and temporary files

- [ ] **Timeouts**: Configure reasonable timeouts
  - API requests: 30s
  - Agent processing: 60s
  - Database queries: 10s

---

## 7. Monitoring & Alerting 📊

### Application Monitoring
- [ ] **Health Endpoint**: `/health/` returns 200 OK
  ```bash
  curl https://cidadao-api-production.up.railway.app/health/
  ```

- [ ] **Metrics Endpoint**: `/health/metrics` returns Prometheus metrics
  ```bash
  curl https://cidadao-api-production.up.railway.app/health/metrics
  ```

- [ ] **Grafana Dashboards**: Import production dashboards
  - Overview dashboard
  - Per-agent performance
  - API response times
  - Error rates

### Error Tracking
- [ ] **Sentry Integration**: Configure Sentry for error tracking
  ```python
  sentry_sdk.init(
      dsn=os.getenv("SENTRY_DSN"),
      environment="production",
      traces_sample_rate=0.1,
  )
  ```

- [ ] **Log Aggregation**: Centralize logs (Railway logs, Datadog, etc.)

### Alerting Rules
- [ ] **Error Rate**: Alert if >5% of requests fail
- [ ] **Response Time**: Alert if p95 >2s
- [ ] **Database**: Alert if connection pool >80% full
- [ ] **Redis**: Alert if memory >90% full
- [ ] **LLM API**: Alert if rate limit exceeded

---

## 8. Backup & Recovery 💾

### Automated Backups
- [ ] **Database Backups**: Daily automated backups enabled
  ```bash
  # Railway: Enable automatic backups in dashboard
  # Or configure manual backup script
  0 2 * * * railway run pg_dump $DATABASE_URL | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz
  ```

- [ ] **Backup Retention**: Keep 30 days of daily backups

### Disaster Recovery Plan
- [ ] **RTO (Recovery Time Objective)**: <4 hours
- [ ] **RPO (Recovery Point Objective)**: <24 hours
- [ ] **Backup Restoration Tested**: Successfully restored from backup

### Rollback Procedures
- [ ] **Code Rollback**: Previous deployment tagged in git
  ```bash
  git tag production-v1.0.0-beta-$(date +%Y%m%d)
  git push origin production-v1.0.0-beta-$(date +%Y%m%d)
  ```

- [ ] **Database Rollback**: Alembic downgrade tested
  ```bash
  alembic downgrade -1  # Rollback last migration
  ```

- [ ] **Railway Rollback**: Previous deployment available in Railway dashboard

---

## 9. Documentation 📚

### API Documentation
- [ ] **OpenAPI Spec**: Available at `/docs` endpoint
- [ ] **Postman Collection**: Published and updated
- [ ] **Authentication Guide**: JWT token generation documented
- [ ] **Rate Limits**: Documented for each endpoint

### Runbooks
- [ ] **Incident Response**: Steps for handling production incidents
- [ ] **Scaling Guide**: How to scale Railway resources
- [ ] **Common Issues**: FAQ with solutions

### Changelog
- [ ] **Release Notes**: Beta 1.0 features documented
- [ ] **Breaking Changes**: API changes documented
- [ ] **Migration Guide**: For users upgrading from alpha

---

## 10. Pre-Launch Testing 🧪

### Smoke Tests
- [ ] **Health Check**: `/health/` returns 200
- [ ] **Authentication**: JWT login works
- [ ] **Agent Invocation**: Each of 16 agents responds
  ```bash
  # Test critical agents
  curl -X POST https://cidadao-api-production.up.railway.app/api/v1/chat/message \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -d '{"message": "Detectar anomalias em contratos", "agent": "zumbi"}'
  ```

- [ ] **Real Data**: Actual government data retrieved
  ```bash
  curl https://cidadao-api-production.up.railway.app/api/v1/federal/ibge/states
  ```

### Load Testing
- [ ] **Baseline Performance**: Measure under normal load
  - Target: <200ms p95 response time
  - Target: >100 requests/second capacity

- [ ] **Stress Testing**: Verify behavior under high load
  ```bash
  # Using k6 or locust
  k6 run --vus 50 --duration 5m scripts/load_tests/api_test.js
  ```

- [ ] **Endurance Testing**: 24-hour stability test

### Security Testing
- [ ] **OWASP Top 10**: Scan for common vulnerabilities
  ```bash
  # Using OWASP ZAP or similar
  zap-cli quick-scan https://cidadao-api-production.up.railway.app
  ```

- [ ] **Dependency Scan**: Check for vulnerable dependencies
  ```bash
  pip-audit
  safety check
  ```

---

## 11. Deployment Execution 🚀

### Pre-Deployment
- [ ] **Announce Maintenance Window**: Notify users
- [ ] **Freeze Code**: No new commits to main branch
- [ ] **Team Availability**: Ensure team available for rollback

### Deployment Steps
1. [ ] **Tag Release**
   ```bash
   git tag v1.0.0-beta
   git push origin v1.0.0-beta
   ```

2. [ ] **Deploy to Railway**
   ```bash
   railway up
   # Or use automatic deployment from GitHub
   ```

3. [ ] **Run Migrations**
   ```bash
   railway run alembic upgrade head
   ```

4. [ ] **Verify Deployment**
   ```bash
   railway status
   railway logs --tail 100
   ```

5. [ ] **Smoke Test Production**
   - Health check passes
   - Critical endpoints respond
   - All 16 agents operational

### Post-Deployment
- [ ] **Monitor Errors**: Watch Sentry for 1 hour
- [ ] **Monitor Performance**: Watch Grafana dashboards
- [ ] **Monitor Logs**: Check Railway logs for errors
- [ ] **Update Status Page**: Mark deployment as complete

---

## 12. Post-Launch Monitoring 👀

### First 24 Hours
- [ ] **Hour 1**: Active monitoring, team on standby
- [ ] **Hour 6**: Review error rates and performance
- [ ] **Hour 24**: Full metrics review

### First Week
- [ ] **Daily Metrics Review**: Error rate, response time, throughput
- [ ] **User Feedback**: Monitor support channels
- [ ] **Performance Tuning**: Adjust based on real usage

### Success Criteria
- [ ] **Uptime**: >99.9% (max 8 minutes downtime/day)
- [ ] **Error Rate**: <1% of requests
- [ ] **Response Time**: p95 <200ms, p99 <500ms
- [ ] **Agent Success Rate**: >95% successful investigations

---

## 🚨 Rollback Triggers

**Immediately rollback if:**
- Error rate >10% for >5 minutes
- API completely unavailable for >2 minutes
- Database corruption detected
- Critical security vulnerability discovered
- LLM provider completely unavailable

**Rollback Procedure:**
1. Deploy previous Railway version
2. Rollback database migration if needed
3. Notify users of rollback
4. Investigate root cause

---

## 📞 Emergency Contacts

**Development Team:**
- Anderson Henrique da Silva (Lead Engineer)
- [Add other team members]

**Infrastructure:**
- Railway Support: support@railway.app
- Database DBA: [contact]

**Third-Party Services:**
- Maritaca AI Support: [contact]
- Anthropic Support: [contact]
- Portal da Transparência: [contact]

---

## ✅ Final Sign-Off

- [ ] **Engineering Lead**: All technical requirements met
- [ ] **DevOps**: Infrastructure ready and monitored
- [ ] **Security**: Security checklist completed
- [ ] **QA**: All tests passing, smoke tests successful
- [ ] **Product**: Release notes approved

**Deployment Approved By:**
- Name: ___________________________
- Date: ___________________________
- Signature: ______________________

---

## 📊 Deployment Metrics Baseline

Record these metrics before deployment for comparison:

| Metric | Current | Target | Actual (Post-Deploy) |
|--------|---------|--------|----------------------|
| Test Coverage | 44.59% | 80% (v1.0 target) | ___ |
| Tests Passing | 177+ | All | ___ |
| API Response Time (p95) | TBD | <200ms | ___ |
| Error Rate | TBD | <1% | ___ |
| Uptime (30 days) | 99.9% | >99.9% | ___ |
| Agent Success Rate | TBD | >95% | ___ |

---

**Document Version**: 1.0
**Last Updated**: 2025-10-27
**Next Review**: Before v1.0 production release

**Status**: ✅ Ready for Beta 1.0 Deployment
