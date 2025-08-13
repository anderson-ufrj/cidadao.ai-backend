# 🔒 Security Guide - Cidadão.AI

## Overview

This document outlines the security practices and requirements for deploying Cidadão.AI safely in production environments.

## ⚠️ CRITICAL SECURITY CHANGES

As of this version, **all hardcoded credentials have been removed**. The application will **NOT start** without proper environment variables configured.

## Required Environment Variables

### Core Security (REQUIRED)

```bash
SECRET_KEY=your_application_secret_key_min_32_characters_long
JWT_SECRET_KEY=your_jwt_secret_key_min_64_characters_long
DATABASE_URL=postgresql://username:password@host:port/database
```

### User Management (Development Only)

```bash
# Admin User (optional - for development)
ADMIN_USER_EMAIL=admin@your-domain.com
ADMIN_USER_PASSWORD=your_secure_admin_password
ADMIN_USER_NAME=Administrator

# Analyst User (optional - for development) 
ANALYST_USER_EMAIL=analyst@your-domain.com
ANALYST_USER_PASSWORD=your_secure_analyst_password
ANALYST_USER_NAME=Analyst
```

**⚠️ Important**: In production, use a proper database-backed user management system instead of environment variables.

## Quick Setup

### 1. Generate Secure Secrets

```bash
# Run the secret generation script
python3 scripts/generate_secrets.py

# This creates:
# - .env.secure (application secrets)
# - deployment/.env.secure (Docker secrets)
```

### 2. Configure Environment

```bash
# Copy and customize for your environment
cp .env.secure .env
cp deployment/.env.secure deployment/.env

# Edit the files to add your API keys and customize settings
nano .env
nano deployment/.env
```

### 3. Verify Security

```bash
# Test that app fails without secrets
python3 -c "from src.api.auth import AuthManager; AuthManager()"
# Should raise: ValueError: JWT_SECRET_KEY environment variable is required

# Test with secrets
export JWT_SECRET_KEY="your-secure-key-here"
python3 -c "from src.api.auth import AuthManager; print('✅ Auth configured')"
```

## Production Deployment

### Secret Management Best Practices

1. **Use a Secret Management System**
   - Recommended: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault
   - Never store secrets in code or configuration files

2. **Environment Variables in Production**
   ```bash
   # Use secure methods to set environment variables
   kubectl create secret generic cidadao-secrets \
     --from-literal=JWT_SECRET_KEY="your-jwt-secret" \
     --from-literal=SECRET_KEY="your-app-secret"
   ```

3. **Database Security**
   ```bash
   # Create dedicated database user with minimal privileges
   CREATE USER cidadao_api WITH PASSWORD 'secure-generated-password';
   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO cidadao_api;
   ```

## Security Features

### Authentication & Authorization
- JWT-based authentication with configurable expiration
- Role-based access control (admin, analyst roles)
- Bcrypt password hashing with configurable rounds
- OAuth2 integration support

### API Security
- Rate limiting (60 requests/minute, 1000/hour)
- Request size validation (10MB max)
- URL length validation (2KB max) 
- XSS and SQL injection protection
- CSRF protection with HMAC tokens

### Security Headers
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

### Audit Logging
- Comprehensive audit trail for all security events
- Login attempts, unauthorized access, rate limit violations
- Cryptographic integrity checking of audit logs
- Configurable retention (default: 90 days)

## Monitoring & Alerting

### Security Metrics
- Failed authentication attempts
- Rate limit violations  
- Suspicious request patterns
- Account lockouts and security events

### Recommended Alerts
```yaml
# Example Prometheus alerts
- alert: HighFailedLogins
  expr: rate(auth_failed_total[5m]) > 10
  
- alert: RateLimitExceeded  
  expr: rate(rate_limit_exceeded_total[1m]) > 5
```

## Incident Response

### Security Incident Checklist
1. **Immediate Response**
   - Identify and isolate affected systems
   - Review audit logs for timeline
   - Notify security team

2. **Investigation**
   - Check authentication logs
   - Review rate limiting events
   - Examine database access patterns

3. **Recovery**
   - Rotate compromised secrets
   - Update security policies
   - Deploy patches if needed

## Security Testing

### Automated Security Tests
```bash
# Run security test suite
pytest tests/unit/test_auth_complete.py -v
pytest tests/unit/test_jwt_validation.py -v
pytest tests/integration/test_api_security.py -v
```

### Manual Security Checks
1. **Authentication Testing**
   - Test token expiration
   - Verify password complexity
   - Check role-based access

2. **API Security Testing**
   - Rate limiting validation
   - Input validation tests
   - SQL injection attempts

## Compliance

### LGPD (Lei Geral de Proteção de Dados)
- Data minimization in logs
- User consent management
- Data retention policies
- Right to be forgotten implementation

### Security Standards
- Following OWASP Top 10 guidelines
- Secure coding practices
- Regular security assessments
- Dependency vulnerability scanning

## Contact

For security issues or questions:
- **Security Team**: security@cidadao.ai
- **Emergency**: Use encrypted communication channels
- **Bug Reports**: Follow responsible disclosure

---

**Remember**: Security is a shared responsibility. Always follow the principle of least privilege and keep systems updated.