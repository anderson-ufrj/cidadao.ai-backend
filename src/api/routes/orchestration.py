"""
API routes for agent orchestration.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from uuid import uuid4

from src.core import get_logger
from src.api.auth import User
from src.api.dependencies import get_current_user
from src.services.agent_orchestrator import (
    AgentOrchestrator,
    WorkflowDefinition,
    WorkflowStep,
    OrchestrationPattern,
    get_orchestrator
)
from src.agents.deodoro import AgentContext
from src.core.exceptions import OrchestrationError


router = APIRouter()
logger = get_logger("api.orchestration")


class WorkflowStepRequest(BaseModel):
    """Request model for workflow step."""
    step_id: str
    agent_name: str
    action: str
    input_mapping: Dict[str, str] = Field(default_factory=dict)
    output_mapping: Dict[str, str] = Field(default_factory=dict)
    conditions: Dict[str, Any] = Field(default_factory=dict)
    retry_config: Dict[str, Any] = Field(default_factory=dict)
    timeout: int = 300


class WorkflowRequest(BaseModel):
    """Request model for workflow execution."""
    workflow_id: Optional[str] = None
    name: str
    pattern: str = "sequential"
    steps: List[WorkflowStepRequest]
    initial_data: Dict[str, Any]
    timeout: int = 1800


class ConditionalWorkflowRequest(BaseModel):
    """Request model for conditional workflow."""
    workflow_definition: Dict[str, Any]
    initial_data: Dict[str, Any]


class CapabilitySearchRequest(BaseModel):
    """Request model for capability search."""
    required_capabilities: List[str]
    prefer_single_agent: bool = True


@router.post("/workflows/execute")
async def execute_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Execute an orchestrated workflow."""
    try:
        # Create workflow definition
        workflow_def = WorkflowDefinition(
            workflow_id=request.workflow_id or str(uuid4()),
            name=request.name,
            pattern=OrchestrationPattern(request.pattern),
            steps=[
                WorkflowStep(
                    step_id=step.step_id,
                    agent_name=step.agent_name,
                    action=step.action,
                    input_mapping=step.input_mapping,
                    output_mapping=step.output_mapping,
                    conditions=step.conditions,
                    retry_config=step.retry_config,
                    timeout=step.timeout
                )
                for step in request.steps
            ],
            timeout=request.timeout
        )
        
        # Register workflow
        orchestrator._workflows[workflow_def.workflow_id] = workflow_def
        
        # Create context
        context = AgentContext(
            investigation_id=str(uuid4()),
            user_id=current_user.id,
            session_id=str(uuid4()),
            metadata={
                "workflow_id": workflow_def.workflow_id,
                "workflow_name": workflow_def.name,
                "pattern": workflow_def.pattern.value
            }
        )
        
        # Execute workflow
        result = await orchestrator.execute_workflow(
            workflow_def.workflow_id,
            request.initial_data,
            context
        )
        
        return {
            "status": "success",
            "workflow_id": workflow_def.workflow_id,
            "result": result
        }
        
    except OrchestrationError as e:
        logger.error(f"Orchestration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in workflow execution: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/workflows/conditional")
