"""
Module: agents.abaporu
Codinome: Abaporu - Núcleo Central da IA
Description: Master agent that orchestrates other agents with self-reflection
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field as PydanticField

from src.core import AgentStatus, ReflectionType, get_logger
from src.core.exceptions import AgentExecutionError, InvestigationError
from .deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    ReflectiveAgent,
)
from .parallel_processor import (
    ParallelAgentProcessor,
    ParallelTask,
    ParallelStrategy,
    parallel_processor,
)


class InvestigationPlan(BaseModel):
    """Plan for conducting an investigation."""
    
    objective: str = PydanticField(..., description="Investigation objective")
    steps: List[Dict[str, Any]] = PydanticField(..., description="Investigation steps")
    required_agents: List[str] = PydanticField(..., description="Required agents")
    estimated_time: int = PydanticField(..., description="Estimated time in seconds")
    quality_criteria: Dict[str, Any] = PydanticField(..., description="Quality criteria")
    fallback_strategies: List[str] = PydanticField(default_factory=list, description="Fallback strategies")


class InvestigationResult(BaseModel):
    """Result of an investigation."""
    
    investigation_id: str = PydanticField(..., description="Investigation ID")
    query: str = PydanticField(..., description="Original query")
    findings: List[Dict[str, Any]] = PydanticField(..., description="Investigation findings")
    confidence_score: float = PydanticField(..., description="Confidence in results")
    sources: List[str] = PydanticField(..., description="Data sources used")
    explanation: Optional[str] = PydanticField(default=None, description="Explanation of findings")
    metadata: Dict[str, Any] = PydanticField(default_factory=dict, description="Additional metadata")
    timestamp: datetime = PydanticField(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = PydanticField(default=None, description="Processing time")


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
        llm_service: Any,
        memory_agent: Any,
        reflection_threshold: float = 0.8,
        max_reflection_loops: int = 3,
        **kwargs: Any
    ) -> None:
        """
        Initialize master agent.
        
        Args:
            llm_service: LLM service instance
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
            **kwargs
        )
        
        self.llm_service = llm_service
        self.memory_agent = memory_agent
        self.active_investigations: Dict[str, InvestigationPlan] = {}
        self.agent_registry: Dict[str, Any] = {}
        
        self.logger.info(
            "abaporu_initialized",
            reflection_threshold=reflection_threshold,
            max_reflection_loops=max_reflection_loops,
        )
    
    async def initialize(self) -> None:
        """Initialize master agent."""
        self.logger.info("abaporu_initializing")
        
        # Initialize sub-services
        if hasattr(self.llm_service, 'initialize'):
            await self.llm_service.initialize()
        
        if hasattr(self.memory_agent, 'initialize'):
            await self.memory_agent.initialize()
        
        self.status = AgentStatus.IDLE
        self.logger.info("abaporu_initialized")
    
    async def shutdown(self) -> None:
        """Shutdown master agent."""
        self.logger.info("abaporu_shutting_down")
        
        # Cleanup resources
        if hasattr(self.llm_service, 'shutdown'):
            await self.llm_service.shutdown()
        
        if hasattr(self.memory_agent, 'shutdown'):
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
                    details={"action": action, "available_actions": self.capabilities}
                )
            
            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result=result,
                metadata={"action": action, "investigation_id": context.investigation_id},
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
                metadata={"action": action, "investigation_id": context.investigation_id},
            )
    
    async def _investigate(
        self,
        payload: Dict[str, Any],
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
        start_time = datetime.utcnow()
        
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
                    tasks,
                    context,
                    strategy=ParallelStrategy.BEST_EFFORT
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
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
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
    
    def _group_parallel_steps(self, steps: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
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
        payload: Dict[str, Any],
        context: AgentContext,
    ) -> InvestigationPlan:
        """
        Create an investigation plan.
        
        Args:
            payload: Planning payload
            context: Agent context
            
        Returns:
            Investigation plan
        """
        query = payload.get("query", "")
        
        # Get relevant context from memory
        memory_context = await self.memory_agent.get_relevant_context(query, context)
        
        # Use LLM to generate plan
        planning_prompt = self._create_planning_prompt(query, memory_context)
        plan_response = await self.llm_service.generate(
            prompt=planning_prompt,
            context=context,
        )
        
        # Parse and validate plan
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
        step: Dict[str, Any],
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
                details={"agent": agent_name, "available_agents": list(self.agent_registry.keys())}
            )
        
        agent = self.agent_registry[agent_name]
        
        message = AgentMessage(
            sender=self.name,
            recipient=agent_name,
            action=action,
            payload=parameters,
            context=context.to_dict(),
        )
        
        return await agent.execute(action, parameters, context)
    
    async def _generate_explanation(
        self,
        findings: List[Dict[str, Any]],
        query: str,
        context: AgentContext,
    ) -> str:
        """
        Generate explanation for investigation findings.
        
        Args:
            findings: Investigation findings
            query: Original query
            context: Agent context
            
        Returns:
            Explanation text
        """
        explanation_prompt = self._create_explanation_prompt(findings, query)
        
        explanation = await self.llm_service.generate(
            prompt=explanation_prompt,
            context=context,
        )
        
        return explanation
    
    def _calculate_confidence_score(
        self,
        findings: List[Dict[str, Any]],
        sources: List[str],
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
        findings_score = min(len(findings) / 10, 1.0)  # More findings = higher confidence
        sources_score = min(len(sources) / 3, 1.0)      # More sources = higher confidence
        
        # Average anomaly scores from findings
        anomaly_scores = [f.get("anomaly_score", 0.0) for f in findings]
        avg_anomaly_score = sum(anomaly_scores) / len(anomaly_scores) if anomaly_scores else 0.0
        
        # Weighted average
        confidence = (
            findings_score * 0.3 +
            sources_score * 0.2 +
            avg_anomaly_score * 0.5
        )
        
        return min(confidence, 1.0)
    
    async def reflect(
        self,
        result: Any,
        context: AgentContext,
    ) -> Dict[str, Any]:
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
                "explanation_length": len(result.explanation) if result.explanation else 0,
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
        issues: List[str],
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
        memory_context: Dict[str, Any],
    ) -> str:
        """Create prompt for investigation planning."""
        return f"""
        Você é um especialista em investigação de gastos públicos. 
        Crie um plano detalhado para investigar: "{query}"
        
        Contexto da memória: {memory_context}
        
        Agentes disponíveis:
        - InvestigatorAgent: detecta anomalias
        - AnalystAgent: analisa padrões
        - ReporterAgent: gera relatórios
        
        Forneça um plano estruturado com:
        1. Objetivo da investigação
        2. Passos específicos
        3. Agentes necessários
        4. Critérios de qualidade
        """
    
    def _create_explanation_prompt(
        self,
        findings: List[Dict[str, Any]],
        query: str,
    ) -> str:
        """Create prompt for explanation generation."""
        return f"""
        Explique em português claro os resultados da investigação sobre: "{query}"
        
        Achados: {findings}
        
        Forneça uma explicação que:
        1. Resumo dos principais achados
        2. Explique por que são suspeitos
        3. Contextualize com dados normais
        4. Sugira próximos passos
        """
    
    def _parse_investigation_plan(
        self,
        plan_response: str,
        query: str,
    ) -> InvestigationPlan:
        """Parse LLM response into investigation plan."""
        # This is a simplified parser - in production, use more robust parsing
        return InvestigationPlan(
            objective=f"Investigar: {query}",
            steps=[
                {
                    "agent": "InvestigatorAgent",
                    "action": "detect_anomalies",
                    "parameters": {"query": query},
                },
                {
                    "agent": "AnalystAgent",
                    "action": "analyze_patterns",
                    "parameters": {"query": query},
                },
            ],
            required_agents=["InvestigatorAgent", "AnalystAgent"],
            estimated_time=60,
            quality_criteria={"min_confidence": 0.7, "min_findings": 1},
        )
    
    async def _monitor_progress(
        self,
        payload: Dict[str, Any],
        context: AgentContext,
    ) -> Dict[str, Any]:
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
        payload: Dict[str, Any],
        context: AgentContext,
    ) -> Dict[str, Any]:
        """Adapt investigation strategy based on results."""
        # Implementation would analyze current results and modify strategy
        return {
            "status": "adapted",
            "changes": ["Added additional data source", "Increased confidence threshold"],
        }