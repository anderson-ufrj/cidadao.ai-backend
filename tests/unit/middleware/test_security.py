"""
Unit tests for src/api/middleware/security.py.

These tests focus on the paths where the middleware is supposed to *deny*
a request: blocked IPs, exhausted rate limits, malicious payloads and
invalid CSRF tokens. The happy path is covered only as a control, so that a
"deny everything" regression would also be caught.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.api.middleware.security import (
    CSRFProtection,
    IPBlockList,
    RateLimiter,
    RequestValidator,
    SecurityConfig,
    SecurityMiddleware,
)

PUBLIC_IP = "203.0.113.7"  # TEST-NET-3, never whitelisted


def build_request(
    path: str = "/api/v1/investigations",
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    query: str = "",
    client_host: str | None = PUBLIC_IP,
    body: bytes = b"",
) -> Request:
    """Build a real Starlette Request from an ASGI scope."""
    raw_headers = [
        (k.lower().encode("latin-1"), v.encode("latin-1"))
        for k, v in (headers or {}).items()
    ]
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "root_path": "",
        "query_string": query.encode("utf-8"),
        "headers": raw_headers,
        "client": (client_host, 54321) if client_host else None,
        "server": ("testserver", 80),
    }

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    return Request(scope, receive=receive)


@pytest.fixture
def middleware():
    """SecurityMiddleware with the audit sink replaced by a spy."""
    mw = SecurityMiddleware(app=AsyncMock())
    return mw


@pytest.fixture
def audit_spy():
    """Replace the module-level audit logger so nothing is written to disk."""
    with patch("src.api.middleware.security.audit_logger") as spy:
        spy.log_event = AsyncMock()
        yield spy.log_event


async def call_next_ok(request):
    return Response(content="ok", status_code=200)


# ---------------------------------------------------------------------------
# IPBlockList
# ---------------------------------------------------------------------------


class TestIPBlockList:
    def test_ip_is_blocked_after_reaching_the_failure_threshold(self):
        blocklist = IPBlockList()

        for _ in range(SecurityConfig.MAX_FAILED_ATTEMPTS - 1):
            blocklist.record_failed_attempt(PUBLIC_IP)
        assert (
            blocklist.is_blocked(PUBLIC_IP) is False
        ), "IP must stay allowed below the threshold"

        blocklist.record_failed_attempt(PUBLIC_IP)
        assert blocklist.is_blocked(PUBLIC_IP) is True

    def test_unknown_ip_is_not_blocked(self):
        assert IPBlockList().is_blocked("198.51.100.4") is False

    @pytest.mark.parametrize("ip", ["127.0.0.1", "192.168.1.50", "10.1.2.3"])
    def test_whitelisted_ips_are_never_blocked(self, ip):
        blocklist = IPBlockList()

        for _ in range(SecurityConfig.MAX_FAILED_ATTEMPTS * 3):
            blocklist.record_failed_attempt(ip)

        assert blocklist.is_whitelisted(ip) is True
        assert blocklist.is_blocked(ip) is False
        assert (
            blocklist.failed_attempts[ip] == []
        ), "whitelisted IPs must not accumulate failed attempts"

    def test_block_expires_after_the_configured_duration(self):
        blocklist = IPBlockList()
        for _ in range(SecurityConfig.MAX_FAILED_ATTEMPTS):
            blocklist.record_failed_attempt(PUBLIC_IP)
        assert blocklist.is_blocked(PUBLIC_IP) is True

        blocklist.blocked_ips[PUBLIC_IP] = datetime.now(UTC) - timedelta(
            minutes=SecurityConfig.BLOCK_DURATION_MINUTES + 1
        )

        assert blocklist.is_blocked(PUBLIC_IP) is False
        assert PUBLIC_IP not in blocklist.blocked_ips, "expired block must be dropped"

    def test_malformed_ip_is_not_treated_as_whitelisted(self):
        blocklist = IPBlockList()
        assert blocklist.is_whitelisted("not-an-ip") is False
        assert blocklist.is_whitelisted("") is False

    def test_failed_attempt_count_only_covers_the_requested_window(self):
        blocklist = IPBlockList()
        now = datetime.now(UTC)
        blocklist.failed_attempts[PUBLIC_IP] = [
            now - timedelta(minutes=90),
            now - timedelta(minutes=45),
            now - timedelta(minutes=1),
        ]

        assert blocklist.get_failed_attempts_count(PUBLIC_IP, window_minutes=60) == 2
        assert blocklist.get_failed_attempts_count(PUBLIC_IP, window_minutes=5) == 1
        assert blocklist.get_failed_attempts_count("198.51.100.9") == 0

    def test_old_failures_are_pruned_so_a_slow_attacker_is_not_blocked(self):
        blocklist = IPBlockList()
        old = datetime.now(UTC) - timedelta(hours=2)
        blocklist.failed_attempts[PUBLIC_IP] = [old] * (
            SecurityConfig.MAX_FAILED_ATTEMPTS - 1
        )

        blocklist.record_failed_attempt(PUBLIC_IP)

        assert blocklist.is_blocked(PUBLIC_IP) is False
        assert len(blocklist.failed_attempts[PUBLIC_IP]) == 1


# ---------------------------------------------------------------------------
# RateLimiter
# ---------------------------------------------------------------------------


class TestRateLimiter:
    def test_burst_budget_is_enforced(self):
        limiter = RateLimiter()

        for i in range(SecurityConfig.RATE_LIMIT_BURST_SIZE):
            allowed, _ = limiter.is_allowed(PUBLIC_IP)
            assert allowed is True, f"request {i + 1} inside the burst must be allowed"

        allowed, info = limiter.is_allowed(PUBLIC_IP)
        assert allowed is False
        assert info["reason"] == "burst_limit_exceeded"

    def test_exhausting_one_client_does_not_affect_another(self):
        limiter = RateLimiter()
        for _ in range(SecurityConfig.RATE_LIMIT_BURST_SIZE + 1):
            limiter.is_allowed(PUBLIC_IP)

        allowed, _ = limiter.is_allowed("198.51.100.22")

        assert allowed is True

    def test_minute_window_is_enforced_independently_of_the_burst_budget(self):
        limiter = RateLimiter()
        now = datetime.now(UTC)
        limiter.burst_tokens[PUBLIC_IP] = 999
        limiter.requests[PUBLIC_IP].extend(
            [now - timedelta(seconds=5)] * SecurityConfig.RATE_LIMIT_REQUESTS_PER_MINUTE
        )

        allowed, info = limiter.is_allowed(PUBLIC_IP)

        assert allowed is False
        assert info["reason"] == "minute_limit_exceeded"

    def test_hour_window_is_enforced(self):
        limiter = RateLimiter()
        now = datetime.now(UTC)
        limiter.burst_tokens[PUBLIC_IP] = 999
        # Old enough to leave the minute window, recent enough to stay in the hour.
        limiter.requests[PUBLIC_IP].extend(
            [now - timedelta(minutes=30)] * SecurityConfig.RATE_LIMIT_REQUESTS_PER_HOUR
        )

        allowed, info = limiter.is_allowed(PUBLIC_IP)

        assert allowed is False
        assert info["reason"] == "hour_limit_exceeded"

    def test_requests_older_than_one_hour_are_discarded(self):
        limiter = RateLimiter()
        stale = datetime.now(UTC) - timedelta(hours=2)
        limiter.requests[PUBLIC_IP].extend(
            [stale] * SecurityConfig.RATE_LIMIT_REQUESTS_PER_HOUR
        )

        allowed, info = limiter.is_allowed(PUBLIC_IP)

        assert allowed is True
        assert info["requests_last_hour"] == 1

    def test_allowed_request_reports_and_consumes_one_burst_token(self):
        limiter = RateLimiter()

        allowed, info = limiter.is_allowed(PUBLIC_IP)

        assert allowed is True
        assert info["requests_last_minute"] == 1
        assert info["burst_tokens"] == SecurityConfig.RATE_LIMIT_BURST_SIZE - 1


# ---------------------------------------------------------------------------
# RequestValidator
# ---------------------------------------------------------------------------


class TestRequestValidatorSize:
    def test_oversized_content_length_is_rejected(self):
        request = build_request(
            headers={"content-length": str(SecurityConfig.MAX_REQUEST_SIZE + 1)}
        )
        assert RequestValidator().validate_request_size(request) is False

    def test_content_length_at_the_limit_is_accepted(self):
        request = build_request(
            headers={"content-length": str(SecurityConfig.MAX_REQUEST_SIZE)}
        )
        assert RequestValidator().validate_request_size(request) is True

    def test_non_numeric_content_length_is_rejected(self):
        request = build_request(headers={"content-length": "not-a-number"})
        assert RequestValidator().validate_request_size(request) is False

    def test_missing_content_length_is_accepted(self):
        assert RequestValidator().validate_request_size(build_request()) is True


class TestRequestValidatorHeaders:
    @pytest.mark.parametrize(
        "payload",
        [
            "<script>alert(1)</script>",
            "javascript:alert(1)",
            "' union select password from users --",
            "../../etc/passwd",
        ],
    )
    def test_malicious_value_in_a_custom_header_is_rejected(self, payload):
        request = build_request(headers={"x-tenant-note": payload})

        valid, error = RequestValidator().validate_headers(request)

        assert valid is False
        assert "x-tenant-note" in error

    def test_browser_headers_are_exempt_from_pattern_matching(self):
        # Real Chrome sends sec-ch-ua values full of characters that trip the
        # command-injection patterns; blocking them would break every browser.
        request = build_request(
            headers={
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "sec-ch-ua": '"Chromium";v="120", "Not:A-Brand";v="99"',
                "accept": "text/html,application/xhtml+xml;q=0.9",
            }
        )

        valid, error = RequestValidator().validate_headers(request)

        assert valid is True
        assert error is None

    def test_oversized_headers_are_rejected(self):
        request = build_request(
            headers={"x-blob": "a" * (SecurityConfig.MAX_HEADER_SIZE + 10)}
        )

        valid, error = RequestValidator().validate_headers(request)

        assert valid is False
        assert error == "Headers too large"


class TestRequestValidatorUrl:
    @pytest.mark.parametrize(
        ("path", "query"),
        [
            ("/api/v1/files/../../etc/passwd", ""),
            ("/api/v1/search", "q=union+select+name+from+users"),
            ("/api/v1/search", "q=<script>alert(1)</script>"),
            ("/api/v1/proxy", "target=file:///etc/shadow"),
            ("/api/v1/exec", "cmd=;%20rm"),
        ],
    )
    def test_suspicious_url_is_rejected(self, path, query):
        request = build_request(path=path, query=query)

        valid, error = RequestValidator().validate_url(request)

        assert valid is False
        assert error is not None

    @pytest.mark.parametrize(
        "query",
        [
            "id=1+union+select+password+from+users",  # form encoding of spaces
            "id=1%20union%20select%20password%20from%20users",  # percent encoding
            "name=x%27%3B%20drop%20table%20users%3B%20--",
            "file=..%2F..%2Fetc%2Fpasswd",
        ],
    )
    def test_encoded_payloads_do_not_bypass_pattern_matching(self, query):
        # Every pattern that relies on \s is defeated by "+" or "%20" unless
        # the validator scans the decoded query string too.
        request = build_request(path="/api/v1/contracts", query=query)

        valid, error = RequestValidator().validate_url(request)

        assert valid is False, f"encoded payload slipped through: {query}"
        assert error == "Suspicious pattern in URL"

    def test_double_url_encoding_is_rejected_even_on_exempt_paths(self):
        request = build_request(path="/docs", query="file=%252e%252e%252f")

        valid, error = RequestValidator().validate_url(request)

        assert valid is False
        assert error == "Double URL encoding detected"

    def test_overlong_url_is_rejected(self):
        request = build_request(path="/api/v1/" + "a" * SecurityConfig.MAX_URL_LENGTH)

        valid, error = RequestValidator().validate_url(request)

        assert valid is False
        assert error == "URL too long"

    def test_exempt_path_skips_pattern_matching(self):
        request = build_request(path="/openapi.json", query="q=union+select+1")

        valid, error = RequestValidator().validate_url(request)

        assert valid is True, "documentation paths are explicitly exempt"
        assert error is None

    def test_ordinary_url_is_accepted(self):
        request = build_request(
            path="/api/v1/investigations", query="page=2&order=created_at"
        )

        assert RequestValidator().validate_url(request) == (True, None)


class TestRequestValidatorContentType:
    @pytest.mark.parametrize(
        "content_type",
        ["application/xml", "text/html", "application/octet-stream"],
    )
    def test_unsupported_content_type_is_rejected(self, content_type):
        request = build_request(headers={"content-type": content_type})
        assert RequestValidator().validate_content_type(request) is False

    @pytest.mark.parametrize(
        "content_type",
        [
            "application/json",
            "application/json; charset=utf-8",
            "APPLICATION/JSON",
            "multipart/form-data; boundary=x",
        ],
    )
    def test_supported_content_type_is_accepted(self, content_type):
        request = build_request(headers={"content-type": content_type})
        assert RequestValidator().validate_content_type(request) is True

    def test_missing_content_type_is_accepted(self):
        assert RequestValidator().validate_content_type(build_request()) is True


class TestRequestValidatorBody:
    @pytest.mark.parametrize(
        "body",
        [
            b'{"q": "drop table investigations"}',
            b'{"q": "<script>fetch(1)</script>"}',
            b'{"q": "1 or 1=1"}',
            b'{"path": "../../etc/passwd"}',
        ],
    )
    async def test_malicious_body_is_rejected(self, body):
        valid, error = await RequestValidator().scan_request_body(body)

        assert valid is False
        assert error == "Suspicious pattern in request body"

    async def test_clean_body_is_accepted(self):
        body = b'{"query": "gastos com merenda escolar em 2024"}'

        assert await RequestValidator().scan_request_body(body) == (True, None)

    async def test_empty_body_is_accepted(self):
        assert await RequestValidator().scan_request_body(b"") == (True, None)

    async def test_invalid_utf8_bytes_do_not_raise(self):
        valid, _ = await RequestValidator().scan_request_body(b"\xff\xfe\x00clean")

        assert valid is True


# ---------------------------------------------------------------------------
# SecurityMiddleware.dispatch — the deny paths
# ---------------------------------------------------------------------------


class TestSecurityMiddlewareDenies:
    async def test_blocked_ip_gets_403_and_the_app_is_never_reached(
        self, middleware, audit_spy
    ):
        for _ in range(SecurityConfig.MAX_FAILED_ATTEMPTS):
            middleware.ip_blocklist.record_failed_attempt(PUBLIC_IP)
        call_next = AsyncMock()

        response = await middleware.dispatch(build_request(), call_next)

        assert response.status_code == 403
        call_next.assert_not_awaited()
        audit_spy.assert_awaited()

    async def test_rate_limited_request_gets_429_with_retry_headers(
        self, middleware, audit_spy
    ):
        middleware.rate_limiter.burst_tokens[PUBLIC_IP] = 0
        call_next = AsyncMock()

        response = await middleware.dispatch(build_request(), call_next)

        assert response.status_code == 429
        assert response.headers["Retry-After"] == "60"
        assert response.headers["X-RateLimit-Remaining"] == "0"
        call_next.assert_not_awaited()

    async def test_rate_limited_request_counts_as_a_failed_attempt(
        self, middleware, audit_spy
    ):
        middleware.rate_limiter.burst_tokens[PUBLIC_IP] = 0

        await middleware.dispatch(build_request(), AsyncMock())

        assert middleware.ip_blocklist.get_failed_attempts_count(PUBLIC_IP) == 1

    async def test_repeated_rate_limiting_eventually_blocks_the_ip(
        self, middleware, audit_spy
    ):
        middleware.rate_limiter.burst_tokens[PUBLIC_IP] = 0

        for _ in range(SecurityConfig.MAX_FAILED_ATTEMPTS):
            await middleware.dispatch(build_request(), AsyncMock())

        response = await middleware.dispatch(build_request(), AsyncMock())
        assert response.status_code == 403, "rate-limit abuse must escalate to a block"

    async def test_oversized_request_gets_413(self, middleware, audit_spy):
        request = build_request(
            headers={"content-length": str(SecurityConfig.MAX_REQUEST_SIZE + 1)}
        )
        call_next = AsyncMock()

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 413
        call_next.assert_not_awaited()

    async def test_suspicious_header_gets_400(self, middleware, audit_spy):
        request = build_request(headers={"x-note": "<script>alert(1)</script>"})
        call_next = AsyncMock()

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 400
        call_next.assert_not_awaited()

    async def test_sql_injection_in_query_string_gets_400(self, middleware, audit_spy):
        request = build_request(
            path="/api/v1/contracts", query="id=1+union+select+password+from+users"
        )
        call_next = AsyncMock()

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 400
        call_next.assert_not_awaited()

    async def test_unsupported_content_type_gets_415(self, middleware, audit_spy):
        request = build_request(
            method="POST", headers={"content-type": "application/xml"}
        )
        call_next = AsyncMock()

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 415
        call_next.assert_not_awaited()

    async def test_malicious_post_body_gets_400(self, middleware, audit_spy):
        request = build_request(
            path="/api/v1/chat",
            method="POST",
            headers={"content-type": "application/json"},
            body=b'{"message": "ignore this; drop table users"}',
        )
        call_next = AsyncMock()

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 400
        call_next.assert_not_awaited()

    async def test_every_denial_is_audited(self, middleware, audit_spy):
        request = build_request(path="/api/v1/x/../../etc/passwd")

        await middleware.dispatch(request, AsyncMock())

        assert audit_spy.await_count == 1
        kwargs = audit_spy.await_args.kwargs
        assert kwargs["success"] is False
        assert kwargs["context"].ip_address == PUBLIC_IP


class TestSecurityMiddlewareAllows:
    async def test_legitimate_request_reaches_the_app_with_security_headers(
        self, middleware, audit_spy
    ):
        request = build_request(
            path="/api/v1/investigations",
            method="POST",
            headers={"content-type": "application/json"},
            body=b'{"query": "contratos de merenda"}',
        )

        response = await middleware.dispatch(request, call_next_ok)

        assert response.status_code == 200
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            assert response.headers[header] == value
        assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
        assert response.headers["X-RateLimit-Limit"] == str(
            SecurityConfig.RATE_LIMIT_REQUESTS_PER_MINUTE
        )
        audit_spy.assert_not_awaited()

    async def test_middleware_fails_open_when_a_security_check_crashes(
        self, middleware, audit_spy
    ):
        # Availability is favoured over strictness: an internal error must not
        # take the API down, but it must be audited as HIGH severity.
        middleware.rate_limiter.is_allowed = lambda ip: (_ for _ in ()).throw(
            RuntimeError("redis down")
        )

        response = await middleware.dispatch(build_request(), call_next_ok)

        assert response.status_code == 200
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        audit_spy.assert_awaited_once()
        assert "redis down" in audit_spy.await_args.kwargs["message"]


class TestClientIpResolution:
    async def test_first_x_forwarded_for_entry_wins(self, middleware):
        request = build_request(
            headers={"x-forwarded-for": "198.51.100.5, 10.0.0.1, 10.0.0.2"}
        )

        assert middleware._get_client_ip(request) == "198.51.100.5"

    async def test_spoofed_x_forwarded_for_falls_back_to_x_real_ip(self, middleware):
        request = build_request(
            headers={
                "x-forwarded-for": "not-an-ip",
                "x-real-ip": "198.51.100.6",
            }
        )

        assert middleware._get_client_ip(request) == "198.51.100.6"

    async def test_falls_back_to_the_socket_peer(self, middleware):
        request = build_request(headers={"x-forwarded-for": "<script>"})

        assert middleware._get_client_ip(request) == PUBLIC_IP

    async def test_returns_unknown_when_there_is_no_peer(self, middleware):
        request = build_request(client_host=None)

        assert middleware._get_client_ip(request) == "unknown"


class TestSecurityHeaders:
    def test_headers_are_added_to_an_arbitrary_response(self, middleware):
        response = JSONResponse(content={"ok": True})

        middleware._add_security_headers(response)

        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "Strict-Transport-Security" in response.headers
        assert response.headers["Content-Security-Policy"].startswith(
            "default-src 'self'"
        )


# ---------------------------------------------------------------------------
# CSRF
# ---------------------------------------------------------------------------


class TestCSRFProtection:
    def test_token_validates_for_the_session_that_generated_it(self):
        csrf = CSRFProtection()
        token = csrf.generate_token("session-abc")

        assert csrf.validate_token(token, "session-abc") is True

    def test_token_from_another_session_is_rejected(self):
        csrf = CSRFProtection()
        token = csrf.generate_token("session-victim")

        assert csrf.validate_token(token, "session-attacker") is False

    def test_tampered_signature_is_rejected(self):
        csrf = CSRFProtection()
        timestamp, signature = csrf.generate_token("session-abc").split(":", 1)
        forged = f"{timestamp}:{'0' * len(signature)}"

        assert csrf.validate_token(forged, "session-abc") is False

    def test_tampered_timestamp_invalidates_the_signature(self):
        csrf = CSRFProtection()
        timestamp, signature = csrf.generate_token("session-abc").split(":", 1)
        forged = f"{int(timestamp) + 1}:{signature}"

        assert csrf.validate_token(forged, "session-abc") is False

    def test_expired_token_is_rejected(self):
        csrf = CSRFProtection()
        token = csrf.generate_token("session-abc")

        with patch("src.api.middleware.security.time.time") as fake_time:
            fake_time.return_value = float(token.split(":")[0]) + 3601
            assert csrf.validate_token(token, "session-abc", max_age=3600) is False

    def test_token_within_max_age_is_accepted(self):
        csrf = CSRFProtection()
        token = csrf.generate_token("session-abc")

        with patch("src.api.middleware.security.time.time") as fake_time:
            fake_time.return_value = float(token.split(":")[0]) + 3500
            assert csrf.validate_token(token, "session-abc", max_age=3600) is True

    @pytest.mark.parametrize("token", ["", "garbage", "notanumber:sig", "::"])
    def test_malformed_token_is_rejected_without_raising(self, token):
        assert CSRFProtection().validate_token(token, "session-abc") is False

    def test_two_sessions_never_share_a_signature(self):
        csrf = CSRFProtection()

        with patch("src.api.middleware.security.time.time", return_value=1_700_000_000):
            token_a = csrf.generate_token("session-a")
            token_b = csrf.generate_token("session-b")

        assert token_a != token_b
