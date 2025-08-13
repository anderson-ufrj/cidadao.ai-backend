#!/bin/bash

# =========================================
# 📊 Update HuggingFace with Monitoring
# =========================================
# Script to update HF Spaces with monitoring
# =========================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}📊 Updating HuggingFace Spaces with Monitoring${NC}"
echo -e "${GREEN}================================================${NC}"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: app.py not found. Run from project root.${NC}"
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${YELLOW}📍 Current branch: $CURRENT_BRANCH${NC}"

# Stash any local changes
echo -e "${YELLOW}💾 Stashing local changes...${NC}"
git stash

# Switch to hf-fastapi branch
echo -e "${YELLOW}🔄 Switching to hf-fastapi branch...${NC}"
git checkout hf-fastapi

# Pull latest changes
echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
git pull origin hf-fastapi

# Apply the monitoring updates
echo -e "${YELLOW}📝 Applying monitoring updates...${NC}"

# Create the embedded monitoring HTML in app.py
cat >> app.py << 'EOF'

# Embedded monitoring HTML for HuggingFace Spaces
MONITORING_HTML_EMBEDDED = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 CIDADÃO.AI - Monitoring Dashboard</title>
    <style>
        :root { --primary: #10B981; --dark: #1F2937; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #111827; color: #E5E7EB; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { background: #1F2937; padding: 20px; margin-bottom: 30px; border-radius: 10px; }
        h1 { color: var(--primary); margin-bottom: 10px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: #1F2937; padding: 20px; border-radius: 10px; border: 1px solid #374151; }
        .metric-value { font-size: 2.5rem; font-weight: bold; color: #fff; margin: 10px 0; }
        .metric-label { color: #9CA3AF; font-size: 0.9rem; }
        .refresh-btn { background: var(--primary); color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
        .links { text-align: center; margin: 20px 0; }
        .links a { color: var(--primary); margin: 0 10px; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 CIDADÃO.AI - Monitoring Dashboard</h1>
            <p>Monitoramento em tempo real - HuggingFace Spaces</p>
        </header>
        <div class="links">
            <a href="/">🏠 Home</a> | 
            <a href="/docs">📚 API Docs</a> | 
            <a href="/metrics">📊 Métricas Raw</a>
        </div>
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>🏛️ Status</h3>
                <div class="metric-value">✅ Online</div>
                <div class="metric-label">HuggingFace Spaces</div>
            </div>
            <div class="metric-card">
                <h3>🔍 Investigações</h3>
                <div class="metric-value" id="investigations">--</div>
                <div class="metric-label">Total realizado</div>
            </div>
            <div class="metric-card">
                <h3>🚨 Anomalias</h3>
                <div class="metric-value" id="anomalies">--</div>
                <div class="metric-label">Detectadas</div>
            </div>
            <div class="metric-card">
                <h3>🤖 Agentes</h3>
                <div class="metric-value">1</div>
                <div class="metric-label">Zumbi Ativo</div>
            </div>
        </div>
        <center>
            <button class="refresh-btn" onclick="location.reload()">🔄 Atualizar</button>
        </center>
    </div>
    <script>
        fetch('/metrics').then(r => r.text()).then(text => {
            const inv = text.match(/cidadao_investigations_total.*\s+(\d+)/);
            const anom = text.match(/cidadao_anomalies_detected_total.*\s+(\d+)/);
            if (inv) document.getElementById('investigations').textContent = inv[1];
            if (anom) document.getElementById('anomalies').textContent = anom[1];
        });
    </script>
</body>
</html>"""
EOF

# Update the monitoring endpoint to use embedded HTML
echo -e "${YELLOW}📝 Updating monitoring endpoint...${NC}"
sed -i 's/from monitoring_embedded import MONITORING_HTML/# Use embedded HTML/g' app.py
sed -i 's/return HTMLResponse(content=MONITORING_HTML)/return HTMLResponse(content=MONITORING_HTML_EMBEDDED)/g' app.py

# Remove the import line if it exists
sed -i '/import monitoring_embedded/d' app.py

# Commit changes
echo -e "${YELLOW}💾 Committing changes...${NC}"
git add app.py
git commit -m "feat: add embedded monitoring dashboard for HF Spaces

- Add /monitoring endpoint with visual dashboard
- Embedded HTML to avoid import issues
- Real-time metrics visualization
- Auto-refresh functionality"

# Push to HuggingFace
echo -e "${YELLOW}🚀 Pushing to HuggingFace...${NC}"
git push origin hf-fastapi

# Return to original branch
echo -e "${YELLOW}🔄 Returning to $CURRENT_BRANCH branch...${NC}"
git checkout $CURRENT_BRANCH

# Restore stashed changes
echo -e "${YELLOW}💾 Restoring stashed changes...${NC}"
git stash pop || true

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Monitoring update complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "\n${YELLOW}📊 Check the monitoring at:${NC}"
echo -e "${GREEN}https://neural-thinker-cidadao-ai-backend.hf.space/monitoring${NC}"
echo -e "\n${YELLOW}📈 Raw metrics at:${NC}"
echo -e "${GREEN}https://neural-thinker-cidadao-ai-backend.hf.space/metrics${NC}"