#!/bin/bash
# Deploy script for Celery Workers on VPS (without FastAPI)
# Author: Anderson Henrique da Silva
# Date: 2025-10-07 18:20:00
#
# This script sets up ONLY the Celery workers for 24/7 auto-investigations
# The FastAPI API continues running on HuggingFace Spaces
# Both save to the same Supabase database

set -e

echo "🚀 Setting up Celery Workers for 24/7 Auto-Investigation"
echo "=========================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (sudo)"
    exit 1
fi

# Update system
echo "📦 Updating system..."
apt-get update
apt-get upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
apt-get install -y python3 python3-pip python3-venv redis-server supervisor git

# Start Redis
echo "🔴 Starting Redis..."
systemctl start redis
systemctl enable redis

# Create app user
echo "👤 Creating app user..."
useradd -m -s /bin/bash cidadao-ai || true

# Clone repository (or you can scp/rsync your code)
echo "📥 Cloning repository..."
cd /opt
git clone https://github.com/anderson-ufrj/cidadao.ai-backend.git || true
cd cidadao-ai-backend
chown -R cidadao-ai:cidadao-ai /opt/cidadao-ai-backend

# Setup Python environment
echo "🐍 Setting up Python environment..."
su - cidadao-ai -c "cd /opt/cidadao-ai-backend && python3 -m venv venv"
su - cidadao-ai -c "cd /opt/cidadao-ai-backend && venv/bin/pip install --upgrade pip"
su - cidadao-ai -c "cd /opt/cidadao-ai-backend && venv/bin/pip install -r requirements.txt"

# Create .env file
echo "⚙️  Creating .env file..."
cat > /opt/cidadao-ai-backend/.env << 'EOF'
# Redis
REDIS_URL=redis://localhost:6379/0

# Supabase (SAME as HuggingFace Spaces)
SUPABASE_URL=your-supabase-url-here
SUPABASE_SERVICE_ROLE_KEY=your-supabase-key-here

# Portal da Transparência
TRANSPARENCY_API_KEY=your-api-key-here

# LLM (for agents)
GROQ_API_KEY=your-groq-key-here

# Environment
ENVIRONMENT=production
ENABLE_CELERY_WORKERS=true
EOF

echo "⚠️  IMPORTANT: Edit /opt/cidadao-ai-backend/.env with your credentials!"
echo "   - SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (same as HF Spaces)"
echo "   - TRANSPARENCY_API_KEY (optional but recommended)"
echo "   - GROQ_API_KEY (for AI agents)"

# Create Supervisor configuration for Celery Worker
echo "📋 Creating Supervisor config for Worker..."
cat > /etc/supervisor/conf.d/cidadao-ai-worker.conf << 'EOF'
[program:cidadao-ai-worker]
command=/opt/cidadao-ai-backend/venv/bin/celery -A src.infrastructure.queue.celery_app worker --loglevel=info --queues=critical,high,default,low,background --concurrency=4
directory=/opt/cidadao-ai-backend
user=cidadao-ai
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
stderr_logfile=/var/log/celery/worker.err.log
environment=PATH="/opt/cidadao-ai-backend/venv/bin"
EOF

# Create Supervisor configuration for Celery Beat
echo "📋 Creating Supervisor config for Beat..."
cat > /etc/supervisor/conf.d/cidadao-ai-beat.conf << 'EOF'
[program:cidadao-ai-beat]
command=/opt/cidadao-ai-backend/venv/bin/celery -A src.infrastructure.queue.celery_app beat --loglevel=info
directory=/opt/cidadao-ai-backend
user=cidadao-ai
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
stderr_logfile=/var/log/celery/beat.err.log
environment=PATH="/opt/cidadao-ai-backend/venv/bin"
EOF

# Create log directory
mkdir -p /var/log/celery
chown cidadao-ai:cidadao-ai /var/log/celery

# Reload Supervisor
echo "🔄 Reloading Supervisor..."
supervisorctl reread
supervisorctl update

# Start services
echo "▶️  Starting Celery services..."
supervisorctl start cidadao-ai-worker
supervisorctl start cidadao-ai-beat

# Check status
sleep 3
echo ""
echo "📊 Service Status:"
supervisorctl status cidadao-ai-worker cidadao-ai-beat

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit /opt/cidadao-ai-backend/.env with your credentials"
echo "2. Restart services: supervisorctl restart cidadao-ai-worker cidadao-ai-beat"
echo "3. Monitor logs: tail -f /var/log/celery/worker.log"
echo ""
echo "🎯 Workers will automatically investigate contracts 24/7 and save to Supabase"
echo "🌐 Your HuggingFace API will continue working normally at:"
echo "   https://neural-thinker-cidadao-ai-backend.hf.space"
echo ""
echo "💰 Estimated cost: $5-10/month for basic VPS"
