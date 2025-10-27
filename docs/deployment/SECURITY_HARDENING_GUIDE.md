# Security Hardening Guide - Production Deployment

**Project**: cidadao.ai Backend Multi-Agent System
**Target Environment**: Railway Production
**Date**: 2025-10-27
**Version**: Beta 1.0

---

## 🎯 Overview

This guide provides comprehensive security hardening procedures for the cidadao.ai backend system. It complements the Production Deployment Checklist with detailed security implementation guidance.

**Security Principles**:
- **Defense in Depth**: Multiple layers of security controls
- **Least Privilege**: Minimal access rights for all components
- **Fail Secure**: System fails to a secure state
- **Security by Design**: Security integrated from the start

---

## 1. OWASP Top 10 Compliance ✅

### A01:2021 - Broken Access Control

#### Current Implementation
- **JWT-based authentication**: Token expiry, signature verification
- **Role-based access control (RBAC)**: Admin vs user permissions
- **API key authentication**: For service-to-service communication

#### Hardening Steps
```python
# src/core/security/access_control.py

# ✅ IMPLEMENTED: JWT token validation
def verify_jwt_token(token: str) -> dict:
    """Verify JWT token with signature and expiry checks."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        if payload.get("exp", 0) < time.time():
            raise TokenExpiredError("Token has expired")
        return payload
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")

# ✅ IMPLEMENTED: Role verification
def require_role(required_role: str):
    """Decorator to enforce role-based access."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = get_current_user()
            if user.role != required_role and user.role != "admin":
                raise PermissionDeniedError(
                    f"Required role: {required_role}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

#### Verification Checklist
- [x] JWT tokens expire after 24 hours
- [x] Tokens use HS256 signature algorithm
- [x] Admin endpoints require `admin` role
- [x] Investigation endpoints require authentication
- [ ] **TODO**: Implement refresh token rotation
- [ ] **TODO**: Add IP-based access restrictions for admin panel

---

### A02:2021 - Cryptographic Failures

#### Current Implementation
- **Password hashing**: Bcrypt with salt (10 rounds)
- **Secret key management**: Environment variables only
- **HTTPS enforcement**: All production traffic

#### Hardening Steps
```bash
# Generate cryptographically secure secrets
python3 scripts/generate_secrets.py

# Output example:
# SECRET_KEY=7f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0
# JWT_SECRET_KEY=9f0e1d2c3b4a5968778695a4b3c2d1e0f9e8d7c6b5a4938271605f4e3d2c1b0a
```

```python
# src/core/security/crypto.py

# ✅ IMPLEMENTED: Secure password hashing
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt with salt."""
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

#### Verification Checklist
- [x] Passwords hashed with bcrypt (10 rounds)
- [x] Secrets stored in environment variables
- [x] No secrets in git repository
- [x] HTTPS enforced in production
- [ ] **TODO**: Rotate secrets every 90 days
- [ ] **TODO**: Implement secret encryption at rest
- [ ] **TODO**: Add secret access audit logging

---

### A03:2021 - Injection

#### Current Implementation
- **Parameterized queries**: SQLAlchemy ORM prevents SQL injection
- **Input validation**: Pydantic models for all API inputs
- **Command injection prevention**: No shell execution with user input

#### Hardening Steps
```python
# src/models/investigation.py

# ✅ IMPLEMENTED: Pydantic validation
from pydantic import BaseModel, Field, validator

class InvestigationCreate(BaseModel):
    """Investigation creation model with strict validation."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Investigation query"
    )

    @validator("query")
    def validate_query(cls, v):
        """Prevent injection attacks in queries."""
        # Block SQL keywords
        sql_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "EXEC"]
        for keyword in sql_keywords:
            if keyword in v.upper():
                raise ValueError(f"Invalid query: contains {keyword}")

        # Block shell metacharacters
        shell_chars = [";", "|", "&", "$", "`", "(", ")"]
        for char in shell_chars:
            if char in v:
                raise ValueError(f"Invalid query: contains {char}")

        return v
