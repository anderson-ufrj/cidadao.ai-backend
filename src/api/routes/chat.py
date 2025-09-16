"""
Chat API endpoints for conversational interface
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import asyncio
import json
import uuid
from datetime import datetime

from src.core import get_logger
from src.core.exceptions import ValidationError
from src.api.dependencies import get_current_optional_user
from src.agents.abaporu import MasterAgent
from src.agents.deodoro import AgentMessage, AgentContext
from src.services.chat_service import ChatService, IntentDetector, IntentType

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Initialize services
chat_service = ChatService()
intent_detector = IntentDetector()
master_agent = MasterAgent()

class ChatRequest(BaseModel):
    """Chat message request"""
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
class ChatResponse(BaseModel):
    """Chat message response"""
    session_id: str
    agent_id: str
    agent_name: str
    message: str
    confidence: float
    suggested_actions: Optional[List[str]] = None
    requires_input: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = {}

class QuickAction(BaseModel):
    """Quick action suggestion"""
    id: str
    label: str
    icon: str
    action: str

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user = Depends(get_current_optional_user)
) -> ChatResponse:
    """
    Process a chat message and return agent response
    """
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        session = await chat_service.get_or_create_session(
            session_id, 
            user_id=current_user.id if current_user else None
        )
        
        # Detect intent from message
        intent = await intent_detector.detect(request.message)
        logger.info(f"Detected intent: {intent.type} with confidence {intent.confidence}")
        
        # Create agent message
        agent_message = AgentMessage(
            content={
                "user_message": request.message,
                "intent": intent.dict(),
                "context": request.context or {},
                "session": session.to_dict()
            },
            sender="user",
            context=AgentContext(
                investigation_id=session.current_investigation_id,
                user_id=session.user_id
            )
        )
        
        # Route to appropriate agent based on intent
        if intent.type == IntentType.INVESTIGATE:
            # For investigations, use master agent to coordinate
            response = await master_agent.process(agent_message)
            agent_id = "abaporu"
            agent_name = "Abaporu"
        else:
            # Route to specific agent
            agent = await chat_service.get_agent_for_intent(intent)
            response = await agent.process(agent_message)
            agent_id = agent.agent_id
            agent_name = agent.name
        
        # Save to chat history
        await chat_service.save_message(
            session_id=session_id,
            role="user",
            content=request.message
        )
        
        await chat_service.save_message(
            session_id=session_id,
            role="assistant",
            content=response.content,
            agent_id=agent_id
        )
        
        # Prepare suggested actions based on response
        suggested_actions = []
        if intent.type == IntentType.INVESTIGATE and not session.current_investigation_id:
            suggested_actions = ["start_investigation", "view_examples", "learn_more"]
        elif session.current_investigation_id:
            suggested_actions = ["view_progress", "generate_report", "new_investigation"]
        
        return ChatResponse(
            session_id=session_id,
            agent_id=agent_id,
            agent_name=agent_name,
            message=response.content.get("message", str(response.content)),
            confidence=response.metadata.get("confidence", intent.confidence),
            suggested_actions=suggested_actions,
            requires_input=response.content.get("requires_input"),
            metadata={
                "intent_type": intent.type.value,
                "processing_time": response.metadata.get("processing_time", 0),
                "is_demo_mode": not bool(current_user),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar mensagem")

@router.post("/stream")
async def stream_message(request: ChatRequest):
    """
    Stream chat response using Server-Sent Events (SSE)
    """
    async def generate():
        try:
            # Send initial event
            yield f"data: {json.dumps({'type': 'start', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
            
            # Detect intent
            yield f"data: {json.dumps({'type': 'detecting', 'message': 'Analisando sua mensagem...'})}\n\n"
            await asyncio.sleep(0.5)
            
            intent = await intent_detector.detect(request.message)
            yield f"data: {json.dumps({'type': 'intent', 'intent': intent.type.value, 'confidence': intent.confidence})}\n\n"
            
            # Select agent
            agent = await chat_service.get_agent_for_intent(intent)
            yield f"data: {json.dumps({'type': 'agent_selected', 'agent_id': agent.agent_id, 'agent_name': agent.name})}\n\n"
            await asyncio.sleep(0.3)
            
            # Process message in chunks (simulate typing)
            response_text = f"Olá! Sou {agent.name} e vou ajudá-lo com sua solicitação sobre {intent.type.value}."
            
            # Send response in chunks
            words = response_text.split()
            chunk = ""
            for i, word in enumerate(words):
                chunk += word + " "
                if i % 3 == 0:  # Send every 3 words
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk.strip()})}\n\n"
                    chunk = ""
                    await asyncio.sleep(0.1)
            
            if chunk:  # Send remaining words
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk.strip()})}\n\n"
            
            # Send completion
            yield f"data: {json.dumps({'type': 'complete', 'suggested_actions': ['start_investigation', 'learn_more']})}\n\n"
            
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': 'Erro ao processar mensagem'})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"
        }
    )

@router.get("/suggestions")
async def get_suggestions() -> List[QuickAction]:
    """
    Get quick action suggestions for the chat
    """
    return [
        QuickAction(
            id="investigate",
            label="Investigar contratos",
            icon="search",
            action="Quero investigar contratos do Ministério da Saúde"
        ),
        QuickAction(
            id="anomalies",
            label="Ver anomalias recentes",
            icon="alert-circle",
            action="Mostre as principais anomalias detectadas"
        ),
        QuickAction(
            id="report",
            label="Gerar relatório",
            icon="file-text",
            action="Gere um relatório das últimas investigações"
        ),
        QuickAction(
            id="help",
            label="Como funciona?",
            icon="help-circle",
            action="Como o Cidadão.AI funciona?"
        )
    ]

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    current_user = Depends(get_current_optional_user)
) -> Dict[str, Any]:
    """
    Get chat history for a session
    """
    session = await chat_service.get_session(session_id)
    
    # Verify user has access to this session
    if session.user_id and current_user and session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    messages = await chat_service.get_session_messages(session_id, limit)
    
    return {
        "session_id": session_id,
        "messages": messages,
        "total_messages": len(messages),
        "current_investigation_id": session.current_investigation_id
    }

@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    current_user = Depends(get_current_optional_user)
) -> Dict[str, str]:
    """
    Clear chat history for a session
    """
    session = await chat_service.get_session(session_id)
    
    # Verify user has access
    if session.user_id and current_user and session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    await chat_service.clear_session(session_id)
    
    return {"message": "Histórico limpo com sucesso"}

@router.get("/agents")
async def get_available_agents() -> List[Dict[str, Any]]:
    """
    Get list of available agents for chat
    """
    return [
        {
            "id": "abaporu",
            "name": "Abaporu",
            "avatar": "🎨",
            "role": "Orquestrador Master",
            "description": "Coordena investigações complexas",
            "status": "active"
        },
        {
            "id": "zumbi",
            "name": "Zumbi dos Palmares",
            "avatar": "🔍",
            "role": "Investigador",
            "description": "Detecta anomalias e irregularidades",
            "status": "active"
        },
        {
            "id": "anita",
            "name": "Anita Garibaldi", 
            "avatar": "📊",
            "role": "Analista",
            "description": "Analisa padrões e tendências",
            "status": "active"
        },
        {
            "id": "tiradentes",
            "name": "Tiradentes",
            "avatar": "📝",
            "role": "Relator",
            "description": "Gera relatórios detalhados",
            "status": "active"
        },
        {
            "id": "machado",
            "name": "Machado de Assis",
            "avatar": "📚",
            "role": "Analista Textual",
            "description": "Analisa documentos e contratos",
            "status": "active"
        },
        {
            "id": "dandara",
            "name": "Dandara",
            "avatar": "⚖️",
            "role": "Justiça Social",
            "description": "Avalia equidade e inclusão",
            "status": "active"
        }
    ]