"""
Module: agents.oxossi
Codinome: Oxóssi - Caçador de Fraudes
Description: Agent specialized in fraud detection and tracking with precision hunting capabilities
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import pandas as pd

from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
    BaseAgent,
)
from src.core import get_logger
from src.core.exceptions import AgentExecutionError

logger = get_logger(__name__)


class FraudType(Enum):
    """Types of fraud detected by Oxóssi."""

    BID_RIGGING = "bid_rigging"
    PRICE_FIXING = "price_fixing"
    PHANTOM_VENDOR = "phantom_vendor"
    INVOICE_FRAUD = "invoice_fraud"
    KICKBACK_SCHEME = "kickback_scheme"
    CONFLICT_OF_INTEREST = "conflict_of_interest"
    MONEY_LAUNDERING = "money_laundering"
    FALSE_CLAIMS = "false_claims"
    PAYROLL_FRAUD = "payroll_fraud"
    PROCUREMENT_FRAUD = "procurement_fraud"


class FraudSeverity(Enum):
    """Severity levels for fraud detection."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FraudIndicator:
    """Individual fraud indicator detected."""

    indicator_type: str
    description: str
    confidence: float  # 0.0 to 1.0
    evidence: list[dict[str, Any]]
    risk_score: float  # 0.0 to 10.0


@dataclass
class FraudPattern:
    """Fraud pattern detection result."""

    fraud_type: FraudType
    severity: FraudSeverity
    confidence: float
    indicators: list[FraudIndicator]
    entities_involved: list[str]
    estimated_impact: float
    recommendations: list[str]
    evidence_trail: dict[str, Any]