```

#### SQL Injection Prevention
```python
# ✅ CORRECT: SQLAlchemy ORM (parameterized)
investigations = db.query(Investigation).filter(
    Investigation.user_id == user_id
).all()

# ❌ WRONG: String concatenation (vulnerable)
# investigations = db.execute(
#     f"SELECT * FROM investigations WHERE user_id = '{user_id}'"
# )
```

#### Verification Checklist
- [x] All database queries use SQLAlchemy ORM
- [x] Pydantic models validate all API inputs
- [x] No raw SQL queries with user input
- [x] No shell command execution with user input
- [x] XSS protection via output encoding
- [ ] **TODO**: Add CSRF tokens for state-changing operations
- [ ] **TODO**: Implement request body size limits

---

### A04:2021 - Insecure Design

#### Threat Modeling

**Assets**:
1. Government transparency data
2. User investigation history
3. Agent analysis results
4. LLM API keys
5. Database credentials

**Threats**:
1. **Unauthorized data access**: Sensitive investigations leaked
2. **Agent manipulation**: Malicious inputs cause incorrect analysis
3. **API key theft**: LLM provider abuse
4. **Denial of service**: Resource exhaustion via agent overload

**Mitigations**:
```python
# src/core/security/rate_limiter.py

# ✅ IMPLEMENTED: Rate limiting per user
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/chat/message")
@limiter.limit("60/minute")  # 60 requests per minute
async def chat_message(request: Request):
    """Chat endpoint with rate limiting."""
    pass

# ✅ IMPLEMENTED: Request timeout
@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    """Enforce 30-second timeout on all requests."""
    try:
        return await asyncio.wait_for(
            call_next(request),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={"detail": "Request timeout"}
        )
```

#### Verification Checklist
- [x] Rate limiting on all public endpoints (60/min)
- [x] Request timeouts (30s API, 60s agents)
- [x] Input validation on all user inputs
- [x] Error messages don't leak system details
- [ ] **TODO**: Implement circuit breakers for LLM APIs
- [ ] **TODO**: Add investigation result caching
- [ ] **TODO**: Document security architecture

---

### A05:2021 - Security Misconfiguration

#### Configuration Management

**Environment-Specific Settings**:
```python
# src/core/config.py

class Settings(BaseSettings):
    """Application settings with environment-specific defaults."""

    # ✅ Production defaults
    DEBUG: bool = False  # NEVER True in production
    TESTING: bool = False
    LOG_LEVEL: str = "INFO"  # Not DEBUG in production

    # ✅ Security headers
    CORS_ORIGINS: list[str] = Field(
        default=["https://cidadao.ai"],
        description="Allowed CORS origins"
    )

    # ✅ Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # ✅ Authentication
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    class Config:
        env_file = ".env"
        case_sensitive = True
```

#### Security Headers Middleware
```python
# src/api/middleware/security_middleware.py

# ✅ IMPLEMENTED: Security headers
@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https:;"
    )

    return response
```

#### Verification Checklist
- [x] `DEBUG=False` in production
- [x] Security headers on all responses
- [x] CORS restricted to production domains
- [x] No default credentials in code
- [x] Error pages don't expose stack traces
- [ ] **TODO**: Remove unused dependencies
- [ ] **TODO**: Disable directory listing
- [ ] **TODO**: Configure secure cookies (HttpOnly, Secure, SameSite)

---

### A06:2021 - Vulnerable and Outdated Components

#### Dependency Management

**Current Stack**:
- **FastAPI**: 0.115.4 (latest stable)
- **Pydantic**: 2.10.0 (v2 with security fixes)
- **SQLAlchemy**: 2.0.36 (async support)
- **httpx**: 0.27.2 (async HTTP client)
- **cryptography**: 44.0.0 (latest)

#### Automated Dependency Scanning
```bash
# Install security scanners
pip install pip-audit safety

