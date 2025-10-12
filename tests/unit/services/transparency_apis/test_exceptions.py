"""
Unit tests for federal API custom exceptions.

Tests the exception hierarchy, context preservation, and factory methods.
"""

import pytest

from src.services.transparency_apis.federal_apis.exceptions import (
    FederalAPIError,
    NetworkError,
    TimeoutError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    ServerError,
    ValidationError,
    ParseError,
    CacheError,
    exception_from_response,
)


class TestExceptionHierarchy:
    """Test exception inheritance and base functionality."""

    def test_federal_api_error_base(self):
        """Test base FederalAPIError exception."""
        error = FederalAPIError(
            "Test error",
            api_name="TestAPI",
            status_code=500,
            response_data={"detail": "error"}
        )

        assert str(error) == "TestAPI: Test error (HTTP 500)"
        assert error.api_name == "TestAPI"
        assert error.status_code == 500
        assert error.response_data == {"detail": "error"}
        assert error.original_error is None

    def test_network_error_inheritance(self):
        """Test NetworkError inherits from FederalAPIError."""
        error = NetworkError("Connection failed", api_name="TestAPI")

        assert isinstance(error, FederalAPIError)
        assert isinstance(error, NetworkError)
        assert str(error) == "TestAPI: Connection failed"

    def test_timeout_error_inheritance(self):
        """Test TimeoutError inherits from NetworkError."""
        error = TimeoutError(
            "Request timeout",
            api_name="TestAPI",
            timeout_seconds=30
        )

        assert isinstance(error, FederalAPIError)
        assert isinstance(error, NetworkError)
        assert isinstance(error, TimeoutError)
        assert error.timeout_seconds == 30

    def test_all_exceptions_inherit_from_base(self):
        """Test all custom exceptions inherit from FederalAPIError."""
        exceptions = [
            NetworkError("msg", api_name="API"),
            TimeoutError("msg", api_name="API", timeout_seconds=10),
            RateLimitError("msg", api_name="API"),
            AuthenticationError("msg", api_name="API"),
            NotFoundError("msg", api_name="API"),
            ServerError("msg", api_name="API"),
            ValidationError("msg", api_name="API"),
            ParseError("msg", api_name="API"),
            CacheError("msg", api_name="API"),
        ]

        for exc in exceptions:
            assert isinstance(exc, FederalAPIError)


class TestOriginalErrorChaining:
    """Test exception chaining with original errors."""

    def test_original_error_preserved(self):
        """Test that original error is preserved in chain."""
        original = ValueError("Original error")
        error = NetworkError(
            "Network failed",
            api_name="TestAPI",
            original_error=original
        )

        assert error.original_error is original
        assert isinstance(error.original_error, ValueError)

    def test_error_chain_string_representation(self):
        """Test string representation includes original error."""
        original = ConnectionError("Connection refused")
        error = NetworkError(
            "Network failed",
            api_name="TestAPI",
            original_error=original
        )

        error_str = str(error)
        assert "TestAPI" in error_str
        assert "Network failed" in error_str


class TestSpecificExceptions:
    """Test specific exception types and their attributes."""

    def test_timeout_error_with_seconds(self):
        """Test TimeoutError stores timeout duration."""
        error = TimeoutError(
            "Timeout occurred",
            api_name="IBGE",
            timeout_seconds=30.5,
            status_code=408
        )

        assert error.timeout_seconds == 30.5
        assert error.status_code == 408
        assert "IBGE" in str(error)

    def test_rate_limit_error_with_retry_after(self):
        """Test RateLimitError stores retry_after value."""
        error = RateLimitError(
            "Rate limit exceeded",
            api_name="DataSUS",
            retry_after=60
        )

        assert error.retry_after == 60
        assert error.status_code == 429
        assert "DataSUS" in str(error)
        assert "60" in str(error)  # retry_after is included in message

    def test_rate_limit_error_without_retry_after(self):
        """Test RateLimitError without retry_after header."""
        error = RateLimitError(
            "Rate limit exceeded",
            api_name="INEP"
        )

        assert error.retry_after is None
        assert error.status_code == 429

    def test_not_found_error_with_resource_id(self):
        """Test NotFoundError stores resource identifier."""
        error = NotFoundError(
            "Resource not found",
            api_name="IBGE",
            resource_id="municipality-123"
        )

        assert error.resource_id == "municipality-123"
        assert error.status_code == 404
        assert "municipality-123" in str(error)  # resource_id is included in message

    def test_authentication_error_attributes(self):
        """Test AuthenticationError with different status codes."""
        # Test 401 Unauthorized
        error_401 = AuthenticationError(
            "Invalid credentials",
            api_name="TestAPI",
            status_code=401
        )
        assert error_401.status_code == 401

        # Test 403 Forbidden
        error_403 = AuthenticationError(
            "Access forbidden",
            api_name="TestAPI",
            status_code=403
        )
        assert error_403.status_code == 403

    def test_server_error_attributes(self):
        """Test ServerError for different 5xx codes."""
        error = ServerError(
            "Internal server error",
            api_name="DataSUS",
            status_code=503,
            response_data={"message": "Service unavailable"}
        )

        assert error.status_code == 503
        assert error.response_data["message"] == "Service unavailable"

    def test_validation_error_with_details(self):
        """Test ValidationError with validation details."""
        error = ValidationError(
            "Invalid data",
            api_name="INEP",
            status_code=400,
            response_data={"errors": ["field1 is required"]}
        )

        assert error.status_code == 400
        assert "errors" in error.response_data

    def test_parse_error_attributes(self):
        """Test ParseError for malformed responses."""
        error = ParseError(
            "Failed to parse JSON",
            api_name="IBGE",
            response_data={"raw": "malformed json"}
        )

        assert "parse" in str(error).lower()
        assert error.response_data["raw"] == "malformed json"


