#!/bin/bash

# =========================================
# 📊 CIDADÃO.AI - Deploy Monitoring Stack
# =========================================
# Deploy Grafana + Prometheus monitoring
# for local and production environments
# =========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_DIR="$PROJECT_ROOT/deployment"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}📊 CIDADÃO.AI - Monitoring Stack Deployment${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to check if docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running! Please start Docker first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker is running${NC}"
}

# Function to check if required files exist
check_files() {
    echo -e "\n${YELLOW}📁 Checking required files...${NC}"
    
    local required_files=(
        "docker-compose.monitoring.yml"
        "prometheus/prometheus.yml"
        "grafana/provisioning/datasources/prometheus.yml"
        "grafana/provisioning/dashboards/dashboards.yml"
        "alertmanager/alertmanager.yml"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$DEPLOYMENT_DIR/$file" ]; then
            echo -e "${GREEN}✅ Found: $file${NC}"
        else
            echo -e "${RED}❌ Missing: $file${NC}"
            exit 1
        fi
    done
}

# Function to create missing directories
create_directories() {
    echo -e "\n${YELLOW}📁 Creating required directories...${NC}"
    
    local dirs=(
        "$DEPLOYMENT_DIR/prometheus/alerts"
        "$DEPLOYMENT_DIR/grafana/plugins"
        "$DEPLOYMENT_DIR/loki"
        "$DEPLOYMENT_DIR/promtail"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            echo -e "${GREEN}✅ Created: $dir${NC}"
        fi
    done
}

# Function to set environment variables
set_environment() {
    echo -e "\n${YELLOW}🔧 Setting environment variables...${NC}"
    
    # Default values if not set
    export GRAFANA_USER=${GRAFANA_USER:-admin}
    export GRAFANA_PASSWORD=${GRAFANA_PASSWORD:-cidadao2025}
    
    echo -e "${GREEN}✅ Grafana User: $GRAFANA_USER${NC}"
    echo -e "${GREEN}✅ Grafana Password: (hidden)${NC}"
}

# Function to start monitoring stack
start_monitoring() {
    echo -e "\n${YELLOW}🚀 Starting monitoring stack...${NC}"
    
    cd "$DEPLOYMENT_DIR"
    
    # Pull latest images
    echo -e "${BLUE}📥 Pulling latest images...${NC}"
    docker-compose -f docker-compose.monitoring.yml pull
    
    # Start services
    echo -e "${BLUE}🎯 Starting services...${NC}"
    docker-compose -f docker-compose.monitoring.yml up -d
    
    # Wait for services to be ready
    echo -e "\n${YELLOW}⏳ Waiting for services to start...${NC}"
    sleep 10
}

# Function to check service health
check_health() {
    echo -e "\n${YELLOW}🏥 Checking service health...${NC}"
    
    local services=(
        "prometheus:9090/-/healthy"
        "grafana:3000/api/health"
        "alertmanager:9093/-/healthy"
        "loki:3100/ready"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r name endpoint <<< "$service"
        
        if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$endpoint" | grep -q "200"; then
            echo -e "${GREEN}✅ $name is healthy${NC}"
        else
            echo -e "${YELLOW}⚠️  $name is starting up...${NC}"
        fi
    done
}

# Function to display access information
show_access_info() {
    echo -e "\n${GREEN}================================================${NC}"
    echo -e "${GREEN}🎉 Monitoring Stack Deployed Successfully!${NC}"
    echo -e "${GREEN}================================================${NC}"
    
    echo -e "\n${BLUE}📊 Access URLs:${NC}"
    echo -e "  • Grafana:       ${GREEN}http://localhost:3000${NC}"
    echo -e "  • Prometheus:    ${GREEN}http://localhost:9090${NC}"
    echo -e "  • AlertManager:  ${GREEN}http://localhost:9093${NC}"
    echo -e "  • Node Exporter: ${GREEN}http://localhost:9100${NC}"
    echo -e "  • cAdvisor:      ${GREEN}http://localhost:8080${NC}"
    
    echo -e "\n${BLUE}🔐 Grafana Login:${NC}"
    echo -e "  • Username: ${GREEN}$GRAFANA_USER${NC}"
    echo -e "  • Password: ${GREEN}$GRAFANA_PASSWORD${NC}"
    
    echo -e "\n${BLUE}📈 Default Dashboards:${NC}"
    echo -e "  • Cidadão.AI Overview"
    echo -e "  • Agent Performance"
    echo -e "  • Zumbi Agent Metrics"
    
    echo -e "\n${YELLOW}💡 Tips:${NC}"
    echo -e "  • Check logs: ${GREEN}docker-compose -f deployment/docker-compose.monitoring.yml logs -f${NC}"
    echo -e "  • Stop stack: ${GREEN}docker-compose -f deployment/docker-compose.monitoring.yml down${NC}"
    echo -e "  • Update stack: ${GREEN}docker-compose -f deployment/docker-compose.monitoring.yml pull && docker-compose -f deployment/docker-compose.monitoring.yml up -d${NC}"
}

# Function to configure production deployment
configure_production() {
    echo -e "\n${YELLOW}🌐 Configuring for production deployment...${NC}"
    
    # Create production config overlay
    cat > "$DEPLOYMENT_DIR/docker-compose.monitoring.prod.yml" << 'EOF'
version: '3.9'

# Production overlay for monitoring stack
services:
  prometheus:
    restart: always
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
    
  grafana:
    restart: always
    environment:
      - GF_SERVER_ROOT_URL=https://monitoring.cidadao.ai
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_AUTH_ANONYMOUS_ENABLED=false
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
    
  alertmanager:
    restart: always
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
        reservations:
          memory: 256M
          cpus: '0.1'
    
  loki:
    restart: always
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
EOF
    
    echo -e "${GREEN}✅ Production configuration created${NC}"
}

# Main execution
main() {
    check_docker
    check_files
    create_directories
    set_environment
    
    # Ask for deployment type
    echo -e "\n${YELLOW}🎯 Select deployment type:${NC}"
    echo -e "  1) Local Development"
    echo -e "  2) Production (with resource limits)"
    read -p "Choice (1-2): " choice
    
    case $choice in
        2)
            configure_production
            echo -e "${YELLOW}📝 Using production configuration...${NC}"
            ;;
        *)
            echo -e "${YELLOW}📝 Using local development configuration...${NC}"
            ;;
    esac
    
    start_monitoring
    check_health
    show_access_info
}

# Run main function
main "$@"