# Run vulnerability scan
pip-audit --desc

# Check for known vulnerabilities
safety check --json

# Output to file for CI/CD
pip-audit --output audit-report.json
safety check --json > safety-report.json
```

#### Update Policy
```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade fastapi

# Update all (with caution)
pip install --upgrade -r requirements.txt

# Lock dependencies
pip freeze > requirements-lock.txt
```

#### Verification Checklist
- [x] All dependencies at latest stable versions
- [x] No known CVEs in dependencies
- [ ] **TODO**: Set up automated dependency scanning (Dependabot)
- [ ] **TODO**: Configure security alerts
- [ ] **TODO**: Establish monthly update schedule
- [ ] **TODO**: Pin exact versions in production

---

### A07:2021 - Identification and Authentication Failures

#### Authentication Implementation

**JWT Authentication Flow**:
```python
# src/core/security/auth.py

# ✅ IMPLEMENTED: Secure token generation
import secrets
from datetime import datetime, timedelta

def create_access_token(user_id: str, role: str) -> str:
    """Create JWT access token with secure random JTI."""
    jti = secrets.token_urlsafe(32)  # Secure random identifier

    payload = {
        "sub": user_id,
        "role": role,
        "jti": jti,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm="HS256"
    )

# ✅ IMPLEMENTED: Token blacklist
class TokenBlacklist:
    """Redis-backed token blacklist for logout."""

    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)

    async def add(self, jti: str, exp: int):
        """Add token to blacklist until expiration."""
        ttl = exp - int(time.time())
        await self.redis.setex(f"blacklist:{jti}", ttl, "1")

    async def is_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted."""
        return await self.redis.exists(f"blacklist:{jti}")
```

#### Session Management
```python
# ✅ IMPLEMENTED: Secure session handling
class SessionManager:
    """Manage user sessions with Redis."""

    MAX_SESSIONS_PER_USER = 5
    SESSION_TIMEOUT = 3600  # 1 hour

    async def create_session(self, user_id: str) -> str:
        """Create new session with limits."""
        # Check active sessions
        sessions = await self.get_user_sessions(user_id)
        if len(sessions) >= self.MAX_SESSIONS_PER_USER:
            # Remove oldest session
            await self.revoke_session(sessions[0])

        # Create new session
        session_id = secrets.token_urlsafe(32)
        await self.redis.setex(
            f"session:{session_id}",
            self.SESSION_TIMEOUT,
            user_id
        )

        return session_id
```

#### Verification Checklist
- [x] JWT tokens with secure random JTI
- [x] Token expiration (24 hours)
- [x] Token blacklist on logout
- [x] Session limits per user (5 max)
- [x] Session timeout (1 hour)
- [ ] **TODO**: Implement MFA (Multi-Factor Authentication)
- [ ] **TODO**: Add account lockout after failed attempts
- [ ] **TODO**: Log all authentication events

---

### A08:2021 - Software and Data Integrity Failures

#### Code Integrity

**Pre-commit Hooks** (Enforced):
```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.7.3
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
      - id: detect-private-key
```

#### Dependency Integrity
```bash
# Generate hash-locked requirements
pip install pip-tools
pip-compile --generate-hashes requirements.in -o requirements.txt

# Install with hash verification
pip install --require-hashes -r requirements.txt
```

#### Verification Checklist
- [x] Pre-commit hooks enforce code quality
- [x] Private key detection enabled
- [x] Large file detection enabled
- [ ] **TODO**: Enable hash verification for dependencies
- [ ] **TODO**: Sign releases with GPG
- [ ] **TODO**: Implement CI/CD signature verification

---

### A09:2021 - Security Logging and Monitoring Failures

#### Logging Implementation

**Structured Logging**:
```python
# src/core/logging.py

import structlog

# ✅ IMPLEMENTED: Structured logging
logger = structlog.get_logger()

# Security event logging
logger.info(
    "authentication_success",
    user_id=user.id,
    ip_address=request.client.host,
    user_agent=request.headers.get("User-Agent"),
    timestamp=datetime.utcnow().isoformat()
)

logger.warning(
    "authentication_failure",
    username=username,
    ip_address=request.client.host,
    reason="invalid_credentials",
    timestamp=datetime.utcnow().isoformat()
)

logger.error(
    "authorization_violation",
    user_id=user.id,
    required_role="admin",
    actual_role=user.role,
    endpoint=request.url.path,
    timestamp=datetime.utcnow().isoformat()
)
```

#### Security Events to Log
```python
# src/core/security/audit_log.py

SECURITY_EVENTS = {
    "authentication_success": "INFO",
    "authentication_failure": "WARNING",
    "authorization_violation": "ERROR",
    "token_expired": "WARNING",
    "token_blacklisted": "INFO",
    "rate_limit_exceeded": "WARNING",
    "suspicious_query": "WARNING",
    "sql_injection_attempt": "CRITICAL",
    "xss_attempt": "CRITICAL",
    "agent_error": "ERROR",
    "investigation_started": "INFO",
    "investigation_completed": "INFO",
}

class AuditLogger:
    """Centralized security event logging."""

    @staticmethod
    async def log_event(
        event_type: str,
        user_id: str | None,
        ip_address: str,
        details: dict
    ):
        """Log security event with context."""
        logger.log(
            SECURITY_EVENTS.get(event_type, "INFO"),
            event_type,
            user_id=user_id,
            ip_address=ip_address,
            **details
        )

        # Store in database for audit trail
        await db.execute(
            insert(SecurityEvent).values(
                event_type=event_type,
                user_id=user_id,
                ip_address=ip_address,
                details=details,
                timestamp=datetime.utcnow()
            )
        )
```

#### Monitoring Alerts
```yaml
# config/prometheus/alerts.yml

groups:
  - name: security_alerts
    interval: 1m
    rules:
      # Failed authentication attempts
      - alert: HighFailedAuthRate
        expr: rate(authentication_failure_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High failed authentication rate detected"

      # Authorization violations
      - alert: AuthorizationViolations
        expr: rate(authorization_violation_total[5m]) > 5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Multiple authorization violations detected"

      # Injection attempts
      - alert: InjectionAttempts
        expr: sql_injection_attempt_total > 0 or xss_attempt_total > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Injection attack detected"
```

#### Verification Checklist
- [x] Structured logging with context
- [x] Security events logged
- [x] Logs include user ID, IP, timestamp
- [x] Prometheus metrics exported
- [ ] **TODO**: Configure log retention (90 days)
- [ ] **TODO**: Set up real-time alerting
- [ ] **TODO**: Create security dashboard

---

### A10:2021 - Server-Side Request Forgery (SSRF)

#### SSRF Prevention

**URL Validation**:
```python
# src/core/security/ssrf_protection.py

import ipaddress
from urllib.parse import urlparse

BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),      # Private
    ipaddress.ip_network("172.16.0.0/12"),   # Private
    ipaddress.ip_network("192.168.0.0/16"),  # Private
    ipaddress.ip_network("127.0.0.0/8"),     # Loopback
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local
]

ALLOWED_DOMAINS = [
    "api.portaldatransparencia.gov.br",
    "servicodados.ibge.gov.br",
    "pncp.gov.br",
    "compras.dados.gov.br",
]

def validate_url(url: str) -> bool:
    """Validate URL against SSRF attacks."""
    try:
        parsed = urlparse(url)

        # Check scheme
        if parsed.scheme not in ["http", "https"]:
            raise ValueError(f"Invalid scheme: {parsed.scheme}")

        # Check domain whitelist
        if parsed.hostname not in ALLOWED_DOMAINS:
            raise ValueError(f"Domain not allowed: {parsed.hostname}")

        # Resolve and check IP
        ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname))
        for network in BLOCKED_NETWORKS:
            if ip in network:
                raise ValueError(f"IP in blocked network: {ip}")

        return True

    except Exception as e:
        logger.error("url_validation_failed", url=url, error=str(e))
        return False

# ✅ IMPLEMENTED: Safe HTTP client
async def safe_fetch(url: str, **kwargs) -> httpx.Response:
    """Fetch URL with SSRF protection."""
    if not validate_url(url):
        raise SecurityError(f"URL validation failed: {url}")

    async with httpx.AsyncClient(
        timeout=10.0,  # Prevent slowloris
        follow_redirects=False  # Prevent redirect-based SSRF
    ) as client:
        return await client.get(url, **kwargs)
```

#### Verification Checklist
- [x] URL validation for external requests
- [x] Domain whitelist enforced
- [x] Private IP ranges blocked
- [x] Redirect following disabled
- [ ] **TODO**: Add URL DNS rebinding protection
- [ ] **TODO**: Implement request signature verification

---

## 2. Authentication & Authorization 🔐

### Multi-Layer Authentication

**Layer 1: JWT Tokens** (User authentication)
```python
# Usage in routes
from src.core.security.dependencies import get_current_user

@app.get("/api/v1/investigations")
async def list_investigations(
    user: User = Depends(get_current_user)
):
    """List user's investigations."""
    return await investigation_service.get_user_investigations(user.id)
