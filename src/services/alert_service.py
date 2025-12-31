"""
Module: services.alert_service
Description: Service for sending alerts about detected anomalies
Author: Anderson H. Silva
Date: 2025-10-07
License: Proprietary - All rights reserved
"""

from datetime import datetime
from typing import Any
from uuid import UUID

import httpx

from src.core import get_logger
from src.core.config import get_settings
from src.services.email_service import send_template_email
from src.services.supabase_anomaly_service import supabase_anomaly_service

settings = get_settings()
logger = get_logger(__name__)


class AlertService:
    """Service for managing and sending alerts."""

    def __init__(self):
        """Initialize alert service."""
        self.webhook_urls = self._parse_webhook_urls()
        self.alert_emails = self._parse_alert_emails()

    def _parse_webhook_urls(self) -> list[str]:
        """Parse webhook URLs from environment."""
        webhooks_str = getattr(settings, "ALERT_WEBHOOKS", "")
        if not webhooks_str:
            return []
        return [url.strip() for url in webhooks_str.split(",") if url.strip()]

    def _parse_alert_emails(self) -> list[str]:
        """Parse alert email addresses from environment."""
        emails_str = getattr(settings, "ALERT_EMAILS", "")
        if not emails_str:
            return []
        return [email.strip() for email in emails_str.split(",") if email.strip()]

    async def send_anomaly_alert(
        self,
        anomaly_id: UUID,
        anomaly_data: dict[str, Any],
        alert_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Send alerts for a detected anomaly.

        Args:
            anomaly_id: Anomaly UUID
            anomaly_data: Full anomaly data
            alert_types: Types of alerts to send (email, webhook, dashboard)

        Returns:
            Summary of sent alerts
        """
        if alert_types is None:
            alert_types = ["webhook", "dashboard"]  # Default alert types

        results = {
            "anomaly_id": str(anomaly_id),
            "alerts_sent": [],
            "alerts_failed": [],
        }

        severity = anomaly_data.get("severity", "medium")
        title = anomaly_data.get("title", "Anomalia Detectada")

        # Generate alert message
        message = self._generate_alert_message(anomaly_data)

        # Send webhook alerts
        if "webhook" in alert_types and self.webhook_urls:
            for webhook_url in self.webhook_urls:
                try:
                    await self._send_webhook_alert(
                        webhook_url=webhook_url, anomaly_data=anomaly_data
                    )

                    # Record in Supabase
                    alert_record = await supabase_anomaly_service.create_alert(
                        anomaly_id=anomaly_id,
                        alert_type="webhook",
                        severity=severity,
                        title=title,
                        message=message,
                        recipients=[webhook_url],
                        metadata={"sent_at": datetime.now().isoformat()},
                    )

                    results["alerts_sent"].append(
                        {
                            "type": "webhook",
                            "destination": webhook_url,
                            "alert_id": alert_record["id"],
                        }
                    )

                    logger.info(
                        "webhook_alert_sent",
                        anomaly_id=str(anomaly_id),
                        webhook_url=webhook_url,
                    )

                except Exception as e:
                    logger.error(
                        "webhook_alert_failed",
                        anomaly_id=str(anomaly_id),
                        webhook_url=webhook_url,
                        error=str(e),
                    )
                    results["alerts_failed"].append(
                        {"type": "webhook", "destination": webhook_url, "error": str(e)}
                    )

        # Send email alerts (if configured)
        if "email" in alert_types and self.alert_emails:
            for email in self.alert_emails:
                try:
                    await self._send_email_alert(email=email, anomaly_data=anomaly_data)

                    # Record in Supabase
                    alert_record = await supabase_anomaly_service.create_alert(
                        anomaly_id=anomaly_id,
                        alert_type="email",
                        severity=severity,
                        title=title,
                        message=message,
                        recipients=[email],
                        metadata={"sent_at": datetime.now().isoformat()},
                    )

                    results["alerts_sent"].append(
                        {
                            "type": "email",
                            "destination": email,
                            "alert_id": alert_record["id"],
                        }
                    )

                    logger.info(
                        "email_alert_sent", anomaly_id=str(anomaly_id), email=email
                    )

                except Exception as e:
                    logger.error(
                        "email_alert_failed",
                        anomaly_id=str(anomaly_id),
                        email=email,
                        error=str(e),
                    )
                    results["alerts_failed"].append(
                        {"type": "email", "destination": email, "error": str(e)}
                    )

        # Dashboard alert (always create)
        if "dashboard" in alert_types:
            try:
                alert_record = await supabase_anomaly_service.create_alert(
                    anomaly_id=anomaly_id,
                    alert_type="dashboard",
                    severity=severity,
                    title=title,
                    message=message,
                    recipients=[],
                    metadata={
                        "created_at": datetime.now().isoformat(),
                        "auto_generated": True,
                    },
                )

                results["alerts_sent"].append(
                    {"type": "dashboard", "alert_id": alert_record["id"]}
                )

            except Exception as e:
                logger.error(
                    "dashboard_alert_failed", anomaly_id=str(anomaly_id), error=str(e)
                )
                results["alerts_failed"].append({"type": "dashboard", "error": str(e)})

        return results

    async def _send_webhook_alert(self, webhook_url: str, anomaly_data: dict[str, Any]):
        """Send webhook alert."""
        payload = {
            "event": "anomaly_detected",
            "timestamp": datetime.now().isoformat(),
            "anomaly": {
                "id": str(anomaly_data.get("id")),
                "title": anomaly_data.get("title"),
                "severity": anomaly_data.get("severity"),
                "score": float(anomaly_data.get("anomaly_score", 0)),
                "source": anomaly_data.get("source"),
                "type": anomaly_data.get("anomaly_type"),
                "description": anomaly_data.get("description"),
                "indicators": anomaly_data.get("indicators", []),
                "recommendations": anomaly_data.get("recommendations", []),
            },
            "contract": anomaly_data.get("contract_data", {}),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload, timeout=10.0)
            response.raise_for_status()

    async def _send_email_alert(self, email: str, anomaly_data: dict[str, Any]):
        """
        Send email alert using the configured email service.

        Uses the anomaly_alert template for HTML email formatting.
        Falls back to logging if email is not enabled.
        """
        # Check if email is enabled
        if not settings.email_enabled:
            logger.info(
                "email_alert_skipped",
                reason="email_disabled",
                recipient=email,
                anomaly_id=str(anomaly_data.get("id")),
            )
            return

        severity = anomaly_data.get("severity", "medium").upper()
        title = anomaly_data.get("title", "Anomalia Detectada")

        # Prepare template data
        template_data = {
            "anomaly_id": str(anomaly_data.get("id")),
            "title": title,
            "severity": severity,
            "severity_color": self._get_severity_color(severity),
            "score": float(anomaly_data.get("anomaly_score", 0)),
            "source": anomaly_data.get("source", "Desconhecido"),
            "anomaly_type": anomaly_data.get("anomaly_type", "N/A"),
            "description": anomaly_data.get("description", ""),
            "indicators": anomaly_data.get("indicators", []),
            "recommendations": anomaly_data.get("recommendations", []),
            "contract_data": anomaly_data.get("contract_data", {}),
            "detected_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }

        # Send email using template
        await send_template_email(
            to=email,
            subject=f"[{severity}] Alerta de Anomalia: {title}",
            template="anomaly_alert",
            template_data=template_data,
        )

        logger.info(
            "email_alert_sent",
            recipient=email,
            anomaly_id=str(anomaly_data.get("id")),
            severity=severity,
        )

    def _get_severity_color(self, severity: str) -> str:
        """Get color code for severity level."""
        colors = {
            "CRITICAL": "#dc3545",  # Red
            "HIGH": "#fd7e14",  # Orange
            "MEDIUM": "#ffc107",  # Yellow
            "LOW": "#28a745",  # Green
        }
        return colors.get(severity.upper(), "#6c757d")  # Gray default

    def _generate_alert_message(self, anomaly_data: dict[str, Any]) -> str:
        """Generate formatted alert message."""
        severity = anomaly_data.get("severity", "medium").upper()
        score = anomaly_data.get("anomaly_score", 0)
        source = anomaly_data.get("source", "unknown")
        title = anomaly_data.get("title", "Anomalia Detectada")

        message = f"""
🚨 ALERTA DE ANOMALIA - {severity}

{title}

📊 Score: {score:.4f}
📍 Fonte: {source}
🔍 Tipo: {anomaly_data.get('anomaly_type', 'N/A')}

{anomaly_data.get('description', '')}

⚠️ Indicadores:
{self._format_list(anomaly_data.get('indicators', []))}

💡 Recomendações:
{self._format_list(anomaly_data.get('recommendations', []))}

🔗 ID: {anomaly_data.get('id')}
⏰ Detectado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """.strip()

        return message

    def _format_list(self, items: list[str]) -> str:
        """Format list items for message."""
        if not items:
            return "- Nenhum"
        return "\n".join(f"- {item}" for item in items)

    async def send_critical_alert_summary(
        self, period_hours: int = 24
    ) -> dict[str, Any]:
        """
        Send summary of critical anomalies detected in the last N hours.

        Args:
            period_hours: Number of hours to look back

        Returns:
            Summary of sent alerts
        """
        # Get critical anomalies from Supabase
        anomalies = await supabase_anomaly_service.get_anomalies(
            severity="critical", limit=100
        )

        if not anomalies:
            logger.info("no_critical_anomalies_to_report")
            return {"summary_sent": False, "reason": "No critical anomalies detected"}

        # Generate summary
        summary_message = f"""
📊 RESUMO DE ANOMALIAS CRÍTICAS ({period_hours}h)

Total de anomalias críticas: {len(anomalies)}

Detalhes:
"""

        for anomaly in anomalies[:10]:  # Top 10
            summary_message += f"""
- {anomaly['title']} (Score: {anomaly['anomaly_score']:.4f})
  Fonte: {anomaly['source']} | ID: {anomaly['id']}
"""

        # Send to all webhook URLs
        results = {"webhooks_sent": 0, "webhooks_failed": 0}

        for webhook_url in self.webhook_urls:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        webhook_url,
                        json={
                            "event": "critical_anomalies_summary",
                            "period_hours": period_hours,
                            "total_critical": len(anomalies),
                            "message": summary_message,
                            "anomalies": [
                                {
                                    "id": str(a["id"]),
                                    "title": a["title"],
                                    "score": float(a["anomaly_score"]),
                                    "source": a["source"],
                                }
                                for a in anomalies[:10]
                            ],
                        },
                        timeout=10.0,
                    )
                results["webhooks_sent"] += 1
            except Exception as e:
                logger.error(
                    "summary_webhook_failed", webhook_url=webhook_url, error=str(e)
                )
                results["webhooks_failed"] += 1

        return results


# Singleton instance
alert_service = AlertService()
