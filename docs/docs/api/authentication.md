---
title: "Authentication"
sidebar_position: 2
description: "Comprehensive guide to API authentication, authorization, and security"
---

# Authentication

## Overview

The Cidadão.AI API implements a **multi-layered authentication system** based on industry standards, providing secure access control through JWT tokens, OAuth 2.0 integration, and role-based permissions.

## Authentication Methods

### 1. JWT Authentication (Primary)

The API uses **JSON Web Tokens (JWT)** as the primary authentication mechanism, following RFC 7519 specifications.

#### Token Structure

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "2024-01-key"
  },
  "payload": {
    "sub": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "role": "user",
    "permissions": ["read:investigations", "write:reports"],
    "iat": 1706616000,
    "exp": 1706616900,
    "jti": "unique-token-id"
  },
  "signature": "..."
}
```

#### Token Lifecycle

```mermaid
graph LR
    Login[Login] --> Access[Access Token<br/>15 minutes]
    Login --> Refresh[Refresh Token<br/>7 days]
    Access --> API[API Requests]
    Access -.->|Expires| Renew[Token Renewal]
    Refresh --> Renew
    Renew --> Access
```

### 2. OAuth 2.0 Integration

Support for third-party authentication providers:

- **Google** (OpenID Connect)
- **GitHub** (OAuth 2.0)
- **Microsoft** (Azure AD)
- **Custom SAML/OIDC** providers

#### OAuth Flow

```mermaid
sequenceDiagram
    participant User
    participant App
    participant API
    participant OAuth
    
    User->>App: Click "Login with Google"
    App->>API: GET /auth/oauth/google/authorize
    API-->>App: Authorization URL
    App->>OAuth: Redirect to Google
    User->>OAuth: Approve permissions
    OAuth->>App: Redirect with code
    App->>API: GET /auth/oauth/google/callback?code=...
    API->>OAuth: Exchange code for token
    OAuth-->>API: User info
    API-->>App: JWT tokens
```

### 3. API Key Authentication (Legacy)

For backwards compatibility and service-to-service communication:

```http
X-API-Key: sk_live_50e8400-e29b-41d4-a716-446655440000
```

## Authentication Endpoints

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure-password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "role": "user",
    "permissions": ["read:investigations", "write:reports"]
  }
}
```

### Token Refresh

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

### User Registration

```http
POST /api/v1/auth/register
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "secure-password",
  "role": "analyst"
}
```

### Change Password

```http
POST /api/v1/auth/change-password
Authorization: Bearer {token}
Content-Type: application/json

{
  "current_password": "old-password",
  "new_password": "new-secure-password"
}
```

## Authorization

### Role-Based Access Control (RBAC)

| Role | Description | Permissions |
|------|-------------|-------------|
| `admin` | System administrator | Full access to all resources |
| `analyst` | Data analyst | Create investigations, analyses, reports |
| `viewer` | Read-only user | View public investigations and reports |
| `service` | Service account | API access for integrations |

### Permission Model

```python
class Permission(Enum):
    # Investigations
    READ_INVESTIGATIONS = "read:investigations"
    WRITE_INVESTIGATIONS = "write:investigations"
    DELETE_INVESTIGATIONS = "delete:investigations"
    
    # Analyses
    READ_ANALYSES = "read:analyses"
    WRITE_ANALYSES = "write:analyses"
    
    # Reports
    READ_REPORTS = "read:reports"
    WRITE_REPORTS = "write:reports"
    
    # Admin
    MANAGE_USERS = "manage:users"
    VIEW_AUDIT_LOGS = "view:audit"
    CONFIGURE_SYSTEM = "configure:system"
```

### Resource-Level Permissions

```python
# Check ownership
if investigation.user_id != current_user.id and not current_user.is_admin:
    raise ForbiddenError("You don't have permission to access this resource")

# Check team access
if investigation.team_id not in current_user.team_ids:
    raise ForbiddenError("This resource belongs to another team")
```

## Security Headers

### Request Headers

```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Client-Version: 1.0.0
```

### Response Headers

```http
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
```

## Token Management

### Token Storage (Client-side)

```javascript
// Secure storage recommendations
class TokenManager {
  // Store in memory for web apps
  private accessToken: string;
  
  // Store in secure storage for mobile
  async storeRefreshToken(token: string) {
    await SecureStore.setItemAsync('refresh_token', token);
  }
  
  // Never store in localStorage for sensitive apps
  // Use httpOnly cookies when possible
}
```

### Token Validation

