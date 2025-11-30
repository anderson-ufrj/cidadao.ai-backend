"""
Dashboard HTML View Routes.

Provides embedded HTML dashboard for direct backend monitoring.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Dashboard View"])

# HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cidadao.AI - Agent Metrics Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .status-healthy { color: #10b981; }
        .status-degraded { color: #f59e0b; }
        .status-unhealthy { color: #ef4444; }
        .status-unknown { color: #6b7280; }
        .bg-healthy { background-color: #d1fae5; }
        .bg-degraded { background-color: #fef3c7; }
        .bg-unhealthy { background-color: #fee2e2; }
        .pulse { animation: pulse 2s infinite; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <!-- Header -->
    <header class="bg-gradient-to-r from-blue-800 to-blue-600 text-white shadow-lg">
        <div class="container mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <div class="flex items-center space-x-3">
                    <span class="text-3xl">🏛️</span>
                    <div>
                        <h1 class="text-xl font-bold">Cidadao.AI</h1>
                        <p class="text-blue-200 text-sm">Agent Metrics Dashboard</p>
                    </div>
                </div>
                <div class="text-right text-sm">
                    <div id="last-update" class="text-blue-200">Loading...</div>
                    <div class="flex items-center space-x-2 mt-1">
                        <span id="auto-refresh-indicator" class="w-2 h-2 rounded-full bg-green-400 pulse"></span>
                        <span>Auto-refresh: <span id="refresh-status">ON</span></span>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <main class="container mx-auto px-4 py-6">
        <!-- Overview Cards -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-white rounded-lg shadow p-4">
                <div class="text-gray-500 text-sm">Total Agents</div>
                <div id="total-agents" class="text-3xl font-bold text-blue-600">-</div>
            </div>
            <div id="healthy-card" class="bg-white rounded-lg shadow p-4">
                <div class="text-gray-500 text-sm">Healthy</div>
                <div id="healthy-agents" class="text-3xl font-bold status-healthy">-</div>
            </div>
            <div id="degraded-card" class="bg-white rounded-lg shadow p-4">
                <div class="text-gray-500 text-sm">Degraded</div>
                <div id="degraded-agents" class="text-3xl font-bold status-degraded">-</div>
            </div>
            <div class="bg-white rounded-lg shadow p-4">
                <div class="text-gray-500 text-sm">Success Rate</div>
                <div id="success-rate" class="text-3xl font-bold text-green-600">-</div>
            </div>
        </div>

        <!-- Performance Summary -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div class="bg-white rounded-lg shadow p-4">
                <div class="text-gray-500 text-sm">Total Requests</div>
                <div id="total-requests" class="text-2xl font-bold">-</div>
            </div>
            <div class="bg-white rounded-lg shadow p-4">
                <div class="text-gray-500 text-sm">Avg Response Time</div>
                <div id="avg-response-time" class="text-2xl font-bold">-</div>
            </div>
            <div class="bg-white rounded-lg shadow p-4">
                <div class="text-gray-500 text-sm">Avg Quality Score</div>
                <div id="avg-quality" class="text-2xl font-bold">-</div>
            </div>
        </div>

        <!-- Chart and Leaderboard -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <!-- Response Time Chart -->
            <div class="bg-white rounded-lg shadow p-4">
                <h2 class="text-lg font-semibold mb-4">📊 Response Time by Agent</h2>
                <canvas id="responseTimeChart" height="300"></canvas>
            </div>

            <!-- Agent Leaderboard -->
            <div class="bg-white rounded-lg shadow p-4">
                <h2 class="text-lg font-semibold mb-4">🏆 Agent Leaderboard</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-3 py-2 text-left">#</th>
                                <th class="px-3 py-2 text-left">Agent</th>
                                <th class="px-3 py-2 text-right">Requests</th>
                                <th class="px-3 py-2 text-right">Avg RT</th>
                                <th class="px-3 py-2 text-center">Status</th>
                            </tr>
                        </thead>
                        <tbody id="leaderboard-body">
                            <tr><td colspan="5" class="text-center py-4">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Recent Errors -->
        <div class="bg-white rounded-lg shadow p-4">
            <h2 class="text-lg font-semibold mb-4">⚠️ Recent Errors</h2>
            <div id="errors-container" class="space-y-2">
                <p class="text-gray-500 text-sm">No recent errors</p>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-4 mt-8">
        <div class="container mx-auto px-4 text-center text-sm">
            <p>🇧🇷 Cidadao.AI - Democratizing Government Transparency Through AI</p>
            <p class="text-gray-400 mt-1">
                <a href="/docs" class="hover:text-blue-400">API Docs</a> |
                <a href="/api/v1/dashboard/agents/summary" class="hover:text-blue-400">JSON API</a>
            </p>
        </div>
    </footer>

    <script>
        // Configuration
        const API_BASE = '/api/v1/dashboard/agents';
        const REFRESH_INTERVAL = 10000; // 10 seconds

        let chart = null;
        let refreshTimer = null;

        // Status icons and colors
        const statusConfig = {
            healthy: { icon: '🟢', class: 'status-healthy', bg: 'bg-healthy' },
            degraded: { icon: '🟡', class: 'status-degraded', bg: 'bg-degraded' },
            unhealthy: { icon: '🔴', class: 'status-unhealthy', bg: 'bg-unhealthy' },
            unknown: { icon: '⚪', class: 'status-unknown', bg: '' }
        };

        // Fetch dashboard data
        async function fetchDashboard() {
            try {
                const response = await fetch(`${API_BASE}/summary`);
                if (!response.ok) throw new Error('Failed to fetch dashboard');
                const data = await response.json();
                updateDashboard(data);
            } catch (error) {
                console.error('Error fetching dashboard:', error);
                document.getElementById('last-update').textContent = 'Error loading data';
            }
        }

        // Update dashboard UI
        function updateDashboard(data) {
            // Update timestamp
            const now = new Date();
            document.getElementById('last-update').textContent =
                `Last updated: ${now.toLocaleTimeString()}`;

            // Update overview cards
            document.getElementById('total-agents').textContent = data.overview.total_agents;
            document.getElementById('healthy-agents').textContent = data.overview.healthy_agents;
            document.getElementById('degraded-agents').textContent = data.overview.degraded_agents;
            document.getElementById('success-rate').textContent =
                `${data.performance.success_rate.toFixed(1)}%`;

            // Update card backgrounds based on status
            const overallStatus = data.overview.overall_health;
            document.getElementById('healthy-card').className =
                `bg-white rounded-lg shadow p-4 ${overallStatus === 'healthy' ? 'ring-2 ring-green-500' : ''}`;
            document.getElementById('degraded-card').className =
                `bg-white rounded-lg shadow p-4 ${overallStatus === 'degraded' ? 'ring-2 ring-yellow-500' : ''}`;

            // Update performance summary
            document.getElementById('total-requests').textContent =
                data.performance.total_requests.toLocaleString();
            document.getElementById('avg-response-time').textContent =
                `${data.performance.avg_response_time_ms.toFixed(0)}ms`;
            document.getElementById('avg-quality').textContent =
                data.performance.avg_quality_score.toFixed(2);

            // Update chart
            updateChart(data.top_performers);

            // Update leaderboard
            updateLeaderboard(data.top_performers);

            // Update errors
            updateErrors(data.recent_errors);
        }

        // Update response time chart
        function updateChart(agents) {
            const ctx = document.getElementById('responseTimeChart').getContext('2d');

            const labels = agents.map(a => a.identity.icon + ' ' + a.identity.display_name.split(' ')[0]);
            const responseTimes = agents.map(a => a.performance.avg_response_time_ms);
            const colors = agents.map(a => {
                const status = a.health_status;
                if (status === 'healthy') return 'rgba(16, 185, 129, 0.7)';
                if (status === 'degraded') return 'rgba(245, 158, 11, 0.7)';
                return 'rgba(239, 68, 68, 0.7)';
            });

            if (chart) {
                chart.data.labels = labels;
                chart.data.datasets[0].data = responseTimes;
                chart.data.datasets[0].backgroundColor = colors;
                chart.update('none');
            } else {
                chart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Response Time (ms)',
                            data: responseTimes,
                            backgroundColor: colors,
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: { display: true, text: 'Response Time (ms)' }
                            }
                        }
                    }
                });
            }
        }

        // Update leaderboard table
        function updateLeaderboard(agents) {
            const tbody = document.getElementById('leaderboard-body');

            if (agents.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-gray-500">No agent data available</td></tr>';
                return;
            }

            tbody.innerHTML = agents.map((agent, idx) => {
                const status = statusConfig[agent.health_status] || statusConfig.unknown;
                return `
                    <tr class="border-b hover:bg-gray-50">
                        <td class="px-3 py-2 font-medium">${idx + 1}</td>
                        <td class="px-3 py-2">
                            <span class="mr-1">${agent.identity.icon}</span>
                            <span class="font-medium">${agent.identity.display_name}</span>
                            <span class="text-gray-400 text-xs ml-1">(${agent.identity.role})</span>
                        </td>
                        <td class="px-3 py-2 text-right">${agent.performance.total_requests.toLocaleString()}</td>
                        <td class="px-3 py-2 text-right">${agent.performance.avg_response_time_ms.toFixed(0)}ms</td>
                        <td class="px-3 py-2 text-center">
                            <span class="${status.class}">${status.icon}</span>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        // Update errors section
        function updateErrors(errors) {
            const container = document.getElementById('errors-container');

            if (!errors || errors.length === 0) {
                container.innerHTML = '<p class="text-gray-500 text-sm">No recent errors</p>';
                return;
            }

            container.innerHTML = errors.slice(0, 5).map(error => `
                <div class="bg-red-50 border-l-4 border-red-400 p-3 rounded">
                    <div class="flex justify-between">
                        <span class="font-medium text-red-800">${error.agent_name}</span>
                        <span class="text-red-600 text-xs">${new Date(error.timestamp).toLocaleString()}</span>
                    </div>
                    <p class="text-red-700 text-sm mt-1">${error.message}</p>
                </div>
            `).join('');
        }

        // Start auto-refresh
        function startAutoRefresh() {
            refreshTimer = setInterval(fetchDashboard, REFRESH_INTERVAL);
            document.getElementById('refresh-status').textContent = 'ON';
            document.getElementById('auto-refresh-indicator').classList.add('pulse');
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            fetchDashboard();
            startAutoRefresh();
        });
    </script>
</body>
</html>
"""

