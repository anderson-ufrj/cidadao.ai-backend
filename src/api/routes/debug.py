"""
Debug routes for diagnosing issues in production.
"""

import importlib
import os
import sys
import traceback
from typing import Any

from fastapi import APIRouter

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
