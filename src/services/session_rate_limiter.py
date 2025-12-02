"""
Session-specific Rate Limiter for Chat System.

This module provides rate limiting per chat session to prevent abuse
while maintaining good UX for legitimate users.

Features:
1. Per-session message limits
2. Burst protection
3. Progressive backoff for abusive sessions
4. Session warmth tracking (new vs active sessions)

Author: Anderson Henrique da Silva
Created: 2025-12-02
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.core import get_logger

logger = get_logger(__name__)

# Constants for session status thresholds
WARM_SESSION_MESSAGE_COUNT = 10
WARM_SESSION_AGE_SECONDS = 300  # 5 minutes
ACTIVE_SESSION_MESSAGE_COUNT = 3
IDLE_THRESHOLD_SECONDS = 3600  # 1 hour


class SessionStatus(str, Enum):
    """Session status for rate limiting."""

    NEW = "new"  # First few messages
    ACTIVE = "active"  # Normal usage
    WARM = "warm"  # Established session
    THROTTLED = "throttled"  # Temporary slowdown
    BLOCKED = "blocked"  # Abuse detected


@dataclass
class SessionLimitConfig:
    """Configuration for session rate limits."""

    # Messages per window
    messages_per_minute: int = 20
    messages_per_hour: int = 200
    messages_per_day: int = 1000

    # Burst protection
    burst_limit: int = 5  # Max messages in quick succession
    burst_window_seconds: float = 10.0  # Window for burst detection

    # Progressive backoff
    throttle_threshold: int = 3  # Violations before throttling
    block_threshold: int = 10  # Violations before blocking

    # Cooldown
    throttle_duration_seconds: float = 60.0
    block_duration_seconds: float = 300.0


@dataclass
class SessionRateLimitState:
    """State tracking for a single session."""

    session_id: str
    status: SessionStatus = SessionStatus.NEW
    message_count: int = 0
    violation_count: int = 0
    last_message_time: float = 0.0
    message_timestamps: list[float] = field(default_factory=list)
    first_message_time: float = field(default_factory=time.time)
    throttle_until: float = 0.0
    block_until: float = 0.0


# In-memory session storage
_session_states: dict[str, SessionRateLimitState] = {}

# Default configuration
_default_config = SessionLimitConfig()


def get_session_state(session_id: str) -> SessionRateLimitState:
    """Get or create session state."""
    if session_id not in _session_states:
        _session_states[session_id] = SessionRateLimitState(session_id=session_id)
        logger.info(f"New session created: {session_id[:8]}...")
    return _session_states[session_id]


def check_session_rate_limit(  # noqa: C901, PLR0911, PLR0915
    session_id: str,
    config: SessionLimitConfig | None = None,
) -> tuple[bool, dict[str, Any]]:
    """
    Check if a session is within rate limits.

    Args:
        session_id: Chat session ID
        config: Optional custom configuration

    Returns:
        Tuple of (allowed, metadata)
    """
    if config is None:
        config = _default_config

    state = get_session_state(session_id)
    now = time.time()
    metadata: dict[str, Any] = {
        "session_id": session_id[:8] + "...",
        "status": state.status.value,
        "message_count": state.message_count,
    }

    # Check if blocked
    if state.status == SessionStatus.BLOCKED:
        if now < state.block_until:
            remaining = int(state.block_until - now)
            metadata["blocked_remaining_seconds"] = remaining
            metadata["reason"] = "session_blocked"
            logger.warning(f"Blocked session attempted access: {session_id[:8]}...")
            return False, metadata
        # Unblock
        state.status = SessionStatus.THROTTLED
        state.violation_count = config.throttle_threshold  # Keep some violations

    # Check if throttled
    if state.status == SessionStatus.THROTTLED:
        if now < state.throttle_until:
            remaining = int(state.throttle_until - now)
            metadata["throttle_remaining_seconds"] = remaining
            metadata["reason"] = "session_throttled"
            return False, metadata
        # Remove throttle
        state.status = SessionStatus.ACTIVE

    # Check burst limit
    recent_messages = [
        ts for ts in state.message_timestamps if now - ts < config.burst_window_seconds
    ]
    if len(recent_messages) >= config.burst_limit:
        state.violation_count += 1
        metadata["reason"] = "burst_limit_exceeded"
        metadata["violation_count"] = state.violation_count

        if state.violation_count >= config.block_threshold:
            state.status = SessionStatus.BLOCKED
            state.block_until = now + config.block_duration_seconds
            logger.warning(f"Session blocked for abuse: {session_id[:8]}...")
            metadata["status"] = "blocked"
            return False, metadata
        if state.violation_count >= config.throttle_threshold:
            state.status = SessionStatus.THROTTLED
            state.throttle_until = now + config.throttle_duration_seconds
            logger.info(f"Session throttled: {session_id[:8]}...")
            metadata["status"] = "throttled"
            return False, metadata

        return False, metadata

    # Check per-minute limit
    minute_ago = now - 60
    messages_last_minute = len(
        [ts for ts in state.message_timestamps if ts > minute_ago]
    )
    if messages_last_minute >= config.messages_per_minute:
        metadata["reason"] = "per_minute_limit_exceeded"
        metadata["limit"] = config.messages_per_minute
        metadata["current"] = messages_last_minute
        return False, metadata

    # Check per-hour limit
    hour_ago = now - 3600
    messages_last_hour = len([ts for ts in state.message_timestamps if ts > hour_ago])
    if messages_last_hour >= config.messages_per_hour:
        metadata["reason"] = "per_hour_limit_exceeded"
        metadata["limit"] = config.messages_per_hour
        metadata["current"] = messages_last_hour
        return False, metadata

    # All checks passed - record this message
    _record_message(state, now, config)
    metadata["allowed"] = True
    metadata["remaining_per_minute"] = config.messages_per_minute - messages_last_minute
    metadata["remaining_per_hour"] = config.messages_per_hour - messages_last_hour

    return True, metadata


def _record_message(
    state: SessionRateLimitState,
    timestamp: float,
    config: SessionLimitConfig,
) -> None:
    """Record a message in session state."""
    state.message_count += 1
    state.last_message_time = timestamp
    state.message_timestamps.append(timestamp)

    # Update session status based on activity
    session_age = timestamp - state.first_message_time
    if (
        state.message_count >= WARM_SESSION_MESSAGE_COUNT
        and session_age > WARM_SESSION_AGE_SECONDS
    ):
        state.status = SessionStatus.WARM
    elif state.message_count >= ACTIVE_SESSION_MESSAGE_COUNT:
        state.status = SessionStatus.ACTIVE
    else:
        state.status = SessionStatus.NEW

    # Cleanup old timestamps (keep last 24 hours)
    day_ago = timestamp - 86400
    state.message_timestamps = [ts for ts in state.message_timestamps if ts > day_ago]

    # Reduce violations over time (decay)
    if state.violation_count > 0 and state.message_count % 10 == 0:
        state.violation_count = max(0, state.violation_count - 1)


def get_session_stats(session_id: str) -> dict[str, Any]:
    """Get statistics for a session."""
    if session_id not in _session_states:
        return {"exists": False}

    state = _session_states[session_id]
    now = time.time()

    return {
        "exists": True,
        "session_id": session_id[:8] + "...",
        "status": state.status.value,
        "message_count": state.message_count,
        "violation_count": state.violation_count,
        "session_age_seconds": int(now - state.first_message_time),
        "last_message_seconds_ago": (
            int(now - state.last_message_time) if state.last_message_time > 0 else None
        ),
        "is_throttled": state.status == SessionStatus.THROTTLED
        and now < state.throttle_until,
        "is_blocked": state.status == SessionStatus.BLOCKED and now < state.block_until,
    }


def reset_session(session_id: str) -> bool:
    """Reset a session's rate limit state."""
    if session_id in _session_states:
        del _session_states[session_id]
        logger.info(f"Session reset: {session_id[:8]}...")
        return True
    return False


