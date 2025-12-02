"""
Tests for Chat Metrics Service.

Tests the Prometheus metrics and in-memory tracking for chat system.

Author: Anderson Henrique da Silva
Created: 2025-12-02
"""

import pytest

from src.services.chat_metrics import (
    PROMETHEUS_AVAILABLE,
    ChatMetricsContext,
    ChatMetricsData,
    MetricCategory,
    get_chat_metrics_summary,
    increment_session_count,
    record_agent_usage,
    record_error,
    record_intent_detection,
    record_request,
    record_response_time,
    reset_metrics,
    update_active_sessions,
)


class TestMetricCategory:
    """Tests for MetricCategory enum."""

    def test_all_categories_exist(self):
        """All expected categories should be defined."""
        expected = [
            "greeting",
            "help",
            "investigate",
            "analyze",
            "report",
            "about_system",
            "question",
            "other",
        ]
        for cat in expected:
            assert hasattr(MetricCategory, cat.upper())

    def test_category_values(self):
        """Category values should match lowercase names."""
        assert MetricCategory.GREETING.value == "greeting"
        assert MetricCategory.INVESTIGATE.value == "investigate"
        assert MetricCategory.ANALYZE.value == "analyze"


class TestChatMetricsData:
    """Tests for ChatMetricsData dataclass."""

    def test_default_values(self):
        """Should initialize with correct defaults."""
        data = ChatMetricsData()
        assert data.response_times == {}
        assert data.agent_usage == {}
        assert data.errors_by_type == {}
        assert data.total_requests == 0
        assert data.successful_requests == 0
        assert data.failed_requests == 0
        assert data.active_sessions == 0
        assert data.total_sessions == 0

    def test_intent_detections_default(self):
        """Intent detections should have correct default keys."""
        data = ChatMetricsData()
        assert "correct" in data.intent_detections
        assert "incorrect" in data.intent_detections
        assert "unknown" in data.intent_detections


class TestRecordResponseTime:
    """Tests for record_response_time function."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_record_single_response_time(self):
        """Should record a single response time."""
        record_response_time("greeting", "drummond", 1.5)
        summary = get_chat_metrics_summary()
        assert "greeting:drummond" in summary["response_times"]
        assert summary["response_times"]["greeting:drummond"]["count"] == 1

    def test_record_multiple_response_times(self):
        """Should record multiple response times."""
        record_response_time("greeting", "drummond", 1.0)
        record_response_time("greeting", "drummond", 2.0)
        record_response_time("greeting", "drummond", 3.0)

        summary = get_chat_metrics_summary()
        stats = summary["response_times"]["greeting:drummond"]
        assert stats["count"] == 3
        assert stats["avg"] == 2.0
        assert stats["min"] == 1.0
        assert stats["max"] == 3.0

    def test_response_time_different_categories(self):
        """Should track different categories separately."""
        record_response_time("greeting", "drummond", 1.0)
        record_response_time("investigate", "zumbi", 5.0)

        summary = get_chat_metrics_summary()
        assert "greeting:drummond" in summary["response_times"]
        assert "investigate:zumbi" in summary["response_times"]


class TestRecordIntentDetection:
    """Tests for record_intent_detection function."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_record_correct_detection(self):
        """Should record correct intent detection."""
        record_intent_detection("greeting", "correct")
        summary = get_chat_metrics_summary()
        assert summary["intent_detection"]["breakdown"]["correct"] == 1

    def test_record_incorrect_detection(self):
        """Should record incorrect intent detection."""
        record_intent_detection("investigate", "incorrect")
        summary = get_chat_metrics_summary()
        assert summary["intent_detection"]["breakdown"]["incorrect"] == 1

    def test_calculate_accuracy(self):
        """Should calculate intent accuracy correctly."""
        record_intent_detection("greeting", "correct")
        record_intent_detection("greeting", "correct")
        record_intent_detection("greeting", "incorrect")
        record_intent_detection("greeting", "unknown")

        summary = get_chat_metrics_summary()
        # 2 correct out of 4 total = 50%
        assert summary["intent_detection"]["accuracy_pct"] == 50.0


class TestRecordAgentUsage:
    """Tests for record_agent_usage function."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_record_single_agent(self):
        """Should record single agent usage."""
        record_agent_usage("drummond", "greeting")
        summary = get_chat_metrics_summary()
        assert "drummond" in summary["agent_usage"]
        assert summary["agent_usage"]["drummond"]["count"] == 1

    def test_record_multiple_agents(self):
        """Should record multiple agents."""
        record_agent_usage("drummond", "greeting")
        record_agent_usage("drummond", "help")
        record_agent_usage("zumbi", "investigate")

        summary = get_chat_metrics_summary()
        assert summary["agent_usage"]["drummond"]["count"] == 2
        assert summary["agent_usage"]["zumbi"]["count"] == 1

    def test_calculate_percentage(self):
        """Should calculate agent usage percentage."""
        record_agent_usage("drummond", "greeting")
        record_agent_usage("drummond", "greeting")
        record_agent_usage("drummond", "greeting")
        record_agent_usage("zumbi", "investigate")

        summary = get_chat_metrics_summary()
        # drummond: 3/4 = 75%, zumbi: 1/4 = 25%
        assert summary["agent_usage"]["drummond"]["percentage"] == 75.0
        assert summary["agent_usage"]["zumbi"]["percentage"] == 25.0


class TestRecordError:
    """Tests for record_error function."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_record_single_error(self):
        """Should record a single error."""
        record_error("timeout", "drummond")
        summary = get_chat_metrics_summary()
        assert "timeout" in summary["errors_by_type"]
        assert summary["errors_by_type"]["timeout"] == 1

    def test_increment_failed_requests(self):
        """Should increment failed requests count."""
        record_error("timeout")
        record_error("llm_error")

        summary = get_chat_metrics_summary()
        assert summary["requests"]["failed"] == 2


