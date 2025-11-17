#!/bin/bash

# Railway 403 Forbidden Fix Script
# Automatically configures Railway to disable IP whitelist

set -e

echo "=================================="
echo "Railway 403 Forbidden Fix Script"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI not found!${NC}"
    echo ""
    echo "Install it with:"
    echo "  npm install -g @railway/cli"
    echo "  or"
    echo "  brew install railway"
    exit 1
fi

echo -e "${GREEN}✓ Railway CLI found${NC}"

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}⚠ Not logged in to Railway${NC}"
    echo ""
    echo "Logging in..."
    railway login
fi

echo -e "${GREEN}✓ Logged in to Railway${NC}"
echo ""

# Show current project
echo "Current project:"
railway status || echo "No project linked"
echo ""

# Ask for confirmation
echo -e "${YELLOW}This will:${NC}"
echo "  1. Disable IP whitelist (ENABLE_IP_WHITELIST=false)"
echo "  2. Trigger automatic redeploy"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Set variable
echo ""
echo "Setting ENABLE_IP_WHITELIST=false..."

if railway variables --set "ENABLE_IP_WHITELIST=false" -s cidadao-api; then
    echo -e "${GREEN}✓ Variable set successfully${NC}"
else
    echo -e "${RED}❌ Failed to set variable${NC}"
    echo ""
    echo "Manual steps:"
    echo "  1. Go to: https://railway.app/"
    echo "  2. Select project: cidadao.ai"
    echo "  3. Select service: cidadao-api"
    echo "  4. Go to Variables tab"
    echo "  5. Add: ENABLE_IP_WHITELIST = false"
    exit 1
fi

echo ""
echo "Waiting for deployment..."
sleep 5

# Show deployment status
railway status

echo ""
echo -e "${GREEN}✓ Configuration complete!${NC}"
echo ""
echo "Verification steps:"
echo "  1. Wait ~2 minutes for Railway to redeploy"
echo "  2. Test health endpoint:"
echo "     curl https://cidadao-api-production.up.railway.app/health"
echo ""
echo "  3. Check logs:"
echo "     railway logs -s cidadao-api"
echo ""
echo -e "${YELLOW}Expected: No more '403 Forbidden' or 'IP address blocked' errors${NC}"
echo ""
