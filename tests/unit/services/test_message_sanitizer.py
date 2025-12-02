"""
Tests for Message Sanitizer module.

Validates sanitization, validation, and edge case handling.

Author: Anderson Henrique da Silva
Created: 2025-12-02
"""

from src.services.message_sanitizer import (
    MAX_MESSAGE_LENGTH,
    MessageValidationStatus,
    extract_safe_log_message,
    get_edge_case_response,
    is_valid_session_id,
    sanitize_message,
)


class TestSanitizeMessage:
    """Tests for the sanitize_message function."""

    def test_valid_message_returns_valid_status(self):
        """Normal messages should return VALID status."""
        result = sanitize_message("Olá, quero investigar contratos")
        assert result.status == MessageValidationStatus.VALID
        assert result.sanitized_message == "Olá, quero investigar contratos"
        assert result.warning is None

    def test_empty_message_returns_empty_status(self):
        """Empty messages should return EMPTY status."""
        result = sanitize_message("")
        assert result.status == MessageValidationStatus.EMPTY
        assert result.suggested_response is not None

    def test_none_message_returns_empty_status(self):
        """None messages should return EMPTY status."""
        result = sanitize_message(None)
        assert result.status == MessageValidationStatus.EMPTY
        assert result.suggested_response is not None

    def test_whitespace_only_returns_empty_status(self):
        """Whitespace-only messages should return EMPTY status."""
        result = sanitize_message("   \t\n   ")
        assert result.status == MessageValidationStatus.EMPTY

    def test_too_short_message_returns_too_short_status(self):
        """Single character messages should return TOO_SHORT status."""
        result = sanitize_message("a")
        assert result.status == MessageValidationStatus.TOO_SHORT
        assert "curta" in result.warning.lower()

    def test_message_length_boundary(self):
        """Messages at MIN_MESSAGE_LENGTH should be valid."""
        result = sanitize_message("ab")  # Exactly MIN_MESSAGE_LENGTH
        assert result.status == MessageValidationStatus.VALID

    def test_long_message_truncation(self):
        """Messages exceeding MAX_MESSAGE_LENGTH should be truncated."""
        long_message = "a" * (MAX_MESSAGE_LENGTH + 100)
        result = sanitize_message(long_message)
        assert len(result.sanitized_message) == MAX_MESSAGE_LENGTH

    def test_xss_injection_detected(self):
        """XSS injection attempts should be detected and sanitized."""
        result = sanitize_message("<script>alert('xss')</script>")
        assert result.status == MessageValidationStatus.POTENTIAL_INJECTION
        assert "<script>" not in result.sanitized_message
        assert "&lt;script&gt;" in result.sanitized_message

    def test_sql_injection_detected(self):
        """SQL injection attempts should be detected."""
        tests = [
            "SELECT * FROM users",
            "INSERT INTO table VALUES",
            "DROP TABLE contracts",
            "' OR '1'='1",
            "; --",
            "UNION SELECT password FROM users",
        ]
        for test_msg in tests:
            result = sanitize_message(test_msg)
            assert (
                result.status == MessageValidationStatus.POTENTIAL_INJECTION
            ), f"Failed to detect SQL injection: {test_msg}"

    def test_template_injection_detected(self):
        """Template injection attempts should be detected."""
        result = sanitize_message("{{constructor.constructor('return this')()}}")
        assert result.status == MessageValidationStatus.POTENTIAL_INJECTION

    def test_event_handler_injection_detected(self):
        """Event handler injection should be detected."""
        result = sanitize_message("<img src=x onerror=alert(1)>")
        assert result.status == MessageValidationStatus.POTENTIAL_INJECTION

    def test_gibberish_detection(self):
        """Repeated characters should be detected as gibberish."""
        result = sanitize_message("aaaaaaaaaaaaaaaaaaaaaa")
        assert result.status == MessageValidationStatus.GIBBERISH
        assert result.suggested_response is not None

    def test_special_chars_only(self):
        """Messages with only special characters should be handled."""
        # Note: Some special chars become HTML entities (& -> &amp;) which contain letters
        result = sanitize_message("!@#$%^*()")  # Without &
        assert result.status == MessageValidationStatus.ONLY_SPECIAL_CHARS

    def test_emojis_only(self):
        """Messages with only emojis should be handled."""
        # Note: Some emojis might be stripped during sanitization
        result = sanitize_message("🇧🇷🎯🔍")
        # Should either be valid or only_special_chars depending on implementation
        assert result.status in [
            MessageValidationStatus.VALID,
            MessageValidationStatus.ONLY_SPECIAL_CHARS,
        ]

    def test_mixed_content_is_valid(self):
        """Messages with text and special chars should be valid."""
        result = sanitize_message("Olá! 🇧🇷 Como vai?")
        assert result.status == MessageValidationStatus.VALID

    def test_unicode_normalization(self):
        """Unicode characters should be normalized."""
        # é can be represented in multiple ways in Unicode
        result = sanitize_message("Caf\u0065\u0301")  # e + combining acute
        assert result.status == MessageValidationStatus.VALID

    def test_newlines_preserved_but_normalized(self):
        """Newlines should be normalized to spaces."""
        result = sanitize_message("Linha 1\nLinha 2\nLinha 3")
        assert result.status == MessageValidationStatus.VALID
        # Multiple whitespaces collapsed
        assert "  " not in result.sanitized_message

    def test_control_characters_removed(self):
        """Control characters (except newlines/tabs) should be removed."""
        result = sanitize_message("Test\x00\x01\x02message")
        assert "\x00" not in result.sanitized_message
        assert "\x01" not in result.sanitized_message
        assert "\x02" not in result.sanitized_message

    def test_html_escaped(self):
        """HTML special characters should be escaped."""
        result = sanitize_message("<b>Bold</b> & 'quotes'")
        assert "&lt;" in result.sanitized_message
        assert "&gt;" in result.sanitized_message
        assert "&amp;" in result.sanitized_message


