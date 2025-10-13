"""
Module: infrastructure.queue.tasks.export_tasks
Description: Celery tasks for document export operations
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from celery.utils.log import get_task_logger

from src.db.simple_session import get_db_session
from src.infrastructure.queue.celery_app import TaskPriority, celery_app, priority_task
from src.services.data_service import DataService
from src.services.export_service import ExportService

logger = get_task_logger(__name__)


@celery_app.task(name="tasks.export_to_pdf", bind=True, queue="normal")
def export_to_pdf(
    self, content_type: str, content_id: str, options: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """
    Export content to PDF format.

    Args:
        content_type: Type of content (report, investigation, analysis)
        content_id: ID of the content to export
        options: Export options

    Returns:
        Export results with file info
    """
    try:
        logger.info(
            "pdf_export_started", content_type=content_type, content_id=content_id
        )

        # Update progress
        self.update_state(state="PROGRESS", meta={"status": "Loading content..."})

        # Run export
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                _export_to_pdf_async(self, content_type, content_id, options)
            )

            logger.info("pdf_export_completed", file_size=result.get("file_size", 0))

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error("pdf_export_failed", error=str(e), exc_info=True)
        raise


async def _export_to_pdf_async(
    task, content_type: str, content_id: str, options: Optional[dict[str, Any]]
) -> dict[str, Any]:
    """Async PDF export implementation."""
    export_service = ExportService()

    async with get_db_session() as db:
        data_service = DataService(db)

        # Load content based on type
        if content_type == "report":
            content = await data_service.get_report(content_id)
            title = content.get("title", "Report")
            markdown = content.get("content", "")
        elif content_type == "investigation":
            content = await data_service.get_investigation(content_id)
            title = f"Investigation: {content.get('query', 'Unknown')}"
            markdown = await _format_investigation_markdown(content)
        else:
            raise ValueError(f"Unknown content type: {content_type}")

        # Update progress
        task.update_state(state="PROGRESS", meta={"status": "Generating PDF..."})

        # Generate PDF
        pdf_bytes = await export_service.generate_pdf(
            content=markdown,
            title=title,
            metadata={
                "content_type": content_type,
                "content_id": content_id,
                "generated_at": datetime.now().isoformat(),
            },
            format_type=content_type,
        )

        # Save to temporary location
        temp_path = Path(f"/tmp/{content_type}_{content_id}.pdf")
        with open(temp_path, "wb") as f:
            f.write(pdf_bytes)

        return {
            "content_type": content_type,
            "content_id": content_id,
            "file_path": str(temp_path),
            "file_size": len(pdf_bytes),
            "title": title,
            "pages": _estimate_pages(len(markdown)),
            "generated_at": datetime.now().isoformat(),
        }


@celery_app.task(name="tasks.export_to_excel", queue="normal")
def export_to_excel(
    data_type: str,
    filters: Optional[dict[str, Any]] = None,
    include_charts: bool = True,
) -> dict[str, Any]:
    """
    Export data to Excel format.

    Args:
        data_type: Type of data to export
        filters: Data filters
        include_charts: Whether to include charts

    Returns:
        Export results
    """
    logger.info(
        "excel_export_started", data_type=data_type, include_charts=include_charts
    )

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                _export_to_excel_async(data_type, filters, include_charts)
            )

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error("excel_export_failed", error=str(e), exc_info=True)
        raise


async def _export_to_excel_async(
    data_type: str, filters: Optional[dict[str, Any]], include_charts: bool
) -> dict[str, Any]:
    """Async Excel export implementation."""
    export_service = ExportService()

    async with get_db_session() as db:
        data_service = DataService(db)

        # Load data based on type
        data = []
        metadata = {"data_type": data_type}

        if data_type == "contracts":
            data = await data_service.get_contracts(filters or {})
            metadata["title"] = "Contract Analysis"
        elif data_type == "anomalies":
            data = await data_service.get_anomalies(filters or {})
            metadata["title"] = "Anomaly Detection Results"
        elif data_type == "suppliers":
            data = await data_service.get_suppliers(filters or {})
            metadata["title"] = "Supplier Analysis"
        else:
            raise ValueError(f"Unknown data type: {data_type}")

        # Generate Excel
        excel_bytes = await export_service.generate_excel(
            data=data, metadata=metadata, include_charts=include_charts
        )

        # Save to temporary location
        temp_path = Path(
            f"/tmp/{data_type}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        with open(temp_path, "wb") as f:
            f.write(excel_bytes)

        return {
            "data_type": data_type,
            "file_path": str(temp_path),
            "file_size": len(excel_bytes),
            "row_count": len(data),
            "include_charts": include_charts,
            "generated_at": datetime.now().isoformat(),
        }


@celery_app.task(name="tasks.export_bulk_data", queue="low")
def export_bulk_data(
    export_config: dict[str, Any], format: str = "csv"
) -> dict[str, Any]:
    """
    Export bulk data in specified format.

    Args:
        export_config: Configuration for bulk export
        format: Export format (csv, json, parquet)

    Returns:
        Bulk export results
    """
    logger.info(
        "bulk_export_started", format=format, datasets=list(export_config.keys())
    )

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                _export_bulk_data_async(export_config, format)
            )

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error("bulk_export_failed", error=str(e), exc_info=True)
        raise


async def _export_bulk_data_async(
    export_config: dict[str, Any], format: str
) -> dict[str, Any]:
    """Async bulk export implementation."""
    export_service = ExportService()

    async with get_db_session() as db:
        data_service = DataService(db)

        # Collect all data
        all_data = {}
        total_rows = 0

        for dataset_name, config in export_config.items():
            data_type = config.get("type")
            filters = config.get("filters", {})

            if data_type == "contracts":
                data = await data_service.get_contracts(filters)
            elif data_type == "anomalies":
                data = await data_service.get_anomalies(filters)
            elif data_type == "investigations":
                data = await data_service.get_investigations(filters)
            else:
                continue

            all_data[dataset_name] = data
            total_rows += len(data)

        # Generate bulk export
        if format == "csv":
            result = await export_service.generate_csv(
                data=all_data, metadata={"export_config": export_config}
            )
        else:
            result = await export_service.generate_bulk_export(
                data_sets=all_data,
                format=format,
                metadata={
                    "export_config": export_config,
                    "total_datasets": len(all_data),
                    "total_rows": total_rows,
                },
            )

        return {
            "format": format,
            "datasets": list(all_data.keys()),
            "total_rows": total_rows,
            "file_paths": result.get("file_paths", []),
            "total_size": result.get("total_size", 0),
            "generated_at": datetime.now().isoformat(),
        }


@priority_task(priority=TaskPriority.LOW)
def scheduled_export(
    export_name: str, schedule: str, config: dict[str, Any]
) -> dict[str, Any]:
    """
    Run scheduled data export.

    Args:
        export_name: Name of the export
        schedule: Schedule identifier
        config: Export configuration

    Returns:
        Export results
    """
    logger.info("scheduled_export_started", export_name=export_name, schedule=schedule)

    # Determine export type and run
    export_type = config.get("type", "bulk")

    if export_type == "pdf":
        result = export_to_pdf.apply_async(
            args=[config["content_type"], config["content_id"]],
            kwargs={"options": config.get("options")},
        ).get()
    elif export_type == "excel":
        result = export_to_excel.apply_async(
            args=[config["data_type"]],
            kwargs={
                "filters": config.get("filters"),
                "include_charts": config.get("include_charts", True),
            },
        ).get()
    else:
        result = export_bulk_data.apply_async(
            args=[config["export_config"]],
            kwargs={"format": config.get("format", "csv")},
        ).get()

    # Log completion
    logger.info("scheduled_export_completed", export_name=export_name, result=result)

    return {
        "export_name": export_name,
        "schedule": schedule,
        "result": result,
        "completed_at": datetime.now().isoformat(),
    }


async def _format_investigation_markdown(investigation: dict[str, Any]) -> str:
    """Format investigation data as markdown."""
    sections = []

    # Title and metadata
    sections.append("# Investigation Report")
    sections.append(f"\n**Query**: {investigation.get('query', 'N/A')}")
    sections.append(f"**Status**: {investigation.get('status', 'N/A')}")
    sections.append(f"**Started**: {investigation.get('started_at', 'N/A')}")

    # Findings
    if investigation.get("findings"):
        sections.append("\n## Key Findings")
        for finding in investigation["findings"]:
            sections.append(
                f"- **{finding.get('type', 'Finding')}**: {finding.get('description', 'N/A')}"
            )

    # Anomalies
    if investigation.get("anomalies"):
        sections.append("\n## Anomalies Detected")
        for anomaly in investigation["anomalies"]:
            sections.append(
                f"- **Severity {anomaly.get('severity', 'N/A')}**: {anomaly.get('description', 'N/A')}"
            )

    # Recommendations
    if investigation.get("recommendations"):
        sections.append("\n## Recommendations")
        for rec in investigation["recommendations"]:
            sections.append(f"- {rec}")

    return "\n".join(sections)


def _estimate_pages(content_length: int) -> int:
    """Estimate number of PDF pages based on content length."""
    # Rough estimate: ~3000 characters per page
    return max(1, content_length // 3000)
