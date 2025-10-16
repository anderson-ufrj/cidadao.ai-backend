"""
Module: services.supabase_anomaly_service
Description: Service for storing and managing anomalies in Supabase
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

settings = get_settings()
logger = get_logger(__name__)


class SupabaseAnomalyService:
    """Service for managing anomalies in Supabase."""

    def __init__(self):
        """Initialize Supabase service."""
        self.supabase_url = settings.supabase_url
        self.supabase_key = settings.supabase_service_role_key

        # Only initialize headers if Supabase is configured
        if self.supabase_url and self.supabase_key:
            key_value = (
                self.supabase_key.get_secret_value()
                if hasattr(self.supabase_key, "get_secret_value")
                else str(self.supabase_key)
            )
            self.headers = {
                "apikey": key_value,
                "Authorization": f"Bearer {key_value}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            }
        else:
            self.headers = None
            logger.warning(
                "Supabase not configured - SupabaseAnomalyService will not function. "
                "Add SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY for HuggingFace Spaces."
            )

    def _ensure_configured(self):
        """Ensure Supabase is configured before using the service."""
        if not self.supabase_url or not self.supabase_key or not self.headers:
            raise RuntimeError(
                "Supabase is not configured. "
                "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables."
            )

    async def create_auto_investigation(
        self, query: str, context: dict[str, Any], initiated_by: str
    ) -> dict[str, Any]:
        """
        Create an AUTO investigation record in Supabase (not user investigation).
        This is for 24/7 autonomous system investigations.

        Args:
            query: Investigation query
            context: Investigation context
            initiated_by: Who initiated (e.g., 'auto_investigation_katana')

        Returns:
            Created auto_investigation record
        """
        self._ensure_configured()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.supabase_url}/rest/v1/auto_investigations",
                headers=self.headers,
                json={
                    "query": query,
                    "context": context,
                    "initiated_by": initiated_by,
                    "status": "pending",
                },
            )
            response.raise_for_status()
            result = response.json()
            return result[0] if isinstance(result, list) else result

    async def create_anomaly(
        self,
        investigation_id: UUID | None,
        source: str,
        source_id: str | None,
        anomaly_type: str,
        anomaly_score: float,
        title: str,
        description: str | None,
        indicators: list[str],
        recommendations: list[str],
        contract_data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
        auto_investigation_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Create an anomaly record in Supabase.

        Args:
            investigation_id: Related user investigation ID (optional)
            source: Source system (portal_transparencia, katana_scan)
            source_id: ID from source system
            anomaly_type: Type of anomaly
            anomaly_score: Confidence score (0.0-1.0)
            title: Anomaly title
            description: Detailed description
            indicators: List of anomaly indicators
            recommendations: List of recommendations
            contract_data: Full contract/dispensa data
            metadata: Additional metadata
            auto_investigation_id: Related auto investigation ID (optional)

        Returns:
            Created anomaly record
        """
        self._ensure_configured()
        # Calculate severity based on score
        if anomaly_score >= 0.85:
            severity = "critical"
        elif anomaly_score >= 0.7:
            severity = "high"
        elif anomaly_score >= 0.5:
            severity = "medium"
        else:
            severity = "low"

        anomaly_data = {
            "source": source,
            "source_id": source_id,
            "anomaly_type": anomaly_type,
            "anomaly_score": float(anomaly_score),
            "severity": severity,
            "title": title,
            "description": description or "",
            "indicators": indicators,
            "recommendations": recommendations,
            "contract_data": contract_data,
            "metadata": metadata or {},
            "status": "detected",
        }

        # Add investigation_id if provided (user investigation)
        if investigation_id:
            anomaly_data["investigation_id"] = str(investigation_id)

        # Add auto_investigation_id if provided (system investigation)
        if auto_investigation_id:
            anomaly_data["auto_investigation_id"] = str(auto_investigation_id)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.supabase_url}/rest/v1/anomalies",
                headers=self.headers,
                json=anomaly_data,
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                "anomaly_created_in_supabase",
                anomaly_id=(
                    result[0]["id"] if isinstance(result, list) else result["id"]
                ),
                source=source,
                severity=severity,
                score=anomaly_score,
            )

            return result[0] if isinstance(result, list) else result

    async def save_katana_dispensa(
        self, dispensa_id: str, dispensa_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Save or update a Katana dispensa in Supabase.

        Args:
            dispensa_id: Dispensa unique identifier
            dispensa_data: Full dispensa data

        Returns:
            Saved dispensa record
        """
        self._ensure_configured()
        dispensa_record = {
            "id": dispensa_id,
            "numero": dispensa_data.get("numero"),
            "objeto": dispensa_data.get("objeto"),
            "valor": float(dispensa_data.get("valor", 0)),
            "fornecedor_nome": dispensa_data.get("fornecedor", {}).get("nome"),
            "fornecedor_cnpj": dispensa_data.get("fornecedor", {}).get("cnpj"),
            "orgao_nome": dispensa_data.get("orgao", {}).get("nome"),
            "orgao_codigo": dispensa_data.get("orgao", {}).get("codigo"),
            "data": dispensa_data.get("data"),
            "justificativa": dispensa_data.get("justificativa"),
            "raw_data": dispensa_data,
        }

        async with httpx.AsyncClient() as client:
            # Try to update first
            response = await client.post(
                f"{self.supabase_url}/rest/v1/katana_dispensas",
                headers={**self.headers, "Prefer": "resolution=merge-duplicates"},
                json=dispensa_record,
            )
            response.raise_for_status()
            result = response.json()
            return result[0] if isinstance(result, list) else result

    async def get_anomalies(
        self,
        source: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Get anomalies from Supabase with filters.

        Args:
            source: Filter by source
            severity: Filter by severity
            status: Filter by status
            limit: Maximum records to return
            offset: Pagination offset

        Returns:
            List of anomaly records
        """
        self._ensure_configured()
        params = {"limit": limit, "offset": offset, "order": "created_at.desc"}

        if source:
            params["source"] = f"eq.{source}"
        if severity:
            params["severity"] = f"eq.{severity}"
        if status:
            params["status"] = f"eq.{status}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.supabase_url}/rest/v1/anomalies",
                headers=self.headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def update_anomaly_status(
        self, anomaly_id: UUID, status: str, assigned_to: str | None = None
    ) -> dict[str, Any]:
        """
        Update anomaly status.

        Args:
            anomaly_id: Anomaly ID
            status: New status
            assigned_to: Optional assignee

        Returns:
            Updated anomaly record
        """
        self._ensure_configured()
        update_data = {"status": status}

        if assigned_to:
            update_data["assigned_to"] = assigned_to

        if status == "resolved":
            update_data["resolved_at"] = datetime.now().isoformat()

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.supabase_url}/rest/v1/anomalies?id=eq.{anomaly_id}",
                headers=self.headers,
                json=update_data,
            )
            response.raise_for_status()
            result = response.json()
            return result[0] if isinstance(result, list) else result

    async def create_alert(
        self,
        anomaly_id: UUID,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        recipients: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create an alert for an anomaly.

        Args:
            anomaly_id: Related anomaly ID
            alert_type: Type of alert (email, webhook, dashboard)
            severity: Alert severity
            title: Alert title
            message: Alert message
            recipients: List of recipients (emails or webhook URLs)
            metadata: Additional metadata

        Returns:
            Created alert record
        """
        self._ensure_configured()
        alert_data = {
            "anomaly_id": str(anomaly_id),
            "alert_type": alert_type,
            "severity": severity,
            "title": title,
            "message": message,
            "recipients": recipients,
            "status": "pending",
            "metadata": metadata or {},
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.supabase_url}/rest/v1/alerts",
                headers=self.headers,
                json=alert_data,
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                "alert_created_in_supabase",
                alert_id=result[0]["id"] if isinstance(result, list) else result["id"],
                anomaly_id=str(anomaly_id),
                alert_type=alert_type,
            )

            return result[0] if isinstance(result, list) else result

    async def get_investigation_summary(self, investigation_id: UUID) -> dict[str, Any]:
        """
        Get investigation summary with anomaly counts.

        Args:
            investigation_id: Investigation ID

        Returns:
            Investigation summary
        """
        self._ensure_configured()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.supabase_url}/rest/v1/investigation_summary?id=eq.{investigation_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            result = response.json()
            return result[0] if result else {}


# Singleton instance
supabase_anomaly_service = SupabaseAnomalyService()