async def execute_conditional_workflow(
    request: ConditionalWorkflowRequest,
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Execute a conditional workflow with branching."""
    try:
        # Create context
        context = AgentContext(
            investigation_id=str(uuid4()),
            user_id=current_user.id,
            session_id=str(uuid4()),
            metadata={
                "workflow_type": "conditional",
                "workflow_definition": request.workflow_definition
            }
        )
        
        # Execute conditional workflow
        execution_path = await orchestrator.execute_conditional_workflow(
            request.workflow_definition,
            request.initial_data,
            context
        )
        
        return {
            "status": "success",
            "execution_path": execution_path,
            "total_steps": len(execution_path)
        }
        
    except Exception as e:
        logger.error(f"Error in conditional workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/discover")
async def discover_agents(
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Discover all available agents and their capabilities."""
    try:
        agents = await orchestrator.discover_agents()
        
        # Enrich with capabilities
        enriched_agents = []
        for agent in agents:
            agent_info = {
                "name": agent["name"],
                "description": agent.get("description", ""),
                "capabilities": orchestrator._agent_capabilities.get(agent["name"], []),
                "status": agent.get("status", "available")
            }
            enriched_agents.append(agent_info)
        
        return {
            "status": "success",
            "total_agents": len(enriched_agents),
            "agents": enriched_agents
        }
        
    except Exception as e:
        logger.error(f"Error discovering agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/find-by-capability")
async def find_agents_by_capability(
    request: CapabilitySearchRequest,
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Find agents with specific capabilities."""
    try:
        # Find agents for each capability
        capability_matches = {}
        for capability in request.required_capabilities:
            matching_agents = await orchestrator.find_agents_with_capability(capability)
            capability_matches[capability] = matching_agents
        
        # Find agents that have all required capabilities
        all_agents = set()
        for agents in capability_matches.values():
            for agent in agents:
                all_agents.add(agent["name"])
        
        # Filter agents that have all capabilities
        qualified_agents = []
        for agent_name in all_agents:
            agent_capabilities = orchestrator._agent_capabilities.get(agent_name, [])
            if all(cap in agent_capabilities for cap in request.required_capabilities):
                qualified_agents.append({
                    "name": agent_name,
                    "capabilities": agent_capabilities,
                    "match_score": len(set(request.required_capabilities) & set(agent_capabilities))
                })
        
        # Sort by match score
        qualified_agents.sort(key=lambda x: x["match_score"], reverse=True)
        
        # If prefer single agent, return the best match
        if request.prefer_single_agent and qualified_agents:
            best_agent = await orchestrator.select_best_agent(request.required_capabilities)
            return {
                "status": "success",
                "best_match": {
                    "name": best_agent.name if best_agent else None,
                    "capabilities": orchestrator._agent_capabilities.get(best_agent.name, []) if best_agent else []
                },
                "all_matches": qualified_agents
            }
        
        return {
            "status": "success",
            "matching_agents": qualified_agents,
            "total_matches": len(qualified_agents)
        }
        
    except Exception as e:
        logger.error(f"Error finding agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orchestrator/stats")
async def get_orchestrator_stats(
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Get orchestrator statistics and performance metrics."""
    try:
        stats = await orchestrator.get_stats()
        return {
            "status": "success",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting orchestrator stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/patterns/{pattern}")
async def execute_pattern_workflow(
    pattern: str,
    data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Execute a specific orchestration pattern."""
    try:
        # Validate pattern
        try:
            pattern_enum = OrchestrationPattern(pattern)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid pattern: {pattern}")
        
        # Create a simple workflow for the pattern
        if pattern == "map_reduce":
            steps = [
                WorkflowStep(
                    step_id="map",
                    agent_name="zumbi",
                    action="analyze"
                ),
                WorkflowStep(
                    step_id="reduce",
                    agent_name="anita",
                    action="aggregate"
                )
            ]
        elif pattern == "fan_out_fan_in":
            steps = [
                WorkflowStep(
                    step_id="analyze1",
                    agent_name="zumbi",
                    action="analyze"
                ),
                WorkflowStep(
                    step_id="analyze2",
                    agent_name="maria_quiteria",
                    action="security_audit"
                ),
                WorkflowStep(
                    step_id="analyze3",
                    agent_name="bonifacio",
                    action="policy_analysis"
                )
            ]
        else:
            steps = [
                WorkflowStep(
                    step_id="step1",
                    agent_name="zumbi",
                    action="analyze"
                )
            ]
        
        workflow = WorkflowDefinition(
            workflow_id=f"{pattern}_{uuid4()}",
            name=f"{pattern} workflow",
            pattern=pattern_enum,
            steps=steps
        )
        
        orchestrator._workflows[workflow.workflow_id] = workflow
        
        # Create context
        context = AgentContext(
            investigation_id=str(uuid4()),
            user_id=current_user.id,
            session_id=str(uuid4()),
            metadata={"pattern": pattern}
        )
        
        # Execute
        result = await orchestrator.execute_workflow(
            workflow.workflow_id,
            data,
            context
        )
        
        return {
            "status": "success",
            "pattern": pattern,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error executing pattern workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows")
async def list_workflows(
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """List all registered workflows."""
    try:
        workflows = []
        for workflow_id, workflow in orchestrator._workflows.items():
            workflows.append({
                "workflow_id": workflow_id,
                "name": workflow.name,
                "pattern": workflow.pattern.value,
                "steps": len(workflow.steps),
                "timeout": workflow.timeout
            })
        
        return {
            "status": "success",
            "total_workflows": len(workflows),
            "workflows": workflows
        }
        
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))