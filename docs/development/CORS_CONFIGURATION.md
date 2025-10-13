# CORS Configuration Guide

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

## Overview

The Cidadão.AI backend uses an enhanced CORS (Cross-Origin Resource Sharing) middleware specifically optimized for integration with Vercel-deployed frontends and other modern deployment platforms.

## Features

- ✅ **Dynamic Origin Validation**: Supports wildcard patterns for Vercel preview deployments
- ✅ **Credentials Support**: Full support for cookies and authentication tokens
- ✅ **Preflight Optimization**: Efficient handling of OPTIONS requests
- ✅ **Environment Awareness**: Different rules for development/production
- ✅ **Custom Headers**: Support for rate limiting and correlation headers

## Configuration

### Environment Variables

Configure CORS through environment variables or `.env` file:

```bash
# Allowed origins (comma-separated)
CORS_ORIGINS=["https://cidadao-ai-frontend.vercel.app","https://*.vercel.app"]

# Allow credentials (cookies, auth headers)
CORS_ALLOW_CREDENTIALS=true

# Allowed methods
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE","PATCH","OPTIONS","HEAD"]

# Max age for preflight cache (seconds)
CORS_MAX_AGE=86400
```

### Default Configuration

The default configuration in `src/core/config.py` includes:

```python
cors_origins = [
    "http://localhost:3000",          # Local development
    "http://localhost:3001",          # Alternative port
    "http://127.0.0.1:3000",         # IP-based localhost
    "https://cidadao-ai-frontend.vercel.app",  # Production
    "https://cidadao-ai.vercel.app",          # Alternative production
    "https://*.vercel.app",                   # Vercel previews
    "https://*.hf.space"                      # HuggingFace Spaces
]
```

## Vercel Integration

### Preview Deployments

The enhanced CORS middleware automatically allows Vercel preview deployments matching these patterns:

- `https://cidadao-ai-frontend-[hash]-[team].vercel.app`
- `https://cidadao-ai-[hash]-[team].vercel.app`
- `https://[project]-[hash]-[team].vercel.app`

### Production Setup

For production Vercel deployments:

1. Add your production domain to `CORS_ORIGINS`
2. Ensure `CORS_ALLOW_CREDENTIALS=true` for authentication
3. Configure exposed headers for client access

## Testing CORS

### Using the Validator

Run the CORS validator to test your configuration:

```bash
python -m src.utils.cors_validator
```

This will:
- Test all configured origins
- Validate credentials flow
- Generate nginx/CloudFlare configurations

### Manual Testing

Test CORS with curl:

```bash
# Preflight request
curl -X OPTIONS \
  -H "Origin: https://cidadao-ai-frontend.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  http://localhost:8000/api/v1/chat/message

# Actual request
curl -X POST \
  -H "Origin: https://cidadao-ai-frontend.vercel.app" \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}' \
  http://localhost:8000/api/v1/chat/message
```

## Common Issues

### 1. "CORS policy blocked" Error

**Symptoms**: Browser shows CORS error, requests fail

**Solutions**:
- Verify origin is in allowed list
- Check for typos in origin URL
- Ensure protocol matches (http vs https)

### 2. Credentials Not Working

**Symptoms**: Cookies not being set, auth failing

**Solutions**:
- Ensure `CORS_ALLOW_CREDENTIALS=true`
- Frontend must include `credentials: 'include'` in fetch
- Origin cannot be `*` when using credentials

### 3. Preview Deployments Blocked

**Symptoms**: Vercel preview URLs getting CORS errors

**Solutions**:
- Enhanced middleware should handle automatically
- Check regex patterns match your preview URL format
- Verify middleware is properly initialized

## Security Considerations

1. **Never use wildcard (`*`) in production** when credentials are enabled
2. **Validate origins strictly** in production environments
3. **Limit exposed headers** to only what's necessary
4. **Use HTTPS** for all production origins
5. **Implement rate limiting** alongside CORS

## Frontend Configuration

### Next.js (Vercel)

```typescript
// Frontend API client configuration
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,  // Important for cookies
  headers: {
    'Content-Type': 'application/json'
  }
});
```

### React SPA

```javascript
// Fetch with credentials
fetch('https://api.cidadao.ai/endpoint', {
  method: 'POST',
  credentials: 'include',  // Include cookies
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
});
```

## Deployment Configurations

### Nginx

Add to your server block:

```nginx
# Handle preflight
if ($request_method = 'OPTIONS') {
    add_header 'Access-Control-Allow-Origin' '$http_origin' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, PATCH, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With,X-API-Key' always;
    add_header 'Access-Control-Allow-Credentials' 'true' always;
    add_header 'Access-Control-Max-Age' 86400 always;
    return 204;
}
```

### CloudFlare

Create transform rules:

```javascript
// Allow Vercel origins
if (http.request.headers["origin"][0] matches "^https://[a-zA-Z0-9-]+\\.vercel\\.app$") {
  headers["Access-Control-Allow-Origin"] = http.request.headers["origin"][0]
  headers["Access-Control-Allow-Credentials"] = "true"
}
```

## Monitoring

Monitor CORS issues through:

1. **Application logs**: Look for `cors_origin_denied` events
2. **Browser console**: Check for CORS policy errors
3. **Network tab**: Inspect preflight OPTIONS requests
4. **Metrics**: Track failed requests by origin

## Support

For CORS-related issues:

1. Check the [CORS validator output](#testing-cors)
2. Review application logs for denied origins
3. Verify frontend is sending correct headers
4. Contact the platform team if patterns need updating