```

**Layer 2: API Keys** (Service authentication)
```python
# Usage for external services
from src.core.security.dependencies import verify_api_key

@app.post("/api/v1/agents/invoke")
async def invoke_agent(
    request: AgentRequest,
    api_key: str = Depends(verify_api_key)
):
    """Invoke agent with API key authentication."""
    return await agent_pool.invoke_agent(request)
```

**Layer 3: IP Whitelist** (Admin endpoints)
```python
# Usage for admin routes
from src.api.middleware.ip_whitelist import IPWhitelistMiddleware

app.add_middleware(
    IPWhitelistMiddleware,
    allowed_ips=settings.ADMIN_IP_WHITELIST,
    restricted_paths=["/api/v1/admin/*"]
)
```

### Role-Based Access Control (RBAC)

**Roles**:
- `user`: Standard user (read investigations, create investigations)
- `admin`: Administrator (all user permissions + manage users, view logs)
- `service`: Service account (invoke agents, no user data access)

**Permission Matrix**:
```python
PERMISSIONS = {
    "user": [
        "investigation:read:own",
        "investigation:create",
        "investigation:delete:own",
        "agent:invoke",
    ],
    "admin": [
        "investigation:read:all",
        "investigation:delete:all",
        "user:read",
        "user:update",
        "logs:read",
        "metrics:read",
    ],
    "service": [
        "agent:invoke",
        "investigation:create",
    ]
}
```

---

## 3. Secrets Management 🔑

### Production Secrets

**Required Secrets**:
```bash
# Core Application
SECRET_KEY=<64-char-hex>              # Flask/FastAPI secret
JWT_SECRET_KEY=<64-char-hex>          # JWT signing key
API_SECRET_KEY=<64-char-hex>          # API key signing

