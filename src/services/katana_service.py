"""
Module: services.katana_service
Description: Integration with Katana Scan API for dispensas de licitação
Author: Anderson H. Silva
Date: 2025-10-07
License: Proprietary - All rights reserved
"""

from datetime import datetime
from typing import Any, Optional

import httpx

from src.core.config import get_settings

settings = get_settings()


class KatanaService:
    """Service for integrating with Katana Scan API."""

    BASE_URL = "http://katanascan.xenoumena.com"
    AUTH_TOKEN = "qa5oAa2WvJl"

    def __init__(self):
        """Initialize Katana service."""
        self.base_url = self.BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.AUTH_TOKEN}",
            "Content-Type": "application/json",
        }

    async def get_all_dispensas(self) -> list[dict[str, Any]]:
        """
        Fetch all dispensas de licitação from Katana API.

        Returns:
            List of dispensas with sanitized data

        Raises:
            httpx.HTTPError: If request fails
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/get-all", headers=self.headers
            )
            response.raise_for_status()

            data = response.json()

            # Ensure we return a list
            if isinstance(data, dict):
                return data.get("data", [])
            elif isinstance(data, list):
                return data
            else:
                return []

    async def get_dispensa_by_id(self, dispensa_id: str) -> Optional[dict[str, Any]]:
        """
        Fetch a specific dispensa by ID.

        Args:
            dispensa_id: Unique identifier for the dispensa

        Returns:
            Dispensa data or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/dispensas/{dispensa_id}", headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def health_check(self) -> bool:
        """
        Check if Katana API is accessible.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/health", headers=self.headers
                )
                return response.status_code == 200
        except Exception:
            return False

    def format_dispensa_for_analysis(self, dispensa: dict[str, Any]) -> dict[str, Any]:
        """
        Format dispensa data for agent analysis.

        Args:
            dispensa: Raw dispensa data from API

        Returns:
            Formatted data ready for analysis
        """
        return {
            "id": dispensa.get("id"),
            "numero": dispensa.get("numero"),
            "objeto": dispensa.get("objeto", ""),
            "valor": float(dispensa.get("valor", 0)),
            "fornecedor": {
                "nome": dispensa.get("fornecedor", {}).get("nome", ""),
                "cnpj": dispensa.get("fornecedor", {}).get("cnpj", ""),
            },
            "orgao": {
                "nome": dispensa.get("orgao", {}).get("nome", ""),
                "codigo": dispensa.get("orgao", {}).get("codigo", ""),
            },
            "data": dispensa.get("data"),
            "justificativa": dispensa.get("justificativa", ""),
            "metadata": {
                "source": "katana_scan",
                "fetched_at": datetime.now().isoformat(),
                "original_data": dispensa,
            },
        }


async def get_katana_service() -> KatanaService:
    """Dependency injection for Katana service."""
    return KatanaService()