class TestExtractSafeLogMessage:
    """Tests for extract_safe_log_message function."""

    def test_truncation(self):
        """Long messages should be truncated for logging."""
        long_message = "a" * 200
        safe_log = extract_safe_log_message(long_message, max_length=100)
        assert len(safe_log) <= 103  # 100 + "..."
        assert safe_log.endswith("...")

    def test_empty_message(self):
        """Empty messages should return [empty]."""
        assert extract_safe_log_message("") == "[empty]"
        assert extract_safe_log_message(None) == "[empty]"

    def test_newlines_removed(self):
        """Newlines should be removed for log readability."""
        safe_log = extract_safe_log_message("Line 1\nLine 2")
        assert "\n" not in safe_log

    def test_short_message_unchanged(self):
        """Short messages should be unchanged."""
        safe_log = extract_safe_log_message("Hello", max_length=100)
        assert safe_log == "Hello"


class TestIsValidSessionId:
    """Tests for is_valid_session_id function."""

    def test_valid_uuid_v4(self):
        """Valid UUID v4 should return True."""
        assert is_valid_session_id("123e4567-e89b-42d3-a456-426614174000")

    def test_none_is_valid(self):
        """None session ID should be valid (auto-generated)."""
        assert is_valid_session_id(None)

    def test_invalid_uuid_format(self):
        """Invalid UUID formats should return False."""
        assert not is_valid_session_id("not-a-uuid")
        assert not is_valid_session_id("123")
        assert not is_valid_session_id(
            "123e4567-e89b-12d3-a456-426614174000"
        )  # v1 not v4
        assert not is_valid_session_id("")

    def test_uppercase_uuid(self):
        """Uppercase UUIDs should be valid."""
        assert is_valid_session_id("123E4567-E89B-42D3-A456-426614174000")


class TestGetEdgeCaseResponse:
    """Tests for get_edge_case_response function."""

    def test_empty_response(self):
        """EMPTY status should have a response."""
        response = get_edge_case_response(MessageValidationStatus.EMPTY)
        assert response is not None
        assert "message" in response
        assert "suggested_actions" in response

    def test_too_short_response(self):
        """TOO_SHORT status should have a response."""
        response = get_edge_case_response(MessageValidationStatus.TOO_SHORT)
        assert response is not None
        assert "message" in response

    def test_gibberish_response(self):
        """GIBBERISH status should have a response."""
        response = get_edge_case_response(MessageValidationStatus.GIBBERISH)
        assert response is not None
        assert "message" in response

    def test_injection_response(self):
        """POTENTIAL_INJECTION status should have a response."""
        response = get_edge_case_response(MessageValidationStatus.POTENTIAL_INJECTION)
        assert response is not None
        assert "message" in response

    def test_valid_no_response(self):
        """VALID status should return None (no special response needed)."""
        response = get_edge_case_response(MessageValidationStatus.VALID)
        assert response is None


class TestBrazilianPortuguese:
    """Tests for Brazilian Portuguese specific messages."""

    def test_common_brazilian_greeting(self):
        """Common Brazilian greetings should be valid."""
        greetings = [
            "Olá, tudo bem?",
            "Oi, bom dia!",
            "E aí, beleza?",
            "Fala, galera!",
        ]
        for greeting in greetings:
            result = sanitize_message(greeting)
            assert (
                result.status == MessageValidationStatus.VALID
            ), f"Failed for: {greeting}"

    def test_common_investigation_queries(self):
        """Common investigation queries should be valid."""
        queries = [
            "Quero investigar contratos do Ministério da Saúde",
            "Busque contratos da educação em 2024",
            "Contratos do Ministério da Defesa",
            "Licitações de tecnologia",
            "Gastos com saúde em Minas Gerais",
        ]
        for query in queries:
            result = sanitize_message(query)
            assert (
                result.status == MessageValidationStatus.VALID
            ), f"Failed for: {query}"

    def test_accented_characters(self):
        """Accented characters common in Portuguese should be preserved."""
        result = sanitize_message("Investigação de órgãos públicos com ações")
        assert "ã" in result.sanitized_message
        assert "ó" in result.sanitized_message
        assert "ç" in result.sanitized_message
        assert "õ" in result.sanitized_message


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_structure(self):
        """ValidationResult should have all required fields."""
        result = sanitize_message("Test message")
        assert hasattr(result, "status")
        assert hasattr(result, "sanitized_message")
        assert hasattr(result, "original_message")
        assert hasattr(result, "warning")
        assert hasattr(result, "suggested_response")

    def test_original_message_preserved(self):
        """Original message should be preserved in result."""
        original = "  Spaces around  "
        result = sanitize_message(original)
        assert result.original_message == original
        assert result.sanitized_message == "Spaces around"