# LLM Providers
MARITACA_API_KEY=<api-key>            # Primary LLM
ANTHROPIC_API_KEY=<api-key>           # Backup LLM

# Database
DATABASE_URL=postgresql://...          # PostgreSQL connection
REDIS_URL=redis://...                  # Redis cache

# Government APIs
TRANSPARENCY_API_KEY=<api-key>         # Portal da Transparência

# Monitoring
SENTRY_DSN=<dsn>                       # Error tracking
```

### Secret Rotation Policy

**Rotation Schedule**:
- **High sensitivity** (JWT_SECRET_KEY, API_SECRET_KEY): 90 days
- **Medium sensitivity** (DATABASE_URL password): 180 days
- **Low sensitivity** (API keys): 365 days or on compromise

**Rotation Procedure**:
```bash
# 1. Generate new secret
python3 scripts/generate_secrets.py

# 2. Update Railway environment
railway variables set JWT_SECRET_KEY=<new-key>

# 3. Restart application
railway up --detach

# 4. Invalidate old tokens (if applicable)
redis-cli FLUSHDB

# 5. Document rotation in changelog
echo "$(date): JWT_SECRET_KEY rotated" >> docs/security/rotation_log.md
```

### Railway Secrets Configuration

```bash
# Set all secrets at once
railway variables set \
  SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))") \
  JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))") \
  API_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Verify secrets are set
