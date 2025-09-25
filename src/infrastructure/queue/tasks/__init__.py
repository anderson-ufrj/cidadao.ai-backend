"""
Celery task modules for Cidadão.AI.

This package contains task definitions organized by domain:
- investigation_tasks: Investigation-related async tasks
- analysis_tasks: Data analysis and pattern detection tasks
- report_tasks: Report generation and processing tasks
- export_tasks: Document export tasks (PDF, Excel, CSV)
- monitoring_tasks: System monitoring and alerting tasks
"""

from .investigation_tasks import (
    run_investigation,
    analyze_contracts_batch,
    detect_anomalies_batch,
)

from .analysis_tasks import (
    analyze_patterns,
    correlation_analysis,
    temporal_analysis,
)

from .report_tasks import (
    generate_report,
    generate_executive_summary,
    batch_report_generation,
)

from .export_tasks import (
    export_to_pdf,
    export_to_excel,
    export_bulk_data,
)

from .monitoring_tasks import (
    monitor_anomalies,
    check_data_updates,
    send_alerts,
)

__all__ = [
    # Investigation tasks
    "run_investigation",
    "analyze_contracts_batch",
    "detect_anomalies_batch",
    
    # Analysis tasks
    "analyze_patterns",
    "correlation_analysis",
    "temporal_analysis",
    
    # Report tasks
    "generate_report",
    "generate_executive_summary",
    "batch_report_generation",
    
    # Export tasks
    "export_to_pdf",
    "export_to_excel",
    "export_bulk_data",
    
    # Monitoring tasks
    "monitor_anomalies",
    "check_data_updates",
    "send_alerts",
]