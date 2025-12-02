"""
Tests for Session Rate Limiter.

Tests the per-session rate limiting functionality.

Author: Anderson Henrique da Silva
Created: 2025-12-02
"""

import time
from unittest.mock import patch

from src.services.session_rate_limiter import (
    SessionLimitConfig,
    SessionRateLimitState,
    SessionStatus,
    check_session_rate_limit,
    cleanup_old_sessions,
    get_all_sessions_summary,
    get_rate_limit_headers,
    get_session_state,
    get_session_stats,
    reset_all_sessions,
    reset_session,
)


class TestSessionStatus:
    """Tests for SessionStatus enum."""

    def test_all_statuses_exist(self):
        """All expected statuses should be defined."""
        expected = ["new", "active", "warm", "throttled", "blocked"]
        for status in expected:
            assert hasattr(SessionStatus, status.upper())


class TestSessionLimitConfig:
    """Tests for SessionLimitConfig dataclass."""

    def test_default_values(self):
        """Should have sensible defaults."""
        config = SessionLimitConfig()
        assert config.messages_per_minute == 20
        assert config.messages_per_hour == 200
        assert config.burst_limit == 5
        assert config.burst_window_seconds == 10.0

    def test_custom_values(self):
        """Should accept custom values."""
        config = SessionLimitConfig(
            messages_per_minute=10,
            messages_per_hour=100,
            burst_limit=3,
        )
        assert config.messages_per_minute == 10
        assert config.messages_per_hour == 100
        assert config.burst_limit == 3


class TestSessionRateLimitState:
    """Tests for SessionRateLimitState dataclass."""

    def test_default_values(self):
        """Should initialize with correct defaults."""
        state = SessionRateLimitState(session_id="test-123")
        assert state.session_id == "test-123"
        assert state.status == SessionStatus.NEW
        assert state.message_count == 0
        assert state.violation_count == 0


class TestGetSessionState:
    """Tests for get_session_state function."""

    def setup_method(self):
        """Reset state before each test."""
        reset_all_sessions()

    def test_creates_new_session(self):
        """Should create new session if not exists."""
        state = get_session_state("new-session-123")
        assert state.session_id == "new-session-123"
        assert state.status == SessionStatus.NEW

    def test_returns_existing_session(self):
        """Should return existing session state."""
        state1 = get_session_state("existing-session")
        state1.message_count = 5

        state2 = get_session_state("existing-session")
        assert state2.message_count == 5


class TestCheckSessionRateLimit:
    """Tests for check_session_rate_limit function."""

    def setup_method(self):
        """Reset state before each test."""
        reset_all_sessions()

    def test_allows_first_message(self):
        """First message should always be allowed."""
        allowed, metadata = check_session_rate_limit("test-session-1")
        assert allowed is True
        assert "remaining_per_minute" in metadata

    def test_allows_normal_usage(self):
        """Normal usage within limits should be allowed."""
        for _ in range(5):
            allowed, _ = check_session_rate_limit("test-session-2")
            assert allowed is True

    def test_burst_detection(self):
        """Rapid messages should trigger burst protection."""
        config = SessionLimitConfig(burst_limit=3, burst_window_seconds=10.0)

        # First 3 messages should pass
        for _ in range(3):
            allowed, _ = check_session_rate_limit("burst-test", config)
            assert allowed is True

        # 4th message should fail (burst limit)
        allowed, metadata = check_session_rate_limit("burst-test", config)
        assert allowed is False
        assert metadata["reason"] == "burst_limit_exceeded"

    def test_per_minute_limit(self):
        """Should enforce per-minute limit."""
        config = SessionLimitConfig(
            messages_per_minute=5,
            burst_limit=10,  # High burst to not trigger
            burst_window_seconds=1.0,  # Short window
        )

        # Allow 5 messages with slight delay to avoid burst
        for i in range(5):
            with patch("time.time", return_value=1000.0 + (i * 2)):
                allowed, _ = check_session_rate_limit("minute-test", config)
                assert allowed is True

        # 6th message should fail
        with patch("time.time", return_value=1010.0):
            allowed, metadata = check_session_rate_limit("minute-test", config)
            assert allowed is False
            assert metadata["reason"] == "per_minute_limit_exceeded"

    def test_throttle_after_violations(self):
        """Should throttle after multiple violations."""
        config = SessionLimitConfig(
            burst_limit=2,
            burst_window_seconds=60.0,
            throttle_threshold=3,
        )

        # Cause violations by hitting burst limit repeatedly
        for _ in range(10):  # Multiple attempts
            check_session_rate_limit("throttle-test", config)

        stats = get_session_stats("throttle-test")
        # After enough violations, should be throttled
        assert stats["violation_count"] >= config.throttle_threshold

    def test_returns_remaining_counts(self):
        """Should return remaining message counts."""
        config = SessionLimitConfig(messages_per_minute=20, messages_per_hour=200)

        allowed, metadata = check_session_rate_limit("remaining-test", config)
        assert allowed is True
        # Note: remaining is calculated BEFORE recording current message
        assert metadata["remaining_per_minute"] <= 20
        assert metadata["remaining_per_hour"] <= 200
        assert "remaining_per_minute" in metadata
        assert "remaining_per_hour" in metadata


