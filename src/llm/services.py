"""
Module: llm.services
Description: High-level LLM services for agent integration
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import asyncio
from typing import Any, Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, Field as PydanticField

from src.core import get_logger
from src.llm.providers import LLMManager, LLMRequest, LLMResponse, create_llm_manager


@dataclass
class LLMServiceConfig:
    """Configuration for LLM service."""
    
    primary_provider: str = "groq"
    enable_fallback: bool = True
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: int = 2048


class LLMChatMessage(BaseModel):
    """Chat message for LLM conversation."""
    
    role: str = PydanticField(description="Message role: system, user, assistant")
    content: str = PydanticField(description="Message content")
    metadata: Optional[Dict[str, Any]] = PydanticField(default=None, description="Additional metadata")


class LLMConversation(BaseModel):
    """LLM conversation context."""
    
    messages: List[LLMChatMessage] = PydanticField(default_factory=list, description="Conversation messages")
    system_prompt: Optional[str] = PydanticField(default=None, description="System prompt")
    conversation_id: Optional[str] = PydanticField(default=None, description="Unique conversation ID")
    user_id: Optional[str] = PydanticField(default=None, description="User ID")
    context: Optional[Dict[str, Any]] = PydanticField(default=None, description="Additional context")


class LLMService:
    """
    High-level LLM service for agent integration.
    
    Provides convenient methods for common LLM tasks:
    - Text summarization
    - Report generation
    - Question answering
    - Data analysis explanation
    - Pattern interpretation
    """
    
    def __init__(self, config: Optional[LLMServiceConfig] = None):
        """
        Initialize LLM service.
        
        Args:
            config: Service configuration
        """
        self.config = config or LLMServiceConfig()
        self.logger = get_logger(__name__)
        
        # Initialize LLM manager
        self.llm_manager = create_llm_manager(
            primary_provider=self.config.primary_provider,
            enable_fallback=self.config.enable_fallback,
        )
        
        # Simple in-memory cache (in production, use Redis)
        self._cache = {}
        
        self.logger.info(
            "llm_service_initialized",
            primary_provider=self.config.primary_provider,
            enable_fallback=self.config.enable_fallback,
            enable_caching=self.config.enable_caching,
        )
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Enable streaming
            
        Returns:
            Generated text
        """
        request = LLMRequest(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=system_prompt,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            stream=stream,
        )
        
        if stream:
            # Collect all chunks for non-streaming return
            chunks = []
            async for chunk in self.llm_manager.stream_complete(request):
                chunks.append(chunk)
            return "".join(chunks)
        else:
            response = await self.llm_manager.complete(request)
            return response.content
    
    async def chat(
        self,
        conversation: LLMConversation,
        new_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Continue a conversation with a new message.
        
        Args:
            conversation: Existing conversation context
            new_message: New user message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Assistant response
        """
        # Add new user message
        conversation.messages.append(
            LLMChatMessage(role="user", content=new_message)
        )
        
        # Convert to LLM request format
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation.messages
        ]
        
        request = LLMRequest(
            messages=messages,
            system_prompt=conversation.system_prompt,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
        )
        
        response = await self.llm_manager.complete(request)
        
        # Add assistant response to conversation
        conversation.messages.append(
            LLMChatMessage(role="assistant", content=response.content)
        )
        
        return response.content
    
    async def summarize_data(
        self,
        data: Dict[str, Any],
        context: str = "government transparency",
        target_audience: str = "technical",
        max_length: int = 500,
    ) -> str:
        """
        Summarize structured data with context.
        
        Args:
            data: Data to summarize
            context: Context for summarization
            target_audience: Target audience (technical, executive, public)
            max_length: Maximum summary length in words
            
        Returns:
            Data summary
        """
        system_prompt = f"""
        You are a data analyst specializing in {context}. 
        Your task is to create clear, concise summaries for {target_audience} audiences.
        Focus on key insights, patterns, and actionable information.
        Keep summaries under {max_length} words.
        Use Portuguese language.
        """
        
        # Format data for the prompt
        data_str = self._format_data_for_prompt(data)
        
        prompt = f"""
        Analise os seguintes dados e forneça um resumo conciso:

        {data_str}

        Resumo (máximo {max_length} palavras):
        """
        
        return await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temperature for more focused summaries
            max_tokens=max_length * 2,  # Account for Portuguese word length
        )
    
    async def explain_anomaly(
        self,
        anomaly_data: Dict[str, Any],
        context: str = "government contracts",
        explain_to: str = "citizen",
    ) -> str:
        """
        Generate human-readable explanation of an anomaly.
        
        Args:
            anomaly_data: Anomaly detection results
            context: Context for explanation
            explain_to: Target audience (citizen, auditor, manager)
            
        Returns:
            Anomaly explanation
        """
        audience_prompts = {
            "citizen": "Explique de forma simples para um cidadão comum, evitando jargão técnico.",
            "auditor": "Forneça uma explicação técnica detalhada para um auditor governamental.",
            "manager": "Explique de forma executiva, focando em impactos e ações necessárias.",
        }
        
        system_prompt = f"""
        Você é um especialista em transparência pública e detecção de irregularidades.
        {audience_prompts.get(explain_to, audience_prompts['citizen'])}
        Use linguagem clara e objetiva em português.
        Sempre inclua o contexto e as implicações da anomalia.
        """
        
        anomaly_description = self._format_anomaly_for_prompt(anomaly_data)
        
        prompt = f"""
        Foi detectada uma anomalia em {context}:

        {anomaly_description}

        Explique esta anomalia de forma clara:
        1. O que foi detectado?
        2. Por que isso é considerado uma anomalia?
        3. Qual o impacto potencial?
        4. Que ações são recomendadas?
        """
        
        return await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=1000,
        )
    
    async def generate_insights(
        self,
        patterns: List[Dict[str, Any]],
        correlations: List[Dict[str, Any]],
        context: str = "government spending",
    ) -> List[str]:
        """
        Generate insights from patterns and correlations.
        
        Args:
            patterns: Detected patterns
            correlations: Found correlations
            context: Analysis context
            
        Returns:
            List of insights
        """
        system_prompt = f"""
        Você é um analista sênior especializado em {context}.
        Sua tarefa é gerar insights valiosos a partir de padrões e correlações detectados.
        Foque em descobertas que possam levar a melhorias ou identificar problemas.
        Use português e seja conciso mas informativo.
        """
        
        patterns_str = self._format_patterns_for_prompt(patterns)
        correlations_str = self._format_correlations_for_prompt(correlations)
        
        prompt = f"""
        Com base nos seguintes padrões e correlações detectados em {context}:

        PADRÕES IDENTIFICADOS:
        {patterns_str}

        CORRELAÇÕES ENCONTRADAS:
        {correlations_str}

        Gere uma lista de 5-7 insights principais que podem ser extraídos desta análise.
        Cada insight deve ser claro, específico e acionável.
        """
        
        response = await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.6,
            max_tokens=1500,
        )
        
        # Parse response into list of insights
        insights = []
        for line in response.split('\n'):
            line = line.strip()
            if line and any(line.startswith(prefix) for prefix in ['•', '-', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.']):
                # Clean up formatting
                insight = line.lstrip('•-* ').lstrip('1234567. ')
                if insight:
                    insights.append(insight)
        
        return insights
    
    async def create_executive_summary(
        self,
        investigation_results: Dict[str, Any],
        analysis_results: Optional[Dict[str, Any]] = None,
        target_length: int = 300,
    ) -> str:
        """
        Create executive summary from investigation and analysis results.
        
        Args:
            investigation_results: Investigation findings
            analysis_results: Optional analysis results
            target_length: Target summary length in words
            
        Returns:
            Executive summary
        """
        system_prompt = f"""
        Você é um consultor executivo especializado em transparência governamental.
        Crie resumos executivos concisos e impactantes para tomadores de decisão.
        Foque nos pontos mais críticos e ações requeridas.
        Use linguagem executiva em português, máximo {target_length} palavras.
        """
        
        inv_summary = self._format_investigation_for_prompt(investigation_results)
        analysis_summary = ""
        
        if analysis_results:
            analysis_summary = f"\n\nRESULTADOS DA ANÁLISE:\n{self._format_analysis_for_prompt(analysis_results)}"
        
        prompt = f"""
        Com base nos seguintes resultados de investigação{' e análise' if analysis_results else ''}:

        RESULTADOS DA INVESTIGAÇÃO:
        {inv_summary}{analysis_summary}

        Crie um resumo executivo focando em:
        1. Principais descobertas
        2. Nível de risco identificado
        3. Impacto financeiro estimado
        4. Ações prioritárias recomendadas

        Resumo executivo ({target_length} palavras):
        """
        
        return await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.4,
            max_tokens=target_length * 2,
        )
    
    async def close(self):
        """Close LLM service and cleanup resources."""
        await self.llm_manager.close()
        self._cache.clear()
    
    # Helper methods for formatting data
    
    def _format_data_for_prompt(self, data: Dict[str, Any]) -> str:
        """Format structured data for LLM prompt."""
        lines = []
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for sub_key, sub_value in value.items():
                    lines.append(f"  {sub_key}: {sub_value}")
            elif isinstance(value, list):
                lines.append(f"{key}: {len(value)} items")
                if value and len(value) <= 5:
                    for item in value:
                        lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")
        
        return "\n".join(lines)
    
    def _format_anomaly_for_prompt(self, anomaly: Dict[str, Any]) -> str:
        """Format anomaly data for LLM prompt."""
        return f"""
        Tipo: {anomaly.get('type', 'N/A')}
        Descrição: {anomaly.get('description', 'N/A')}
        Severidade: {anomaly.get('severity', 0):.2f}
        Confiança: {anomaly.get('confidence', 0):.2f}
        Explicação: {anomaly.get('explanation', 'N/A')}
        Evidências: {anomaly.get('evidence', {})}
        Impacto Financeiro: R$ {anomaly.get('financial_impact', 0):,.2f}
        """
    
    def _format_patterns_for_prompt(self, patterns: List[Dict[str, Any]]) -> str:
        """Format patterns for LLM prompt."""
        if not patterns:
            return "Nenhum padrão detectado."
        
        lines = []
        for i, pattern in enumerate(patterns[:5], 1):  # Limit to top 5
            lines.append(f"{i}. {pattern.get('description', 'Padrão detectado')}")
            lines.append(f"   Significância: {pattern.get('significance', 0):.2f}")
            if 'insights' in pattern:
                for insight in pattern['insights'][:2]:  # Top 2 insights
                    lines.append(f"   - {insight}")
        
        return "\n".join(lines)
    
    def _format_correlations_for_prompt(self, correlations: List[Dict[str, Any]]) -> str:
        """Format correlations for LLM prompt."""
        if not correlations:
            return "Nenhuma correlação significativa encontrada."
        
        lines = []
        for i, corr in enumerate(correlations[:3], 1):  # Limit to top 3
            lines.append(f"{i}. {corr.get('description', 'Correlação detectada')}")
            lines.append(f"   Coeficiente: {corr.get('correlation_coefficient', 0):.3f}")
            lines.append(f"   Interpretação: {corr.get('business_interpretation', 'N/A')}")
        
        return "\n".join(lines)
    
    def _format_investigation_for_prompt(self, results: Dict[str, Any]) -> str:
        """Format investigation results for LLM prompt."""
        summary = results.get('summary', {})
        anomalies = results.get('anomalies', [])
        
        lines = [
            f"Registros analisados: {summary.get('total_records', 0)}",
            f"Anomalias encontradas: {summary.get('anomalies_found', 0)}",
            f"Score de risco: {summary.get('risk_score', 0):.1f}/10",
            f"Valor suspeito: R$ {summary.get('suspicious_value', 0):,.2f}",
        ]
        
        if anomalies:
            lines.append("\nPrincipais anomalias:")
            for anomaly in anomalies[:3]:  # Top 3 anomalies
                lines.append(f"- {anomaly.get('description', 'Anomalia detectada')}")
        
        return "\n".join(lines)
    
    def _format_analysis_for_prompt(self, results: Dict[str, Any]) -> str:
        """Format analysis results for LLM prompt."""
        summary = results.get('summary', {})
        patterns = results.get('patterns', [])
        
        lines = [
            f"Registros analisados: {summary.get('total_records', 0)}",
            f"Padrões encontrados: {summary.get('patterns_found', 0)}",
            f"Score de análise: {summary.get('analysis_score', 0):.1f}/10",
            f"Organizações analisadas: {summary.get('organizations_analyzed', 0)}",
        ]
        
        if patterns:
            lines.append("\nPrincipais padrões:")
            for pattern in patterns[:3]:  # Top 3 patterns
                lines.append(f"- {pattern.get('description', 'Padrão detectado')}")
        
        return "\n".join(lines)


# Factory function for easy service creation
def create_llm_service(
    primary_provider: str = "groq",
    enable_fallback: bool = True,
    **kwargs
) -> LLMService:
    """
    Create LLM service with specified configuration.
    
    Args:
        primary_provider: Primary LLM provider
        enable_fallback: Enable fallback providers
        **kwargs: Additional configuration
        
    Returns:
        Configured LLM service
    """
    config = LLMServiceConfig(
        primary_provider=primary_provider,
        enable_fallback=enable_fallback,
        **kwargs
    )
    
    return LLMService(config)