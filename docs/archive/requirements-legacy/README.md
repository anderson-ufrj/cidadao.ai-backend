# 📦 Requirements Files

This directory contains organized Python dependencies for different environments.

## Files Overview

| File | Purpose | Usage |
|------|---------|-------|
| `base.txt` | Core dependencies | Base requirements for all environments |
| `production.txt` | Production extras | Additional deps for Railway/production |
| `dev.txt` | Development tools | Testing, linting, formatting tools |
| `hf.txt` | HuggingFace Spaces | **DEPRECATED** - HF-specific deps |
| `hf-deprecated.txt` | HF full deps | **DEPRECATED** - Archive |

## Installation

### Railway Production (Recommended)

```bash
# Railway uses root requirements.txt
pip install -r requirements.txt
```

### Local Development

```bash
# Full development environment
pip install -r requirements.txt
pip install -r requirements/dev.txt

# Or use Make
make install-dev
```

### Base Dependencies Only

```bash
pip install -r requirements/base.txt
```

## Root requirements.txt

The **root `requirements.txt`** is the **primary production file** used by Railway.

It includes all necessary dependencies for:
- FastAPI application
- Celery Worker + Beat
- Redis integration
- Supabase connectivity
- Multi-agent system
- LLM integrations (Groq, OpenAI)

## Deprecated Files

### HuggingFace Files (No Longer Used)

- `hf.txt` - HuggingFace Spaces minimal deps
- `hf-deprecated.txt` - HF full dependencies

**Reason for deprecation**: Migrated to Railway on 2025-10-07.

See: [Migration Documentation](../docs/deployment/migration-hf-to-railway.md)

## Maintenance

### Adding a New Dependency

1. **For production**: Add to root `requirements.txt`
2. **For base**: Add to `requirements/base.txt`
3. **For dev only**: Add to `requirements/dev.txt`

### Updating Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update requirements
pip freeze > requirements.txt

# Test installation
pip install -r requirements.txt --dry-run
```

## Dependencies by Category

### Core API (base.txt)
- FastAPI, Uvicorn
- Pydantic, Pydantic-settings
- HTTPx (async HTTP)
- Redis, PostgreSQL drivers

### Background Tasks (production.txt)
- Celery
- Redis (broker + backend)
- Kombu (messaging)

### LLM & Agents (production.txt)
- LangChain
- Groq SDK
- OpenAI SDK

### Development (dev.txt)
- pytest, pytest-asyncio
- black, ruff, mypy
- coverage
- pre-commit

## Notes

- **DO NOT** modify `hf*.txt` files (deprecated)
- Always test locally before updating production
- Keep `requirements.txt` synchronized with Railway deployment
- Document breaking changes in CHANGELOG.md
