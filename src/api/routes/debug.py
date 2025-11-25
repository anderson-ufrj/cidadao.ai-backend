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

router = APIRouter(tags=["debug"])


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


@router.get("/list-all-investigations")
async def list_all_investigations() -> dict[str, Any]:
    """List all investigations from database (debug only)."""

    result = {"status": "started", "investigations": [], "errors": []}

    try:
        from src.infrastructure.database import get_db_pool

        pool = await get_db_pool()

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    id,
                    user_id,
                    query,
                    status,
                    progress,
                    current_phase,
                    created_at,
                    completed_at,
                    anomalies_found,
                    records_processed,
                    confidence_score
                FROM investigations
                ORDER BY created_at DESC
                LIMIT 10
            """
            )

            for row in rows:
                result["investigations"].append(
                    {
                        "id": row["id"],
                        "user_id": row["user_id"],
                        "query": row["query"][:100],
                        "status": row["status"],
                        "progress": (
                            row["progress"] if "progress" in row.keys() else None
                        ),
                        "current_phase": (
                            row["current_phase"]
                            if "current_phase" in row.keys()
                            else None
                        ),
                        "created_at": str(row["created_at"]),
                        "completed_at": (
                            str(row["completed_at"]) if row["completed_at"] else None
                        ),
                        "anomalies_found": row["anomalies_found"],
                        "records_processed": (
                            row["records_processed"]
                            if "records_processed" in row.keys()
                            else None
                        ),
                        "confidence_score": row["confidence_score"],
                    }
                )

        result["status"] = "completed"
        result["total"] = len(result["investigations"])

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(
            {
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }
        )

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


@router.post("/run-migration")
async def run_migration() -> dict[str, Any]:
    """Run pending database migrations (USE WITH CAUTION IN PRODUCTION)."""

    result = {"status": "started", "migrations_applied": [], "errors": []}

    try:
        import subprocess

        # Check current migration version
        alembic_cmd = (
            "venv/bin/alembic" if os.path.exists("venv/bin/alembic") else "alembic"
        )

        current_cmd = subprocess.run(
            [alembic_cmd, "current"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        result["current_version"] = current_cmd.stdout.strip()

        # Run upgrade
        upgrade_cmd = subprocess.run(
            [alembic_cmd, "upgrade", "head"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

        result["upgrade_output"] = upgrade_cmd.stdout
        result["upgrade_errors"] = upgrade_cmd.stderr

        if upgrade_cmd.returncode == 0:
            result["status"] = "success"
            result["message"] = "Migrations applied successfully"
        else:
            result["status"] = "failed"
            result["message"] = "Migration failed"
            result["return_code"] = upgrade_cmd.returncode

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(
            {
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }
        )

    return result


@router.get("/check-constraints")
async def check_database_constraints() -> dict[str, Any]:
    """Check database constraints for investigations table and list recent investigations."""

    result = {
        "status": "started",
        "constraints": [],
        "investigations": [],
        "errors": [],
    }

    try:
        from src.infrastructure.database import get_db_pool

        # Get database pool
        pool = await get_db_pool()

        # Check constraints on investigations table
        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT conname, pg_get_constraintdef(oid) as definition
                    FROM pg_constraint
                    WHERE conrelid = 'investigations'::regclass;
                    """
                )
                result["constraints"] = [
                    {"name": row["conname"], "definition": row["definition"]}
                    for row in rows
                ]
        except Exception as e:
            result["errors"].append(
                {"check": "constraints", "error": str(e), "type": type(e).__name__}
            )

        result["status"] = (
            "completed" if not result["errors"] else "completed_with_errors"
        )

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(
            {
                "phase": "database_connection",
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }
        )

    return result


