"""
Security tests for the /api/v1/debug router.

The debug router used to be mounted unconditionally, without authentication,
on an API that is reachable from the public internet. These tests pin the two
guarantees that replaced it:

1. Endpoints that execute arbitrary imports, run migrations, mutate the schema
   or dump other users' data are gone from the router entirely.
2. What is left is mounted only when ``DEBUG_ENDPOINTS_ENABLED`` is explicitly
   turned on (it is off by default) and, even then, requires an admin token.
"""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.api.app import app
from src.api.routes import debug
from src.core.config import Settings

DEBUG_PREFIX = "/api/v1/debug"

# Endpoints removed outright: no legitimate use for them on a public API.
REMOVED_ENDPOINTS = [
    ("GET", f"{DEBUG_PREFIX}/module-info/os"),
    ("GET", f"{DEBUG_PREFIX}/llm-config"),
    ("GET", f"{DEBUG_PREFIX}/list-all-investigations"),
    ("GET", f"{DEBUG_PREFIX}/investigation/any-id/logs"),
    ("POST", f"{DEBUG_PREFIX}/run-migration"),
    ("POST", f"{DEBUG_PREFIX}/add-investigation-columns"),
    ("POST", f"{DEBUG_PREFIX}/fix-database"),
    ("POST", f"{DEBUG_PREFIX}/fix-stuck-investigations"),
    ("POST", f"{DEBUG_PREFIX}/test-update-status/any-id"),
]

# Read-only diagnostics kept behind the flag plus admin authentication.
KEPT_ENDPOINTS = [
    "/drummond-status",
    "/infrastructure-status",
    "/database-config",
    "/check-constraints",
]


@pytest.fixture
def client():
    """Client for the real application, built with the default settings."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def guarded_client():
    """Client for an app where the debug router is mounted (flag simulated on)."""
    isolated_app = FastAPI()
    isolated_app.include_router(debug.router, prefix=DEBUG_PREFIX)
    return TestClient(isolated_app, raise_server_exceptions=False)


class TestDangerousEndpointsRemoved:
    """The endpoints that granted code execution or data mutation are gone."""

    @pytest.mark.unit
    def test_removed_endpoints_are_not_declared_in_the_router(self):
        declared = {route.path for route in debug.router.routes}
        for _method, path in REMOVED_ENDPOINTS:
            suffix = path[len(DEBUG_PREFIX) :]
            leaf = suffix.split("/")[1]
            assert not any(
                leaf in declared_path for declared_path in declared
            ), f"{leaf} is still declared in the debug router"

    @pytest.mark.unit
    @pytest.mark.parametrize(("method", "path"), REMOVED_ENDPOINTS)
    def test_removed_endpoints_do_not_answer_an_anonymous_client(
        self, client, method, path
    ):
        response = client.request(method, path)
        assert response.status_code == 404, (
            f"{method} {path} answered {response.status_code}; "
            "it must not exist anymore"
        )


class TestDebugRouterIsOffByDefault:
    """Nothing under /api/v1/debug is reachable with the default settings."""

    @pytest.mark.unit
    def test_flag_is_disabled_by_default(self):
        assert Settings.model_fields["debug_endpoints_enabled"].default is False

    @pytest.mark.unit
    def test_no_debug_route_is_mounted_by_default(self):
        # The OpenAPI schema is the ground truth here: this FastAPI version keeps
        # included routers nested, so walking app.routes misses mounted paths.
        mounted = [
            path
            for path in app.openapi().get("paths", {})
            if path.startswith(DEBUG_PREFIX)
        ]
        assert mounted == [], f"debug routes mounted with the flag off: {mounted}"

    @pytest.mark.unit
    @pytest.mark.parametrize("suffix", KEPT_ENDPOINTS)
    def test_kept_endpoints_are_absent_when_the_flag_is_off(self, client, suffix):
        response = client.get(f"{DEBUG_PREFIX}{suffix}")
        assert response.status_code == 404


class TestDebugRouterRequiresAdmin:
    """Even when mounted, the router refuses anonymous callers."""

    @pytest.mark.unit
    @pytest.mark.parametrize("suffix", KEPT_ENDPOINTS)
    def test_anonymous_caller_is_rejected(self, guarded_client, suffix):
        response = guarded_client.get(f"{DEBUG_PREFIX}{suffix}")
        assert response.status_code in (
            401,
            403,
        ), f"{suffix} answered {response.status_code} to an anonymous caller"

    @pytest.mark.unit
    @pytest.mark.parametrize("suffix", KEPT_ENDPOINTS)
    def test_invalid_token_is_rejected(self, guarded_client, suffix):
        response = guarded_client.get(
            f"{DEBUG_PREFIX}{suffix}",
            headers={"Authorization": "Bearer not-a-real-token"},
        )
        assert response.status_code in (401, 403)


class TestRequireDebugAdmin:
    """The dependency admits a real admin, so the rejections above mean something."""

    @pytest.mark.unit
    def test_admin_is_accepted(self):
        user = {"user_id": "u-1", "email": "a@b.c", "roles": ["admin"]}
        assert debug.require_debug_admin(user) == user

    @pytest.mark.unit
    def test_anonymous_is_rejected_with_401(self):
        with pytest.raises(HTTPException) as exc:
            debug.require_debug_admin(None)
        assert exc.value.status_code == 401

    @pytest.mark.unit
    def test_authenticated_non_admin_is_rejected_with_403(self):
        with pytest.raises(HTTPException) as exc:
            debug.require_debug_admin({"user_id": "u-2", "roles": ["user"]})
        assert exc.value.status_code == 403
