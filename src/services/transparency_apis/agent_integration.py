"""
Agent Integration for Transparency APIs

Provides integration layer between transparency APIs and investigation agents.
Enables agents (Zumbi, Anita, etc.) to seamlessly access transparency data.

Author: Anderson Henrique da Silva
Created: 2025-10-09 15:40:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime
from typing import Any, Optional

from .cache import get_cache
from .health_check import get_health_monitor
from .registry import registry
from .validators import AnomalyDetector, DataValidator


class TransparencyDataCollector:
    """
    Data collector for transparency APIs.

    Provides high-level methods for agents to collect transparency data
    across multiple sources with automatic caching, validation, and
    error handling.
    """

    def __init__(self):
        """Initialize transparency data collector."""
        self.cache = get_cache()
        self.health_monitor = get_health_monitor()

    async def _collect_from_single_api(
        self,
        api_key: str,
        year: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        municipality_code: Optional[str] = None,
        validate: bool = True,
        timeout: float = 15.0,
    ) -> dict[str, Any]:
        """
        Collect contracts from a single API with timeout protection.

        Args:
            api_key: API identifier
            year: Filter by year
            start_date: Start date
            end_date: End date
            municipality_code: Municipality code
            validate: Whether to validate data
            timeout: Timeout in seconds for this API

        Returns:
            Dict with contracts, source, and any errors
        """
        try:
            client = registry.get_client(api_key)
            if not client:
                return {"contracts": [], "source": None, "error": "Client not found"}

            # Check cache first
            cached_data = self.cache.get_contracts(
                api_key, year=year, municipality_code=municipality_code
            )

            if cached_data:
                return {
                    "contracts": cached_data,
                    "source": f"{api_key} (cached)",
                    "error": None,
                }

            # Fetch from API with timeout
            contracts = await asyncio.wait_for(
                client.get_contracts(
                    start_date=start_date,
                    end_date=end_date,
                    year=year,
                    municipality_code=municipality_code,
                ),
                timeout=timeout,
            )

            if contracts:
                # Validate if requested
                if validate:
                    validation = DataValidator.validate_batch(contracts, "contract")
                    if validation["validation_rate"] < 0.8:
                        return {
                            "contracts": contracts,
                            "source": api_key,
                            "error": f"Low validation rate: {validation['validation_rate']:.1%}",
                        }

                # Cache the results
                self.cache.set_contracts(
                    api_key,
                    contracts,
                    year=year,
                    municipality_code=municipality_code,
                )

                return {"contracts": contracts, "source": api_key, "error": None}

            return {"contracts": [], "source": None, "error": "No data returned"}

        except asyncio.TimeoutError:
            return {
                "contracts": [],
                "source": None,
                "error": f"Timeout after {timeout}s",
            }
        except Exception as e:
            return {"contracts": [], "source": None, "error": str(e)}

    async def collect_contracts(
        self,
        state: Optional[str] = None,
        municipality_code: Optional[str] = None,
        year: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        validate: bool = True,
        api_timeout: float = 15.0,
        global_timeout: float = 60.0,
    ) -> dict[str, Any]:
        """
        Collect contracts from available APIs in parallel.

        Args:
            state: State code (e.g., "PE", "CE")
            municipality_code: IBGE municipality code
            year: Filter by year
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            validate: Whether to validate data
            api_timeout: Timeout per API in seconds (default: 15s)
            global_timeout: Global timeout for all APIs in seconds (default: 60s)

        Returns:
            Dictionary with contracts and metadata
        """
        all_contracts = []
        sources_used = []
        errors = []

        # Determine which APIs to use
        api_keys = self._select_apis(state)

        # Create collection tasks for all APIs in parallel
        tasks = [
            self._collect_from_single_api(
                api_key=api_key,
                year=year,
                start_date=start_date,
                end_date=end_date,
                municipality_code=municipality_code,
                validate=validate,
                timeout=api_timeout,
            )
            for api_key in api_keys
        ]

        try:
            # Execute all API calls in parallel with global timeout
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True), timeout=global_timeout
            )

            # Process results
            for api_key, result in zip(api_keys, results, strict=False):
                if isinstance(result, Exception):
                    errors.append({"api": api_key, "error": str(result)})
                    continue

                if isinstance(result, dict):
                    if result.get("contracts"):
                        all_contracts.extend(result["contracts"])

                    if result.get("source"):
                        sources_used.append(result["source"])

                    if result.get("error"):
                        errors.append({"api": api_key, "error": result["error"]})

        except asyncio.TimeoutError:
            errors.append(
                {
                    "api": "global",
                    "error": f"Global timeout reached after {global_timeout}s",
                }
            )

        return {
            "contracts": all_contracts,
            "total": len(all_contracts),
            "sources": sources_used,
            "errors": errors,
            "metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "collection_mode": "parallel",
                "api_timeout": api_timeout,
                "global_timeout": global_timeout,
                "apis_attempted": len(api_keys),
                "apis_succeeded": len(sources_used),
                "apis_failed": len(errors),
                "filters": {
                    "state": state,
                    "municipality_code": municipality_code,
                    "year": year,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            },
        }

    async def collect_expenses(
        self,
        state: Optional[str] = None,
        municipality_code: Optional[str] = None,
        year: Optional[int] = None,
        validate: bool = True,
    ) -> dict[str, Any]:
        """
        Collect expenses from available APIs.

        Args:
            state: State code
            municipality_code: IBGE municipality code
            year: Filter by year
            validate: Whether to validate data

        Returns:
            Dictionary with expenses and metadata
        """
        all_expenses = []
        sources_used = []
        errors = []

        api_keys = self._select_apis(state)

        for api_key in api_keys:
            try:
                client = registry.get_client(api_key)
                if not client or not hasattr(client, "get_expenses"):
                    continue

                # Check cache
                cached_data = self.cache.get_expenses(
                    api_key, year=year, municipality_code=municipality_code
                )

                if cached_data:
                    all_expenses.extend(cached_data)
                    sources_used.append(f"{api_key} (cached)")
                    continue

                # Fetch from API
                expenses = await client.get_expenses(
                    year=year, municipality_code=municipality_code
                )

                if expenses:
                    if validate:
                        validation = DataValidator.validate_batch(expenses, "expense")
                        if validation["validation_rate"] < 0.8:
                            errors.append(
                                {
                                    "api": api_key,
                                    "error": f"Low validation rate: {validation['validation_rate']:.1%}",
                                }
                            )

                    self.cache.set_expenses(
                        api_key,
                        expenses,
                        year=year,
                        municipality_code=municipality_code,
                    )

                    all_expenses.extend(expenses)
                    sources_used.append(api_key)

            except Exception as e:
                errors.append({"api": api_key, "error": str(e)})

        return {
            "expenses": all_expenses,
            "total": len(all_expenses),
            "sources": sources_used,
            "errors": errors,
            "metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "filters": {
                    "state": state,
                    "municipality_code": municipality_code,
                    "year": year,
                },
            },
        }

    async def collect_suppliers(
        self,
        state: Optional[str] = None,
        municipality_code: Optional[str] = None,
        validate: bool = True,
    ) -> dict[str, Any]:
        """
        Collect suppliers from available APIs.

        Args:
            state: State code
            municipality_code: IBGE municipality code
            validate: Whether to validate data

        Returns:
            Dictionary with suppliers and metadata
        """
        all_suppliers = []
        sources_used = []
        errors = []

        api_keys = self._select_apis(state)

        for api_key in api_keys:
            try:
                client = registry.get_client(api_key)
                if not client or not hasattr(client, "get_suppliers"):
                    continue

                # Check cache
                cached_data = self.cache.get_suppliers(
                    api_key, municipality_code=municipality_code
                )

                if cached_data:
                    all_suppliers.extend(cached_data)
                    sources_used.append(f"{api_key} (cached)")
                    continue

                # Fetch from API
                suppliers = await client.get_suppliers(
                    municipality_code=municipality_code
                )

                if suppliers:
                    if validate:
                        validation = DataValidator.validate_batch(suppliers, "supplier")
                        if validation["validation_rate"] < 0.8:
                            errors.append(
                                {
                                    "api": api_key,
                                    "error": f"Low validation rate: {validation['validation_rate']:.1%}",
                                }
                            )

                    self.cache.set_suppliers(
                        api_key, suppliers, municipality_code=municipality_code
                    )

                    all_suppliers.extend(suppliers)
                    sources_used.append(api_key)

            except Exception as e:
                errors.append({"api": api_key, "error": str(e)})

        return {
            "suppliers": all_suppliers,
            "total": len(all_suppliers),
            "sources": sources_used,
            "errors": errors,
            "metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "filters": {"state": state, "municipality_code": municipality_code},
            },
        }

    async def analyze_contracts_for_anomalies(
        self, contracts: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Analyze contracts for anomalies.

        This method integrates with Zumbi agent's anomaly detection.

        Args:
            contracts: List of contracts to analyze

        Returns:
            Dictionary with anomaly analysis results
        """
        # Detect various types of anomalies
        outliers = AnomalyDetector.detect_value_outliers(contracts)
        concentration = AnomalyDetector.detect_supplier_concentration(contracts)
        duplicates = AnomalyDetector.detect_duplicate_contracts(contracts)

        # Calculate summary statistics
        total_value = sum(float(c.get("value", 0)) for c in contracts)
        avg_value = total_value / len(contracts) if contracts else 0

        # Determine risk score
        risk_factors = []
        risk_score = 0

        if len(outliers) > len(contracts) * 0.05:  # > 5% outliers
            risk_factors.append("High outlier rate")
            risk_score += 3

        if concentration.get("concentrated"):
            risk_factors.append("High supplier concentration")
            risk_score += 2

        if len(duplicates) > 0:
            risk_factors.append("Potential duplicate contracts")
            risk_score += 2

        # Normalize risk score to 0-10
        risk_score = min(risk_score, 10)

        return {
            "summary": {
                "total_contracts": len(contracts),
                "total_value": total_value,
                "avg_value": avg_value,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
            },
            "anomalies": {
                "outliers": outliers[:10],  # Top 10
                "outlier_count": len(outliers),
                "concentration": concentration,
                "duplicates": duplicates[:5],  # Top 5
                "duplicate_count": len(duplicates),
            },
            "metadata": {
                "analyzed_at": datetime.utcnow().isoformat(),
                "analysis_version": "1.0.0",
            },
        }

    async def check_apis_health(self) -> dict[str, Any]:
        """
        Check health of all transparency APIs.

        Returns:
            Health report for all APIs
        """
        return await self.health_monitor.generate_report()

    def _select_apis(self, state: Optional[str] = None) -> list[str]:
        """
        Select appropriate APIs based on state.

        Prioritizes Portal da Transparência Federal for national coverage,
        followed by state-specific APIs.

        Args:
            state: State code

        Returns:
            List of API keys to use (federal first, then state/municipal)
        """
        api_keys = []

        # Always include federal Portal da Transparência first (national coverage)
        api_keys.append("FEDERAL-portal")

        if state:
            # Get APIs for specific state
            api_keys.extend([f"{state}-tce", f"{state}-state", f"{state}-ckan"])
        else:
            # Return all available APIs (excluding federal portal since already added)
            api_keys.extend(
                [
                    key
                    for key in registry.list_available_apis()
                    if key != "FEDERAL-portal"
                ]
            )

        return api_keys


# Global collector instance
_global_collector: Optional[TransparencyDataCollector] = None


def get_transparency_collector() -> TransparencyDataCollector:
    """
    Get global transparency collector instance (singleton pattern).

    Returns:
        Global TransparencyDataCollector instance
    """
    global _global_collector

    if _global_collector is None:
        _global_collector = TransparencyDataCollector()

    return _global_collector
