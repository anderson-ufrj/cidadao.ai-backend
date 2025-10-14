"""
Intent Classifier

Classifies user queries into investigation intents using LLM.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

import json
from typing import Any

from src.core import get_logger
from src.core.llm_client import LLMClient
from src.services.orchestration.models.investigation import InvestigationIntent

logger = get_logger(__name__)


class IntentClassifier:
    """
    Classifies user queries into investigation intents.

    Uses LLM to understand Portuguese queries and map them to structured intents.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm = llm_client or LLMClient()
        self.logger = get_logger(__name__)

    async def classify(self, query: str) -> dict[str, Any]:
        """
        Classify user query into an investigation intent.

        Args:
            query: User query in Portuguese

        Returns:
            Dict with:
                - intent: InvestigationIntent
                - confidence: float (0-1)
                - reasoning: str
        """
        prompt = self._build_classification_prompt(query)

        try:
            response = await self.llm.generate(
                prompt=prompt,
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=500,
            )

            result = self._parse_llm_response(response)
            self.logger.info(
                f"Classified query as {result['intent']} "
                f"(confidence: {result['confidence']:.2f})"
            )

            return result

        except Exception as e:
            self.logger.error(f"Intent classification failed: {e}")
            return {
                "intent": InvestigationIntent.GENERAL_QUERY,
                "confidence": 0.5,
                "reasoning": "Fallback due to classification error",
            }

    def _build_classification_prompt(self, query: str) -> str:
        """Build prompt for LLM classification."""
        return f"""Analise a seguinte consulta do usuário e classifique a intenção de investigação.

CONSULTA DO USUÁRIO:
"{query}"

INTENÇÕES DISPONÍVEIS:
1. supplier_investigation: Investigar fornecedor específico, contratos ganhos, histórico
   Exemplos: "Investigar fornecedor X", "Contratos da empresa Y", "CNPJ 12345678000190"

2. contract_anomaly_detection: Detectar anomalias em contratos, preços suspeitos, favorecimento
   Exemplos: "Contratos suspeitos", "Preços acima da média", "Detectar fraudes em licitações"

3. budget_analysis: Análise de orçamento público, distribuição de gastos
   Exemplos: "Orçamento da saúde", "Gastos do município X", "Distribuição de recursos"

4. health_budget_analysis: Análise específica de saúde pública
   Exemplos: "Gastos com SUS", "Investimento em hospitais", "Verba da saúde"

5. education_performance: Desempenho educacional, IDEB, escolas
   Exemplos: "IDEB do município", "Qualidade das escolas", "Desempenho ENEM"

6. corruption_indicators: Indicadores de corrupção, padrões suspeitos
   Exemplos: "Detectar corrupção", "Padrões de favorecimento", "Empresas fantasma"

7. general_query: Consulta geral sobre transparência
   Exemplos: "Como funciona?", "Quais dados disponíveis?", "Ajuda"

RESPONDA EM JSON:
{{
    "intent": "nome_da_intencao",
    "confidence": 0.95,
    "reasoning": "Breve explicação da classificação"
}}

RESPOSTA JSON:"""

    def _parse_llm_response(self, response: str) -> dict[str, Any]:
        """Parse LLM response into structured result."""
        try:
            # Try to extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            # Validate intent
            intent_str = data.get("intent", "general_query")
            try:
                intent = InvestigationIntent(intent_str)
            except ValueError:
                self.logger.warning(
                    f"Invalid intent: {intent_str}, using GENERAL_QUERY"
                )
                intent = InvestigationIntent.GENERAL_QUERY

            return {
                "intent": intent,
                "confidence": float(data.get("confidence", 0.7)),
                "reasoning": data.get("reasoning", "No reasoning provided"),
            }

        except Exception as e:
            self.logger.error(f"Failed to parse LLM response: {e}")
            return {
                "intent": InvestigationIntent.GENERAL_QUERY,
                "confidence": 0.5,
                "reasoning": "Parse error",
            }
