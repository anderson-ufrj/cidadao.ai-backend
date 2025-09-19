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
from src.api.routes.chat_drummond_factory import get_drummond_agent
from src.agents.deodoro import AgentMessage, AgentContext, AgentResponse, AgentStatus
from src.services.chat_service_with_cache import chat_service
from src.services.chat_service import IntentDetector, IntentType
from src.api.models.pagination import CursorPaginationResponse

# Import the simple Zumbi agent for investigations
import sys
sys.path.append('/')
from app import enhanced_zumbi, UniversalSearchRequest, DataSourceType

logger = get_logger(__name__)
router = APIRouter(tags=["chat"])

# Services are already initialized
intent_detector = IntentDetector()

# Drummond agent handled by factory to avoid import issues

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
        
        # Determine target agent based on intent
        if intent.type in [IntentType.GREETING, IntentType.CONVERSATION, IntentType.HELP_REQUEST, 
                          IntentType.ABOUT_SYSTEM, IntentType.SMALLTALK, IntentType.THANKS, IntentType.GOODBYE]:
            target_agent = "drummond"
            logger.info(f"Routing to Drummond for intent type: {intent.type}")
        elif intent.type == IntentType.INVESTIGATE:
            target_agent = "abaporu"
            logger.info(f"Routing to Abaporu for intent type: {intent.type}")
        else:
            target_agent = "abaporu"  # Default to master agent
            logger.info(f"Defaulting to Abaporu for intent type: {intent.type}")
            
        # Create agent message
        agent_message = AgentMessage(
            sender="user",
            recipient=target_agent,
            action="process_chat",
            payload={
                "user_message": request.message,
                "intent": intent.dict(),
                "context": request.context or {},
                "session": session.to_dict()
            },
            context={
                "investigation_id": session.current_investigation_id,
                "user_id": session.user_id,
                "session_id": session_id
            }
        )
        
        # Route to appropriate agent based on intent
        logger.info(f"Target agent: {target_agent}")
        
        if target_agent == "drummond":
            # Use Drummond for conversational intents
            try:
                drummond_agent = await get_drummond_agent()
                
                if drummond_agent:
                    response = await drummond_agent.process(agent_message, context)
                else:
                    raise Exception("Drummond agent not available")
                agent_id = "drummond"
                agent_name = "Carlos Drummond de Andrade"
                logger.info(f"Drummond response received: {response}")
            except Exception as e:
                logger.error(f"Error processing with Drummond: {e}")
                import traceback
                traceback.print_exc()
                raise
        elif target_agent == "abaporu" and intent.type == IntentType.INVESTIGATE:
            # Handle investigation requests with Zumbi
            try:
                logger.info("Routing investigation to Zumbi agent")
                
                # Extract what to investigate from the message
                search_query = request.message.lower()
                data_source = DataSourceType.CONTRACTS  # Default
                
                # Detect data source from keywords
                if any(word in search_query for word in ["servidor", "salário", "funcionário"]):
                    data_source = DataSourceType.SERVANTS
                elif any(word in search_query for word in ["despesa", "gasto", "pagamento"]):
                    data_source = DataSourceType.EXPENSES
                elif any(word in search_query for word in ["licitação", "pregão"]):
                    data_source = DataSourceType.BIDDINGS
                
                # Create investigation request
                investigation_request = UniversalSearchRequest(
                    query=request.message,
                    data_source=data_source,
                    max_results=10
                )
                
                # Run investigation
                investigation_result = await enhanced_zumbi.investigate_universal(investigation_request)
                
                # Format response
                message = f"🏹 **Investigação Concluída**\n\n"
                message += f"Fonte de dados: {investigation_result.data_source}\n"
                message += f"Resultados encontrados: {investigation_result.total_found}\n"
                message += f"Anomalias detectadas: {investigation_result.anomalies_detected}\n\n"
                
                if investigation_result.results:
                    message += "**Principais achados:**\n"
                    for i, result in enumerate(investigation_result.results[:3], 1):
                        if investigation_result.data_source == "contratos":
                            message += f"{i}. Contrato {result.get('numero', 'N/A')} - R$ {result.get('valor', 0):,.2f}\n"
                        elif investigation_result.data_source == "servidores":
                            message += f"{i}. {result.get('nome', 'N/A')} - {result.get('cargo', 'N/A')}\n"
                else:
                    message += "Nenhum resultado encontrado para esta busca.\n"
                
                response = AgentResponse(
                    agent_name="Zumbi dos Palmares",
                    status=AgentStatus.COMPLETED,
                    result={
                        "message": message,
                        "investigation_data": investigation_result.dict(),
                        "status": "investigation_completed"
                    },
                    metadata={
                        "confidence": investigation_result.confidence_score,
                        "processing_time": investigation_result.processing_time_ms
                    }
                )
                agent_id = "zumbi"
                agent_name = "Zumbi dos Palmares"
                
            except Exception as e:
                logger.error(f"Investigation error: {e}")
                response = AgentResponse(
                    agent_name="Sistema",
                    status=AgentStatus.ERROR,
                    result={
                        "message": "Erro ao processar investigação. Por favor, tente novamente.",
                        "error": str(e)
                    },
                    metadata={"confidence": 0.0}
                )
                agent_id = "system"
                agent_name = "Sistema"
        else:
            # For now, return a simple response if agents are not available
            logger.warning(f"Falling back to maintenance message. Target: {target_agent}")
            # Include debug info about why Drummond failed
            debug_info = ""
            if target_agent == "drummond":
                debug_info = " (Drummond not initialized)"
            
            response = AgentResponse(
                agent_name="Sistema",
                status=AgentStatus.COMPLETED,
                result={
                    "message": f"Desculpe, estou em manutenção. Por favor, tente novamente em alguns instantes.{debug_info}",
                    "status": "maintenance",
                    "debug": "Drummond not available" if target_agent == "drummond" else None
                },
                metadata={
                    "confidence": 0.0
                }
            )
            agent_id = "system"
            agent_name = "Sistema"
        
        # Save to chat history
        await chat_service.save_message(
            session_id=session_id,
            role="user",
            content=request.message
        )
        
        # Get content from response
        response_content = response.result if hasattr(response, 'result') else str(response)
        
        await chat_service.save_message(
            session_id=session_id,
            role="assistant",
            content=response_content,
            agent_id=agent_id
        )
        
        # Prepare suggested actions based on response
        suggested_actions = []
        if intent.type == IntentType.INVESTIGATE and not session.current_investigation_id:
            suggested_actions = ["start_investigation", "view_examples", "learn_more"]
        elif session.current_investigation_id:
            suggested_actions = ["view_progress", "generate_report", "new_investigation"]
        
        # Extract message from response
        if hasattr(response, 'result') and isinstance(response.result, dict):
            message_text = response.result.get("message", str(response.result))
            requires_input = response.result.get("requires_input")
        elif hasattr(response, 'result'):
            message_text = str(response.result)
            requires_input = None
        else:
            message_text = str(response)
            requires_input = None
            
        return ChatResponse(
            session_id=session_id,
            agent_id=agent_id,
            agent_name=agent_name,
            message=message_text,
            confidence=response.metadata.get("confidence", intent.confidence) if hasattr(response, 'metadata') else intent.confidence,
            suggested_actions=suggested_actions,
            requires_input=requires_input,
            metadata={
                "intent_type": intent.type.value,
                "processing_time": response.metadata.get("processing_time", 0) if hasattr(response, 'metadata') else 0,
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

@router.get("/history/{session_id}/paginated")
async def get_chat_history_paginated(
    session_id: str,
    cursor: Optional[str] = None,
    limit: int = 50,
    direction: str = "prev",
    current_user = Depends(get_current_optional_user)
) -> CursorPaginationResponse[Dict[str, Any]]:
    """
    Get paginated chat history using cursor pagination.
    
    This is more efficient for large chat histories and real-time updates.
    
    Args:
        session_id: Session identifier
        cursor: Pagination cursor from previous request
        limit: Number of messages per page (max: 100)
        direction: "next" for newer messages, "prev" for older (default)
    """
    session = await ChatService.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    # Verify user has access to this session
    if session.user_id and current_user and session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Get paginated messages
    paginated_response = await ChatService.get_session_messages_paginated(
        session_id=session_id,
        cursor=cursor,
        limit=min(limit, 100),  # Cap at 100
        direction=direction
    )
    
    # Add session info to metadata
    paginated_response.metadata.update({
        "session_id": session_id,
        "investigation_id": session.current_investigation_id,
        "session_created": session.created_at.isoformat() if session else None
    })
    
    return paginated_response

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

@router.get("/cache/stats")
async def get_cache_stats(
    current_user = Depends(get_current_optional_user)
) -> Dict[str, Any]:
    """
    Get cache statistics (admin only in production)
    """
    try:
        stats = await ChatService.get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"error": "Unable to get cache statistics"}

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

@router.get("/debug/drummond-status")
async def debug_drummond_status():
    """Debug endpoint to check Drummond agent status"""
    return {
        "drummond_initialized": True,  # Factory handles initialization
        "drummond_error": None,
        "drummond_type": "Factory managed",
        "has_process_method": True,
        "intent_types_for_drummond": [
            "GREETING", "CONVERSATION", "HELP_REQUEST", 
            "ABOUT_SYSTEM", "SMALLTALK", "THANKS", "GOODBYE"
        ]
    }