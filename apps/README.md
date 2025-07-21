# Backend Applications

This directory contains application entry points for the Cidadão.AI backend.

## Files

- `api_app.py.backup` - Original Gradio interface (backup)

## Current Setup

The backend now runs as a pure FastAPI REST API without Gradio interface.
The main entry point is `/app.py` in the root directory.

## API Documentation

When the server is running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json