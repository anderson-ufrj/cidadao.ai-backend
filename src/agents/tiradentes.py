"""
Module: agents.tiradentes
Codinome: Tiradentes - Avaliador de Riscos
Description: Agent specialized in generating natural language reports from investigation and analysis results
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field as PydanticField

from src.agents.deodoro import BaseAgent, AgentContext, AgentMessage, AgentResponse
from src.core import get_logger, AgentStatus
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
    subsections: List['ReportSection'] = None
    charts: List[Dict[str, Any]] = None
    tables: List[Dict[str, Any]] = None
    importance: int = 1  # 1-5 scale


class ReportRequest(BaseModel):
    """Request for report generation."""
    
    report_type: ReportType = PydanticField(description="Type of report to generate")
    format: ReportFormat = PydanticField(default=ReportFormat.MARKDOWN, description="Output format")
    investigation_results: Optional[Dict[str, Any]] = PydanticField(default=None, description="Investigation results from InvestigatorAgent")
    analysis_results: Optional[Dict[str, Any]] = PydanticField(default=None, description="Analysis results from AnalystAgent")
    target_audience: str = PydanticField(default="technical", description="Target audience: technical, executive, public")
    language: str = PydanticField(default="pt", description="Report language")
    include_visualizations: bool = PydanticField(default=True, description="Include charts and visualizations")
    executive_summary: bool = PydanticField(default=True, description="Include executive summary")
    detailed_findings: bool = PydanticField(default=True, description="Include detailed findings")
    recommendations: bool = PydanticField(default=True, description="Include recommendations")


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
                "transparency_reporting"
            ],
            max_retries=3,
            timeout=60
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
        self,
        message: AgentMessage,
        context: AgentContext
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
                    f"Unsupported action: {message.action}",
                    agent_id=self.name
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
                    metadata={"investigation_id": context.investigation_id}
                )
            
            # Generate report content
            report_sections = await self._generate_report_content(request, context)
            
            # Render report in requested format
            formatted_report = await self._render_report(report_sections, request, context)
            
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
                }
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
                metadata={"investigation_id": context.investigation_id}
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
                metadata={"investigation_id": context.investigation_id}
            )
    
    async def _generate_report_content(
        self,
        request: ReportRequest,
        context: AgentContext
    ) -> List[ReportSection]:
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
                f"Unsupported report type: {request.report_type}",
                agent_id=self.name
            )
    
    async def _generate_investigation_report(
        self,
        request: ReportRequest,
        context: AgentContext
    ) -> List[ReportSection]:
        """Generate investigation report sections."""
        sections = []
        
        if not request.investigation_results:
            return sections
        
        inv_data = request.investigation_results
        anomalies = inv_data.get("anomalies", [])
        summary = inv_data.get("summary", {})
        
        # Executive Summary
        if request.executive_summary:
            exec_summary = self._create_executive_summary(inv_data, request.target_audience)
            sections.append(ReportSection(
                title="Resumo Executivo",
                content=exec_summary,
                importance=5
            ))
        
        # Investigation Overview
        overview = self._create_investigation_overview(inv_data, summary)
        sections.append(ReportSection(
            title="Visão Geral da Investigação",
            content=overview,
            importance=4
        ))
        
        # Anomalies Analysis
        if anomalies and request.detailed_findings:
            anomaly_sections = self._create_anomaly_sections(anomalies, request.target_audience)
            sections.extend(anomaly_sections)
        
        # Risk Assessment
        risk_section = self._create_risk_assessment(summary, anomalies)
        sections.append(ReportSection(
            title="Avaliação de Risco",
            content=risk_section,
            importance=4
        ))
        
        # Recommendations
        if request.recommendations:
            recommendations = self._create_recommendations(anomalies, "investigation")
            sections.append(ReportSection(
                title="Recomendações",
                content=recommendations,
                importance=5
            ))
        
        return sections
    
    async def _generate_analysis_report(
        self,
        request: ReportRequest,
        context: AgentContext
    ) -> List[ReportSection]:
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
            exec_summary = self._create_analysis_executive_summary(analysis_data, request.target_audience)
            sections.append(ReportSection(
                title="Resumo Executivo da Análise",
                content=exec_summary,
                importance=5
            ))
        
        # Data Overview
        overview = self._create_analysis_overview(analysis_data, summary)
        sections.append(ReportSection(
            title="Visão Geral dos Dados",
            content=overview,
            importance=4
        ))
        
        # Pattern Analysis
        if patterns and request.detailed_findings:
            pattern_sections = self._create_pattern_sections(patterns, request.target_audience)
            sections.extend(pattern_sections)
        
        # Correlation Analysis
        if correlations and request.detailed_findings:
            correlation_section = self._create_correlation_section(correlations)
            sections.append(ReportSection(
                title="Análise de Correlações",
                content=correlation_section,
                importance=3
            ))
        
        # Key Insights
        if insights:
            insights_section = self._create_insights_section(insights)
            sections.append(ReportSection(
                title="Principais Insights",
                content=insights_section,
                importance=4
            ))
        
        # Recommendations
        if request.recommendations:
            recommendations = self._create_recommendations(patterns, "analysis")
            sections.append(ReportSection(
                title="Recomendações Estratégicas",
                content=recommendations,
                importance=5
            ))
        
        return sections
    
    async def _generate_combined_report(
        self,
        request: ReportRequest,
        context: AgentContext
    ) -> List[ReportSection]:
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
                request.target_audience
            )
            sections.append(ReportSection(
                title="Resumo Executivo Consolidado",
                content=combined_summary,
                importance=5
            ))
        
        # Add sections from both reports (avoiding duplicate executive summaries)
        for section in inv_sections:
            if "Resumo Executivo" not in section.title:
                sections.append(section)
        
        for section in analysis_sections:
            if "Resumo Executivo" not in section.title:
                sections.append(section)
        
        # Combined conclusions
        combined_conclusions = self._create_combined_conclusions(
            request.investigation_results,
            request.analysis_results
        )
        sections.append(ReportSection(
            title="Conclusões Consolidadas",
            content=combined_conclusions,
            importance=5
        ))
        
        return sections
    
    async def _generate_executive_summary(
        self,
        request: ReportRequest,
        context: AgentContext
    ) -> List[ReportSection]:
        """Generate executive summary only."""
        sections = []
        
        summary_content = self._create_combined_executive_summary(
            request.investigation_results,
            request.analysis_results,
            "executive"
        )
        
        sections.append(ReportSection(
            title="Resumo Executivo",
            content=summary_content,
            importance=5
        ))
        
        return sections
    
    async def _generate_anomaly_summary(
        self,
        request: ReportRequest,
        context: AgentContext
    ) -> List[ReportSection]:
        """Generate anomaly-focused summary."""
        sections = []
        
        if request.investigation_results:
            anomalies = request.investigation_results.get("anomalies", [])
            
            if anomalies:
                # High priority anomalies
                high_priority = [a for a in anomalies if a.get("severity", 0) > 0.7]
                if high_priority:
                    content = self._create_high_priority_anomaly_summary(high_priority)
                    sections.append(ReportSection(
                        title="Anomalias de Alta Prioridade",
                        content=content,
                        importance=5
                    ))
                
                # Anomaly categories
                categories = {}
                for anomaly in anomalies:
                    cat = anomaly.get("type", "unknown")
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(anomaly)
                
                for category, cat_anomalies in categories.items():
                    content = self._create_category_anomaly_summary(category, cat_anomalies)
                    sections.append(ReportSection(
                        title=f"Anomalias: {category.replace('_', ' ').title()}",
                        content=content,
                        importance=3
                    ))
        
        return sections
    
    async def _generate_trend_analysis(
        self,
        request: ReportRequest,
        context: AgentContext
    ) -> List[ReportSection]:
        """Generate trend analysis report."""
        sections = []
        
        if request.analysis_results:
            patterns = request.analysis_results.get("patterns", [])
            
            # Filter for trend-related patterns
            trend_patterns = [p for p in patterns if "trend" in p.get("type", "").lower()]
            
            if trend_patterns:
                content = self._create_trend_analysis_content(trend_patterns)
                sections.append(ReportSection(
                    title="Análise de Tendências",
                    content=content,
                    importance=4
                ))
        
        return sections
    
    def _create_executive_summary(self, inv_data: Dict[str, Any], audience: str) -> str:
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
    
    def _create_investigation_overview(self, inv_data: Dict[str, Any], summary: Dict[str, Any]) -> str:
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
    
    def _create_anomaly_sections(self, anomalies: List[Dict[str, Any]], audience: str) -> List[ReportSection]:
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
            
            sections.append(ReportSection(
                title=title,
                content=content,
                importance=4 if any(a.get("severity", 0) > 0.7 for a in group_anomalies) else 3
            ))
        
        return sections
    
    def _create_risk_assessment(self, summary: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> str:
        """Create risk assessment section."""
        risk_score = summary.get("risk_score", 0)
        high_severity = summary.get("high_severity_count", 0)
        medium_severity = summary.get("medium_severity_count", 0)
        
        risk_level = "BAIXO" if risk_score < 3 else "MÉDIO" if risk_score < 7 else "ALTO"
        
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
    
    def _create_recommendations(self, items: List[Dict[str, Any]], report_type: str) -> str:
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
        sections: List[ReportSection],
        request: ReportRequest,
        context: AgentContext
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
        sections: List[ReportSection],
        request: ReportRequest,
        context: AgentContext
    ) -> str:
        """Render report in Markdown format."""
        report_lines = []
        
        # Report header
        report_lines.append(f"# Relatório: {request.report_type.value.replace('_', ' ').title()}")
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
        report_lines.append("*Relatório gerado automaticamente pelo sistema Cidadão.AI*")
        
        return "\n".join(report_lines)
    
    async def _render_html(
        self,
        sections: List[ReportSection],
        request: ReportRequest,
        context: AgentContext
    ) -> str:
        """Render report in HTML format."""
        html_parts = []
        
        # HTML header
        html_parts.append("""
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
        """)
        
        # Report content
        html_parts.append(f"<h1>Relatório: {request.report_type.value.replace('_', ' ').title()}</h1>")
        html_parts.append(f"""
        <div class="metadata">
            <strong>Data:</strong> {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}<br>
            <strong>ID da Investigação:</strong> {context.investigation_id}<br>
            <strong>Público-alvo:</strong> {request.target_audience}
        </div>
        """)
        
        # Render sections
        for section in sorted(sections, key=lambda s: s.importance, reverse=True):
            priority_class = "high-priority" if section.importance >= 4 else "medium-priority" if section.importance >= 3 else "low-priority"
            html_parts.append(f'<div class="{priority_class}">')
            html_parts.append(f"<h2>{section.title}</h2>")
            html_parts.append(f"<div>{self._markdown_to_html(section.content)}</div>")
            html_parts.append("</div>")
        
        # HTML footer
        html_parts.append("""
        <hr>
        <p><em>Relatório gerado automaticamente pelo sistema Cidadão.AI</em></p>
        </body>
        </html>
        """)
        
        return "\n".join(html_parts)
    
    async def _render_json(
        self,
        sections: List[ReportSection],
        request: ReportRequest,
        context: AgentContext
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
                "high_priority_sections": len([s for s in sections if s.importance >= 4]),
                "word_count": sum(self._count_words(s.content) for s in sections),
            }
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    async def _render_executive_summary(
        self,
        sections: List[ReportSection],
        request: ReportRequest,
        context: AgentContext
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
            content_lines = section.content.split('\n')
            key_content = []
            for line in content_lines:
                if line.strip() and len(key_content) < 3:
                    key_content.append(line.strip())
            summary_parts.extend(key_content)
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    # Helper methods
    
    def _format_anomaly_summary(self, anomalies: List[Dict[str, Any]]) -> str:
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
            "payment_patterns": "Padrões de Pagamento Irregulares"
        }
        return titles.get(atype, atype.replace("_", " ").title())
    
    def _get_anomaly_type_name(self, atype: str) -> str:
        """Get human-readable name for anomaly type."""
        names = {
            "price_anomaly": "preços suspeitos",
            "vendor_concentration": "concentração de fornecedores",
            "temporal_patterns": "padrões temporais irregulares",
            "duplicate_contracts": "contratos duplicados",
            "payment_patterns": "irregularidades de pagamento"
        }
        return names.get(atype, atype.replace("_", " "))
    
    def _format_summary_stats(self, summary: Dict[str, Any]) -> str:
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
    
    def _analyze_risk_factors(self, anomalies: List[Dict[str, Any]]) -> str:
        """Analyze and describe risk factors."""
        factors = []
        
        high_severity = [a for a in anomalies if a.get("severity", 0) > 0.7]
        if high_severity:
            factors.append(f"• {len(high_severity)} anomalias de alta severidade requerem ação imediata")
        
        price_anomalies = [a for a in anomalies if a.get("type") == "price_anomaly"]
        if price_anomalies:
            factors.append(f"• {len(price_anomalies)} casos de possível superfaturamento")
        
        vendor_issues = [a for a in anomalies if a.get("type") == "vendor_concentration"]
        if vendor_issues:
            factors.append(f"• {len(vendor_issues)} situações de concentração de mercado")
        
        return "\n".join(factors) if factors else "• Riscos identificados são de baixa a média criticidade"
    
    def _generate_risk_mitigation_recommendations(self, risk_score: float, anomalies: List[Dict[str, Any]]) -> str:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        if risk_score >= 7:
            recommendations.append("• **URGENTE:** Suspender processos com anomalias críticas")
            recommendations.append("• Acionar controladoria e órgãos de fiscalização")
        elif risk_score >= 4:
            recommendations.append("• Intensificar monitoramento dos processos identificados")
            recommendations.append("• Revisar controles internos")
        else:
            recommendations.append("• Manter monitoramento de rotina")
        
        recommendations.append("• Implementar alertas automáticos para padrões similares")
        recommendations.append("• Capacitar equipes em detecção de irregularidades")
        
        return "\n".join(recommendations)
    
    def _format_priority_recommendations(self, recommendations: List[str]) -> str:
        """Format priority recommendations."""
        if not recommendations:
            return "Nenhuma recomendação prioritária específica."
        
        return "\n".join(f"1. {rec}" for rec in recommendations[:5])
    
    def _format_complementary_recommendations(self, recommendations: List[str]) -> str:
        """Format complementary recommendations."""
        if not recommendations:
            return "Nenhuma recomendação complementar adicional."
        
        return "\n".join(f"• {rec}" for rec in recommendations[:5])
    
    # Placeholder methods for analysis report sections
    def _create_analysis_executive_summary(self, analysis_data: Dict[str, Any], audience: str) -> str:
        """Create executive summary for analysis results."""
        return "Resumo executivo da análise de padrões (placeholder)"
    
    def _create_analysis_overview(self, analysis_data: Dict[str, Any], summary: Dict[str, Any]) -> str:
        """Create analysis overview section."""
        return "Visão geral da análise de dados (placeholder)"
    
    def _create_pattern_sections(self, patterns: List[Dict[str, Any]], audience: str) -> List[ReportSection]:
        """Create pattern analysis sections."""
        return [ReportSection(title="Padrões Detectados", content="Análise de padrões (placeholder)", importance=3)]
    
    def _create_correlation_section(self, correlations: List[Dict[str, Any]]) -> str:
        """Create correlation analysis section."""
        return "Análise de correlações (placeholder)"
    
    def _create_insights_section(self, insights: List[str]) -> str:
        """Create insights section."""
        return "\n".join(f"• {insight}" for insight in insights)
    
    def _create_combined_executive_summary(self, inv_data: Dict[str, Any], analysis_data: Dict[str, Any], audience: str) -> str:
        """Create combined executive summary."""
        return "Resumo executivo consolidado (placeholder)"
    
    def _create_combined_conclusions(self, inv_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> str:
        """Create combined conclusions."""
        return "Conclusões consolidadas (placeholder)"
    
    def _create_high_priority_anomaly_summary(self, anomalies: List[Dict[str, Any]]) -> str:
        """Create high priority anomaly summary."""
        return "Resumo de anomalias de alta prioridade (placeholder)"
    
    def _create_category_anomaly_summary(self, category: str, anomalies: List[Dict[str, Any]]) -> str:
        """Create category-specific anomaly summary."""
        return f"Resumo de anomalias da categoria {category} (placeholder)"
    
    def _create_trend_analysis_content(self, patterns: List[Dict[str, Any]]) -> str:
        """Create trend analysis content."""
        return "Análise de tendências (placeholder)"
    
    def _format_anomaly_group(self, anomalies: List[Dict[str, Any]], audience: str) -> str:
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
        sections: List[ReportSection],
        request: ReportRequest,
        context: AgentContext
    ) -> str:
        """Render report in PDF format and return base64 encoded string."""
        # First convert sections to markdown
        markdown_content = await self._render_markdown(sections, request, context)
        
        # Generate PDF using export service
        pdf_bytes = await export_service.generate_pdf(
            content=markdown_content,
            title=f"Relatório: {request.report_type.value.replace('_', ' ').title()}",
            metadata={
                'generated_at': datetime.utcnow().isoformat(),
                'report_type': request.report_type.value,
                'investigation_id': context.investigation_id,
                'target_audience': request.target_audience,
                'author': 'Agente Tiradentes - Cidadão.AI'
            },
            format_type="report"
        )
        
        # Return base64 encoded PDF for easy transmission
        import base64
        return base64.b64encode(pdf_bytes).decode('utf-8')