"""
Enhanced chat service with Redis caching integration
"""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from src.api.models.pagination import ChatMessagePagination, CursorPaginationResponse
from src.core import get_logger
from src.core.config import get_settings
from src.services.cache_service import cache_service
from src.services.chat_service import ChatService, Intent, IntentDetector

logger = get_logger(__name__)


class CachedChatService(ChatService):
    """Chat service with Redis caching for improved performance"""

    def __init__(self):
        super().__init__()
        self.intent_detector = IntentDetector()

    async def process_message(
        self,
        message: str,
        session_id: str,
        user_id: str | None = None,
        context: dict[str, Any] | None = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        """
        Process a chat message with caching support.

        Args:
            message: User message
            session_id: Session identifier
            user_id: Optional user ID
            context: Optional context
            stream: Whether to stream response

        Returns:
            Chat response dictionary
        """
        # Get or create session
        session = await self.get_or_create_session(session_id, user_id)

        # Save user message
        await self.save_message(session_id, "user", message)

        # Detect intent
        intent = self.intent_detector.detect(message)

        # Check cache for common responses (only for non-streaming)
        if not stream and intent.confidence > 0.8:
            cached_response = await cache_service.get_cached_chat_response(
                message, intent.type.value
            )

            if cached_response:
                logger.info(f"Returning cached response for: {message[:50]}...")
                # Save cached response to history
                await self.save_message(
                    session_id,
                    "assistant",
                    cached_response.get("message", ""),
                    cached_response.get("agent_id"),
                )
                return cached_response

        # Get appropriate agent
        agent = await self.get_agent_for_intent(intent)

        try:
            # Process with agent
            if stream:
                # For streaming, return async generator
                return self._stream_agent_response(
                    agent, message, intent, session, session_id
                )
            # Regular response
            response = await self._get_agent_response(agent, message, intent, session)

            # Save agent response
            await self.save_message(
                session_id, "assistant", response["message"], response["agent_id"]
            )

            # Cache successful responses with high confidence
            if intent.confidence > 0.8 and response.get("confidence", 0) > 0.7:
                await cache_service.cache_chat_response(
                    message, response, intent.type.value
                )

            # Update session with any investigation ID
            if "investigation_id" in response:
                await self.update_session_investigation(
                    session_id, response["investigation_id"]
                )

            # Save session state to cache
            await cache_service.save_session_state(
                session_id,
                {
                    "last_message": message,
                    "last_intent": intent.dict(),
                    "last_agent": response["agent_id"],
                    "investigation_id": session.current_investigation_id,
                    "message_count": session.message_count or 0,
                },
            )

            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_response = {
                "session_id": session_id,
                "agent_id": "system",
                "agent_name": "Sistema",
                "message": "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.",
                "confidence": 0.0,
                "error": True,
            }

            await self.save_message(
                session_id, "assistant", error_response["message"], "system"
            )

            return error_response

    async def _get_agent_response(
        self, agent, message: str, intent: Intent, session
    ) -> dict[str, Any]:
        """Get response from agent"""
        # Create agent context
        context = {
            "session_id": session.id,
            "intent": intent.dict(),
            "entities": intent.entities,
            "investigation_id": session.current_investigation_id,
            "history": await self.get_session_messages(session.id, limit=10),
        }

        # Check agent context cache
        cached_context = await cache_service.get_agent_context(
            agent.agent_id, session.id
        )

        if cached_context:
            context.update(cached_context)

        # Execute agent
        result = await agent.execute({"message": message, "context": context})

        # Save agent context for future use
        if result.get("context_update"):
            await cache_service.save_agent_context(
                agent.agent_id, session.id, result["context_update"]
            )

        # Format response
        return {
            "session_id": session.id,
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "message": result.get("response", ""),
            "confidence": result.get("confidence", 0.5),
            "suggested_actions": result.get("suggested_actions", []),
            "requires_input": result.get("requires_input"),
            "metadata": {
                "intent_type": intent.type.value,
                "processing_time": result.get("processing_time", 0),
                "is_demo_mode": not bool(get_settings().transparency_api_key),
                "timestamp": session.last_activity.isoformat(),
            },
        }

    async def _stream_agent_response(
        self, agent, message: str, intent: Intent, session, session_id: str
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream response from agent"""
        # Initial chunks
        yield {"type": "start", "timestamp": session.last_activity.isoformat()}

        yield {"type": "detecting", "message": "Analisando sua mensagem..."}

        yield {
            "type": "intent",
            "intent": intent.type.value,
            "confidence": intent.confidence,
        }

        yield {
            "type": "agent_selected",
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
        }

        # Simulate streaming response
        # In production, this would stream from the LLM
        response = await self._get_agent_response(agent, message, intent, session)

        # Stream response in chunks
        message_text = response["message"]
        words = message_text.split()

        for i in range(0, len(words), 3):
            chunk = " ".join(words[i : i + 3])
            yield {"type": "chunk", "content": chunk + " "}
            await asyncio.sleep(0.05)  # Simulate typing

        # Save complete message
        await self.save_message(
            session_id, "assistant", message_text, response["agent_id"]
        )

        # Final completion
        yield {
            "type": "complete",
            "suggested_actions": response.get("suggested_actions", []),
        }

    async def restore_session_from_cache(
        self, session_id: str
    ) -> dict[str, Any] | None:
        """Restore session state from cache"""
        cached_state = await cache_service.get_session_state(session_id)

        if cached_state:
            # Restore session
            session = await self.get_or_create_session(session_id)

            if cached_state.get("investigation_id"):
                session.current_investigation_id = cached_state["investigation_id"]

            logger.info(f"Restored session {session_id} from cache")
            return cached_state

        return None

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics for monitoring"""
        return await cache_service.get_cache_stats()

    async def get_session_messages_paginated(
        self,
        session_id: str,
        cursor: str | None = None,
        limit: int = 50,
        direction: str = "prev",
    ) -> CursorPaginationResponse[dict[str, Any]]:
        """
        Get paginated messages for a session using cursor pagination.

        Args:
            session_id: Session identifier
            cursor: Pagination cursor
            limit: Number of messages per page
            direction: "next" or "prev" (default: "prev" for chat)

        Returns:
            Paginated response with messages and cursors
        """
        # Get all messages from DB
        messages = await self.get_session_messages(session_id, limit=10000)

        # Add unique IDs if missing
        for i, msg in enumerate(messages):
            if "id" not in msg:
                msg["id"] = f"{session_id}-{i}"

        # Paginate using cursor
        return ChatMessagePagination.paginate_messages(
            messages=messages, cursor=cursor, limit=limit, direction=direction
        )


# Export the enhanced service
# Use lazy initialization to avoid import-time errors
_chat_service_instance = None


def get_chat_service():
    """Get or create the chat service instance"""
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = CachedChatService()
    return _chat_service_instance


# For backward compatibility
chat_service = None  # Will be replaced by getter
