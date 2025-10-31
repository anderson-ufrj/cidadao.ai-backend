"""
Module: api.routes.export
Description: Export endpoints for downloading investigations, reports and data
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from pydantic import Field as PydanticField
from pydantic import field_validator

from src.api.middleware.authentication import get_current_user
from src.core import get_logger, json_utils
from src.services.data_service import data_service
from src.services.export_service import export_service
from src.services.investigation_service_selector import investigation_service

logger = get_logger(__name__)

router = APIRouter()


class ExportRequest(BaseModel):
    """Request model for data export."""

    export_type: str = PydanticField(description="Type of data to export")
    format: str = PydanticField(description="Export format")
    filters: Optional[dict[str, Any]] = PydanticField(
        default={}, description="Filters to apply"
    )
    include_metadata: bool = PydanticField(default=True, description="Include metadata")
    compress: bool = PydanticField(default=False, description="Compress output")

    @field_validator("export_type")
    @classmethod
    def validate_export_type(cls, v):
        """Validate export type."""
        allowed_types = [
            "investigations",
            "contracts",
            "anomalies",
            "reports",
            "analytics",
            "full_data",
            "visualization",
            "regional_analysis",
            "time_series",
        ]
        if v not in allowed_types:
            raise ValueError(f"Export type must be one of: {allowed_types}")
        return v

    @field_validator("format")
    @classmethod
    def validate_format(cls, v):
        """Validate export format."""
        allowed_formats = ["excel", "csv", "json", "pdf"]
        if v not in allowed_formats:
            raise ValueError(f"Format must be one of: {allowed_formats}")
        return v


class BulkExportRequest(BaseModel):
    """Request model for bulk export."""

    exports: list[dict[str, Any]] = PydanticField(
        description="List of exports to generate"
    )
    compress: bool = PydanticField(default=True, description="Compress all exports")

    @field_validator("exports")
    @classmethod
    def validate_exports(cls, v):
        """Validate exports list."""
        if not v:
            raise ValueError("At least one export must be specified")
        if len(v) > 50:
            raise ValueError("Maximum 50 exports allowed per request")
        return v


@router.post("/investigations/{investigation_id}/download")
async def export_investigation(
    investigation_id: str,
    format: str = Query("excel", description="Export format: excel, csv, pdf, json"),
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Export investigation data in various formats.

    Exports complete investigation data including anomalies,
    contracts, and analysis results.
    """
    # Get investigation data
    investigation = await investigation_service.get_investigation(
        investigation_id, user_id=current_user.get("user_id")
    )

    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")

    filename = (
        f"investigation_{investigation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    if format == "excel":
        # Convert to Excel
        file_bytes = await export_service.convert_investigation_to_excel(investigation)

        return Response(
            content=file_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"},
        )

    elif format == "csv":
        # Create CSV with main data
        main_data = {
            "investigation_id": investigation["id"],
            "type": investigation["type"],
            "status": investigation["status"],
            "created_at": investigation["created_at"],
            "anomalies_count": len(investigation.get("anomalies", [])),
            "total_value": investigation.get("total_value", 0),
        }

        df = pd.DataFrame([main_data])
        csv_bytes = await export_service.generate_csv(df)

        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
        )

    elif format == "pdf":
        # Generate PDF report
        content = _format_investigation_as_markdown(investigation)
        pdf_bytes = await export_service.generate_pdf(
            content=content,
            title=f"Investigação {investigation_id}",
            metadata={
                "investigation_id": investigation_id,
                "generated_at": datetime.now().isoformat(),
                "user": current_user.get("email", "Unknown"),
            },
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}.pdf"},
        )

    elif format == "json":
        return Response(
            content=json_utils.dumps(investigation, indent=2, ensure_ascii=False),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}.json"},
        )

    else:
        raise HTTPException(status_code=400, detail="Unsupported format")


