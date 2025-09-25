"""
Module: api.routes.export
Description: Export endpoints for downloading investigations, reports and data
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import io
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, Query, Response
from fastapi.responses import StreamingResponse
import pandas as pd
from pydantic import BaseModel, Field as PydanticField, validator

from src.core import json_utils
from src.core import get_logger
from src.api.middleware.authentication import get_current_user
from src.services.export_service import export_service
from src.services.investigation_service import investigation_service
from src.services.data_service import data_service

logger = get_logger(__name__)

router = APIRouter()


class ExportRequest(BaseModel):
    """Request model for data export."""
    
    export_type: str = PydanticField(description="Type of data to export")
    format: str = PydanticField(description="Export format")
    filters: Optional[Dict[str, Any]] = PydanticField(default={}, description="Filters to apply")
    include_metadata: bool = PydanticField(default=True, description="Include metadata")
    compress: bool = PydanticField(default=False, description="Compress output")
    
    @validator('export_type')
    def validate_export_type(cls, v):
        """Validate export type."""
        allowed_types = [
            'investigations', 'contracts', 'anomalies', 
            'reports', 'analytics', 'full_data'
        ]
        if v not in allowed_types:
            raise ValueError(f'Export type must be one of: {allowed_types}')
        return v
    
    @validator('format')
    def validate_format(cls, v):
        """Validate export format."""
        allowed_formats = ['excel', 'csv', 'json', 'pdf']
        if v not in allowed_formats:
            raise ValueError(f'Format must be one of: {allowed_formats}')
        return v


class BulkExportRequest(BaseModel):
    """Request model for bulk export."""
    
    exports: List[Dict[str, Any]] = PydanticField(description="List of exports to generate")
    compress: bool = PydanticField(default=True, description="Compress all exports")
    
    @validator('exports')
    def validate_exports(cls, v):
        """Validate exports list."""
        if not v:
            raise ValueError('At least one export must be specified')
        if len(v) > 50:
            raise ValueError('Maximum 50 exports allowed per request')
        return v


@router.post("/investigations/{investigation_id}/download")
async def export_investigation(
    investigation_id: str,
    format: str = Query("excel", description="Export format: excel, csv, pdf, json"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Export investigation data in various formats.
    
    Exports complete investigation data including anomalies, 
    contracts, and analysis results.
    """
    # Get investigation data
    investigation = await investigation_service.get_investigation(
        investigation_id, 
        user_id=current_user.get("user_id")
    )
    
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    filename = f"investigation_{investigation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if format == "excel":
        # Convert to Excel
        file_bytes = await export_service.convert_investigation_to_excel(investigation)
        
        return Response(
            content=file_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.xlsx"
            }
        )
    
    elif format == "csv":
        # Create CSV with main data
        main_data = {
            'investigation_id': investigation['id'],
            'type': investigation['type'],
            'status': investigation['status'],
            'created_at': investigation['created_at'],
            'anomalies_count': len(investigation.get('anomalies', [])),
            'total_value': investigation.get('total_value', 0),
        }
        
        df = pd.DataFrame([main_data])
        csv_bytes = await export_service.generate_csv(df)
        
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.csv"
            }
        )
    
    elif format == "pdf":
        # Generate PDF report
        content = _format_investigation_as_markdown(investigation)
        pdf_bytes = await export_service.generate_pdf(
            content=content,
            title=f"Investigação {investigation_id}",
            metadata={
                'investigation_id': investigation_id,
                'generated_at': datetime.now().isoformat(),
                'user': current_user.get('email', 'Unknown')
            }
        )
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.pdf"
            }
        )
    
    elif format == "json":
        return Response(
            content=json_utils.dumps(investigation, indent=2, ensure_ascii=False),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.json"
            }
        )
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")