class TestExceptionFactory:
    """Test exception_from_response factory method."""

    def test_factory_creates_validation_error_400(self):
        """Test factory creates ValidationError for 400."""
        error = exception_from_response(
            400,
            "Bad request",
            api_name="TestAPI",
            response_data={"detail": "invalid"}
        )

        assert isinstance(error, ValidationError)
        assert error.status_code == 400
        assert "TestAPI" in str(error)

    def test_factory_creates_authentication_error_401(self):
        """Test factory creates AuthenticationError for 401."""
        error = exception_from_response(
            401,
            "Unauthorized",
            api_name="TestAPI"
        )

        assert isinstance(error, AuthenticationError)
        assert error.status_code == 401

    def test_factory_creates_authentication_error_403(self):
        """Test factory creates AuthenticationError for 403."""
        error = exception_from_response(
            403,
            "Forbidden",
            api_name="TestAPI"
        )

        assert isinstance(error, AuthenticationError)
        assert error.status_code == 403

    def test_factory_creates_not_found_error_404(self):
        """Test factory creates NotFoundError for 404."""
        error = exception_from_response(
            404,
            "Not found",
            api_name="IBGE",
            response_data={"resource": "state-99"}
        )

        assert isinstance(error, NotFoundError)
        assert error.status_code == 404
        # Factory doesn't extract resource_id, but creates NotFoundError
        assert error.resource_id is None

    def test_factory_creates_rate_limit_error_429(self):
        """Test factory creates RateLimitError for 429."""
        error = exception_from_response(
            429,
            "Too many requests",
            api_name="DataSUS"
        )

        assert isinstance(error, RateLimitError)
        assert error.status_code == 429
        assert error.retry_after is None  # No retry_after in response_data

    def test_factory_creates_rate_limit_error_with_retry_after(self):
        """Test factory extracts retry_after from response_data."""
        error = exception_from_response(
            429,
            "Too many requests",
            api_name="DataSUS",
            response_data={"retry_after": 120}
        )

        assert isinstance(error, RateLimitError)
        assert error.status_code == 429
        assert error.retry_after == 120

    def test_factory_creates_server_error_500(self):
        """Test factory creates ServerError for 500."""
        error = exception_from_response(
            500,
            "Internal server error",
            api_name="INEP"
        )

        assert isinstance(error, ServerError)
        assert error.status_code == 500

    def test_factory_creates_server_error_502(self):
        """Test factory creates ServerError for 502."""
        error = exception_from_response(
            502,
            "Bad gateway",
            api_name="TestAPI"
        )

        assert isinstance(error, ServerError)
        assert error.status_code == 502

    def test_factory_creates_server_error_503(self):
        """Test factory creates ServerError for 503."""
        error = exception_from_response(
            503,
            "Service unavailable",
            api_name="TestAPI"
        )

        assert isinstance(error, ServerError)
        assert error.status_code == 503

    def test_factory_creates_timeout_error_504(self):
        """Test factory creates TimeoutError for 504."""
        error = exception_from_response(
            504,
            "Gateway timeout",
            api_name="TestAPI"
        )

        assert isinstance(error, TimeoutError)
        assert error.status_code == 504

    def test_factory_creates_federal_api_error_for_unknown(self):
        """Test factory creates generic FederalAPIError for unknown status."""
        error = exception_from_response(
            418,  # I'm a teapot
            "Unknown error",
            api_name="TestAPI"
        )

        assert isinstance(error, FederalAPIError)
        assert error.status_code == 418

    def test_factory_preserves_all_context(self):
        """Test factory preserves all context information."""
        response_data = {
            "message": "Error details",
            "code": "ERR_001",
            "timestamp": "2025-10-12T18:00:00Z"
        }

        error = exception_from_response(
            500,
            "Server error",
            api_name="IBGE",
            response_data=response_data
        )

        assert error.api_name == "IBGE"
        assert error.status_code == 500
        assert error.response_data == response_data
        assert "Server error" in error.message


class TestExceptionEquality:
    """Test exception comparison and equality."""

    def test_same_exception_type_and_message(self):
        """Test exceptions with same type and message."""
        error1 = NetworkError("Connection failed", api_name="API1")
        error2 = NetworkError("Connection failed", api_name="API1")

        # Exceptions are different instances
        assert error1 is not error2
        # But have same attributes
        assert type(error1) == type(error2)
        assert error1.message == error2.message
        assert error1.api_name == error2.api_name

    def test_different_api_names(self):
        """Test exceptions with different api_names."""
        error1 = NetworkError("Error", api_name="IBGE")
        error2 = NetworkError("Error", api_name="DataSUS")

        assert error1.api_name != error2.api_name
        assert str(error1) != str(error2)
