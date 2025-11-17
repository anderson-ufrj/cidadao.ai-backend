"""
Intent Classifier

Classifies user queries into investigation intents using keyword patterns + LLM fallback.

Author: Anderson Henrique da Silva
Created: 2025-10-14
Updated: 2025-11-17 - Added keyword-based detection
"""

import json
import re
from typing import Any

from src.core import get_logger
from src.core.llm_client import LLMClient
from src.services.orchestration.models.investigation import InvestigationIntent

logger = get_logger(__name__)


class IntentClassifier:
    """
    Classifies user queries into investigation intents.

    Uses keyword patterns for fast detection, with LLM fallback for complex queries.
    """

    # Keywords that indicate contract/investigation intents
    INVESTIGATION_KEYWORDS = [
        # Contract terms
        "contrato",
        "contratos",
        "licitação",
        "licitações",
        # Investigation verbs
        "investigar",
        "analisar",
        "verificar",
        "auditar",
        "fiscalizar",
        # Anomaly detection
        "anomalia",
        "anomalias",
        "suspeito",
        "suspeitos",
        "fraude",
        "fraudulentos",
        "irregular",
        "irregularidades",
        # Money/values
        "acima de",
        "maior que",
        "superior a",
        "mais de",
        "milhão",
        "milhões",
        "mil",
        "bilhão",
        # Public spending
        "despesa",
        "despesas",
        "gasto",
        "gastos",
        "orçamento",
        # Government entities
        "prefeitura",
        "governo",
        "município",
        "estado",
        "federal",
    ]

    # CNPJ pattern
    CNPJ_PATTERN = re.compile(r"\d{2}\.?\d{3}\.?\d{3}/?000\d-?\d{2}")

    # Monetary value patterns
    MONEY_PATTERNS = [
        re.compile(r"R\$\s*[\d.,]+\s*(milhão|milhões|mil|bilhão)", re.IGNORECASE),
        re.compile(
            r"(acima|maior|mais|superior)\s+(de|que)\s+R?\$?\s*[\d.,]+", re.IGNORECASE
        ),
        re.compile(r"valor.*?R\$\s*[\d.,]+", re.IGNORECASE),
    ]

    def __init__(
        self, llm_client: LLMClient | None = None, keyword_only: bool = False
    ) -> None:
        # Allow keyword-only mode to avoid LLMClient dependency issues
        if keyword_only:
            self.llm = None
        else:
            self.llm = llm_client or LLMClient()
        self.keyword_only = keyword_only
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
                - method: str (keyword, llm, or fallback)
        """
        # Try keyword-based classification first (fast path)
        keyword_result = self._classify_by_keywords(query)
        if keyword_result:
            self.logger.info(
                f"[KEYWORD] Classified query as {keyword_result['intent']} "
                f"(confidence: {keyword_result['confidence']:.2f}) - {keyword_result['reasoning']}"
            )
            return keyword_result

        # Fallback to LLM classification for complex queries (if LLM available)
        if self.keyword_only or self.llm is None:
            # Keyword-only mode: return GENERAL_QUERY for ambiguous queries
            self.logger.info(
                "[KEYWORD-ONLY] No clear pattern, defaulting to GENERAL_QUERY"
            )
            return {
                "intent": InvestigationIntent.GENERAL_QUERY,
                "confidence": 0.6,
                "reasoning": "No keyword pattern match (keyword-only mode)",
                "method": "keyword-fallback",
            }

        self.logger.info("[LLM] Using LLM classification for complex query")
        prompt = self._build_classification_prompt(query)

        try:
            response = await self.llm.generate(
                prompt=prompt,
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=500,
            )

            result = self._parse_llm_response(response)
            result["method"] = "llm"
            self.logger.info(
                f"[LLM] Classified query as {result['intent']} "
                f"(confidence: {result['confidence']:.2f})"
            )

            return result

        except Exception as e:
            self.logger.error(f"Intent classification failed: {e}")
            return {
                "intent": InvestigationIntent.GENERAL_QUERY,
                "confidence": 0.5,
                "reasoning": "Fallback due to classification error",
                "method": "fallback",
            }

    def _classify_by_keywords(self, query: str) -> dict[str, Any] | None:
        """
        Fast classification using keyword patterns.

        Returns None if no clear pattern match (defer to LLM).
        """
        query_lower = query.lower()

        # Check for CNPJ (strong indicator of supplier investigation)
        if self.CNPJ_PATTERN.search(query):
            return {
                "intent": InvestigationIntent.SUPPLIER_INVESTIGATION,
                "confidence": 0.95,
                "reasoning": "CNPJ detected in query",
                "method": "keyword",
            }

        # Count investigation keywords
        keyword_count = sum(
            1 for kw in self.INVESTIGATION_KEYWORDS if kw in query_lower
        )

        # Check for monetary values
        has_money_pattern = any(
            pattern.search(query) for pattern in self.MONEY_PATTERNS
        )

        # Thresholds for keyword detection
        min_keywords_with_money = 2
        min_keywords_strong = 3

        # Strong investigation signal: keywords + money
        if (
            keyword_count >= min_keywords_with_money
            and has_money_pattern
            and any(
                word in query_lower for word in ["contrato", "contratos", "licitação"]
            )
        ):
            return {
                "intent": InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
                "confidence": 0.90,
                "reasoning": f"Contract keywords ({keyword_count}) + monetary value detected",
                "method": "keyword",
            }

        # Medium investigation signal: multiple keywords
        if keyword_count >= min_keywords_strong:
            return {
                "intent": InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
                "confidence": 0.85,
                "reasoning": f"Multiple investigation keywords detected ({keyword_count})",
                "method": "keyword",
            }

        # Check for specific investigation verbs at start
        investigation_verbs = [
            "investigar",
            "analisar",
            "verificar",
            "auditar",
            "fiscalizar",
        ]
        if any(query_lower.startswith(verb) for verb in investigation_verbs):
            return {
                "intent": InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
                "confidence": 0.80,
                "reasoning": "Query starts with investigation verb",
                "method": "keyword",
            }

        # No clear pattern - defer to LLM
        return None

    def _build_classification_prompt(self, query: str) -> str:
        """Build improved prompt for LLM classification."""
        return f"""Você é um classificador de intenções para investigações de transparência pública.
