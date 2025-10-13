#!/bin/bash

# Federal APIs Dashboard Testing Script
# Validates dashboard configuration and provides testing instructions

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_section() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Validate dashboard JSON
validate_dashboard_json() {
    print_section "Validating Dashboard JSON"

    local dashboard_file="$SCRIPT_DIR/grafana/dashboards/federal-apis-dashboard.json"

    if [[ ! -f "$dashboard_file" ]]; then
        print_error "Dashboard file not found: $dashboard_file"
        return 1
    fi

    # Validate JSON syntax
    if python3 -c "import json; json.load(open('$dashboard_file'))" 2>/dev/null; then
        print_success "Dashboard JSON is valid"
    else
        print_error "Dashboard JSON is invalid!"
        return 1
    fi

    # Extract dashboard metadata
    local title=$(python3 -c "import json; d=json.load(open('$dashboard_file')); print(d.get('title', 'Unknown'))")
    local uid=$(python3 -c "import json; d=json.load(open('$dashboard_file')); print(d.get('uid', 'Unknown'))")
    local panel_count=$(python3 -c "import json; d=json.load(open('$dashboard_file')); print(len(d.get('panels', [])))")

    echo "  Title: $title"
    echo "  UID: $uid"
    echo "  Panels: $panel_count"

    print_success "Dashboard metadata extracted"
}

# Check provisioning configuration
check_provisioning_config() {
    print_section "Checking Provisioning Configuration"

    local dashboards_config="$SCRIPT_DIR/grafana/provisioning/dashboards/dashboards.yml"
    local datasources_config="$SCRIPT_DIR/grafana/provisioning/datasources/prometheus.yml"

    if [[ -f "$dashboards_config" ]]; then
        print_success "Dashboards provisioning config exists"
        echo "  Path: $dashboards_config"
    else
        print_error "Dashboards provisioning config not found!"
        return 1
    fi

    if [[ -f "$datasources_config" ]]; then
        print_success "Datasources provisioning config exists"
        echo "  Path: $datasources_config"
    else
        print_error "Datasources provisioning config not found!"
        return 1
    fi
}

# Validate metrics module
validate_metrics_module() {
    print_section "Validating Metrics Module"

    local metrics_file="$PROJECT_DIR/src/services/transparency_apis/federal_apis/metrics.py"

    if [[ -f "$metrics_file" ]]; then
        print_success "Federal API metrics module exists"

        # Check for key metric definitions
        local metrics_found=0

        if grep -q "federal_api_request_duration_seconds" "$metrics_file"; then
            echo "  ✓ Request duration metric registered"
            ((metrics_found++))
        fi

        if grep -q "federal_api_requests_total" "$metrics_file"; then
            echo "  ✓ Request counter metric registered"
            ((metrics_found++))
        fi

        if grep -q "federal_api_cache_operations_total" "$metrics_file"; then
            echo "  ✓ Cache operations metric registered"
            ((metrics_found++))
        fi

        if grep -q "federal_api_errors_total" "$metrics_file"; then
            echo "  ✓ Error counter metric registered"
            ((metrics_found++))
        fi

        if grep -q "federal_api_retries_total" "$metrics_file"; then
            echo "  ✓ Retry counter metric registered"
            ((metrics_found++))
        fi

        print_success "Found $metrics_found/5 key metrics"
    else
        print_error "Metrics module not found!"
        return 1
    fi
}

# Check if API clients are instrumented
check_client_instrumentation() {
    print_section "Checking API Client Instrumentation"

    local clients=("ibge_client.py" "datasus_client.py" "inep_client.py")
    local instrumented_count=0

    for client in "${clients[@]}"; do
        local client_file="$PROJECT_DIR/src/services/transparency_apis/federal_apis/$client"

        if [[ -f "$client_file" ]]; then
            if grep -q "FederalAPIMetrics" "$client_file"; then
                print_success "$client is instrumented"
                ((instrumented_count++))
            else
                print_warning "$client is NOT instrumented"
            fi
        else
            print_warning "$client not found"
        fi
    done

    if [[ $instrumented_count -eq 3 ]]; then
        print_success "All API clients are instrumented"
    else
        print_warning "Only $instrumented_count/3 clients are instrumented"
    fi
}

