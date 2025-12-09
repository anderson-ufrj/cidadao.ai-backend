"""
Module: agents.base_kids_agent
Description: Base class for all kids educational agents with shared safety features
Author: Anderson H. Silva
Date: 2025-12-09
License: Proprietary - All rights reserved

This module provides:
- Centralized content safety filtering (BLOCKED_TOPICS)
- Shared safe redirect behavior
- Common initialization patterns
- DSPy service integration

All kids agents (Monteiro Lobato, Tarsila, etc.) should inherit from BaseKidsAgent
to ensure consistent safety behavior and avoid code drift.
"""

from abc import abstractmethod
from typing import Any

from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
    BaseAgent,
)
from src.core import get_logger

# Import DSPy service for intelligent responses
try:
    from src.services.dspy_agents import get_dspy_agent_service

    _dspy_service = get_dspy_agent_service()
    _DSPY_AVAILABLE = _dspy_service.is_available() if _dspy_service else False
except ImportError:
    _dspy_service = None
    _DSPY_AVAILABLE = False


# =============================================================================
# BLOCKED TOPICS - SINGLE SOURCE OF TRUTH FOR ALL KIDS AGENTS
# =============================================================================
# WARNING: Any changes here affect ALL kids agents. Review carefully!
# =============================================================================
BLOCKED_TOPICS: list[str] = [
    # Violence
    "violencia",
    "violence",
    "matar",
    "kill",
    "morte",
    "death",
    "arma",
    "weapon",
    "gun",
    "guerra",
    "war",
    "sangue",
    "blood",
    "briga",
    "fight",
    "lutar",
    # Adult content
    "sexo",
    "sex",
    "pornografia",
    "adulto",
    "adult",
    "namorar",
    "beijar",
    # Drugs and substances
    "droga",
    "drug",
    "alcool",
    "alcohol",
    "cerveja",
    "beer",
    "cigarro",
    "cigarette",
    "fumar",
    "smoke",
    # Dangerous activities
    "hackear",
    "hack",
    "invadir",
    "roubar",
    "steal",
    "crime",
    "ilegal",
    "illegal",
    # Scary content
    "terror",
    "horror",
    "medo",
    "fear",
    "assustador",
    "scary",
    "pesadelo",
    "nightmare",
    "monstro",
    "monster",
    # Hate speech
    "odio",
    "hate",
    "racismo",
    "racism",
    "preconceito",
    "bullying",
    # Personal information (phishing protection)
    "senha",
    "password",
    "cartao",
    "card",
    "banco",
    "bank",
    "dinheiro",
    "money",
    # Politics and controversy
    "politica",
    "politics",
    "eleicao",
    "election",
    "presidente",
]