@router.post("/add-investigation-columns")
async def add_investigation_columns() -> dict[str, Any]:
    """Add missing investigation tracking columns (SAFE - uses IF NOT EXISTS)."""

    result = {"status": "started", "columns_added": [], "errors": []}

    try:
        from src.infrastructure.database import get_db_pool

        pool = await get_db_pool()

        # SQL commands to add missing columns
        columns_to_add = [
            (
                "progress",
                "ALTER TABLE investigations ADD COLUMN IF NOT EXISTS progress FLOAT DEFAULT 0.0",
            ),
            (
                "current_phase",
                "ALTER TABLE investigations ADD COLUMN IF NOT EXISTS current_phase VARCHAR(100) DEFAULT 'pending'",
            ),
            (
                "summary",
                "ALTER TABLE investigations ADD COLUMN IF NOT EXISTS summary TEXT",
            ),
            (
                "records_processed",
                "ALTER TABLE investigations ADD COLUMN IF NOT EXISTS records_processed INTEGER DEFAULT 0",
            ),
        ]

        async with pool.acquire() as conn:
            for column_name, sql in columns_to_add:
                try:
                    await conn.execute(sql)
                    result["columns_added"].append(
                        {
                            "column": column_name,
                            "status": "success",
                            "message": f"Column '{column_name}' added successfully",
                        }
                    )
                except Exception as e:
                    result["errors"].append(
                        {
                            "column": column_name,
                            "error": str(e),
                            "type": type(e).__name__,
                        }
                    )

        result["status"] = (
            "completed" if not result["errors"] else "completed_with_errors"
        )

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(
            {
                "phase": "database_connection",
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }
        )

    return result