class OxossiAgent(BaseAgent):
    """
    Oxóssi - The Fraud Hunter Agent.

    Specialized in detecting and tracking various types of fraud in government
    contracts and financial transactions with hunter-like precision.

    Cultural reference: Oxóssi is the Yoruba deity of the hunt, known for
    his precision, focus, and ability to track targets through any terrain.
    """

    def __init__(self):
        """Initialize Oxóssi agent."""
        super().__init__(
            name="oxossi",
            description="Fraud detection specialist with precision tracking capabilities",
            capabilities=[
                "fraud_detection",
                "pattern_recognition",
                "entity_relationship_analysis",
                "financial_forensics",
                "risk_assessment",
                "evidence_tracking",
            ],
        )

        # Fraud detection thresholds
        self.fraud_thresholds = {
            "bid_similarity": 0.85,  # Similarity threshold for bid rigging
            "price_deviation": 2.5,  # Standard deviations for price fixing
            "vendor_activity": 0.1,  # Minimum activity for legitimate vendor
            "invoice_anomaly": 0.7,  # Confidence threshold for invoice fraud
            "relationship_strength": 0.6,  # Threshold for suspicious relationships
        }

        # Known fraud patterns database
        self.fraud_patterns = self._initialize_fraud_patterns()

    @property
    def agent_id(self) -> str:
        """Return agent ID (name) for compatibility."""
        return self.name

    async def initialize(self):
        """Initialize agent and fraud detection systems."""
        await super().initialize()
        logger.info("Oxóssi agent initialized and ready to hunt fraud")

    async def shutdown(self):
        """Shutdown agent and cleanup resources."""
        await super().shutdown()
        logger.info("Oxóssi agent shutdown complete")

    def _initialize_fraud_patterns(self) -> dict[str, Any]:
        """Initialize known fraud pattern templates."""
        return {
            FraudType.BID_RIGGING: {
                "indicators": [
                    "identical_bid_amounts",
                    "sequential_bid_numbers",
                    "rotation_pattern",
                    "last_minute_withdrawals",
                ],
                "min_confidence": 0.7,
            },
            FraudType.PRICE_FIXING: {
                "indicators": [
                    "uniform_price_increases",
                    "identical_pricing_across_vendors",
                    "price_stability_anomaly",
                    "market_share_stability",
                ],
                "min_confidence": 0.65,
            },
            FraudType.PHANTOM_VENDOR: {
                "indicators": [
                    "no_physical_address",
                    "recent_registration",
                    "single_contract_only",
                    "no_web_presence",
                    "shared_contact_info",
                ],
                "min_confidence": 0.75,
            },
            FraudType.INVOICE_FRAUD: {
                "indicators": [
                    "duplicate_invoices",
                    "sequential_invoice_numbers",
                    "rounded_amounts",
                    "unusual_descriptions",
                    "timing_anomalies",
                ],
                "min_confidence": 0.7,
            },
        }

    async def process(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        """Process fraud detection request."""
        start_time = datetime.now()

        try:
            self.status = AgentStatus.THINKING
            logger.info(f"Oxóssi starting fraud hunt: {message.action}")

            # Extract data for analysis
            data = message.payload
            if not data:
                raise AgentExecutionError("No data provided for fraud detection")

            # Determine analysis type
            if "contracts" in data:
                fraud_patterns = await self._analyze_contract_fraud(
                    data["contracts"], context
                )
            elif "transactions" in data:
                fraud_patterns = await self._analyze_transaction_fraud(
                    data["transactions"], context
                )
            elif "vendors" in data:
                fraud_patterns = await self._analyze_vendor_fraud(
                    data["vendors"], context
                )
            elif "invoices" in data:
                fraud_patterns = await self._analyze_invoice_fraud(
                    data["invoices"], context
                )
            else:
                # Comprehensive fraud analysis
                fraud_patterns = await self._comprehensive_fraud_analysis(data, context)

            # Generate fraud report
            report = self._generate_fraud_report(fraud_patterns)

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            self.status = AgentStatus.IDLE

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result={
                    "fraud_analysis": report,
                    "patterns_detected": len(fraud_patterns),
                    "high_risk_entities": self._identify_high_risk_entities(
                        fraud_patterns
                    ),
                    "total_estimated_impact": sum(
                        p.estimated_impact for p in fraud_patterns
                    ),
                    "processing_time": processing_time,
                },
                metadata={
                    "agent": self.name,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "confidence_score": self._calculate_overall_confidence(
                        fraud_patterns
                    ),
                },
                processing_time_ms=processing_time * 1000,
            )

        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Oxóssi fraud detection failed: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.ERROR,
                error=str(e),
                metadata={"agent": self.name, "error_type": type(e).__name__},
            )

    async def _analyze_contract_fraud(
        self, contracts: list[dict[str, Any]], context: AgentContext
    ) -> list[FraudPattern]:
        """Analyze contracts for fraud patterns."""
        fraud_patterns = []

        # Check for bid rigging
        bid_rigging = await self._detect_bid_rigging(contracts)
        if bid_rigging:
            fraud_patterns.extend(bid_rigging)

        # Check for price fixing
        price_fixing = await self._detect_price_fixing(contracts)
        if price_fixing:
            fraud_patterns.extend(price_fixing)

        # Check for phantom vendors
        phantom_vendors = await self._detect_phantom_vendors(contracts)
        if phantom_vendors:
            fraud_patterns.extend(phantom_vendors)

        # Apply Benford's Law to contract values if enough data
        contract_values = [
            c.get("contract_value", 0) for c in contracts if c.get("contract_value")
        ]
        if len(contract_values) >= 30:
            benford_patterns = self._analyze_benfords_law(contract_values, "Contracts")
            fraud_patterns.extend(benford_patterns)

        # Apply temporal analysis to contracts
        temporal_patterns = self._detect_temporal_anomalies(contracts, "Contracts")
        fraud_patterns.extend(temporal_patterns)

        return fraud_patterns

    async def _detect_bid_rigging(
        self, contracts: list[dict[str, Any]]
    ) -> list[FraudPattern]:
        """Detect bid rigging patterns."""
        patterns = []

        # Group contracts by bidding process
        bidding_groups = {}
        for contract in contracts:
            bid_id = contract.get("bidding_process_id")
            if bid_id:
                if bid_id not in bidding_groups:
                    bidding_groups[bid_id] = []
                bidding_groups[bid_id].append(contract)

        # Analyze each bidding group
        for bid_id, group_contracts in bidding_groups.items():
            if len(group_contracts) < 3:  # Need multiple bids to detect rigging
                continue

            indicators = []

            # Check for identical or very similar bid amounts
            bid_amounts = [c.get("bid_amount", 0) for c in group_contracts]
            if self._check_bid_similarity(bid_amounts):
                indicators.append(
                    FraudIndicator(
                        indicator_type="identical_bid_amounts",
                        description="Multiple bids with identical or nearly identical amounts",
                        confidence=0.8,
                        evidence=[{"bid_amounts": bid_amounts}],
                        risk_score=7.5,
                    )
                )

            # Check for bid rotation patterns
            if self._check_bid_rotation(group_contracts):
                indicators.append(
                    FraudIndicator(
                        indicator_type="rotation_pattern",
                        description="Vendors appear to be taking turns winning bids",
                        confidence=0.75,
                        evidence=[{"pattern": "rotation_detected"}],
                        risk_score=8.0,
                    )
                )

            if indicators:
                patterns.append(
                    FraudPattern(
                        fraud_type=FraudType.BID_RIGGING,
                        severity=FraudSeverity.HIGH,
                        confidence=max(ind.confidence for ind in indicators),
                        indicators=indicators,
                        entities_involved=[
                            c.get("vendor_name", "Unknown") for c in group_contracts
                        ],
                        estimated_impact=sum(
                            c.get("contract_value", 0) for c in group_contracts
                        )
                        * 0.1,
                        recommendations=[
                            "Investigate bidding process for collusion",
                            "Review communications between vendors",
                            "Check for common ownership or management",
                        ],
                        evidence_trail={"bidding_process_id": bid_id},
                    )
                )

        return patterns

    async def _detect_phantom_vendors(
        self, contracts: list[dict[str, Any]]
    ) -> list[FraudPattern]:
        """Detect phantom vendor patterns."""
        patterns = []

        # Analyze vendors
        vendor_contracts = {}
        for contract in contracts:
            vendor_id = contract.get("vendor_id")
            if vendor_id:
                if vendor_id not in vendor_contracts:
                    vendor_contracts[vendor_id] = []
                vendor_contracts[vendor_id].append(contract)

        for vendor_id, vendor_contracts_list in vendor_contracts.items():
            indicators = []

            # Check for single contract vendors
            if len(vendor_contracts_list) == 1:
                indicators.append(
                    FraudIndicator(
                        indicator_type="single_contract_only",
                        description="Vendor has only one contract in the system",
                        confidence=0.6,
                        evidence=[{"contract_count": 1}],
                        risk_score=5.0,
                    )
                )

            # Check for recent registration before contract
            for contract in vendor_contracts_list:
                vendor_reg_date = contract.get("vendor_registration_date")
                contract_date = contract.get("contract_date")
                if vendor_reg_date and contract_date:
                    days_diff = (
                        pd.to_datetime(contract_date) - pd.to_datetime(vendor_reg_date)
                    ).days
                    if days_diff < 30:  # Registered less than 30 days before contract
                        indicators.append(
                            FraudIndicator(
                                indicator_type="recent_registration",
                                description="Vendor registered shortly before receiving contract",
                                confidence=0.7,
                                evidence=[{"days_before_contract": days_diff}],
                                risk_score=6.5,
                            )
                        )

            if indicators:
                patterns.append(
                    FraudPattern(
                        fraud_type=FraudType.PHANTOM_VENDOR,
                        severity=(
                            FraudSeverity.HIGH
                            if len(indicators) > 1
                            else FraudSeverity.MEDIUM
                        ),
                        confidence=max(ind.confidence for ind in indicators),
                        indicators=indicators,
                        entities_involved=[
                            vendor_contracts_list[0].get(
                                "vendor_name", f"Vendor_{vendor_id}"
                            )
                        ],
                        estimated_impact=sum(
                            c.get("contract_value", 0) for c in vendor_contracts_list
                        ),
                        recommendations=[
                            "Verify vendor physical existence",
                            "Check vendor registration details",
                            "Validate vendor tax records",
                            "Conduct site visits if necessary",
                        ],
                        evidence_trail={"vendor_id": vendor_id},
                    )
                )

        return patterns

    async def _detect_price_fixing(
        self, contracts: list[dict[str, Any]]
    ) -> list[FraudPattern]:
        """Detect price fixing patterns."""
        patterns = []

        # Group contracts by category/type
        category_contracts = {}
        for contract in contracts:
            category = contract.get("category", "Unknown")
            if category not in category_contracts:
                category_contracts[category] = []
            category_contracts[category].append(contract)

        for category, contracts_list in category_contracts.items():
            if len(contracts_list) < 5:  # Need sufficient data for price analysis
                continue

            # Extract prices and vendors
            price_data = []
            for contract in contracts_list:
                price_data.append(
                    {
                        "vendor": contract.get("vendor_name"),
                        "price": contract.get(
                            "unit_price", contract.get("contract_value", 0)
                        ),
                        "date": contract.get("contract_date"),
                    }
                )

            df = pd.DataFrame(price_data)
            if df.empty:
                continue

            indicators = []

            # Check for identical pricing across vendors
            price_groups = df.groupby("vendor")["price"].mean()
            if len(price_groups) > 1:
                price_variance = price_groups.std() / price_groups.mean()
                if price_variance < 0.05:  # Less than 5% variance
                    indicators.append(
                        FraudIndicator(
                            indicator_type="identical_pricing_across_vendors",
                            description="Multiple vendors have nearly identical pricing",
                            confidence=0.75,
                            evidence=[{"price_variance": price_variance}],
                            risk_score=7.0,
                        )
                    )

            # Check for synchronized price increases
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")

            # Group by time periods and check for uniform increases
            monthly_avg = df.groupby(pd.Grouper(key="date", freq="M"))["price"].mean()
            if len(monthly_avg) > 3:
                price_changes = monthly_avg.pct_change().dropna()
                if (price_changes > 0.05).sum() > 1:  # Multiple 5%+ increases
                    if price_changes.std() < 0.02:  # Very similar increase rates
                        indicators.append(
                            FraudIndicator(
                                indicator_type="uniform_price_increases",
                                description="Synchronized price increases across time periods",
                                confidence=0.7,
                                evidence=[{"price_increases": price_changes.to_list()}],
                                risk_score=6.5,
                            )
                        )

            if indicators:
                patterns.append(
                    FraudPattern(
                        fraud_type=FraudType.PRICE_FIXING,
                        severity=FraudSeverity.HIGH,
                        confidence=max(ind.confidence for ind in indicators),
                        indicators=indicators,
                        entities_involved=df["vendor"].unique().tolist(),
                        estimated_impact=df["price"].sum()
                        * 0.15,  # Estimated 15% overcharge
                        recommendations=[
                            "Compare prices with market rates",
                            "Investigate vendor communications",
                            "Review industry pricing trends",
                            "Consider antitrust investigation",
                        ],
                        evidence_trail={"category": category},
                    )
                )

        return patterns

    async def _analyze_transaction_fraud(
        self, transactions: list[dict[str, Any]], context: AgentContext
    ) -> list[FraudPattern]:
        """Analyze financial transactions for fraud."""
        patterns = []

        # Check for money laundering patterns
        laundering = await self._detect_money_laundering(transactions)
        if laundering:
            patterns.extend(laundering)

        # Check for kickback schemes
        kickbacks = await self._detect_kickback_schemes(transactions)
        if kickbacks:
            patterns.extend(kickbacks)

        return patterns

    async def _analyze_vendor_fraud(
        self, vendors: list[dict[str, Any]], context: AgentContext
    ) -> list[FraudPattern]:
        """Analyze vendor data for fraud patterns."""
        patterns = []

        # Check for shell companies
        for vendor in vendors:
            indicators = []

            # Check for shared addresses
            address = vendor.get("address")
            if address:
                same_address_vendors = [
                    v for v in vendors if v.get("address") == address
                ]
                if len(same_address_vendors) > 2:
                    indicators.append(
                        FraudIndicator(
                            indicator_type="shared_address",
                            description="Multiple vendors share the same address",
                            confidence=0.8,
                            evidence=[
                                {
                                    "vendors": [
                                        v.get("name") for v in same_address_vendors
                                    ]
                                }
                            ],
                            risk_score=7.0,
                        )
                    )

            # Check for shared contact information
            phone = vendor.get("phone")
            email = vendor.get("email")
            if phone or email:
                same_contact_vendors = [
                    v
                    for v in vendors
                    if (phone and v.get("phone") == phone)
                    or (email and v.get("email") == email)
                ]
                if len(same_contact_vendors) > 1:
                    indicators.append(
                        FraudIndicator(
                            indicator_type="shared_contact_info",
                            description="Multiple vendors share contact information",
                            confidence=0.85,
                            evidence=[
                                {
                                    "vendors": [
                                        v.get("name") for v in same_contact_vendors
                                    ]
                                }
                            ],
                            risk_score=8.0,
                        )
                    )

            if indicators:
                patterns.append(
                    FraudPattern(
                        fraud_type=FraudType.PHANTOM_VENDOR,
                        severity=FraudSeverity.HIGH,
                        confidence=max(ind.confidence for ind in indicators),
                        indicators=indicators,
                        entities_involved=[vendor.get("name", "Unknown")],
                        estimated_impact=0,  # Unknown until contracts analyzed
                        recommendations=[
                            "Investigate vendor relationships",
                            "Verify vendor legitimacy",
                            "Check for common ownership",
                        ],
                        evidence_trail={"vendor_id": vendor.get("id")},
                    )
                )

        return patterns

    async def _analyze_invoice_fraud(
        self, invoices: list[dict[str, Any]], context: AgentContext
    ) -> list[FraudPattern]:
        """Analyze invoices for fraud patterns."""
        patterns = []

        # Check for duplicate invoices
        invoice_hashes = {}
        for invoice in invoices:
            # Create hash of key invoice attributes
            hash_key = f"{invoice.get('vendor_id')}_{invoice.get('amount')}_{invoice.get('date')}"
            if hash_key in invoice_hashes:
                patterns.append(
                    FraudPattern(
                        fraud_type=FraudType.INVOICE_FRAUD,
                        severity=FraudSeverity.HIGH,
                        confidence=0.9,
                        indicators=[
                            FraudIndicator(
                                indicator_type="duplicate_invoices",
                                description="Duplicate invoice detected",
                                confidence=0.9,
                                evidence=[
                                    {
                                        "invoice_1": invoice_hashes[hash_key],
                                        "invoice_2": invoice.get("invoice_number"),
                                    }
                                ],
                                risk_score=8.5,
                            )
                        ],
                        entities_involved=[invoice.get("vendor_name", "Unknown")],
                        estimated_impact=invoice.get("amount", 0),
                        recommendations=[
                            "Reject duplicate invoice",
                            "Investigate vendor billing practices",
                            "Review payment controls",
                        ],
                        evidence_trail={
                            "invoice_numbers": [
                                invoice_hashes[hash_key],
                                invoice.get("invoice_number"),
                            ]
                        },
                    )
                )
            else:
                invoice_hashes[hash_key] = invoice.get("invoice_number")

        # Check for sequential invoice patterns
        vendor_invoices = {}
        for invoice in invoices:
            vendor_id = invoice.get("vendor_id")
            if vendor_id:
                if vendor_id not in vendor_invoices:
                    vendor_invoices[vendor_id] = []
                vendor_invoices[vendor_id].append(invoice)

        for vendor_id, vendor_invoice_list in vendor_invoices.items():
            # Sort by invoice number if numeric
            try:
                sorted_invoices = sorted(
                    vendor_invoice_list,
                    key=lambda x: int(x.get("invoice_number", "0").replace("-", "")),
                )

                # Check for suspicious sequential patterns
                invoice_numbers = [
                    int(inv.get("invoice_number", "0").replace("-", ""))
                    for inv in sorted_invoices
                ]
                if len(invoice_numbers) > 5:
                    # Check if all invoices are perfectly sequential
                    expected_sequence = list(
                        range(min(invoice_numbers), max(invoice_numbers) + 1)
                    )
                    if invoice_numbers == expected_sequence:
                        patterns.append(
                            FraudPattern(
                                fraud_type=FraudType.INVOICE_FRAUD,
                                severity=FraudSeverity.MEDIUM,
                                confidence=0.7,
                                indicators=[
                                    FraudIndicator(
                                        indicator_type="sequential_invoice_numbers",
                                        description="Perfectly sequential invoice numbers suggest manipulation",
                                        confidence=0.7,
                                        evidence=[
                                            {"sequence": invoice_numbers[:10]}
                                        ],  # First 10 as example
                                        risk_score=6.0,
                                    )
                                ],
                                entities_involved=[
                                    sorted_invoices[0].get(
                                        "vendor_name", f"Vendor_{vendor_id}"
                                    )
                                ],
                                estimated_impact=sum(
                                    inv.get("amount", 0) for inv in sorted_invoices
                                )
                                * 0.05,
                                recommendations=[
                                    "Audit vendor invoicing practices",
                                    "Verify actual services delivered",
                                    "Review invoice approval process",
                                ],
                                evidence_trail={"vendor_id": vendor_id},
                            )
                        )
            except:
                pass  # Skip if invoice numbers aren't numeric

        return patterns

    async def _comprehensive_fraud_analysis(
        self, data: dict[str, Any], context: AgentContext
    ) -> list[FraudPattern]:
        """Perform comprehensive fraud analysis across all data types."""
        all_patterns = []

        # Analyze each data type if present
        if "contracts" in data:
            patterns = await self._analyze_contract_fraud(data["contracts"], context)
            all_patterns.extend(patterns)

            # Apply Benford's Law to contract values
            contract_values = [
                c.get("contract_value", 0)
                for c in data["contracts"]
                if c.get("contract_value")
            ]
            if len(contract_values) >= 30:
                benford_patterns = self._analyze_benfords_law(
                    contract_values, "Contracts"
                )
                all_patterns.extend(benford_patterns)

            # Apply temporal analysis to contracts
            temporal_patterns = self._detect_temporal_anomalies(
                data["contracts"], "Contracts"
            )
            all_patterns.extend(temporal_patterns)

        if "transactions" in data:
            patterns = await self._analyze_transaction_fraud(
                data["transactions"], context
            )
            all_patterns.extend(patterns)

            # Apply Benford's Law to transaction amounts
            transaction_amounts = [
                t.get("amount", 0) for t in data["transactions"] if t.get("amount")
            ]
            if len(transaction_amounts) >= 30:
                benford_patterns = self._analyze_benfords_law(
                    transaction_amounts, "Transactions"
                )
                all_patterns.extend(benford_patterns)

            # Apply temporal analysis to transactions
            temporal_patterns = self._detect_temporal_anomalies(
                data["transactions"], "Transactions"
            )
            all_patterns.extend(temporal_patterns)

        if "vendors" in data:
            patterns = await self._analyze_vendor_fraud(data["vendors"], context)
            all_patterns.extend(patterns)

        if "invoices" in data:
            patterns = await self._analyze_invoice_fraud(data["invoices"], context)
            all_patterns.extend(patterns)

            # Apply Benford's Law to invoice amounts
            invoice_amounts = [
                inv.get("amount", 0) for inv in data["invoices"] if inv.get("amount")
            ]
            if len(invoice_amounts) >= 30:
                benford_patterns = self._analyze_benfords_law(
                    invoice_amounts, "Invoices"
                )
                all_patterns.extend(benford_patterns)

            # Apply temporal analysis to invoices
            temporal_patterns = self._detect_temporal_anomalies(
                data["invoices"], "Invoices"
            )
            all_patterns.extend(temporal_patterns)

        # Cross-reference patterns for complex fraud schemes
        complex_patterns = await self._detect_complex_fraud_schemes(all_patterns, data)
        all_patterns.extend(complex_patterns)

        return all_patterns

    async def _detect_money_laundering(
        self, transactions: list[dict[str, Any]]
    ) -> list[FraudPattern]:
        """Detect potential money laundering patterns."""
        patterns = []

        # Look for structuring (smurfing) patterns
        daily_transactions = {}
        for trans in transactions:
            date = trans.get("date", "").split("T")[0]  # Extract date part
            entity = trans.get("entity_id")
            amount = trans.get("amount", 0)

            key = f"{date}_{entity}"
            if key not in daily_transactions:
                daily_transactions[key] = []
            daily_transactions[key].append(amount)

        # Check for multiple transactions just below reporting threshold
        threshold = 10000  # Common reporting threshold
        for key, amounts in daily_transactions.items():
            if len(amounts) > 2:  # Multiple transactions in one day
                below_threshold = [
                    a for a in amounts if threshold * 0.8 < a < threshold
                ]
                if len(below_threshold) >= 2:
                    patterns.append(
                        FraudPattern(
                            fraud_type=FraudType.MONEY_LAUNDERING,
                            severity=FraudSeverity.HIGH,
                            confidence=0.75,
                            indicators=[
                                FraudIndicator(
                                    indicator_type="structuring",
                                    description="Multiple transactions just below reporting threshold",
                                    confidence=0.75,
                                    evidence=[{"transactions": below_threshold}],
                                    risk_score=8.0,
                                )
                            ],
                            entities_involved=[key.split("_")[1]],
                            estimated_impact=sum(below_threshold),
                            recommendations=[
                                "File suspicious activity report",
                                "Review all transactions by entity",
                                "Check for related accounts",
                            ],
                            evidence_trail={"date_entity": key},
                        )
                    )

        return patterns

    async def _detect_kickback_schemes(
        self, transactions: list[dict[str, Any]]
    ) -> list[FraudPattern]:
        """
        Detect potential kickback schemes.

        Kickbacks are illegal payments made to government officials or decision-makers
        in exchange for favorable treatment in contract awards or procurement processes.

        Detection patterns:
        - Payments shortly after contract awards
        - Round-number payments to officials
        - Transfers between vendors and public officials
        - Payments to shell companies linked to officials
        """
        patterns = []

        if not transactions or len(transactions) < 2:
            return patterns

        # Convert to DataFrame for analysis
        df = pd.DataFrame(transactions)

        # Look for suspicious payment timing (within 30 days after contract award)
        contract_transactions = (
            df[df.get("transaction_type") == "contract_award"].copy()
            if "transaction_type" in df.columns
            else pd.DataFrame()
        )
        payment_transactions = (
            df[df.get("transaction_type") == "payment"].copy()
            if "transaction_type" in df.columns
            else df.copy()
        )

        if not contract_transactions.empty and not payment_transactions.empty:
            # Ensure date columns are datetime
            if "date" in contract_transactions.columns:
                contract_transactions["date"] = pd.to_datetime(
                    contract_transactions["date"], errors="coerce"
                )
            if "date" in payment_transactions.columns:
                payment_transactions["date"] = pd.to_datetime(
                    payment_transactions["date"], errors="coerce"
                )

            for _, contract in contract_transactions.iterrows():
                contract_date = contract.get("date")
                vendor_id = contract.get("vendor_id")
                contract_value = contract.get("amount", 0)

                if pd.isna(contract_date):
                    continue

                # Find payments within 30 days after contract award
                suspicious_payments = payment_transactions[
                    (payment_transactions["date"] > contract_date)
                    & (
                        payment_transactions["date"]
                        <= contract_date + pd.Timedelta(days=30)
                    )
                ].copy()

                if suspicious_payments.empty:
                    continue

                indicators = []

                # Check for round-number payments (common in kickbacks)
                for _, payment in suspicious_payments.iterrows():
                    amount = payment.get("amount", 0)

                    # Round numbers (divisible by 1000, 5000, 10000)
                    if amount > 0 and (amount % 10000 == 0 or amount % 5000 == 0):
                        # Check if payment is to an individual (not a company)
                        recipient_type = payment.get("recipient_type", "")
                        if recipient_type in ["individual", "person", "employee"]:
                            indicators.append(
                                FraudIndicator(
                                    indicator_type="suspicious_round_payment",
                                    description=f"Round-number payment of {amount} to individual within 30 days of contract award",
                                    confidence=0.75,
                                    evidence=[
                                        {
                                            "payment_amount": amount,
                                            "days_after_contract": (
                                                payment["date"] - contract_date
                                            ).days,
                                            "recipient_id": payment.get("recipient_id"),
                                            "contract_id": contract.get("contract_id"),
                                        }
                                    ],
                                    risk_score=7.5,
                                )
                            )

                    # Check for payments that are percentage of contract (e.g., 5%, 10%)
                    if contract_value > 0:
                        percentage = (amount / contract_value) * 100
                        common_kickback_percentages = [5, 10, 15, 20, 25]

                        for pct in common_kickback_percentages:
                            if abs(percentage - pct) < 0.5:  # Within 0.5%
                                indicators.append(
                                    FraudIndicator(
                                        indicator_type="percentage_payment",
                                        description=f"Payment is exactly {pct}% of contract value",
                                        confidence=0.8,
                                        evidence=[
                                            {
                                                "payment_amount": amount,
                                                "contract_value": contract_value,
                                                "percentage": round(percentage, 2),
                                                "days_after_contract": (
                                                    payment["date"] - contract_date
                                                ).days,
                                            }
                                        ],
                                        risk_score=8.5,
                                    )
                                )
                                break

                # Check for payments to related entities
                for _, payment in suspicious_payments.iterrows():
                    recipient_id = payment.get("recipient_id")
                    payer_id = payment.get("payer_id")

                    # Check if payer is the vendor who won the contract
                    if payer_id == vendor_id:
                        # Payment from vendor who just won contract
                        indicators.append(
                            FraudIndicator(
                                indicator_type="vendor_payment_after_award",
                                description="Payment from vendor shortly after winning contract",
                                confidence=0.7,
                                evidence=[
                                    {
                                        "vendor_id": vendor_id,
                                        "recipient_id": recipient_id,
                                        "payment_amount": payment.get("amount"),
                                        "days_after_contract": (
                                            payment["date"] - contract_date
                                        ).days,
                                    }
                                ],
                                risk_score=7.0,
                            )
                        )

                if indicators:
                    patterns.append(
                        FraudPattern(
                            fraud_type=FraudType.KICKBACK_SCHEME,
                            severity=(
                                FraudSeverity.CRITICAL
                                if len(indicators) > 2
                                else FraudSeverity.HIGH
                            ),
                            confidence=max(ind.confidence for ind in indicators),
                            indicators=indicators,
                            entities_involved=[
                                vendor_id,
                                *[
                                    p.get("recipient_id")
                                    for _, p in suspicious_payments.iterrows()
                                    if p.get("recipient_id")
                                ],
                            ],
                            estimated_impact=contract_value
                            * 0.1,  # Estimated 10% kickback
                            recommendations=[
                                "Investigate relationship between vendor and payment recipients",
                                "Review contract award decision-making process",
                                "Check for conflicts of interest",
                                "Analyze financial records of involved parties",
                                "Consider law enforcement referral",
                            ],
                            evidence_trail={
                                "contract_id": contract.get("contract_id"),
                                "contract_date": str(contract_date),
                                "suspicious_payment_count": len(suspicious_payments),
                            },
                        )
                    )

        # Look for circular payment patterns (A pays B, B pays C, C pays A)
        circular_patterns = self._detect_circular_payments(transactions)
        if circular_patterns:
            patterns.extend(circular_patterns)

        return patterns

    async def _detect_complex_fraud_schemes(
        self, patterns: list[FraudPattern], data: dict[str, Any]
    ) -> list[FraudPattern]:
        """Detect complex fraud schemes involving multiple fraud types."""
        complex_patterns = []

        # Look for entities involved in multiple fraud types
        entity_fraud_types = {}
        for pattern in patterns:
            for entity in pattern.entities_involved:
                if entity not in entity_fraud_types:
                    entity_fraud_types[entity] = set()
                entity_fraud_types[entity].add(pattern.fraud_type)

        # Entities with multiple fraud types indicate complex schemes
        for entity, fraud_types in entity_fraud_types.items():
            if len(fraud_types) >= 2:
                # Combine evidence from all patterns involving this entity
                entity_patterns = [p for p in patterns if entity in p.entities_involved]

                complex_patterns.append(
                    FraudPattern(
                        fraud_type=FraudType.PROCUREMENT_FRAUD,  # Complex multi-type fraud
                        severity=FraudSeverity.CRITICAL,
                        confidence=0.85,
                        indicators=[
                            FraudIndicator(
                                indicator_type="complex_scheme",
                                description=f"Entity involved in multiple fraud types: {', '.join(f.value for f in fraud_types)}",
                                confidence=0.85,
                                evidence=[
                                    {"fraud_types": [f.value for f in fraud_types]}
                                ],
                                risk_score=9.5,
                            )
                        ],
                        entities_involved=[entity],
                        estimated_impact=sum(
                            p.estimated_impact for p in entity_patterns
                        ),
                        recommendations=[
                            "Launch comprehensive investigation",
                            "Freeze entity accounts",
                            "Coordinate with law enforcement",
                            "Review all entity transactions and contracts",
                        ],
                        evidence_trail={
                            "related_patterns": [
                                p.fraud_type.value for p in entity_patterns
                            ]
                        },
                    )
                )

        return complex_patterns

    def _check_bid_similarity(self, bid_amounts: list[float]) -> bool:
        """Check if bids are suspiciously similar."""
        if len(bid_amounts) < 2:
            return False

        # Calculate pairwise similarities
        similarities = []
        for i in range(len(bid_amounts)):
            for j in range(i + 1, len(bid_amounts)):
                if bid_amounts[i] > 0 and bid_amounts[j] > 0:
                    similarity = 1 - abs(bid_amounts[i] - bid_amounts[j]) / max(
                        bid_amounts[i], bid_amounts[j]
                    )
                    similarities.append(similarity)

        # If any pair is too similar, flag it
        return any(s > self.fraud_thresholds["bid_similarity"] for s in similarities)

    def _detect_circular_payments(
        self, transactions: list[dict[str, Any]]
    ) -> list[FraudPattern]:
        """
        Detect circular payment patterns indicating money laundering or kickbacks.

        Circular payments: A → B → C → A (money flows in a circle)
        """
        patterns = []

        if len(transactions) < 3:
            return patterns

        # Build payment graph
        payment_graph = {}  # {payer_id: [(recipient_id, amount, date)]}

        for trans in transactions:
            payer = trans.get("payer_id")
            recipient = trans.get("recipient_id")
            amount = trans.get("amount", 0)
            date = trans.get("date")

            if not payer or not recipient:
                continue

            if payer not in payment_graph:
                payment_graph[payer] = []
            payment_graph[payer].append((recipient, amount, date))

        # Look for circular paths (simple 3-node circles)
        for entity_a in payment_graph:
            for entity_b, amount_ab, date_ab in payment_graph.get(entity_a, []):
                if entity_b not in payment_graph:
                    continue

                for entity_c, amount_bc, date_bc in payment_graph.get(entity_b, []):
                    if entity_c not in payment_graph:
                        continue

                    # Check if C pays back to A (completing the circle)
                    for entity_back, amount_ca, date_ca in payment_graph.get(
                        entity_c, []
                    ):
                        if entity_back == entity_a:
                            # Found circular payment: A → B → C → A
                            patterns.append(
                                FraudPattern(
                                    fraud_type=FraudType.MONEY_LAUNDERING,
                                    severity=FraudSeverity.CRITICAL,
                                    confidence=0.85,
                                    indicators=[
                                        FraudIndicator(
                                            indicator_type="circular_payments",
                                            description=f"Circular payment pattern detected: {entity_a} → {entity_b} → {entity_c} → {entity_a}",
                                            confidence=0.85,
                                            evidence=[
                                                {
                                                    "path": [
                                                        entity_a,
                                                        entity_b,
                                                        entity_c,
                                                        entity_a,
                                                    ],
                                                    "amounts": [
                                                        amount_ab,
                                                        amount_bc,
                                                        amount_ca,
                                                    ],
                                                    "total_flow": amount_ab
                                                    + amount_bc
                                                    + amount_ca,
                                                }
                                            ],
                                            risk_score=9.0,
                                        )
                                    ],
                                    entities_involved=[entity_a, entity_b, entity_c],
                                    estimated_impact=min(
                                        amount_ab, amount_bc, amount_ca
                                    ),
                                    recommendations=[
                                        "Investigate circular payment scheme",
                                        "Freeze accounts involved",
                                        "Report to financial crimes unit",
                                        "Analyze all transactions between entities",
                                    ],
                                    evidence_trail={
                                        "payment_path": f"{entity_a}->{entity_b}->{entity_c}->{entity_a}",
                                        "amounts": [amount_ab, amount_bc, amount_ca],
                                    },
                                )
                            )

        return patterns

    def _check_bid_rotation(self, contracts: list[dict[str, Any]]) -> bool:
        """Check for bid rotation patterns."""
        # Sort by date
        sorted_contracts = sorted(contracts, key=lambda x: x.get("contract_date", ""))

        # Track winning vendors
        winners = [
            c.get("vendor_id") for c in sorted_contracts if c.get("is_winner", False)
        ]

        if len(winners) < 4:
            return False

        # Check for rotation pattern (simplified check)
        unique_winners = list(
            dict.fromkeys(winners)
        )  # Preserve order, remove duplicates
        if len(unique_winners) >= 3:
            # Check if winners cycle through vendors
            for i in range(len(winners) - len(unique_winners)):
                if winners[i : i + len(unique_winners)] == unique_winners:
                    return True

        return False

    def _identify_high_risk_entities(
        self, patterns: list[FraudPattern]
    ) -> list[dict[str, Any]]:
        """Identify high-risk entities from fraud patterns."""
        entity_risks = {}

        for pattern in patterns:
            for entity in pattern.entities_involved:
                if entity not in entity_risks:
                    entity_risks[entity] = {
                        "entity": entity,
                        "risk_score": 0,
                        "fraud_types": set(),
                        "total_impact": 0,
                    }

                # Update risk score (max of all patterns)
                max_risk = max(ind.risk_score for ind in pattern.indicators)
                entity_risks[entity]["risk_score"] = max(
                    entity_risks[entity]["risk_score"], max_risk
                )

                # Add fraud type
                entity_risks[entity]["fraud_types"].add(pattern.fraud_type.value)

                # Add to total impact
                entity_risks[entity]["total_impact"] += pattern.estimated_impact

        # Convert to list and sort by risk
        high_risk_entities = []
        for entity_data in entity_risks.values():
            entity_data["fraud_types"] = list(entity_data["fraud_types"])
            high_risk_entities.append(entity_data)

        high_risk_entities.sort(key=lambda x: x["risk_score"], reverse=True)

        return high_risk_entities[:10]  # Top 10 high-risk entities

    def _calculate_overall_confidence(self, patterns: list[FraudPattern]) -> float:
        """Calculate overall confidence score for the fraud analysis."""
        if not patterns:
            return 0.0

        # Weighted average based on estimated impact
        total_impact = sum(p.estimated_impact for p in patterns)
        if total_impact == 0:
            # Simple average if no impact estimates
            return sum(p.confidence for p in patterns) / len(patterns)

        # Weighted average
        weighted_confidence = sum(p.confidence * p.estimated_impact for p in patterns)
        return weighted_confidence / total_impact

    def _generate_fraud_report(self, patterns: list[FraudPattern]) -> dict[str, Any]:
        """Generate comprehensive fraud analysis report."""
        if not patterns:
            return {
                "summary": "No fraud patterns detected",
                "risk_level": "LOW",
                "patterns": [],
                "recommendations": ["Continue routine monitoring"],
            }

        # Categorize by severity
        critical_patterns = [
            p for p in patterns if p.severity == FraudSeverity.CRITICAL
        ]
        high_patterns = [p for p in patterns if p.severity == FraudSeverity.HIGH]
        medium_patterns = [p for p in patterns if p.severity == FraudSeverity.MEDIUM]
        low_patterns = [p for p in patterns if p.severity == FraudSeverity.LOW]

        # Determine overall risk level
        if critical_patterns:
            risk_level = "CRITICAL"
        elif len(high_patterns) >= 3:
            risk_level = "CRITICAL"
        elif high_patterns:
            risk_level = "HIGH"
        elif medium_patterns:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Compile all recommendations
        all_recommendations = []
        recommendation_set = set()
        for pattern in patterns:
            for rec in pattern.recommendations:
                if rec not in recommendation_set:
                    recommendation_set.add(rec)
                    all_recommendations.append(rec)

        # Create summary
        summary = f"Detected {len(patterns)} fraud patterns: "
        summary += f"{len(critical_patterns)} critical, {len(high_patterns)} high, "
        summary += f"{len(medium_patterns)} medium, {len(low_patterns)} low severity"

        return {
            "summary": summary,
            "risk_level": risk_level,
            "total_estimated_impact": sum(p.estimated_impact for p in patterns),
            "patterns_by_type": {
                fraud_type.value: len(
                    [p for p in patterns if p.fraud_type == fraud_type]
                )
                for fraud_type in FraudType
            },
            "patterns": [self._pattern_to_dict(p) for p in patterns],
            "recommendations": all_recommendations[:10],  # Top 10 recommendations
            "requires_immediate_action": risk_level in ["CRITICAL", "HIGH"],
        }

    def _pattern_to_dict(self, pattern: FraudPattern) -> dict[str, Any]:
        """Convert FraudPattern to dictionary for reporting."""
        return {
            "fraud_type": pattern.fraud_type.value,
            "severity": pattern.severity.value,
            "confidence": pattern.confidence,
            "entities_involved": pattern.entities_involved,
            "estimated_impact": pattern.estimated_impact,
            "indicators": [
                {
                    "type": ind.indicator_type,
                    "description": ind.description,
                    "confidence": ind.confidence,
                    "risk_score": ind.risk_score,
                }
                for ind in pattern.indicators
            ],
            "evidence_trail": pattern.evidence_trail,
            "recommendations": pattern.recommendations[:3],  # Top 3 for each pattern
        }

    def _analyze_benfords_law(
        self, values: list[float], entity_name: str = "Unknown"
    ) -> list[FraudPattern]:
        """
        Analyze values using Benford's Law to detect potential fraud.

        Benford's Law states that in many naturally occurring collections of numbers,
        the leading digit is more likely to be small. The distribution follows:
        - 1: 30.1%
        - 2: 17.6%
        - 3: 12.5%
        - ...
        - 9: 4.6%

        Fraudulent data often deviates from this distribution.
        """
        patterns = []

        if len(values) < 30:  # Need sufficient data for statistical significance
            return patterns

        # Filter out zeros and negative values
        valid_values = [v for v in values if v > 0]

        if len(valid_values) < 30:
            return patterns

        # Extract first digits
        first_digits = []
        for value in valid_values:
            first_digit = int(str(abs(value))[0])
            if 1 <= first_digit <= 9:
                first_digits.append(first_digit)

        if len(first_digits) < 30:
            return patterns

        # Calculate observed distribution
        observed_dist = {}
        for digit in range(1, 10):
            observed_dist[digit] = first_digits.count(digit) / len(first_digits)

        # Expected distribution according to Benford's Law
        import math

        benford_dist = {digit: math.log10(1 + 1 / digit) for digit in range(1, 10)}

        # Calculate chi-square statistic
        chi_square = 0
        for digit in range(1, 10):
            expected_count = benford_dist[digit] * len(first_digits)
            observed_count = first_digits.count(digit)
            if expected_count > 0:
                chi_square += ((observed_count - expected_count) ** 2) / expected_count

        # Chi-square critical value for 8 degrees of freedom at 95% confidence is ~15.51
        # At 99% confidence it's ~20.09
        deviation_threshold = 15.51

        if chi_square > deviation_threshold:
            # Calculate which digits deviate most
            major_deviations = []
            for digit in range(1, 10):
                diff = abs(observed_dist[digit] - benford_dist[digit])
                if diff > 0.05:  # 5% deviation
                    major_deviations.append(
                        {
                            "digit": digit,
                            "expected": round(benford_dist[digit] * 100, 1),
                            "observed": round(observed_dist[digit] * 100, 1),
                            "deviation": round(diff * 100, 1),
                        }
                    )

            # Determine confidence based on chi-square value
            if chi_square > 30:
                confidence = 0.9
                severity = FraudSeverity.HIGH
            elif chi_square > 20:
                confidence = 0.8
                severity = FraudSeverity.MEDIUM
            else:
                confidence = 0.7
                severity = FraudSeverity.MEDIUM

            patterns.append(
                FraudPattern(
                    fraud_type=FraudType.FALSE_CLAIMS,
                    severity=severity,
                    confidence=confidence,
                    indicators=[
                        FraudIndicator(
                            indicator_type="benfords_law_violation",
                            description=f"Values deviate from Benford's Law (χ² = {chi_square:.2f})",
                            confidence=confidence,
                            evidence=[
                                {
                                    "chi_square": round(chi_square, 2),
                                    "threshold": deviation_threshold,
                                    "sample_size": len(first_digits),
                                    "major_deviations": major_deviations,
                                }
                            ],
                            risk_score=min(9.0, 5.0 + (chi_square / 10)),
                        )
                    ],
                    entities_involved=[entity_name],
                    estimated_impact=sum(valid_values)
                    * 0.05,  # Estimated 5% manipulation
                    recommendations=[
                        "Conduct detailed audit of value generation process",
                        "Verify authenticity of financial documents",
                        "Compare with source documents",
                        "Investigate data entry procedures",
                        "Check for systematic manipulation",
                    ],
                    evidence_trail={
                        "chi_square_statistic": round(chi_square, 2),
                        "sample_size": len(first_digits),
                        "first_digit_distribution": {
                            str(k): round(v * 100, 1) for k, v in observed_dist.items()
                        },
                    },
                )
            )

        return patterns

    def _detect_temporal_anomalies(
        self, data_with_timestamps: list[dict[str, Any]], entity_name: str = "Unknown"
    ) -> list[FraudPattern]:
        """
        Detect temporal anomalies in transactions, contracts, or activities.

        Patterns detected:
        - After-hours activity (weekends, late nights)
        - Velocity anomalies (too fast processing)
        - Unusual clustering of events
        - Sequential timestamp manipulation
        """
        patterns = []

        if len(data_with_timestamps) < 5:
            return patterns

        # Convert to DataFrame for time analysis
        df = pd.DataFrame(data_with_timestamps)

        if "date" not in df.columns and "timestamp" not in df.columns:
            return patterns

        # Use date or timestamp column
        time_col = "date" if "date" in df.columns else "timestamp"
        df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
        df = df.dropna(subset=[time_col])

        if len(df) < 5:
            return patterns

        indicators = []

        # Check for after-hours activity
        df["hour"] = df[time_col].dt.hour
        df["day_of_week"] = df[time_col].dt.dayofweek  # 0=Monday, 6=Sunday

        # Activity after 8 PM or before 6 AM
        after_hours = df[(df["hour"] >= 20) | (df["hour"] < 6)]
        if len(after_hours) > len(df) * 0.2:  # More than 20% after hours
            indicators.append(
                FraudIndicator(
                    indicator_type="after_hours_activity",
                    description=f"{len(after_hours)} transactions ({len(after_hours)/len(df)*100:.1f}%) occurred after hours",
                    confidence=0.7,
                    evidence=[
                        {
                            "after_hours_count": len(after_hours),
                            "total_count": len(df),
                            "percentage": round(len(after_hours) / len(df) * 100, 1),
                        }
                    ],
                    risk_score=6.5,
                )
            )

        # Weekend activity
        weekend = df[df["day_of_week"] >= 5]  # Saturday or Sunday
        if len(weekend) > len(df) * 0.3:  # More than 30% on weekends
            indicators.append(
                FraudIndicator(
                    indicator_type="weekend_activity",
                    description=f"{len(weekend)} transactions ({len(weekend)/len(df)*100:.1f}%) occurred on weekends",
                    confidence=0.65,
                    evidence=[
                        {
                            "weekend_count": len(weekend),
                            "total_count": len(df),
                            "percentage": round(len(weekend) / len(df) * 100, 1),
                        }
                    ],
                    risk_score=6.0,
                )
            )

        # Check for unusually fast processing (velocity check)
        df_sorted = df.sort_values(time_col)
        time_diffs = df_sorted[time_col].diff()

        # Find transactions processed within 1 minute of each other
        very_fast = time_diffs[time_diffs < pd.Timedelta(minutes=1)]
        if len(very_fast) > 3:
            indicators.append(
                FraudIndicator(
                    indicator_type="velocity_anomaly",
                    description=f"{len(very_fast)} transactions processed within 1 minute intervals",
                    confidence=0.75,
                    evidence=[
                        {
                            "fast_transaction_count": len(very_fast),
                            "min_interval_seconds": (
                                time_diffs.min().total_seconds()
                                if not time_diffs.empty
                                else 0
                            ),
                        }
                    ],
                    risk_score=7.0,
                )
            )

        # Check for timestamp clustering (many transactions in short period)
        df["date_only"] = df[time_col].dt.date
        daily_counts = df.groupby("date_only").size()

        if len(daily_counts) > 1:
            mean_daily = daily_counts.mean()
            std_daily = daily_counts.std()

            if std_daily > 0:
                outlier_days = daily_counts[daily_counts > mean_daily + 2 * std_daily]

                if len(outlier_days) > 0:
                    indicators.append(
                        FraudIndicator(
                            indicator_type="temporal_clustering",
                            description=f"{len(outlier_days)} days with unusually high activity",
                            confidence=0.7,
                            evidence=[
                                {
                                    "outlier_days": len(outlier_days),
                                    "max_daily_count": int(daily_counts.max()),
                                    "average_daily_count": round(mean_daily, 1),
                                }
                            ],
                            risk_score=6.5,
                        )
                    )

        if indicators:
            patterns.append(
                FraudPattern(
                    fraud_type=FraudType.PROCUREMENT_FRAUD,
                    severity=(
                        FraudSeverity.MEDIUM
                        if len(indicators) < 3
                        else FraudSeverity.HIGH
                    ),
                    confidence=max(ind.confidence for ind in indicators),
                    indicators=indicators,
                    entities_involved=[entity_name],
                    estimated_impact=0,  # Temporal patterns don't directly estimate impact
                    recommendations=[
                        "Review approval processes for temporal controls",
                        "Investigate authorization for after-hours activity",
                        "Check system logs for automated processes",
                        "Verify legitimacy of high-velocity transactions",
                    ],
                    evidence_trail={
                        "analysis_period": f"{df[time_col].min()} to {df[time_col].max()}",
                        "total_records_analyzed": len(df),
                    },
                )
            )

        return patterns

    async def hunt_specific_fraud(
        self, fraud_type: FraudType, data: dict[str, Any], context: AgentContext
    ) -> AgentResponse:
        """Hunt for a specific type of fraud with focused analysis."""
        # This method allows targeting specific fraud types for deeper analysis
        message = AgentMessage(
            sender="system",
            recipient="oxossi",
            action=f"hunt_{fraud_type.value}",
            payload=data,
        )

        return await self.process(message, context)