class BaseKidsAgent(BaseAgent):
    """
    Base class for all kids educational agents.

    Provides centralized safety features:
    - Content safety filtering via BLOCKED_TOPICS
    - Topic validation via allowed_topics (defined by subclass)
    - Safe redirect responses when content is inappropriate
    - DSPy service integration for intelligent responses

    Subclasses must implement:
    - allowed_topics: list[str] - Topics this agent can discuss
    - personality_prompt: str - Agent's personality for LLM
    - _get_safe_redirect_response() - Response when redirecting
    - _get_fallback_response(message) - Domain-specific fallbacks

    Example:
        class MyKidsAgent(BaseKidsAgent):
            allowed_topics = ["math", "numbers", "counting"]
            personality_prompt = "You are a friendly math teacher..."

            def _get_safe_redirect_response(self) -> str:
                return "Let's talk about numbers instead!"

            def _get_fallback_response(self, message: str) -> str:
                return "I can help you with math!"
    """

    # Subclasses must define these
    allowed_topics: list[str] = []
    personality_prompt: str = ""

    def __init__(
        self,
        name: str,
        description: str,
        capabilities: list[str],
        max_retries: int = 3,
        timeout: int = 60,
        config: dict[str, Any] | None = None,
    ):
        """
        Initialize the kids agent.

        Args:
            name: Agent identifier (e.g., "monteiro_lobato")
            description: Human-readable description
            capabilities: List of agent capabilities
            max_retries: Max retry attempts for operations
            timeout: Timeout in seconds
            config: Optional configuration dictionary
        """
        super().__init__(
            name=name,
            description=description,
            capabilities=capabilities,
            max_retries=max_retries,
            timeout=timeout,
        )
        self.logger = get_logger(__name__)
        self.config = config or {}

        self.logger.info(
            "kids_agent_initialized",
            agent_name=self.name,
            dspy_available=_DSPY_AVAILABLE,
            blocked_topics_count=len(BLOCKED_TOPICS),
            allowed_topics_count=len(self.allowed_topics),
        )

    async def initialize(self) -> None:
        """Initialize agent resources."""
        self.logger.info(f"{self.name} agent initialized")

    async def shutdown(self) -> None:
        """Cleanup agent resources."""
        self.logger.info(f"{self.name} agent shutting down")

    def is_content_safe(self, text: str) -> tuple[bool, str]:
        """
        Check if content is safe for kids.

        This is the SINGLE SOURCE OF TRUTH for content safety across all kids agents.

        Args:
            text: Text to check

        Returns:
            Tuple of (is_safe, reason)
        """
        text_lower = text.lower()

        for blocked in BLOCKED_TOPICS:
            if blocked in text_lower:
                return False, f"Blocked topic detected: {blocked}"

        return True, "Content is safe"

    def is_topic_allowed(self, text: str) -> bool:
        """
        Check if topic is within this agent's allowed scope.

        Args:
            text: Text to check

        Returns:
            True if topic is allowed for this agent
        """
        text_lower = text.lower()

        # Check if any allowed topic is mentioned
        for allowed in self.allowed_topics:
            if allowed in text_lower:
                return True

        # Allow general questions (curiosity is always welcome!)
        general_patterns = [
            "o que",
            "como",
            "porque",
            "por que",
            "quando",
            "onde",
            "quem",
            "qual",
            "?",
            "ola",
            "oi",
            "bom dia",
            "boa tarde",
            "boa noite",
        ]
        for pattern in general_patterns:
            if pattern in text_lower:
                return True

        return False

    @abstractmethod
    def _get_safe_redirect_response(self) -> str:
        """
        Get a safe redirect response when content is not appropriate.

        Subclasses must implement this with domain-specific redirect message.

        Returns:
            Safe redirect message that guides child back to appropriate topics
        """
        pass

    @abstractmethod
    def _get_fallback_response(self, message: str) -> str:
        """
        Get a domain-specific fallback response.

        Subclasses must implement this with responses for common topics.

        Args:
            message: User message to respond to

        Returns:
            Appropriate fallback response
        """
        pass

    async def _generate_response(self, message: str, context: AgentContext) -> str:
        """
        Generate a safe, educational response for kids.

        This method implements the safety pipeline:
        1. Check content safety (blocked topics)
        2. Check topic relevance (allowed topics)
        3. Try DSPy for intelligent response
        4. Fall back to predefined responses

        Args:
            message: User message
            context: Agent context

        Returns:
            Safe response string
        """
        # Step 1: Check content safety
        is_safe, reason = self.is_content_safe(message)
        if not is_safe:
            self.logger.warning(
                "unsafe_content_detected",
                reason=reason,
                agent_name=self.name,
                investigation_id=context.investigation_id,
            )
            return self._get_safe_redirect_response()

        # Step 2: Check if topic is within allowed scope
        if not self.is_topic_allowed(message):
            self.logger.info(
                "topic_redirect",
                message=message[:50],
                agent_name=self.name,
                investigation_id=context.investigation_id,
            )
            return self._get_safe_redirect_response()

        # Step 3: Try DSPy service if available
        if _DSPY_AVAILABLE and _dspy_service and self.personality_prompt:
            try:
                response = await _dspy_service.generate_response(
                    agent_name=self.name,
                    personality_prompt=self.personality_prompt,
                    user_message=message,
                    context={
                        "target_audience": "children_6_12",
                        "style": "fun_educational",
                        "max_words": 150,
                    },
                )
                if response:
                    # Double-check the generated response is safe
                    is_safe, _ = self.is_content_safe(response)
                    if is_safe:
                        return response
            except Exception as e:
                self.logger.warning(f"DSPy generation failed for {self.name}: {e}")

        # Step 4: Fallback to predefined responses
        return self._get_fallback_response(message)

    async def process(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        """
        Process a message from a kid and return an educational response.

        Args:
            message: Message to process
            context: Agent context

        Returns:
            AgentResponse with educational content
        """
        try:
            self.logger.info(
                "kids_message_received",
                investigation_id=context.investigation_id,
                agent_name=self.name,
                action=message.action,
            )

            # Extract user message from payload
            user_message = ""
            if isinstance(message.payload, dict):
                user_message = message.payload.get(
                    "message", message.payload.get("query", "")
                )
            elif isinstance(message.payload, str):
                user_message = message.payload

            if not user_message:
                user_message = "ola"

            # Generate safe, educational response
            response_text = await self._generate_response(user_message, context)

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result={
                    "response": response_text,
                    "message": response_text,  # Alias for compatibility
                    "agent": self.name,
                    "safe_content": True,
                },
                metadata={
                    "agent_type": "kids_educational",
                    "content_filtered": True,
                    "dspy_used": _DSPY_AVAILABLE,
                },
            )

        except Exception as e:
            self.logger.error(
                "kids_agent_error",
                error=str(e),
                agent_name=self.name,
                investigation_id=context.investigation_id,
            )
            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.ERROR,
                result={"error": str(e)},
                metadata={"error_type": type(e).__name__},
            )