class TestRecordRequest:
    """Tests for record_request function."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_record_successful_request(self):
        """Should record successful request."""
        record_request("success", "/message")
        summary = get_chat_metrics_summary()
        assert summary["requests"]["total"] == 1
        assert summary["requests"]["successful"] == 1

    def test_record_error_request(self):
        """Should record error request."""
        record_request("error", "/stream")
        summary = get_chat_metrics_summary()
        assert summary["requests"]["total"] == 1
        assert summary["requests"]["successful"] == 0

    def test_calculate_error_rate(self):
        """Should calculate error rate correctly."""
        record_request("success")
        record_request("success")
        record_request("error")  # This counts as request
        record_error("timeout")  # This only increments failed count

        summary = get_chat_metrics_summary()
        # 1 failed out of 3 total requests = 33.33%
        assert summary["requests"]["error_rate_pct"] == 33.33


class TestSessionTracking:
    """Tests for session tracking functions."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_update_active_sessions(self):
        """Should update active sessions count."""
        update_active_sessions(5)
        summary = get_chat_metrics_summary()
        assert summary["sessions"]["active"] == 5

    def test_increment_session_count(self):
        """Should increment total sessions."""
        increment_session_count()
        increment_session_count()
        summary = get_chat_metrics_summary()
        assert summary["sessions"]["total"] == 2


class TestGetChatMetricsSummary:
    """Tests for get_chat_metrics_summary function."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_summary_structure(self):
        """Summary should have all required sections."""
        summary = get_chat_metrics_summary()
        assert "timestamp" in summary
        assert "requests" in summary
        assert "sessions" in summary
        assert "response_times" in summary
        assert "intent_detection" in summary
        assert "agent_usage" in summary
        assert "errors_by_type" in summary

    def test_summary_timestamp_format(self):
        """Timestamp should be ISO format."""
        summary = get_chat_metrics_summary()
        # Should contain date separator
        assert "T" in summary["timestamp"]


class TestResetMetrics:
    """Tests for reset_metrics function."""

    def test_reset_clears_all_data(self):
        """Reset should clear all metrics."""
        record_response_time("greeting", "drummond", 1.0)
        record_agent_usage("zumbi", "investigate")
        record_error("timeout")
        record_request("success")

        reset_metrics()
        summary = get_chat_metrics_summary()

        assert summary["requests"]["total"] == 0
        assert summary["response_times"] == {}
        assert summary["agent_usage"] == {}
        assert summary["errors_by_type"] == {}


class TestChatMetricsContext:
    """Tests for ChatMetricsContext context manager."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    @pytest.mark.asyncio
    async def test_context_records_response_time(self):
        """Context manager should record response time."""
        async with ChatMetricsContext(intent_type="greeting", agent_id="drummond"):
            pass  # Simulate processing

        summary = get_chat_metrics_summary()
        assert "greeting:drummond" in summary["response_times"]

    @pytest.mark.asyncio
    async def test_context_records_agent_usage(self):
        """Context manager should record agent usage."""
        async with ChatMetricsContext(intent_type="investigate", agent_id="zumbi"):
            pass

        summary = get_chat_metrics_summary()
        assert "zumbi" in summary["agent_usage"]

    @pytest.mark.asyncio
    async def test_context_records_success(self):
        """Context manager should record successful request."""
        async with ChatMetricsContext() as ctx:
            ctx.mark_success()

        summary = get_chat_metrics_summary()
        assert summary["requests"]["successful"] == 1

    @pytest.mark.asyncio
    async def test_context_records_error(self):
        """Context manager should record error."""
        async with ChatMetricsContext() as ctx:
            ctx.mark_error("timeout")

        summary = get_chat_metrics_summary()
        assert "timeout" in summary["errors_by_type"]

    @pytest.mark.asyncio
    async def test_context_update_agent(self):
        """Should allow updating agent mid-context."""
        async with ChatMetricsContext(agent_id="unknown") as ctx:
            ctx.update_agent("drummond")

        summary = get_chat_metrics_summary()
        assert "drummond" in summary["agent_usage"]

    @pytest.mark.asyncio
    async def test_context_update_intent(self):
        """Should allow updating intent mid-context."""
        async with ChatMetricsContext(intent_type="unknown") as ctx:
            ctx.update_intent("greeting")

        summary = get_chat_metrics_summary()
        assert "greeting:" in list(summary["response_times"].keys())[0]

    @pytest.mark.asyncio
    async def test_context_handles_exception(self):
        """Context should handle exceptions and record error."""
        try:
            async with ChatMetricsContext(agent_id="test"):
                raise ValueError("Test error")
        except ValueError:
            pass

        summary = get_chat_metrics_summary()
        assert "ValueError" in summary["errors_by_type"]


class TestPrometheusAvailability:
    """Tests for Prometheus client availability."""

    def test_prometheus_flag_exists(self):
        """PROMETHEUS_AVAILABLE flag should exist."""
        assert isinstance(PROMETHEUS_AVAILABLE, bool)
