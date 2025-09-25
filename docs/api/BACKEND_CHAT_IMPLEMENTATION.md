# 🤖 Implementações Necessárias no Backend para Chat e Mobile

## 1. 💬 Endpoint de Chat Conversacional

### Novo Endpoint: `/api/v1/chat`

```python
# src/api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import json

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    agent_id: str
    agent_name: str
    message: str
    metadata: Dict[str, Any]
    suggested_actions: Optional[List[str]] = None
    requires_input: Optional[Dict[str, str]] = None

@router.post("/message")
async def chat_message(
    request: ChatMessage,
    current_user: User = Depends(get_current_user)
) -> ChatResponse:
    """
    Processa mensagem do chat e retorna resposta do agente apropriado
    """
    # Detectar intenção
    intent = await detect_intent(request.message)
    
    # Selecionar agente baseado na intenção
    agent = await select_agent_for_intent(intent)
    
    # Manter contexto da sessão
    session = await get_or_create_session(request.session_id)
    
    # Processar com o agente
    response = await agent.process_chat(
        message=request.message,
        context={
            **request.context,
            "session": session,
            "intent": intent
        }
    )
    
    # Salvar no histórico
    await save_chat_history(session.id, request, response)
    
    return ChatResponse(
        agent_id=agent.agent_id,
        agent_name=agent.name,
        message=response.content,
        metadata={
            "confidence": response.confidence,
            "processing_time": response.processing_time
        },
        suggested_actions=response.suggested_actions,
        requires_input=response.requires_input
    )

@router.post("/stream")
async def chat_stream(request: ChatMessage):
    """
    Streaming de respostas para experiência mais fluida
    """
    async def generate():
        # Header do SSE
        yield f"data: {json.dumps({'type': 'start', 'agent': 'detecting'})}\n\n"
        
        # Detectar intenção
        intent = await detect_intent(request.message)
        yield f"data: {json.dumps({'type': 'intent', 'intent': intent.type})}\n\n"
        
        # Selecionar agente
        agent = await select_agent_for_intent(intent)
        yield f"data: {json.dumps({'type': 'agent', 'agent_id': agent.agent_id, 'agent_name': agent.name})}\n\n"
        
        # Processar em chunks
        async for chunk in agent.process_chat_stream(request.message):
            yield f"data: {json.dumps({'type': 'message', 'content': chunk})}\n\n"
            await asyncio.sleep(0.1)  # Simula digitação
        
        # Finalizar
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

## 2. 🧠 Sistema de Detecção de Intenção

```python
# src/services/intent_detection.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
import re

class IntentType(Enum):
    INVESTIGATE = "investigate"
    ANALYZE = "analyze"
    REPORT = "report"
    QUESTION = "question"
    HELP = "help"
    GREETING = "greeting"

@dataclass
class Intent:
    type: IntentType
    entities: Dict[str, Any]
    confidence: float
    suggested_agent: str

class IntentDetector:
    """Detecta intenção do usuário para roteamento correto"""
    
    def __init__(self):
        self.patterns = {
            IntentType.INVESTIGATE: [
                r"investigar?\s+(\w+)",
                r"analis[ae]r?\s+contratos",
                r"verificar?\s+gastos",
                r"procurar?\s+irregularidades"
            ],
            IntentType.ANALYZE: [
                r"anomalias?\s+em",
                r"padr[õo]es?\s+suspeitos",
                r"gastos?\s+excessivos",
                r"fornecedores?\s+concentrados"
            ],
            IntentType.REPORT: [
                r"gerar?\s+relat[óo]rio",
                r"documento\s+sobre",
                r"resumo\s+de",
                r"exportar?\s+dados"
            ]
        }
    
    async def detect(self, message: str) -> Intent:
        message_lower = message.lower()
        
        # Detectar órgãos mencionados
        organs = self._extract_organs(message_lower)
        
        # Detectar período
        period = self._extract_period(message_lower)
        
        # Detectar tipo de intenção
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return Intent(
                        type=intent_type,
                        entities={
                            "organs": organs,
                            "period": period,
                            "original_message": message
                        },
                        confidence=0.85,
                        suggested_agent=self._get_agent_for_intent(intent_type)
                    )
        
        # Fallback
        return Intent(
            type=IntentType.HELP,
            entities={"original_message": message},
            confidence=0.5,
            suggested_agent="abaporu"
        )
    
    def _extract_organs(self, text: str) -> List[str]:
        """Extrai menções a órgãos governamentais"""
        organ_map = {
            "saúde": "26000",
            "educação": "25000",
            "presidência": "20000",
            "justiça": "30000",
            "agricultura": "22000"
        }
        
        found = []
        for name, code in organ_map.items():
            if name in text:
                found.append({"name": name, "code": code})
        
        return found
    
    def _get_agent_for_intent(self, intent_type: IntentType) -> str:
        """Retorna o agente mais apropriado para a intenção"""
        mapping = {
            IntentType.INVESTIGATE: "zumbi",
            IntentType.ANALYZE: "anita",
            IntentType.REPORT: "tiradentes",
            IntentType.QUESTION: "machado",
            IntentType.HELP: "abaporu",
            IntentType.GREETING: "abaporu"
        }
        return mapping.get(intent_type, "abaporu")
