"""
Module: api.routes.reports
Description: Report generation endpoints for creating natural language reports
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, Response
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field as PydanticField, validator
import json

from src.core import get_logger
from src.agents import ReporterAgent, AgentContext
from src.api.middleware.authentication import get_current_user


logger = get_logger(__name__)

router = APIRouter()


class ReportRequest(BaseModel):
    """Request model for report generation."""
    
    report_type: str = PydanticField(description="Type of report to generate")
    title: str = PydanticField(description="Report title")
    data_sources: List[str] = PydanticField(description="Data sources to include")
    investigation_ids: List[str] = PydanticField(default=[], description="Investigation IDs to include")
    analysis_ids: List[str] = PydanticField(default=[], description="Analysis IDs to include")
    time_range: Dict[str, str] = PydanticField(description="Time range for the report")
    output_format: str = PydanticField(default="markdown", description="Output format")
    include_visualizations: bool = PydanticField(default=True, description="Include charts and graphs")
    include_raw_data: bool = PydanticField(default=False, description="Include raw data appendix")
    target_audience: str = PydanticField(default="general", description="Target audience")
    
    @validator('report_type')
    def validate_report_type(cls, v):
        """Validate report type."""
        allowed_types = [
            'executive_summary', 'detailed_analysis', 'investigation_report',
            'transparency_dashboard', 'comparative_analysis', 'audit_report'
        ]
        if v not in allowed_types:
            raise ValueError(f'Report type must be one of: {allowed_types}')
        return v
    
    @validator('output_format')
    def validate_output_format(cls, v):
        """Validate output format."""
        allowed_formats = ['markdown', 'html', 'json', 'pdf']
        if v not in allowed_formats:
            raise ValueError(f'Output format must be one of: {allowed_formats}')
        return v
    
    @validator('target_audience')
    def validate_target_audience(cls, v):
        """Validate target audience."""
        allowed_audiences = ['general', 'technical', 'executive', 'journalist', 'researcher']
        if v not in allowed_audiences:
            raise ValueError(f'Target audience must be one of: {allowed_audiences}')
        return v


class ReportResponse(BaseModel):
    """Response model for generated reports."""
    
    report_id: str
    title: str
    report_type: str
    output_format: str
    generated_at: datetime
    word_count: int
    status: str
    content: str
    metadata: Dict[str, Any]
    download_url: Optional[str] = None


class ReportStatus(BaseModel):
    """Report generation status."""
    
    report_id: str
    status: str
    progress: float
    current_phase: str
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None


# In-memory storage for report tracking
_active_reports: Dict[str, Dict[str, Any]] = {}


@router.post("/generate", response_model=Dict[str, str])
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate a new report.
    
    Creates and queues a report generation task that will create
    natural language reports from investigations and analyses.
    """
    report_id = str(uuid4())
    
    # Store report metadata
    _active_reports[report_id] = {
        "id": report_id,
        "status": "started",
        "title": request.title,
        "report_type": request.report_type,
        "output_format": request.output_format,
        "target_audience": request.target_audience,
        "data_sources": request.data_sources,
        "investigation_ids": request.investigation_ids,
        "analysis_ids": request.analysis_ids,
        "time_range": request.time_range,
        "user_id": current_user.get("user_id"),
        "started_at": datetime.utcnow(),
        "progress": 0.0,
        "current_phase": "initializing",
        "content": "",
        "metadata": {},
        "word_count": 0,
    }
    
    # Start report generation in background
    background_tasks.add_task(
        _generate_report,
        report_id,
        request
    )
    
    logger.info(
        "report_generation_started",
        report_id=report_id,
        report_type=request.report_type,
        title=request.title,
        user_id=current_user.get("user_id"),
    )
    
    return {
        "report_id": report_id,
        "status": "started",
        "message": "Report generation queued for processing"
    }


