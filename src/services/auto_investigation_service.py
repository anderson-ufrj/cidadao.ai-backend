"""
Module: services.auto_investigation_service
Description: Auto Investigation Service - 24/7 Contract Monitoring and Analysis
Author: Anderson Henrique da Silva
Date: 2025-10-07 18:11:37
License: Proprietary - All rights reserved

This service continuously monitors government contracts (new and historical)
and automatically triggers investigations when suspicious patterns are detected.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional

from src.agents import AgentContext, InvestigatorAgent
from src.config.system_users import SYSTEM_AUTO_MONITOR_USER_ID
from src.core import get_logger
from src.services.investigation_service_selector import investigation_service
from src.tools.transparency_api import TransparencyAPIClient, TransparencyAPIFilter

logger = get_logger(__name__)


class AutoInvestigationService:
    """
    Service for 24/7 automatic contract investigation.

    Features:
    - Monitors new contracts from Portal da Transparência
    - Re-analyzes historical contracts with updated ML models
    - Triggers investigations automatically on suspicious patterns
    - Learns from discovered patterns (unsupervised)
    """

    def __init__(self):
        """Initialize auto-investigation service."""
        self.transparency_api = TransparencyAPIClient()
        self.investigator = None

        # Thresholds for auto-triggering investigations
        self.value_threshold = 100000.0  # R$ 100k+
        self.daily_contract_limit = 500  # Max contracts to analyze per day

    async def _get_investigator(self) -> InvestigatorAgent:
        """Lazy load investigator agent."""
        if self.investigator is None:
            self.investigator = InvestigatorAgent()
        return self.investigator

    async def monitor_new_contracts(
        self, lookback_hours: int = 24, organization_codes: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """
        Monitor and investigate new contracts from the last N hours.

        Args:
            lookback_hours: How many hours back to look for new contracts
            organization_codes: Specific organizations to monitor

        Returns:
            Summary of monitoring results
        """
        logger.info(
            "auto_monitoring_started",
            lookback_hours=lookback_hours,
            org_count=len(organization_codes) if organization_codes else "all",
        )

        start_time = datetime.utcnow()

        try:
            # Build date filter
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(hours=lookback_hours)

            # Fetch recent contracts
            contracts = await self._fetch_recent_contracts(
                start_date=start_date,
                end_date=end_date,
                organization_codes=organization_codes,
            )

            logger.info(
                "contracts_fetched",
                count=len(contracts),
                date_range=f"{start_date.date()} to {end_date.date()}",
            )

            # Quick pre-screening
            suspicious_contracts = await self._pre_screen_contracts(contracts)

            logger.info(
                "contracts_pre_screened",
                total=len(contracts),
                suspicious=len(suspicious_contracts),
            )

            # Investigate suspicious contracts
            investigations = await self._investigate_batch(suspicious_contracts)

            duration = (datetime.utcnow() - start_time).total_seconds()

            result = {
                "monitoring_type": "new_contracts",
                "lookback_hours": lookback_hours,
                "contracts_analyzed": len(contracts),
                "suspicious_found": len(suspicious_contracts),
                "investigations_created": len(investigations),
                "anomalies_detected": sum(
                    len(inv.get("anomalies", [])) for inv in investigations
                ),
                "duration_seconds": duration,
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info("auto_monitoring_completed", **result)
            return result

        except Exception as e:
            logger.error("auto_monitoring_failed", error=str(e), exc_info=True)
            raise

    async def reanalyze_historical_contracts(
        self, months_back: int = 6, batch_size: int = 100
    ) -> dict[str, Any]:
        """
        Re-analyze historical contracts with updated detection models.

        This is useful after ML model improvements to find previously
        missed anomalies in historical data.

        Args:
            months_back: How many months of historical data to analyze
            batch_size: Number of contracts per batch

        Returns:
            Summary of reanalysis results
        """
        logger.info(
            "historical_reanalysis_started",
            months_back=months_back,
            batch_size=batch_size,
        )

        start_time = datetime.utcnow()

        try:
            # Build date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=months_back * 30)

            total_analyzed = 0
            total_investigations = 0
            total_anomalies = 0

            # Process in batches to avoid memory issues
            current_date = start_date
            batch_end_date = start_date + timedelta(days=7)  # Weekly batches

            while current_date < end_date:
                # Fetch batch
                contracts = await self._fetch_recent_contracts(
                    start_date=current_date,
                    end_date=min(batch_end_date, end_date),
                    limit=batch_size,
                )

                if not contracts:
                    current_date = batch_end_date
                    batch_end_date += timedelta(days=7)
                    continue

                # Pre-screen
                suspicious_contracts = await self._pre_screen_contracts(contracts)

                # Investigate
                if suspicious_contracts:
                    investigations = await self._investigate_batch(suspicious_contracts)
                    total_investigations += len(investigations)
                    total_anomalies += sum(
                        len(inv.get("anomalies", [])) for inv in investigations
                    )

                total_analyzed += len(contracts)

                logger.info(
                    "historical_batch_processed",
                    date_range=f"{current_date.date()} to {batch_end_date.date()}",
                    contracts=len(contracts),
                    suspicious=len(suspicious_contracts),
                )

                # Move to next batch
                current_date = batch_end_date
                batch_end_date += timedelta(days=7)

                # Rate limiting
                await asyncio.sleep(1)

            duration = (datetime.utcnow() - start_time).total_seconds()

            result = {
                "monitoring_type": "historical_reanalysis",
                "months_analyzed": months_back,
                "contracts_analyzed": total_analyzed,
                "investigations_created": total_investigations,
                "anomalies_detected": total_anomalies,
                "duration_seconds": duration,
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info("historical_reanalysis_completed", **result)
            return result

        except Exception as e:
            logger.error("historical_reanalysis_failed", error=str(e), exc_info=True)
            raise

    async def _fetch_recent_contracts(
        self,
        start_date: datetime,
        end_date: datetime,
        organization_codes: Optional[list[str]] = None,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        """Fetch contracts from Portal da Transparência."""
        try:
            filters = TransparencyAPIFilter(
                dataInicial=start_date.strftime("%d/%m/%Y"),
                dataFinal=end_date.strftime("%d/%m/%Y"),
            )

            # If specific organizations, fetch for each
            if organization_codes:
                all_contracts = []
                for org_code in organization_codes:
                    filters.codigoOrgao = org_code
                    contracts = await self.transparency_api.get_contracts(
                        filters=filters, limit=limit // len(organization_codes)
                    )
                    all_contracts.extend(contracts)
                return all_contracts
            else:
                # Fetch general contracts (may be limited by API)
                return await self.transparency_api.get_contracts(
                    filters=filters, limit=limit
                )

        except Exception as e:
            logger.warning(
                "contract_fetch_failed",
                error=str(e),
                date_range=f"{start_date.date()} to {end_date.date()}",
            )
            return []

    async def _pre_screen_contracts(
        self, contracts: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Quick pre-screening to identify potentially suspicious contracts.

        This reduces load by only fully investigating high-risk contracts.
        """
        suspicious = []

        for contract in contracts:
            suspicion_score = 0
            reasons = []

            # Check 1: High value
            valor = contract.get("valorInicial") or contract.get("valorGlobal") or 0
            if isinstance(valor, (int, float)) and valor > self.value_threshold:
                suspicion_score += 2
                reasons.append(f"high_value:{valor}")

            # Check 2: Emergency/waiver process
            modalidade = str(contract.get("modalidadeLicitacao", "")).lower()
            if "dispensa" in modalidade or "inexigibilidade" in modalidade:
                suspicion_score += 3
                reasons.append(f"emergency_process:{modalidade}")

            # Check 3: Single bidder
            num_proponentes = contract.get("numeroProponentes", 0)
            if num_proponentes == 1:
                suspicion_score += 2
                reasons.append("single_bidder")

            # Check 4: Short bidding period
            # (would need to parse dates - simplified here)

            # Check 5: Known problematic supplier
            # (would check against watchlist - placeholder)

            if suspicion_score >= 3:
                contract["_suspicion_score"] = suspicion_score
                contract["_suspicion_reasons"] = reasons
                suspicious.append(contract)

        return suspicious

    async def _investigate_batch(
        self, contracts: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Investigate a batch of suspicious contracts.

        Creates investigation records and runs full forensic analysis.
        """
        investigations = []
        investigator = await self._get_investigator()

        for contract in contracts:
            try:
                # Create investigation record
                investigation = await investigation_service.create(
                    user_id=SYSTEM_AUTO_MONITOR_USER_ID,
                    query=f"Auto-investigation: {contract.get('objeto', 'N/A')[:100]}",
                    data_source="contracts",
                    filters={
                        "contract_id": contract.get("id"),
                        "auto_triggered": True,
                        "suspicion_score": contract.get("_suspicion_score"),
                        "suspicion_reasons": contract.get("_suspicion_reasons", []),
                    },
                    anomaly_types=[
                        "price",
                        "vendor",
                        "temporal",
                        "payment",
                        "duplicate",
                    ],
                )

                investigation_id = (
                    investigation.id
                    if hasattr(investigation, "id")
                    else investigation["id"]
                )

                # Create agent context
                context = AgentContext(
                    conversation_id=investigation_id,
                    user_id=SYSTEM_AUTO_MONITOR_USER_ID,
                    session_data={
                        "auto_investigation": True,
                        "contract_data": contract,
                    },
                )

                # Run investigation
                anomalies = await investigator.investigate_anomalies(
                    query=f"Analyze contract {contract.get('id')}",
                    data_source="contracts",
                    filters=TransparencyAPIFilter(),
                    anomaly_types=["price", "vendor", "temporal", "payment"],
                    context=context,
                )

                # Update investigation with results
                if anomalies:
                    await investigation_service.update_status(
                        investigation_id=investigation_id,
                        status="completed",
                        progress=1.0,
                        results=[
                            {
                                "anomaly_type": a.anomaly_type,
                                "severity": a.severity,
                                "confidence": a.confidence,
                                "description": a.description,
                            }
                            for a in anomalies
                        ],
                        anomalies_found=len(anomalies),
                    )

                    investigations.append(
                        {
                            "investigation_id": investigation_id,
                            "contract_id": contract.get("id"),
                            "anomalies": [
                                {
                                    "type": a.anomaly_type,
                                    "severity": a.severity,
                                    "confidence": a.confidence,
                                }
                                for a in anomalies
                            ],
                        }
                    )

                    logger.info(
                        "auto_investigation_completed",
                        investigation_id=investigation_id,
                        contract_id=contract.get("id"),
                        anomalies_found=len(anomalies),
                    )
                else:
                    # No anomalies found
                    await investigation_service.update_status(
                        investigation_id=investigation_id,
                        status="completed",
                        progress=1.0,
                        results=[],
                        anomalies_found=0,
                    )

                # Rate limiting between investigations
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(
                    "auto_investigation_failed",
                    contract_id=contract.get("id"),
                    error=str(e),
                    exc_info=True,
                )
                continue

        return investigations


# Global service instance
auto_investigation_service = AutoInvestigationService()
