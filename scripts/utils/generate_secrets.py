#!/usr/bin/env python3
"""
Script to generate secure secrets for Cidadão.AI
Generates cryptographically secure random secrets for production use
"""

import os
import secrets
import string
from pathlib import Path


def generate_secret_key(length=64):
    """Generate a secure random secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_jwt_secret(length=64):
    """Generate a secure JWT secret"""
    return secrets.token_urlsafe(length)


def generate_password(length=24):
    """Generate a secure password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_token(length=32):
    """Generate a secure token"""
    return secrets.token_urlsafe(length)


def create_env_file(output_path: str, deployment: bool = False):
    """Create .env file with secure secrets"""

    secrets_data = {
        "SECRET_KEY": generate_secret_key(),
        "JWT_SECRET_KEY": generate_jwt_secret(),
        "POSTGRES_PASSWORD": generate_password(),
        "MINIO_ROOT_PASSWORD": generate_password(),
        "CHROMA_AUTH_TOKEN": generate_token(),
        "PGADMIN_PASSWORD": generate_password(),
        "REDIS_PASSWORD": generate_password(),
    }

    if deployment:
        # Deployment-specific .env
        content = f"""# Generated secrets for Docker Compose - {pd.datetime.now().isoformat()}
# KEEP THIS FILE SECURE - DO NOT COMMIT TO VERSION CONTROL

# PostgreSQL Configuration
POSTGRES_USER=cidadao
POSTGRES_PASSWORD={secrets_data['POSTGRES_PASSWORD']}
POSTGRES_DB=cidadao_ai

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD={secrets_data['MINIO_ROOT_PASSWORD']}

# ChromaDB Configuration
CHROMA_AUTH_TOKEN={secrets_data['CHROMA_AUTH_TOKEN']}

# PgAdmin Configuration
PGADMIN_PASSWORD={secrets_data['PGADMIN_PASSWORD']}

# Redis Configuration
REDIS_PASSWORD={secrets_data['REDIS_PASSWORD']}
"""
    else:
        # Application .env
        content = f"""# Generated secrets for Cidadao.AI - {pd.datetime.now().isoformat()}
# KEEP THIS FILE SECURE - DO NOT COMMIT TO VERSION CONTROL

# Application Configuration
APP_NAME=cidadao-ai
APP_ENV=development
APP_VERSION=1.0.0
LOG_LEVEL=INFO
DEBUG=false

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Database Configuration
DATABASE_URL=postgresql://cidadao:{secrets_data['POSTGRES_PASSWORD']}@localhost:5432/cidadao_ai
DATABASE_POOL_SIZE=10
DATABASE_POOL_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD={secrets_data['REDIS_PASSWORD']}
REDIS_POOL_SIZE=10

# Security Configuration (REQUIRED)
SECRET_KEY={secrets_data['SECRET_KEY']}
JWT_SECRET_KEY={secrets_data['JWT_SECRET_KEY']}

# User Management (Configure for your needs)
ADMIN_USER_EMAIL=admin@your-domain.com
ADMIN_USER_PASSWORD={generate_password()}
ADMIN_USER_NAME=Administrator

ANALYST_USER_EMAIL=analyst@your-domain.com
ANALYST_USER_PASSWORD={generate_password()}
ANALYST_USER_NAME=Analyst

# API Keys - Configure these
TRANSPARENCY_API_KEY=your_portal_transparencia_api_key_here
GROQ_API_KEY=your_groq_api_key_here
TOGETHER_API_KEY=your_together_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(content)

    # Set restrictive permissions (owner read/write only)
    os.chmod(output_path, 0o600)

    print(f"✅ Secure .env file created at: {output_path}")
    print("⚠️  IMPORTANT: This file contains secrets. Keep it secure!")

    return secrets_data


def main():
    """Generate secrets for development and deployment"""

    print("🔐 Generating secure secrets for Cidadão.AI...")
    print()

    # Generate main application .env
    app_secrets = create_env_file(".env.secure")

    # Generate deployment .env
    deploy_secrets = create_env_file("deployment/.env.secure", deployment=True)

    print()
    print("📋 Summary of generated secrets:")
    print("-" * 50)
    for key, value in app_secrets.items():
        masked_value = value[:8] + "..." + value[-8:] if len(value) > 16 else "***"
        print(f"{key}: {masked_value}")

    print()
    print("📚 Next steps:")
    print("1. Review the generated .env files")
    print("2. Customize user emails and API keys")
    print("3. Copy .env.secure to .env for development")
    print("4. Copy deployment/.env.secure to deployment/.env for Docker")
    print("5. Add .env to .gitignore (if not already)")
    print("6. Test the application startup")


if __name__ == "__main__":
    main()
