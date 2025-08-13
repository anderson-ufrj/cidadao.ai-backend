#!/bin/bash
#
# Vault Setup Script for Cidadão.AI
# Initializes Vault with secrets for development/production
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-}"
SECRET_PATH="${SECRET_PATH:-secret/cidadao-ai}"

echo -e "${BLUE}🔐 Cidadão.AI Vault Setup${NC}"
echo -e "${BLUE}=========================${NC}"
echo

# Check if Vault is available
echo -e "${YELLOW}🔍 Checking Vault availability...${NC}"
if ! curl -s "${VAULT_ADDR}/v1/sys/health" > /dev/null; then
    echo -e "${RED}❌ Vault is not accessible at ${VAULT_ADDR}${NC}"
    echo -e "${YELLOW}💡 Make sure Vault is running: docker-compose up vault${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Vault is accessible${NC}"

# Check authentication
if [ -z "$VAULT_TOKEN" ]; then
    echo -e "${YELLOW}🔑 Please provide Vault token:${NC}"
    read -s VAULT_TOKEN
    export VAULT_TOKEN
fi

# Verify token
if ! vault auth -address="$VAULT_ADDR" "$VAULT_TOKEN" > /dev/null 2>&1; then
    echo -e "${RED}❌ Invalid Vault token${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Authenticated with Vault${NC}"

# Enable KV v2 secrets engine if not already enabled
echo -e "${YELLOW}🔧 Enabling KV v2 secrets engine...${NC}"
vault secrets enable -address="$VAULT_ADDR" -path=secret kv-v2 2>/dev/null || true

# Function to set secret
set_secret() {
    local path="$1"
    local key="$2"
    local value="$3"
    local description="$4"
    
    echo -e "${YELLOW}📝 Setting ${description}...${NC}"
    vault kv put -address="$VAULT_ADDR" "${SECRET_PATH}/${path}" "${key}=${value}"
}

# Function to generate secure password
generate_password() {
    python3 -c "
import secrets
import string
alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
print(''.join(secrets.choice(alphabet) for _ in range(32)))
"
}

# Function to generate JWT secret
generate_jwt_secret() {
    python3 -c "
import secrets
print(secrets.token_urlsafe(64))
"
}

echo -e "${BLUE}🚀 Setting up secrets...${NC}"
echo

# Application secrets
echo -e "${YELLOW}🔐 Application Secrets${NC}"
APP_SECRET=$(generate_password)
set_secret "application" "secret_key" "$APP_SECRET" "Application secret key"

# JWT secrets
echo -e "${YELLOW}🎫 JWT Secrets${NC}"
JWT_SECRET=$(generate_jwt_secret)
set_secret "jwt" "secret_key" "$JWT_SECRET" "JWT secret key"
set_secret "jwt" "algorithm" "HS256" "JWT algorithm"
set_secret "jwt" "access_token_expire_minutes" "30" "JWT access token expiry"
set_secret "jwt" "refresh_token_expire_days" "7" "JWT refresh token expiry"

# Database secrets
echo -e "${YELLOW}🗄️ Database Secrets${NC}"
DB_PASSWORD=$(generate_password)
set_secret "database" "url" "postgresql://cidadao:${DB_PASSWORD}@postgres:5432/cidadao_ai" "Database URL"
set_secret "database" "username" "cidadao" "Database username"
set_secret "database" "password" "$DB_PASSWORD" "Database password"
set_secret "database" "host" "postgres" "Database host"
set_secret "database" "port" "5432" "Database port"
set_secret "database" "database" "cidadao_ai" "Database name"

# Redis secrets
echo -e "${YELLOW}📮 Redis Secrets${NC}"
REDIS_PASSWORD=$(generate_password)
set_secret "redis" "url" "redis://:${REDIS_PASSWORD}@redis:6379/0" "Redis URL"
set_secret "redis" "password" "$REDIS_PASSWORD" "Redis password"

