"""
Message Sanitization and Validation Service

This module provides centralized message validation and sanitization
for the chat system, handling edge cases gracefully.

Author: Anderson Henrique da Silva
Created: 2025-12-02
"""

import html
import re
import unicodedata
from dataclasses import dataclass
from enum import Enum

from src.core import get_logger

logger = get_logger(__name__)


class MessageValidationStatus(Enum):
    """Status of message validation."""

    VALID = "valid"
    EMPTY = "empty"
    TOO_SHORT = "too_short"
    TOO_LONG = "too_long"
    ONLY_SPECIAL_CHARS = "only_special_chars"
    POTENTIAL_INJECTION = "potential_injection"
    GIBBERISH = "gibberish"


@dataclass
class ValidationResult:
    """Result of message validation."""

    status: MessageValidationStatus
    sanitized_message: str
    original_message: str
    warning: str | None = None
    suggested_response: str | None = None


# Minimum message length for meaningful processing
MIN_MESSAGE_LENGTH = 2

# Maximum message length
MAX_MESSAGE_LENGTH = 2000

# Patterns that indicate potential injection attempts
INJECTION_PATTERNS = [
    r"<script[^>]*>",  # XSS script tags
    r"javascript:",  # JavaScript protocol
    r"on\w+\s*=",  # Event handlers (onclick, onload, etc)
    r"SELECT\s+.+\s+FROM",  # SQL SELECT
    r"INSERT\s+INTO",  # SQL INSERT
    r"UPDATE\s+.+\s+SET",  # SQL UPDATE
    r"DELETE\s+FROM",  # SQL DELETE
    r"DROP\s+TABLE",  # SQL DROP
    r"UNION\s+SELECT",  # SQL UNION injection
    r";\s*--",  # SQL comment injection
    r"'\s*OR\s+'1'\s*=\s*'1",  # SQL OR injection
    r"\{\{.*\}\}",  # Template injection
    r"\$\{.*\}",  # Expression injection
]

# Compiled injection patterns for performance
COMPILED_INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE) for pattern in INJECTION_PATTERNS
]

# Pattern for repeated characters (gibberish detection)
REPEATED_CHAR_PATTERN = re.compile(r"(.)\1{9,}")  # Same char 10+ times

# Pattern for valid Brazilian Portuguese text
VALID_TEXT_PATTERN = re.compile(
    r"[a-záàâãéêíóôõúüçA-ZÁÀÂÃÉÊÍÓÔÕÚÜÇ0-9\s\.,!?\-\(\)\[\]\"\'@#$%&*+=:;/\\]"
)


def sanitize_message(message: str) -> ValidationResult:
    """
    Sanitize and validate a user message.

    This function:
    1. Strips whitespace
    2. Normalizes unicode characters
    3. Removes/escapes potentially dangerous content
    4. Validates message length and content
    5. Detects injection attempts

    Args:
        message: Raw user message

    Returns:
        ValidationResult with status and sanitized message
    """
    original = message

    # Handle None or non-string
    if message is None:
        return ValidationResult(
            status=MessageValidationStatus.EMPTY,
            sanitized_message="",
            original_message="",
            warning="Mensagem vazia recebida",
            suggested_response="Olá! Como posso ajudá-lo hoje? Você pode me pedir para investigar contratos, analisar gastos públicos ou tirar dúvidas sobre transparência governamental.",
        )

    # Strip whitespace
    message = message.strip()

    # Check for empty message
    if not message:
        return ValidationResult(
            status=MessageValidationStatus.EMPTY,
            sanitized_message="",
            original_message=original,
            warning="Mensagem vazia após limpeza",
            suggested_response="Parece que sua mensagem está vazia. Como posso ajudá-lo? Experimente perguntar sobre contratos públicos ou gastos governamentais.",
        )

    # Normalize unicode (NFC form for consistency)
    message = unicodedata.normalize("NFC", message)

    # Check message length
    if len(message) < MIN_MESSAGE_LENGTH:
        return ValidationResult(
            status=MessageValidationStatus.TOO_SHORT,
            sanitized_message=message,
            original_message=original,
            warning=f"Mensagem muito curta: {len(message)} caracteres",
            suggested_response=f'Recebi: "{message}". Poderia elaborar um pouco mais? Por exemplo, você pode perguntar sobre contratos de um ministério específico.',
        )

    if len(message) > MAX_MESSAGE_LENGTH:
        # Truncate and warn
        message = message[:MAX_MESSAGE_LENGTH]
        logger.warning(
            f"Message truncated from {len(original)} to {MAX_MESSAGE_LENGTH}"
        )

    # Check for injection attempts BEFORE sanitization (for logging)
    injection_detected = False
    for pattern in COMPILED_INJECTION_PATTERNS:
        if pattern.search(message):
            injection_detected = True
            logger.warning(
                "Potential injection attempt detected",
                extra={
                    "pattern": pattern.pattern,
                    "message_preview": (
                        message[:50] + "..." if len(message) > 50 else message
                    ),
                },
            )
            break

    # HTML escape to prevent XSS
    message = html.escape(message)

    # Remove null bytes and control characters (except newlines/tabs)
    message = "".join(
        char
        for char in message
        if char == "\n" or char == "\t" or (ord(char) >= 32 and ord(char) != 127)
    )

    # Collapse multiple whitespaces
    message = re.sub(r"\s+", " ", message).strip()

    if injection_detected:
        return ValidationResult(
            status=MessageValidationStatus.POTENTIAL_INJECTION,
            sanitized_message=message,
            original_message=original,
            warning="Conteúdo potencialmente malicioso detectado e sanitizado",
            suggested_response="Recebi sua mensagem. Como posso ajudá-lo com informações sobre transparência governamental?",
        )

    # Check for gibberish (repeated characters)
    if REPEATED_CHAR_PATTERN.search(message):
        return ValidationResult(
            status=MessageValidationStatus.GIBBERISH,
            sanitized_message=message,
            original_message=original,
            warning="Mensagem parece conter texto repetitivo",
            suggested_response="Não consegui entender sua mensagem. Poderia reformular? Posso ajudar com investigações de contratos, análise de gastos ou informações sobre órgãos públicos.",
        )

    # Check if message is only special characters/emojis
    text_only = re.sub(r"[^\w\s]", "", message, flags=re.UNICODE)
    if len(text_only.strip()) == 0:
        return ValidationResult(
            status=MessageValidationStatus.ONLY_SPECIAL_CHARS,
            sanitized_message=message,
            original_message=original,
            warning="Mensagem contém apenas caracteres especiais",
            suggested_response="Recebi sua mensagem! 😊 Como posso ajudá-lo hoje? Experimente perguntar sobre contratos públicos ou gastos governamentais.",
        )

    # All checks passed
    return ValidationResult(
        status=MessageValidationStatus.VALID,
        sanitized_message=message,
        original_message=original,
    )


