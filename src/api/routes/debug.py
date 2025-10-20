"""
Debug routes for diagnosing issues in production.
"""

import importlib
import os
import sys
import traceback
from typing import Any

from fastapi import APIRouter

from src.core import settings

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/drummond-status")
async def drummond_status() -> dict[str, Any]:
    """Check the status of Drummond agent and diagnose import issues."""

    result = {
        "python_version": sys.version,
        "working_dir": os.getcwd(),
        "sys_path": sys.path[:5],  # First 5 paths
        "checks": {},
    }

    # Check 1: Can we import BaseAgent?
    try:
        from src.agents.deodoro import BaseAgent

        result["checks"]["base_agent_import"] = {
            "status": "success",
            "abstract_methods": list(getattr(BaseAgent, "__abstractmethods__", [])),
        }
    except Exception as e:
        result["checks"]["base_agent_import"] = {
            "status": "failed",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }

    # Check 2: Can we import CommunicationAgent?
    try:
        from src.agents.drummond import CommunicationAgent

        abstract_methods = getattr(CommunicationAgent, "__abstractmethods__", set())
        result["checks"]["communication_agent_import"] = {
            "status": "success",
            "type": str(type(CommunicationAgent)),
            "base_classes": [str(base) for base in CommunicationAgent.__bases__],
            "abstract_methods": list(abstract_methods) if abstract_methods else "none",
            "has_shutdown": hasattr(CommunicationAgent, "shutdown"),
            "has_initialize": hasattr(CommunicationAgent, "initialize"),
            "has_process": hasattr(CommunicationAgent, "process"),
        }
    except Exception as e:
        result["checks"]["communication_agent_import"] = {
            "status": "failed",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }

    # Check 3: Can we instantiate?
    try:
        from src.agents.drummond import CommunicationAgent

        agent = CommunicationAgent()
        result["checks"]["instantiation"] = {
            "status": "success",
            "agent_name": agent.name,
        }
    except Exception as e:
        result["checks"]["instantiation"] = {
            "status": "failed",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
        }

    # Check 4: Factory status
    try:
        from src.api.routes.chat_drummond_factory import (
            _import_error,
            _initialized,
            get_drummond_agent,
        )

        agent = await get_drummond_agent()
        result["checks"]["factory"] = {
            "status": "success" if agent else "failed",
            "initialized": _initialized,
            "import_error": _import_error,
            "agent_available": agent is not None,
        }
    except Exception as e:
        result["checks"]["factory"] = {
            "status": "failed",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }

    return result


@router.get("/llm-config")
async def llm_config_status() -> dict[str, Any]:
    """Check LLM configuration and provider status."""

    result = {
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "configuration": {},
        "environment_variables": {},
        "provider_status": {},
    }

    # Check configuration from settings
    result["configuration"] = {
        "llm_provider": settings.llm_provider,
        "llm_model_name": settings.llm_model_name,
        "llm_temperature": settings.llm_temperature,
        "llm_max_tokens": settings.llm_max_tokens,
    }

    # Check environment variables directly
    result["environment_variables"] = {
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER"),
        "MARITACA_API_KEY": (
            "***" + os.getenv("MARITACA_API_KEY", "")[-4:]
            if os.getenv("MARITACA_API_KEY")
            else None
        ),
        "MARITACA_MODEL": os.getenv("MARITACA_MODEL"),
        "GROQ_API_KEY": (
            "***" + os.getenv("GROQ_API_KEY", "")[-4:]
            if os.getenv("GROQ_API_KEY")
            else None
        ),
        "ANTHROPIC_API_KEY": (
            "***" + os.getenv("ANTHROPIC_API_KEY", "")[-4:]
            if os.getenv("ANTHROPIC_API_KEY")
            else None
        ),
    }

    # Check if Maritaca is configured in settings
    result["provider_status"]["maritaca"] = {
        "api_key_configured": bool(settings.maritaca_api_key),
        "model": (
            settings.maritaca_model if hasattr(settings, "maritaca_model") else None
        ),
        "base_url": (
            settings.maritaca_api_base_url
            if hasattr(settings, "maritaca_api_base_url")
            else None
        ),
    }

    # Test LLM provider initialization
    try:
        from src.llm.providers import create_llm_manager

        manager = create_llm_manager(
            primary_provider=settings.llm_provider, enable_fallback=False
        )

        result["provider_status"]["initialization"] = {
            "status": "success",
            "primary_provider": str(manager.primary_provider),
            "providers_available": (
                list(manager.providers.keys()) if hasattr(manager, "providers") else []
            ),
        }
    except Exception as e:
        result["provider_status"]["initialization"] = {
            "status": "failed",
            "error": str(e),
            "type": type(e).__name__,
        }

    # Test actual LLM call
    try:
        from src.llm.services import LLMService

        service = LLMService()
        test_response = await service.generate_text(
            prompt="Responda em português: Olá", max_tokens=50
        )

        result["provider_status"]["test_call"] = {
            "status": "success",
            "response_preview": test_response[:100] if test_response else None,
            "provider_used": service.config.primary_provider,
        }
    except Exception as e:
        result["provider_status"]["test_call"] = {
            "status": "failed",
            "error": str(e),
            "type": type(e).__name__,
        }

    return result