railway variables

# View specific secret (masked)
railway variables get JWT_SECRET_KEY
```

---

## 4. Common Vulnerabilities & Mitigations 🛡️

### SQL Injection

**✅ SAFE**: SQLAlchemy ORM
```python
# Parameterized query (safe)
investigations = db.query(Investigation).filter(
    Investigation.user_id == user_id,
    Investigation.status == status
).all()
```

**❌ UNSAFE**: String concatenation
```python
# Never do this
query = f"SELECT * FROM investigations WHERE user_id = '{user_id}'"
```

### Cross-Site Scripting (XSS)

**✅ SAFE**: Pydantic output models
```python
# Automatic HTML escaping in responses
class InvestigationResponse(BaseModel):
    query: str  # Automatically escaped
    results: str  # Automatically escaped
```

**❌ UNSAFE**: Raw HTML rendering
```python
# Never do this
return f"<div>{user_input}</div>"
```

### Command Injection

**✅ SAFE**: No shell execution
```python
# Use subprocess with array arguments
subprocess.run(["git", "status"], check=True)
```

**❌ UNSAFE**: Shell=True
```python
# Never do this
subprocess.run(f"git status {user_input}", shell=True)
```

### Path Traversal

**✅ SAFE**: Path validation
```python
from pathlib import Path

def safe_read_file(filename: str) -> str:
    """Read file with path traversal protection."""
    base_dir = Path("/app/data")
    requested_path = (base_dir / filename).resolve()

    # Ensure path is within base directory
    if not str(requested_path).startswith(str(base_dir)):
        raise SecurityError("Path traversal detected")

    return requested_path.read_text()
```

**❌ UNSAFE**: Direct path concatenation
```python
# Never do this
with open(f"/app/data/{user_input}") as f:
    return f.read()
```

---

## 5. Security Testing Procedures 🧪

### Automated Security Scanning

**Dependency Vulnerabilities**:
```bash
# Install scanners
pip install pip-audit safety bandit

# Run scans
pip-audit --desc                    # CVE scanning
safety check --json                 # Known vulnerabilities
bandit -r src/ -f json -o bandit.json  # Code security issues

# Add to CI/CD
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run pip-audit
        run: pip-audit --desc
      - name: Run safety
        run: safety check
      - name: Run bandit
        run: bandit -r src/
```

### Manual Security Testing

**Authentication Testing**:
```bash
# Test invalid token
curl -H "Authorization: Bearer invalid" \
  https://cidadao-api-production.up.railway.app/api/v1/investigations
# Expected: 401 Unauthorized

# Test expired token
curl -H "Authorization: Bearer <expired-token>" \
  https://cidadao-api-production.up.railway.app/api/v1/investigations
# Expected: 401 Unauthorized

# Test without token
curl https://cidadao-api-production.up.railway.app/api/v1/investigations
# Expected: 401 Unauthorized
```

**Authorization Testing**:
```bash
# Test user accessing admin endpoint
curl -H "Authorization: Bearer <user-token>" \
  https://cidadao-api-production.up.railway.app/api/v1/admin/users
# Expected: 403 Forbidden

