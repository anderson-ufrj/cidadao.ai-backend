"""
Module: agents.machado_agent
Description: Machado de Assis - Textual Analysis Agent specialized in processing government documents
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel
from pydantic import Field as PydanticField

from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
    BaseAgent,
)
from src.core import get_logger


class DocumentType(Enum):
    """Types of government documents."""

    CONTRACT = "contract"
    PUBLIC_TENDER = "edital"
    LAW = "lei"
    DECREE = "decreto"
    ORDINANCE = "portaria"
    RESOLUTION = "resolucao"
    NORMATIVE_INSTRUCTION = "instrucao_normativa"


class AlertSeverity(Enum):
    """Severity levels for document alerts."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


@dataclass
class EntityExtraction:
    """Extracted entities from document."""

    organizations: list[str]
    values: list[dict[str, Any]]  # {amount: float, context: str}
    dates: list[dict[str, Any]]  # {date: str, event: str}
    people: list[str]
    locations: list[str]
    legal_references: list[str]


@dataclass
class DocumentAlert:
    """Alert for suspicious or problematic content."""

    alert_type: str
    excerpt: str
    legal_violation: Optional[str]
    severity: AlertSeverity
    confidence: float
    explanation: str
    recommendation: str


@dataclass
class TextualAnalysisResult:
    """Result of comprehensive textual analysis."""

    document_id: str
    document_type: DocumentType
    entities: EntityExtraction
    alerts: list[DocumentAlert]
    complexity_score: float  # Flesch adapted for PT-BR
    transparency_score: float  # 0.0 to 1.0
    legal_compliance: float  # 0.0 to 1.0
    readability_grade: int
    suspicious_patterns: list[str]
    checksum: str
    analysis_timestamp: datetime


class TextualAnalysisRequest(BaseModel):
    """Request for textual analysis of government documents."""

    document_content: str = PydanticField(description="Full text of the document")
    document_type: Optional[str] = PydanticField(
        default=None, description="Type of document"
    )
    document_metadata: Optional[dict[str, Any]] = PydanticField(
        default=None, description="Document metadata"
    )
    focus_areas: Optional[list[str]] = PydanticField(
        default=None, description="Specific analysis focus areas"
    )
    legal_framework: Optional[list[str]] = PydanticField(
        default=None, description="Legal frameworks to check against"
    )
    complexity_threshold: float = PydanticField(
        default=0.7, description="Complexity alert threshold"
    )


