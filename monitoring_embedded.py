# Embedded monitoring HTML for HuggingFace Spaces
MONITORING_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 CIDADÃO.AI - Monitoring Dashboard</title>
    <style>
        :root {
            --primary: #10B981;
            --secondary: #3B82F6;
            --danger: #EF4444;
            --warning: #F59E0B;
            --dark: #1F2937;
            --light: #F3F4F6;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #111827;
            color: #E5E7EB;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            background: #1F2937;
            padding: 20px 0;
            margin-bottom: 30px;
            border-bottom: 2px solid var(--primary);
        }

        h1 {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 2rem;
            color: var(--primary);
        }

        .subtitle {
            color: #9CA3AF;
            margin-top: 5px;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: #1F2937;
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #374151;
            transition: transform 0.2s, border-color 0.2s;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            border-color: var(--primary);
        }

        .metric-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .metric-title {
            font-size: 1.1rem;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #fff;
            margin-bottom: 10px;
        }

        .metric-label {
            color: #9CA3AF;
            font-size: 0.9rem;
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--primary);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.6; }
            100% { opacity: 1; }
        }

        .agents-section {
            background: #1F2937;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
        }

        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .agent-card {
            background: #111827;
            border: 1px solid #374151;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            transition: all 0.2s;
        }

        .agent-card.active {
            border-color: var(--primary);
            background: #065F46;
        }

        .agent-icon {
            font-size: 2rem;
            margin-bottom: 8px;
        }

        .agent-name {
            font-weight: 600;
            margin-bottom: 5px;
        }

        .agent-status {
            font-size: 0.85rem;
            color: #9CA3AF;
        }

        .chart-container {
            background: #1F2937;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
        }

        .chart-title {
            font-size: 1.3rem;
            color: var(--primary);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .refresh-btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: background 0.2s;
            margin: 20px auto;
        }

        .refresh-btn:hover {
            background: #059669;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #9CA3AF;
        }

        .error-message {
            background: #991B1B;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }

        #lastUpdate {
            color: #9CA3AF;
            font-size: 0.9rem;
            margin-left: auto;
        }

        .links-section {
            background: #1F2937;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }

        .links-section a {
            color: var(--primary);
            text-decoration: none;
            margin: 0 10px;
            padding: 8px 16px;
            border: 1px solid var(--primary);
            border-radius: 6px;
            display: inline-block;
            transition: all 0.2s;
        }

        .links-section a:hover {
            background: var(--primary);
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>
                📊 CIDADÃO.AI - Monitoring Dashboard
                <span id="lastUpdate"></span>
            </h1>
            <p class="subtitle">Monitoramento em tempo real do sistema multi-agente de transparência pública</p>
        </header>

        <div class="error-message" id="errorMessage"></div>

        <div class="links-section">
            <a href="/">🏠 Home</a>
            <a href="/docs">📚 API Docs</a>
            <a href="/metrics">📊 Métricas Raw</a>
            <a href="/api/agents/zumbi">🏹 Zumbi Agent</a>
        </div>

        <!-- Main Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-title">🏛️ System Status</span>
                    <span class="status-indicator" id="systemStatus"></span>
                </div>
                <div class="metric-value" id="systemVersion">v1.2.0</div>
                <div class="metric-label">HuggingFace Spaces</div>
            </div>

            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-title">🔍 Investigações</span>
                </div>
                <div class="metric-value" id="totalInvestigations">--</div>
                <div class="metric-label">Total de investigações realizadas</div>
            </div>

            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-title">🚨 Anomalias</span>
                </div>
                <div class="metric-value" id="totalAnomalies">--</div>
                <div class="metric-label">Anomalias detectadas</div>
            </div>

            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-title">🤖 Agentes</span>
                </div>
                <div class="metric-value" id="activeAgents">1</div>
                <div class="metric-label">Agentes ativos (Zumbi)</div>
            </div>
        </div>

        <!-- Agents Status -->
        <div class="agents-section">
            <h2 class="chart-title">🤖 Status dos Agentes</h2>
            <div class="agents-grid" id="agentsGrid">
                <div class="agent-card active">
                    <div class="agent-icon">🏹</div>
                    <div class="agent-name">Zumbi dos Palmares</div>
                    <div class="agent-status">✅ Ativo</div>
                </div>
                <div class="agent-card">
                    <div class="agent-icon">⚔️</div>
                    <div class="agent-name">Anita Garibaldi</div>
                    <div class="agent-status">🚧 Em desenvolvimento</div>
                </div>
                <div class="agent-card">
                    <div class="agent-icon">🗡️</div>
                    <div class="agent-name">Tiradentes</div>
                    <div class="agent-status">🚧 Em desenvolvimento</div>
                </div>
                <div class="agent-card">
                    <div class="agent-icon">📝</div>
                    <div class="agent-name">Machado de Assis</div>
                    <div class="agent-status">📅 Planejado</div>
                </div>
                <div class="agent-card">
                    <div class="agent-icon">🏛️</div>
                    <div class="agent-name">José Bonifácio</div>
                    <div class="agent-status">📅 Planejado</div>
                </div>
                <div class="agent-card">
                    <div class="agent-icon">👑</div>
                    <div class="agent-name">Dandara</div>
                    <div class="agent-status">📅 Planejado</div>
                </div>
            </div>
        </div>

        <!-- API Examples -->
        <div class="chart-container">
            <h2 class="chart-title">🚀 Exemplos de Uso</h2>
            <pre style="background: #111827; padding: 15px; border-radius: 8px; overflow-x: auto;">
# Obter dados de teste
curl https://neural-thinker-cidadao-ai-backend.hf.space/api/agents/zumbi/test

# Investigar anomalias
curl -X POST https://neural-thinker-cidadao-ai-backend.hf.space/api/agents/zumbi/investigate \\
  -H "Content-Type: application/json" \\
  -d @test_data.json
            </pre>
        </div>

        <!-- Refresh Button -->
        <button class="refresh-btn" onclick="refreshMetrics()">
            🔄 Atualizar Métricas
        </button>
    </div>

    <script>
        // Parse Prometheus metrics format
        function parseMetrics(text) {
            const lines = text.split('\\n');
            const metrics = {};
            
            lines.forEach(line => {
                if (line.startsWith('#') || !line.trim()) return;
                
                const match = line.match(/^([a-zA-Z_:][a-zA-Z0-9_:]*(?:\\{[^}]+\\})?)\\s+(.+)$/);
                if (match) {
                    const [_, name, value] = match;
                    metrics[name] = parseFloat(value);
                }
            });
            
            return metrics;
        }

        // Update UI with metrics
        function updateUI(metrics) {
            // Investigations total
            let totalInvestigations = 0;
            Object.keys(metrics).forEach(key => {
                if (key.startsWith('cidadao_investigations_total')) {
                    totalInvestigations += metrics[key] || 0;
                }
            });
            document.getElementById('totalInvestigations').textContent = 
                totalInvestigations > 0 ? totalInvestigations.toLocaleString('pt-BR') : '0';
            
            // Anomalies total
            let totalAnomalies = 0;
            Object.keys(metrics).forEach(key => {
                if (key.startsWith('cidadao_anomalies_detected_total')) {
                    totalAnomalies += metrics[key] || 0;
                }
            });
            document.getElementById('totalAnomalies').textContent = 
                totalAnomalies > 0 ? totalAnomalies.toLocaleString('pt-BR') : '0';
            
            // Active agents count
            const activeAgents = metrics['cidadao_agents_active_total'] || 1;
            document.getElementById('activeAgents').textContent = activeAgents;
            
            // Update last update time
            const now = new Date();
            document.getElementById('lastUpdate').textContent = 
                `Última atualização: ${now.toLocaleTimeString('pt-BR')}`;
        }

        // Fetch and refresh metrics
        async function refreshMetrics() {
            try {
                const response = await fetch('/metrics');
                if (!response.ok) throw new Error('Failed to fetch metrics');
                
                const text = await response.text();
                const metrics = parseMetrics(text);
                updateUI(metrics);
                
                document.getElementById('errorMessage').style.display = 'none';
                document.getElementById('systemStatus').style.background = '#10B981';
            } catch (error) {
                console.error('Error fetching metrics:', error);
                document.getElementById('errorMessage').textContent = 
                    'Erro ao carregar métricas. Tentando novamente...';
                document.getElementById('errorMessage').style.display = 'block';
                document.getElementById('systemStatus').style.background = '#EF4444';
            }
        }

        // Auto-refresh every 30 seconds
        setInterval(refreshMetrics, 30000);
        
        // Initial load
        refreshMetrics();
    </script>
</body>
</html>"""