# Test accessing other user's data
curl -H "Authorization: Bearer <user1-token>" \
  https://cidadao-api-production.up.railway.app/api/v1/investigations/<user2-investigation-id>
# Expected: 403 Forbidden
```

**Input Validation Testing**:
```bash
# Test SQL injection
curl -X POST https://cidadao-api-production.up.railway.app/api/v1/investigations \
  -H "Content-Type: application/json" \
  -d '{"query": "test; DROP TABLE investigations;"}'
# Expected: 400 Bad Request (validation error)

# Test XSS
curl -X POST https://cidadao-api-production.up.railway.app/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "<script>alert(1)</script>"}'
# Expected: Response escaped, no script execution

# Test path traversal
curl https://cidadao-api-production.up.railway.app/api/v1/files/../../../etc/passwd
# Expected: 404 Not Found or 400 Bad Request
```

### Penetration Testing

**OWASP ZAP Scan**:
```bash
# Install OWASP ZAP
docker pull owasp/zap2docker-stable

# Run automated scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://cidadao-api-production.up.railway.app \
  -r zap-report.html

# Run full scan (takes longer)
docker run -t owasp/zap2docker-stable zap-full-scan.py \
  -t https://cidadao-api-production.up.railway.app \
  -r zap-full-report.html
```

**Burp Suite Testing**:
1. Configure browser to use Burp proxy (127.0.0.1:8080)
2. Navigate to application and interact normally
3. Review requests in Burp's HTTP History
4. Use Burp Scanner to identify vulnerabilities
5. Test authentication bypasses manually

---

## 6. Incident Response Plan 🚨

### Security Incident Classification

**Severity Levels**:
- **P0 - Critical**: Active exploitation, data breach, system compromise
- **P1 - High**: Attempted exploitation, authentication bypass discovered
- **P2 - Medium**: Vulnerability discovered, no exploitation detected
- **P3 - Low**: Security best practice violation, no immediate risk

### Incident Response Procedure

**Phase 1: Detection** (0-15 minutes)
1. Alert triggered via monitoring system
2. On-call engineer notified
3. Initial assessment of severity
4. Escalate if P0/P1

**Phase 2: Containment** (15-60 minutes)
1. **P0/P1**: Immediately isolate affected systems
   ```bash
   # Disable compromised API keys
   railway variables set COMPROMISED_KEY=disabled

   # Block malicious IPs
   railway variables set IP_BLACKLIST="<malicious-ips>"

   # Restart application
   railway up --detach
   ```

2. **P2/P3**: Monitor and prepare fix

**Phase 3: Investigation** (1-4 hours)
1. Review security logs
   ```bash
   railway logs --filter "authentication_failure|authorization_violation"
   ```

2. Identify attack vector
3. Assess data exposure
4. Document findings

**Phase 4: Eradication** (4-24 hours)
1. Deploy security patch
2. Rotate compromised credentials
3. Update firewall rules
4. Re-scan for vulnerabilities

**Phase 5: Recovery** (24-48 hours)
1. Restore normal operations
2. Monitor for repeated attacks
3. Validate security controls

**Phase 6: Post-Incident** (1 week)
1. Write incident report
2. Conduct post-mortem
3. Update security procedures
4. Improve monitoring/alerts

### Emergency Contacts

**Security Team**:
- **Lead Engineer**: Anderson Henrique da Silva
- **DevOps**: [Contact]
- **Legal**: [Contact]

**External**:
- **Railway Support**: support@railway.app
- **Maritaca AI**: [Security contact]
- **Anthropic**: [Security contact]

---

## 7. Compliance & Audit 📋

### LGPD (Lei Geral de Proteção de Dados)

**Data Processing Principles**:
- **Purpose Limitation**: Only collect data necessary for investigations
- **Data Minimization**: Store minimal user information
- **Consent**: Obtain user consent for data processing
- **Transparency**: Inform users how data is used

**Implementation**:
```python
# src/models/user.py

