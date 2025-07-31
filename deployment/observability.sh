#!/bin/bash

# Cidadão.AI Observability Stack Management Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.observability.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if docker-compose is installed
check_requirements() {
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose is not installed. Please install it first."
        exit 1
    fi
}

# Start observability stack
start_stack() {
    log_info "Starting Cidadão.AI Observability Stack..."
    
    # Ensure the main network exists
    docker network create cidadao-network 2>/dev/null || true
    
    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    log_info "Waiting for services to be ready..."
    sleep 10
    
    log_info "Observability stack started successfully!"
    log_info ""
    log_info "Access the following services:"
    log_info "  - Prometheus: http://localhost:9090"
    log_info "  - Grafana: http://localhost:3001 (admin/admin123)"
    log_info "  - Jaeger: http://localhost:16686"
    log_info "  - Alertmanager: http://localhost:9093"
    log_info ""
}

# Stop observability stack
stop_stack() {
    log_info "Stopping Cidadão.AI Observability Stack..."
    docker-compose -f "$COMPOSE_FILE" down
    log_info "Observability stack stopped."
}

# View logs
view_logs() {
    docker-compose -f "$COMPOSE_FILE" logs -f "$1"
}

# Check status
check_status() {
    log_info "Checking Observability Stack Status..."
    docker-compose -f "$COMPOSE_FILE" ps
}

# Setup dashboards
setup_dashboards() {
    log_info "Setting up Grafana dashboards..."
    
    # Wait for Grafana to be ready
    until curl -s http://localhost:3001/api/health > /dev/null 2>&1; do
        log_info "Waiting for Grafana to be ready..."
        sleep 5
    done
    
    log_info "Grafana is ready. Dashboards will be automatically provisioned."
}

# Main menu
show_menu() {
    echo ""
    echo "Cidadão.AI Observability Stack Manager"
    echo "======================================"
    echo "1. Start observability stack"
    echo "2. Stop observability stack"
    echo "3. View logs (all services)"
    echo "4. View logs (specific service)"
    echo "5. Check status"
    echo "6. Setup dashboards"
    echo "7. Exit"
    echo ""
}

# Main script
main() {
    check_requirements
    
    if [ $# -eq 0 ]; then
        # Interactive mode
        while true; do
            show_menu
            read -p "Select an option: " choice
            
            case $choice in
                1) start_stack ;;
                2) stop_stack ;;
                3) view_logs ;;
                4)
                    read -p "Enter service name (prometheus/grafana/jaeger/etc): " service
                    view_logs "$service"
                    ;;
                5) check_status ;;
                6) setup_dashboards ;;
                7) exit 0 ;;
                *) log_error "Invalid option" ;;
            esac
        done
    else
        # Command mode
        case $1 in
            start) start_stack ;;
            stop) stop_stack ;;
            logs) view_logs "${2:-}" ;;
            status) check_status ;;
            setup) setup_dashboards ;;
            *)
                log_error "Unknown command: $1"
                echo "Usage: $0 {start|stop|logs|status|setup}"
                exit 1
                ;;
        esac
    fi
}

main "$@"