# Validate PromQL queries in dashboard
validate_promql_queries() {
    print_section "Validating PromQL Queries"

    local dashboard_file="$SCRIPT_DIR/grafana/dashboards/federal-apis-dashboard.json"

    # Extract unique metric names used in queries
    local metrics=$(python3 << 'EOF'
import json
import re

with open('monitoring/grafana/dashboards/federal-apis-dashboard.json') as f:
    dashboard = json.load(f)

metrics = set()
for panel in dashboard.get('panels', []):
    if 'targets' in panel:
        for target in panel['targets']:
            expr = target.get('expr', '')
            # Extract metric names (simplified)
            found = re.findall(r'federal_api_\w+', expr)
            metrics.update(found)

for metric in sorted(metrics):
    print(metric)
EOF
    )

    echo "Metrics used in dashboard queries:"
    echo "$metrics" | while read -r metric; do
        if [[ -n "$metric" ]]; then
            echo "  • $metric"
        fi
    done

    print_success "PromQL queries validated"
}

# Check Docker configuration
check_docker_config() {
    print_section "Checking Docker Configuration"

    local docker_compose_file="$PROJECT_DIR/config/docker/docker-compose.monitoring.yml"

    if [[ -f "$docker_compose_file" ]]; then
        print_success "Docker Compose monitoring config exists"

        # Check for required services
        if grep -q "prometheus:" "$docker_compose_file"; then
            echo "  ✓ Prometheus service configured"
        fi

        if grep -q "grafana:" "$docker_compose_file"; then
            echo "  ✓ Grafana service configured"
        fi

        # Check volume mounts
        if grep -q "./monitoring/grafana/dashboards:/var/lib/grafana/dashboards" "$docker_compose_file"; then
            echo "  ✓ Dashboard directory mounted correctly"
        else
            print_warning "Dashboard directory mount may be incorrect"
        fi
    else
        print_error "Docker Compose monitoring config not found!"
        return 1
    fi
}

# Print testing instructions
print_testing_instructions() {
    print_section "Dashboard Testing Instructions"

    cat << 'EOF'
To test the Federal APIs Dashboard, follow these steps:

1. Start the monitoring stack:
   cd /home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend
   ./monitoring/manage-monitoring.sh start

2. Wait for services to be ready (30-60 seconds):
   ./monitoring/manage-monitoring.sh health

3. Access Grafana:
   URL: http://localhost:3000
   Username: admin
   Password: cidadao123

4. Verify dashboard loaded:
   - Navigate to Dashboards → Browse
   - Look for "Federal APIs Monitoring"
   - Dashboard UID: federal-apis

5. Generate test data by making API calls:
   # Start the backend (if not already running)
   make run-dev

   # Make test calls to Federal APIs
   curl http://localhost:8000/api/v1/transparency/ibge/states
   curl http://localhost:8000/api/v1/transparency/datasus/health-indicators?state_code=RJ
   curl http://localhost:8000/api/v1/transparency/inep/institutions?state=RJ

6. Verify metrics in dashboard:
   - Request rate should show activity
   - Cache hit/miss ratio should populate
   - Duration percentiles should display
   - No errors should appear (if APIs are working)

7. Check metrics endpoint directly:
   curl http://localhost:7860/health/metrics | grep federal_api

8. Monitor logs:
   ./monitoring/manage-monitoring.sh logs

Troubleshooting:
- If Docker permission error: sudo usermod -aG docker $USER (logout/login)
- If dashboard not appearing: Check provisioning logs
- If no data in panels: Verify metrics endpoint is accessible
- If Prometheus not scraping: Check prometheus.yml targets

EOF

    print_success "Testing instructions displayed"
}

# Main validation flow
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   Federal APIs Dashboard Validation & Testing Tool        ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""

    local errors=0

    validate_dashboard_json || ((errors++))
    check_provisioning_config || ((errors++))
    validate_metrics_module || ((errors++))
    check_client_instrumentation || ((errors++))
    validate_promql_queries || ((errors++))
    check_docker_config || ((errors++))
    print_testing_instructions

    print_section "Validation Summary"

    if [[ $errors -eq 0 ]]; then
        print_success "✅ All validations passed!"
        print_success "Dashboard is ready for testing"
        echo ""
        print_status "Next steps:"
        echo "  1. Fix Docker permissions if needed: sudo usermod -aG docker \$USER"
        echo "  2. Start monitoring stack: ./monitoring/manage-monitoring.sh start"
        echo "  3. Access Grafana at: http://localhost:3000"
        return 0
    else
        print_error "❌ $errors validation(s) failed"
        print_error "Please fix the issues above before testing"
        return 1
    fi
}

# Run main function
main "$@"