@router.post("/contracts/export")
async def export_contracts(
    request: ExportRequest, current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Export contract data with filters.

    Allows exporting filtered contract data in various formats.
    """
    # Apply filters
    filters = request.filters or {}

    # Get contracts data
    contracts = await data_service.search_contracts(
        **filters, limit=10000  # Reasonable limit for exports
    )

    if not contracts:
        raise HTTPException(
            status_code=404, detail="No contracts found with given filters"
        )

    filename = f"contracts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if request.format == "excel":
        # Convert to DataFrame
        df = pd.DataFrame(contracts)

        # Generate Excel with formatting
        excel_bytes = await export_service.generate_excel(
            data=df,
            title="Contratos - Portal da Transparência",
            metadata={
                "exported_at": datetime.now().isoformat(),
                "total_records": len(contracts),
                "filters": filters,
            },
        )

        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"},
        )

    elif request.format == "csv":
        df = pd.DataFrame(contracts)
        csv_bytes = await export_service.generate_csv(df)

        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
        )

    else:
        raise HTTPException(
            status_code=400, detail="Format not supported for contracts export"
        )


@router.post("/anomalies/export")
async def export_anomalies(
    request: ExportRequest, current_user: dict[str, Any] = Depends(get_current_user)
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
        user_id=current_user.get("user_id"), status="completed", limit=100
    )

    all_anomalies = []
    for inv in investigations:
        anomalies = inv.get("anomalies", [])
        for anomaly in anomalies:
            anomaly["investigation_id"] = inv["id"]
            all_anomalies.append(anomaly)

    if not all_anomalies:
        raise HTTPException(status_code=404, detail="No anomalies found")

    filename = f"anomalies_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if request.format == "excel":
        df = pd.DataFrame(all_anomalies)

        # Separate by severity
        high_severity = df[df["severity"] >= 0.7]
        medium_severity = df[(df["severity"] >= 0.4) & (df["severity"] < 0.7)]
        low_severity = df[df["severity"] < 0.4]

        dataframes = {
            "Alta Severidade": high_severity,
            "Média Severidade": medium_severity,
            "Baixa Severidade": low_severity,
            "Todas Anomalias": df,
        }

        excel_bytes = await export_service.generate_excel(
            data=dataframes,
            title="Anomalias Detectadas - Cidadão.AI",
            metadata={
                "exported_at": datetime.now().isoformat(),
                "total_anomalies": len(all_anomalies),
                "high_severity_count": len(high_severity),
                "medium_severity_count": len(medium_severity),
                "low_severity_count": len(low_severity),
            },
        )

        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"},
        )

    else:
        raise HTTPException(
            status_code=400, detail="Format not supported for anomalies export"
        )


@router.post("/bulk")
async def bulk_export(
    request: BulkExportRequest, current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Create bulk export with multiple files.

    Generates a ZIP file containing multiple exports.
    """
    exports_config = []

    for export in request.exports:
        export_type = export.get("type")
        export_format = export.get("format", "json")

        if export_type == "investigation":
            investigation = await investigation_service.get_investigation(
                export["id"], user_id=current_user.get("user_id")
            )

            if investigation:
                if export_format == "pdf":
                    content = _format_investigation_as_markdown(investigation)
                    exports_config.append(
                        {
                            "filename": f"investigation_{export['id']}.pdf",
                            "content": content,
                            "format": "pdf",
                            "title": f"Investigação {export['id']}",
                            "metadata": {"investigation_id": export["id"]},
                        }
                    )
                else:
                    exports_config.append(
                        {
                            "filename": f"investigation_{export['id']}.json",
                            "content": json_utils.dumps(investigation, indent=2),
                            "format": "json",
                        }
                    )

    if not exports_config:
        raise HTTPException(status_code=404, detail="No data found for bulk export")

    # Generate ZIP
    zip_bytes = await export_service.generate_bulk_export(exports_config)

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=bulk_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        },
    )


def _format_investigation_as_markdown(investigation: dict[str, Any]) -> str:
    """Format investigation data as markdown for PDF generation."""
    lines = []

    lines.append(f"# Investigação {investigation['id']}")
    lines.append("")
    lines.append(f"**Tipo**: {investigation.get('type', 'N/A')}")
    lines.append(f"**Status**: {investigation.get('status', 'N/A')}")
    lines.append(f"**Data de Criação**: {investigation.get('created_at', 'N/A')}")
    lines.append("")

    if investigation.get("summary"):
        lines.append("## Resumo")
        lines.append(investigation["summary"])
        lines.append("")

    anomalies = investigation.get("anomalies", [])
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


