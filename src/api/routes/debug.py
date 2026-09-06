"""
Diagnostic routes for troubleshooting a running deployment.

These endpoints expose infrastructure internals (connection status, agent import
diagnostics, schema constraints), so they are guarded twice over:

- ``app.py`` mounts this router only when ``DEBUG_ENDPOINTS_ENABLED`` is true;
  the setting defaults to false, so a deployment that says nothing gets nothing.
- Every route requires an authenticated admin, so turning the flag on by mistake
  still does not hand the diagnostics to an anonymous caller.

Endpoints that imported arbitrary modules, ran migrations, altered the schema or
returned other users' investigations were removed rather than guarded: they had
no legitimate use on an internet-facing API.
"""

import os
import sys
import traceback
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_current_optional_user


def require_debug_admin(
    user: dict[str, Any] | None = Depends(get_current_optional_user),
) -> dict[str, Any]:
    """Allow only authenticated admins through. Fails closed on anything else."""
    if not user or not user.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    roles = [str(role).lower() for role in (user.get("roles") or [])]
    if "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    return user


router = APIRouter(tags=["debug"], dependencies=[Depends(require_debug_admin)])


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
                rows = await conn.fetch("""
                    SELECT conname, pg_get_constraintdef(oid) as definition
                    FROM pg_constraint
                    WHERE conrelid = 'investigations'::regclass;
                    """)
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
            # Never echo the URL itself: it carries user, password and host.
        }

        # Check actual DATABASE_URL being used
        result["database"] = {
            "url_configured": bool(DATABASE_URL),
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
        "CELERY_BROKER_URL_configured": bool(os.getenv("CELERY_BROKER_URL")),
    }

    # Check Redis
    try:
        import redis.asyncio as aioredis

        from src.core import settings

        redis_url = settings.redis_url
        result["redis"]["url_configured"] = bool(redis_url)

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

        result["celery"]["broker_configured"] = bool(celery_app.conf.broker_url)

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
