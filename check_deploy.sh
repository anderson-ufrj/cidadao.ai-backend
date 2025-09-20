#!/bin/bash
# Script to check HuggingFace deployment status

echo "======================================"
echo "🔍 HuggingFace Deployment Check"
echo "======================================"
echo ""
echo "📅 Current time: $(date)"
echo ""
echo "🏷️  Expected version markers:"
echo "   - Deploy timestamp: 2025-09-20 13:46:00 -03"
echo "   - Version: MAIN BRANCH - Full multi-agent system"
echo "   - Fixed: Lazy initialization + MasterAgent import"
echo ""
echo "📋 To verify deployment:"
echo "   1. Check https://neural-thinker-cidadao-ai-backend.hf.space/"
echo "   2. Look for 'healthy' status (not 'degraded')"
echo "   3. Test chat endpoint: https://neural-thinker-cidadao-ai-backend.hf.space/api/v1/chat/message"
echo ""
echo "🔄 Latest commits:"
git log --oneline -n 5
echo ""
echo "======================================"