@router.post("/visualization/export")
async def export_visualization_data(
    request: ExportRequest, current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Export visualization data in optimized formats.

    Uses the Oscar Niemeyer agent to format data for charts and dashboards.
    Supports Excel with multiple sheets, CSV, and JSON formats.
    """
    from src.agents.deodoro import AgentContext
    from src.agents.oscar_niemeyer import OscarNiemeyerAgent
    from src.services.agent_lazy_loader import AgentLazyLoader

    agent_loader = AgentLazyLoader()

    # Get Oscar Niemeyer agent
    oscar_agent = await agent_loader.get_agent("oscar_niemeyer")
    if not oscar_agent:
        oscar_agent = OscarNiemeyerAgent()
        await oscar_agent.initialize()

    filename = f"visualization_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Get data based on filters
    filters = request.filters or {}
    dataset_type = filters.get("dataset_type", "contracts")
    time_range = filters.get("time_range", "30d")
    dimensions = filters.get("dimensions", ["category"])
    metrics = filters.get("metrics", ["total_value", "count"])

    # Create context for Oscar agent
    context = AgentContext(
        investigation_id=f"export_{uuid4()}",
        user_id=current_user.get("user_id"),
        session_id="export_session",
        metadata={"export_format": request.format},
    )

    # Get visualization data from Oscar
    from src.agents.deodoro import AgentMessage

    message = AgentMessage(
        role="user",
        content="Generate visualization data for export",
        type="visualization_metadata",
        data={
            "data_type": dataset_type,
            "dimensions": dimensions,
            "metrics": metrics,
            "time_range": time_range,
            "export": True,
        },
    )

    response = await oscar_agent.process(message, context)

    if not response.success:
        raise HTTPException(
            status_code=500, detail="Failed to generate visualization data"
        )

    viz_data = response.data

    if request.format == "excel":
        # Create multiple sheets for different visualizations
        dataframes = {}

        # Summary sheet
        summary_data = {
            "Metric": metrics,
            "Total": [1000000, 150],  # Placeholder values
            "Average": [50000, 7.5],
            "Min": [1000, 1],
            "Max": [500000, 50],
        }
        dataframes["Summary"] = pd.DataFrame(summary_data)

        # Time series data if applicable
        if hasattr(viz_data, "series"):
            series_data = []
            for series in viz_data.series:
                series_data.append(
                    {
                        "Series": series["name"],
                        "Field": series["field"],
                        "Type": series.get("type", "line"),
                    }
                )
            dataframes["Series Configuration"] = pd.DataFrame(series_data)

        # Dimensional breakdown
        if dimensions:
            dim_data = {
                "Dimension": dimensions,
                "Unique Values": [10, 5, 20],  # Placeholder
                "Coverage": ["100%", "95%", "100%"],
            }
            dataframes["Dimensions"] = pd.DataFrame(dim_data)

        excel_bytes = await export_service.generate_excel(
            data=dataframes,
            title=f"Visualization Data - {dataset_type}",
            metadata={
                "exported_at": datetime.now().isoformat(),
                "dataset_type": dataset_type,
                "time_range": time_range,
                "dimensions": dimensions,
                "metrics": metrics,
                "visualization_type": (
                    viz_data.visualization_type.value
                    if hasattr(viz_data, "visualization_type")
                    else "unknown"
                ),
            },
        )

        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"},
        )

    elif request.format == "csv":
        # For CSV, export a simplified flat structure
        export_data = await oscar_agent.create_export_format(
            data=[],  # Would contain actual data
            format_type="csv",
            options={"delimiter": ","},
        )

        return Response(
            content=export_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
        )

    elif request.format == "json":
        # For JSON, provide the full visualization specification
        export_data = await oscar_agent.create_export_format(
            data={
                "visualization": {
                    "type": (
                        viz_data.visualization_type.value
                        if hasattr(viz_data, "visualization_type")
                        else "unknown"
                    ),
                    "title": (
                        viz_data.title if hasattr(viz_data, "title") else "Data Export"
                    ),
                    "config": {
                        "x_axis": (
                            viz_data.x_axis if hasattr(viz_data, "x_axis") else {}
                        ),
                        "y_axis": (
                            viz_data.y_axis if hasattr(viz_data, "y_axis") else {}
                        ),
                        "series": (
                            viz_data.series if hasattr(viz_data, "series") else []
                        ),
                    },
                },
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "filters": filters,
                },
            },
            format_type="json",
            options={"pretty": True},
        )

        return Response(
            content=export_data,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}.json"},
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Format {request.format} not supported for visualization export",
        )


@router.post("/regional-analysis/export")
async def export_regional_analysis(
    request: ExportRequest, current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Export regional analysis data with geographic insights.

    Uses the Lampião agent to export regional disparities and clustering analysis.
    Includes inequality indices, regional rankings, and policy recommendations.
    """
    from src.agents.deodoro import AgentContext, AgentMessage
    from src.agents.lampiao import LampiaoAgent
    from src.services.agent_lazy_loader import AgentLazyLoader

    agent_loader = AgentLazyLoader()

    # Get Lampião agent
    lampiao_agent = await agent_loader.get_agent("lampiao")
    if not lampiao_agent:
        lampiao_agent = LampiaoAgent()
        await lampiao_agent.initialize()

    filename = f"regional_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Get parameters from filters
    filters = request.filters or {}
    metric = filters.get("metric", "government_spending")
    region_type = filters.get("region_type", "state")

    # Create context
    context = AgentContext(
        investigation_id=f"export_regional_{uuid4()}",
        user_id=current_user.get("user_id"),
        session_id="export_session",
        metadata={"export_format": request.format},
    )

    # Get regional analysis
    message = AgentMessage(
        role="user",
        content=f"Analyze regional distribution of {metric}",
        data={"metric": metric, "region_type": region_type, "export": True},
    )

    response = await lampiao_agent.process(message, context)

    if not response.success:
        raise HTTPException(
            status_code=500, detail="Failed to generate regional analysis"
        )

    regional_data = response.data

    if request.format == "excel":
        dataframes = {}

        # Regional metrics sheet
        metrics_data = []
        for metric in regional_data.metrics:
            metrics_data.append(
                {
                    "Region Code": metric.region_id,
                    "Region Name": metric.region_name,
                    "Value": metric.value,
                    "Normalized Value": metric.normalized_value,
                    "Rank": metric.rank,
                    "Percentile": metric.percentile,
                    "Population": metric.metadata.get("population", "N/A"),
                }
            )
        dataframes["Regional Data"] = pd.DataFrame(metrics_data)

        # Inequality indices
        inequality_data = {
            "Index": list(regional_data.inequalities.keys()),
            "Value": list(regional_data.inequalities.values()),
            "Interpretation": [
                (
                    "High inequality"
                    if v > 0.4
                    else "Moderate inequality" if v > 0.2 else "Low inequality"
                )
                for v in regional_data.inequalities.values()
            ],
        }
        dataframes["Inequality Analysis"] = pd.DataFrame(inequality_data)

        # Clusters
        if regional_data.clusters:
            cluster_data = []
            for cluster in regional_data.clusters:
                for region in cluster["regions"]:
                    cluster_data.append(
                        {
                            "Cluster": cluster["cluster_id"],
                            "Region": region,
                            "Avg Value": cluster["characteristics"].get(
                                "avg_value", "N/A"
                            ),
                        }
                    )
            dataframes["Regional Clusters"] = pd.DataFrame(cluster_data)

        # Recommendations
        rec_data = {
            "Recommendation": regional_data.recommendations,
            "Priority": ["High"] * min(2, len(regional_data.recommendations))
            + ["Medium"] * (len(regional_data.recommendations) - 2),
        }
        dataframes["Policy Recommendations"] = pd.DataFrame(rec_data)

        excel_bytes = await export_service.generate_excel(
            data=dataframes,
            title=f"Regional Analysis - {metric}",
            metadata={
                "exported_at": datetime.now().isoformat(),
                "metric": metric,
                "region_type": region_type,
                "regions_analyzed": regional_data.regions_analyzed,
                "analysis_type": regional_data.analysis_type.value,
            },
        )

        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"},
        )

    elif request.format == "csv":
        # For CSV, create a flat structure with all regional data
        csv_data = []
        for metric_data in regional_data.metrics:
            csv_data.append(
                {
                    "region_id": metric_data.region_id,
                    "region_name": metric_data.region_name,
                    "metric": metric,
                    "value": metric_data.value,
                    "normalized_value": metric_data.normalized_value,
                    "rank": metric_data.rank,
                    "percentile": metric_data.percentile,
                    "population": metric_data.metadata.get("population", 0),
                    "area_km2": metric_data.metadata.get("area", 0),
                    "gini_index": regional_data.inequalities.get("gini", 0),
                    "theil_index": regional_data.inequalities.get("theil_l", 0),
                    "analysis_type": regional_data.analysis_type.value,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        df = pd.DataFrame(csv_data)
        csv_bytes = await export_service.generate_csv(df)

        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
        )

    elif request.format == "json":
        # For JSON, provide complete structured data optimized for visualization
        export_data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "metric": metric,
                "region_type": region_type,
                "analysis_type": regional_data.analysis_type.value,
                "regions_analyzed": regional_data.regions_analyzed,
            },
            "data": {
                "regions": [
                    {
                        "id": m.region_id,
                        "name": m.region_name,
                        "value": m.value,
                        "normalized_value": m.normalized_value,
                        "rank": m.rank,
                        "percentile": m.percentile,
                        "metadata": m.metadata,
                    }
                    for m in regional_data.metrics
                ],
                "statistics": regional_data.statistics,
                "inequalities": regional_data.inequalities,
                "clusters": regional_data.clusters,
                "recommendations": [
                    {"text": rec, "priority": "high" if i < 2 else "medium"}
                    for i, rec in enumerate(regional_data.recommendations)
                ],
            },
            "visualization_hints": {
                "chart_type": "choropleth_map",
                "color_scale": "viridis",
                "value_field": "value",
                "region_id_field": "id",
                "tooltip_fields": ["name", "value", "rank", "percentile"],
            },
        }

        return Response(
            content=json_utils.dumps(export_data, indent=2, ensure_ascii=False),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}.json"},
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Format {request.format} not supported for regional analysis export",
        )


