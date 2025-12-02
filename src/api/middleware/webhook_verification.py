"""
Module: api.middleware.webhook_verification
Description: Webhook signature verification middleware
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import hashlib
import hmac
import time

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.core import get_logger

logger = get_logger(__name__)


class WebhookVerificationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for verifying incoming webhook signatures.

    Protects endpoints that receive webhooks from external services.
    """

    def __init__(
        self,
        app,
        webhook_paths: dict[str, str] | None = None,
        max_timestamp_age: int = 300,  # 5 minutes
    ):
        """
        Initialize webhook verification middleware.

        Args:
            app: FastAPI application
            webhook_paths: Dict of path -> secret mapping
            max_timestamp_age: Maximum age of timestamp in seconds
        """
        super().__init__(app)
        self.webhook_paths = webhook_paths or {}
        self.max_timestamp_age = max_timestamp_age

    async def dispatch(self, request: Request, call_next):
        """Process request with webhook verification."""
        # Check if this is a webhook path
        if request.url.path not in self.webhook_paths:
            return await call_next(request)

        # Get the secret for this path
        secret = self.webhook_paths[request.url.path]

        try:
            # Read body
            body = await request.body()

            # Verify signature
            if not self._verify_signature(request, body, secret):
                logger.warning(
                    "webhook_signature_verification_failed",
                    path=request.url.path,
                    headers=dict(request.headers),
                )

                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Invalid webhook signature",
                        "error": "INVALID_SIGNATURE",
                    },
                )

            # Verify timestamp if present
            if not self._verify_timestamp(request):
                logger.warning(
                    "webhook_timestamp_verification_failed", path=request.url.path
                )

                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Webhook timestamp too old",
                        "error": "TIMESTAMP_TOO_OLD",
                    },
                )

            # Store raw body for handler
            request.state.webhook_body = body

            # Process request
            return await call_next(request)

        except Exception as e:
            logger.error("webhook_verification_error", error=str(e), exc_info=True)

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Webhook verification error",
                    "error": "VERIFICATION_ERROR",
                },
            )

    def _verify_signature(self, request: Request, body: bytes, secret: str) -> bool:
        """Verify webhook signature."""
        # Get signature header - support multiple formats
        signature_header = (
            request.headers.get("X-Cidadao-Signature")
            or request.headers.get("X-Webhook-Signature")
            or request.headers.get("X-Hub-Signature-256")  # GitHub format
        )

        if not signature_header:
            logger.debug("No signature header found")
            return False

        # Parse signature
        if "=" in signature_header:
            algorithm, signature = signature_header.split("=", 1)
        else:
            algorithm = "sha256"
            signature = signature_header

        # Calculate expected signature
        if algorithm == "sha256":
            expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        elif algorithm == "sha1":
            expected = hmac.new(secret.encode(), body, hashlib.sha1).hexdigest()
        else:
            logger.warning(f"Unsupported signature algorithm: {algorithm}")
            return False

        # Compare signatures
        return hmac.compare_digest(signature, expected)

    def _verify_timestamp(self, request: Request) -> bool:
        """Verify webhook timestamp is recent."""
        timestamp_header = request.headers.get(
            "X-Cidadao-Timestamp"
        ) or request.headers.get("X-Webhook-Timestamp")

        if not timestamp_header:
            # No timestamp to verify
            return True

        try:
            # Parse timestamp
            if timestamp_header.isdigit():
                # Unix timestamp
                webhook_time = float(timestamp_header)
            else:
                # ISO format
                from dateutil.parser import parse

                webhook_time = parse(timestamp_header).timestamp()

            # Check age
            current_time = time.time()
            age = abs(current_time - webhook_time)

            return age <= self.max_timestamp_age

        except Exception as e:
            logger.error(f"Failed to parse timestamp: {e}")
            return False


def create_webhook_signature(
    payload: bytes, secret: str, algorithm: str = "sha256"
) -> str:
    """
    Create webhook signature for outgoing webhooks.

    Args:
        payload: Request body
        secret: Webhook secret
        algorithm: Hash algorithm (sha256, sha1)

    Returns:
        Signature string with format "algorithm=signature"
    """
    if algorithm == "sha256":
        signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    elif algorithm == "sha1":
        signature = hmac.new(secret.encode(), payload, hashlib.sha1).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    return f"{algorithm}={signature}"


def verify_webhook_signature(signature: str, payload: bytes, secret: str) -> bool:
    """
    Verify webhook signature.

    Args:
        signature: Signature header value
        payload: Request body
        secret: Webhook secret

    Returns:
        True if signature is valid
    """
    try:
        # Parse signature
        if "=" in signature:
            algorithm, sig = signature.split("=", 1)
        else:
            algorithm = "sha256"
            sig = signature

        # Generate expected signature
        expected = create_webhook_signature(payload, secret, algorithm)

        # Extract just the signature part
        if "=" in expected:
            _, expected_sig = expected.split("=", 1)
        else:
            expected_sig = expected

        # Compare
        return hmac.compare_digest(sig, expected_sig)

    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False


class WebhookSigner:
    """Helper class for signing webhook requests."""

    def __init__(self, secret: str, algorithm: str = "sha256"):
        """Initialize webhook signer."""
        self.secret = secret
        self.algorithm = algorithm

    def sign(self, payload: bytes) -> dict[str, str]:
        """
        Generate webhook headers with signature.

        Args:
            payload: Request body

        Returns:
            Dict of headers to include in request
        """
        signature = create_webhook_signature(payload, self.secret, self.algorithm)

        timestamp = str(int(time.time()))

        return {
            "X-Cidadao-Signature": signature,
            "X-Cidadao-Timestamp": timestamp,
            "X-Cidadao-Algorithm": self.algorithm,
        }
