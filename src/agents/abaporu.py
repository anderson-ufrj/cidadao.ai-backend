"""
Module: agents.abaporu
Codinome: Abaporu - Núcleo Central da IA (Master Orchestrator)
Description: Master agent that orchestrates multi-agent investigations with self-reflection

This module implements the Abaporu master agent, responsible for:
- Orchestrating complex investigations across multiple specialized agents
- Dynamic investigation planning based on query analysis
- Parallel execution of independent investigation steps
- Self-reflection and quality assessment of results
- Adaptive strategy adjustment based on intermediate findings

The agent uses keyword-based query analysis to intelligently select and coordinate
the most appropriate specialized agents for each investigation.

Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved

Example:
    >>> from src.agents.abaporu import MasterAgent
    >>> from src.agents.deodoro import AgentContext, AgentMessage
    >>>
    >>> # Initialize master agent with dependencies
    >>> master = MasterAgent(llm_service=llm, memory_agent=memory)
    >>> await master.initialize()
    >>>
    >>> # Register specialized agents
    >>> master.register_agent("Zumbi", zumbi_instance)
    >>> master.register_agent("Anita", anita_instance)
    >>>
    >>> # Process investigation
    >>> message = AgentMessage(
    ...     sender="user",
    ...     recipient="Abaporu",
    ...     action="investigate",
    ...     payload={"query": "Detect anomalies in health contracts"}
    ... )
    >>> result = await master.process(message, context)
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel
from pydantic import Field as PydanticField

from src.core import AgentStatus, ReflectionType
from src.core.exceptions import AgentExecutionError, InvestigationError
from src.services.maritaca_client import MaritacaClient

from .deodoro import AgentContext, AgentMessage, AgentResponse, ReflectiveAgent
from .parallel_processor import ParallelStrategy, ParallelTask, parallel_processor


class InvestigationPlan(BaseModel):
    """Plan for conducting an investigation."""

    objective: str = PydanticField(..., description="Investigation objective")
    steps: list[dict[str, Any]] = PydanticField(..., description="Investigation steps")
    required_agents: list[str] = PydanticField(..., description="Required agents")
    estimated_time: int = PydanticField(..., description="Estimated time in seconds")
    quality_criteria: dict[str, Any] = PydanticField(
        ..., description="Quality criteria"
    )
    fallback_strategies: list[str] = PydanticField(
        default_factory=list, description="Fallback strategies"
    )


class InvestigationResult(BaseModel):
    """Result of an investigation."""

    investigation_id: str = PydanticField(..., description="Investigation ID")
    query: str = PydanticField(..., description="Original query")
    findings: list[dict[str, Any]] = PydanticField(
        ..., description="Investigation findings"
    )
    confidence_score: float = PydanticField(..., description="Confidence in results")
    sources: list[str] = PydanticField(..., description="Data sources used")
    explanation: str | None = PydanticField(
        default=None, description="Explanation of findings"
    )
    metadata: dict[str, Any] = PydanticField(
        default_factory=dict, description="Additional metadata"
    )
    timestamp: datetime = PydanticField(default_factory=lambda: datetime.now(UTC))
    processing_time_ms: float | None = PydanticField(
        default=None, description="Processing time"
    )


class MasterAgent(ReflectiveAgent):
    """
    Master agent that orchestrates investigations using other agents.

    This agent has self-reflection capabilities and can:
    - Plan investigation strategies
    - Coordinate with other agents
    - Monitor progress and quality
    - Adapt strategies based on results
    - Provide comprehensive explanations
    """

    def __init__(
        self,
        maritaca_client: MaritacaClient,
        memory_agent: Any,
        reflection_threshold: float = 0.8,
        max_reflection_loops: int = 3,
        **kwargs: Any,
    ) -> None:
        """
        Initialize master agent.

        Args:
            maritaca_client: Maritaca AI client for LLM operations
            memory_agent: Memory agent instance
            reflection_threshold: Minimum quality threshold
            max_reflection_loops: Maximum reflection iterations
            **kwargs: Additional arguments
        """
        super().__init__(
            name="MasterAgent",
            description="Orchestrates investigations with self-reflection capabilities",
            capabilities=[
                "plan_investigation",
                "coordinate_agents",
                "monitor_progress",
                "reflect_on_results",
                "generate_explanations",
                "adapt_strategies",
            ],
            reflection_threshold=reflection_threshold,
            max_reflection_loops=max_reflection_loops,
            **kwargs,
        )

        self.maritaca_client = maritaca_client
        self.memory_agent = memory_agent
        self.active_investigations: dict[str, InvestigationPlan] = {}
        self.agent_registry: dict[str, Any] = {}

        self.logger.info(
            "abaporu_initialized",
            reflection_threshold=reflection_threshold,
            max_reflection_loops=max_reflection_loops,
        )

    async def initialize(self) -> None:
        """Initialize master agent."""
        self.logger.info("abaporu_initializing")

        # Initialize sub-services
        if hasattr(self.memory_agent, "initialize"):
            await self.memory_agent.initialize()

        # Verify Maritaca client is functional
        try:
            health = await self.maritaca_client.health_check()
            self.logger.info(
                "maritaca_health_check",
                status=health.get("status"),
                model=health.get("model"),
            )
        except Exception as e:
            self.logger.warning(
                "maritaca_health_check_failed",
                error=str(e),
                message="Continuing without health check",
            )

        self.status = AgentStatus.IDLE
        self.logger.info("abaporu_initialized")

    async def shutdown(self) -> None:
        """Shutdown master agent."""
        self.logger.info("abaporu_shutting_down")

        # Cleanup resources
        if hasattr(self.maritaca_client, "shutdown"):
            await self.maritaca_client.shutdown()

        if hasattr(self.memory_agent, "shutdown"):
            await self.memory_agent.shutdown()

        self.active_investigations.clear()
        self.agent_registry.clear()

        self.logger.info("abaporu_shutdown_complete")

    def register_agent(self, agent_name: str, agent_instance: Any) -> None:
        """
        Register a sub-agent with the master agent.

        Args:
            agent_name: Name of the agent
            agent_instance: Agent instance
        """
        self.agent_registry[agent_name] = agent_instance
        self.logger.info(
            "agent_registered",
            agent_name=agent_name,
            total_agents=len(self.agent_registry),
        )

    async def process(
        self,
        message: AgentMessage,
        context: AgentContext,
    ) -> AgentResponse:
        """
        Process a message using the master agent.

        Args:
            message: Message to process
            context: Agent context

        Returns:
            Agent response
        """
        action = message.action
        payload = message.payload

        self.logger.info(
            "master_agent_processing",
            action=action,
            investigation_id=context.investigation_id,
        )

        try:
            if action == "investigate":
                result = await self._investigate(payload, context)
            elif action == "plan_investigation":
                result = await self._plan_investigation(payload, context)
            elif action == "monitor_progress":
                result = await self._monitor_progress(payload, context)
            elif action == "adapt_strategy":
                result = await self._adapt_strategy(payload, context)
            else:
                raise AgentExecutionError(
                    f"Unknown action: {action}",
                    details={"action": action, "available_actions": self.capabilities},
                )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result=result,
                metadata={
                    "action": action,
                    "investigation_id": context.investigation_id,
                },
            )

        except Exception as e:
            self.logger.error(
                "master_agent_processing_failed",
                action=action,
                error=str(e),
                investigation_id=context.investigation_id,
            )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.ERROR,
                error=str(e),
                metadata={
                    "action": action,
                    "investigation_id": context.investigation_id,
                },
            )

    async def _investigate(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> InvestigationResult:
        """
        Conduct a full investigation.

        Args:
            payload: Investigation payload with query
            context: Agent context

        Returns:
            Investigation result
        """
        query = payload.get("query", "")
        if not query:
            raise InvestigationError("No query provided for investigation")

        investigation_id = context.investigation_id
        start_time = datetime.now(UTC)

        self.logger.info(
            "investigation_started",
            investigation_id=investigation_id,
            query=query,
        )

        # Step 1: Create investigation plan
        plan = await self._plan_investigation({"query": query}, context)
        self.active_investigations[investigation_id] = plan

        # Step 2: Execute investigation steps in parallel when possible
        findings = []
        sources = []

        # Group steps that can be executed in parallel
        parallel_groups = self._group_parallel_steps(plan.steps)

        for group_idx, step_group in enumerate(parallel_groups):
            if len(step_group) > 1:
                # Execute in parallel
                self.logger.info(
                    f"Executing {len(step_group)} steps in parallel for group {group_idx}"
                )

                # Create parallel tasks
                tasks = []
                for step in step_group:
                    agent_type = self.agent_registry.get(step["agent"])
                    if agent_type:
                        task = ParallelTask(
                            agent_type=agent_type,
                            message=AgentMessage(
                                sender=self.name,
                                recipient=step["agent"],
                                action=step["action"],
                                payload=step.get("payload", {}),
                            ),
                            timeout=30.0,
                        )
                        tasks.append(task)

                # Execute parallel tasks
                parallel_results = await parallel_processor.execute_parallel(
                    tasks, context, strategy=ParallelStrategy.BEST_EFFORT
                )

                # Aggregate results
                aggregated = parallel_processor.aggregate_results(parallel_results)
                findings.extend(aggregated.get("findings", []))
                sources.extend(aggregated.get("sources", []))

            else:
                # Execute single step
                step = step_group[0]
                step_result = await self._execute_step(step, context)

                if step_result.status == AgentStatus.COMPLETED:
                    findings.extend(step_result.result.get("findings", []))
                    sources.extend(step_result.result.get("sources", []))
                else:
                    self.logger.warning(
                        "investigation_step_failed",
                        investigation_id=investigation_id,
                        step=step,
                        error=step_result.error,
                    )

        # Step 3: Generate explanation
        explanation = await self._generate_explanation(findings, query, context)

        # Step 4: Calculate confidence score
        confidence_score = self._calculate_confidence_score(findings, sources)

        # Step 5: Create result
        processing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

        result = InvestigationResult(
            investigation_id=investigation_id,
            query=query,
            findings=findings,
            confidence_score=confidence_score,
            sources=list(set(sources)),
            explanation=explanation,
            metadata={
                "plan": plan.model_dump(),
                "steps_executed": len(plan.steps),
                "agents_used": plan.required_agents,
            },
            processing_time_ms=processing_time,
        )

        # Store in memory
        await self.memory_agent.store_investigation(result, context)

        self.logger.info(
            "investigation_completed",
            investigation_id=investigation_id,
            findings_count=len(findings),
            confidence_score=confidence_score,
            processing_time_ms=processing_time,
        )

        return result

    def _group_parallel_steps(
        self, steps: list[dict[str, Any]]
    ) -> list[list[dict[str, Any]]]:
        """
        Group steps that can be executed in parallel.

        Steps can be parallel if they don't depend on each other's output.
        """
        groups = []
        current_group = []
        seen_agents = set()

        for step in steps:
            agent = step.get("agent", "")
            depends_on = step.get("depends_on", [])

            # Check if this step depends on any agent in current group
            depends_on_current = any(dep in seen_agents for dep in depends_on)

            if depends_on_current or agent in seen_agents:
                # Start new group
                if current_group:
                    groups.append(current_group)
                current_group = [step]
                seen_agents = {agent}
            else:
                # Add to current group
                current_group.append(step)
                seen_agents.add(agent)

        # Add final group
        if current_group:
            groups.append(current_group)

        return groups

    async def _plan_investigation(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> InvestigationPlan:
        """
        Create an investigation plan using Maritaca AI.

        Args:
            payload: Planning payload
            context: Agent context

        Returns:
            Investigation plan
        """
        query = payload.get("query", "")

        # Get relevant context from memory
        memory_context = {}
        try:
            if hasattr(self.memory_agent, "get_relevant_context"):
                memory_context = await self.memory_agent.get_relevant_context(
                    query, context
                )
        except Exception as e:
            self.logger.warning(
                "memory_context_retrieval_failed",
                error=str(e),
                message="Continuing without memory context",
            )

        # Use Maritaca AI to generate plan
        planning_prompt = self._create_planning_prompt(query, memory_context)

        try:
            response = await self.maritaca_client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em análise de transparência pública brasileira, responsável por planejar investigações detalhadas.",
                    },
                    {"role": "user", "content": planning_prompt},
                ],
                temperature=0.7,
                max_tokens=2048,
            )

            plan_response = response.content
            self.logger.info(
                "llm_plan_generation_success",
                investigation_id=context.investigation_id,
                tokens_used=response.usage.get("total_tokens", 0),
            )

        except Exception as e:
            self.logger.warning(
                "llm_plan_generation_failed",
                error=str(e),
                message="Falling back to keyword-based planning",
            )
            # Fallback to keyword-based plan
            plan_response = ""

        # Parse and validate plan (fallback to keyword-based if LLM fails)
        plan = self._parse_investigation_plan(plan_response, query)

        self.logger.info(
            "investigation_plan_created",
            investigation_id=context.investigation_id,
            steps_count=len(plan.steps),
            required_agents=plan.required_agents,
        )

        return plan

    async def _execute_step(
        self,
        step: dict[str, Any],
        context: AgentContext,
    ) -> AgentResponse:
        """
        Execute a single investigation step.

        Args:
            step: Investigation step
            context: Agent context

        Returns:
            Step result
        """
        agent_name = step.get("agent")
        action = step.get("action")
        parameters = step.get("parameters", {})

        if agent_name not in self.agent_registry:
            raise AgentExecutionError(
                f"Agent {agent_name} not registered",
                details={
                    "agent": agent_name,
                    "available_agents": list(self.agent_registry.keys()),
                },
            )

        agent = self.agent_registry[agent_name]

        return await agent.execute(action, parameters, context)

    async def _generate_explanation(
        self,
        findings: list[dict[str, Any]],
        query: str,
        context: AgentContext,
    ) -> str:
        """
        Generate explanation for investigation findings using Maritaca AI.

        Args:
            findings: Investigation findings
            query: Original query
            context: Agent context

        Returns:
            Explanation text
        """
        explanation_prompt = self._create_explanation_prompt(findings, query)

        try:
            response = await self.maritaca_client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um jornalista investigativo especializado em transparência pública brasileira. Crie explicações claras e objetivas para cidadãos comuns.",
                    },
                    {"role": "user", "content": explanation_prompt},
                ],
                temperature=0.6,  # Lower temperature for more focused explanations
                max_tokens=3000,  # Allow longer explanations
            )

            explanation = response.content
            self.logger.info(
                "llm_explanation_generation_success",
                investigation_id=context.investigation_id,
                tokens_used=response.usage.get("total_tokens", 0),
                explanation_length=len(explanation),
            )

        except Exception as e:
            self.logger.error(
                "llm_explanation_generation_failed",
                error=str(e),
                investigation_id=context.investigation_id,
            )
            # Fallback to basic summary
            explanation = self._generate_fallback_explanation(findings, query)

        return explanation

    def _generate_fallback_explanation(
        self,
        findings: list[dict[str, Any]],
        query: str,
    ) -> str:
        """
        Generate a basic fallback explanation when LLM is unavailable.

        Args:
            findings: Investigation findings
            query: Original query

        Returns:
            Basic explanation text
        """
        findings_count = len(findings)
        high_anomaly_count = len(
            [f for f in findings if f.get("anomaly_score", 0) > 0.7]
        )

        explanation = f"""
