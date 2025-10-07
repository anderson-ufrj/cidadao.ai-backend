#!/bin/bash
# Deploy Script for Cidadão.AI

set -e

echo "🚀 Cidadão.AI Deploy Script"
echo "=========================="

# Check environment
if [ -z "$1" ]; then
    echo "Usage: ./deploy.sh [local|render|railway|k8s|vps]"
    exit 1
fi

DEPLOY_TARGET=$1

case $DEPLOY_TARGET in
    "local")
        echo "📦 Deploying locally with Docker Compose..."
        
        # Check if .env exists
        if [ ! -f .env ]; then
            echo "Creating .env file..."
            cp .env.example .env
            echo "⚠️  Please edit .env with your credentials"
            exit 1
        fi
        
        # Build and start services
        docker-compose -f docker-compose.production.yml up -d --build
        
        # Run migrations
        echo "Running database migrations..."
        docker-compose -f docker-compose.production.yml exec api python -m alembic upgrade head
        
        echo "✅ Local deployment complete!"
        echo "🌐 API available at http://localhost:8000"
        ;;
        
    "render")
        echo "☁️  Deploying to Render..."
        
        # Check Render CLI
        if ! command -v render &> /dev/null; then
            echo "Installing Render CLI..."
            pip install render-cli
        fi
        
        # Deploy
        render up
        
        echo "✅ Render deployment initiated!"
        ;;
        
    "railway")
        echo "🚂 Deploying to Railway..."
        
        # Check Railway CLI
        if ! command -v railway &> /dev/null; then
            echo "Please install Railway CLI: https://docs.railway.app/develop/cli"
            exit 1
        fi
        
        # Login and deploy
        railway login
        railway up
        
        echo "✅ Railway deployment complete!"
        ;;
        
    "k8s")
        echo "☸️  Deploying to Kubernetes..."
        
        # Check kubectl
        if ! command -v kubectl &> /dev/null; then
            echo "kubectl not found. Please install it first."
            exit 1
        fi
        
        # Create namespace
        kubectl create namespace cidadao-ai --dry-run=client -o yaml | kubectl apply -f -
        
        # Create secrets
        echo "Creating secrets..."
        kubectl create secret generic cidadao-secrets \
            --from-literal=database-url="${DATABASE_URL}" \
            --from-literal=redis-url="${REDIS_URL}" \
            --from-literal=maritaca-api-key="${MARITACA_API_KEY}" \
            --namespace=cidadao-ai \
            --dry-run=client -o yaml | kubectl apply -f -
        
        # Apply configurations
        kubectl apply -f k8s/ -n cidadao-ai
        
        echo "✅ Kubernetes deployment complete!"
        ;;
        
    "vps")
        echo "🖥️  Deploying to VPS..."
        
        # Check SSH config
        if [ -z "$VPS_HOST" ]; then
            echo "Please set VPS_HOST environment variable"
            exit 1
        fi
        
        # Copy files
        echo "Copying files to VPS..."
        rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='.env' . $VPS_HOST:~/cidadao-ai/
        
        # Setup on VPS
        ssh $VPS_HOST << 'ENDSSH'
            cd ~/cidadao-ai
            
            # Install Docker if needed
            if ! command -v docker &> /dev/null; then
                curl -fsSL https://get.docker.com | sh
                sudo usermod -aG docker $USER
            fi
            
            # Install Docker Compose if needed
            if ! command -v docker-compose &> /dev/null; then
                sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                sudo chmod +x /usr/local/bin/docker-compose
            fi
            
            # Start services
            docker-compose -f docker-compose.production.yml up -d --build
            
            # Setup nginx and SSL
            sudo apt-get update
            sudo apt-get install -y nginx certbot python3-certbot-nginx
            
            echo "VPS setup complete!"
ENDSSH
        
        echo "✅ VPS deployment complete!"
        ;;
        
    *)
        echo "❌ Unknown deploy target: $DEPLOY_TARGET"
        echo "Options: local, render, railway, k8s, vps"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment finished!"
echo ""
echo "Next steps:"
echo "1. Check application logs"
echo "2. Run health checks"
echo "3. Configure monitoring"
echo "4. Setup backups"