# Embedded version (no header/footer, for iframe)
DASHBOARD_EMBED_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Metrics - Embedded</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .status-healthy { color: #10b981; }
        .status-degraded { color: #f59e0b; }
        .status-unhealthy { color: #ef4444; }
    </style>
</head>
<body class="bg-transparent p-4">
    <div class="grid grid-cols-4 gap-2 text-center">
        <div class="bg-white rounded shadow p-2">
            <div class="text-xs text-gray-500">Agents</div>
            <div id="total" class="text-xl font-bold">-</div>
        </div>
        <div class="bg-white rounded shadow p-2">
            <div class="text-xs text-gray-500">Healthy</div>
            <div id="healthy" class="text-xl font-bold status-healthy">-</div>
        </div>
        <div class="bg-white rounded shadow p-2">
            <div class="text-xs text-gray-500">Degraded</div>
            <div id="degraded" class="text-xl font-bold status-degraded">-</div>
        </div>
        <div class="bg-white rounded shadow p-2">
            <div class="text-xs text-gray-500">Success</div>
            <div id="success" class="text-xl font-bold text-green-600">-</div>
        </div>
    </div>
    <script>
        async function update() {
            try {
                const r = await fetch('/api/v1/dashboard/agents/summary');
                const d = await r.json();
                document.getElementById('total').textContent = d.overview.total_agents;
                document.getElementById('healthy').textContent = d.overview.healthy_agents;
                document.getElementById('degraded').textContent = d.overview.degraded_agents;
                document.getElementById('success').textContent = d.performance.success_rate.toFixed(1) + '%';
            } catch(e) { console.error(e); }
        }
        update();
        setInterval(update, 10000);
    </script>
</body>
</html>
"""


@router.get(
    "/dashboard/agents",
    response_class=HTMLResponse,
    summary="Agent Metrics Dashboard",
    description="Visual dashboard for monitoring agent metrics directly in the browser.",
    include_in_schema=True,
)
async def dashboard_view(request: Request) -> HTMLResponse:
    """Render the agent metrics dashboard HTML page."""
    return HTMLResponse(content=DASHBOARD_HTML)


@router.get(
    "/dashboard/agents/embed",
    response_class=HTMLResponse,
    summary="Embedded Dashboard Widget",
    description="Minimal dashboard widget for embedding in iframes.",
    include_in_schema=True,
)
async def dashboard_embed(request: Request) -> HTMLResponse:
    """Render minimal embedded dashboard for iframes."""
    return HTMLResponse(content=DASHBOARD_EMBED_HTML)