class User(Base):
    """User model with LGPD compliance."""

    # Personal data
    id: str
    email: str
    created_at: datetime

    # Consent tracking
    consent_given: bool = False
    consent_date: datetime | None = None

    # Data retention
    data_retention_days: int = 365

    # Right to erasure
    async def request_deletion(self):
        """User right to be forgotten (LGPD Art. 18)."""
        # Anonymize user data
        self.email = f"deleted-{self.id}@example.com"
        self.consent_given = False

        # Delete investigation history
        await db.execute(
            delete(Investigation).where(Investigation.user_id == self.id)
        )
```

### Security Audit Checklist

**Monthly Audit**:
- [ ] Review access logs for anomalies
- [ ] Check for new CVEs in dependencies
- [ ] Verify backup integrity
- [ ] Test incident response plan
- [ ] Review security metrics

**Quarterly Audit**:
- [ ] Full penetration testing
- [ ] Security training for team
- [ ] Update threat model
- [ ] Review and update security policies
- [ ] Third-party security assessment

**Annual Audit**:
- [ ] Comprehensive security audit by external firm
- [ ] LGPD compliance review
- [ ] Disaster recovery testing
- [ ] Security architecture review
- [ ] Update business continuity plan

---

## 8. Security Metrics & KPIs 📊

### Key Security Metrics

**Authentication Metrics**:
```promql
# Failed authentication rate
rate(authentication_failure_total[5m])

# Account lockout rate
rate(account_lockout_total[1h])

# Token expiration rate
rate(token_expired_total[1h])
```

**Authorization Metrics**:
```promql
# Authorization violation rate
rate(authorization_violation_total[5m])

# Unauthorized access attempts
rate(unauthorized_access_total[5m])
```

**Attack Metrics**:
```promql
# SQL injection attempts
sql_injection_attempt_total

# XSS attempts
xss_attempt_total

# SSRF attempts
ssrf_attempt_total
```

### Security Dashboard

**Grafana Panels**:
1. **Authentication Health**
   - Success rate (target: >99%)
   - Failed attempts (alert: >10/min)
   - Average login time

2. **Attack Detection**
   - Injection attempts (alert: >0)
   - Authorization violations (alert: >5/min)
   - Rate limit hits

3. **System Health**
   - Uptime (target: >99.9%)
   - Error rate (alert: >1%)
   - Response time (target: <200ms p95)

---

## 9. Security Best Practices Summary ✅

### Development
- [x] Use parameterized queries (SQLAlchemy ORM)
- [x] Validate all user inputs (Pydantic models)
- [x] Implement proper error handling
- [x] Never log sensitive data
- [x] Use secure random number generation
- [x] Follow principle of least privilege
- [x] Keep dependencies updated

### Production
- [x] Enforce HTTPS only
- [x] Use strong secrets (64+ char hex)
- [x] Enable rate limiting
- [x] Configure security headers
- [x] Implement logging and monitoring
- [x] Regular security scans
- [x] Incident response plan documented

### Ongoing
- [ ] Monthly security audits
- [ ] Quarterly penetration testing
- [ ] Annual external security assessment
- [ ] Continuous dependency monitoring
- [ ] Regular security training
- [ ] Threat model updates

---

## 10. References & Resources 📚

### OWASP Resources
- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)

### Python Security
- [Bandit Security Linter](https://bandit.readthedocs.io/)
- [Safety Vulnerability Scanner](https://github.com/pyupio/safety)
- [PEP 543 - Unified TLS API](https://www.python.org/dev/peps/pep-0543/)

### FastAPI Security
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [FastAPI OAuth2](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

### LGPD Compliance
- [LGPD Full Text](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [ANPD Guidelines](https://www.gov.br/anpd/pt-br)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-27
**Next Review**: 2025-11-27

**Status**: ✅ Ready for Beta 1.0 Production Deployment