@router.post("/time-series/export")
async def export_time_series_data(
    request: ExportRequest, current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Export time series data optimized for visualization.

    Formats historical data, trends, and optionally forecasts
    in formats suitable for charting libraries.
    """
    from src.agents.deodoro import AgentContext
    from src.agents.oscar_niemeyer import OscarNiemeyerAgent, TimeGranularity
    from src.services.agent_lazy_loader import AgentLazyLoader

    agent_loader = AgentLazyLoader()

    # Get Oscar Niemeyer agent
    oscar_agent = await agent_loader.get_agent("oscar_niemeyer")
    if not oscar_agent:
        oscar_agent = OscarNiemeyerAgent()
        await oscar_agent.initialize()

    filename = f"time_series_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Get parameters from filters
    filters = request.filters or {}
    metric = filters.get("metric", "total_value")
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    granularity = filters.get("granularity", "day")
    include_forecast = filters.get("include_forecast", False)

    # Create context
    context = AgentContext(
        investigation_id=f"export_ts_{uuid4()}",
        user_id=current_user.get("user_id"),
        session_id="export_session",
        metadata={"export_format": request.format},
    )

    # Get time series data
    granularity_enum = (
        TimeGranularity[granularity.upper()]
        if granularity.upper() in TimeGranularity.__members__
        else TimeGranularity.DAY
    )
    time_series_data = await oscar_agent.generate_time_series(
        metric, start_date, end_date, granularity_enum, context
    )

    if request.format == "excel":
        # Create Excel with time series data
        dataframes = {}

        # Main time series data
        ts_data = []
        for i, (time_point, value) in enumerate(
            zip(time_series_data.time_points, time_series_data.values, strict=False)
        ):
            ts_data.append(
                {"Date": time_point, "Value": value, "Metric": metric, "Index": i}
            )
        dataframes["Time Series"] = pd.DataFrame(ts_data)

        # Summary statistics
        summary_data = {
            "Metric": metric,
            "Start Date": (
                time_series_data.time_points[0]
                if time_series_data.time_points
                else None
            ),
            "End Date": (
                time_series_data.time_points[-1]
                if time_series_data.time_points
                else None
            ),
            "Data Points": len(time_series_data.values),
            "Min Value": min(time_series_data.values) if time_series_data.values else 0,
            "Max Value": max(time_series_data.values) if time_series_data.values else 0,
            "Mean Value": (
                sum(time_series_data.values) / len(time_series_data.values)
                if time_series_data.values
                else 0
            ),
            "Granularity": granularity,
        }
        dataframes["Summary"] = pd.DataFrame([summary_data])

        excel_bytes = await export_service.generate_excel(
            data=dataframes,
            title=f"Time Series - {metric}",
            metadata={
                "exported_at": datetime.now().isoformat(),
                "metric": metric,
                "granularity": granularity,
                "data_points": len(ts_data),
            },
        )

        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"},
        )

    elif request.format == "csv":
        # Create CSV with time series data
        ts_data = []
        for time_point, value in zip(
            time_series_data.time_points, time_series_data.values, strict=False
        ):
            ts_data.append(
                {
                    "timestamp": time_point.isoformat(),
                    "value": value,
                    "metric": metric,
                    "granularity": granularity,
                }
            )

        df = pd.DataFrame(ts_data)
        csv_bytes = await export_service.generate_csv(df)

        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
        )

    elif request.format == "json":
        # JSON format optimized for charting libraries (Chart.js, D3.js, etc.)
        export_data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "metric": metric,
                "granularity": granularity,
                "aggregation_type": time_series_data.aggregation_type.value,
                "data_points": len(time_series_data.values),
            },
            "data": {
                "labels": [tp.isoformat() for tp in time_series_data.time_points],
                "datasets": [
                    {
                        "label": metric.replace("_", " ").title(),
                        "data": time_series_data.values,
                        "borderColor": "rgb(75, 192, 192)",
                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
                    }
                ],
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"{metric.replace('_', ' ').title()} - Time Series",
                    },
                    "tooltip": {"mode": "index", "intersect": False},
                },
                "scales": {
                    "x": {"display": True, "title": {"display": True, "text": "Date"}},
                    "y": {
                        "display": True,
                        "title": {
                            "display": True,
                            "text": metric.replace("_", " ").title(),
                        },
                    },
                },
            },
        }

        # Add forecast data if requested
        if include_forecast:
            # Simple forecast placeholder
            forecast_points = 7
            last_value = time_series_data.values[-1] if time_series_data.values else 0
            last_time = (
                time_series_data.time_points[-1]
                if time_series_data.time_points
                else datetime.utcnow()
            )

            forecast_labels = []
            forecast_values = []
            for i in range(forecast_points):
                if granularity == "day":
                    next_time = last_time + timedelta(days=i + 1)
                else:
                    next_time = last_time + timedelta(days=(i + 1) * 30)

                forecast_labels.append(next_time.isoformat())
                forecast_values.append(last_value * (1 + 0.02 * (i + 1)))

            export_data["data"]["datasets"].append(
                {
                    "label": "Forecast",
                    "data": forecast_values,
                    "borderColor": "rgb(255, 99, 132)",
                    "backgroundColor": "rgba(255, 99, 132, 0.2)",
                    "borderDash": [5, 5],
                }
            )

            # Extend labels for forecast
            export_data["data"]["labels"].extend(forecast_labels)

        return Response(
            content=json_utils.dumps(export_data, indent=2, ensure_ascii=False),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}.json"},
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Format {request.format} not supported for time series export",
        )
