#!/bin/bash

# Cidadão.AI Deployment Script
# Automates the deployment process for production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="cidadao-ai"
BACKUP_DIR="/backups"
DEPLOY_ENV=${1:-production}

echo -e "${BLUE}🚀 Starting Cidadão.AI deployment...${NC}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Do not run this script as root${NC}"
    exit 1
fi

# Check dependencies
echo -e "${YELLOW}📋 Checking dependencies...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies check passed${NC}"

# Check environment file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found, copying from template...${NC}"
    if [ -f ".env.${DEPLOY_ENV}" ]; then
        cp ".env.${DEPLOY_ENV}" .env
        echo -e "${YELLOW}📝 Please edit .env file with your configuration${NC}"
        echo -e "${YELLOW}Press Enter when ready...${NC}"
        read
    else
        echo -e "${RED}❌ No .env template found for environment: ${DEPLOY_ENV}${NC}"
        exit 1
    fi
fi

# Load environment variables
source .env

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p data logs infrastructure/nginx/ssl

# Check SSL certificates
if [ ! -f "infrastructure/nginx/ssl/cert.pem" ] || [ ! -f "infrastructure/nginx/ssl/key.pem" ]; then
    echo -e "${YELLOW}🔒 SSL certificates not found, generating self-signed certificates...${NC}"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout infrastructure/nginx/ssl/key.pem \
        -out infrastructure/nginx/ssl/cert.pem \
        -subj "/C=BR/ST=Brazil/L=Brasilia/O=Cidadao.AI/OU=IT/CN=cidadao.ai"
    echo -e "${YELLOW}⚠️  Using self-signed certificates. Please replace with proper SSL certificates for production.${NC}"
fi

# Backup existing data (if any)
if [ -d "data" ] && [ "$(ls -A data)" ]; then
    echo -e "${YELLOW}💾 Creating backup...${NC}"
    BACKUP_NAME="${PROJECT_NAME}-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "${BACKUP_DIR}"
    tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" data/
    echo -e "${GREEN}✅ Backup created: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz${NC}"
fi

# Pull latest changes (if in git repository)
if [ -d ".git" ]; then
    echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
    git pull origin main
fi

# Build and start services
echo -e "${YELLOW}🏗️  Building and starting services...${NC}"

# Build Docker images
echo -e "${YELLOW}📦 Building API image...${NC}"
docker build -t cidadao-ai:latest -f deployment/Dockerfile .

echo -e "${YELLOW}👷 Building worker image...${NC}"
docker build -t cidadao-ai-worker:latest -f deployment/Dockerfile.worker .

echo -e "${YELLOW}🤖 Building ML service image...${NC}"
docker build -t cidadao-ai-ml:latest -f deployment/Dockerfile.ml .

if [ "${DEPLOY_ENV}" = "production" ]; then
    docker-compose -f deployment/docker-compose.prod.yml down
    docker-compose -f deployment/docker-compose.prod.yml up -d
else
    docker-compose down
    docker-compose up -d
fi

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Health checks
echo -e "${YELLOW}🔍 Running health checks...${NC}"

# Check API health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API is healthy${NC}"
else
    echo -e "${RED}❌ API health check failed${NC}"
    docker-compose logs api
    exit 1
fi

# Check database connection
if docker-compose exec -T postgres pg_isready -U cidadao -d cidadao_ai > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database is healthy${NC}"
else
    echo -e "${RED}❌ Database health check failed${NC}"
    docker-compose logs postgres
    exit 1
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is healthy${NC}"
else
    echo -e "${RED}❌ Redis health check failed${NC}"
    docker-compose logs redis
    exit 1
fi

# Run migrations (if available)
echo -e "${YELLOW}🔄 Running database migrations...${NC}"
# docker-compose exec api python -m alembic upgrade head

# Show deployment summary
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${BLUE}📊 Service URLs:${NC}"
echo -e "  • Frontend: https://localhost (or your domain)"
echo -e "  • API: http://localhost:8000"
echo -e "  • API Docs: http://localhost:8000/docs"
echo -e "  • Grafana: http://localhost:3000 (admin / ${GRAFANA_PASSWORD})"
echo -e "  • Prometheus: http://localhost:9090"

echo -e "${BLUE}📝 Next steps:${NC}"
echo -e "  1. Update DNS records to point to this server"
echo -e "  2. Replace self-signed SSL certificates with proper ones"
echo -e "  3. Configure firewall rules"
echo -e "  4. Set up monitoring alerts"
echo -e "  5. Schedule regular backups"

echo -e "${GREEN}✅ Cidadão.AI is now running in ${DEPLOY_ENV} mode!${NC}"