def get_all_sessions_summary() -> dict[str, Any]:
    """Get summary of all active sessions."""
    summary: dict[str, Any] = {
        "total_sessions": len(_session_states),
        "by_status": {status.value: 0 for status in SessionStatus},
        "total_messages": 0,
        "total_violations": 0,
    }

    for state in _session_states.values():
        summary["by_status"][state.status.value] += 1
        summary["total_messages"] += state.message_count
        summary["total_violations"] += state.violation_count

    return summary


def cleanup_old_sessions(max_age_hours: int = 24) -> int:
    """Remove sessions older than specified hours."""
    now = time.time()
    max_age_seconds = max_age_hours * 3600
    sessions_to_remove = []

    for session_id, state in _session_states.items():
        session_age = now - state.first_message_time
        idle_time = now - state.last_message_time if state.last_message_time > 0 else 0

        # Remove if session is old AND idle
        if session_age > max_age_seconds and idle_time > IDLE_THRESHOLD_SECONDS:
            sessions_to_remove.append(session_id)

    for session_id in sessions_to_remove:
        del _session_states[session_id]

    if sessions_to_remove:
        logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")

    return len(sessions_to_remove)


def reset_all_sessions() -> None:
    """Reset all session states. Useful for testing."""
    global _session_states  # noqa: PLW0603
    _session_states = {}


# Rate limit headers for API responses
def get_rate_limit_headers(metadata: dict[str, Any]) -> dict[str, str]:
    """Generate rate limit headers from metadata."""
    headers = {}

    if "remaining_per_minute" in metadata:
        headers["X-Session-RateLimit-Remaining-Minute"] = str(
            metadata["remaining_per_minute"]
        )

    if "remaining_per_hour" in metadata:
        headers["X-Session-RateLimit-Remaining-Hour"] = str(
            metadata["remaining_per_hour"]
        )

    if "throttle_remaining_seconds" in metadata:
        headers["X-Session-RateLimit-Retry-After"] = str(
            metadata["throttle_remaining_seconds"]
        )

    if "blocked_remaining_seconds" in metadata:
        headers["X-Session-RateLimit-Block-Remaining"] = str(
            metadata["blocked_remaining_seconds"]
        )

    return headers
