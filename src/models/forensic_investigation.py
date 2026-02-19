"""
Module: models.forensic_investigation
Description: Forensic Investigation Models - Ultra-detailed investigation data structures
Author: Anderson Henrique da Silva
Date: 2025-10-07 17:59:00
License: Proprietary - All rights reserved

This module defines comprehensive data models for storing detailed forensic
evidence, legal references, and documentary proof for government transparency.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class AnomalySeverity(str, Enum):
    """Severity levels for anomalies."""

    CRITICAL = "critical"  # Suspeita forte de irregularidade grave
    HIGH = "high"  # Irregularidade significativa
    MEDIUM = "medium"  # Padrão suspeito que merece atenção
    LOW = "low"  # Desvio menor, monitoramento recomendado
    INFO = "info"  # Informativo, sem suspeita


class EvidenceType(str, Enum):
    """Types of evidence collected."""

    DOCUMENT = "document"  # Documento oficial
    STATISTICAL = "statistical"  # Análise estatística
    COMPARATIVE = "comparative"  # Comparação com outros casos
    TEMPORAL = "temporal"  # Análise temporal/padrões
    FINANCIAL = "financial"  # Análise financeira
    LEGAL = "legal"  # Base legal/jurídica
    WITNESS = "witness"  # Declarações/testemunhos públicos
    OPEN_DATA = "open_data"  # Dados abertos gov.br


@dataclass
class OfficialDocument:
    """Official government document with full traceability."""

    title: str
    document_type: str  # edital, contrato, nota_fiscal, processo, etc
    document_number: str | None = None
    url: str | None = None  # Link direto ao documento
    portal_url: str | None = None  # Portal da Transparência
    issue_date: datetime | None = None
    issuing_authority: str | None = None
    legal_basis: str | None = None  # Base legal aplicável
    hash_verification: str | None = None  # Hash para verificação
    access_date: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: str | None = None


@dataclass
class LegalEntity:
    """Complete information about a legal entity (supplier, contractor, etc)."""

    name: str
    entity_type: str  # empresa, pessoa_fisica, orgao_publico

    # Identificação
    cnpj: str | None = None
    cpf: str | None = None
    company_registration: str | None = None  # Inscrição estadual/municipal

    # Contato
    address: str | None = None
    city: str | None = None
    state: str | None = None
    phone: str | None = None
    email: str | None = None

    # Links e Referências
    receita_federal_url: str | None = None
    transparency_portal_url: str | None = None
    company_website: str | None = None

    # Histórico
    foundation_date: datetime | None = None
    previous_contracts_count: int = 0
    previous_irregularities: list[str] = field(default_factory=list)
    total_contracted_value: float | None = None

    # Status Legal
    legal_status: str | None = None  # ativa, suspensa, inidônea
    sanctions: list[dict[str, Any]] = field(default_factory=list)

    # Metadata
    last_updated: datetime = field(default_factory=lambda: datetime.now(UTC))
    data_sources: list[str] = field(default_factory=list)


@dataclass
class Evidence:
    """Piece of evidence supporting an anomaly finding."""

    evidence_id: str
    evidence_type: EvidenceType
    title: str
    description: str

    # Conteúdo da evidência
    data: dict[str, Any]  # Dados estruturados da evidência

    # Análise
    analysis_method: str  # Como foi obtida/analisada

    # Optional fields with defaults
    raw_data: str | None = None  # Dados brutos se aplicável
    confidence_score: float = 1.0  # 0-1, confiança na evidência

    # Referências
    source_documents: list[OfficialDocument] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)

    # Comparações
    comparison_baseline: str | None = None  # O que foi usado como referência
    deviation_percentage: float | None = None
    statistical_significance: float | None = None  # p-value

    # Metadata
    collected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    verified: bool = False
    verification_notes: str | None = None


@dataclass
class FinancialImpact:
    """Detailed financial impact analysis."""

    # Valores
    contract_value: float
    expected_value: float | None = None  # Valor esperado/normal
    overcharge_amount: float | None = None  # Sobrepreço identificado
    potential_savings: float | None = None  # Economia potencial

    # Análise Comparativa
    market_average: float | None = None
    previous_contracts_average: float | None = None
    similar_contracts: list[dict[str, Any]] = field(default_factory=list)

    # Classificação Orçamentária
    budget_source: str | None = None  # Fonte de recurso
    budget_category: str | None = None
    fiscal_year: int | None = None

    # Impacto
    affected_population: int | None = None  # Pessoas afetadas
    opportunity_cost: str | None = None  # O que poderia ser feito com o valor

    # Cálculos
    calculation_method: str | None = None
    calculation_notes: str | None = None


@dataclass
class Timeline:
    """Detailed timeline of events related to the anomaly."""

    event_date: datetime
    event_type: str  # licitacao, assinatura, pagamento, fiscalizacao, etc
    description: str
    relevance: str  # Por que esse evento é relevante

    # Documentação
    related_documents: list[OfficialDocument] = field(default_factory=list)
    responsible_party: str | None = None

    # Análise
    suspicious_aspects: list[str] = field(default_factory=list)
    legal_implications: str | None = None


@dataclass
class LegalFramework:
    """Legal framework and regulatory context."""

    # Legislação Aplicável
    applicable_laws: list[str] = field(default_factory=list)  # Lei 8666/93, etc
    regulations: list[str] = field(default_factory=list)
    jurisprudence: list[str] = field(default_factory=list)  # Precedentes

    # Órgãos Competentes
    oversight_bodies: list[str] = field(default_factory=list)  # TCU, CGU, MPF
    jurisdiction: str | None = None  # Federal, estadual, municipal

    # Procedimentos
    required_procedures: list[str] = field(default_factory=list)
    procedures_followed: list[str] = field(default_factory=list)
    procedures_violated: list[str] = field(default_factory=list)

    # Penalidades Possíveis
    possible_sanctions: list[str] = field(default_factory=list)
    responsible_parties: list[str] = field(default_factory=list)


@dataclass
class RecommendedAction:
    """Recommended action with full justification."""

    action_type: str  # investigacao, auditoria, denuncia, recurso
    priority: str  # urgente, alta, media, baixa
    title: str
    description: str

    # Justificativa
    rationale: str  # Por que essa ação é recomendada
    expected_outcome: str  # Resultado esperado

    # Execução
    responsible_body: str | None = None  # Quem deve executar
    contact_info: str | None = None
    submission_url: str | None = None
    required_documents: list[str] = field(default_factory=list)

    # Prazos
    recommended_deadline: datetime | None = None
    legal_deadline: datetime | None = None

    # Referências
    legal_basis: list[str] = field(default_factory=list)
    similar_cases: list[str] = field(default_factory=list)


@dataclass
class ForensicAnomalyResult:
    """Ultra-detailed anomaly result with full forensic evidence."""

    # Identificação
    anomaly_id: str
    anomaly_type: str
    severity: AnomalySeverity

    # Título e Descrição Executiva
    title: str
    executive_summary: str  # Resumo executivo (2-3 parágrafos)
    detailed_description: str  # Descrição completa e técnica

    # O QUE foi detectado
    what_happened: str  # Descrição clara do que aconteceu

    # COMO foi detectado
    detection_method: str  # Como o sistema detectou
    analysis_methodology: str  # Metodologia de análise aplicada

    # POR QUE é suspeito/irregular
    why_suspicious: str  # Explicação clara das irregularidades
    legal_violations: list[str] = field(default_factory=list)

    # Confiança e Qualidade
    confidence_score: float = 0.0  # 0-1
    data_quality_score: float = 0.0  # 0-1
    completeness_score: float = 0.0  # 0-1

    # ENTIDADES ENVOLVIDAS
    involved_entities: list[LegalEntity] = field(default_factory=list)

    # DOCUMENTAÇÃO E EVIDÊNCIAS
    official_documents: list[OfficialDocument] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    # ANÁLISE FINANCEIRA
    financial_impact: FinancialImpact | None = None

    # CRONOLOGIA
    timeline: list[Timeline] = field(default_factory=list)

    # CONTEXTO LEGAL
    legal_framework: LegalFramework | None = None

    # COMPARAÇÕES E BENCHMARK
    similar_cases: list[dict[str, Any]] = field(default_factory=list)
    statistical_comparison: dict[str, Any] | None = None

    # AÇÕES RECOMENDADAS
    recommended_actions: list[RecommendedAction] = field(default_factory=list)

    # FONTES E RASTREABILIDADE
    data_sources: list[str] = field(default_factory=list)
    api_endpoints_used: list[str] = field(default_factory=list)
    external_references: list[str] = field(default_factory=list)

    # VISUALIZAÇÕES
    charts: list[dict[str, Any]] = field(default_factory=list)
    visualizations_urls: list[str] = field(default_factory=list)

    # METADATA
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    analyzed_by: str = "Cidadão.AI"
    analysis_version: str = "1.0"
    last_updated: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Para Auditoria
    reproducible: bool = True
    reproducibility_notes: str | None = None
    peer_reviewed: bool = False
    review_notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "anomaly_id": self.anomaly_id,
            "anomaly_type": self.anomaly_type,
            "severity": self.severity.value,
            "title": self.title,
            "executive_summary": self.executive_summary,
            "detailed_description": self.detailed_description,
            "what_happened": self.what_happened,
            "detection_method": self.detection_method,
            "analysis_methodology": self.analysis_methodology,
            "why_suspicious": self.why_suspicious,
            "legal_violations": self.legal_violations,
            "confidence_score": self.confidence_score,
            "data_quality_score": self.data_quality_score,
            "completeness_score": self.completeness_score,
            "involved_entities": [
                {
                    "name": e.name,
                    "type": e.entity_type,
                    "cnpj": e.cnpj,
                    "cpf": e.cpf,
                    "address": e.address,
                    "city": e.city,
                    "state": e.state,
                    "transparency_portal_url": e.transparency_portal_url,
                    "previous_contracts_count": e.previous_contracts_count,
                    "legal_status": e.legal_status,
                    "sanctions": e.sanctions,
                }
                for e in self.involved_entities
            ],
            "official_documents": [
                {
                    "title": d.title,
                    "type": d.document_type,
                    "number": d.document_number,
                    "url": d.url,
                    "portal_url": d.portal_url,
                    "issue_date": d.issue_date.isoformat() if d.issue_date else None,
                    "issuing_authority": d.issuing_authority,
                    "legal_basis": d.legal_basis,
                }
                for d in self.official_documents
            ],
            "evidence": [
                {
                    "id": e.evidence_id,
                    "type": e.evidence_type.value,
                    "title": e.title,
                    "description": e.description,
                    "data": e.data,
                    "analysis_method": e.analysis_method,
                    "confidence_score": e.confidence_score,
                    "source_urls": e.source_urls,
                    "deviation_percentage": e.deviation_percentage,
                    "statistical_significance": e.statistical_significance,
                }
                for e in self.evidence
            ],
            "financial_impact": (
                {
                    "contract_value": self.financial_impact.contract_value,
                    "expected_value": self.financial_impact.expected_value,
                    "overcharge_amount": self.financial_impact.overcharge_amount,
                    "potential_savings": self.financial_impact.potential_savings,
                    "market_average": self.financial_impact.market_average,
                    "similar_contracts": self.financial_impact.similar_contracts,
                    "opportunity_cost": self.financial_impact.opportunity_cost,
                }
                if self.financial_impact
                else None
            ),
            "timeline": [
                {
                    "date": t.event_date.isoformat(),
                    "type": t.event_type,
                    "description": t.description,
                    "relevance": t.relevance,
                    "suspicious_aspects": t.suspicious_aspects,
                }
                for t in self.timeline
            ],
            "legal_framework": (
                {
                    "applicable_laws": self.legal_framework.applicable_laws,
                    "oversight_bodies": self.legal_framework.oversight_bodies,
                    "procedures_violated": self.legal_framework.procedures_violated,
                    "possible_sanctions": self.legal_framework.possible_sanctions,
                }
                if self.legal_framework
                else None
            ),
            "recommended_actions": [
                {
                    "type": a.action_type,
                    "priority": a.priority,
                    "title": a.title,
                    "description": a.description,
                    "rationale": a.rationale,
                    "expected_outcome": a.expected_outcome,
                    "responsible_body": a.responsible_body,
                    "submission_url": a.submission_url,
                    "legal_basis": a.legal_basis,
                }
                for a in self.recommended_actions
            ],
            "data_sources": self.data_sources,
            "created_at": self.created_at.isoformat(),
            "analyzed_by": self.analyzed_by,
            "reproducible": self.reproducible,
        }