```python
def validate_token(token: str) -> TokenPayload:
    try:
        # Verify signature
        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            options={"verify_exp": True}
        )
        
        # Check additional claims
        if payload.get("iss") != "https://api.cidadao.ai":
            raise InvalidTokenError("Invalid issuer")
            
        # Verify token not revoked
        if is_token_revoked(payload["jti"]):
            raise InvalidTokenError("Token has been revoked")
            
        return TokenPayload(**payload)
        
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise InvalidTokenError(f"Invalid token: {str(e)}")
```

## Multi-Factor Authentication (MFA)

### TOTP Setup

```http
POST /api/v1/auth/mfa/setup
Authorization: Bearer {token}

Response:
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,...",
  "backup_codes": [
    "12345678",
    "87654321",
    ...
  ]
}
```

### MFA Verification

```http
POST /api/v1/auth/mfa/verify
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password",
  "totp_code": "123456"
}
```

## Session Management

### Session Configuration

```python
SESSION_CONFIG = {
    "access_token_expire": timedelta(minutes=15),
    "refresh_token_expire": timedelta(days=7),
    "max_refresh_count": 5,
    "concurrent_sessions": 3,
    "idle_timeout": timedelta(hours=2)
}
```

### Active Session Monitoring

```http
GET /api/v1/auth/sessions
Authorization: Bearer {token}

Response:
{
  "sessions": [
    {
      "id": "session-1",
      "device": "Chrome on Windows",
      "ip_address": "192.168.1.1",
      "location": "São Paulo, BR",
      "last_active": "2025-01-30T10:15:30Z",
      "current": true
    }
  ]
}
```

## Security Best Practices

### 1. Token Security

```python
# Use secure random generation
def generate_token_id():
    return secrets.token_urlsafe(32)

# Implement token rotation
def rotate_refresh_token(old_token: str) -> tuple[str, str]:
    # Validate old token
    payload = validate_token(old_token)
    
    # Generate new tokens
    new_access = create_access_token(payload.sub)
    new_refresh = create_refresh_token(payload.sub)
    
    # Revoke old refresh token
    revoke_token(old_token)
    
    return new_access, new_refresh
```

### 2. Rate Limiting

```python
# Implement progressive delays for failed attempts
LOGIN_ATTEMPTS = {
    1: 0,      # No delay
    2: 1,      # 1 second
    3: 5,      # 5 seconds
    4: 15,     # 15 seconds
    5: 60,     # 1 minute
    6: 300     # 5 minutes (lockout)
}
```

### 3. Audit Logging

```python
@audit_log(AuditEventType.AUTHENTICATION_SUCCESS)
async def login(credentials: LoginRequest) -> LoginResponse:
    # Authentication logic
    pass

@audit_log(AuditEventType.UNAUTHORIZED_ACCESS)
async def handle_unauthorized(request: Request):
    # Log unauthorized attempts
    pass
```

## OAuth Configuration

### Provider Setup

```python
OAUTH_PROVIDERS = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scope": ["openid", "email", "profile"]
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "scope": ["user:email"]
    }
}
```

### User Approval Flow

```mermaid
stateDiagram-v2
    [*] --> OAuthLogin
    OAuthLogin --> PendingApproval
    PendingApproval --> AdminReview
    AdminReview --> Approved: Admin approves
    AdminReview --> Rejected: Admin rejects
    Approved --> ActiveUser
    Rejected --> [*]
```

## Error Handling

### Authentication Errors

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| `INVALID_CREDENTIALS` | Wrong email/password | 401 |
| `TOKEN_EXPIRED` | Access token expired | 401 |
| `TOKEN_INVALID` | Malformed or tampered token | 401 |
| `INSUFFICIENT_PERMISSIONS` | Lacks required permissions | 403 |
| `ACCOUNT_LOCKED` | Too many failed attempts | 423 |
| `MFA_REQUIRED` | Must provide MFA code | 428 |

### Error Response Example

```json
{
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "Access token has expired",
    "details": {
      "expired_at": "2025-01-30T10:15:30Z",
      "refresh_token_valid": true
    },
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

## Testing Authentication

### Integration Tests

```python
async def test_full_authentication_flow():
    # 1. Register user
    response = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "secure-password"
    })
    assert response.status_code == 201
    
    # 2. Login
    response = await client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "secure-password"
    })
    tokens = response.json()
    
    # 3. Use access token
    response = await client.get(
        "/investigations",
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert response.status_code == 200
    
    # 4. Refresh token
    response = await client.post("/auth/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })
    assert "access_token" in response.json()
```

---

Next: [Endpoints Reference →](./endpoints/index.md)