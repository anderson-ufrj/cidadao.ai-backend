#!/bin/bash
#
# Setup Git Hooks - Cidadão.AI
# Configures git hooks for automated README synchronization
#

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Setting up Git Hooks for Cidadão.AI${NC}"
echo -e "${BLUE}======================================${NC}"

# Get project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}📁 Project root: $PROJECT_ROOT${NC}"

# Check if we're in a git repository
if [[ ! -d "$PROJECT_ROOT/.git" ]]; then
    echo -e "${RED}❌ Not a git repository${NC}"
    exit 1
fi

# Create hooks directory if it doesn't exist
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"
if [[ ! -d "$HOOKS_DIR" ]]; then
    mkdir -p "$HOOKS_DIR"
    echo -e "${GREEN}📁 Created hooks directory${NC}"
fi

# Install pre-push hook
PRE_PUSH_SOURCE="$PROJECT_ROOT/.githooks/pre-push"
PRE_PUSH_TARGET="$HOOKS_DIR/pre-push"

if [[ -f "$PRE_PUSH_SOURCE" ]]; then
    cp "$PRE_PUSH_SOURCE" "$PRE_PUSH_TARGET"
    chmod +x "$PRE_PUSH_TARGET"
    echo -e "${GREEN}✅ Installed pre-push hook${NC}"
else
    echo -e "${RED}❌ Pre-push hook source not found: $PRE_PUSH_SOURCE${NC}"
    exit 1
fi

# Test sync script
SYNC_SCRIPT="$PROJECT_ROOT/scripts/sync_readme.py"
if [[ -f "$SYNC_SCRIPT" ]]; then
    echo -e "${BLUE}🧪 Testing sync script...${NC}"
    cd "$PROJECT_ROOT"
    python3 "$SYNC_SCRIPT" --check
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Sync script is working${NC}"
    else
        echo -e "${YELLOW}⚠️  Sync script test failed, but continuing...${NC}"
    fi
else
    echo -e "${RED}❌ Sync script not found: $SYNC_SCRIPT${NC}"
    exit 1
fi

# Configure git hooks path (optional)
echo -e "${BLUE}🔧 Configuring git hooks path...${NC}"
git config core.hooksPath .githooks 2>/dev/null
if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ Git hooks path configured to use .githooks${NC}"
else
    echo -e "${YELLOW}⚠️  Could not set hooks path, using standard .git/hooks${NC}"
fi

# Show current git remotes
echo -e "${BLUE}🌐 Current git remotes:${NC}"
git remote -v

echo -e "${GREEN}🎉 Git hooks setup complete!${NC}"
echo -e "${BLUE}📋 Next steps:${NC}"
echo -e "   1. The pre-push hook will automatically sync README files"
echo -e "   2. Use ${YELLOW}python scripts/sync_readme.py --check${NC} to check status"
echo -e "   3. Use ${YELLOW}python scripts/sync_readme.py --auto-detect${NC} for manual sync"
echo -e "   4. GitHub Actions will validate README format on pushes"

echo -e "${BLUE}💡 Manual usage:${NC}"
echo -e "   • Sync for GitHub: ${YELLOW}python scripts/sync_readme.py --target github${NC}"
echo -e "   • Sync for HF:     ${YELLOW}python scripts/sync_readme.py --target hf${NC}"
echo -e "   • Auto-detect:     ${YELLOW}python scripts/sync_readme.py --auto-detect${NC}"