```

## 3. 📱 Otimizações para Mobile

### Compressão e Paginação

```python
# src/api/middleware/mobile_optimization.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import gzip
import json

class MobileOptimizationMiddleware(BaseHTTPMiddleware):
    """Otimizações específicas para mobile"""
    
    async def dispatch(self, request: Request, call_next):
        # Detectar cliente mobile
        user_agent = request.headers.get("user-agent", "").lower()
        is_mobile = any(x in user_agent for x in ["mobile", "android", "iphone"])
        
        # Adicionar header para indicar mobile
        request.state.is_mobile = is_mobile
        
        response = await call_next(request)
        
        # Compressão para mobile
        if is_mobile and response.headers.get("content-type", "").startswith("application/json"):
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Comprimir resposta
            compressed = gzip.compress(body)
            
            # Se vale a pena comprimir
            if len(compressed) < len(body) * 0.9:
                response.headers["content-encoding"] = "gzip"
                response.headers["vary"] = "Accept-Encoding"
                return Response(
                    content=compressed,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
        
        return response
```

### Paginação Otimizada

```python
# src/api/utils/pagination.py
from typing import Optional, List, Any
from pydantic import BaseModel

class MobilePagination(BaseModel):
    """Paginação otimizada para scroll infinito mobile"""
    items: List[Any]
    next_cursor: Optional[str] = None
    has_more: bool = False
    total_count: Optional[int] = None

async def paginate_for_mobile(
    query,
    cursor: Optional[str] = None,
    limit: int = 20
) -> MobilePagination:
    """
    Paginação baseada em cursor para performance mobile
    """
    # Decodificar cursor
    offset = 0
    if cursor:
        offset = int(cursor)
    
    # Buscar items + 1 para saber se há mais
    items = await query.offset(offset).limit(limit + 1).all()
    
    has_more = len(items) > limit
    if has_more:
        items = items[:-1]
    
    next_cursor = str(offset + limit) if has_more else None
    
    return MobilePagination(
        items=items,
        next_cursor=next_cursor,
        has_more=has_more
    )
```

## 4. 💾 Cache para Modo Offline

```python
# src/api/utils/offline_cache.py
from datetime import datetime, timedelta
import hashlib
import json

class OfflineCache:
    """Cache agressivo para suporte offline"""
    
    def __init__(self):
        self.cache_durations = {
            "investigations": timedelta(hours=24),
            "reports": timedelta(days=7),
            "static_data": timedelta(days=30),
            "chat_history": timedelta(days=1)
        }
    
    async def cache_for_offline(self, key: str, data: Any, category: str):
        """Salva dados para acesso offline"""
        cache_key = self._generate_cache_key(key, category)
        
        cache_data = {
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "expires_at": (
                datetime.now() + self.cache_durations.get(category, timedelta(hours=1))
            ).isoformat()
        }
        
        # Salvar no Redis com TTL apropriado
        await redis_client.setex(
            cache_key,
            self.cache_durations.get(category, timedelta(hours=1)),
            json.dumps(cache_data)
        )
        
        # Headers para cache do navegador
        return {
            "Cache-Control": f"max-age={self.cache_durations.get(category).total_seconds()}",
            "ETag": hashlib.md5(json.dumps(data).encode()).hexdigest(),
            "X-Cache-Category": category
        }
```

## 5. 🔄 WebSocket para Chat em Tempo Real

```python
# src/api/websocket/chat_ws.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        self.active_connections.pop(session_id, None)
    
    async def send_message(self, session_id: str, message: dict):
        websocket = self.active_connections.get(session_id)
        if websocket:
            await websocket.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receber mensagem
            data = await websocket.receive_json()
            
            # Processar com agente
            response = await process_chat_message(data)
            
            # Enviar resposta em chunks para simular digitação
            for chunk in response.split_into_chunks():
                await manager.send_message(session_id, {
                    "type": "chunk",
                    "content": chunk,
                    "agent": response.agent_id
                })
                await asyncio.sleep(0.05)
            
            # Mensagem completa
            await manager.send_message(session_id, {
                "type": "complete",
                "suggested_actions": response.suggested_actions
            })
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)
```

## 6. 🎯 Endpoints Otimizados para Mobile

```python
# src/api/routes/mobile.py
@router.get("/mobile/quick-stats")
async def get_quick_stats(
    current_user: User = Depends(get_optional_user)
) -> Dict[str, Any]:
    """Estatísticas rápidas para home do app"""
    
    # Cache agressivo para mobile
    cached = await cache.get("mobile_quick_stats")
    if cached:
        return cached
    
    stats = {
        "total_investigations": await get_total_investigations(),
        "anomalies_found": await get_total_anomalies(),
        "money_at_risk": await get_money_at_risk(),
        "trending_organs": await get_trending_organs(limit=5),
        "recent_alerts": await get_recent_alerts(limit=3),
        "is_demo_mode": current_user is None
    }
    
    await cache.set("mobile_quick_stats", stats, ttl=300)  # 5 min
    return stats

