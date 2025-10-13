"""
Module: agents.ayrton_senna
Codinome: Ayrton Senna - Navegador das Rotas Perfeitas
Description: Semantic router for directing queries to appropriate agents with precision and speed
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import re
from typing import Any, Optional

from pydantic import BaseModel
from pydantic import Field as PydanticField

from src.core import AgentStatus
from src.core.exceptions import AgentError, ValidationError

from .deodoro import AgentContext, AgentMessage, AgentResponse, BaseAgent


class RoutingRule(BaseModel):
    """Rule for routing queries to agents."""

    name: str = PydanticField(..., description="Rule name")
    patterns: list[str] = PydanticField(..., description="Regex patterns to match")
    keywords: list[str] = PydanticField(
        default_factory=list, description="Keywords to match"
    )
    target_agent: str = PydanticField(..., description="Target agent name")
    action: str = PydanticField(..., description="Action to perform")
    priority: int = PydanticField(default=5, description="Rule priority (1-10)")
    confidence_threshold: float = PydanticField(
        default=0.7, description="Confidence threshold"
    )
    metadata: dict[str, Any] = PydanticField(
        default_factory=dict, description="Additional metadata"
    )


class RoutingDecision(BaseModel):
    """Result of routing decision."""

    target_agent: str = PydanticField(..., description="Selected agent")
    action: str = PydanticField(..., description="Action to perform")
    confidence: float = PydanticField(..., description="Confidence in decision")
    rule_used: str = PydanticField(..., description="Rule that matched")
    parameters: dict[str, Any] = PydanticField(
        default_factory=dict, description="Parameters for agent"
    )
    fallback_agents: list[str] = PydanticField(
        default_factory=list, description="Fallback agents"
    )


class SemanticRouter(BaseAgent):
    """
    Semantic router that analyzes queries and routes them to appropriate agents.

    The router uses:
    - Rule-based routing with regex patterns and keywords
    - Semantic similarity for complex queries
    - Intent detection for conversational flows
    - Fallback strategies for ambiguous cases
    """

    def __init__(
        self,
        llm_service: Any,
        embedding_service: Optional[Any] = None,
        confidence_threshold: float = 0.7,
        **kwargs: Any,
    ) -> None:
        """
        Initialize semantic router.

        Args:
            llm_service: LLM service for intent detection
            embedding_service: Embedding service for semantic similarity
            confidence_threshold: Minimum confidence for routing decisions
            **kwargs: Additional arguments
        """
        super().__init__(
            name="SemanticRouter",
            description="Routes queries to appropriate agents based on semantic analysis",
            capabilities=[
                "route_query",
                "detect_intent",
                "analyze_query_type",
                "suggest_agents",
                "validate_routing",
            ],
            **kwargs,
        )

        self.llm_service = llm_service
        self.embedding_service = embedding_service
        self.confidence_threshold = confidence_threshold
        self.routing_rules: list[RoutingRule] = []
        self.agent_capabilities: dict[str, list[str]] = {}

        self._initialize_default_rules()

        self.logger.info(
            "semantic_router_initialized",
            confidence_threshold=confidence_threshold,
            rules_count=len(self.routing_rules),
        )

    async def initialize(self) -> None:
        """Initialize semantic router."""
        self.logger.info("semantic_router_initializing")

        # Initialize services
        if hasattr(self.llm_service, "initialize"):
            await self.llm_service.initialize()

        if self.embedding_service and hasattr(self.embedding_service, "initialize"):
            await self.embedding_service.initialize()

        self.status = AgentStatus.IDLE
        self.logger.info("semantic_router_initialized")

    async def shutdown(self) -> None:
        """Shutdown semantic router."""
        self.logger.info("semantic_router_shutting_down")

        if hasattr(self.llm_service, "shutdown"):
            await self.llm_service.shutdown()

        if self.embedding_service and hasattr(self.embedding_service, "shutdown"):
            await self.embedding_service.shutdown()

        self.logger.info("semantic_router_shutdown_complete")

    async def process(
        self,
        message: AgentMessage,
        context: AgentContext,
    ) -> AgentResponse:
        """
        Process routing requests.

        Args:
            message: Message to process
            context: Agent context

        Returns:
            Agent response with routing decision
        """
        action = message.action
        payload = message.payload

        self.logger.info(
            "semantic_router_processing",
            action=action,
            context_id=context.investigation_id,
        )

        try:
            if action == "route_query":
                result = await self._route_query(payload, context)
            elif action == "detect_intent":
                result = await self._detect_intent(payload, context)
            elif action == "analyze_query_type":
                result = await self._analyze_query_type(payload, context)
            elif action == "suggest_agents":
                result = await self._suggest_agents(payload, context)
            elif action == "validate_routing":
                result = await self._validate_routing(payload, context)
            else:
                raise AgentError(
                    f"Unknown action: {action}",
                    details={"action": action, "available_actions": self.capabilities},
                )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result=result,
                metadata={"action": action, "context_id": context.investigation_id},
            )

        except Exception as e:
            self.logger.error(
                "semantic_router_processing_failed",
                action=action,
                error=str(e),
                context_id=context.investigation_id,
            )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.ERROR,
                error=str(e),
                metadata={"action": action, "context_id": context.investigation_id},
            )

    def register_agent_capabilities(
        self,
        agent_name: str,
        capabilities: list[str],
    ) -> None:
        """
        Register agent capabilities for routing decisions.

        Args:
            agent_name: Name of the agent
            capabilities: List of capabilities
        """
        self.agent_capabilities[agent_name] = capabilities
        self.logger.info(
            "agent_capabilities_registered",
            agent_name=agent_name,
            capabilities=capabilities,
        )

    def add_routing_rule(self, rule: RoutingRule) -> None:
        """
        Add a custom routing rule.

        Args:
            rule: Routing rule to add
        """
        self.routing_rules.append(rule)
        # Sort by priority (higher priority first)
        self.routing_rules.sort(key=lambda r: r.priority, reverse=True)

        self.logger.info(
            "routing_rule_added",
            rule_name=rule.name,
            target_agent=rule.target_agent,
            priority=rule.priority,
        )

    async def route_query(
        self,
        query: str,
        context: AgentContext,
        user_preferences: Optional[dict[str, Any]] = None,
    ) -> RoutingDecision:
        """
        Route a query to the most appropriate agent.

        Args:
            query: Query to route
            context: Agent context
            user_preferences: Optional user preferences

        Returns:
            Routing decision
        """
        self.logger.info(
            "routing_query",
            query=query[:100],  # Log first 100 chars
            context_id=context.investigation_id,
        )

        # Step 1: Rule-based routing
        rule_decision = await self._apply_routing_rules(query, context)

        if rule_decision and rule_decision.confidence >= self.confidence_threshold:
            self.logger.info(
                "rule_based_routing_success",
                target_agent=rule_decision.target_agent,
                confidence=rule_decision.confidence,
                rule=rule_decision.rule_used,
            )
            return rule_decision

        # Step 2: Semantic routing using LLM
        semantic_decision = await self._semantic_routing(query, context)

        if (
            semantic_decision
            and semantic_decision.confidence >= self.confidence_threshold
        ):
            self.logger.info(
                "semantic_routing_success",
                target_agent=semantic_decision.target_agent,
                confidence=semantic_decision.confidence,
            )
            return semantic_decision

        # Step 3: Fallback to master agent
        fallback_decision = RoutingDecision(
            target_agent="MasterAgent",
            action="investigate",
            confidence=0.5,
            rule_used="fallback",
            parameters={"query": query},
            fallback_agents=["InvestigatorAgent", "AnalystAgent"],
        )

        self.logger.warning(
            "routing_fallback_used",
            query=query[:50],
            confidence=fallback_decision.confidence,
        )

        return fallback_decision

    async def _route_query(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> RoutingDecision:
        """Route query based on payload."""
        query = payload.get("query", "")
        if not query:
            raise ValidationError("Query is required for routing")

        user_preferences = payload.get("user_preferences")
        return await self.route_query(query, context, user_preferences)

    async def _apply_routing_rules(
        self,
        query: str,
        context: AgentContext,
    ) -> Optional[RoutingDecision]:
        """Apply rule-based routing."""
        query_lower = query.lower()

        for rule in self.routing_rules:
            confidence = 0.0

            # Check regex patterns
            pattern_matches = 0
            for pattern in rule.patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    pattern_matches += 1

            if rule.patterns:
                confidence += (pattern_matches / len(rule.patterns)) * 0.6

            # Check keywords
            keyword_matches = 0
            for keyword in rule.keywords:
                if keyword.lower() in query_lower:
                    keyword_matches += 1

            if rule.keywords:
                confidence += (keyword_matches / len(rule.keywords)) * 0.4

            # Apply rule priority weight
            confidence = min(confidence * (rule.priority / 10), 1.0)

            if confidence >= rule.confidence_threshold:
                return RoutingDecision(
                    target_agent=rule.target_agent,
                    action=rule.action,
                    confidence=confidence,
                    rule_used=rule.name,
                    parameters={"query": query, **rule.metadata},
                )

        return None

    async def _semantic_routing(
        self,
        query: str,
        context: AgentContext,
    ) -> Optional[RoutingDecision]:
        """Use LLM for semantic routing."""
        try:
            routing_prompt = self._create_routing_prompt(query)

            response = await self.llm_service.generate(
                prompt=routing_prompt,
                context=context,
            )

            # Parse LLM response
            decision = self._parse_routing_response(response, query)
            return decision

        except Exception as e:
            self.logger.error(
                "semantic_routing_failed",
                query=query[:50],
                error=str(e),
            )
            return None

    async def _detect_intent(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """Detect intent from query."""
        query = payload.get("query", "")

        # Simple intent detection based on patterns
        intents = {
            "investigation": ["investigar", "analisar", "verificar", "buscar"],
            "explanation": ["explicar", "entender", "como", "por que"],
            "comparison": ["comparar", "diferença", "melhor", "versus"],
            "trend_analysis": ["tendência", "evolução", "histórico", "ao longo"],
            "anomaly_detection": ["suspeito", "anômalo", "irregular", "estranho"],
        }

        query_lower = query.lower()
        detected_intents = []

        for intent, keywords in intents.items():
            confidence = sum(1 for keyword in keywords if keyword in query_lower)
            if confidence > 0:
                detected_intents.append(
                    {
                        "intent": intent,
                        "confidence": min(confidence / len(keywords), 1.0),
                    }
                )

        # Sort by confidence
        detected_intents.sort(key=lambda x: x["confidence"], reverse=True)

        return {
            "query": query,
            "intents": detected_intents,
            "primary_intent": (
                detected_intents[0]["intent"] if detected_intents else "unknown"
            ),
        }

    async def _analyze_query_type(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """Analyze query type and complexity."""
        query = payload.get("query", "")

        # Simple query analysis
        analysis = {
            "length": len(query),
            "word_count": len(query.split()),
            "has_numbers": bool(re.search(r"\d", query)),
            "has_dates": bool(re.search(r"\d{4}|\d{2}/\d{2}", query)),
            "has_organizations": bool(
                re.search(r"ministério|prefeitura|secretaria", query, re.IGNORECASE)
            ),
            "complexity": "simple",
        }

        # Determine complexity
        if analysis["word_count"] > 20 or "e" in query.lower():
            analysis["complexity"] = "complex"
        elif analysis["word_count"] > 10:
            analysis["complexity"] = "medium"

        return analysis

    async def _suggest_agents(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> list[dict[str, Any]]:
        """Suggest possible agents for a query."""
        query = payload.get("query", "")

        suggestions = []

        # Analyze query and match with agent capabilities
        for agent_name, capabilities in self.agent_capabilities.items():
            score = 0.0
            reasons = []

            query_lower = query.lower()

            # Score based on capabilities
            if "investigar" in query_lower and "investigate" in capabilities:
                score += 0.8
                reasons.append("Query requires investigation")

            if "analisar" in query_lower and "analyze" in capabilities:
                score += 0.7
                reasons.append("Query requires analysis")

            if "relatório" in query_lower and "report" in capabilities:
                score += 0.6
                reasons.append("Query mentions reports")

            if score > 0:
                suggestions.append(
                    {
                        "agent_name": agent_name,
                        "score": score,
                        "reasons": reasons,
                        "capabilities": capabilities,
                    }
                )

        # Sort by score
        suggestions.sort(key=lambda x: x["score"], reverse=True)

        return suggestions

    async def _validate_routing(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """Validate a routing decision."""
        decision_data = payload.get("decision", {})

        target_agent = decision_data.get("target_agent")
        action = decision_data.get("action")

        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
        }

        # Check if agent exists
        if target_agent not in self.agent_capabilities:
            validation["valid"] = False
            validation["errors"].append(f"Agent {target_agent} not registered")

        # Check if agent supports the action
        elif action not in self.agent_capabilities.get(target_agent, []):
            validation["warnings"].append(
                f"Agent {target_agent} may not support action {action}"
            )

        return validation

    def _initialize_default_rules(self) -> None:
        """Initialize default routing rules."""
        rules = [
            # Investigation rules
            RoutingRule(
                name="investigation_query",
                patterns=[r"investigar|verificar|analisar.*gasto"],
                keywords=["investigar", "verificar", "analisar", "suspeito"],
                target_agent="MasterAgent",
                action="investigate",
                priority=9,
            ),
            # Anomaly detection rules
            RoutingRule(
                name="anomaly_detection",
                patterns=[r"suspeito|anômalo|irregular|estranho"],
                keywords=["suspeito", "anômalo", "irregular", "superfaturamento"],
                target_agent="InvestigatorAgent",
                action="detect_anomalies",
                priority=8,
            ),
            # Pattern analysis rules
            RoutingRule(
                name="pattern_analysis",
                patterns=[r"padrão|tendência|evolução"],
                keywords=["padrão", "tendência", "evolução", "histórico"],
                target_agent="AnalystAgent",
                action="analyze_patterns",
                priority=7,
            ),
            # Report generation rules
            RoutingRule(
                name="report_generation",
                patterns=[r"relatório|resumo|gerar.*relatório"],
                keywords=["relatório", "resumo", "documento"],
                target_agent="ReporterAgent",
                action="generate_report",
                priority=6,
            ),
            # Memory/context rules
            RoutingRule(
                name="memory_query",
                patterns=[r"lembrar|anterior|histórico.*investigação"],
                keywords=["lembrar", "anterior", "histórico"],
                target_agent="ContextMemoryAgent",
                action="retrieve_episodic",
                priority=5,
            ),
        ]

        for rule in rules:
            self.routing_rules.append(rule)

        # Sort by priority
        self.routing_rules.sort(key=lambda r: r.priority, reverse=True)

    def _create_routing_prompt(self, query: str) -> str:
        """Create prompt for LLM-based routing."""
        agents_info = []
        for agent_name, capabilities in self.agent_capabilities.items():
            agents_info.append(f"- {agent_name}: {', '.join(capabilities)}")

        agents_text = (
            "\n".join(agents_info)
            if agents_info
            else "- MasterAgent: investigate, coordinate"
        )

        return f"""
        Analise a seguinte consulta e determine qual agente é mais adequado para processá-la:

        Consulta: "{query}"

        Agentes disponíveis:
        {agents_text}

        Responda em formato JSON:
        {{
            "target_agent": "nome_do_agente",
            "action": "ação_a_executar",
            "confidence": 0.8,
            "reasoning": "explicação da escolha"
        }}
        """

    def _parse_routing_response(
        self,
        response: str,
        query: str,
    ) -> Optional[RoutingDecision]:
        """Parse LLM routing response."""
        try:
            import json

            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)

                return RoutingDecision(
                    target_agent=data.get("target_agent", "MasterAgent"),
                    action=data.get("action", "investigate"),
                    confidence=data.get("confidence", 0.5),
                    rule_used="llm_semantic",
                    parameters={"query": query, "reasoning": data.get("reasoning", "")},
                )

        except Exception as e:
            self.logger.error(
                "routing_response_parse_failed",
                response=response[:100],
                error=str(e),
            )

        return None