def extract_safe_log_message(message: str, max_length: int = 100) -> str:
    """
    Extract a safe version of a message for logging.

    This removes potentially sensitive content and truncates for log safety.

    Args:
        message: Original message
        max_length: Maximum length for log entry

    Returns:
        Safe string for logging
    """
    if not message:
        return "[empty]"

    # Sanitize first
    result = sanitize_message(message)
    safe_msg = result.sanitized_message

    # Truncate
    if len(safe_msg) > max_length:
        safe_msg = safe_msg[:max_length] + "..."

    # Remove any remaining newlines for log readability
    safe_msg = safe_msg.replace("\n", " ").replace("\r", "")

    return safe_msg


def is_valid_session_id(session_id: str | None) -> bool:
    """
    Validate a session ID format.

    Args:
        session_id: Session ID to validate

    Returns:
        True if valid UUID format or None
    """
    if session_id is None:
        return True

    # UUID v4 pattern
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )

    return bool(uuid_pattern.match(session_id))


# Pre-built responses for common edge cases
EDGE_CASE_RESPONSES = {
    MessageValidationStatus.EMPTY: {
        "message": "Olá! Parece que você enviou uma mensagem vazia. Como posso ajudá-lo hoje?",
        "suggested_actions": ["start_investigation", "learn_more", "view_examples"],
    },
    MessageValidationStatus.TOO_SHORT: {
        "message": "Recebi uma mensagem muito curta. Poderia elaborar um pouco mais para que eu possa ajudá-lo melhor?",
        "suggested_actions": ["view_examples", "learn_more"],
    },
    MessageValidationStatus.GIBBERISH: {
        "message": "Não consegui entender sua mensagem. Poderia reformular? Posso ajudar com investigações de contratos, análise de gastos ou informações sobre órgãos públicos.",
        "suggested_actions": ["view_examples", "learn_more"],
    },
    MessageValidationStatus.ONLY_SPECIAL_CHARS: {
        "message": "Recebi sua mensagem! Como posso ajudá-lo com a transparência governamental hoje?",
        "suggested_actions": ["start_investigation", "learn_more"],
    },
    MessageValidationStatus.POTENTIAL_INJECTION: {
        "message": "Recebi sua mensagem. Como posso ajudá-lo com informações sobre transparência governamental?",
        "suggested_actions": ["start_investigation", "learn_more"],
    },
}


def get_edge_case_response(status: MessageValidationStatus) -> dict | None:
    """
    Get a pre-built response for edge case statuses.

    Args:
        status: The validation status

    Returns:
        Response dict or None if status is VALID
    """
    return EDGE_CASE_RESPONSES.get(status)