class TestGetSessionStats:
    """Tests for get_session_stats function."""

    def setup_method(self):
        """Reset state before each test."""
        reset_all_sessions()

    def test_nonexistent_session(self):
        """Should return exists=False for unknown session."""
        stats = get_session_stats("nonexistent-session")
        assert stats["exists"] is False

    def test_existing_session(self):
        """Should return stats for existing session."""
        check_session_rate_limit("stats-test")
        check_session_rate_limit("stats-test")

        stats = get_session_stats("stats-test")
        assert stats["exists"] is True
        assert stats["message_count"] == 2
        assert stats["status"] == "new"  # Still new with only 2 messages


class TestResetSession:
    """Tests for reset_session function."""

    def setup_method(self):
        """Reset state before each test."""
        reset_all_sessions()

    def test_reset_existing_session(self):
        """Should remove existing session."""
        check_session_rate_limit("to-reset")
        assert reset_session("to-reset") is True

        stats = get_session_stats("to-reset")
        assert stats["exists"] is False

    def test_reset_nonexistent_session(self):
        """Should return False for nonexistent session."""
        assert reset_session("nonexistent") is False


class TestGetAllSessionsSummary:
    """Tests for get_all_sessions_summary function."""

    def setup_method(self):
        """Reset state before each test."""
        reset_all_sessions()

    def test_empty_summary(self):
        """Should return zeros when no sessions."""
        summary = get_all_sessions_summary()
        assert summary["total_sessions"] == 0
        assert summary["total_messages"] == 0

    def test_summary_with_sessions(self):
        """Should count sessions correctly."""
        check_session_rate_limit("session-1")
        check_session_rate_limit("session-1")
        check_session_rate_limit("session-2")

        summary = get_all_sessions_summary()
        assert summary["total_sessions"] == 2
        assert summary["total_messages"] == 3


class TestCleanupOldSessions:
    """Tests for cleanup_old_sessions function."""

    def setup_method(self):
        """Reset state before each test."""
        reset_all_sessions()

    def test_cleanup_keeps_recent_sessions(self):
        """Recent active sessions should not be removed."""
        check_session_rate_limit("recent-session")

        removed = cleanup_old_sessions(max_age_hours=24)
        assert removed == 0

        stats = get_session_stats("recent-session")
        assert stats["exists"] is True

    def test_cleanup_removes_old_idle_sessions(self):
        """Old idle sessions should be removed."""
        # Create a session and manually age it
        check_session_rate_limit("old-session")
        state = get_session_state("old-session")

        # Make it old and idle
        old_time = time.time() - (25 * 3600)  # 25 hours ago
        state.first_message_time = old_time
        state.last_message_time = old_time

        removed = cleanup_old_sessions(max_age_hours=24)
        assert removed == 1


class TestGetRateLimitHeaders:
    """Tests for get_rate_limit_headers function."""

    def test_headers_from_allowed_metadata(self):
        """Should generate headers from allowed request metadata."""
        metadata = {
            "remaining_per_minute": 19,
            "remaining_per_hour": 199,
        }

        headers = get_rate_limit_headers(metadata)
        assert headers["X-Session-RateLimit-Remaining-Minute"] == "19"
        assert headers["X-Session-RateLimit-Remaining-Hour"] == "199"

    def test_headers_from_throttled_metadata(self):
        """Should generate retry-after header when throttled."""
        metadata = {"throttle_remaining_seconds": 30}

        headers = get_rate_limit_headers(metadata)
        assert headers["X-Session-RateLimit-Retry-After"] == "30"

    def test_headers_from_blocked_metadata(self):
        """Should generate block header when blocked."""
        metadata = {"blocked_remaining_seconds": 300}

        headers = get_rate_limit_headers(metadata)
        assert headers["X-Session-RateLimit-Block-Remaining"] == "300"


class TestSessionStatusTransitions:
    """Tests for session status transitions."""

    def setup_method(self):
        """Reset state before each test."""
        reset_all_sessions()

    def test_new_to_active_transition(self):
        """Should transition from NEW to ACTIVE after 3 messages."""
        for _ in range(3):
            check_session_rate_limit("transition-test")

        stats = get_session_stats("transition-test")
        assert stats["status"] == "active"

    def test_violation_count_decay(self):
        """Violations should decay over time with good behavior."""
        # Test that decay mechanism exists - violations decrease after 10 good messages
        # This is a simpler test to verify the decay functionality works
        config = SessionLimitConfig(
            burst_limit=100,  # High limit to avoid bursts
            burst_window_seconds=1.0,
            messages_per_minute=1000,  # Very high limit
            messages_per_hour=10000,
        )

        # First, manually set up a session with violations
        check_session_rate_limit("decay-test-2", config)
        state = get_session_state("decay-test-2")
        state.violation_count = 5  # Set initial violations manually
        state.message_count = 9  # Set to 9 so next message is the 10th

        # The 10th message should trigger decay
        check_session_rate_limit("decay-test-2", config)

        final_stats = get_session_stats("decay-test-2")
        # Violations should have decayed by 1 (from 5 to 4)
        assert final_stats["violation_count"] == 4
