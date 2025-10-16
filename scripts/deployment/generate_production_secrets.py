#!/usr/bin/env python3
"""
Script to generate secure production secrets.

Usage:
    python scripts/deployment/generate_production_secrets.py
    python scripts/deployment/generate_production_secrets.py --output .env.production
"""

import argparse
import secrets
import sys
from pathlib import Path


def generate_secret(length: int = 64) -> str:
    """Generate a cryptographically secure random string."""
    return secrets.token_urlsafe(length)


def generate_jwt_secret() -> str:
    """Generate JWT secret key."""
    return generate_secret(64)


def generate_app_secret() -> str:
    """Generate application secret key."""
    return generate_secret(64)


def main():
    parser = argparse.ArgumentParser(description="Generate secure production secrets")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: print to stdout)",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["env", "railway", "json"],
        default="env",
        help="Output format",
    )

    args = parser.parse_args()

    jwt_secret = generate_jwt_secret()
    app_secret = generate_app_secret()

    if args.format == "env":
        output = f"""# Production Secrets - Generated at {Path(__file__).name}
# KEEP THESE SECRET! Do not commit to version control.

JWT_SECRET_KEY={jwt_secret}
SECRET_KEY={app_secret}

# To use with Railway:
# railway variables set JWT_SECRET_KEY="{jwt_secret}"
# railway variables set SECRET_KEY="{app_secret}"
"""
    elif args.format == "railway":
        output = f"""# Railway Variables Commands
# Copy and paste these commands:

railway variables set JWT_SECRET_KEY="{jwt_secret}"
railway variables set SECRET_KEY="{app_secret}"
"""
    elif args.format == "json":
        import json

        output = json.dumps(
            {
                "JWT_SECRET_KEY": jwt_secret,
                "SECRET_KEY": app_secret,
            },
            indent=2,
        )

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output)
        print(f"✅ Secrets written to: {output_path}")
        print(f"⚠️  Remember to add {output_path} to .gitignore!")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