## Resumo da Investigação

**Consulta**: {query}

**Achados**: {findings_count} contratos/registros analisados, {high_anomaly_count} com alta suspeita.

### Principais Achados:
"""

        for i, finding in enumerate(findings[:5], 1):  # Top 5 findings
            anomaly_score = finding.get("anomaly_score", 0)
            value = finding.get("value", "N/A")
            description = finding.get("description", "Sem descrição")

            severity = (
                "🔴 CRÍTICO"
                if anomaly_score > 0.9
                else "🟡 ALTO" if anomaly_score > 0.7 else "🟢 MODERADO"
            )

            explanation += f"\n{i}. {severity} - {description}"
            explanation += (
                f"\n   - Valor: R$ {value:,.2f}"
                if isinstance(value, (int, float))
                else f"\n   - Valor: {value}"
            )
            explanation += f"\n   - Score de Anomalia: {anomaly_score:.2%}\n"

        explanation += """
### Nota:
Esta é uma análise automatizada básica. Para uma interpretação mais detalhada,
recomendamos consulta com especialistas em transparência pública.
"""

        return explanation

    def _calculate_confidence_score(
        self,
        findings: list[dict[str, Any]],
        sources: list[str],
    ) -> float:
        """
        Calculate confidence score for investigation results.

        Args:
            findings: Investigation findings
            sources: Data sources used

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not findings:
            return 0.0

        # Base confidence on number of findings and sources
        findings_score = min(
            len(findings) / 10, 1.0
        )  # More findings = higher confidence
        sources_score = min(len(sources) / 3, 1.0)  # More sources = higher confidence

        # Average anomaly scores from findings
        anomaly_scores = [f.get("anomaly_score", 0.0) for f in findings]
        avg_anomaly_score = (
            sum(anomaly_scores) / len(anomaly_scores) if anomaly_scores else 0.0
        )

        # Weighted average
        confidence = (
            findings_score * 0.3 + sources_score * 0.2 + avg_anomaly_score * 0.5
        )

        return min(confidence, 1.0)

    async def reflect(
        self,
        result: Any,
        context: AgentContext,
    ) -> dict[str, Any]:
        """
        Reflect on investigation results and provide quality assessment.

        Args:
            result: Investigation result
            context: Agent context

        Returns:
            Reflection result
        """
        if not isinstance(result, InvestigationResult):
            return {
                "quality_score": 0.0,
                "issues": ["Invalid result type"],
                "suggestions": ["Fix result format"],
            }

        issues = []
        suggestions = []

        # Check completeness
        if not result.findings:
            issues.append("No findings generated")
            suggestions.append("Review investigation strategy")

        # Check confidence
        if result.confidence_score < 0.5:
            issues.append("Low confidence score")
            suggestions.append("Gather more data or use additional sources")

        # Check explanation quality
        if not result.explanation or len(result.explanation.strip()) < 50:
            issues.append("Poor explanation quality")
            suggestions.append("Generate more detailed explanation")

        # Check source diversity
        if len(result.sources) < 2:
            issues.append("Limited source diversity")
            suggestions.append("Include more data sources")

        # Calculate quality score
        quality_score = self._calculate_quality_score(result, issues)

        reflection = {
            "quality_score": quality_score,
            "issues": issues,
            "suggestions": suggestions,
            "reflection_type": ReflectionType.COMPLETENESS_CHECK.value,
            "metrics": {
                "findings_count": len(result.findings),
                "confidence_score": result.confidence_score,
                "sources_count": len(result.sources),
                "explanation_length": (
                    len(result.explanation) if result.explanation else 0
                ),
            },
        }

        self.logger.info(
            "investigation_reflection",
            investigation_id=result.investigation_id,
            quality_score=quality_score,
            issues_count=len(issues),
        )

        return reflection

    def _calculate_quality_score(
        self,
        result: InvestigationResult,
        issues: list[str],
    ) -> float:
        """Calculate quality score based on result and issues."""
        base_score = 1.0

        # Deduct points for issues
        penalty_per_issue = 0.2
        score = base_score - (len(issues) * penalty_per_issue)

        # Bonus for high confidence
        if result.confidence_score > 0.8:
            score += 0.1

        # Bonus for good explanation
        if result.explanation and len(result.explanation) > 100:
            score += 0.1

        return max(0.0, min(1.0, score))

    def _create_planning_prompt(
        self,
        query: str,
        memory_context: dict[str, Any],
    ) -> str:
        """Create prompt for investigation planning."""
        return f"""
        Você é um especialista em transparência pública e análise de gastos governamentais brasileiros.

        INVESTIGAÇÃO SOLICITADA: "{query}"

        CONTEXTO DE MEMÓRIA: {memory_context if memory_context else "Nenhum contexto anterior disponível"}

        AGENTES ESPECIALIZADOS DISPONÍVEIS:

        1. **Zumbi dos Palmares** - Detector de Anomalias
           - Análise FFT espectral de contratos
           - Detecção de superfaturamento (>2.5σ)
           - Identificação de concentração de fornecedores (>70%)
           - Contratos emergenciais suspeitos

        2. **Anita Garibaldi** - Analista de Padrões
           - Análise temporal de gastos
           - Padrões de licitação
           - Correlação entre fornecedores
           - Tendências e sazonalidade

        3. **José Bonifácio** - Analista de Políticas Públicas
           - Avaliação de efetividade (ROI social)
           - Análise de impacto e beneficiários
           - Frameworks: Logic Model, Theory of Change, Cost-Effectiveness
           - Sustentabilidade de programas

        4. **Lampião** - Analista Regional
           - Desigualdade regional (Gini, Theil, Williamson)
           - Análise geográfica IBGE
           - Hot spots e cold spots (Getis-Ord G*)
           - Otimização de alocação de recursos

        5. **Oscar Niemeyer** - Arquiteto de Dados
           - Agregação multidimensional
           - Séries temporais
           - Metadados para visualização
           - Exportação (JSON, CSV)

        6. **Tiradentes** - Repórter
           - Geração de relatórios executivos
           - Síntese de achados
           - Comunicação clara
           - Recomendações

        FORNEÇA UM PLANO DETALHADO COM:
        1. Objetivo claro da investigação
        2. Sequência de agentes a utilizar (em ordem ou paralelo)
        3. Parâmetros específicos para cada agente
        4. Critérios de qualidade esperados
        5. Fontes de dados a consultar (Portal da Transparência, TCEs, APIs estaduais)
        """

    def _create_explanation_prompt(
        self,
        findings: list[dict[str, Any]],
        query: str,
    ) -> str:
        """Create prompt for explanation generation."""
        findings_count = len(findings)
        anomaly_count = len([f for f in findings if f.get("anomaly_score", 0) > 0.7])

        return f"""
        Você é um jornalista investigativo especializado em transparência pública brasileira.

        INVESTIGAÇÃO: "{query}"

        ACHADOS DA ANÁLISE ({findings_count} total, {anomaly_count} com alta suspeita):
        {findings}

        TAREFA: Crie uma explicação clara e objetiva em português que um cidadão comum possa entender.

        ESTRUTURA OBRIGATÓRIA:

        **1. RESUMO EXECUTIVO (2-3 frases)**
        - O que foi encontrado em linguagem simples
        - Qual o impacto financeiro ou social
        - Nível de gravidade (baixo/médio/alto/crítico)

        **2. ACHADOS PRINCIPAIS**
        Para cada achado importante:
        - Descrição clara do que foi identificado
        - Por que é suspeito ou irregular
        - Valores e datas específicas
        - Entidades envolvidas (órgãos, fornecedores, municípios)

        **3. CONTEXTO COMPARATIVO**
        - Como esses valores/padrões diferem do normal
        - Comparação com médias históricas
        - Comparação com outras regiões (se aplicável)
        - Referências a legislação (LGL, LRF, etc.)

        **4. ANÁLISE DE IMPACTO**
        - Quanto dinheiro público está envolvido
        - Quantas pessoas/municípios afetados
        - Quais serviços públicos podem ter sido prejudicados
        - Dano potencial à população

        **5. PRÓXIMOS PASSOS RECOMENDADOS**
        - Investigações mais aprofundadas necessárias
        - Órgãos de controle que deveriam ser acionados (TCU, TCE, MPF, CGU)
        - Dados adicionais que poderiam ser coletados
        - Possíveis ações judiciais ou administrativas

        **6. NÍVEL DE CONFIANÇA**
        - Qual a certeza dessa análise (0-100%)
        - Quais fontes foram usadas
        - Quais limitações existem nos dados

        IMPORTANTE:
        - Use linguagem clara e acessível (evite jargões técnicos excessivos)
        - Seja preciso com números e datas
        - Cite as fontes (Portal da Transparência, IBGE, TCE, etc.)
        - Mantenha tom profissional e factual (sem sensacionalismo)
        - Se houver incerteza, deixe isso claro
        """

    def _parse_investigation_plan(
        self,
        plan_response: str,
        query: str,
    ) -> InvestigationPlan:
        """
        Parse LLM response or create intelligent investigation plan based on query.

        Creates context-aware plans based on query keywords:
        - Contract/supplier keywords → Zumbi (anomaly detection)
        - Policy/effectiveness keywords → Bonifácio (policy analysis)
        - Geographic/regional keywords → Lampião (regional analysis)
        - Report/visualization keywords → Tiradentes + Niemeyer
        """
        query_lower = query.lower()

        steps = []
        required_agents = []

        # Analyze query to determine needed agents
        needs_anomaly_detection = any(
            keyword in query_lower
            for keyword in [
                "suspeito",
                "anomalia",
                "fraud",
                "irregularidade",
                "contrato",
                "licitação",
                "superfaturamento",
                "emergencial",
            ]
        )

        needs_policy_analysis = any(
            keyword in query_lower
            for keyword in [
                "política",
                "efetividade",
                "impacto",
                "resultado",
                "beneficiário",
                "programa",
                "projeto",
                "investimento",
            ]
        )

        needs_regional_analysis = any(
            keyword in query_lower
            for keyword in [
                "região",
                "estado",
                "município",
                "geográfico",
                "territorial",
                "norte",
                "nordeste",
                "sul",
                "sudeste",
                "centro-oeste",
            ]
        )

        needs_reporting = any(
            keyword in query_lower
            for keyword in ["relatório", "resumo", "análise", "explicação", "documento"]
        )

        # Build investigation plan
        if needs_anomaly_detection:
            steps.append(
                {
                    "agent": "Zumbi",
                    "action": "detect_anomalies",
                    "parameters": {"query": query},
                    "depends_on": [],
                }
            )
            required_agents.append("Zumbi")

        if needs_policy_analysis:
            steps.append(
                {
                    "agent": "Bonifácio",
                    "action": "analyze_policy",
                    "parameters": {"query": query},
                    "depends_on": [],
                }
            )
            required_agents.append("Bonifácio")

        if needs_regional_analysis:
            steps.append(
                {
                    "agent": "Lampião",
                    "action": "analyze_regions",
                    "parameters": {"query": query},
                    "depends_on": [],
                }
            )
            required_agents.append("Lampião")

        # Always include analyst for pattern analysis if anomalies detected
        if needs_anomaly_detection:
            steps.append(
                {
                    "agent": "Anita",
                    "action": "analyze_patterns",
                    "parameters": {"query": query},
                    "depends_on": ["Zumbi"],  # Depends on anomaly detection
                }
            )
            required_agents.append("Anita")

        # Add data aggregation for visualizations
        if needs_regional_analysis or len(steps) > 2:
            steps.append(
                {
                    "agent": "OscarNiemeyer",
                    "action": "aggregate_data",
                    "parameters": {"query": query},
                    "depends_on": required_agents.copy(),  # Depends on all previous
                }
            )
            required_agents.append("OscarNiemeyer")

        # Add reporting if requested
        if needs_reporting or len(steps) > 1:
            steps.append(
                {
                    "agent": "Tiradentes",
                    "action": "generate_report",
                    "parameters": {"query": query},
                    "depends_on": required_agents.copy(),  # Depends on all previous
                }
            )
            required_agents.append("Tiradentes")

        # Fallback: if no steps matched, do basic anomaly detection
        if not steps:
            steps = [
                {
                    "agent": "Zumbi",
                    "action": "detect_anomalies",
                    "parameters": {"query": query},
                    "depends_on": [],
                }
            ]
            required_agents = ["Zumbi"]

        # Estimate time based on complexity
        estimated_time = 30 + (len(steps) * 15)  # Base 30s + 15s per step

        # Quality criteria based on investigation type
        quality_criteria = {
            "min_confidence": 0.75 if needs_anomaly_detection else 0.70,
            "min_findings": 1,
            "min_sources": 2 if len(required_agents) > 1 else 1,
        }

        return InvestigationPlan(
            objective=f"Investigar transparência pública: {query}",
            steps=steps,
            required_agents=list(set(required_agents)),
            estimated_time=estimated_time,
            quality_criteria=quality_criteria,
            fallback_strategies=[
                "Reduzir threshold de anomalias se poucos resultados",
                "Expandir período de análise",
                "Incluir dados de fontes secundárias",
            ],
        )

    async def _monitor_progress(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """Monitor investigation progress."""
        investigation_id = context.investigation_id

        if investigation_id not in self.active_investigations:
            return {"status": "not_found", "message": "Investigation not found"}

        plan = self.active_investigations[investigation_id]

        return {
            "status": "active",
            "plan": plan.model_dump(),
            "progress": {
                "total_steps": len(plan.steps),
                "completed_steps": 0,  # Would track actual progress
            },
        }

    async def _adapt_strategy(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """
        Adapt investigation strategy based on current results.

        Adaptation strategies:
        - Low findings → Expand search criteria or time period
        - Low confidence → Add more data sources
        - High anomaly rate → Increase analysis depth
        - Geographic concentration → Add regional analysis
        """
        investigation_id = context.investigation_id
        current_results = payload.get("current_results", {})
        current_plan = self.active_investigations.get(investigation_id)

        if not current_plan:
            return {"status": "error", "message": "No active investigation found"}

        changes = []
        new_steps = []

        # Extract metrics from current results
        findings_count = len(current_results.get("findings", []))
        confidence_score = current_results.get("confidence_score", 0.0)
        sources_count = len(current_results.get("sources", []))
        anomaly_rate = current_results.get("anomaly_rate", 0.0)

        # Adaptation logic
        if findings_count < current_plan.quality_criteria.get("min_findings", 1):
            # Few findings → Expand search
            changes.append("Expandir critérios de busca")
            changes.append("Reduzir threshold de anomalias de 2.5σ para 2.0σ")

            # Add step to search with relaxed criteria
            new_steps.append(
                {
                    "agent": "Zumbi",
                    "action": "detect_anomalies",
                    "parameters": {
                        "query": payload.get("query", ""),
                        "sensitivity": "high",  # More sensitive
                        "threshold": 2.0,  # Lower threshold
                    },
                    "depends_on": [],
                }
            )

        if confidence_score < current_plan.quality_criteria.get("min_confidence", 0.7):
            # Low confidence → More sources
            changes.append("Adicionar fontes de dados adicionais")
            changes.append("Incluir análise de padrões históricos")

            # Add Anita for pattern analysis if not present
            if "Anita" not in current_plan.required_agents:
                new_steps.append(
                    {
                        "agent": "Anita",
                        "action": "analyze_patterns",
                        "parameters": {"query": payload.get("query", "")},
                        "depends_on": ["Zumbi"],
                    }
                )
                changes.append("Adicionar agente Anita para análise de padrões")

        if sources_count < current_plan.quality_criteria.get("min_sources", 2):
            # Few sources → Diversify
            changes.append("Diversificar fontes de dados")

            # Add regional analysis if not present
            if "Lampião" not in current_plan.required_agents:
                new_steps.append(
                    {
                        "agent": "Lampião",
                        "action": "analyze_regions",
                        "parameters": {"query": payload.get("query", "")},
                        "depends_on": [],
                    }
                )
                changes.append("Adicionar análise regional com Lampião")

        if anomaly_rate > 0.3:  # More than 30% anomalies
            # High anomaly rate → Deep analysis
            changes.append("Aumentar profundidade da análise")
            changes.append("Adicionar análise de políticas públicas")

            # Add Bonifácio for policy analysis
            if "Bonifácio" not in current_plan.required_agents:
                new_steps.append(
                    {
                        "agent": "Bonifácio",
                        "action": "analyze_policy",
                        "parameters": {"query": payload.get("query", "")},
                        "depends_on": [],
                    }
                )
                changes.append("Adicionar José Bonifácio para análise de políticas")

        # Check if concentrated in specific region
        geographic_concentration = current_results.get("geographic_concentration", 0.0)
        if geographic_concentration > 0.7:  # 70% in one region
            changes.append("Detectada concentração geográfica")
            if "Lampião" not in current_plan.required_agents:
                new_steps.append(
                    {
                        "agent": "Lampião",
                        "action": "analyze_inequality",
                        "parameters": {"metric": "contract_distribution"},
                        "depends_on": [],
                    }
                )
                changes.append("Adicionar análise de desigualdade regional")

        # Update plan with new steps
        if new_steps:
            current_plan.steps.extend(new_steps)
            # Update required agents
            for step in new_steps:
                agent = step.get("agent")
                if agent and agent not in current_plan.required_agents:
                    current_plan.required_agents.append(agent)

        # Log adaptation
        self.logger.info(
            "strategy_adapted",
            investigation_id=investigation_id,
            changes_count=len(changes),
            new_steps_count=len(new_steps),
            reason=f"findings={findings_count}, confidence={confidence_score:.2f}",
        )

        return {
            "status": "adapted",
            "changes": changes,
            "new_steps": new_steps,
            "metrics": {
                "findings_count": findings_count,
                "confidence_score": confidence_score,
                "sources_count": sources_count,
                "anomaly_rate": anomaly_rate,
            },
        }