@router.post("/fix-database")
async def fix_database_schema() -> dict[str, Any]:
    """Fix database schema issues (USE WITH CAUTION IN PRODUCTION)."""

    result = {"status": "started", "fixes_applied": [], "errors": []}

    try:
        from src.infrastructure.database import get_db_pool

        # Get database pool
        pool = await get_db_pool()

        # Fix 1: Drop existing status CHECK constraint and recreate with 'running'
        try:
            async with pool.acquire() as conn:
                # First, find the constraint name
                constraint_row = await conn.fetchrow(
                    """
                    SELECT conname
                    FROM pg_constraint
                    WHERE conrelid = 'investigations'::regclass
                    AND contype = 'c'
                    AND pg_get_constraintdef(oid) LIKE '%status%';
                    """
                )

                if constraint_row:
                    constraint_name = constraint_row["conname"]

                    # Drop the old constraint
                    await conn.execute(
                        f"""
                        ALTER TABLE investigations
                        DROP CONSTRAINT {constraint_name};
                        """
                    )

                    # Create new constraint with 'running' status
                    await conn.execute(
                        """
                        ALTER TABLE investigations
                        ADD CONSTRAINT investigations_status_check
                        CHECK (status IN ('pending', 'running', 'completed', 'failed'));
                        """
                    )

                    result["fixes_applied"].append(
                        {
                            "fix": "status_constraint",
                            "description": f"Dropped constraint '{constraint_name}' and recreated with 'running' status",
                            "status": "success",
                        }
                    )
                else:
                    result["errors"].append(
                        {
                            "fix": "status_constraint",
                            "error": "No status constraint found",
                            "type": "NotFound",
                        }
                    )
        except Exception as e:
            result["errors"].append(
                {"fix": "status_constraint", "error": str(e), "type": type(e).__name__}
            )

        # Verify the fix
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT conname, pg_get_constraintdef(oid) as definition
                    FROM pg_constraint
                    WHERE conrelid = 'investigations'::regclass
                    AND contype = 'c'
                    AND pg_get_constraintdef(oid) LIKE '%status%';
                """
                )
                if row:
                    result["verification"] = {
                        "constraint_name": row["conname"],
                        "definition": row["definition"],
                    }
        except Exception as e:
            result["errors"].append(
                {"phase": "verification", "error": str(e), "type": type(e).__name__}
            )

        result["status"] = (
            "completed" if not result["errors"] else "completed_with_errors"
        )

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(
            {
                "phase": "database_connection",
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }
        )

    return result


@router.get("/database-config")
async def database_config() -> dict[str, Any]:
    """
    Check database configuration and connection status.

    Returns information about:
    - DATABASE_URL configuration
    - Database type (PostgreSQL vs SQLite)
    - Connection status
    - Table existence
    """
    import os

    from src.db.simple_session import DATABASE_URL, _get_engine

    result = {
        "status": "checking",
        "environment": {},
        "database": {},
        "tables": {},
        "investigations": {},
    }

    try:
        # Check environment variables
        raw_db_url = os.getenv("DATABASE_URL")
        result["environment"] = {
            "DATABASE_URL_configured": raw_db_url is not None,
            "DATABASE_URL_type": (
                "PostgreSQL"
                if raw_db_url and "postgres" in raw_db_url
                else "SQLite" if raw_db_url else "Not configured"
            ),
            "DATABASE_URL_preview": (
                f"{raw_db_url[:20]}...{raw_db_url[-20:]}"
                if raw_db_url and len(raw_db_url) > 60
                else "Not set"
            ),
        }

        # Check actual DATABASE_URL being used
        result["database"] = {
            "active_url_preview": (
                f"{DATABASE_URL[:30]}..." if len(DATABASE_URL) > 30 else DATABASE_URL
            ),
            "database_type": (
                "PostgreSQL"
                if "postgres" in DATABASE_URL
                else "SQLite" if "sqlite" in DATABASE_URL else "Unknown"
            ),
            "async_driver": (
                "asyncpg"
                if "asyncpg" in DATABASE_URL
                else "aiosqlite" if "aiosqlite" in DATABASE_URL else "Unknown"
            ),
        }

        # Try to connect and check tables
        from sqlalchemy import text

        engine = _get_engine()

        async with engine.begin() as conn:
            # Check if investigations table exists using direct query
            try:
                check_result = await conn.execute(
                    text(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'investigations')"
                    )
                )
                table_exists = check_result.scalar()
            except Exception:
                # Fallback for SQLite
                try:
                    await conn.execute(text("SELECT 1 FROM investigations LIMIT 1"))
                    table_exists = True
                except Exception:
                    table_exists = False

            result["tables"]["investigations_exists"] = table_exists

            if table_exists:
                # Count investigations
                count_result = await conn.execute(
                    text("SELECT COUNT(*) as count FROM investigations")
                )
                row = count_result.fetchone()
                investigation_count = row[0] if row else 0

                # Get recent investigations
                recent_result = await conn.execute(
                    text(
                        "SELECT id, status, created_at FROM investigations ORDER BY created_at DESC LIMIT 5"
                    )
                )
                recent = [
                    {"id": r[0], "status": r[1], "created_at": str(r[2])}
                    for r in recent_result.fetchall()
                ]

                result["investigations"] = {
                    "total_count": investigation_count,
                    "recent_investigations": recent,
                    "table_accessible": True,
                }
            else:
                result["investigations"] = {
                    "error": "investigations table does not exist",
                    "suggestion": "Run database migrations: alembic upgrade head",
                }

        result["status"] = "success"
        result["connection_test"] = "✅ Connection successful"

    except Exception as e:
        result["status"] = "error"
        result["error"] = {
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
        }
        result["connection_test"] = "❌ Connection failed"

    return result


@router.get("/infrastructure-status")
async def infrastructure_status() -> dict[str, Any]:
    """
    Check infrastructure status (Redis, Celery, Database).

    Returns comprehensive status of all backend services.
    """
    result = {
        "status": "checking",
        "redis": {},
        "celery": {},
        "database": {},
        "environment": {},
    }

    # Check environment
    result["environment"] = {
        "REDIS_URL_configured": bool(os.getenv("REDIS_URL")),
        "DATABASE_URL_configured": bool(os.getenv("DATABASE_URL")),
        "CELERY_BROKER_URL": os.getenv("CELERY_BROKER_URL", "Not set"),
    }

    # Check Redis
    try:
        import redis.asyncio as aioredis

        from src.core import settings

        redis_url = settings.redis_url
        result["redis"]["url_preview"] = (
            f"{redis_url[:20]}..." if len(redis_url) > 20 else redis_url
        )

        client = aioredis.from_url(redis_url, decode_responses=True)
        ping_result = await client.ping()
        await client.close()

        result["redis"]["status"] = "✅ Connected" if ping_result else "❌ No response"
        result["redis"]["ping"] = ping_result

    except Exception as e:
        result["redis"]["status"] = "❌ Failed"
        result["redis"]["error"] = str(e)
        result["redis"]["type"] = type(e).__name__

    # Check Celery
    try:
        from src.infrastructure.queue.celery_app import celery_app

        # Try to inspect workers
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        registered_tasks = inspect.registered()

        result["celery"]["broker_url"] = (
            f"{celery_app.conf.broker_url[:30]}..."
            if celery_app.conf.broker_url
            else "Not configured"
        )

        if active_workers:
            result["celery"]["status"] = "✅ Workers running"
            result["celery"]["workers"] = list(active_workers.keys())
            result["celery"]["active_tasks"] = sum(
                len(tasks) for tasks in active_workers.values()
            )
        else:
            result["celery"]["status"] = "⚠️ No workers detected"
            result["celery"]["workers"] = []
            result["celery"][
                "note"
            ] = "Celery workers are not running. Background tasks will not execute."

        if registered_tasks:
            result["celery"]["registered_tasks_count"] = sum(
                len(tasks) for tasks in registered_tasks.values()
            )

    except Exception as e:
        result["celery"]["status"] = "❌ Failed to connect"
        result["celery"]["error"] = str(e)
        result["celery"]["type"] = type(e).__name__
        result["celery"][
            "note"
        ] = "Celery broker (Redis) may not be configured or accessible."

    # Check Database (quick test)
    try:
        from sqlalchemy import text

        from src.db.simple_session import _get_engine

        engine = _get_engine()
        async with engine.begin() as conn:
            check_result = await conn.execute(text("SELECT 1"))
            check_result.fetchone()

        result["database"]["status"] = "✅ Connected"

        # Quick investigation count
        async with engine.begin() as conn:
            count_result = await conn.execute(
                text("SELECT COUNT(*) FROM investigations")
            )
            row = count_result.fetchone()
            result["database"]["investigations_count"] = row[0] if row else 0

            # Count stuck investigations
            stuck_result = await conn.execute(
                text(
                    "SELECT COUNT(*) FROM investigations WHERE status = 'running' AND created_at < NOW() - INTERVAL '1 hour'"
                )
            )
            stuck_row = stuck_result.fetchone()
            result["database"]["stuck_investigations"] = (
                stuck_row[0] if stuck_row else 0
            )

    except Exception as e:
        result["database"]["status"] = "❌ Failed"
        result["database"]["error"] = str(e)

    # Overall status
    all_ok = all(
        "✅" in str(result.get(k, {}).get("status", ""))
        for k in ["redis", "celery", "database"]
    )

    result["status"] = "✅ All systems operational" if all_ok else "⚠️ Issues detected"

    return result


@router.post("/fix-stuck-investigations")
async def fix_stuck_investigations() -> dict[str, Any]:
    """
    Fix stuck investigations by marking old 'running' ones as 'failed'.

    This is safe to run - only affects investigations stuck for >1 hour.
    """
    result = {
        "status": "started",
        "fixed_count": 0,
        "fixed_ids": [],
        "errors": [],
    }

    try:
        from sqlalchemy import text

        from src.db.simple_session import _get_engine

        engine = _get_engine()

        async with engine.begin() as conn:
            # First, get stuck investigations
            stuck_result = await conn.execute(
                text(
                    """
                    SELECT id, query, created_at
                    FROM investigations
                    WHERE status = 'running'
                    AND created_at < NOW() - INTERVAL '1 hour'
                    """
                )
            )
            stuck_rows = stuck_result.fetchall()

            for row in stuck_rows:
                result["fixed_ids"].append(
                    {
                        "id": row[0],
                        "query": row[1][:50] if row[1] else "",
                        "created_at": str(row[2]),
                    }
                )

            # Update stuck investigations
            update_result = await conn.execute(
                text(
                    """
                    UPDATE investigations
                    SET status = 'failed',
                        error_message = 'Investigation timed out (stuck in running state for >1 hour)',
                        completed_at = NOW()
                    WHERE status = 'running'
                    AND created_at < NOW() - INTERVAL '1 hour'
                    RETURNING id
                    """
                )
            )

            result["fixed_count"] = update_result.rowcount

        result["status"] = "completed"
        result["message"] = (
            f"Fixed {result['fixed_count']} stuck investigations"
            if result["fixed_count"] > 0
            else "No stuck investigations found"
        )

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(
            {
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }
        )

    return result