@router.get("/templates", response_model=List[Dict[str, Any]])
async def get_report_templates():
    """
    Get available report templates.
    
    Returns a list of predefined report templates with descriptions
    and required parameters.
    """
    templates = [
        {
            "type": "executive_summary",
            "name": "Relatório Executivo",
            "description": "Resumo executivo com principais achados e recomendações",
            "target_audience": "executive",
            "sections": ["resumo", "principais_achados", "recomendacoes", "proximos_passos"],
            "estimated_pages": "2-4",
        },
        {
            "type": "detailed_analysis",
            "name": "Análise Detalhada",
            "description": "Relatório técnico com análise aprofundada de dados",
            "target_audience": "technical",
            "sections": ["metodologia", "analise_dados", "descobertas", "conclusoes", "anexos"],
            "estimated_pages": "10-20",
        },
        {
            "type": "investigation_report",
            "name": "Relatório de Investigação",
            "description": "Relatório focado em anomalias e irregularidades encontradas",
            "target_audience": "journalist",
            "sections": ["contexto", "metodologia", "anomalias", "evidencias", "recomendacoes"],
            "estimated_pages": "5-15",
        },
        {
            "type": "transparency_dashboard",
            "name": "Dashboard de Transparência",
            "description": "Visão geral interativa dos dados de transparência",
            "target_audience": "general",
            "sections": ["metricas_principais", "graficos", "tendencias", "destaques"],
            "estimated_pages": "1-3",
        },
        {
            "type": "comparative_analysis",
            "name": "Análise Comparativa",
            "description": "Comparação entre diferentes períodos ou organizações",
            "target_audience": "researcher",
            "sections": ["baseline", "comparacao", "diferencas", "fatores", "insights"],
            "estimated_pages": "8-12",
        },
        {
            "type": "audit_report",
            "name": "Relatório de Auditoria",
            "description": "Relatório formal para auditores e órgãos de controle",
            "target_audience": "technical",
            "sections": ["escopo", "metodologia", "achados", "riscos", "recomendacoes", "resposta_gestao"],
            "estimated_pages": "15-30",
        }
    ]
    
    return templates