class MachadoAgent(BaseAgent):
    """
    Machado de Assis - Textual Analysis Agent

    Specialized in processing government documents, extracting structured information,
    detecting inconsistencies, and identifying problematic clauses.
    Inspired by Machado de Assis, master of Brazilian literature and language.
    """

    def __init__(self):
        super().__init__(
            name="machado",
            description="Textual Analysis Agent specialized in processing government documents",
            capabilities=[
                "document_parsing",
                "named_entity_recognition",
                "semantic_analysis",
                "legal_compliance_checking",
                "ambiguity_detection",
                "readability_assessment",
                "contract_analysis",
                "tender_document_review",
                "regulatory_text_processing",
                "suspicious_clause_identification",
                "linguistic_complexity_analysis",
                "transparency_scoring",
            ],
        )
        self.logger = get_logger("agent.machado")

        # Legal framework references
        self._legal_frameworks = {
            "CF88": "Constituição Federal de 1988",
            "LEI8666": "Lei 8.666/93 - Licitações e Contratos",
            "LEI14133": "Lei 14.133/21 - Nova Lei de Licitações",
            "LAI": "Lei 12.527/11 - Lei de Acesso à Informação",
            "LGPD": "Lei 13.709/18 - Lei Geral de Proteção de Dados",
        }

        # Suspicious patterns regex
        self._suspicious_patterns = {
            "urgency_abuse": r"(urgente|emergencial|inadiável)(?!.*justificativa)",
            "vague_specifications": r"(conforme|adequado|satisfatório|apropriado)\s+(?!critério|norma)",
            "exclusive_criteria": r"(exclusivamente|unicamente|somente)(?=.*fornecedor|empresa)",
            "price_manipulation": r"(valor\s+aproximado|preço\s+estimado)(?=.*sigiloso|confidencial)",
            "favoritism_indicators": r"(experiência\s+mínima\s+\d+\s+anos?)(?=.*específic)",
        }

        # NER patterns for Brazilian documents
        self._ner_patterns = {
            "cnpj": r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}",
            "cpf": r"\d{3}\.\d{3}\.\d{3}-\d{2}",
            "money": r"R\$\s*[\d,.]+",
            "percentage": r"\d+(?:,\d+)?%",
            "law_reference": r"Lei\s+n?º?\s*[\d./-]+",
            "article": r"Art\.?\s*\d+[º°]?",
        }

    async def initialize(self) -> None:
        """Initialize agent resources."""
        self.logger.info("Machado agent initialized and ready for textual analysis")

    async def shutdown(self) -> None:
        """Cleanup agent resources."""
        self.logger.info("Machado agent shutdown completed")

    async def process(
        self,
        message: AgentMessage,
        context: AgentContext,
    ) -> AgentResponse:
        """
        Process textual analysis request.

        Args:
            message: Document analysis request
            context: Agent execution context

        Returns:
            Comprehensive textual analysis results
        """
        try:
            self.logger.info(
                "Processing textual analysis request",
                investigation_id=context.investigation_id,
                action=message.action,
            )

            # Parse request
            if isinstance(message.payload, dict):
                request = TextualAnalysisRequest(**message.payload)
            else:
                request = TextualAnalysisRequest(document_content=str(message.payload))

            # Perform comprehensive textual analysis
            analysis_result = await self._analyze_document(request, context)

            # Generate insights and recommendations
            insights = await self._generate_document_insights(analysis_result, request)

            response_data = {
                "document_id": analysis_result.document_id,
                "timestamp": datetime.utcnow().isoformat(),
                "agent": "machado",
                "analysis_type": "textual_analysis",
                "document_type": analysis_result.document_type.value,
                "entities": {
                    "organizations": analysis_result.entities.organizations,
                    "values": analysis_result.entities.values,
                    "dates": analysis_result.entities.dates,
                    "people": analysis_result.entities.people,
                    "legal_references": analysis_result.entities.legal_references,
                },
                "alerts": [
                    {
                        "type": alert.alert_type,
                        "excerpt": alert.excerpt,
                        "legal_violation": alert.legal_violation,
                        "severity": alert.severity.value,
                        "confidence": alert.confidence,
                        "explanation": alert.explanation,
                    }
                    for alert in analysis_result.alerts
                ],
                "metrics": {
                    "complexity_score": analysis_result.complexity_score,
                    "transparency_score": analysis_result.transparency_score,
                    "legal_compliance": analysis_result.legal_compliance,
                    "readability_grade": analysis_result.readability_grade,
                },
                "suspicious_patterns": analysis_result.suspicious_patterns,
                "insights": insights,
                "checksum": analysis_result.checksum,
            }

            self.logger.info(
                "Textual analysis completed",
                investigation_id=context.investigation_id,
                document_type=analysis_result.document_type.value,
                alerts_count=len(analysis_result.alerts),
                transparency_score=analysis_result.transparency_score,
            )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result=response_data,
                metadata={"analysis_type": "textual_analysis"},
            )

        except Exception as e:
            self.logger.error(
                "Textual analysis failed",
                investigation_id=context.investigation_id,
                error=str(e),
                exc_info=True,
            )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.ERROR,
                result=None,
                error=str(e),
                metadata={"analysis_type": "textual_analysis"},
            )

    async def _analyze_document(
        self, request: TextualAnalysisRequest, context: AgentContext
    ) -> TextualAnalysisResult:
        """Perform comprehensive document analysis."""

        self.logger.info(
            "Starting textual analysis",
            document_length=len(request.document_content),
            document_type=request.document_type,
        )

        # Generate document ID
        doc_id = hashlib.md5(request.document_content.encode()).hexdigest()[:12]

        # Determine document type
        doc_type = await self._classify_document_type(request.document_content)

        # Extract entities using NER
        entities = await self._extract_entities(request.document_content)

        # Detect alerts and issues
        alerts = await self._detect_document_alerts(request.document_content, doc_type)

        # Calculate metrics
        complexity = await self._calculate_complexity_score(request.document_content)
        transparency = await self._calculate_transparency_score(
            request.document_content, entities
        )
        compliance = await self._assess_legal_compliance(
            request.document_content, doc_type
        )
        readability = await self._calculate_readability_grade(request.document_content)

        # Detect suspicious patterns
        suspicious = await self._detect_suspicious_patterns(request.document_content)

        # Generate checksum
        checksum = hashlib.md5(
            f"{doc_id}{complexity}{transparency}{len(alerts)}".encode()
        ).hexdigest()

        return TextualAnalysisResult(
            document_id=doc_id,
            document_type=doc_type,
            entities=entities,
            alerts=alerts,
            complexity_score=complexity,
            transparency_score=transparency,
            legal_compliance=compliance,
            readability_grade=readability,
            suspicious_patterns=suspicious,
            checksum=checksum,
            analysis_timestamp=datetime.utcnow(),
        )

    async def _classify_document_type(self, text: str) -> DocumentType:
        """Classify document type based on content patterns."""

        text_lower = text.lower()

        # Contract indicators
        if any(
            keyword in text_lower
            for keyword in ["contrato", "contratação", "contratado"]
        ):
            return DocumentType.CONTRACT

        # Public tender indicators
        if any(keyword in text_lower for keyword in ["edital", "licitação", "pregão"]):
            return DocumentType.PUBLIC_TENDER

        # Law indicators
        if any(
            keyword in text_lower for keyword in ["lei nº", "lei n°", "projeto de lei"]
        ):
            return DocumentType.LAW

        # Decree indicators
        if any(keyword in text_lower for keyword in ["decreto", "decreto nº"]):
            return DocumentType.DECREE

        # Default to contract if unsure
        return DocumentType.CONTRACT

    async def _extract_entities(self, text: str) -> EntityExtraction:
        """Extract named entities from document text."""

        # Extract organizations (simplified)
        organizations = []
        org_patterns = [
            r"(?:Ministério|Secretaria|Prefeitura|Câmara)\s+[\w\s]+",
            r"(?:Empresa|Companhia|Sociedade)\s+[\w\s]+",
        ]

        for pattern in org_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            organizations.extend(matches[:5])  # Limit to avoid clutter

        # Extract monetary values
        values = []
        money_matches = re.findall(r"R\$\s*([\d,.]+)", text, re.IGNORECASE)
        for match in money_matches[:10]:  # Limit matches
            try:
                amount = float(match.replace(".", "").replace(",", "."))
                values.append(
                    {"amount": amount, "context": f"Valor encontrado: R$ {match}"}
                )
            except ValueError:
                continue

        # Extract dates
        dates = []
        date_patterns = [
            r"(\d{1,2})/(\d{1,2})/(\d{4})",
            r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})",
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches[:5]:
                dates.append(
                    {
                        "date": (
                            "/".join(match) if "/" in pattern else " de ".join(match)
                        ),
                        "event": "Data identificada no documento",
                    }
                )

        # Extract people names (simplified)
        people = []
        # This would need a proper NER model for better results

        # Extract locations
        locations = []
        location_patterns = [
            r"(?:Estado|Município)\s+(?:de|do|da)\s+([\w\s]+)",
            r"(Brasília|São Paulo|Rio de Janeiro|Belo Horizonte)",
        ]

        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            locations.extend(matches[:5])

        # Extract legal references
        legal_refs = []
        legal_patterns = [
            r"Lei\s+n?º?\s*[\d./-]+",
            r"Art\.?\s*\d+[º°]?",
            r"CF/\d{2}",
        ]

        for pattern in legal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            legal_refs.extend(matches[:10])

        return EntityExtraction(
            organizations=list(set(organizations))[:10],
            values=values,
            dates=dates,
            people=people,
            locations=list(set(locations))[:5],
            legal_references=list(set(legal_refs))[:10],
        )

    async def _detect_document_alerts(
        self, text: str, doc_type: DocumentType
    ) -> list[DocumentAlert]:
        """Detect alerts and suspicious patterns in document."""

        alerts = []

        # Check for suspicious patterns
        for pattern_name, pattern in self._suspicious_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 50)
                excerpt = text[context_start:context_end].strip()

                alerts.append(
                    DocumentAlert(
                        alert_type=pattern_name,
                        excerpt=excerpt,
                        legal_violation=(
                            "Lei 8.666/93"
                            if pattern_name in ["urgency_abuse", "exclusive_criteria"]
                            else None
                        ),
                        severity=(
                            AlertSeverity.HIGH
                            if pattern_name == "urgency_abuse"
                            else AlertSeverity.MEDIUM
                        ),
                        confidence=0.75,
                        explanation=f"Padrão suspeito detectado: {pattern_name}",
                        recommendation="Revisar critérios e justificativas",
                    )
                )

        # Check for ambiguous language
        ambiguous_terms = [
            "conforme",
            "adequado",
            "satisfatório",
            "apropriado",
            "razoável",
        ]
        for term in ambiguous_terms:
            if term in text.lower() and text.lower().count(term) > 3:
                alerts.append(
                    DocumentAlert(
                        alert_type="ambiguity",
                        excerpt=f"Termo '{term}' usado frequentemente",
                        legal_violation=None,
                        severity=AlertSeverity.LOW,
                        confidence=0.6,
                        explanation=f"Uso excessivo de linguagem ambígua: '{term}'",
                        recommendation="Especificar critérios objetivos",
                    )
                )

        return alerts[:20]  # Limit alerts

    async def _calculate_complexity_score(self, text: str) -> float:
        """Calculate text complexity using adapted Flesch formula."""

        sentences = len(re.findall(r"[.!?]+", text))
        words = len(text.split())
        syllables = sum(self._count_syllables(word) for word in text.split())

        if sentences == 0 or words == 0:
            return 1.0  # Maximum complexity

        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words

        # Adapted Flesch formula for Portuguese
        flesch_score = (
            248.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        )

        # Convert to 0-1 scale (higher = more complex)
        complexity = max(0.0, min(1.0, (100 - flesch_score) / 100))

        return round(complexity, 3)

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a Portuguese word (simplified)."""
        vowels = "aeiouAEIOU"
        count = 0
        previous_was_vowel = False

        for char in word:
            if char in vowels:
                if not previous_was_vowel:
                    count += 1
                previous_was_vowel = True
            else:
                previous_was_vowel = False

        return max(1, count)  # At least one syllable

    async def _calculate_transparency_score(
        self, text: str, entities: EntityExtraction
    ) -> float:
        """Calculate document transparency score."""

        score = 0.0

        # Check for specific information
        if entities.values:  # Has monetary values
            score += 0.3

        if entities.dates:  # Has specific dates
            score += 0.2

        if entities.organizations:  # Identifies organizations
            score += 0.2

        if entities.legal_references:  # References legal framework
            score += 0.2

        # Check for transparency indicators
        transparency_indicators = [
            "justificativa",
            "critério",
            "metodologia",
            "público",
            "transparente",
            "acesso",
            "divulgação",
        ]

        indicator_count = sum(
            1 for indicator in transparency_indicators if indicator in text.lower()
        )

        score += min(0.1, indicator_count / len(transparency_indicators))

        return round(min(1.0, score), 3)

    async def _assess_legal_compliance(
        self, text: str, doc_type: DocumentType
    ) -> float:
        """Assess legal compliance based on document type."""

        compliance_score = 0.5  # Base score

        # Check for required legal references based on document type
        if doc_type in [DocumentType.CONTRACT, DocumentType.PUBLIC_TENDER]:
            if "8.666" in text or "14.133" in text:
                compliance_score += 0.3
            if "art." in text.lower() or "artigo" in text.lower():
                compliance_score += 0.2

        # Check for common compliance issues
        compliance_issues = [
            ("urgente", -0.1),  # Unjustified urgency
            ("sigiloso", -0.1),  # Inappropriate secrecy
            ("exclusivo", -0.1),  # Exclusive criteria
        ]

        for term, penalty in compliance_issues:
            if term in text.lower():
                compliance_score += penalty

        return round(max(0.0, min(1.0, compliance_score)), 3)

    async def _calculate_readability_grade(self, text: str) -> int:
        """Calculate readability grade level."""

        sentences = len(re.findall(r"[.!?]+", text))
        words = len(text.split())

        if sentences == 0:
            return 20  # Maximum difficulty

        avg_sentence_length = words / sentences

        # Simplified grade calculation
        if avg_sentence_length <= 10:
            return 6  # Elementary
        elif avg_sentence_length <= 15:
            return 8  # Middle school
        elif avg_sentence_length <= 20:
            return 12  # High school
        else:
            return 16  # College level

    async def _detect_suspicious_patterns(self, text: str) -> list[str]:
        """Detect suspicious patterns in document."""

        patterns_found = []

        for pattern_name, pattern in self._suspicious_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                patterns_found.append(pattern_name)

        return patterns_found

    async def _generate_document_insights(
        self, analysis: TextualAnalysisResult, request: TextualAnalysisRequest
    ) -> list[dict[str, Any]]:
        """Generate actionable insights from document analysis."""

        insights = []

        # Complexity insight
        if analysis.complexity_score > 0.8:
            insights.append(
                {
                    "type": "complexity_warning",
                    "message": "Documento apresenta alta complexidade linguística",
                    "recommendation": "Simplificar linguagem para melhor compreensão pública",
                    "impact": "high",
                }
            )

        # Transparency insight
        if analysis.transparency_score < 0.5:
            insights.append(
                {
                    "type": "transparency_concern",
                    "message": "Documento apresenta baixo nível de transparência",
                    "recommendation": "Incluir mais detalhes específicos e referências",
                    "impact": "medium",
                }
            )

        # Alert summary
        if analysis.alerts:
            high_severity_alerts = [a for a in analysis.alerts if a.severity.value >= 3]
            if high_severity_alerts:
                insights.append(
                    {
                        "type": "compliance_risk",
                        "message": f"Identificados {len(high_severity_alerts)} alertas de alta gravidade",
                        "recommendation": "Revisar e corrigir questões identificadas antes da publicação",
                        "impact": "critical",
                    }
                )

        return insights
