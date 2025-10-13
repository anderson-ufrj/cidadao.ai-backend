"""
Module: agents.tiradentes
Codinome: Tiradentes - Avaliador de Riscos
Description: Agent specialized in generating natural language reports from investigation and analysis results
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel
from pydantic import Field as PydanticField

from src.agents.deodoro import AgentContext, AgentMessage, AgentResponse, BaseAgent
from src.core import AgentStatus
from src.core.exceptions import AgentExecutionError
from src.services.export_service import export_service


class ReportFormat(str, Enum):
    """Supported report formats."""

    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    EXECUTIVE_SUMMARY = "executive_summary"


class ReportType(str, Enum):
    """Types of reports that can be generated."""

    INVESTIGATION_REPORT = "investigation_report"
    ANALYSIS_REPORT = "analysis_report"
    COMBINED_REPORT = "combined_report"
    EXECUTIVE_SUMMARY = "executive_summary"
    ANOMALY_SUMMARY = "anomaly_summary"
    TREND_ANALYSIS = "trend_analysis"


@dataclass
class ReportSection:
    """A section within a report."""

    title: str
    content: str
    subsections: list["ReportSection"] = None
    charts: list[dict[str, Any]] = None
    tables: list[dict[str, Any]] = None
    importance: int = 1  # 1-5 scale


class ReportRequest(BaseModel):
    """Request for report generation."""

    report_type: ReportType = PydanticField(description="Type of report to generate")
    format: ReportFormat = PydanticField(
        default=ReportFormat.MARKDOWN, description="Output format"
    )
    investigation_results: Optional[dict[str, Any]] = PydanticField(
        default=None, description="Investigation results from InvestigatorAgent"
    )
    analysis_results: Optional[dict[str, Any]] = PydanticField(
        default=None, description="Analysis results from AnalystAgent"
    )
    target_audience: str = PydanticField(
        default="technical", description="Target audience: technical, executive, public"
    )
    language: str = PydanticField(default="pt", description="Report language")
    include_visualizations: bool = PydanticField(
        default=True, description="Include charts and visualizations"
    )
    executive_summary: bool = PydanticField(
        default=True, description="Include executive summary"
    )
    detailed_findings: bool = PydanticField(
        default=True, description="Include detailed findings"
    )
    recommendations: bool = PydanticField(
        default=True, description="Include recommendations"
    )


class ReporterAgent(BaseAgent):
    """
    Agent specialized in generating natural language reports from investigation and analysis results.

    Capabilities:
    - Generate comprehensive investigation reports
    - Create pattern analysis reports
    - Produce executive summaries
    - Format reports in multiple formats (Markdown, HTML, PDF)
    - Adapt language and complexity to target audience
    - Include visualizations and data tables
    - Provide actionable recommendations
    - Generate public transparency reports
    """

    def __init__(
        self,
        default_language: str = "pt",
        max_report_length: int = 10000,  # words
    ):
        """
        Initialize the Reporter Agent.

        Args:
            default_language: Default language for reports
            max_report_length: Maximum report length in words
        """
        super().__init__(
            name="Tiradentes",
            description="Tiradentes - Agent specialized in generating natural language reports",
            capabilities=[
                "investigation_report_generation",
                "pattern_analysis_reporting",
                "executive_summary_creation",
                "multi_format_rendering",
                "audience_adaptation",
                "data_visualization",
                "recommendation_generation",
                "transparency_reporting",
            ],
            max_retries=3,
            timeout=60,
        )
        self.default_language = default_language
        self.max_length = max_report_length

        # Report generators registry
        self.report_generators = {
            ReportType.INVESTIGATION_REPORT: self._generate_investigation_report,
            ReportType.ANALYSIS_REPORT: self._generate_analysis_report,
            ReportType.COMBINED_REPORT: self._generate_combined_report,
            ReportType.EXECUTIVE_SUMMARY: self._generate_executive_summary,
            ReportType.ANOMALY_SUMMARY: self._generate_anomaly_summary,
            ReportType.TREND_ANALYSIS: self._generate_trend_analysis,
        }

        # Format renderers registry
        self.format_renderers = {
            ReportFormat.MARKDOWN: self._render_markdown,
            ReportFormat.HTML: self._render_html,
            ReportFormat.JSON: self._render_json,
            ReportFormat.PDF: self._render_pdf,
            ReportFormat.EXECUTIVE_SUMMARY: self._render_executive_summary,
        }

        self.logger.info(
            "tiradentes_initialized",
            agent_name=self.name,
            default_language=default_language,
            max_length=max_report_length,
        )

    async def initialize(self) -> None:
        """Initialize agent resources."""
        self.logger.info(f"{self.name} agent initialized")

    async def shutdown(self) -> None:
        """Cleanup agent resources."""
        self.logger.info(f"{self.name} agent shutting down")

    async def process(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        """
        Process report generation request and return formatted report.

        Args:
            message: Report request message
            context: Agent execution context

        Returns:
            AgentResponse with generated report
        """
        try:
            self.logger.info(
                "report_generation_started",
                investigation_id=context.investigation_id,
                agent_name=self.name,
                action=message.action,
            )

            # Parse report request
            if message.action == "generate_report":
                request = ReportRequest(**message.payload)
            else:
                raise AgentExecutionError(
                    f"Unsupported action: {message.action}", agent_id=self.name
                )

            # Validate input data
            if not request.investigation_results and not request.analysis_results:
                return AgentResponse(
                    agent_name=self.name,
                    status=AgentStatus.ERROR,
                    error="No data provided for report generation",
                    result={
                        "status": "error",
                        "error": "No data provided for report generation",
                        "investigation_id": context.investigation_id,
                    },
                    metadata={"investigation_id": context.investigation_id},
                )

            # Generate report content
            report_sections = await self._generate_report_content(request, context)

            # Render report in requested format
            formatted_report = await self._render_report(
                report_sections, request, context
            )

            # Create result message
            result = {
                "status": "completed",
                "report_type": request.report_type,
                "format": request.format,
                "content": formatted_report,
                "metadata": {
                    "investigation_id": context.investigation_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent_name": self.name,
                    "target_audience": request.target_audience,
                    "language": request.language,
                    "sections_count": len(report_sections),
                    "word_count": self._count_words(formatted_report),
                },
            }

            self.logger.info(
                "report_generation_completed",
                investigation_id=context.investigation_id,
                report_type=request.report_type,
                format=request.format,
                sections_count=len(report_sections),
            )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result=result,
                metadata={"investigation_id": context.investigation_id},
            )

        except Exception as e:
            self.logger.error(
                "report_generation_failed",
                investigation_id=context.investigation_id,
                error=str(e),
                agent_name=self.name,
            )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.ERROR,
                error=str(e),
                result={
                    "status": "error",
                    "error": str(e),
                    "investigation_id": context.investigation_id,
                },
                metadata={"investigation_id": context.investigation_id},
            )

    async def _generate_report_content(
        self, request: ReportRequest, context: AgentContext
    ) -> list[ReportSection]:
        """
        Generate report content sections based on the request.

        Args:
            request: Report generation request
            context: Agent context

        Returns:
            List of report sections
        """
        if request.report_type in self.report_generators:
            generator = self.report_generators[request.report_type]
            return await generator(request, context)
        else:
            raise AgentExecutionError(
                f"Unsupported report type: {request.report_type}", agent_id=self.name
            )

    async def _generate_investigation_report(
        self, request: ReportRequest, context: AgentContext
    ) -> list[ReportSection]:
        """Generate investigation report sections."""
        sections = []

        if not request.investigation_results:
            return sections

        inv_data = request.investigation_results
        anomalies = inv_data.get("anomalies", [])
        summary = inv_data.get("summary", {})

        # Executive Summary
        if request.executive_summary:
            exec_summary = self._create_executive_summary(
                inv_data, request.target_audience
            )
            sections.append(
                ReportSection(
                    title="Resumo Executivo", content=exec_summary, importance=5
                )
            )

        # Investigation Overview
        overview = self._create_investigation_overview(inv_data, summary)
        sections.append(
            ReportSection(
                title="Visão Geral da Investigação", content=overview, importance=4
            )
        )

        # Anomalies Analysis
        if anomalies and request.detailed_findings:
            anomaly_sections = self._create_anomaly_sections(
                anomalies, request.target_audience
            )
            sections.extend(anomaly_sections)

        # Risk Assessment
        risk_section = self._create_risk_assessment(summary, anomalies)
        sections.append(
            ReportSection(
                title="Avaliação de Risco", content=risk_section, importance=4
            )
        )

        # Recommendations
        if request.recommendations:
            recommendations = self._create_recommendations(anomalies, "investigation")
            sections.append(
                ReportSection(
                    title="Recomendações", content=recommendations, importance=5
                )
            )

        return sections

    async def _generate_analysis_report(
        self, request: ReportRequest, context: AgentContext
    ) -> list[ReportSection]:
        """Generate analysis report sections."""
        sections = []

        if not request.analysis_results:
            return sections

        analysis_data = request.analysis_results
        patterns = analysis_data.get("patterns", [])
        correlations = analysis_data.get("correlations", [])
        insights = analysis_data.get("insights", [])
        summary = analysis_data.get("summary", {})

        # Executive Summary
        if request.executive_summary:
            exec_summary = self._create_analysis_executive_summary(
                analysis_data, request.target_audience
            )
            sections.append(
                ReportSection(
                    title="Resumo Executivo da Análise",
                    content=exec_summary,
                    importance=5,
                )
            )

        # Data Overview
        overview = self._create_analysis_overview(analysis_data, summary)
        sections.append(
            ReportSection(title="Visão Geral dos Dados", content=overview, importance=4)
        )

        # Pattern Analysis
        if patterns and request.detailed_findings:
            pattern_sections = self._create_pattern_sections(
                patterns, request.target_audience
            )
            sections.extend(pattern_sections)

        # Correlation Analysis
        if correlations and request.detailed_findings:
            correlation_section = self._create_correlation_section(correlations)
            sections.append(
                ReportSection(
                    title="Análise de Correlações",
                    content=correlation_section,
                    importance=3,
                )
            )

        # Key Insights
        if insights:
            insights_section = self._create_insights_section(insights)
            sections.append(
                ReportSection(
                    title="Principais Insights", content=insights_section, importance=4
                )
            )

        # Recommendations
        if request.recommendations:
            recommendations = self._create_recommendations(patterns, "analysis")
            sections.append(
                ReportSection(
                    title="Recomendações Estratégicas",
                    content=recommendations,
                    importance=5,
                )
            )

        return sections

    async def _generate_combined_report(
        self, request: ReportRequest, context: AgentContext
    ) -> list[ReportSection]:
        """Generate combined investigation and analysis report."""
        sections = []

        # Generate both investigation and analysis sections
        inv_sections = await self._generate_investigation_report(request, context)
        analysis_sections = await self._generate_analysis_report(request, context)

        # Combined executive summary
        if request.executive_summary:
            combined_summary = self._create_combined_executive_summary(
                request.investigation_results,
                request.analysis_results,
                request.target_audience,
            )
            sections.append(
                ReportSection(
                    title="Resumo Executivo Consolidado",
                    content=combined_summary,
                    importance=5,
                )
            )

        # Add sections from both reports (avoiding duplicate executive summaries)
        for section in inv_sections:
            if "Resumo Executivo" not in section.title:
                sections.append(section)

        for section in analysis_sections:
            if "Resumo Executivo" not in section.title:
                sections.append(section)

        # Combined conclusions
        combined_conclusions = self._create_combined_conclusions(
            request.investigation_results, request.analysis_results
        )
        sections.append(
            ReportSection(
                title="Conclusões Consolidadas",
                content=combined_conclusions,
                importance=5,
            )
        )

        return sections

    async def _generate_executive_summary(
        self, request: ReportRequest, context: AgentContext
    ) -> list[ReportSection]:
        """Generate executive summary only."""
        sections = []

        summary_content = self._create_combined_executive_summary(
            request.investigation_results, request.analysis_results, "executive"
        )

        sections.append(
            ReportSection(
                title="Resumo Executivo", content=summary_content, importance=5
            )
        )

        return sections

    async def _generate_anomaly_summary(
        self, request: ReportRequest, context: AgentContext
    ) -> list[ReportSection]:
        """Generate anomaly-focused summary."""
        sections = []

        if request.investigation_results:
            anomalies = request.investigation_results.get("anomalies", [])

            if anomalies:
                # High priority anomalies
                high_priority = [a for a in anomalies if a.get("severity", 0) > 0.7]
                if high_priority:
                    content = self._create_high_priority_anomaly_summary(high_priority)
                    sections.append(
                        ReportSection(
                            title="Anomalias de Alta Prioridade",
                            content=content,
                            importance=5,
                        )
                    )

                # Anomaly categories
                categories = {}
                for anomaly in anomalies:
                    cat = anomaly.get("type", "unknown")
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(anomaly)

                for category, cat_anomalies in categories.items():
                    content = self._create_category_anomaly_summary(
                        category, cat_anomalies
                    )
                    sections.append(
                        ReportSection(
                            title=f"Anomalias: {category.replace('_', ' ').title()}",
                            content=content,
                            importance=3,
                        )
                    )

        return sections

    async def _generate_trend_analysis(
        self, request: ReportRequest, context: AgentContext
    ) -> list[ReportSection]:
        """Generate trend analysis report."""
        sections = []

        if request.analysis_results:
            patterns = request.analysis_results.get("patterns", [])

            # Filter for trend-related patterns
            trend_patterns = [
                p for p in patterns if "trend" in p.get("type", "").lower()
            ]

            if trend_patterns:
                content = self._create_trend_analysis_content(trend_patterns)
                sections.append(
                    ReportSection(
                        title="Análise de Tendências", content=content, importance=4
                    )
                )

        return sections

    def _create_executive_summary(self, inv_data: dict[str, Any], audience: str) -> str:
        """Create executive summary for investigation results."""
        summary = inv_data.get("summary", {})
        anomalies = inv_data.get("anomalies", [])

        total_records = summary.get("total_records", 0)
        anomalies_found = summary.get("anomalies_found", 0)
        risk_score = summary.get("risk_score", 0)
        suspicious_value = summary.get("suspicious_value", 0)

        if audience == "executive":
            return f"""
            **Síntese da Investigação**

            A análise de {total_records} contratos públicos identificou {anomalies_found} anomalias
            que requerem atenção. O nível de risco identificado é de {risk_score:.1f}/10, com
            valor suspeito estimado em R$ {suspicious_value:,.2f}.

            **Principais Achados:**
            • {len([a for a in anomalies if a.get("severity", 0) > 0.7])} anomalias de alta severidade
            • {len([a for a in anomalies if a.get("type") == "price_anomaly"])} casos de preços suspeitos
            • {len([a for a in anomalies if a.get("type") == "vendor_concentration"])} situações de concentração de fornecedores

            **Ação Requerida:** Investigação detalhada das anomalias de alta prioridade e implementação
            das recomendações de controle.
            """

        return f"""
        ## Resumo Executivo da Investigação

        ### Escopo da Análise
        - **Contratos analisados:** {total_records}
        - **Anomalias identificadas:** {anomalies_found}
        - **Score de risco:** {risk_score:.1f}/10
        - **Valor suspeito:** R$ {suspicious_value:,.2f}

        ### Principais Descobertas
        {self._format_anomaly_summary(anomalies)}

        ### Recomendações Imediatas
        1. Priorizar investigação das anomalias de alta severidade
        2. Implementar controles adicionais nos processos identificados
        3. Monitorar continuamente os padrões detectados
        """

    def _create_investigation_overview(
        self, inv_data: dict[str, Any], summary: dict[str, Any]
    ) -> str:
        """Create investigation overview section."""
        query = inv_data.get("query", "Investigação de contratos públicos")
        metadata = inv_data.get("metadata", {})

        return f"""
        ## Metodologia da Investigação

        **Consulta Original:** {query}

        **Parâmetros da Análise:**
        - Registros analisados: {summary.get("total_records", 0)}
        - Período: {metadata.get("timestamp", "N/A")[:10]}
        - Algoritmos utilizados: Detecção de anomalias estatísticas, análise de concentração, padrões temporais

        **Critérios de Detecção:**
        - Anomalias de preço: Desvios > 2.5 desvios padrão
        - Concentração de fornecedores: > 70% do valor total
        - Padrões temporais: Concentrações > 2 desvios padrão da média

        ## Resultados Gerais
        {self._format_summary_stats(summary)}
        """

    def _create_anomaly_sections(
        self, anomalies: list[dict[str, Any]], audience: str
    ) -> list[ReportSection]:
        """Create detailed anomaly sections."""
        sections = []

        # Group anomalies by type
        anomaly_groups = {}
        for anomaly in anomalies:
            atype = anomaly.get("type", "unknown")
            if atype not in anomaly_groups:
                anomaly_groups[atype] = []
            anomaly_groups[atype].append(anomaly)

        # Create section for each type
        for atype, group_anomalies in anomaly_groups.items():
            title = self._get_anomaly_type_title(atype)
            content = self._format_anomaly_group(group_anomalies, audience)

            sections.append(
                ReportSection(
                    title=title,
                    content=content,
                    importance=(
                        4
                        if any(a.get("severity", 0) > 0.7 for a in group_anomalies)
                        else 3
                    ),
                )
            )

        return sections

    def _create_risk_assessment(
        self, summary: dict[str, Any], anomalies: list[dict[str, Any]]
    ) -> str:
        """Create risk assessment section."""
        risk_score = summary.get("risk_score", 0)
        high_severity = summary.get("high_severity_count", 0)
        medium_severity = summary.get("medium_severity_count", 0)

        risk_level = (
            "BAIXO" if risk_score < 3 else "MÉDIO" if risk_score < 7 else "ALTO"
        )

        return f"""
        ## Avaliação de Risco Consolidada

        **Nível de Risco: {risk_level}** (Score: {risk_score:.1f}/10)

        ### Distribuição de Severidade
        - **Alta severidade:** {high_severity} anomalias
        - **Média severidade:** {medium_severity} anomalias
        - **Baixa severidade:** {summary.get("low_severity_count", 0)} anomalias

        ### Fatores de Risco Identificados
        {self._analyze_risk_factors(anomalies)}

        ### Impacto Financeiro Estimado
        Valor potencialmente afetado: R$ {summary.get("suspicious_value", 0):,.2f}

        ### Recomendações de Mitigação
        {self._generate_risk_mitigation_recommendations(risk_score, anomalies)}
        """

    def _create_recommendations(
        self, items: list[dict[str, Any]], report_type: str
    ) -> str:
        """Create recommendations section."""
        recommendations = set()

        for item in items:
            item_recs = item.get("recommendations", [])
            recommendations.update(item_recs)

        recommendations_list = list(recommendations)

        return f"""
        ## Recomendações {'de Investigação' if report_type == 'investigation' else 'Estratégicas'}

        ### Ações Prioritárias
        {self._format_priority_recommendations(recommendations_list[:5])}

        ### Ações Complementares
        {self._format_complementary_recommendations(recommendations_list[5:10])}

        ### Implementação e Monitoramento
        - Estabelecer cronograma de implementação das recomendações
        - Definir indicadores de acompanhamento
        - Realizar auditorias periódicas de verificação
        - Reportar progresso às autoridades competentes
        """

    async def _render_report(
        self,
        sections: list[ReportSection],
        request: ReportRequest,
        context: AgentContext,
    ) -> str:
        """
        Render report sections in the requested format.

        Args:
            sections: Report sections to render
            request: Report request with format specification
            context: Agent context

        Returns:
            Formatted report content
        """
        if request.format in self.format_renderers:
            renderer = self.format_renderers[request.format]
            return await renderer(sections, request, context)
        else:
            # Default to markdown
            return await self._render_markdown(sections, request, context)

    async def _render_markdown(
        self,
        sections: list[ReportSection],
        request: ReportRequest,
        context: AgentContext,
    ) -> str:
        """Render report in Markdown format."""
        report_lines = []

        # Report header
        report_lines.append(
            f"# Relatório: {request.report_type.value.replace('_', ' ').title()}"
        )
        report_lines.append(f"**Data:** {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}")
        report_lines.append(f"**ID da Investigação:** {context.investigation_id}")
        report_lines.append("")

        # Table of contents for long reports
        if len(sections) > 3:
            report_lines.append("## Índice")
            for i, section in enumerate(sections, 1):
                report_lines.append(f"{i}. {section.title}")
            report_lines.append("")

        # Render sections
        for section in sorted(sections, key=lambda s: s.importance, reverse=True):
            report_lines.append(f"## {section.title}")
            report_lines.append("")
            report_lines.append(section.content)
            report_lines.append("")

        # Report footer
        report_lines.append("---")
        report_lines.append(
            "*Relatório gerado automaticamente pelo sistema Cidadão.AI*"
        )

        return "\n".join(report_lines)

    async def _render_html(
        self,
        sections: list[ReportSection],
        request: ReportRequest,
        context: AgentContext,
    ) -> str:
        """Render report in HTML format."""
        html_parts = []

        # HTML header
        html_parts.append(
            """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório Cidadão.AI</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }
                h1 { color: #2c3e50; border-bottom: 3px solid #3498db; }
                h2 { color: #34495e; border-bottom: 1px solid #bdc3c7; }
                .metadata { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .high-priority { border-left: 5px solid #e74c3c; padding-left: 15px; }
                .medium-priority { border-left: 5px solid #f39c12; padding-left: 15px; }
                .low-priority { border-left: 5px solid #27ae60; padding-left: 15px; }
            </style>
        </head>
        <body>
        """
        )

        # Report content
        html_parts.append(
            f"<h1>Relatório: {request.report_type.value.replace('_', ' ').title()}</h1>"
        )
        html_parts.append(
            f"""
        <div class="metadata">
            <strong>Data:</strong> {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}<br>
            <strong>ID da Investigação:</strong> {context.investigation_id}<br>
            <strong>Público-alvo:</strong> {request.target_audience}
        </div>
        """
        )

        # Render sections
        for section in sorted(sections, key=lambda s: s.importance, reverse=True):
            priority_class = (
                "high-priority"
                if section.importance >= 4
                else "medium-priority" if section.importance >= 3 else "low-priority"
            )
            html_parts.append(f'<div class="{priority_class}">')
            html_parts.append(f"<h2>{section.title}</h2>")
            html_parts.append(f"<div>{self._markdown_to_html(section.content)}</div>")
            html_parts.append("</div>")

        # HTML footer
        html_parts.append(
            """
        <hr>
        <p><em>Relatório gerado automaticamente pelo sistema Cidadão.AI</em></p>
        </body>
        </html>
        """
        )

        return "\n".join(html_parts)

    async def _render_json(
        self,
        sections: list[ReportSection],
        request: ReportRequest,
        context: AgentContext,
    ) -> str:
        """Render report in JSON format."""
        import json

        report_data = {
            "report_metadata": {
                "type": request.report_type,
                "format": request.format,
                "generated_at": datetime.utcnow().isoformat(),
                "investigation_id": context.investigation_id,
                "target_audience": request.target_audience,
                "language": request.language,
            },
            "sections": [
                {
                    "title": section.title,
                    "content": section.content,
                    "importance": section.importance,
                    "subsections": section.subsections or [],
                    "charts": section.charts or [],
                    "tables": section.tables or [],
                }
                for section in sections
            ],
            "summary": {
                "total_sections": len(sections),
                "high_priority_sections": len(
                    [s for s in sections if s.importance >= 4]
                ),
                "word_count": sum(self._count_words(s.content) for s in sections),
            },
        }

        return json.dumps(report_data, indent=2, ensure_ascii=False)

    async def _render_executive_summary(
        self,
        sections: list[ReportSection],
        request: ReportRequest,
        context: AgentContext,
    ) -> str:
        """Render executive summary format."""
        # Find or create executive summary
        exec_sections = [s for s in sections if "executivo" in s.title.lower()]

        if exec_sections:
            return exec_sections[0].content

        # Create condensed summary from high-importance sections
        high_importance = [s for s in sections if s.importance >= 4]

        summary_parts = []
        summary_parts.append("# RESUMO EXECUTIVO")
        summary_parts.append("")

        for section in high_importance[:3]:  # Top 3 most important
            summary_parts.append(f"## {section.title}")
            # Extract first paragraph or key points
            content_lines = section.content.split("\n")
            key_content = []
            for line in content_lines:
                if line.strip() and len(key_content) < 3:
                    key_content.append(line.strip())
            summary_parts.extend(key_content)
            summary_parts.append("")

        return "\n".join(summary_parts)

    # Helper methods

    def _format_anomaly_summary(self, anomalies: list[dict[str, Any]]) -> str:
        """Format anomaly summary for executive overview."""
        if not anomalies:
            return "Nenhuma anomalia significativa detectada."

        high_severity = [a for a in anomalies if a.get("severity", 0) > 0.7]
        types = {}
        for anomaly in anomalies:
            atype = anomaly.get("type", "unknown")
            types[atype] = types.get(atype, 0) + 1

        lines = []
        if high_severity:
            lines.append(f"• **{len(high_severity)} anomalias críticas** identificadas")

        for atype, count in types.items():
            type_name = self._get_anomaly_type_name(atype)
            lines.append(f"• {count} casos de {type_name}")

        return "\n".join(lines)

    def _get_anomaly_type_title(self, atype: str) -> str:
        """Get human-readable title for anomaly type."""
        titles = {
            "price_anomaly": "Anomalias de Preço",
            "vendor_concentration": "Concentração de Fornecedores",
            "temporal_patterns": "Padrões Temporais Suspeitos",
            "duplicate_contracts": "Contratos Duplicados",
            "payment_patterns": "Padrões de Pagamento Irregulares",
        }
        return titles.get(atype, atype.replace("_", " ").title())

    def _get_anomaly_type_name(self, atype: str) -> str:
        """Get human-readable name for anomaly type."""
        names = {
            "price_anomaly": "preços suspeitos",
            "vendor_concentration": "concentração de fornecedores",
            "temporal_patterns": "padrões temporais irregulares",
            "duplicate_contracts": "contratos duplicados",
            "payment_patterns": "irregularidades de pagamento",
        }
        return names.get(atype, atype.replace("_", " "))

    def _format_summary_stats(self, summary: dict[str, Any]) -> str:
        """Format summary statistics."""
        return f"""
        **Estatísticas Consolidadas:**
        - Total de registros: {summary.get("total_records", 0):,}
        - Anomalias detectadas: {summary.get("anomalies_found", 0)}
        - Valor total analisado: R$ {summary.get("total_value", 0):,.2f}
        - Score de risco: {summary.get("risk_score", 0):.1f}/10
        """

    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())

    def _markdown_to_html(self, markdown_text: str) -> str:
        """Simple markdown to HTML conversion."""
        html = markdown_text
        html = html.replace("**", "<strong>").replace("**", "</strong>")
        html = html.replace("*", "<em>").replace("*", "</em>")
        html = html.replace("\n\n", "</p><p>")
        html = f"<p>{html}</p>"
        return html

    def _analyze_risk_factors(self, anomalies: list[dict[str, Any]]) -> str:
        """Analyze and describe risk factors."""
        factors = []

        high_severity = [a for a in anomalies if a.get("severity", 0) > 0.7]
        if high_severity:
            factors.append(
                f"• {len(high_severity)} anomalias de alta severidade requerem ação imediata"
            )

        price_anomalies = [a for a in anomalies if a.get("type") == "price_anomaly"]
        if price_anomalies:
            factors.append(
                f"• {len(price_anomalies)} casos de possível superfaturamento"
            )

        vendor_issues = [
            a for a in anomalies if a.get("type") == "vendor_concentration"
        ]
        if vendor_issues:
            factors.append(
                f"• {len(vendor_issues)} situações de concentração de mercado"
            )

        return (
            "\n".join(factors)
            if factors
            else "• Riscos identificados são de baixa a média criticidade"
        )

    def _generate_risk_mitigation_recommendations(
        self, risk_score: float, anomalies: list[dict[str, Any]]
    ) -> str:
        """Generate risk mitigation recommendations."""
        recommendations = []

        if risk_score >= 7:
            recommendations.append(
                "• **URGENTE:** Suspender processos com anomalias críticas"
            )
            recommendations.append("• Acionar controladoria e órgãos de fiscalização")
        elif risk_score >= 4:
            recommendations.append(
                "• Intensificar monitoramento dos processos identificados"
            )
            recommendations.append("• Revisar controles internos")
        else:
            recommendations.append("• Manter monitoramento de rotina")

        recommendations.append(
            "• Implementar alertas automáticos para padrões similares"
        )
        recommendations.append("• Capacitar equipes em detecção de irregularidades")

        return "\n".join(recommendations)

    def _format_priority_recommendations(self, recommendations: list[str]) -> str:
        """Format priority recommendations."""
        if not recommendations:
            return "Nenhuma recomendação prioritária específica."

        return "\n".join(f"1. {rec}" for rec in recommendations[:5])

    def _format_complementary_recommendations(self, recommendations: list[str]) -> str:
        """Format complementary recommendations."""
        if not recommendations:
            return "Nenhuma recomendação complementar adicional."

        return "\n".join(f"• {rec}" for rec in recommendations[:5])

    # Analysis report section generators
    def _create_analysis_executive_summary(
        self, analysis_data: dict[str, Any], audience: str
    ) -> str:
        """Create executive summary for analysis results."""
        summary = analysis_data.get("summary", {})
        patterns = analysis_data.get("patterns", [])
        correlations = analysis_data.get("correlations", [])
        insights = analysis_data.get("insights", [])

        total_records = summary.get("total_records", 0)
        patterns_found = len(patterns)
        correlations_found = len(correlations)

        if audience == "executive":
            return f"""
            **Síntese da Análise de Dados**

            A análise de {total_records} registros identificou {patterns_found} padrões significativos
            e {correlations_found} correlações relevantes que indicam tendências e comportamentos sistemáticos.

            **Principais Descobertas:**
            • {len([p for p in patterns if p.get("confidence", 0) > 0.8])} padrões de alta confiabilidade
            • {len([c for c in correlations if abs(c.get("strength", 0)) > 0.7])} correlações fortes detectadas
            • {len(insights)} insights estratégicos identificados

            **Ação Requerida:** Aprofundar investigação nos padrões de alta confiabilidade e
            implementar monitoramento contínuo das correlações identificadas.
            """

        return f"""
        ## Resumo Executivo da Análise

        ### Escopo da Análise
        - **Registros analisados:** {total_records}
        - **Padrões identificados:** {patterns_found}
        - **Correlações encontradas:** {correlations_found}
        - **Insights gerados:** {len(insights)}

        ### Principais Descobertas
        {self._format_top_patterns(patterns[:5])}

        ### Correlações Significativas
        {self._format_top_correlations(correlations[:3])}

        ### Recomendações Estratégicas
        1. Aprofundar análise dos padrões de alta confiabilidade
        2. Monitorar continuamente as correlações identificadas
        3. Implementar alertas para desvios dos padrões esperados
        """

    def _create_analysis_overview(
        self, analysis_data: dict[str, Any], summary: dict[str, Any]
    ) -> str:
        """Create analysis overview section."""
        metadata = analysis_data.get("metadata", {})
        patterns = analysis_data.get("patterns", [])

        # Calculate pattern type distribution
        pattern_types = {}
        for pattern in patterns:
            ptype = pattern.get("type", "unknown")
            pattern_types[ptype] = pattern_types.get(ptype, 0) + 1

        return f"""
        ## Metodologia da Análise de Dados

        **Objetivo:** Identificação de padrões, correlações e tendências em dados públicos

        **Parâmetros da Análise:**
        - Registros processados: {summary.get("total_records", 0):,}
        - Período analisado: {metadata.get("timestamp", "N/A")[:10]}
        - Algoritmos utilizados: Análise estatística, detecção de padrões, correlação temporal

        **Técnicas Aplicadas:**
        - Análise de séries temporais
        - Detecção de outliers estatísticos
        - Análise de correlação multivariada
        - Clustering e agrupamento de dados

        ## Distribuição de Padrões Identificados
        {self._format_pattern_distribution(pattern_types)}

        ## Métricas de Qualidade
        - Confiabilidade média: {summary.get("average_confidence", 0):.1%}
        - Cobertura de dados: {summary.get("data_coverage", 0):.1%}
        - Taxa de detecção: {summary.get("detection_rate", 0):.1%}
        """

    def _create_pattern_sections(
        self, patterns: list[dict[str, Any]], audience: str
    ) -> list[ReportSection]:
        """Create pattern analysis sections."""
        sections = []

        # Group patterns by type
        pattern_groups = {}
        for pattern in patterns:
            ptype = pattern.get("type", "unknown")
            if ptype not in pattern_groups:
                pattern_groups[ptype] = []
            pattern_groups[ptype].append(pattern)

        # Create section for each pattern type
        for ptype, group_patterns in pattern_groups.items():
            title = self._get_pattern_type_title(ptype)
            content = self._format_pattern_group(group_patterns, audience)

            # Determine importance based on confidence and count
            high_confidence_count = len(
                [p for p in group_patterns if p.get("confidence", 0) > 0.8]
            )
            importance = 4 if high_confidence_count > 0 else 3

            sections.append(
                ReportSection(title=title, content=content, importance=importance)
            )

        # If no patterns, create a single informative section
        if not sections:
            sections.append(
                ReportSection(
                    title="Padrões Detectados",
                    content="Nenhum padrão significativo foi identificado na análise dos dados.",
                    importance=2,
                )
            )

        return sections

    def _create_correlation_section(self, correlations: list[dict[str, Any]]) -> str:
        """Create correlation analysis section."""
        if not correlations:
            return "Nenhuma correlação significativa foi identificada entre as variáveis analisadas."

        # Separate correlations by strength
        strong_correlations = [
            c for c in correlations if abs(c.get("strength", 0)) > 0.7
        ]
        moderate_correlations = [
            c for c in correlations if 0.4 < abs(c.get("strength", 0)) <= 0.7
        ]

        content_parts = []

        content_parts.append("## Análise de Correlações Estatísticas")
        content_parts.append("")

        if strong_correlations:
            content_parts.append("### Correlações Fortes (|r| > 0.7)")
            for corr in strong_correlations[:5]:  # Top 5
                var1 = corr.get("variable1", "Variável 1")
                var2 = corr.get("variable2", "Variável 2")
                strength = corr.get("strength", 0)
                direction = "positiva" if strength > 0 else "negativa"

                content_parts.append(f"**{var1} ↔ {var2}**")
                content_parts.append(f"- Força: {abs(strength):.2f} ({direction})")
                content_parts.append(f"- Significância: {corr.get('p_value', 0):.4f}")
                content_parts.append(
                    f"- Interpretação: {corr.get('interpretation', 'N/A')}"
                )
                content_parts.append("")

        if moderate_correlations:
            content_parts.append("### Correlações Moderadas (0.4 < |r| ≤ 0.7)")
            for corr in moderate_correlations[:3]:  # Top 3
                var1 = corr.get("variable1", "Variável 1")
                var2 = corr.get("variable2", "Variável 2")
                strength = corr.get("strength", 0)

                content_parts.append(f"• {var1} ↔ {var2}: {abs(strength):.2f}")

            content_parts.append("")

        content_parts.append("### Implicações das Correlações")
        content_parts.append(
            "- As correlações fortes indicam relações sistemáticas entre as variáveis"
        )
        content_parts.append("- Correlações negativas sugerem comportamentos inversos")
        content_parts.append(
            "- Recomenda-se aprofundar a análise causal das correlações identificadas"
        )

        return "\n".join(content_parts)

    def _create_insights_section(self, insights: list[str]) -> str:
        """Create insights section."""
        return "\n".join(f"• {insight}" for insight in insights)

    def _create_combined_executive_summary(
        self, inv_data: dict[str, Any], analysis_data: dict[str, Any], audience: str
    ) -> str:
        """Create combined executive summary."""
        # Extract investigation data
        inv_summary = inv_data.get("summary", {}) if inv_data else {}
        anomalies = inv_data.get("anomalies", []) if inv_data else []

        # Extract analysis data
        analysis_summary = analysis_data.get("summary", {}) if analysis_data else {}
        patterns = analysis_data.get("patterns", []) if analysis_data else []
        insights = analysis_data.get("insights", []) if analysis_data else []

        total_records = max(
            inv_summary.get("total_records", 0),
            analysis_summary.get("total_records", 0),
        )
        anomalies_found = inv_summary.get("anomalies_found", 0)
        patterns_found = len(patterns)
        risk_score = inv_summary.get("risk_score", 0)

        if audience == "executive":
            return f"""
            **Síntese Consolidada: Investigação & Análise**

            A análise integrada de {total_records} registros combinou detecção de anomalias com
            identificação de padrões, revelando {anomalies_found} anomalias e {patterns_found} padrões
            sistemáticos que requerem atenção.

            **Achados Críticos:**
            • Nível de risco: {risk_score:.1f}/10
            • {len([a for a in anomalies if a.get("severity", 0) > 0.7])} anomalias de alta severidade
            • {len([p for p in patterns if p.get("confidence", 0) > 0.8])} padrões de alta confiabilidade
            • {len(insights)} insights estratégicos identificados

            **Ação Executiva:** Implementar medidas corretivas para anomalias críticas e
            estabelecer monitoramento contínuo dos padrões identificados.
            """

        return f"""
        ## Resumo Executivo Consolidado

        ### Visão Geral Integrada
        Esta análise consolida os resultados da investigação de anomalias com a análise de padrões,
        proporcionando uma visão holística dos dados públicos analisados.

        **Escopo Total:**
        - Registros analisados: {total_records:,}
        - Anomalias detectadas: {anomalies_found}
        - Padrões identificados: {patterns_found}
        - Score de risco: {risk_score:.1f}/10

        ### Principais Descobertas

        **Da Investigação de Anomalias:**
        {self._format_anomaly_summary(anomalies[:3])}

        **Da Análise de Padrões:**
        {self._format_top_patterns(patterns[:3])}

        ### Insights Estratégicos
        {self._format_key_insights(insights[:5])}

        ### Recomendações Consolidadas
        1. Priorizar investigação das {len([a for a in anomalies if a.get("severity", 0) > 0.7])} anomalias críticas
        2. Implementar monitoramento dos {len([p for p in patterns if p.get("confidence", 0) > 0.8])} padrões de alta confiabilidade
        3. Aprofundar análise das correlações identificadas
        4. Estabelecer alertas automáticos para desvios futuros
        """

    def _create_combined_conclusions(
        self, inv_data: dict[str, Any], analysis_data: dict[str, Any]
    ) -> str:
        """Create combined conclusions."""
        # Extract investigation data
        inv_summary = inv_data.get("summary", {}) if inv_data else {}
        anomalies = inv_data.get("anomalies", []) if inv_data else []

        # Extract analysis data
        patterns = analysis_data.get("patterns", []) if analysis_data else []
        correlations = analysis_data.get("correlations", []) if analysis_data else []
        insights = analysis_data.get("insights", []) if analysis_data else []

        risk_score = inv_summary.get("risk_score", 0)
        high_severity_anomalies = len(
            [a for a in anomalies if a.get("severity", 0) > 0.7]
        )
        high_confidence_patterns = len(
            [p for p in patterns if p.get("confidence", 0) > 0.8]
        )
        strong_correlations = len(
            [c for c in correlations if abs(c.get("strength", 0)) > 0.7]
        )

        # Determine overall assessment
        if risk_score >= 7 or high_severity_anomalies >= 5:
            overall_assessment = "CRÍTICO"
            urgency = "URGENTE"
        elif risk_score >= 4 or high_severity_anomalies >= 2:
            overall_assessment = "ALTO"
            urgency = "PRIORITÁRIO"
        else:
            overall_assessment = "MODERADO"
            urgency = "MONITORAMENTO"

        return f"""
        ## Conclusões Consolidadas

        ### Avaliação Geral
        **Nível de Criticidade: {overall_assessment}** (Risk Score: {risk_score:.1f}/10)

        A análise integrada dos dados revelou indicadores que exigem atenção **{urgency}**.
        A combinação de anomalias detectadas com padrões sistemáticos sugere a necessidade de
        intervenção e monitoramento contínuo.

        ### Principais Conclusões

        **1. Anomalias Identificadas:**
        - {len(anomalies)} anomalias detectadas no total
        - {high_severity_anomalies} de alta severidade requerem ação imediata
        - Valor potencialmente afetado: R$ {inv_summary.get("suspicious_value", 0):,.2f}

        **2. Padrões Sistemáticos:**
        - {len(patterns)} padrões identificados na análise de dados
        - {high_confidence_patterns} padrões de alta confiabilidade confirmados
        - Padrões indicam comportamentos recorrentes que necessitam investigação

        **3. Correlações Relevantes:**
        - {len(correlations)} correlações identificadas entre variáveis
        - {strong_correlations} correlações fortes que indicam relações causais potenciais
        - Recomenda-se aprofundar análise causal destas correlações

        ### Impacto e Implicações

        **Impacto Financeiro:**
        Os achados sugerem potencial impacto financeiro estimado em R$ {inv_summary.get("suspicious_value", 0):,.2f},
        considerando apenas as anomalias de alta severidade identificadas.

        **Impacto Operacional:**
        Os padrões sistemáticos detectados indicam possíveis falhas nos processos de controle e
        monitoramento, exigindo revisão dos procedimentos atuais.

        **Impacto Legal e Reputacional:**
        As irregularidades identificadas podem ter implicações legais e de conformidade,
        requerendo atenção de autoridades competentes.

        ### Recomendações Finais

        **Ações Imediatas:**
        1. Investigar em profundidade as {high_severity_anomalies} anomalias críticas
        2. Suspender processos com indicadores de alto risco
        3. Acionar controladoria e órgãos de fiscalização

        **Ações de Médio Prazo:**
        1. Implementar monitoramento contínuo dos {high_confidence_patterns} padrões identificados
        2. Revisar e fortalecer controles internos
        3. Capacitar equipes em detecção de irregularidades

        **Ações Estratégicas:**
        1. Estabelecer sistema de alertas automatizados
        2. Implementar análise preditiva para prevenir futuras irregularidades
        3. Desenvolver cultura de transparência e compliance

        ### Próximos Passos

        1. **Curto Prazo (1-7 dias):** Investigação detalhada das anomalias críticas
        2. **Médio Prazo (1-3 meses):** Implementação de controles e monitoramento
        3. **Longo Prazo (3-12 meses):** Avaliação de eficácia e ajustes do sistema

        ---

        *Análise concluída em {datetime.utcnow().strftime('%d/%m/%Y %H:%M')} UTC*
        *Recomenda-se revisão periódica das conclusões e atualização baseada em novos dados*
        """

    def _create_high_priority_anomaly_summary(
        self, anomalies: list[dict[str, Any]]
    ) -> str:
        """Create high priority anomaly summary."""
        if not anomalies:
            return "Nenhuma anomalia de alta prioridade foi identificada."

        content_parts = []

        content_parts.append("## Anomalias Críticas - Ação Imediata Requerida")
        content_parts.append("")
        content_parts.append(f"**Total de anomalias críticas:** {len(anomalies)}")
        content_parts.append("")

        # Calculate total suspicious value
        total_suspicious = sum(a.get("value", 0) for a in anomalies)
        content_parts.append(f"**Valor total suspeito:** R$ {total_suspicious:,.2f}")
        content_parts.append("")

        # Group by type for summary
        types_count = {}
        for anomaly in anomalies:
            atype = anomaly.get("type", "unknown")
            types_count[atype] = types_count.get(atype, 0) + 1

        content_parts.append("### Distribuição por Tipo")
        for atype, count in sorted(
            types_count.items(), key=lambda x: x[1], reverse=True
        ):
            type_name = self._get_anomaly_type_name(atype)
            content_parts.append(f"- **{type_name.title()}:** {count} casos")
        content_parts.append("")

        # Detail top anomalies
        content_parts.append("### Anomalias Mais Críticas")
        content_parts.append("")

        # Sort by severity
        sorted_anomalies = sorted(
            anomalies, key=lambda a: a.get("severity", 0), reverse=True
        )

        for i, anomaly in enumerate(sorted_anomalies[:5], 1):  # Top 5
            content_parts.append(
                f"**{i}. {anomaly.get('description', 'Anomalia detectada')}**"
            )
            content_parts.append(
                f"- **Severidade:** {anomaly.get('severity', 0):.2f}/1.00"
            )
            content_parts.append(
                f"- **Tipo:** {self._get_anomaly_type_name(anomaly.get('type', 'unknown'))}"
            )
            content_parts.append(
                f"- **Valor afetado:** R$ {anomaly.get('value', 0):,.2f}"
            )
            content_parts.append(
                f"- **Explicação:** {anomaly.get('explanation', 'N/A')}"
            )

            recommendations = anomaly.get("recommendations", [])
            if recommendations:
                content_parts.append(f"- **Ação recomendada:** {recommendations[0]}")

            content_parts.append("")

        # Urgency warning
        content_parts.append("### ⚠️ Aviso de Urgência")
        content_parts.append("")
        content_parts.append(
            "Estas anomalias apresentam características que indicam potencial irregularidade grave."
        )
        content_parts.append("Recomenda-se:")
        content_parts.append("1. **Suspensão imediata** dos processos identificados")
        content_parts.append("2. **Investigação detalhada** por equipe especializada")
        content_parts.append("3. **Notificação** às autoridades competentes")
        content_parts.append("4. **Preservação** de toda documentação relacionada")

        return "\n".join(content_parts)

    def _create_category_anomaly_summary(
        self, category: str, anomalies: list[dict[str, Any]]
    ) -> str:
        """Create category-specific anomaly summary."""
        if not anomalies:
            return f"Nenhuma anomalia detectada na categoria {category}."

        category_name = self._get_anomaly_type_name(category)

        content_parts = []

        content_parts.append(f"## Análise: {category_name.title()}")
        content_parts.append("")
        content_parts.append(f"**Total de anomalias:** {len(anomalies)}")
        content_parts.append("")

        # Calculate statistics
        total_value = sum(a.get("value", 0) for a in anomalies)
        avg_severity = (
            sum(a.get("severity", 0) for a in anomalies) / len(anomalies)
            if anomalies
            else 0
        )
        high_severity = len([a for a in anomalies if a.get("severity", 0) > 0.7])

        content_parts.append("### Estatísticas da Categoria")
        content_parts.append(f"- **Valor total afetado:** R$ {total_value:,.2f}")
        content_parts.append(f"- **Severidade média:** {avg_severity:.2f}/1.00")
        content_parts.append(f"- **Casos de alta severidade:** {high_severity}")
        content_parts.append("")

        # Category-specific insights
        content_parts.append("### Descrição da Categoria")
        category_descriptions = {
            "price_anomaly": "Anomalias de preço indicam valores significativamente diferentes da média de mercado, "
            "sugerindo possível superfaturamento ou subfaturamento.",
            "vendor_concentration": "Concentração de fornecedores indica que poucos fornecedores dominam um grande volume "
            "de contratos, reduzindo competitividade e aumentando riscos.",
            "temporal_patterns": "Padrões temporais suspeitos indicam concentração anormal de contratos em períodos específicos, "
            "sugerindo possível direcionamento.",
            "duplicate_contracts": "Contratos duplicados indicam possível pagamento múltiplo pelo mesmo serviço ou produto.",
            "payment_patterns": "Padrões de pagamento irregulares indicam possíveis problemas no processo de liquidação financeira.",
        }

        description = category_descriptions.get(
            category, f"Anomalias do tipo {category_name}."
        )
        content_parts.append(description)
        content_parts.append("")

        # Top cases
        content_parts.append("### Casos Mais Relevantes")
        content_parts.append("")

        sorted_anomalies = sorted(
            anomalies, key=lambda a: a.get("severity", 0), reverse=True
        )

        for i, anomaly in enumerate(sorted_anomalies[:3], 1):  # Top 3
            content_parts.append(
                f"**{i}. {anomaly.get('description', 'Anomalia detectada')}**"
            )
            content_parts.append(f"- Severidade: {anomaly.get('severity', 0):.2f}")
            content_parts.append(f"- Valor: R$ {anomaly.get('value', 0):,.2f}")

            explanation = anomaly.get("explanation", "")
            if explanation:
                # Truncate long explanations
                if len(explanation) > 150:
                    explanation = explanation[:150] + "..."
                content_parts.append(f"- Detalhes: {explanation}")

            content_parts.append("")

        # Recommendations for this category
        content_parts.append("### Recomendações Específicas")
        category_recommendations = {
            "price_anomaly": [
                "Realizar pesquisa de mercado para validar preços praticados",
                "Revisar processo de formação de preço de referência",
                "Investigar possível conluio entre fornecedores",
            ],
            "vendor_concentration": [
                "Ampliar base de fornecedores cadastrados",
                "Revisar critérios de qualificação de fornecedores",
                "Implementar rodízio de fornecedores quando possível",
            ],
            "temporal_patterns": [
                "Distribuir licitações de forma mais equilibrada ao longo do ano",
                "Revisar processos de urgência e dispensa",
                "Implementar planejamento de compras mais eficiente",
            ],
            "duplicate_contracts": [
                "Implementar sistema de verificação de duplicidade",
                "Revisar processo de controle de contratos",
                "Auditar pagamentos realizados",
            ],
            "payment_patterns": [
                "Revisar processo de liquidação e pagamento",
                "Implementar controles de alçada e segregação de funções",
                "Auditar contas bancárias e beneficiários",
            ],
        }

        recommendations = category_recommendations.get(
            category,
            [
                "Aprofundar investigação dos casos identificados",
                "Implementar controles específicos para esta categoria",
                "Monitorar continuamente para detectar novos casos",
            ],
        )

        for rec in recommendations:
            content_parts.append(f"• {rec}")

        return "\n".join(content_parts)

    def _create_trend_analysis_content(self, patterns: list[dict[str, Any]]) -> str:
        """Create trend analysis content."""
        if not patterns:
            return "Nenhuma tendência significativa foi identificada na análise temporal dos dados."

        content_parts = []

        content_parts.append("## Análise de Tendências Temporais")
        content_parts.append("")
        content_parts.append(f"**Total de tendências identificadas:** {len(patterns)}")
        content_parts.append("")

        # Classify trends by direction
        upward_trends = [
            p for p in patterns if p.get("direction", "").lower() == "upward"
        ]
        downward_trends = [
            p for p in patterns if p.get("direction", "").lower() == "downward"
        ]
        stable_trends = [
            p for p in patterns if p.get("direction", "").lower() == "stable"
        ]

        content_parts.append("### Distribuição de Tendências")
        content_parts.append(f"- **Tendências ascendentes:** {len(upward_trends)}")
        content_parts.append(f"- **Tendências descendentes:** {len(downward_trends)}")
        content_parts.append(f"- **Tendências estáveis:** {len(stable_trends)}")
        content_parts.append("")

        # Analyze upward trends
        if upward_trends:
            content_parts.append("### Tendências Ascendentes")
            content_parts.append("*Indicam aumento ao longo do tempo*")
            content_parts.append("")

            for trend in sorted(
                upward_trends, key=lambda p: p.get("confidence", 0), reverse=True
            )[:3]:
                content_parts.append(
                    f"**{trend.get('description', 'Tendência identificada')}**"
                )
                content_parts.append(
                    f"- Confiabilidade: {trend.get('confidence', 0):.1%}"
                )
                content_parts.append(
                    f"- Taxa de crescimento: {trend.get('rate', 0):.1f}% ao período"
                )

                significance = trend.get("significance", "")
                if significance:
                    content_parts.append(f"- Significância: {significance}")

                content_parts.append("")

        # Analyze downward trends
        if downward_trends:
            content_parts.append("### Tendências Descendentes")
            content_parts.append("*Indicam redução ao longo do tempo*")
            content_parts.append("")

            for trend in sorted(
                downward_trends, key=lambda p: p.get("confidence", 0), reverse=True
            )[:3]:
                content_parts.append(
                    f"**{trend.get('description', 'Tendência identificada')}**"
                )
                content_parts.append(
                    f"- Confiabilidade: {trend.get('confidence', 0):.1%}"
                )
                content_parts.append(
                    f"- Taxa de redução: {abs(trend.get('rate', 0)):.1f}% ao período"
                )

                significance = trend.get("significance", "")
                if significance:
                    content_parts.append(f"- Significância: {significance}")

                content_parts.append("")

        # Temporal patterns analysis
        content_parts.append("### Padrões Temporais Identificados")
        content_parts.append("")

        # Check for seasonal patterns
        seasonal = [p for p in patterns if "seasonal" in p.get("type", "").lower()]
        if seasonal:
            content_parts.append("**Padrões Sazonais:**")
            for pattern in seasonal[:2]:
                content_parts.append(
                    f"• {pattern.get('description', 'Padrão sazonal')}"
                )
            content_parts.append("")

        # Check for cyclical patterns
        cyclical = [p for p in patterns if "cyclical" in p.get("type", "").lower()]
        if cyclical:
            content_parts.append("**Padrões Cíclicos:**")
            for pattern in cyclical[:2]:
                content_parts.append(
                    f"• {pattern.get('description', 'Padrão cíclico')}"
                )
            content_parts.append("")

        # Projections and implications
        content_parts.append("### Projeções e Implicações")
        content_parts.append("")

        if upward_trends:
            content_parts.append("**Tendências Ascendentes:**")
            content_parts.append(
                "- Podem indicar crescimento de atividade ou aumento de custos"
            )
            content_parts.append(
                "- Requerem monitoramento para identificar causas raiz"
            )
            content_parts.append(
                "- Se relacionadas a anomalias, sugerem agravamento do problema"
            )
            content_parts.append("")

        if downward_trends:
            content_parts.append("**Tendências Descendentes:**")
            content_parts.append(
                "- Podem indicar melhoria de controles ou redução de atividade"
            )
            content_parts.append(
                "- Se relacionadas a anomalias, sugerem eficácia de medidas corretivas"
            )
            content_parts.append("- Requerem validação para confirmar causas")
            content_parts.append("")

        # Recommendations
        content_parts.append("### Recomendações Baseadas em Tendências")
        content_parts.append("")
        content_parts.append(
            "1. **Monitoramento Contínuo:** Acompanhar evolução das tendências identificadas"
        )
        content_parts.append(
            "2. **Análise de Causas:** Investigar fatores que determinam as tendências"
        )
        content_parts.append(
            "3. **Projeções Futuras:** Utilizar tendências para prever comportamentos futuros"
        )
        content_parts.append(
            "4. **Ajuste de Controles:** Adaptar controles baseado nas tendências observadas"
        )

        # Statistical confidence note
        content_parts.append("")
        content_parts.append("---")
        content_parts.append(
            "*Nota: A confiabilidade das tendências é baseada em análise estatística dos dados históricos.*"
        )
        content_parts.append(
            "*Tendências com confiabilidade > 80% são consideradas altamente robustas.*"
        )

        return "\n".join(content_parts)

    # Helper methods for pattern and correlation formatting

    def _format_top_patterns(self, patterns: list[dict[str, Any]]) -> str:
        """Format top patterns for summary sections."""
        if not patterns:
            return "Nenhum padrão significativo identificado."

        lines = []
        for i, pattern in enumerate(patterns[:5], 1):  # Top 5
            desc = pattern.get("description", "Padrão detectado")
            confidence = pattern.get("confidence", 0)
            lines.append(f"{i}. **{desc}** (confiabilidade: {confidence:.1%})")

        return "\n".join(lines)

    def _format_top_correlations(self, correlations: list[dict[str, Any]]) -> str:
        """Format top correlations for summary sections."""
        if not correlations:
            return "Nenhuma correlação significativa identificada."

        lines = []
        for i, corr in enumerate(correlations[:3], 1):  # Top 3
            var1 = corr.get("variable1", "Variável 1")
            var2 = corr.get("variable2", "Variável 2")
            strength = corr.get("strength", 0)
            direction = "positiva" if strength > 0 else "negativa"
            lines.append(f"{i}. {var1} ↔ {var2}: {abs(strength):.2f} ({direction})")

        return "\n".join(lines)

    def _format_pattern_distribution(self, pattern_types: dict[str, int]) -> str:
        """Format pattern type distribution."""
        if not pattern_types:
            return "Nenhuma distribuição de padrões disponível."

        lines = []
        for ptype, count in sorted(
            pattern_types.items(), key=lambda x: x[1], reverse=True
        ):
            type_name = self._get_pattern_type_name(ptype)
            lines.append(f"- **{type_name}:** {count} padrões")

        return "\n".join(lines)

    def _get_pattern_type_title(self, ptype: str) -> str:
        """Get human-readable title for pattern type."""
        titles = {
            "temporal": "Padrões Temporais",
            "seasonal": "Padrões Sazonais",
            "cyclical": "Padrões Cíclicos",
            "trend": "Tendências",
            "correlation": "Padrões de Correlação",
            "cluster": "Agrupamentos de Dados",
            "outlier": "Padrões de Outliers",
            "frequency": "Padrões de Frequência",
        }
        return titles.get(ptype, ptype.replace("_", " ").title())

    def _get_pattern_type_name(self, ptype: str) -> str:
        """Get human-readable name for pattern type."""
        names = {
            "temporal": "padrões temporais",
            "seasonal": "padrões sazonais",
            "cyclical": "padrões cíclicos",
            "trend": "tendências",
            "correlation": "padrões de correlação",
            "cluster": "agrupamentos",
            "outlier": "outliers",
            "frequency": "padrões de frequência",
        }
        return names.get(ptype, ptype.replace("_", " "))

    def _format_pattern_group(
        self, patterns: list[dict[str, Any]], audience: str
    ) -> str:
        """Format a group of patterns."""
        content = []

        for pattern in sorted(
            patterns, key=lambda p: p.get("confidence", 0), reverse=True
        )[
            :5
        ]:  # Top 5
            content.append(f"**{pattern.get('description', 'Padrão detectado')}**")
            content.append(f"- Confiabilidade: {pattern.get('confidence', 0):.1%}")

            frequency = pattern.get("frequency", "")
            if frequency:
                content.append(f"- Frequência: {frequency}")

            impact = pattern.get("impact", "")
            if impact:
                content.append(f"- Impacto: {impact}")

            if audience == "technical":
                # Add technical details for technical audience
                statistical_sig = pattern.get("statistical_significance", "")
                if statistical_sig:
                    content.append(f"- Significância estatística: {statistical_sig}")

            content.append("")

        return "\n".join(content)

    def _format_key_insights(self, insights: list[str]) -> str:
        """Format key insights for summary sections."""
        if not insights:
            return "Nenhum insight estratégico disponível."

        return "\n".join(f"• {insight}" for insight in insights[:5])  # Top 5

    def _format_anomaly_group(
        self, anomalies: list[dict[str, Any]], audience: str
    ) -> str:
        """Format a group of anomalies."""
        content = []
        for anomaly in anomalies:
            content.append(f"**{anomaly.get('description', 'Anomalia detectada')}**")
            content.append(f"Severidade: {anomaly.get('severity', 0):.2f}")
            content.append(f"Explicação: {anomaly.get('explanation', 'N/A')}")
            content.append("")

        return "\n".join(content)

    async def _render_pdf(
        self,
        sections: list[ReportSection],
        request: ReportRequest,
        context: AgentContext,
    ) -> str:
        """Render report in PDF format and return base64 encoded string."""
        # First convert sections to markdown
        markdown_content = await self._render_markdown(sections, request, context)

        # Generate PDF using export service
        pdf_bytes = await export_service.generate_pdf(
            content=markdown_content,
            title=f"Relatório: {request.report_type.value.replace('_', ' ').title()}",
            metadata={
                "generated_at": datetime.utcnow().isoformat(),
                "report_type": request.report_type.value,
                "investigation_id": context.investigation_id,
                "target_audience": request.target_audience,
                "author": "Agente Tiradentes - Cidadão.AI",
            },
            format_type="report",
        )

        # Return base64 encoded PDF for easy transmission
        import base64

        return base64.b64encode(pdf_bytes).decode("utf-8")