@router.get("/{report_id}/status", response_model=ReportStatus)
async def get_report_status(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get the current status of a report generation.
    
    Returns progress information and current phase.
    """
    if report_id not in _active_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = _active_reports[report_id]
    
    # Check user authorization
    if report["user_id"] != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ReportStatus(
        report_id=report_id,
        status=report["status"],
        progress=report["progress"],
        current_phase=report["current_phase"],
        estimated_completion=report.get("estimated_completion"),
        error_message=report.get("error_message"),
    )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a generated report.
    
    Returns the complete report content and metadata.
    """
    if report_id not in _active_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = _active_reports[report_id]
    
    # Check user authorization
    if report["user_id"] != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if report["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=409, detail="Report not yet completed")
    
    return ReportResponse(
        report_id=report_id,
        title=report["title"],
        report_type=report["report_type"],
        output_format=report["output_format"],
        generated_at=report.get("completed_at", report["started_at"]),
        word_count=report["word_count"],
        status=report["status"],
        content=report["content"],
        metadata=report["metadata"],
        download_url=f"/api/v1/reports/{report_id}/download" if report["status"] == "completed" else None
    )


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    format: str = Query("html", description="Download format"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Download a report in the specified format.
    
    Returns the report as a downloadable file.
    """
    if report_id not in _active_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = _active_reports[report_id]
    
    # Check user authorization
    if report["user_id"] != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if report["status"] != "completed":
        raise HTTPException(status_code=409, detail="Report not yet completed")
    
    content = report["content"]
    title = report["title"].replace(" ", "_")
    
    if format == "html":
        # Convert markdown to HTML if needed
        if report["output_format"] == "markdown":
            # TODO: Implement markdown to HTML conversion
            html_content = f"<html><body><h1>{report['title']}</h1><pre>{content}</pre></body></html>"
        else:
            html_content = content
        
        return HTMLResponse(
            content=html_content,
            headers={
                "Content-Disposition": f"attachment; filename={title}.html"
            }
        )
    
    elif format == "markdown":
        return Response(
            content=content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={title}.md"
            }
        )
    
    elif format == "json":
        json_content = {
            "report": report,
            "content": content,
            "metadata": report["metadata"]
        }
        
        return Response(
            content=json.dumps(json_content, indent=2, ensure_ascii=False),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={title}.json"
            }
        )
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")


@router.get("/", response_model=List[Dict[str, Any]])
async def list_reports(
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100, description="Number of reports to return"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List user's reports.
    
    Returns a list of reports owned by the current user.
    """
    user_id = current_user.get("user_id")
    
    # Filter reports by user
    user_reports = [
        report for report in _active_reports.values()
        if report["user_id"] == user_id
    ]
    
    # Filter by report type if provided
    if report_type:
        user_reports = [report for report in user_reports if report["report_type"] == report_type]
    
    # Filter by status if provided
    if status:
        user_reports = [report for report in user_reports if report["status"] == status]
    
    # Sort by start time (newest first)
    user_reports.sort(key=lambda x: x["started_at"], reverse=True)
    
    # Apply limit
    user_reports = user_reports[:limit]
    
    return [
        {
            "report_id": report["id"],
            "title": report["title"],
            "report_type": report["report_type"],
            "output_format": report["output_format"],
            "status": report["status"],
            "progress": report["progress"],
            "word_count": report["word_count"],
            "started_at": report["started_at"],
            "completed_at": report.get("completed_at"),
        }
        for report in user_reports
    ]


@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a report.
    
    Removes the report from storage.
    """
    if report_id not in _active_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = _active_reports[report_id]
    
    # Check user authorization
    if report["user_id"] != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Remove report
    del _active_reports[report_id]
    
    logger.info(
        "report_deleted",
        report_id=report_id,
        user_id=current_user.get("user_id"),
    )
    
    return {"message": "Report deleted successfully"}


async def _generate_report(report_id: str, request: ReportRequest):
    """
    Generate the report in the background.
    
    This function runs the actual report generation using ReporterAgent.
    """
    report = _active_reports[report_id]
    
    try:
        # Update status
        report["status"] = "running"
        report["current_phase"] = "data_collection"
        report["progress"] = 0.1
        
        # Create agent context
        context = AgentContext(
            conversation_id=report_id,
            user_id=report["user_id"],
            session_data={"report_type": request.report_type}
        )
        
        # Initialize ReporterAgent
        reporter = ReporterAgent()
        
        report["current_phase"] = "content_generation"
        report["progress"] = 0.3
        
        # Generate report content based on type
        if request.report_type == "executive_summary":
            content = await reporter.generate_executive_summary(
                investigation_ids=request.investigation_ids,
                analysis_ids=request.analysis_ids,
                time_range=request.time_range,
                context=context
            )
        elif request.report_type == "detailed_analysis":
            content = await reporter.generate_detailed_analysis(
                data_sources=request.data_sources,
                analysis_ids=request.analysis_ids,
                time_range=request.time_range,
                context=context
            )
        elif request.report_type == "investigation_report":
            content = await reporter.generate_investigation_report(
                investigation_ids=request.investigation_ids,
                include_evidence=True,
                context=context
            )
        else:
            content = await reporter.generate_custom_report(
                report_type=request.report_type,
                title=request.title,
                data_sources=request.data_sources,
                investigation_ids=request.investigation_ids,
                analysis_ids=request.analysis_ids,
                context=context
            )
        
        report["current_phase"] = "formatting"
        report["progress"] = 0.7
        
        # Format content according to output format
        if request.output_format == "html":
            formatted_content = await reporter.format_as_html(content, request.title)
        elif request.output_format == "json":
            formatted_content = await reporter.format_as_json(content, report)
        else:
            formatted_content = content  # Keep as markdown
        
        report["current_phase"] = "finalization"
        report["progress"] = 0.9
        
        # Calculate word count
        word_count = len(formatted_content.split())
        
        # Generate metadata
        metadata = {
            "sections_generated": content.count("#"),
            "data_sources_used": len(request.data_sources),
            "investigations_included": len(request.investigation_ids),
            "analyses_included": len(request.analysis_ids),
            "target_audience": request.target_audience,
            "generation_method": "ai_assisted",
        }
        
        # Store final results
        report["content"] = formatted_content
        report["word_count"] = word_count
        report["metadata"] = metadata
        
        # Mark as completed
        report["status"] = "completed"
        report["completed_at"] = datetime.utcnow()
        report["progress"] = 1.0
        report["current_phase"] = "completed"
        
        logger.info(
            "report_generated",
            report_id=report_id,
            report_type=request.report_type,
            word_count=word_count,
        )
        
    except Exception as e:
        logger.error(
            "report_generation_failed",
            report_id=report_id,
            error=str(e),
        )
        
        report["status"] = "failed"
        report["completed_at"] = datetime.utcnow()
        report["current_phase"] = "failed"
        report["error_message"] = str(e)