@router.get("/mobile/investigation-summary/{id}")
async def get_investigation_summary_mobile(
    id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Resumo otimizado para mobile com dados essenciais"""
    
    investigation = await get_investigation(id)
    
    # Retornar apenas dados essenciais para mobile
    return {
        "id": investigation.id,
        "status": investigation.status,
        "progress": investigation.progress,
        "risk_level": investigation.risk_level,
        "key_findings": investigation.get_top_findings(3),
        "quick_stats": {
            "anomalies": investigation.anomaly_count,
            "contracts": investigation.contract_count,
            "value_at_risk": investigation.value_at_risk
        },
        "last_update": investigation.updated_at
    }
```

## 7. 🔔 Push Notifications Ready

```python
# src/services/notifications.py
class NotificationService:
    """Preparado para push notifications mobile"""
    
    async def notify_investigation_complete(
        self,
        user_id: str,
        investigation_id: str,
        summary: Dict[str, Any]
    ):
        """Notifica quando investigação completa"""
        
        notification = {
            "title": "Investigação Concluída! 🔍",
            "body": f"Encontramos {summary['anomalies']} anomalias",
            "data": {
                "type": "investigation_complete",
                "investigation_id": investigation_id,
                "risk_level": summary['risk_level']
            },
            "icon": "/icons/icon-192x192.png",
            "badge": "/icons/badge-72x72.png"
        }
        
        # Enviar via FCM/WebPush quando configurado
        await self.send_push_notification(user_id, notification)
```

## 📋 Checklist de Implementação

- [ ] Endpoint `/api/v1/chat/message` para chat
- [ ] Endpoint `/api/v1/chat/stream` para SSE
- [ ] WebSocket `/ws/chat/{session_id}` 
- [ ] Sistema de detecção de intenção
- [ ] Contexto de sessão para chat
- [ ] Compressão automática para mobile
- [ ] Paginação baseada em cursor
- [ ] Cache agressivo para offline
- [ ] Endpoints otimizados `/mobile/*`
- [ ] Headers CORS para Capacitor
- [ ] Rate limiting diferenciado mobile

---

Com essas implementações, o backend estará totalmente preparado para suportar o chatbot conversacional e a experiência mobile/PWA! 🚀