Analise a consulta e determine se é uma INVESTIGAÇÃO ou PERGUNTA GERAL.

CONSULTA DO USUÁRIO:
"{query}"

REGRAS IMPORTANTES:
• Queries com valores monetários, contratos, licitações = INVESTIGAÇÃO
• Queries com "investigar", "analisar", "verificar" = INVESTIGAÇÃO
• Queries sobre "como funciona", "o que é" = PERGUNTA GERAL

INTENÇÕES DISPONÍVEIS:

🔍 INVESTIGAÇÕES (Prioridade ALTA):
1. contract_anomaly_detection: Contratos, licitações, despesas, gastos públicos
   Exemplos: "Contratos de saúde acima de R$ 1 milhão", "Licitações suspeitas"

2. supplier_investigation: Fornecedor específico, empresa, CNPJ
   Exemplos: "Investigar fornecedor X", "CNPJ 12345678000190"

3. corruption_indicators: Fraudes, irregularidades, corrupção
   Exemplos: "Detectar fraudes", "Padrões suspeitos"

4. budget_analysis: Orçamento, distribuição de recursos
   Exemplos: "Orçamento da educação", "Gastos do município"

5. health_budget_analysis: Saúde pública específica
   Exemplos: "Investimento em hospitais", "Verba SUS"

6. education_performance: Educação, IDEB, escolas
   Exemplos: "Desempenho ENEM", "Qualidade das escolas"

❓ PERGUNTAS GERAIS:
7. general_query: Dúvidas sobre o sistema, ajuda, informações
   Exemplos: "Como funciona?", "Quais dados?", "Ajuda"

RESPONDA EM JSON (APENAS O JSON, SEM TEXTO EXTRA):
{{
    "intent": "nome_da_intencao",
    "confidence": 0.95,
    "reasoning": "Explicação clara"
}}

JSON:"""

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
