"""
Module: infrastructure.queue.tasks.analysis_tasks
Description: Celery tasks for data analysis and pattern detection
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional

import numpy as np
from celery import chord
from celery.utils.log import get_task_logger

from src.agents import get_agent_pool
from src.db.simple_session import get_db_session
from src.infrastructure.queue.celery_app import TaskPriority, celery_app, priority_task
from src.ml.pattern_analyzer import PatternAnalyzer
from src.services.data_service import DataService

logger = get_task_logger(__name__)


@celery_app.task(name="tasks.analyze_patterns", queue="normal")
def analyze_patterns(
    data_type: str,
    time_range: dict[str, str],
    pattern_types: Optional[list[str]] = None,
    min_confidence: float = 0.7,
) -> dict[str, Any]:
    """
    Analyze patterns in data.

    Args:
        data_type: Type of data to analyze
        time_range: Time range for analysis
        pattern_types: Specific patterns to look for
        min_confidence: Minimum confidence threshold

    Returns:
        Pattern analysis results
    """
    logger.info(
        "pattern_analysis_started",
        data_type=data_type,
        time_range=time_range,
        pattern_types=pattern_types,
    )

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                _analyze_patterns_async(
                    data_type, time_range, pattern_types, min_confidence
                )
            )

            logger.info(
                "pattern_analysis_completed",
                patterns_found=len(result.get("patterns", [])),
            )

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error("pattern_analysis_failed", error=str(e), exc_info=True)
        raise


async def _analyze_patterns_async(
    data_type: str,
    time_range: dict[str, str],
    pattern_types: Optional[list[str]],
    min_confidence: float,
) -> dict[str, Any]:
    """Async pattern analysis implementation."""
    async with get_db_session() as db:
        data_service = DataService(db)
        agent_pool = get_agent_pool()

        # Get Anita agent for pattern analysis
        anita = agent_pool.get_agent("anita")
        if not anita:
            raise RuntimeError("Pattern analysis agent not available")

        # Get data for analysis
        if data_type == "contracts":
            data = await data_service.get_contracts_in_range(
                start_date=time_range.get("start"), end_date=time_range.get("end")
            )
        elif data_type == "suppliers":
            data = await data_service.get_supplier_activity(
                start_date=time_range.get("start"), end_date=time_range.get("end")
            )
        else:
            raise ValueError(f"Unknown data type: {data_type}")

        # Run pattern analysis
        patterns = await anita.analyze_patterns(
            data=data,
            pattern_types=pattern_types or ["temporal", "value", "supplier"],
            min_confidence=min_confidence,
        )

        return {
            "data_type": data_type,
            "time_range": time_range,
            "total_records": len(data),
            "patterns": patterns,
            "analysis_timestamp": datetime.now().isoformat(),
        }


@celery_app.task(name="tasks.correlation_analysis", queue="normal")
def correlation_analysis(
    datasets: list[dict[str, Any]],
    correlation_type: str = "pearson",
    min_correlation: float = 0.7,
) -> dict[str, Any]:
    """
    Analyze correlations between datasets.

    Args:
        datasets: List of datasets to correlate
        correlation_type: Type of correlation (pearson, spearman, kendall)
        min_correlation: Minimum correlation threshold

    Returns:
        Correlation analysis results
    """
    logger.info(
        "correlation_analysis_started",
        dataset_count=len(datasets),
        correlation_type=correlation_type,
    )

    try:
        # Prepare data for correlation
        prepared_data = []
        for dataset in datasets:
            values = [float(item.get("value", 0)) for item in dataset.get("data", [])]
            prepared_data.append(values)

        # Calculate correlations
        correlations = []

        for i in range(len(prepared_data)):
            for j in range(i + 1, len(prepared_data)):
                if len(prepared_data[i]) == len(prepared_data[j]):
                    if correlation_type == "pearson":
                        corr = np.corrcoef(prepared_data[i], prepared_data[j])[0, 1]
                    else:
                        # Simplified for example
                        corr = np.corrcoef(prepared_data[i], prepared_data[j])[0, 1]

                    if abs(corr) >= min_correlation:
                        correlations.append(
                            {
                                "dataset1": datasets[i].get("name", f"Dataset {i}"),
                                "dataset2": datasets[j].get("name", f"Dataset {j}"),
                                "correlation": float(corr),
                                "strength": (
                                    "strong" if abs(corr) >= 0.8 else "moderate"
                                ),
                                "direction": "positive" if corr > 0 else "negative",
                            }
                        )

        return {
            "correlation_type": correlation_type,
            "datasets_analyzed": len(datasets),
            "significant_correlations": len(correlations),
            "correlations": correlations,
            "min_correlation": min_correlation,
        }

    except Exception as e:
        logger.error("correlation_analysis_failed", error=str(e), exc_info=True)
        raise


@celery_app.task(name="tasks.temporal_analysis", queue="normal")
def temporal_analysis(
    data_source: str, time_window: str = "monthly", metrics: Optional[list[str]] = None
) -> dict[str, Any]:
    """
    Analyze temporal trends and seasonality.

    Args:
        data_source: Source of temporal data
        time_window: Analysis window (daily, weekly, monthly, yearly)
        metrics: Specific metrics to analyze

    Returns:
        Temporal analysis results
    """
    logger.info(
        "temporal_analysis_started", data_source=data_source, time_window=time_window
    )

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                _temporal_analysis_async(data_source, time_window, metrics)
            )

            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error("temporal_analysis_failed", error=str(e), exc_info=True)
        raise


async def _temporal_analysis_async(
    data_source: str, time_window: str, metrics: Optional[list[str]]
) -> dict[str, Any]:
    """Async temporal analysis implementation."""
    async with get_db_session() as db:
        data_service = DataService(db)

        # Define time windows
        window_days = {"daily": 1, "weekly": 7, "monthly": 30, "yearly": 365}

        days = window_days.get(time_window, 30)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days * 12)  # 12 periods

        # Get temporal data
        if data_source == "contracts":
            data = await data_service.get_contracts_in_range(
                start_date=start_date.isoformat(), end_date=end_date.isoformat()
            )
        else:
            raise ValueError(f"Unknown data source: {data_source}")

        # Analyze trends
        pattern_analyzer = PatternAnalyzer()
        trends = await pattern_analyzer.predict(data)

        return {
            "data_source": data_source,
            "time_window": time_window,
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "trends": trends,
            "seasonality_detected": any(t.get("seasonal") for t in trends),
            "anomaly_periods": [t for t in trends if t.get("is_anomaly")],
        }


@priority_task(priority=TaskPriority.HIGH)
def complex_analysis_pipeline(
    investigation_id: str, analysis_config: dict[str, Any]
) -> dict[str, Any]:
    """
    Run complex analysis pipeline with multiple steps.

    Args:
        investigation_id: Investigation ID
        analysis_config: Analysis configuration

    Returns:
        Combined analysis results
    """
    logger.info(
        "complex_analysis_started",
        investigation_id=investigation_id,
        steps=list(analysis_config.keys()),
    )

    # Create analysis subtasks
    tasks = []

    if "patterns" in analysis_config:
        tasks.append(analyze_patterns.s(**analysis_config["patterns"]))

    if "correlations" in analysis_config:
        tasks.append(correlation_analysis.s(**analysis_config["correlations"]))

    if "temporal" in analysis_config:
        tasks.append(temporal_analysis.s(**analysis_config["temporal"]))

    # Execute in parallel and combine results
    callback = combine_analysis_results.s(investigation_id=investigation_id)
    job = chord(tasks)(callback)

    return job.get()


@celery_app.task(name="tasks.combine_analysis_results", queue="normal")
def combine_analysis_results(
    results: list[dict[str, Any]], investigation_id: str
) -> dict[str, Any]:
    """Combine multiple analysis results."""
    combined = {
        "investigation_id": investigation_id,
        "analysis_count": len(results),
        "timestamp": datetime.now().isoformat(),
        "results": {},
    }

    # Merge results by type
    for result in results:
        if "patterns" in result:
            combined["results"]["patterns"] = result
        elif "correlations" in result:
            combined["results"]["correlations"] = result
        elif "trends" in result:
            combined["results"]["temporal"] = result

    # Generate summary insights
    combined["summary"] = {
        "total_patterns": sum(
            len(r.get("patterns", [])) for r in results if "patterns" in r
        ),
        "significant_correlations": sum(
            r.get("significant_correlations", 0) for r in results if "correlations" in r
        ),
        "anomaly_periods": sum(
            len(r.get("anomaly_periods", [])) for r in results if "anomaly_periods" in r
        ),
    }

    logger.info(
        "analysis_combined",
        investigation_id=investigation_id,
        result_count=len(results),
    )

    return combined
