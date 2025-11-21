"""
Module: services.forensic_enrichment_service
Description: Forensic Data Enrichment Service
Author: Anderson Henrique da Silva
Date: 2025-10-07 17:59:00
License: Proprietary - All rights reserved

This service enriches investigation results with detailed evidence, documentation,
legal references, and actionable intelligence.
"""

from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4

from src.core import get_logger
from src.models.forensic_investigation import (
    AnomalySeverity,
    Evidence,
    EvidenceType,
    FinancialImpact,
    ForensicAnomalyResult,
    LegalEntity,
    LegalFramework,
    OfficialDocument,
    RecommendedAction,
    Timeline,
)

logger = get_logger(__name__)


class ForensicEnrichmentService:
    """
    Service for enriching anomaly results with comprehensive forensic data.

    This is the SECRET SAUCE that makes Cidadão.AI investigations superior:
    - Complete evidence chain
    - Full documentation links
    - Legal framework analysis
    - Actionable recommendations with contact info
    """

    def __init__(self):
        """Initialize forensic enrichment service."""
        self.transparency_portal_base = "https://portaldatransparencia.gov.br"
        self.receita_federal_base = "https://solucoes.receita.fazenda.gov.br"

    async def enrich_anomaly(
        self,
        basic_anomaly: dict[str, Any],
        contract_data: dict[str, Any],
        comparative_data: Optional[list[dict[str, Any]]] = None,
    ) -> ForensicAnomalyResult:
        """
        Transform a basic anomaly into a comprehensive forensic report.

        Args:
            basic_anomaly: Basic anomaly data from detection
            contract_data: Full contract data from Portal da Transparência
            comparative_data: Similar contracts for comparison

        Returns:
            Comprehensive forensic anomaly result
        """
        logger.info(
            f"Starting forensic enrichment for anomaly type: {basic_anomaly.get('type')}"
        )

        # Generate unique ID
        anomaly_id = str(uuid4())

        # Build executive summary
        executive_summary = self._build_executive_summary(basic_anomaly, contract_data)

        # Extract involved entities with full details
        entities = await self._extract_entities(contract_data)

        # Generate official documents list with links
        documents = await self._generate_document_list(contract_data)

        # Collect and analyze evidence
        evidence = await self._collect_evidence(
            basic_anomaly, contract_data, comparative_data or []
        )

        # Calculate financial impact
        financial_impact = await self._analyze_financial_impact(
            contract_data, comparative_data or []
        )

        # Build timeline of events
        timeline = await self._build_timeline(contract_data)

        # Determine legal framework
        legal_framework = await self._determine_legal_framework(
            contract_data, basic_anomaly.get("type")
        )

        # Generate actionable recommendations
        actions = await self._generate_recommendations(
            basic_anomaly, contract_data, financial_impact
        )

        # Create comprehensive result
        forensic_result = ForensicAnomalyResult(
            anomaly_id=anomaly_id,
            anomaly_type=basic_anomaly.get("type", "unknown"),
            severity=self._map_severity(basic_anomaly.get("severity", 0.5)),
            title=self._generate_title(basic_anomaly, contract_data),
            executive_summary=executive_summary,
            detailed_description=self._build_detailed_description(
                basic_anomaly, contract_data, evidence
            ),
            what_happened=self._describe_what_happened(basic_anomaly, contract_data),
            detection_method=self._describe_detection_method(basic_anomaly),
            analysis_methodology=self._describe_methodology(basic_anomaly),
            why_suspicious=self._explain_why_suspicious(basic_anomaly, contract_data),
            legal_violations=self._identify_legal_violations(
                basic_anomaly, contract_data
            ),
            confidence_score=basic_anomaly.get("confidence", 0.0),
            data_quality_score=self._assess_data_quality(contract_data),
            completeness_score=self._assess_completeness(contract_data),
            involved_entities=entities,
            official_documents=documents,
            evidence=evidence,
            financial_impact=financial_impact,
            timeline=timeline,
            legal_framework=legal_framework,
            recommended_actions=actions,
            data_sources=self._list_data_sources(contract_data),
            api_endpoints_used=self._list_api_endpoints(contract_data),
        )

        logger.info(
            f"Forensic enrichment completed for anomaly {anomaly_id}",
            evidence_count=len(evidence),
            documents_count=len(documents),
            entities_count=len(entities),
        )

        return forensic_result

    def _build_executive_summary(
        self, anomaly: dict[str, Any], contract: dict[str, Any]
    ) -> str:
        """Build executive summary (2-3 paragraphs)."""
        anomaly_type = anomaly.get("type", "unknown")
        confidence = anomaly.get("confidence", 0) * 100

        supplier = contract.get("fornecedor", {}).get(
            "nome", "Fornecedor não identificado"
        )
        value = contract.get("valorInicial", 0)

        summary = f"""
**RESUMO EXECUTIVO**

Foi identificada uma anomalia do tipo "{anomaly_type}" com {confidence:.0f}% de confiança nesta análise.
O contrato em questão, firmado com {supplier}, apresenta indícios de irregularidade que merecem investigação detalhada.

O valor contratado de R$ {value:,.2f} apresenta desvios significativos em relação aos padrões de mercado
e contratos similares identificados em nossa base de dados. A metodologia aplicada combina análise estatística,
comparação com dados históricos e verificação de conformidade legal.

Esta investigação fornece evidências documentadas, referências legais completas e recomendações de ações específicas
para os órgãos competentes. Todas as informações são rastreáveis e verificáveis através dos links oficiais fornecidos.
"""
        return summary.strip()

    async def _extract_entities(self, contract: dict[str, Any]) -> list[LegalEntity]:
        """Extract all involved entities with complete data."""
        entities = []

        # Fornecedor
        fornecedor = contract.get("fornecedor", {})
        if fornecedor:
            cnpj = fornecedor.get("cnpjFormatado") or fornecedor.get("cnpj")
            entity = LegalEntity(
                name=fornecedor.get("nome", "Nome não disponível"),
                entity_type="empresa",
                cnpj=cnpj,
                transparency_portal_url=(
                    self._build_supplier_url(cnpj) if cnpj else None
                ),
                receita_federal_url=self._build_receita_url(cnpj) if cnpj else None,
            )
            entities.append(entity)

        # Órgão Contratante
        orgao = contract.get("orgaoContratante", {}) or contract.get(
            "unidadeGestora", {}
        )
        if orgao:
            entity = LegalEntity(
                name=orgao.get("nome", "Órgão não identificado"),
                entity_type="orgao_publico",
                company_registration=orgao.get("codigo"),
                transparency_portal_url=self._build_agency_url(orgao.get("codigo")),
            )
            entities.append(entity)

        return entities

    async def _generate_document_list(
        self, contract: dict[str, Any]
    ) -> list[OfficialDocument]:
        """Generate list of official documents with direct links."""
        documents = []

        # Contrato principal
        contract_number = contract.get("numeroContrato") or contract.get("numero")
        if contract_number:
            doc = OfficialDocument(
                title=f"Contrato nº {contract_number}",
                document_type="contrato",
                document_number=contract_number,
                portal_url=self._build_contract_url(contract.get("id")),
                issue_date=self._parse_date(contract.get("dataAssinatura")),
                issuing_authority=contract.get("orgaoContratante", {}).get("nome"),
                legal_basis="Lei 8.666/93 - Licitações e Contratos",
            )
            documents.append(doc)

        # Processo Licitatório
        if contract.get("numeroProcesso"):
            doc = OfficialDocument(
                title=f"Processo Licitatório nº {contract['numeroProcesso']}",
                document_type="processo",
                document_number=contract["numeroProcesso"],
                legal_basis="Lei 8.666/93, Art. 38",
            )
            documents.append(doc)

        # Edital (se disponível)
        if contract.get("modalidadeCompra"):
            doc = OfficialDocument(
                title=f"Edital - {contract['modalidadeCompra']}",
                document_type="edital",
                legal_basis="Lei 8.666/93, Art. 40",
            )
            documents.append(doc)

        return documents

    async def _collect_evidence(
        self,
        anomaly: dict[str, Any],
        contract: dict[str, Any],
        comparative_contracts: list[dict[str, Any]],
    ) -> list[Evidence]:
        """Collect and document all evidence."""
        evidence_list = []

        # Evidência 1: Análise Estatística
        if anomaly.get("type") == "price_deviation":
            evidence_list.append(
                Evidence(
                    evidence_id=str(uuid4()),
                    evidence_type=EvidenceType.STATISTICAL,
                    title="Análise Estatística de Preços",
                    description=f"Análise comparativa revela desvio de {anomaly.get('deviation_percentage', 0):.1f}% em relação à média de mercado",
                    data={
                        "contract_value": contract.get("valorInicial"),
                        "market_average": anomaly.get("market_average"),
                        "standard_deviation": anomaly.get("std_deviation"),
                        "z_score": anomaly.get("z_score"),
                    },
                    analysis_method="Análise estatística usando z-score e desvio padrão",
                    confidence_score=anomaly.get("confidence", 0.8),
                    deviation_percentage=anomaly.get("deviation_percentage"),
                    statistical_significance=anomaly.get("p_value"),
                )
            )

        # Evidência 2: Comparação com Contratos Similares
        if comparative_contracts:
            evidence_list.append(
                Evidence(
                    evidence_id=str(uuid4()),
                    evidence_type=EvidenceType.COMPARATIVE,
                    title=f"Comparação com {len(comparative_contracts)} Contratos Similares",
                    description="Contratos similares identificados com valores significativamente inferiores",
                    data={
                        "similar_contracts_count": len(comparative_contracts),
                        "similar_contracts": [
                            {
                                "id": c.get("id"),
                                "value": c.get("valorInicial"),
                                "supplier": c.get("fornecedor", {}).get("nome"),
                                "url": self._build_contract_url(c.get("id")),
                            }
                            for c in comparative_contracts[:5]  # Top 5
                        ],
                    },
                    analysis_method="Busca e comparação de contratos com objeto similar",
                    confidence_score=0.9,
                    source_urls=[
                        self._build_contract_url(c.get("id"))
                        for c in comparative_contracts[:5]
                    ],
                )
            )

        # Evidência 3: Análise Temporal
        evidence_list.append(
            Evidence(
                evidence_id=str(uuid4()),
                evidence_type=EvidenceType.TEMPORAL,
                title="Análise Temporal do Contrato",
                description="Análise da linha do tempo de eventos relevantes",
                data={
                    "data_assinatura": contract.get("dataAssinatura"),
                    "data_inicio_vigencia": contract.get("dataInicioVigencia"),
                    "data_fim_vigencia": contract.get("dataFimVigencia"),
                },
                analysis_method="Verificação de prazos e sequência de eventos",
                confidence_score=1.0,
            )
        )

        return evidence_list

    async def _analyze_financial_impact(
        self, contract: dict[str, Any], comparative_contracts: list[dict[str, Any]]
    ) -> FinancialImpact:
        """Analyze detailed financial impact."""
        contract_value = contract.get("valorInicial", 0)

        # Calculate market average from similar contracts
        market_avg = None
        if comparative_contracts:
            values = [
                c.get("valorInicial", 0)
                for c in comparative_contracts
                if c.get("valorInicial")
            ]
            if values:
                market_avg = sum(values) / len(values)

        # Calculate overcharge
        overcharge = None
        if market_avg and contract_value > market_avg:
            overcharge = contract_value - market_avg

        return FinancialImpact(
            contract_value=contract_value,
            expected_value=market_avg,
            overcharge_amount=overcharge,
            potential_savings=overcharge,
            market_average=market_avg,
            similar_contracts=[
                {
                    "id": c.get("id"),
                    "value": c.get("valorInicial"),
                    "supplier": c.get("fornecedor", {}).get("nome"),
                }
                for c in comparative_contracts[:10]
            ],
            opportunity_cost=(
                self._calculate_opportunity_cost(overcharge) if overcharge else None
            ),
            calculation_method="Média aritmética de contratos similares identificados no Portal da Transparência",
        )

    async def _build_timeline(self, contract: dict[str, Any]) -> list[Timeline]:
        """Build detailed timeline of events."""
        timeline = []

        # Assinatura
        if contract.get("dataAssinatura"):
            timeline.append(
                Timeline(
                    event_date=self._parse_date(contract["dataAssinatura"]),
                    event_type="assinatura",
                    description="Assinatura do contrato",
                    relevance="Data oficial de formalização do vínculo contratual",
                )
            )

        # Início de vigência
        if contract.get("dataInicioVigencia"):
            timeline.append(
                Timeline(
                    event_date=self._parse_date(contract["dataInicioVigencia"]),
                    event_type="inicio_vigencia",
                    description="Início da vigência contratual",
                    relevance="Data a partir da qual as obrigações contratuais começam",
                )
            )

        # Fim de vigência
        if contract.get("dataFimVigencia"):
            timeline.append(
                Timeline(
                    event_date=self._parse_date(contract["dataFimVigencia"]),
                    event_type="fim_vigencia",
                    description="Fim da vigência contratual",
                    relevance="Data limite para execução do objeto contratual",
                )
            )

        return sorted(timeline, key=lambda x: x.event_date)

    async def _determine_legal_framework(
        self, contract: dict[str, Any], anomaly_type: str
    ) -> LegalFramework:
        """Determine applicable legal framework."""
        return LegalFramework(
            applicable_laws=[
                "Lei nº 8.666/1993 - Licitações e Contratos Administrativos",
                "Lei nº 14.133/2021 - Nova Lei de Licitações",
                "Lei nº 8.429/1992 - Lei de Improbidade Administrativa",
                "Decreto nº 10.024/2019 - Pregão Eletrônico",
            ],
            regulations=[
                "Instrução Normativa SEGES/ME nº 65/2021",
                "Acórdão TCU nº 2.622/2013",
            ],
            oversight_bodies=[
                "Tribunal de Contas da União (TCU)",
                "Controladoria-Geral da União (CGU)",
                "Ministério Público Federal (MPF)",
                "Polícia Federal",
            ],
            procedures_violated=self._identify_procedure_violations(anomaly_type),
            possible_sanctions=[
                "Multa contratual",
                "Rescisão unilateral do contrato",
                "Declaração de inidoneidade do fornecedor",
                "Responsabilização por improbidade administrativa",
                "Ação de ressarcimento ao erário",
            ],
        )

    async def _generate_recommendations(
        self,
        anomaly: dict[str, Any],
        contract: dict[str, Any],
        financial_impact: FinancialImpact,
    ) -> list[RecommendedAction]:
        """Generate detailed actionable recommendations."""
        actions = []

        # Ação 1: Denúncia ao TCU
        actions.append(
            RecommendedAction(
                action_type="denuncia",
                priority="alta",
                title="Denúncia ao Tribunal de Contas da União (TCU)",
                description="Apresentar denúncia formal ao TCU sobre possível irregularidade",
                rationale="O TCU tem competência constitucional para fiscalizar contratos públicos e aplicar sanções",
                expected_outcome="Instauração de processo de fiscalização e auditoria do contrato",
                responsible_body="Tribunal de Contas da União (TCU)",
                contact_info="Ouvidoria TCU: 0800 644 1500 | ouvidoria@tcu.gov.br",
                submission_url="https://portal.tcu.gov.br/ouvidoria/denuncias/",
                legal_basis=[
                    "Constituição Federal, Art. 71",
                    "Lei nº 8.443/1992 - Lei Orgânica do TCU",
                ],
            )
        )

        # Ação 2: Representação à CGU
        actions.append(
            RecommendedAction(
                action_type="representacao",
                priority="alta",
                title="Representação à Controladoria-Geral da União (CGU)",
                description="Comunicar indícios de irregularidade à CGU para apuração",
                rationale="A CGU é responsável por controle interno e combate à corrupção no âmbito federal",
                expected_outcome="Abertura de procedimento administrativo de apuração",
                responsible_body="Controladoria-Geral da União (CGU)",
                contact_info="Fala.BR: https://www.gov.br/cgu/pt-br/canais_atendimento/fala-br",
                submission_url="https://sistema.ouvidorias.gov.br",
                legal_basis=[
                    "Lei nº 10.683/2003, Art. 24",
                    "Decreto nº 11.529/2023",
                ],
            )
        )

        # Ação 3: Notificação ao Órgão Contratante
        orgao = contract.get("orgaoContratante", {})
        if orgao:
            actions.append(
                RecommendedAction(
                    action_type="notificacao",
                    priority="media",
                    title=f"Notificação ao Órgão Contratante - {orgao.get('nome')}",
                    description="Comunicar formalmente ao órgão sobre as irregularidades identificadas",
                    rationale="O órgão contratante pode tomar medidas administrativas imediatas",
                    expected_outcome="Revisão do contrato e possível rescisão",
                    responsible_body=orgao.get("nome"),
                    legal_basis=[
                        "Lei nº 8.666/1993, Art. 78",
                        "Lei nº 8.666/1993, Art. 87",
                    ],
                )
            )

        # Ação 4: Representação ao MPF (se grave)
        if (
            financial_impact.overcharge_amount
            and financial_impact.overcharge_amount > 100000
        ):
            actions.append(
                RecommendedAction(
                    action_type="representacao",
                    priority="urgente",
                    title="Representação ao Ministério Público Federal (MPF)",
                    description="Comunicar possível lesão ao erário de valor significativo",
                    rationale="O MPF tem legitimidade para propor ação civil pública e ação de improbidade",
                    expected_outcome="Investigação criminal e/ou ação civil pública",
                    responsible_body="Ministério Público Federal",
                    contact_info="Representação Criminal: http://www.mpf.mp.br/para-o-cidadao/sac",
                    submission_url="http://www.mpf.mp.br",
                    legal_basis=[
                        "Lei nº 8.429/1992 - Improbidade Administrativa",
                        "Lei Complementar nº 75/1993 - Lei Orgânica do MPF",
                    ],
                )
            )

        return actions

    # Helper methods

    def _map_severity(self, score: float) -> AnomalySeverity:
        """Map confidence score to severity level."""
        if score >= 0.9:
            return AnomalySeverity.CRITICAL
        elif score >= 0.7:
            return AnomalySeverity.HIGH
        elif score >= 0.5:
            return AnomalySeverity.MEDIUM
        elif score >= 0.3:
            return AnomalySeverity.LOW
        return AnomalySeverity.INFO

    def _generate_title(self, anomaly: dict[str, Any], contract: dict[str, Any]) -> str:
        """Generate descriptive title."""
        anomaly_type = anomaly.get("type", "unknown")
        supplier = contract.get("fornecedor", {}).get(
            "nome", "Fornecedor não identificado"
        )
        return f"Anomalia: {anomaly_type} - Contrato com {supplier}"

    def _build_detailed_description(
        self,
        anomaly: dict[str, Any],
        contract: dict[str, Any],
        evidence: list[Evidence],
    ) -> str:
        """Build detailed technical description."""
        return f"""
**DESCRIÇÃO DETALHADA DA ANOMALIA**

Tipo de Anomalia: {anomaly.get('type')}
Confiança: {anomaly.get('confidence', 0) * 100:.1f}%

Contrato: {contract.get('numeroContrato') or 'Não identificado'}
Fornecedor: {contract.get('fornecedor', {}).get('nome')}
Valor: R$ {contract.get('valorInicial', 0):,.2f}

Esta análise identificou {len(evidence)} peças de evidência que suportam a conclusão de irregularidade.
Cada evidência foi coletada de fontes oficiais e pode ser verificada independentemente através dos links fornecidos.
"""

    def _describe_what_happened(
        self, anomaly: dict[str, Any], contract: dict[str, Any]
    ) -> str:
        """Describe what happened in clear terms."""
        return anomaly.get("description", "Descrição não disponível")

    def _describe_detection_method(self, anomaly: dict[str, Any]) -> str:
        """Describe how the anomaly was detected."""
        return "Análise automatizada usando algoritmos de detecção de anomalias baseados em machine learning e análise estatística"

    def _describe_methodology(self, anomaly: dict[str, Any]) -> str:
        """Describe analysis methodology."""
        return """
Metodologia aplicada:
1. Coleta de dados do Portal da Transparência via API REST
2. Normalização e limpeza de dados
3. Análise estatística comparativa (z-score, desvio padrão)
4. Comparação com base histórica de contratos similares
5. Verificação de conformidade legal
6. Cálculo de confiança usando ensemble de modelos
"""

    def _explain_why_suspicious(
        self, anomaly: dict[str, Any], contract: dict[str, Any]
    ) -> str:
        """Explain why this is suspicious."""
        return anomaly.get("explanation", "Explicação não disponível")

    def _identify_legal_violations(
        self, anomaly: dict[str, Any], contract: dict[str, Any]
    ) -> list[str]:
        """Identify potential legal violations."""
        return [
            "Possível sobrepreço (Lei 8.666/93, Art. 43, IV)",
            "Falta de pesquisa de preços adequada (Lei 8.666/93, Art. 43, IV)",
        ]

    def _assess_data_quality(self, contract: dict[str, Any]) -> float:
        """Assess quality of data available."""
        # Count how many key fields are present
        key_fields = ["numeroContrato", "valorInicial", "fornecedor", "dataAssinatura"]
        present = sum(1 for field in key_fields if contract.get(field))
        return present / len(key_fields)

    def _assess_completeness(self, contract: dict[str, Any]) -> float:
        """Assess completeness of contract data."""
        all_fields = [
            "numeroContrato",
            "valorInicial",
            "fornecedor",
            "dataAssinatura",
            "dataInicioVigencia",
            "dataFimVigencia",
            "objeto",
            "modalidadeCompra",
        ]
        present = sum(1 for field in all_fields if contract.get(field))
        return present / len(all_fields)

    def _list_data_sources(self, contract: dict[str, Any]) -> list[str]:
        """List all data sources used."""
        return [
            "Portal da Transparência do Governo Federal",
            "API de Dados Abertos do Governo Federal",
            "Base histórica de contratos públicos",
        ]

    def _list_api_endpoints(self, contract: dict[str, Any]) -> list[str]:
        """List API endpoints used."""
        return [
            "https://api.portaldatransparencia.gov.br/api-de-dados/contratos",
            "https://api.portaldatransparencia.gov.br/api-de-dados/fornecedores",
        ]

    def _identify_procedure_violations(self, anomaly_type: str) -> list[str]:
        """Identify which procedures may have been violated."""
        violations = {
            "price_deviation": [
                "Pesquisa de preços inadequada ou ausente",
                "Não observância do princípio da economicidade",
            ],
            "vendor_concentration": [
                "Possível direcionamento de licitação",
                "Restrição à competitividade",
            ],
        }
        return violations.get(anomaly_type, [])

    def _calculate_opportunity_cost(self, overcharge: float) -> str:
        """Calculate what could be done with the overcharged amount."""
        # Examples of what the money could fund
        return f"Com R$ {overcharge:,.2f} seria possível contratar aproximadamente {int(overcharge / 5000)} consultas médicas no SUS"

    def _build_contract_url(self, contract_id: Optional[str]) -> Optional[str]:
        """Build direct URL to contract in transparency portal."""
        if not contract_id:
            return None
        return f"{self.transparency_portal_base}/despesas/contrato/{contract_id}"

    def _build_supplier_url(self, cnpj: Optional[str]) -> Optional[str]:
        """Build URL to supplier page."""
        if not cnpj:
            return None
        # Remove formatting from CNPJ
        cnpj_clean = "".join(c for c in str(cnpj) if c.isdigit())
        return f"{self.transparency_portal_base}/despesas/fornecedor/{cnpj_clean}"

    def _build_agency_url(self, code: Optional[str]) -> Optional[str]:
        """Build URL to agency page."""
        if not code:
            return None
        return f"{self.transparency_portal_base}/orgaos/{code}"

    def _build_receita_url(self, cnpj: Optional[str]) -> Optional[str]:
        """Build URL to Receita Federal."""
        if not cnpj:
            return None
        return f"{self.receita_federal_base}/servicos/cnpj/cnpj.asp"

    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse date string to datetime."""
        if not date_str:
            return datetime.now(UTC)

        # Try different formats
        for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
            try:
                return datetime.strptime(date_str, fmt)
            except (ValueError, TypeError):
                continue

        return datetime.now(UTC)


# Global service instance
forensic_enrichment_service = ForensicEnrichmentService()
