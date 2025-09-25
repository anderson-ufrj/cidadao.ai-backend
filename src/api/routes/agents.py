"""
Module: api.routes.agents
Description: Direct agent endpoints for specialized AI agents
Author: Anderson H. Silva
Date: 2025-09-25
License: Proprietary - All rights reserved
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from src.core import get_logger
from src.api.middleware.authentication import get_current_user
from src.api.auth import User
from src.infrastructure.rate_limiter import RateLimitTier

# Temporary function until proper rate limit tier detection is implemented
async def get_rate_limit_tier() -> RateLimitTier:
    """Get rate limit tier for current user."""
    return RateLimitTier.BASIC
from src.agents import ZumbiAgent, AnitaAgent, TiradentesAgent, BonifacioAgent, AgentContext
from src.infrastructure.observability.metrics import track_time, count_calls


logger = get_logger(__name__)
router = APIRouter()


class AgentRequest(BaseModel):
    """Base request model for agent operations."""
    query: str = Field(..., description="Query or input for the agent")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    options: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific options")


class AgentResponse(BaseModel):
    """Base response model for agent operations."""
    agent: str = Field(..., description="Agent name")
    result: Dict[str, Any] = Field(..., description="Agent processing result")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata")
    success: bool = Field(default=True, description="Operation success status")
    message: Optional[str] = Field(None, description="Optional status message")


@router.post("/zumbi", response_model=AgentResponse)
@track_time("agent_zumbi_process")
@count_calls("agent_zumbi_requests")
async def process_zumbi_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier)
):
    """
    Process request with Zumbi dos Palmares agent.
    
    Zumbi specializes in anomaly detection and investigation:
    - Price anomalies and overpricing
    - Vendor concentration and cartels
    - Temporal pattern irregularities
    - Contract duplication
    - Payment irregularities
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=current_user.id if current_user else "anonymous",
            session_id=str(request.context.get("session_id", "default")),
            request_id=str(request.context.get("request_id", "unknown")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                **request.context
            }
        )
        
        # Initialize Zumbi agent
        zumbi = ZumbiAgent()
        
        # Process request
        result = await zumbi.process(
            message=request.query,
            context=context,
            **request.options
        )
        
        return AgentResponse(
            agent="zumbi_dos_palmares",
            result=result.data if hasattr(result, 'data') else {"analysis": str(result)},
            metadata={
                "processing_time": result.metadata.get("processing_time", 0) if hasattr(result, 'metadata') else 0,
                "anomalies_detected": result.metadata.get("anomalies_detected", 0) if hasattr(result, 'metadata') else 0,
            },
            success=True,
            message="Anomaly detection completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Zumbi agent error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Zumbi agent processing failed: {str(e)}"
        )


@router.post("/anita", response_model=AgentResponse)
@track_time("agent_anita_process")
@count_calls("agent_anita_requests")
async def process_anita_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier)
):
    """
    Process request with Anita Garibaldi agent.
    
    Anita specializes in pattern analysis and correlation:
    - Spending trends and patterns
    - Organizational behavior analysis
    - Vendor relationship mapping
    - Seasonal pattern detection
    - Efficiency metrics calculation
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=current_user.id if current_user else "anonymous",
            session_id=str(request.context.get("session_id", "default")),
            request_id=str(request.context.get("request_id", "unknown")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                **request.context
            }
        )
        
        # Initialize Anita agent
        anita = AnitaAgent()
        
        # Process request
        result = await anita.process(
            message=request.query,
            context=context,
            **request.options
        )
        
        return AgentResponse(
            agent="anita_garibaldi",
            result=result.data if hasattr(result, 'data') else {"analysis": str(result)},
            metadata={
                "processing_time": result.metadata.get("processing_time", 0) if hasattr(result, 'metadata') else 0,
                "patterns_found": result.metadata.get("patterns_found", 0) if hasattr(result, 'metadata') else 0,
            },
            success=True,
            message="Pattern analysis completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Anita agent error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Anita agent processing failed: {str(e)}"
        )


@router.post("/tiradentes", response_model=AgentResponse)
@track_time("agent_tiradentes_process")
@count_calls("agent_tiradentes_requests")
async def process_tiradentes_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier)
):
    """
    Process request with Tiradentes agent.
    
    Tiradentes specializes in report generation:
    - Executive summaries
    - Detailed investigation reports
    - Multi-format output (JSON, Markdown, HTML)
    - Natural language explanations
    - Actionable recommendations
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=current_user.id if current_user else "anonymous",
            session_id=str(request.context.get("session_id", "default")),
            request_id=str(request.context.get("request_id", "unknown")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                **request.context
            }
        )
        
        # Initialize Tiradentes agent
        tiradentes = TiradentesAgent()
        
        # Process request
        result = await tiradentes.process(
            message=request.query,
            context=context,
            **request.options
        )
        
        return AgentResponse(
            agent="tiradentes",
            result=result.data if hasattr(result, 'data') else {"report": str(result)},
            metadata={
                "processing_time": result.metadata.get("processing_time", 0) if hasattr(result, 'metadata') else 0,
                "report_format": request.options.get("format", "markdown"),
            },
            success=True,
            message="Report generation completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Tiradentes agent error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Tiradentes agent processing failed: {str(e)}"
        )