@router.get("/investigation/{investigation_id}/logs")
async def investigation_logs(investigation_id: str) -> dict[str, Any]:
    """Get detailed logs for a specific investigation."""

    result = {
        "investigation_id": investigation_id,
        "status": {},
        "llm_calls": [],
        "errors": [],
    }

    # Try to get investigation from database
    try:
        from src.services.investigation_service import InvestigationService

        service = InvestigationService()
        investigation = await service.get_by_id(investigation_id)

        if investigation:
            result["status"] = {
                "current_status": investigation.status,
                "progress": (
                    investigation.progress if hasattr(investigation, "progress") else 0
                ),
                "current_phase": (
                    investigation.current_phase
                    if hasattr(investigation, "current_phase")
                    else None
                ),
                "created_at": (
                    str(investigation.created_at)
                    if hasattr(investigation, "created_at")
                    else None
                ),
                "updated_at": (
                    str(investigation.updated_at)
                    if hasattr(investigation, "updated_at")
                    else None
                ),
                "anomalies_found": (
                    investigation.anomalies_found
                    if hasattr(investigation, "anomalies_found")
                    else 0
                ),
                "error_message": (
                    investigation.error_message
                    if hasattr(investigation, "error_message")
                    else None
                ),
            }

            # Check investigation metadata for LLM info
            metadata = (
                investigation.investigation_metadata
                if hasattr(investigation, "investigation_metadata")
                else {}
            )
            if metadata:
                result["llm_info"] = {
                    "provider": (
                        metadata.get("llm_provider")
                        if isinstance(metadata, dict)
                        else None
                    ),
                    "model": (
                        metadata.get("llm_model")
                        if isinstance(metadata, dict)
                        else None
                    ),
                    "total_time": (
                        metadata.get("total_time")
                        if isinstance(metadata, dict)
                        else None
                    ),
                    "llm_response_time": (
                        metadata.get("llm_response_time")
                        if isinstance(metadata, dict)
                        else None
                    ),
                }
        else:
            result["error"] = "Investigation not found"

    except Exception as e:
        result["errors"].append(
            {"phase": "database_lookup", "error": str(e), "type": type(e).__name__}
        )

    # Add current LLM configuration for comparison
    result["current_llm_config"] = {
        "provider": settings.llm_provider,
        "model": settings.llm_model_name,
        "maritaca_configured": bool(settings.maritaca_api_key),
    }

    return result


@router.get("/module-info/{module_path}")
async def module_info(module_path: str) -> dict[str, Any]:
    """Get information about a specific module."""

    try:
        module = importlib.import_module(module_path)

        return {
            "module": module_path,
            "file": getattr(module, "__file__", "unknown"),
            "attributes": [attr for attr in dir(module) if not attr.startswith("_")],
            "status": "loaded",
        }
    except Exception as e:
        return {
            "module": module_path,
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