# Infrastructure secrets
echo -e "${YELLOW}🏗️ Infrastructure Secrets${NC}"
MINIO_PASSWORD=$(generate_password)
CHROMA_TOKEN=$(generate_jwt_secret)
PGADMIN_PASSWORD=$(generate_password)

set_secret "infrastructure" "minio_access_key" "minioadmin" "MinIO access key"
set_secret "infrastructure" "minio_secret_key" "$MINIO_PASSWORD" "MinIO secret key"
set_secret "infrastructure" "chroma_auth_token" "$CHROMA_TOKEN" "ChromaDB auth token"
set_secret "infrastructure" "pgadmin_password" "$PGADMIN_PASSWORD" "PgAdmin password"

# User credentials (for development)
echo -e "${YELLOW}👥 User Credentials${NC}"
ADMIN_PASSWORD=$(generate_password)
ANALYST_PASSWORD=$(generate_password)

set_secret "users" "admin_email" "admin@cidadao.ai" "Admin user email"
set_secret "users" "admin_password" "$ADMIN_PASSWORD" "Admin user password"
set_secret "users" "admin_name" "Administrador" "Admin user name"
set_secret "users" "analyst_email" "analyst@cidadao.ai" "Analyst user email"
set_secret "users" "analyst_password" "$ANALYST_PASSWORD" "Analyst user password"
set_secret "users" "analyst_name" "Analista" "Analyst user name"

# API Keys (placeholders - to be updated with real keys)
echo -e "${YELLOW}🔑 API Key Placeholders${NC}"
set_secret "api_keys" "transparency_api_key" "REPLACE_WITH_REAL_KEY" "Portal da Transparência API key"
set_secret "api_keys" "groq_api_key" "REPLACE_WITH_REAL_KEY" "Groq API key"
set_secret "api_keys" "together_api_key" "REPLACE_WITH_REAL_KEY" "Together AI API key"
set_secret "api_keys" "huggingface_api_key" "REPLACE_WITH_REAL_KEY" "Hugging Face API key"
set_secret "api_keys" "openai_api_key" "REPLACE_WITH_REAL_KEY" "OpenAI API key"

echo
echo -e "${GREEN}🎉 Vault setup completed successfully!${NC}"
echo
echo -e "${BLUE}📋 Summary:${NC}"
echo -e "${GREEN}✅ Application secrets configured${NC}"
echo -e "${GREEN}✅ JWT secrets configured${NC}" 
echo -e "${GREEN}✅ Database secrets configured${NC}"
echo -e "${GREEN}✅ Redis secrets configured${NC}"
echo -e "${GREEN}✅ Infrastructure secrets configured${NC}"
echo -e "${GREEN}✅ User credentials configured${NC}"
echo -e "${YELLOW}⚠️  API key placeholders created (update with real keys)${NC}"
echo
echo -e "${BLUE}🔍 Generated credentials:${NC}"
echo -e "${YELLOW}Admin User:${NC} admin@cidadao.ai / $ADMIN_PASSWORD"
echo -e "${YELLOW}Analyst User:${NC} analyst@cidadao.ai / $ANALYST_PASSWORD"
echo -e "${YELLOW}Database Password:${NC} $DB_PASSWORD"
echo -e "${YELLOW}Redis Password:${NC} $REDIS_PASSWORD"
echo
echo -e "${BLUE}🚀 Next steps:${NC}"
echo "1. Update API keys in Vault with real values"
echo "2. Set VAULT_TOKEN in your environment"
echo "3. Start the application with Vault integration"
echo "4. Test the secret retrieval"
echo
echo -e "${BLUE}🔧 Useful commands:${NC}"
echo "# List all secrets:"
echo "vault kv list -address=$VAULT_ADDR $SECRET_PATH"
echo
echo "# Get a specific secret:"
echo "vault kv get -address=$VAULT_ADDR $SECRET_PATH/jwt"
echo
echo "# Update an API key:"
echo "vault kv patch -address=$VAULT_ADDR $SECRET_PATH/api_keys groq_api_key=your_real_key"