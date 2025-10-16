#!/usr/bin/env python3
"""
Validate environment configuration before deployment.

Usage:
    python scripts/deployment/validate_config.py
    python scripts/deployment/validate_config.py --env production
"""

import argparse
import os
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Security constants
MIN_KEY_LENGTH = 32


def check_required_vars() -> tuple[list[str], list[str]]:
    """Check required environment variables."""
    required = {
        "JWT_SECRET_KEY": "JWT authentication secret",
        "SECRET_KEY": "Application secret key",
    }

    # At least one LLM provider
    llm_providers = {
        "MARITACA_API_KEY": "Maritaca AI (Primary - Brazilian Portuguese)",
        "ANTHROPIC_API_KEY": "Anthropic Claude (Secondary - Fallback)",
        "TOGETHER_API_KEY": "Together AI (Alternative)",
        "HUGGINGFACE_API_KEY": "HuggingFace (Alternative)",
    }

    missing = []
    found = []

    # Check required vars
    for var, desc in required.items():
        value = os.getenv(var, "")
        if not value or value.startswith("your-") or value.startswith("dev-"):
            missing.append(f"{var} ({desc})")
        else:
            found.append(f"{var} ✓")

    # Check LLM providers (at least one)
    llm_found = False
    for var, desc in llm_providers.items():
        value = os.getenv(var, "")
        if value and not value.startswith("your-"):
            llm_found = True
            found.append(f"{var} ({desc}) ✓")

    if not llm_found:
        missing.append("At least one LLM provider (MARITACA_API_KEY recommended)")

    return found, missing


def check_optional_vars() -> list[str]:
    """Check optional but recommended environment variables."""
    optional = {
        "DATABASE_URL": "PostgreSQL connection",
        "SUPABASE_URL": "Supabase project URL",
        "SUPABASE_SERVICE_ROLE_KEY": "Supabase service role key",
        "REDIS_URL": "Redis cache",
        "TRANSPARENCY_API_KEY": "Portal da Transparência",
        "DADOS_GOV_API_KEY": "Dados.gov.br",
    }

    configured = []
    for var, desc in optional.items():
        value = os.getenv(var, "")
        if value and not value.startswith("your-"):
            configured.append(f"{var} ({desc}) ✓")

    return configured


def check_security() -> list[str]:
    """Check security-related configurations."""
    warnings = []

    # Check if using development keys
    jwt_key = os.getenv("JWT_SECRET_KEY", "")
    if "dev-" in jwt_key.lower() or "test" in jwt_key.lower():
        warnings.append("JWT_SECRET_KEY appears to be a development key")

    secret_key = os.getenv("SECRET_KEY", "")
    if "dev-" in secret_key.lower() or "test" in secret_key.lower():
        warnings.append("SECRET_KEY appears to be a development key")

    # Check key length
    if jwt_key and len(jwt_key) < MIN_KEY_LENGTH:
        warnings.append(
            f"JWT_SECRET_KEY is too short (minimum {MIN_KEY_LENGTH} characters)"
        )

    if secret_key and len(secret_key) < MIN_KEY_LENGTH:
        warnings.append(
            f"SECRET_KEY is too short (minimum {MIN_KEY_LENGTH} characters)"
        )

    # Check if DEBUG is disabled in production
    debug = os.getenv("DEBUG", "false").lower()
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment == "production" and debug in ["true", "1", "yes"]:
        warnings.append("DEBUG is enabled in production environment")

    return warnings


def print_section(title: str, items: list[str], color: str = BLUE):
    """Print a section with items."""
    if not items:
        return

    print(f"\n{color}{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}{RESET}")
    for item in items:
        print(f"  {item}")


def main():  # noqa: C901, PLR0915
    parser = argparse.ArgumentParser(description="Validate environment configuration")
    parser.add_argument(
        "--env",
        type=str,
        choices=["development", "production"],
        default="development",
        help="Environment to validate",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if any issues found",
    )

    args = parser.parse_args()

    print(f"\n{BLUE}{'=' * 60}")
    print(f"🔍 Validating {args.env.upper()} configuration")
    print(f"{'=' * 60}{RESET}")

    # Load .env file if exists
    env_file = Path(".env")
    if env_file.exists():
        print(f"\n📄 Loading environment from: {env_file}")
        # Simple .env parser
        for env_line in env_file.read_text().splitlines():
            env_line = env_line.strip()  # noqa: PLW2901
            if env_line and not env_line.startswith("#") and "=" in env_line:
                key, value = env_line.split("=", 1)
                if key not in os.environ:  # Don't override existing env vars
                    os.environ[key] = value

    # Run checks
    found, missing = check_required_vars()
    optional = check_optional_vars()
    warnings = check_security()

    # Print results
    print_section("✅ CONFIGURED REQUIRED", found, GREEN)
    print_section("⚠️  OPTIONAL CONFIGURED", optional, BLUE)

    if missing:
        print_section("❌ MISSING REQUIRED", missing, RED)

    if warnings:
        print_section("⚠️  SECURITY WARNINGS", warnings, YELLOW)

    # Summary
    print(f"\n{BLUE}{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}{RESET}")
    print(f"  Required configured: {GREEN}{len(found)}{RESET}")
    print(f"  Required missing: {RED}{len(missing)}{RESET}")
    print(f"  Optional configured: {BLUE}{len(optional)}{RESET}")
    print(f"  Security warnings: {YELLOW}{len(warnings)}{RESET}")

    # Exit status
    has_errors = len(missing) > 0
    has_warnings = len(warnings) > 0

    if has_errors:
        print(f"\n{RED}❌ Configuration validation FAILED{RESET}")
        print(f"\nFix missing required variables before deploying to {args.env}")
        if args.strict:
            return 1
    elif has_warnings and args.env == "production":
        print(f"\n{YELLOW}⚠️  Configuration has warnings{RESET}")
        print("\nReview security warnings before deploying to production")
        if args.strict:
            return 1
    else:
        print(f"\n{GREEN}✅ Configuration validation PASSED{RESET}")

    # Additional tips
    if missing:
        print(f"\n{BLUE}💡 Quick fixes:{RESET}")
        print("\n  1. Generate secrets:")
        print("     python scripts/deployment/generate_production_secrets.py")
        print("\n  2. Get Maritaca AI API key:")
        print("     https://plataforma.maritaca.ai/")
        print("\n  3. Get Anthropic Claude API key (optional):")
        print("     https://console.anthropic.com/")
        print("\n  4. Update .env file with the generated values")
        print("\n  5. Test LLM providers:")
        print("     python scripts/deployment/test_llm_providers.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