@router.post("/contracts/export")
async def export_contracts(
    request: ExportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Export contract data with filters.
    
    Allows exporting filtered contract data in various formats.
    """
    # Apply filters
    filters = request.filters or {}
    
    # Get contracts data
    contracts = await data_service.search_contracts(
        **filters,
        limit=10000  # Reasonable limit for exports
    )
    
    if not contracts:
        raise HTTPException(status_code=404, detail="No contracts found with given filters")
    
    filename = f"contracts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if request.format == "excel":
        # Convert to DataFrame
        df = pd.DataFrame(contracts)
        
        # Generate Excel with formatting
        excel_bytes = await export_service.generate_excel(
            data=df,
            title="Contratos - Portal da Transparência",
            metadata={
                'exported_at': datetime.now().isoformat(),
                'total_records': len(contracts),
                'filters': filters
            }
        )
        
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.xlsx"
            }
        )
    
    elif request.format == "csv":
        df = pd.DataFrame(contracts)
        csv_bytes = await export_service.generate_csv(df)
        
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.csv"
            }
        )
    
    else:
        raise HTTPException(status_code=400, detail="Format not supported for contracts export")


@router.post("/anomalies/export")
async def export_anomalies(
    request: ExportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Export anomaly data with filters.
    
    Exports detected anomalies in various formats.
    """
    # Get anomalies from investigations
    filters = request.filters or {}
    
    # For now, get anomalies from recent investigations
    # In production, this would query a dedicated anomalies table
    investigations = await investigation_service.list_investigations(
        user_id=current_user.get("user_id"),
        status="completed",
        limit=100
    )
    
    all_anomalies = []
    for inv in investigations:
        anomalies = inv.get('anomalies', [])
        for anomaly in anomalies:
            anomaly['investigation_id'] = inv['id']
            all_anomalies.append(anomaly)
    
    if not all_anomalies:
        raise HTTPException(status_code=404, detail="No anomalies found")
    
    filename = f"anomalies_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if request.format == "excel":
        df = pd.DataFrame(all_anomalies)
        
        # Separate by severity
        high_severity = df[df['severity'] >= 0.7]
        medium_severity = df[(df['severity'] >= 0.4) & (df['severity'] < 0.7)]
        low_severity = df[df['severity'] < 0.4]
        
        dataframes = {
            'Alta Severidade': high_severity,
            'Média Severidade': medium_severity,
            'Baixa Severidade': low_severity,
            'Todas Anomalias': df
        }
        
        excel_bytes = await export_service.generate_excel(
            data=dataframes,
            title="Anomalias Detectadas - Cidadão.AI",
            metadata={
                'exported_at': datetime.now().isoformat(),
                'total_anomalies': len(all_anomalies),
                'high_severity_count': len(high_severity),
                'medium_severity_count': len(medium_severity),
                'low_severity_count': len(low_severity),
            }
        )
        
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.xlsx"
            }
        )
    
    else:
        raise HTTPException(status_code=400, detail="Format not supported for anomalies export")


@router.post("/bulk")
async def bulk_export(
    request: BulkExportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create bulk export with multiple files.
    
    Generates a ZIP file containing multiple exports.
    """
    exports_config = []
    
    for export in request.exports:
        export_type = export.get('type')
        export_format = export.get('format', 'json')
        
        if export_type == 'investigation':
            investigation = await investigation_service.get_investigation(
                export['id'],
                user_id=current_user.get("user_id")
            )
            
            if investigation:
                if export_format == 'pdf':
                    content = _format_investigation_as_markdown(investigation)
                    exports_config.append({
                        'filename': f"investigation_{export['id']}.pdf",
                        'content': content,
                        'format': 'pdf',
                        'title': f"Investigação {export['id']}",
                        'metadata': {'investigation_id': export['id']}
                    })
                else:
                    exports_config.append({
                        'filename': f"investigation_{export['id']}.json",
                        'content': json_utils.dumps(investigation, indent=2),
                        'format': 'json'
                    })
    
    if not exports_config:
        raise HTTPException(status_code=404, detail="No data found for bulk export")
    
    # Generate ZIP
    zip_bytes = await export_service.generate_bulk_export(exports_config)
    
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=bulk_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        }
    )


def _format_investigation_as_markdown(investigation: Dict[str, Any]) -> str:
    """Format investigation data as markdown for PDF generation."""
    lines = []
    
    lines.append(f"# Investigação {investigation['id']}")
    lines.append("")
    lines.append(f"**Tipo**: {investigation.get('type', 'N/A')}")
    lines.append(f"**Status**: {investigation.get('status', 'N/A')}")
    lines.append(f"**Data de Criação**: {investigation.get('created_at', 'N/A')}")
    lines.append("")
    
    if investigation.get('summary'):
        lines.append("## Resumo")
        lines.append(investigation['summary'])
        lines.append("")
    
    anomalies = investigation.get('anomalies', [])
    if anomalies:
        lines.append("## Anomalias Detectadas")
        lines.append("")
        lines.append(f"Total de anomalias: {len(anomalies)}")
        lines.append("")
        
        for i, anomaly in enumerate(anomalies, 1):
            lines.append(f"### Anomalia {i}")
            lines.append(f"**Tipo**: {anomaly.get('type', 'N/A')}")
            lines.append(f"**Severidade**: {anomaly.get('severity', 0):.2f}")
            lines.append(f"**Descrição**: {anomaly.get('description', 'N/A')}")
            lines.append(f"**Explicação**: {anomaly.get('explanation', 'N/A')}")
            lines.append("")
    
    return "\n".join(lines)