@router.post("/bonifacio", response_model=AgentResponse)
@track_time("agent_bonifacio_process")
@count_calls("agent_bonifacio_requests")
async def process_bonifacio_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier)
):
    """
    Process request with José Bonifácio agent.
    
    Bonifácio specializes in legal and compliance analysis:
    - Legal framework verification
    - Compliance assessment
    - Regulatory requirement checking
    - Constitutional alignment analysis
    - Legal risk identification
    - Jurisprudence application
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=current_user.id if current_user else "anonymous",
            session_id=str(request.context.get("session_id", "default")),
            request_id=str(request.context.get("request_id", "unknown")),
            metadata={
                "rate_limit_tier": rate_limit_tier.value,
                **request.context
            }
        )
        
        # Initialize Bonifacio agent
        bonifacio = BonifacioAgent()
        
        # Process request
        result = await bonifacio.process(
            message=request.query,
            context=context,
            **request.options
        )
        
        return AgentResponse(
            agent="jose_bonifacio",
            result=result.data if hasattr(result, 'data') else {"analysis": str(result)},
            metadata={
                "processing_time": result.metadata.get("processing_time", 0) if hasattr(result, 'metadata') else 0,
                "compliance_issues": result.metadata.get("compliance_issues", 0) if hasattr(result, 'metadata') else 0,
                "legal_risks": result.metadata.get("legal_risks", []) if hasattr(result, 'metadata') else [],
            },
            success=True,
            message="Legal and compliance analysis completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Bonifacio agent error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Bonifacio agent processing failed: {str(e)}"
        )


@router.post("/maria-quiteria", response_model=AgentResponse)
@track_time("agent_maria_quiteria_process")
@count_calls("agent_maria_quiteria_requests")
async def process_maria_quiteria_request(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    rate_limit_tier: RateLimitTier = Depends(get_rate_limit_tier)
):
    """
    Process request with Maria Quitéria agent.
    
    Maria Quitéria specializes in security auditing and system protection:
    - Security threat detection
    - Vulnerability assessment
    - Compliance verification (LGPD, ISO27001, etc.)
    - Intrusion detection
    - Digital forensics
    - Risk assessment
    - Security monitoring
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id=current_user.id if current_user else "anonymous",
            session_id=str(uuid4()),
            investigation_id=request.metadata.get("investigation_id", str(uuid4()))
        )
        
        # Get or create agent
        from src.agents import MariaQuiteriaAgent
        maria_quiteria = MariaQuiteriaAgent()
        
        # Process request
        result = await maria_quiteria.process(
            message=request.query,
            context=context,
            **request.options
        )
        
        return AgentResponse(
            agent="maria_quiteria",
            result=result.data if hasattr(result, 'data') else {"analysis": str(result)},
            metadata={
                "processing_time": result.metadata.get("processing_time", 0) if hasattr(result, 'metadata') else 0,
                "threats_detected": result.metadata.get("threats_detected", 0) if hasattr(result, 'metadata') else 0,
                "security_score": result.metadata.get("security_score", 0) if hasattr(result, 'metadata') else 0,
            },
            success=True,
            message="Security audit completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Maria Quiteria agent error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Maria Quiteria agent processing failed: {str(e)}"
        )


@router.get("/status")
async def get_agents_status(
    current_user: User = Depends(get_current_user)
):
    """Get status of all available agents."""
    agents = {
        "zumbi_dos_palmares": {
            "name": "Zumbi dos Palmares",
            "role": "Anomaly Detection Specialist",
            "status": "active",
            "capabilities": [
                "Price anomaly detection",
                "Vendor concentration analysis",
                "Temporal pattern recognition",
                "Contract duplication detection",
                "Payment irregularity identification"
            ]
        },
        "anita_garibaldi": {
            "name": "Anita Garibaldi", 
            "role": "Pattern Analysis Specialist",
            "status": "active",
            "capabilities": [
                "Spending trend analysis",
                "Organizational behavior mapping",
                "Vendor relationship analysis",
                "Seasonal pattern detection",
                "Efficiency metrics calculation"
            ]
        },
        "tiradentes": {
            "name": "Tiradentes",
            "role": "Report Generation Specialist",
            "status": "active",
            "capabilities": [
                "Executive summary generation",
                "Detailed investigation reports",
                "Multi-format output",
                "Natural language explanations",
                "Actionable recommendations"
            ]
        },
        "jose_bonifacio": {
            "name": "José Bonifácio",
            "role": "Legal & Compliance Specialist",
            "status": "active",
            "capabilities": [
                "Legal framework verification",
                "Compliance assessment",
                "Regulatory requirement checking",
                "Constitutional alignment analysis",
                "Legal risk identification"
            ]
        },
        "maria_quiteria": {
            "name": "Maria Quitéria",
            "role": "Security Auditor & System Guardian",
            "status": "active",
            "capabilities": [
                "Security threat detection",
                "Vulnerability assessment",
                "Compliance verification (LGPD, ISO27001)",
                "Intrusion detection",
                "Digital forensics",
                "Risk assessment"
            ]
        }
    }
    
    return {
        "agents": agents,
        "total_active": sum(1 for a in agents.values() if a["status"] == "active"),
        "timestamp": "2025-09-25T14:30:00Z"
    }


@router.get("/")
async def list_agents():
    """List all available agents with their endpoints."""
    return {
        "message": "Cidadão.AI Agent System",
        "version": "2.0.0",
        "agents": [
            {
                "name": "Zumbi dos Palmares",
                "endpoint": "/api/v1/agents/zumbi",
                "description": "Anomaly detection and investigation specialist"
            },
            {
                "name": "Anita Garibaldi",
                "endpoint": "/api/v1/agents/anita",
                "description": "Pattern analysis and correlation specialist"
            },
            {
                "name": "Tiradentes",
                "endpoint": "/api/v1/agents/tiradentes",
                "description": "Report generation and natural language specialist"
            },
            {
                "name": "José Bonifácio",
                "endpoint": "/api/v1/agents/bonifacio",
                "description": "Legal and compliance analysis specialist"
            },
            {
                "name": "Maria Quitéria",
                "endpoint": "/api/v1/agents/maria-quiteria",
                "description": "Security auditing and system protection specialist"
            }
        ]
    }