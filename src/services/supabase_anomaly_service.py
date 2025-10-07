"""
Module: services.supabase_anomaly_service
Description: Service for storing and managing anomalies in Supabase
Author: Anderson H. Silva
Date: 2025-10-07
License: Proprietary - All rights reserved
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
import httpx

from src.core.config import get_settings
from src.core import get_logger

settings = get_settings()
logger = get_logger(__name__)


class SupabaseAnomalyService:
    """Service for managing anomalies in Supabase."""

    def __init__(self):
        """Initialize Supabase service."""
        self.supabase_url = settings.supabase_url
        self.supabase_key = settings.supabase_service_role_key
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    async def create_investigation(
        self,
        query: str,
        context: Dict[str, Any],
        initiated_by: str
    ) -> Dict[str, Any]:
        """
        Create an investigation record in Supabase.

        Args:
            query: Investigation query
            context: Investigation context
            initiated_by: Who initiated the investigation

        Returns:
            Created investigation record
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.supabase_url}/rest/v1/investigations",
                headers=self.headers,
                json={
                    "query": query,
                    "context": context,
                    "initiated_by": initiated_by,
                    "status": "pending"
                }
            )
            response.raise_for_status()
            result = response.json()
            return result[0] if isinstance(result, list) else result

    async def create_anomaly(
        self,
        investigation_id: Optional[UUID],
        source: str,
        source_id: Optional[str],
        anomaly_type: str,
        anomaly_score: float,
        title: str,
        description: Optional[str],
        indicators: List[str],
        recommendations: List[str],
        contract_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an anomaly record in Supabase.

        Args:
            investigation_id: Related investigation ID
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

        Returns:
            Created anomaly record
        """
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
            "status": "detected"
        }

        # Add investigation_id if provided
        if investigation_id:
            anomaly_data["investigation_id"] = str(investigation_id)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.supabase_url}/rest/v1/anomalies",
                headers=self.headers,
                json=anomaly_data
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                "anomaly_created_in_supabase",
                anomaly_id=result[0]["id"] if isinstance(result, list) else result["id"],
                source=source,
                severity=severity,
                score=anomaly_score
            )

            return result[0] if isinstance(result, list) else result

    async def save_katana_dispensa(
        self,
        dispensa_id: str,
        dispensa_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save or update a Katana dispensa in Supabase.

        Args:
            dispensa_id: Dispensa unique identifier
            dispensa_data: Full dispensa data

        Returns:
            Saved dispensa record
        """
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
            "raw_data": dispensa_data
        }

        async with httpx.AsyncClient() as client:
            # Try to update first
            response = await client.post(
                f"{self.supabase_url}/rest/v1/katana_dispensas",
                headers={**self.headers, "Prefer": "resolution=merge-duplicates"},
                json=dispensa_record
            )
            response.raise_for_status()
            result = response.json()
            return result[0] if isinstance(result, list) else result

    async def get_anomalies(
        self,
        source: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
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
        params = {
            "limit": limit,
            "offset": offset,
            "order": "created_at.desc"
        }

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
                params=params
            )
            response.raise_for_status()
            return response.json()

    async def update_anomaly_status(
        self,
        anomaly_id: UUID,
        status: str,
        assigned_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update anomaly status.

        Args:
            anomaly_id: Anomaly ID
            status: New status
            assigned_to: Optional assignee

        Returns:
            Updated anomaly record
        """
        update_data = {"status": status}

        if assigned_to:
            update_data["assigned_to"] = assigned_to

        if status == "resolved":
            update_data["resolved_at"] = datetime.now().isoformat()

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.supabase_url}/rest/v1/anomalies?id=eq.{anomaly_id}",
                headers=self.headers,
                json=update_data
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
        recipients: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
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
        alert_data = {
            "anomaly_id": str(anomaly_id),
            "alert_type": alert_type,
            "severity": severity,
            "title": title,
            "message": message,
            "recipients": recipients,
            "status": "pending",
            "metadata": metadata or {}
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.supabase_url}/rest/v1/alerts",
                headers=self.headers,
                json=alert_data
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                "alert_created_in_supabase",
                alert_id=result[0]["id"] if isinstance(result, list) else result["id"],
                anomaly_id=str(anomaly_id),
                alert_type=alert_type
            )

            return result[0] if isinstance(result, list) else result

    async def get_investigation_summary(
        self,
        investigation_id: UUID
    ) -> Dict[str, Any]:
        """
        Get investigation summary with anomaly counts.

        Args:
            investigation_id: Investigation ID

        Returns:
            Investigation summary
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.supabase_url}/rest/v1/investigation_summary?id=eq.{investigation_id}",
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            return result[0] if result else {}


# Singleton instance
supabase_anomaly_service = SupabaseAnomalyService()
