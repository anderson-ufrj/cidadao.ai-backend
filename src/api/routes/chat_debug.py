"""
Debug version of chat.py to understand the error
"""
print("=== CHAT MODULE IMPORT DEBUG ===")
print("Starting imports...")

try:
    from fastapi import APIRouter, Depends, HTTPException, Request
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field
    from typing import Optional, Dict, Any, List
    import asyncio
    import json
    import uuid
    from datetime import datetime
    print("✓ Basic imports OK")
except Exception as e:
    print(f"✗ Basic imports failed: {e}")
    raise

try:
    from src.core import get_logger
    from src.core.exceptions import ValidationError
    from src.api.dependencies import get_current_optional_user
    from src.api.routes.chat_drummond_factory import get_drummond_agent
    print("✓ Core imports OK")
except Exception as e:
    print(f"✗ Core imports failed: {e}")
    raise

try:
    from src.agents.deodoro import AgentMessage, AgentContext, AgentResponse, AgentStatus
    print("✓ Deodoro imports OK")
except Exception as e:
    print(f"✗ Deodoro imports failed: {e}")
    raise

try:
    from src.agents.abaporu import MasterAgent
    print("✓ MasterAgent import OK")
except Exception as e:
    print(f"✗ MasterAgent import failed: {e}")
    # This might be the real error!
    raise

try:
    from src.services.chat_service_with_cache import chat_service
    from src.services.chat_service import IntentDetector, IntentType
    from src.api.models.pagination import CursorPaginationResponse
    print("✓ Service imports OK")
except Exception as e:
    print(f"✗ Service imports failed: {e}")
    raise

# Import the simple Zumbi agent for investigations
try:
    import sys
    sys.path.append('/')
    from app import enhanced_zumbi, UniversalSearchRequest, DataSourceType
    print("✓ Zumbi imports OK")
except Exception as e:
    print(f"✗ Zumbi imports failed: {e}")
    raise

logger = get_logger(__name__)
print("✓ Logger created")

router = APIRouter(tags=["chat"])
print("✓ Router created")

# Services are already initialized
intent_detector = IntentDetector()
print("✓ IntentDetector created")

# Initialize master agent
print("Attempting to create MasterAgent...")
try:
    master_agent = MasterAgent()
    print("✓ MasterAgent created successfully!")
except Exception as e:
    print(f"✗ MasterAgent creation failed: {type(e).__name__}: {e}")
    import traceback
    print(traceback.format_exc())
    raise

print("=== CHAT MODULE IMPORT COMPLETE ===")