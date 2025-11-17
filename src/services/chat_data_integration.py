"""
Chat Data Integration Service
Connects chat agents with Portal da Transparência data
"""

import re
from datetime import date, datetime, timedelta
from typing import Any

from src.core import get_logger
from src.core.config import settings
from src.services.maritaca_client import MaritacaClient, MaritacaModel
from src.services.portal_transparencia_service import portal_transparencia

logger = get_logger(__name__)


class ChatDataIntegration:
    """Integrates chat requests with real government data."""

    def __init__(self):
        """Initialize the integration service."""
        self.portal = portal_transparencia
        self.ai_client = None
        self._init_ai_client()

    def _init_ai_client(self):
        """Initialize AI client for data interpretation."""
        api_key = getattr(settings, "maritaca_api_key", None)
        if api_key:
            api_key_value = (
                api_key.get_secret_value()
                if hasattr(api_key, "get_secret_value")
                else api_key
            )
            self.ai_client = MaritacaClient(
                api_key=api_key_value, model=MaritacaModel.SABIAZINHO_3
            )

    async def process_user_query(
        self, message: str, context: dict | None = None
    ) -> dict[str, Any]:
        """
        Process user query and fetch relevant data.

        Args:
            message: User's message
            context: Optional conversation context

        Returns:
            Dict with data and formatted response
        """
        # Extract entities and intent from message
        entities = await self._extract_entities(message)

        # Determine data type to search
        data_type = self._determine_data_type(message)

        logger.info(f"Processing query - Type: {data_type}, Entities: {entities}")

        # Fetch relevant data
        try:
            if data_type == "contratos":
                data = await self._search_contracts(message, entities)
            elif data_type == "licitacoes":
                data = await self._search_biddings(message, entities)
            elif data_type == "despesas":
                data = await self._search_expenses(message, entities)
            elif data_type == "servidores":
                data = await self._search_servants(message, entities)
            elif data_type == "fornecedor":
                data = await self._get_supplier_details(message, entities)
            elif data_type == "analise":
                data = await self._analyze_patterns(message, entities)
            else:
                data = {
                    "tipo": "desconhecido",
                    "mensagem": "Não entendi que tipo de dados você procura",
                }

            # Format response with AI
            formatted_response = await self._format_response_with_ai(data, message)

            return {
                "data": data,
                "response": formatted_response,
                "entities": entities,
                "data_type": data_type,
            }

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "data": None,
                "response": "Desculpe, tive um problema ao buscar os dados. Por favor, tente novamente.",
                "error": str(e),
            }

    async def _extract_entities(self, message: str) -> dict[str, Any]:
        """Extract entities from user message."""
        entities = {}

        # Mapeamento de estados completos para siglas
        STATES_MAP = {
            "acre": "AC",
            "alagoas": "AL",
            "amapá": "AP",
            "amapa": "AP",
            "amazonas": "AM",
            "bahia": "BA",
            "ceará": "CE",
            "ceara": "CE",
            "distrito federal": "DF",
            "brasília": "DF",
            "brasilia": "DF",
            "espírito santo": "ES",
            "espirito santo": "ES",
            "goiás": "GO",
            "goias": "GO",
            "maranhão": "MA",
            "maranhao": "MA",
            "mato grosso": "MT",
            "mato grosso do sul": "MS",
            "minas gerais": "MG",
            "pará": "PA",
            "para": "PA",
            "paraíba": "PB",
            "paraiba": "PB",
            "paraná": "PR",
            "parana": "PR",
            "pernambuco": "PE",
            "piauí": "PI",
            "piaui": "PI",
            "rio de janeiro": "RJ",
            "rio grande do norte": "RN",
            "rio grande do sul": "RS",
            "rondônia": "RO",
            "rondonia": "RO",
            "roraima": "RR",
            "santa catarina": "SC",
            "são paulo": "SP",
            "sao paulo": "SP",
            "sergipe": "SE",
            "tocantins": "TO",
        }

        # Mapeamento de siglas para códigos IBGE
        IBGE_CODES = {
            "AC": "12",
            "AL": "27",
            "AP": "16",
            "AM": "13",
            "BA": "29",
            "CE": "23",
            "DF": "53",
            "ES": "32",
            "GO": "52",
            "MA": "21",
            "MT": "51",
            "MS": "50",
            "MG": "31",
            "PA": "15",
            "PB": "25",
            "PR": "41",
            "PE": "26",
            "PI": "22",
            "RJ": "33",
            "RN": "24",
            "RS": "43",
            "RO": "11",
            "RR": "14",
            "SC": "42",
            "SP": "35",
            "SE": "28",
            "TO": "17",
        }

        # Extract state (nome completo ou sigla)
        message_lower = message.lower()
        for state_name, state_code in STATES_MAP.items():
            if state_name in message_lower:
                entities["estado"] = state_code
                entities["codigo_uf"] = IBGE_CODES[state_code]
                logger.info(
                    f"Extracted state: {state_name} -> {state_code} (IBGE: {IBGE_CODES[state_code]})"
                )
                break

        # Se não encontrou por nome, tentar sigla
        if "estado" not in entities:
            for sigla, codigo in IBGE_CODES.items():
                pattern = rf"\b{sigla}\b"
                if re.search(pattern, message, re.IGNORECASE):
                    entities["estado"] = sigla
                    entities["codigo_uf"] = codigo
                    logger.info(f"Extracted state by code: {sigla} (IBGE: {codigo})")
                    break

        # Extract CNPJ
        cnpj_match = re.search(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b", message)
        if cnpj_match:
            entities["cnpj"] = re.sub(r"[^\d]", "", cnpj_match.group())

        # Extract CPF
        cpf_match = re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", message)
        if cpf_match:
            entities["cpf"] = re.sub(r"[^\d]", "", cpf_match.group())

        # Extract dates
        date_patterns = [
            (r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", "%d/%m/%Y"),
            (r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", "%Y-%m-%d"),
        ]

        for pattern, fmt in date_patterns:
            matches = re.findall(pattern, message)
            if matches:
                try:
                    if fmt == "%d/%m/%Y":
                        date_str = f"{matches[0][0]}/{matches[0][1]}/{matches[0][2]}"
                    else:
                        date_str = f"{matches[0][0]}-{matches[0][1]}-{matches[0][2]}"
                    entities["data"] = datetime.strptime(date_str, fmt).date()
                except:
                    pass

        # Extract year
        year_match = re.search(r"\b(20\d{2})\b", message)
        if year_match and "data" not in entities:
            entities["ano"] = int(year_match.group(1))

        # Extract monetary values (melhorado: bilhão, milhão, mil)
        value_patterns = [
            (r"R\$\s*([\d.,]+)\s*bilh[ãõa]o", 1000000000),
            (r"R\$\s*([\d.,]+)\s*bilh[ãõa]es", 1000000000),
            (r"([\d.,]+)\s*bilh[ãõa]o", 1000000000),
            (r"R\$\s*([\d.,]+)\s*milh[ãõa]o", 1000000),
            (r"R\$\s*([\d.,]+)\s*milh[õõe]es", 1000000),
            (r"([\d.,]+)\s*milh[ãõa]o", 1000000),
            (r"R\$\s*([\d.,]+)\s*mil", 1000),
            (r"([\d.,]+)\s*mil\s+reais", 1000),
            (r"R\$\s*([\d.,]+)", 1),
            (r"([\d.,]+)\s*reais", 1),
        ]

        for pattern, multiplier in value_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(".", "").replace(",", ".")
                try:
                    value = float(value_str) * multiplier
                    entities["valor"] = value
                    logger.info(f"Extracted value: {match.group(0)} -> R$ {value:,.2f}")
                    break
                except:
                    pass

        # Extract category/area (saúde, educação, etc.)
        category_keywords = {
            "saúde": ["saúde", "saude", "hospital", "médico", "medicamento"],
            "educação": ["educação", "educacao", "escola", "universidade", "ensino"],
            "infraestrutura": [
                "infraestrutura",
                "obra",
                "construção",
                "estrada",
                "rodovia",
            ],
            "segurança": ["segurança", "seguranca", "polícia", "policia"],
            "cultura": ["cultura", "arte", "museu", "teatro"],
        }

        for category, keywords in category_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                entities["categoria"] = category
                logger.info(f"Extracted category: {category}")
                break

        # Extract agency/organization names
        org_keywords = ["ministério", "secretaria", "prefeitura", "governo", "órgão"]
        for keyword in org_keywords:
            pattern = rf"{keyword}\s+(?:de\s+|da\s+|do\s+)?([A-Za-zÀ-ú\s]+?)(?:\.|,|$)"
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                entities["orgao"] = match.group(1).strip()
                break

        logger.info(f"Total entities extracted: {len(entities)}")
        return entities

    def _determine_data_type(self, message: str) -> str:
        """Determine what type of data the user is asking for."""
        message_lower = message.lower()

        # Keywords for each data type
        keywords = {
            "contratos": [
                "contrato",
                "contratos",
                "contratação",
                "contratações",
                "contratou",
                "contratado",
            ],
            "licitacoes": [
                "licitação",
                "licitações",
                "pregão",
                "concorrência",
                "tomada de preço",
            ],
            "despesas": [
                "despesa",
                "despesas",
                "gasto",
                "gastos",
                "pagamento",
                "pagamentos",
            ],
            "servidores": [
                "servidor",
                "servidores",
                "funcionário",
                "funcionários",
                "salário",
                "remuneração",
            ],
            "fornecedor": ["fornecedor", "fornecedores", "empresa", "cnpj"],
            "analise": [
                "análise",
                "analisar",
                "padrão",
                "padrões",
                "tendência",
                "evolução",
                "comparar",
            ],
        }

        # Count matches for each type
        scores = {}
        for data_type, words in keywords.items():
            scores[data_type] = sum(1 for word in words if word in message_lower)

        # Return type with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        # Default to contracts if no clear match
        return "contratos"

    async def _search_contracts(self, message: str, entities: dict) -> dict[str, Any]:
        """Search for contracts based on extracted entities."""
        # Build search parameters
        params = {}

        if "orgao" in entities:
            # TODO: Map organization name to code
            params["orgao"] = entities["orgao"]

        if "cnpj" in entities:
            params["cnpj_fornecedor"] = entities["cnpj"]

        if "data" in entities:
            # Search 30 days around the date
            params["data_inicial"] = entities["data"] - timedelta(days=30)
            params["data_final"] = entities["data"] + timedelta(days=30)
        elif "ano" in entities:
            params["data_inicial"] = date(entities["ano"], 1, 1)
            params["data_final"] = date(entities["ano"], 12, 31)

        if "valor" in entities:
            # Search 20% range around value
            params["valor_minimo"] = entities["valor"] * 0.8
            params["valor_maximo"] = entities["valor"] * 1.2

        # Search contracts
        result = await self.portal.search_contracts(**params, size=20)

        return {
            "tipo": "contratos",
            "dados": result["contratos"],
            "total": result["total"],
            "parametros": params,
        }

    async def _search_biddings(self, message: str, entities: dict) -> dict[str, Any]:
        """Search for biddings based on extracted entities."""
        params = {}

        if "orgao" in entities:
            params["orgao"] = entities["orgao"]

        if "data" in entities:
            params["data_inicial"] = entities["data"] - timedelta(days=30)
            params["data_final"] = entities["data"] + timedelta(days=30)
        elif "ano" in entities:
            params["data_inicial"] = date(entities["ano"], 1, 1)
            params["data_final"] = date(entities["ano"], 12, 31)

        result = await self.portal.search_biddings(**params, size=20)

        return {
            "tipo": "licitacoes",
            "dados": result["licitacoes"],
            "total": result["total"],
            "parametros": params,
        }

    async def _search_expenses(self, message: str, entities: dict) -> dict[str, Any]:
        """Search for expenses based on extracted entities."""
        params = {}

        if "orgao" in entities:
            params["orgao"] = entities["orgao"]

        # Determine month/year
        if "data" in entities:
            params["mes_ano"] = entities["data"].strftime("%m/%Y")
        elif "ano" in entities:
            # Get current month for the specified year
            params["mes_ano"] = f"{datetime.now().month:02d}/{entities['ano']}"

        result = await self.portal.search_expenses(**params, size=50)

        return {
            "tipo": "despesas",
            "dados": result["despesas"],
            "total": result["total"],
            "parametros": params,
        }

    async def _search_servants(self, message: str, entities: dict) -> dict[str, Any]:
        """Search for public servants based on extracted entities."""
        params = {}

        # Extract name from message
        name_pattern = (
            r"(?:servidor|funcionário)\s+([A-Za-zÀ-ú\s]+?)(?:\.|,|$|trabalha|recebe)"
        )
        name_match = re.search(name_pattern, message, re.IGNORECASE)
        if name_match:
            params["nome"] = name_match.group(1).strip()

        if "cpf" in entities:
            params["cpf"] = entities["cpf"]

        if "orgao" in entities:
            params["orgao"] = entities["orgao"]

        result = await self.portal.search_public_servants(**params, size=20)

        return {
            "tipo": "servidores",
            "dados": result["servidores"],
            "total": result["total"],
            "parametros": params,
        }

    async def _get_supplier_details(
        self, message: str, entities: dict
    ) -> dict[str, Any]:
        """Get detailed supplier information."""
        if "cnpj" not in entities:
            return {"tipo": "fornecedor", "erro": "CNPJ não encontrado na mensagem"}

        result = await self.portal.get_supplier_info(entities["cnpj"])

        return {"tipo": "fornecedor", "dados": result, "cnpj": entities["cnpj"]}

    async def _analyze_patterns(self, message: str, entities: dict) -> dict[str, Any]:
        """Analyze spending patterns."""
        params = {}

        if "orgao" in entities:
            params["orgao"] = entities["orgao"]

        # Determine period
        if "ano" in entities:
            params["periodo_meses"] = 12
        else:
            params["periodo_meses"] = 6  # Default to 6 months

        result = await self.portal.analyze_spending_patterns(**params)

        return {"tipo": "analise", "dados": result}

    async def _format_response_with_ai(self, data: dict, original_query: str) -> str:
        """Format the data response using AI."""
        if not self.ai_client or not data.get("dados"):
            return self._format_response_simple(data)

        try:
            # Prepare context for AI
            system_prompt = """Você é um assistente especializado em transparência pública.
            Sua tarefa é explicar dados governamentais de forma clara e acessível.
            Use linguagem simples, destaque informações importantes e sempre seja preciso com valores e datas.
            Se encontrar possíveis irregularidades, mencione-as de forma objetiva."""

            # Prepare data summary
            if data["tipo"] == "contratos":
                data_summary = f"Encontrei {data.get('total', 0)} contratos. "
                if data.get("dados"):
                    data_summary += "Aqui estão os principais: "
                    for i, contract in enumerate(data["dados"][:3]):
                        data_summary += (
                            f"\n{i+1}. {contract.get('objeto', 'Sem descrição')} - "
                        )
                        data_summary += f"R$ {contract.get('valorTotal', 0):,.2f} - "
                        data_summary += f"Fornecedor: {contract.get('nomeFantasiaFornecedor', 'Não informado')}"

            elif data["tipo"] == "analise":
                analysis = data["dados"]
                data_summary = f"Análise de gastos do período {analysis['periodo']['inicio']} a {analysis['periodo']['fim']}: "
                data_summary += f"\n- Total de contratos: {analysis['total_contratos']}"
                data_summary += (
                    f"\n- Valor total: R$ {analysis['valor_total_contratos']:,.2f}"
                )
                data_summary += (
                    f"\n- Fornecedores únicos: {analysis['fornecedores_unicos']}"
                )
                if analysis.get("alertas"):
                    data_summary += "\n\nAlertas encontrados:"
                    for alert in analysis["alertas"]:
                        data_summary += f"\n⚠️ {alert['mensagem']}"

            else:
                data_summary = (
                    f"Encontrei {data.get('total', 0)} registros do tipo {data['tipo']}"
                )

            # Generate AI response
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"O usuário perguntou: '{original_query}'\n\nDados encontrados:\n{data_summary}\n\nExplique esses dados de forma clara e útil.",
                },
            ]

            response = await self.ai_client.chat_completion(
                messages=messages, max_tokens=500, temperature=0.7
            )

            return response.content

        except Exception as e:
            logger.error(f"Error formatting with AI: {e}")
            return self._format_response_simple(data)

    def _format_response_simple(self, data: dict) -> str:
        """Simple formatting without AI."""
        if not data.get("dados"):
            return "Não encontrei dados com os critérios especificados. Tente refinar sua busca."

        response = f"Encontrei {data.get('total', 0)} registros.\n\n"

        if data["tipo"] == "contratos" and data.get("dados"):
            response += "Principais contratos:\n"
            for i, contract in enumerate(data["dados"][:5], 1):
                response += f"{i}. {contract.get('objeto', 'Sem descrição')[:100]}...\n"
                response += f"   Valor: R$ {contract.get('valorTotal', 0):,.2f}\n"
                response += f"   Fornecedor: {contract.get('nomeFantasiaFornecedor', 'Não informado')}\n\n"

        return response


# Singleton instance
chat_data_integration = ChatDataIntegration()
