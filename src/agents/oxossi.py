"""
Module: agents.oxossi
Codinome: Oxóssi - Caçador de Fraudes
Description: Agent specialized in fraud detection and tracking with precision hunting capabilities
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field as PydanticField

from src.agents.deodoro import BaseAgent, AgentContext, AgentMessage, AgentResponse, AgentStatus
from src.core import get_logger
from src.core.exceptions import AgentExecutionError, DataAnalysisError


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
    evidence: List[Dict[str, Any]]
    risk_score: float  # 0.0 to 10.0


@dataclass
class FraudPattern:
    """Fraud pattern detection result."""
    
    fraud_type: FraudType
    severity: FraudSeverity
    confidence: float
    indicators: List[FraudIndicator]
    entities_involved: List[str]
    estimated_impact: float
    recommendations: List[str]
    evidence_trail: Dict[str, Any]


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
            agent_id="oxossi",
            name="Oxóssi",
            description="Fraud detection specialist with precision tracking capabilities",
            capabilities=[
                "fraud_detection",
                "pattern_recognition",
                "entity_relationship_analysis",
                "financial_forensics",
                "risk_assessment",
                "evidence_tracking"
            ]
        )
        
        # Fraud detection thresholds
        self.fraud_thresholds = {
            "bid_similarity": 0.85,  # Similarity threshold for bid rigging
            "price_deviation": 2.5,  # Standard deviations for price fixing
            "vendor_activity": 0.1,  # Minimum activity for legitimate vendor
            "invoice_anomaly": 0.7,  # Confidence threshold for invoice fraud
            "relationship_strength": 0.6  # Threshold for suspicious relationships
        }
        
        # Known fraud patterns database
        self.fraud_patterns = self._initialize_fraud_patterns()
    
    def _initialize_fraud_patterns(self) -> Dict[str, Any]:
        """Initialize known fraud pattern templates."""
        return {
            FraudType.BID_RIGGING: {
                "indicators": [
                    "identical_bid_amounts",
                    "sequential_bid_numbers",
                    "rotation_pattern",
                    "last_minute_withdrawals"
                ],
                "min_confidence": 0.7
            },
            FraudType.PRICE_FIXING: {
                "indicators": [
                    "uniform_price_increases",
                    "identical_pricing_across_vendors",
                    "price_stability_anomaly",
                    "market_share_stability"
                ],
                "min_confidence": 0.65
            },
            FraudType.PHANTOM_VENDOR: {
                "indicators": [
                    "no_physical_address",
                    "recent_registration",
                    "single_contract_only",
                    "no_web_presence",
                    "shared_contact_info"
                ],
                "min_confidence": 0.75
            },
            FraudType.INVOICE_FRAUD: {
                "indicators": [
                    "duplicate_invoices",
                    "sequential_invoice_numbers",
                    "rounded_amounts",
                    "unusual_descriptions",
                    "timing_anomalies"
                ],
                "min_confidence": 0.7
            }
        }
    
    async def process(self, message: AgentMessage, context: AgentContext) -> AgentResponse:
        """Process fraud detection request."""
        start_time = datetime.now()
        
        try:
            self.status = AgentStatus.THINKING
            logger.info(f"Oxóssi starting fraud hunt: {message.content}")
            
            # Extract data for analysis
            data = message.data
            if not data:
                raise AgentExecutionError("No data provided for fraud detection")
            
            # Determine analysis type
            if "contracts" in data:
                fraud_patterns = await self._analyze_contract_fraud(data["contracts"], context)
            elif "transactions" in data:
                fraud_patterns = await self._analyze_transaction_fraud(data["transactions"], context)
            elif "vendors" in data:
                fraud_patterns = await self._analyze_vendor_fraud(data["vendors"], context)
            elif "invoices" in data:
                fraud_patterns = await self._analyze_invoice_fraud(data["invoices"], context)
            else:
                # Comprehensive fraud analysis
                fraud_patterns = await self._comprehensive_fraud_analysis(data, context)
            
            # Generate fraud report
            report = self._generate_fraud_report(fraud_patterns)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.status = AgentStatus.IDLE
            
            return AgentResponse(
                success=True,
                data={
                    "fraud_analysis": report,
                    "patterns_detected": len(fraud_patterns),
                    "high_risk_entities": self._identify_high_risk_entities(fraud_patterns),
                    "total_estimated_impact": sum(p.estimated_impact for p in fraud_patterns),
                    "processing_time": processing_time
                },
                metadata={
                    "agent": self.name,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "confidence_score": self._calculate_overall_confidence(fraud_patterns)
                }
            )
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Oxóssi fraud detection failed: {str(e)}")
            return AgentResponse(
                success=False,
                data={"error": str(e)},
                metadata={"agent": self.name, "error_type": type(e).__name__}
            )
    
    async def _analyze_contract_fraud(
        self, contracts: List[Dict[str, Any]], context: AgentContext
    ) -> List[FraudPattern]:
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
        
        return fraud_patterns
    
    async def _detect_bid_rigging(self, contracts: List[Dict[str, Any]]) -> List[FraudPattern]:
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
                indicators.append(FraudIndicator(
                    indicator_type="identical_bid_amounts",
                    description="Multiple bids with identical or nearly identical amounts",
                    confidence=0.8,
                    evidence=[{"bid_amounts": bid_amounts}],
                    risk_score=7.5
                ))
            
            # Check for bid rotation patterns
            if self._check_bid_rotation(group_contracts):
                indicators.append(FraudIndicator(
                    indicator_type="rotation_pattern",
                    description="Vendors appear to be taking turns winning bids",
                    confidence=0.75,
                    evidence=[{"pattern": "rotation_detected"}],
                    risk_score=8.0
                ))
            
            if indicators:
                patterns.append(FraudPattern(
                    fraud_type=FraudType.BID_RIGGING,
                    severity=FraudSeverity.HIGH,
                    confidence=max(ind.confidence for ind in indicators),
                    indicators=indicators,
                    entities_involved=[c.get("vendor_name", "Unknown") for c in group_contracts],
                    estimated_impact=sum(c.get("contract_value", 0) for c in group_contracts) * 0.1,
                    recommendations=[
                        "Investigate bidding process for collusion",
                        "Review communications between vendors",
                        "Check for common ownership or management"
                    ],
                    evidence_trail={"bidding_process_id": bid_id}
                ))
        
        return patterns
    
    async def _detect_phantom_vendors(self, contracts: List[Dict[str, Any]]) -> List[FraudPattern]:
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
                indicators.append(FraudIndicator(
                    indicator_type="single_contract_only",
                    description="Vendor has only one contract in the system",
                    confidence=0.6,
                    evidence=[{"contract_count": 1}],
                    risk_score=5.0
                ))
            
            # Check for recent registration before contract
            for contract in vendor_contracts_list:
                vendor_reg_date = contract.get("vendor_registration_date")
                contract_date = contract.get("contract_date")
                if vendor_reg_date and contract_date:
                    days_diff = (pd.to_datetime(contract_date) - pd.to_datetime(vendor_reg_date)).days
                    if days_diff < 30:  # Registered less than 30 days before contract
                        indicators.append(FraudIndicator(
                            indicator_type="recent_registration",
                            description="Vendor registered shortly before receiving contract",
                            confidence=0.7,
                            evidence=[{"days_before_contract": days_diff}],
                            risk_score=6.5
                        ))
            
            if indicators:
                patterns.append(FraudPattern(
                    fraud_type=FraudType.PHANTOM_VENDOR,
                    severity=FraudSeverity.HIGH if len(indicators) > 1 else FraudSeverity.MEDIUM,
                    confidence=max(ind.confidence for ind in indicators),
                    indicators=indicators,
                    entities_involved=[vendor_contracts_list[0].get("vendor_name", f"Vendor_{vendor_id}")],
                    estimated_impact=sum(c.get("contract_value", 0) for c in vendor_contracts_list),
                    recommendations=[
                        "Verify vendor physical existence",
                        "Check vendor registration details",
                        "Validate vendor tax records",
                        "Conduct site visits if necessary"
                    ],
                    evidence_trail={"vendor_id": vendor_id}
                ))
        
        return patterns
    
    async def _detect_price_fixing(self, contracts: List[Dict[str, Any]]) -> List[FraudPattern]:
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
                price_data.append({
                    "vendor": contract.get("vendor_name"),
                    "price": contract.get("unit_price", contract.get("contract_value", 0)),
                    "date": contract.get("contract_date")
                })
            
            df = pd.DataFrame(price_data)
            if df.empty:
                continue
            
            indicators = []
            
            # Check for identical pricing across vendors
            price_groups = df.groupby("vendor")["price"].mean()
            if len(price_groups) > 1:
                price_variance = price_groups.std() / price_groups.mean()
                if price_variance < 0.05:  # Less than 5% variance
                    indicators.append(FraudIndicator(
                        indicator_type="identical_pricing_across_vendors",
                        description="Multiple vendors have nearly identical pricing",
                        confidence=0.75,
                        evidence=[{"price_variance": price_variance}],
                        risk_score=7.0
                    ))
            
            # Check for synchronized price increases
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            
            # Group by time periods and check for uniform increases
            monthly_avg = df.groupby(pd.Grouper(key="date", freq="M"))["price"].mean()
            if len(monthly_avg) > 3:
                price_changes = monthly_avg.pct_change().dropna()
                if (price_changes > 0.05).sum() > 1:  # Multiple 5%+ increases
                    if price_changes.std() < 0.02:  # Very similar increase rates
                        indicators.append(FraudIndicator(
                            indicator_type="uniform_price_increases",
                            description="Synchronized price increases across time periods",
                            confidence=0.7,
                            evidence=[{"price_increases": price_changes.to_list()}],
                            risk_score=6.5
                        ))
            
            if indicators:
                patterns.append(FraudPattern(
                    fraud_type=FraudType.PRICE_FIXING,
                    severity=FraudSeverity.HIGH,
                    confidence=max(ind.confidence for ind in indicators),
                    indicators=indicators,
                    entities_involved=df["vendor"].unique().tolist(),
                    estimated_impact=df["price"].sum() * 0.15,  # Estimated 15% overcharge
                    recommendations=[
                        "Compare prices with market rates",
                        "Investigate vendor communications",
                        "Review industry pricing trends",
                        "Consider antitrust investigation"
                    ],
                    evidence_trail={"category": category}
                ))
        
        return patterns
    
    async def _analyze_transaction_fraud(
        self, transactions: List[Dict[str, Any]], context: AgentContext
    ) -> List[FraudPattern]:
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
        self, vendors: List[Dict[str, Any]], context: AgentContext
    ) -> List[FraudPattern]:
        """Analyze vendor data for fraud patterns."""
        patterns = []
        
        # Check for shell companies
        for vendor in vendors:
            indicators = []
            
            # Check for shared addresses
            address = vendor.get("address")
            if address:
                same_address_vendors = [v for v in vendors if v.get("address") == address]
                if len(same_address_vendors) > 2:
                    indicators.append(FraudIndicator(
                        indicator_type="shared_address",
                        description="Multiple vendors share the same address",
                        confidence=0.8,
                        evidence=[{"vendors": [v.get("name") for v in same_address_vendors]}],
                        risk_score=7.0
                    ))
            
            # Check for shared contact information
            phone = vendor.get("phone")
            email = vendor.get("email")
            if phone or email:
                same_contact_vendors = [
                    v for v in vendors 
                    if (phone and v.get("phone") == phone) or (email and v.get("email") == email)
                ]
                if len(same_contact_vendors) > 1:
                    indicators.append(FraudIndicator(
                        indicator_type="shared_contact_info",
                        description="Multiple vendors share contact information",
                        confidence=0.85,
                        evidence=[{"vendors": [v.get("name") for v in same_contact_vendors]}],
                        risk_score=8.0
                    ))
            
            if indicators:
                patterns.append(FraudPattern(
                    fraud_type=FraudType.PHANTOM_VENDOR,
                    severity=FraudSeverity.HIGH,
                    confidence=max(ind.confidence for ind in indicators),
                    indicators=indicators,
                    entities_involved=[vendor.get("name", "Unknown")],
                    estimated_impact=0,  # Unknown until contracts analyzed
                    recommendations=[
                        "Investigate vendor relationships",
                        "Verify vendor legitimacy",
                        "Check for common ownership"
                    ],
                    evidence_trail={"vendor_id": vendor.get("id")}
                ))
        
        return patterns
    
    async def _analyze_invoice_fraud(
        self, invoices: List[Dict[str, Any]], context: AgentContext
    ) -> List[FraudPattern]:
        """Analyze invoices for fraud patterns."""
        patterns = []
        
        # Check for duplicate invoices
        invoice_hashes = {}
        for invoice in invoices:
            # Create hash of key invoice attributes
            hash_key = f"{invoice.get('vendor_id')}_{invoice.get('amount')}_{invoice.get('date')}"
            if hash_key in invoice_hashes:
                patterns.append(FraudPattern(
                    fraud_type=FraudType.INVOICE_FRAUD,
                    severity=FraudSeverity.HIGH,
                    confidence=0.9,
                    indicators=[FraudIndicator(
                        indicator_type="duplicate_invoices",
                        description="Duplicate invoice detected",
                        confidence=0.9,
                        evidence=[{
                            "invoice_1": invoice_hashes[hash_key],
                            "invoice_2": invoice.get("invoice_number")
                        }],
                        risk_score=8.5
                    )],
                    entities_involved=[invoice.get("vendor_name", "Unknown")],
                    estimated_impact=invoice.get("amount", 0),
                    recommendations=[
                        "Reject duplicate invoice",
                        "Investigate vendor billing practices",
                        "Review payment controls"
                    ],
                    evidence_trail={"invoice_numbers": [invoice_hashes[hash_key], invoice.get("invoice_number")]}
                ))
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
                    key=lambda x: int(x.get("invoice_number", "0").replace("-", ""))
                )
                
                # Check for suspicious sequential patterns
                invoice_numbers = [int(inv.get("invoice_number", "0").replace("-", "")) for inv in sorted_invoices]
                if len(invoice_numbers) > 5:
                    # Check if all invoices are perfectly sequential
                    expected_sequence = list(range(min(invoice_numbers), max(invoice_numbers) + 1))
                    if invoice_numbers == expected_sequence:
                        patterns.append(FraudPattern(
                            fraud_type=FraudType.INVOICE_FRAUD,
                            severity=FraudSeverity.MEDIUM,
                            confidence=0.7,
                            indicators=[FraudIndicator(
                                indicator_type="sequential_invoice_numbers",
                                description="Perfectly sequential invoice numbers suggest manipulation",
                                confidence=0.7,
                                evidence=[{"sequence": invoice_numbers[:10]}],  # First 10 as example
                                risk_score=6.0
                            )],
                            entities_involved=[sorted_invoices[0].get("vendor_name", f"Vendor_{vendor_id}")],
                            estimated_impact=sum(inv.get("amount", 0) for inv in sorted_invoices) * 0.05,
                            recommendations=[
                                "Audit vendor invoicing practices",
                                "Verify actual services delivered",
                                "Review invoice approval process"
                            ],
                            evidence_trail={"vendor_id": vendor_id}
                        ))
            except:
                pass  # Skip if invoice numbers aren't numeric
        
        return patterns
    
    async def _comprehensive_fraud_analysis(
        self, data: Dict[str, Any], context: AgentContext
    ) -> List[FraudPattern]:
        """Perform comprehensive fraud analysis across all data types."""
        all_patterns = []
        
        # Analyze each data type if present
        if "contracts" in data:
            patterns = await self._analyze_contract_fraud(data["contracts"], context)
            all_patterns.extend(patterns)
        
        if "transactions" in data:
            patterns = await self._analyze_transaction_fraud(data["transactions"], context)
            all_patterns.extend(patterns)
        
        if "vendors" in data:
            patterns = await self._analyze_vendor_fraud(data["vendors"], context)
            all_patterns.extend(patterns)
        
        if "invoices" in data:
            patterns = await self._analyze_invoice_fraud(data["invoices"], context)
            all_patterns.extend(patterns)
        
        # Cross-reference patterns for complex fraud schemes
        complex_patterns = await self._detect_complex_fraud_schemes(all_patterns, data)
        all_patterns.extend(complex_patterns)
        
        return all_patterns
    
    async def _detect_money_laundering(self, transactions: List[Dict[str, Any]]) -> List[FraudPattern]:
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
                below_threshold = [a for a in amounts if threshold * 0.8 < a < threshold]
                if len(below_threshold) >= 2:
                    patterns.append(FraudPattern(
                        fraud_type=FraudType.MONEY_LAUNDERING,
                        severity=FraudSeverity.HIGH,
                        confidence=0.75,
                        indicators=[FraudIndicator(
                            indicator_type="structuring",
                            description="Multiple transactions just below reporting threshold",
                            confidence=0.75,
                            evidence=[{"transactions": below_threshold}],
                            risk_score=8.0
                        )],
                        entities_involved=[key.split("_")[1]],
                        estimated_impact=sum(below_threshold),
                        recommendations=[
                            "File suspicious activity report",
                            "Review all transactions by entity",
                            "Check for related accounts"
                        ],
                        evidence_trail={"date_entity": key}
                    ))
        
        return patterns
    
    async def _detect_kickback_schemes(self, transactions: List[Dict[str, Any]]) -> List[FraudPattern]:
        """Detect potential kickback schemes."""
        patterns = []
        
        # Look for payments shortly after contract awards
        # This is a simplified detection - real implementation would be more sophisticated
        
        return patterns
    
    async def _detect_complex_fraud_schemes(
        self, patterns: List[FraudPattern], data: Dict[str, Any]
    ) -> List[FraudPattern]:
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
                
                complex_patterns.append(FraudPattern(
                    fraud_type=FraudType.PROCUREMENT_FRAUD,  # Complex multi-type fraud
                    severity=FraudSeverity.CRITICAL,
                    confidence=0.85,
                    indicators=[
                        FraudIndicator(
                            indicator_type="complex_scheme",
                            description=f"Entity involved in multiple fraud types: {', '.join(f.value for f in fraud_types)}",
                            confidence=0.85,
                            evidence=[{"fraud_types": [f.value for f in fraud_types]}],
                            risk_score=9.5
                        )
                    ],
                    entities_involved=[entity],
                    estimated_impact=sum(p.estimated_impact for p in entity_patterns),
                    recommendations=[
                        "Launch comprehensive investigation",
                        "Freeze entity accounts",
                        "Coordinate with law enforcement",
                        "Review all entity transactions and contracts"
                    ],
                    evidence_trail={"related_patterns": [p.fraud_type.value for p in entity_patterns]}
                ))
        
        return complex_patterns
    
    def _check_bid_similarity(self, bid_amounts: List[float]) -> bool:
        """Check if bids are suspiciously similar."""
        if len(bid_amounts) < 2:
            return False
        
        # Calculate pairwise similarities
        similarities = []
        for i in range(len(bid_amounts)):
            for j in range(i + 1, len(bid_amounts)):
                if bid_amounts[i] > 0 and bid_amounts[j] > 0:
                    similarity = 1 - abs(bid_amounts[i] - bid_amounts[j]) / max(bid_amounts[i], bid_amounts[j])
                    similarities.append(similarity)
        
        # If any pair is too similar, flag it
        return any(s > self.fraud_thresholds["bid_similarity"] for s in similarities)
    
    def _check_bid_rotation(self, contracts: List[Dict[str, Any]]) -> bool:
        """Check for bid rotation patterns."""
        # Sort by date
        sorted_contracts = sorted(contracts, key=lambda x: x.get("contract_date", ""))
        
        # Track winning vendors
        winners = [c.get("vendor_id") for c in sorted_contracts if c.get("is_winner", False)]
        
        if len(winners) < 4:
            return False
        
        # Check for rotation pattern (simplified check)
        unique_winners = list(dict.fromkeys(winners))  # Preserve order, remove duplicates
        if len(unique_winners) >= 3:
            # Check if winners cycle through vendors
            for i in range(len(winners) - len(unique_winners)):
                if winners[i:i+len(unique_winners)] == unique_winners:
                    return True
        
        return False
    
    def _identify_high_risk_entities(self, patterns: List[FraudPattern]) -> List[Dict[str, Any]]:
        """Identify high-risk entities from fraud patterns."""
        entity_risks = {}
        
        for pattern in patterns:
            for entity in pattern.entities_involved:
                if entity not in entity_risks:
                    entity_risks[entity] = {
                        "entity": entity,
                        "risk_score": 0,
                        "fraud_types": set(),
                        "total_impact": 0
                    }
                
                # Update risk score (max of all patterns)
                max_risk = max(ind.risk_score for ind in pattern.indicators)
                entity_risks[entity]["risk_score"] = max(entity_risks[entity]["risk_score"], max_risk)
                
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
    
    def _calculate_overall_confidence(self, patterns: List[FraudPattern]) -> float:
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
    
    def _generate_fraud_report(self, patterns: List[FraudPattern]) -> Dict[str, Any]:
        """Generate comprehensive fraud analysis report."""
        if not patterns:
            return {
                "summary": "No fraud patterns detected",
                "risk_level": "LOW",
                "patterns": [],
                "recommendations": ["Continue routine monitoring"]
            }
        
        # Categorize by severity
        critical_patterns = [p for p in patterns if p.severity == FraudSeverity.CRITICAL]
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
                fraud_type.value: len([p for p in patterns if p.fraud_type == fraud_type])
                for fraud_type in FraudType
            },
            "patterns": [self._pattern_to_dict(p) for p in patterns],
            "recommendations": all_recommendations[:10],  # Top 10 recommendations
            "requires_immediate_action": risk_level in ["CRITICAL", "HIGH"]
        }
    
    def _pattern_to_dict(self, pattern: FraudPattern) -> Dict[str, Any]:
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
                    "risk_score": ind.risk_score
                }
                for ind in pattern.indicators
            ],
            "evidence_trail": pattern.evidence_trail,
            "recommendations": pattern.recommendations[:3]  # Top 3 for each pattern
        }
    
    async def hunt_specific_fraud(
        self, fraud_type: FraudType, data: Dict[str, Any], context: AgentContext
    ) -> AgentResponse:
        """Hunt for a specific type of fraud with focused analysis."""
        # This method allows targeting specific fraud types for deeper analysis
        message = AgentMessage(
            role="user",
            content=f"Hunt for {fraud_type.value} fraud",
            data=data,
            metadata={"target_fraud_type": fraud_type.value}
        )
        
        return await self.process(message, context)