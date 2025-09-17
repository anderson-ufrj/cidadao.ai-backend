"""FastAPI-based REST API for Cidadao.AI.

This module provides a comprehensive REST API for the multi-agent transparency
platform, featuring enterprise-grade security, comprehensive monitoring,
and Brazilian-themed documentation.

Key Features:
- FastAPI with async/await throughout
- Multi-layer security (JWT + OAuth2 + API Keys)
- Custom OpenAPI documentation with Brazilian theme
- Comprehensive audit logging
- Rate limiting and DDoS protection
- Prometheus metrics integration
- Health checks and monitoring endpoints

Main Components:
- app: Main FastAPI application with lifespan management
- routes: All API route handlers organized by domain
- middleware: Security, logging, and monitoring middleware
- auth: Authentication and authorization systems
- models: Pydantic models for request/response validation

Usage:
    from src.api import create_app, get_api_router
    
    app = create_app()
    router = get_api_router()

Status: Production-ready with comprehensive enterprise features.
"""

from src.api.app import app

# Key exports for application setup
__all__ = [
    "app",
]