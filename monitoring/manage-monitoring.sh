#!/bin/bash

# Cidadão.AI Monitoring Stack Management Script
# This script helps manage the Prometheus + Grafana monitoring stack

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to start the monitoring stack
start_monitoring() {
    print_status "Starting Cidadão.AI monitoring stack..."
    
    cd "$PROJECT_DIR"
    
    # Create necessary directories
    mkdir -p monitoring/prometheus/data
    mkdir -p monitoring/grafana/data
    
    # Set proper permissions
    chmod 777 monitoring/prometheus/data
    chmod 777 monitoring/grafana/data
    
    # Start services
    docker-compose -f config/docker/docker-compose.monitoring.yml up -d
    
    print_success "Monitoring stack started successfully!"
    print_status "Services available at:"
    echo "  🏛️  Cidadão.AI Backend: http://localhost:7860"
    echo "  📊 Grafana Dashboard:   http://localhost:3000 (admin/cidadao123)"
    echo "  📈 Prometheus:          http://localhost:9090"
    echo "  🖥️  Node Exporter:      http://localhost:9100"
    echo "  📦 cAdvisor:            http://localhost:8080"
}

# Function to stop the monitoring stack
stop_monitoring() {
    print_status "Stopping Cidadão.AI monitoring stack..."
    
    cd "$PROJECT_DIR"
    docker-compose -f config/docker/docker-compose.monitoring.yml down
    
    print_success "Monitoring stack stopped successfully!"
}

# Function to restart the monitoring stack
restart_monitoring() {
    print_status "Restarting Cidadão.AI monitoring stack..."
    stop_monitoring
    sleep 2
    start_monitoring
}

# Function to show status of monitoring services
status_monitoring() {
    print_status "Checking monitoring stack status..."
    
    cd "$PROJECT_DIR"
    docker-compose -f config/docker/docker-compose.monitoring.yml ps
}

# Function to view logs
logs_monitoring() {
    local service=${1:-}
    
    cd "$PROJECT_DIR"
    
    if [[ -n "$service" ]]; then
        print_status "Showing logs for service: $service"
        docker-compose -f config/docker/docker-compose.monitoring.yml logs -f "$service"
    else
        print_status "Showing logs for all monitoring services (use Ctrl+C to exit)"
        docker-compose -f config/docker/docker-compose.monitoring.yml logs -f
    fi
}

# Function to clean up monitoring data
cleanup_monitoring() {
    print_warning "This will remove all monitoring data including Prometheus metrics and Grafana dashboards."
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping services and cleaning up data..."
        
        cd "$PROJECT_DIR"
        docker-compose -f config/docker/docker-compose.monitoring.yml down -v
        
        # Remove data directories
        sudo rm -rf monitoring/prometheus/data/*
        sudo rm -rf monitoring/grafana/data/*
        
        print_success "Monitoring data cleaned up successfully!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to run health checks
health_check() {
    print_status "Running health checks on monitoring services..."
    
    # Check Cidadão.AI Backend
    if curl -s -f http://localhost:7860/health > /dev/null; then
        print_success "✅ Cidadão.AI Backend: Healthy"
    else
        print_error "❌ Cidadão.AI Backend: Not responding"
    fi
    
    # Check Grafana
    if curl -s -f http://localhost:3000/api/health > /dev/null; then
        print_success "✅ Grafana: Healthy"
    else
        print_error "❌ Grafana: Not responding"
    fi
    
    # Check Prometheus
    if curl -s -f http://localhost:9090/-/healthy > /dev/null; then
        print_success "✅ Prometheus: Healthy"
    else
        print_error "❌ Prometheus: Not responding"
    fi
    
    # Check Node Exporter
    if curl -s -f http://localhost:9100/metrics > /dev/null; then
        print_success "✅ Node Exporter: Healthy"
    else
        print_error "❌ Node Exporter: Not responding"
    fi
    
    # Check cAdvisor
    if curl -s -f http://localhost:8080/healthz > /dev/null; then
        print_success "✅ cAdvisor: Healthy"
    else
        print_error "❌ cAdvisor: Not responding"
    fi
}

# Function to show help
show_help() {
    echo "Cidadão.AI Monitoring Stack Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start the monitoring stack"
    echo "  stop        Stop the monitoring stack"
    echo "  restart     Restart the monitoring stack"
    echo "  status      Show status of monitoring services"
    echo "  logs [SVC]  Show logs (optionally for specific service)"
    echo "  health      Run health checks on all services"
    echo "  cleanup     Stop services and remove all data"
    echo "  help        Show this help message"
    echo ""
    echo "Available services for logs:"
    echo "  cidadao-ai, prometheus, grafana, node_exporter, cadvisor"
}

# Main script logic
main() {
    check_docker
    
    case "${1:-}" in
        start)
            start_monitoring
            ;;
        stop)
            stop_monitoring
            ;;
        restart)
            restart_monitoring
            ;;
        status)
            status_monitoring
            ;;
        logs)
            logs_monitoring "${2:-}"
            ;;
        health)
            health_check
            ;;
        cleanup)
            cleanup_monitoring
            ;;
        help|--help|-h)
            show_help
            ;;
        "")
            print_error "No command specified. Use 'help' to see available commands."
            exit 1
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"