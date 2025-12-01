"""
Chat Investigative Service
Real-time contract search with streaming during agent conversations.

Author: Anderson H. Silva
Date: 2025-11-25
Updated: 2025-12-01 - Added date filters and pagination for varied results
"""

import asyncio
import csv
import io
import json
import re
import secrets
from collections.abc import AsyncGenerator
from datetime import UTC, date, datetime, timedelta
from typing import Any

import httpx

from src.core import get_logger
from src.core.config import settings

logger = get_logger(__name__)

# Default search period (last N years)
DEFAULT_SEARCH_YEARS = 2

# HTTP Status Codes
HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_FORBIDDEN = 403


class ChatInvestigativeService:
    """
    Service for real-time data fetching during chat conversations.

    Provides streaming search capabilities that allow agents to:
    - Search contracts in real-time while responding
    - Fetch detailed contract data for download
    - Stream progress updates to the user
    """

    BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"

    # Organization codes (SIAFI)
    ORGAOS = {
        "saude": "36000",
        "educacao": "26000",
        "economia": "25000",
        "justica": "30000",
        "defesa": "52000",
        "meio_ambiente": "44000",
        "ciencia": "24000",
        "trabalho": "38000",
        "agricultura": "22000",
        "transportes": "39000",
    }

    ORGAO_NAMES = {
        "36000": "Ministério da Saúde",
        "26000": "Ministério da Educação",
        "25000": "Ministério da Economia",
        "30000": "Ministério da Justiça",
        "52000": "Ministério da Defesa",
        "44000": "Ministério do Meio Ambiente",
        "24000": "Ministério da Ciência e Tecnologia",
        "38000": "Ministério do Trabalho",
        "22000": "Ministério da Agricultura",
        "39000": "Ministério dos Transportes",
    }

    def __init__(self) -> None:
        """Initialize the investigative service."""
        self.api_key = getattr(settings, "transparency_api_key", None)
        if self.api_key and hasattr(self.api_key, "get_secret_value"):
            self.api_key = self.api_key.get_secret_value()

        self.client = None
        self._init_client()

        logger.info(
            f"ChatInvestigativeService initialized - API key: {'configured' if self.api_key else 'missing'}"
        )

    def _init_client(self) -> None:
        """Initialize HTTP client."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "CidadaoAI/1.0 (https://cidadao.ai)",
        }

        if self.api_key:
            headers["chave-api-dados"] = self.api_key

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=30.0,
        )

    def _detect_orgao_from_message(self, message: str) -> str | None:
        """Detect organization code from user message."""
        message_lower = message.lower()

        keyword_mapping = {
            "saude": ["saúde", "saude", "hospital", "médico", "medicamento", "sus"],
            "educacao": [
                "educação",
                "educacao",
                "escola",
                "universidade",
                "mec",
                "ensino",
            ],
            "economia": ["economia", "fazenda", "receita", "impostos", "orçamento"],
            "justica": ["justiça", "justica", "polícia", "policia", "segurança"],
            "defesa": ["defesa", "exército", "exercito", "marinha", "aeronáutica"],
            "meio_ambiente": ["ambiente", "meio ambiente", "ibama", "floresta"],
            "ciencia": ["ciência", "ciencia", "tecnologia", "pesquisa", "cnpq"],
            "trabalho": ["trabalho", "emprego", "trabalhador"],
            "agricultura": ["agricultura", "agro", "rural", "pecuária"],
            "transportes": ["transporte", "rodovia", "estrada", "infraestrutura"],
        }

        for orgao_key, keywords in keyword_mapping.items():
            if any(kw in message_lower for kw in keywords):
                return self.ORGAOS[orgao_key]

        # Default to Saúde (most requested)
        return self.ORGAOS["saude"]

    def _extract_year_from_message(self, message: str) -> int | None:
        """Extract year from user message if mentioned."""
        # Look for 4-digit years (2020-2030 range)
        years = re.findall(r"\b(202[0-9]|203[0-0])\b", message)
        if years:
            return int(years[0])
        return None

    def _build_date_range(self, message: str) -> tuple[str, str]:
        """
        Build date range for contract search.

        Returns dates in DD/MM/YYYY format required by the API.
        """
        # Check if user mentioned a specific year
        mentioned_year = self._extract_year_from_message(message)

        if mentioned_year:
            # Search the entire mentioned year
            start_date = f"01/01/{mentioned_year}"
            end_date = f"31/12/{mentioned_year}"
        else:
            # Default: last 2 years from today
            today = date.today()
            start = today - timedelta(days=DEFAULT_SEARCH_YEARS * 365)
            start_date = start.strftime("%d/%m/%Y")
            end_date = today.strftime("%d/%m/%Y")

        return start_date, end_date

    async def search_contracts_streaming(  # noqa: C901
        self,
        message: str,
        orgao_code: str | None = None,
        max_results: int = 10,
        page: int | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Search contracts with streaming progress updates.

        Yields events as the search progresses:
        - thinking: Agent is processing
        - searching: Querying API
        - found: Results found
        - contract: Individual contract data
        - complete: Search finished
        - error: Error occurred

        Args:
            message: User's search query
            orgao_code: Optional organization code (auto-detected if not provided)
            max_results: Maximum number of contracts to return
            page: Optional page number (random 1-5 if not provided for variety)

        Yields:
            Dict events with type and data
        """
        # Auto-detect organization if not provided
        if not orgao_code:
            orgao_code = self._detect_orgao_from_message(message)

        orgao_name = self.ORGAO_NAMES.get(orgao_code, "Órgão Federal")

        # Build date range based on message
        data_inicial, data_final = self._build_date_range(message)

        # Use random page for variety if not specified (not cryptographic, just for variation)
        if page is None:
            page = secrets.randbelow(3) + 1  # Random page 1-3

        # Phase 1: Thinking
        yield {
            "type": "thinking",
            "message": f"🔍 Analisando sua solicitação sobre {orgao_name}...",
            "agent": "Zumbi dos Palmares",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        await asyncio.sleep(0.3)

        # Phase 2: Searching
        yield {
            "type": "searching",
            "message": f"📡 Consultando Portal da Transparência (órgão: {orgao_code}, período: {data_inicial} a {data_final})...",
            "orgao": orgao_code,
            "orgao_nome": orgao_name,
            "periodo": {"inicio": data_inicial, "fim": data_final},
            "pagina": page,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        if not self.api_key:
            yield {
                "type": "warning",
                "message": "⚠️ API key não configurada - usando dados de demonstração",
                "timestamp": datetime.now(UTC).isoformat(),
            }
            # Return demo data
            async for event in self._generate_demo_contracts(
                orgao_code, orgao_name, max_results
            ):
                yield event
            return

        try:
            # Build query parameters with date filters
            params = {
                "codigoOrgao": orgao_code,
                "dataInicial": data_inicial,
                "dataFinal": data_final,
                "pagina": page,
                "tamanhoPagina": max_results,
            }

            logger.info(f"Searching contracts with params: {params}")

            # Make API request
            response = await self.client.get("/contratos", params=params)

            if response.status_code == HTTP_FORBIDDEN:
                yield {
                    "type": "error",
                    "message": "🚫 Acesso negado pela API (CloudFront). Usando dados alternativos...",
                    "error_code": 403,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                async for event in self._generate_demo_contracts(
                    orgao_code, orgao_name, max_results
                ):
                    yield event
                return

            if response.status_code == HTTP_BAD_REQUEST:
                error_msg = response.text
                yield {
                    "type": "error",
                    "message": f"⚠️ Parâmetros inválidos: {error_msg[:100]}",
                    "error_code": 400,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                return

            response.raise_for_status()
            data = response.json()

            # Parse response
            contracts = data if isinstance(data, list) else data.get("resultado", [])
            total = (
                len(contracts)
                if isinstance(data, list)
                else data.get("quantidadeTotal", len(contracts))
            )

            # Extract year range for display
            year_start = data_inicial.split("/")[-1]
            year_end = data_final.split("/")[-1]
            period_display = (
                f"{year_start}"
                if year_start == year_end
                else f"{year_start}-{year_end}"
            )

            yield {
                "type": "found",
                "message": f"✅ Encontrados {total} contratos ({period_display}, página {page})!",
                "total": total,
                "showing": min(len(contracts), max_results),
                "periodo": {"inicio": data_inicial, "fim": data_final},
                "pagina": page,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            await asyncio.sleep(0.2)

            # Phase 3: Stream individual contracts
            for i, contract in enumerate(contracts[:max_results]):
                yield {
                    "type": "contract",
                    "index": i + 1,
                    "total": min(len(contracts), max_results),
                    "data": self._format_contract(contract),
                    "raw": contract,  # Include raw for download
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                await asyncio.sleep(0.1)  # Small delay for streaming effect

            # Phase 4: Complete
            yield {
                "type": "complete",
                "message": f"🎯 Pesquisa concluída: {len(contracts[:max_results])} contratos do {orgao_name} ({period_display})",
                "total_contracts": len(contracts[:max_results]),
                "orgao": orgao_code,
                "orgao_nome": orgao_name,
                "periodo": {"inicio": data_inicial, "fim": data_final},
                "pagina": page,
                "download_available": True,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except httpx.TimeoutException:
            yield {
                "type": "error",
                "message": "⏱️ Timeout na conexão com o Portal da Transparência",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error in streaming search: {e}")
            yield {
                "type": "error",
                "message": f"❌ Erro na pesquisa: {str(e)}",
                "timestamp": datetime.now(UTC).isoformat(),
            }

    async def _generate_demo_contracts(
        self, orgao_code: str, orgao_name: str, max_results: int
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Generate demo contracts when API is unavailable."""

        demo_objects = [
            "Aquisição de medicamentos essenciais",
            "Manutenção de equipamentos hospitalares",
            "Serviços de limpeza e conservação",
            "Fornecimento de material de escritório",
            "Contratação de serviços de TI",
            "Obras de reforma predial",
            "Aquisição de veículos oficiais",
            "Serviços de vigilância patrimonial",
            "Fornecimento de alimentação",
            "Consultoria especializada",
        ]

        demo_suppliers = [
            ("12.345.678/0001-90", "Tech Solutions Ltda"),
            ("98.765.432/0001-10", "Saúde & Vida Distribuidora"),
            ("11.222.333/0001-44", "ServiçosPro Brasil"),
            ("55.666.777/0001-88", "Construtora União"),
            ("33.444.555/0001-22", "Logística Express"),
        ]

        yield {
            "type": "found",
            "message": f"✅ Encontrados {max_results} contratos (modo demonstração)",
            "total": max_results,
            "showing": max_results,
            "demo_mode": True,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        await asyncio.sleep(0.2)

        for i in range(min(max_results, len(demo_objects))):
            supplier = demo_suppliers[i % len(demo_suppliers)]
            contract = {
                "id": 698621306 + i,
                "numero": f"00{38 + i:03d}/2024",
                "objeto": demo_objects[i],
                "numeroProcesso": f"23000.00{1234 + i:04d}/2024-{10 + i:02d}",
                "fundamentoLegal": "Lei 14.133/2021",
                "dataAssinatura": (
                    date.today() - timedelta(days=30 + i * 10)
                ).isoformat(),
                "dataVigenciaInicio": (
                    date.today() - timedelta(days=25 + i * 10)
                ).isoformat(),
                "dataVigenciaFim": (date.today() + timedelta(days=365)).isoformat(),
                "valorInicial": 150000.00 + (i * 75000),
                "valorFinal": 180000.00 + (i * 80000),
                "situacao": "Ativo",
                "modalidadeCompra": "Pregão Eletrônico",
                "codigoOrgao": orgao_code,
                "nomeOrgao": orgao_name,
                "cnpjFornecedor": supplier[0],
                "nomeFornecedor": supplier[1],
            }

            yield {
                "type": "contract",
                "index": i + 1,
                "total": max_results,
                "data": self._format_contract(contract),
                "raw": contract,
                "demo_mode": True,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            await asyncio.sleep(0.15)

        yield {
            "type": "complete",
            "message": f"🎯 Pesquisa concluída (demonstração): {max_results} contratos do {orgao_name}",
            "total_contracts": max_results,
            "orgao": orgao_code,
            "orgao_nome": orgao_name,
            "download_available": True,
            "demo_mode": True,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def _format_contract(self, contract: dict[str, Any]) -> dict[str, Any]:
        """Format contract data for display."""
        valor = contract.get("valorInicial") or contract.get("valorFinal") or 0

        return {
            "id": contract.get("id"),
            "numero": contract.get("numero", "N/A"),
            "objeto": contract.get("objeto", "Sem descrição")[:200],
            "valor_formatado": f"R$ {valor:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
            "valor": valor,
            "fornecedor": contract.get("nomeFornecedor")
            or contract.get("nomeFantasiaFornecedor", "Não informado"),
            "cnpj_fornecedor": contract.get("cnpjFornecedor", "N/A"),
            "orgao": contract.get("nomeOrgao", "N/A"),
            "data_assinatura": contract.get("dataAssinatura", "N/A"),
            "vigencia_inicio": contract.get("dataVigenciaInicio", "N/A"),
            "vigencia_fim": contract.get("dataVigenciaFim", "N/A"),
            "situacao": contract.get("situacao", "N/A"),
            "modalidade": contract.get("modalidadeCompra", "N/A"),
            "processo": contract.get("numeroProcesso", "N/A"),
        }

    async def get_contract_details(self, contract_id: int) -> dict[str, Any]:
        """
        Get detailed contract information for download.

        Note: The /contratos/{id} endpoint returns 403 from CloudFront.
        We need to search by contract number instead.

        Args:
            contract_id: Contract ID

        Returns:
            Full contract details or error
        """
        if not self.api_key:
            return {
                "error": "API key not configured",
                "demo_mode": True,
                "contract_id": contract_id,
            }

        # Try direct endpoint (may be blocked)
        try:
            response = await self.client.get(f"/contratos/{contract_id}")

            if response.status_code == HTTP_OK:
                return {
                    "success": True,
                    "contract": response.json(),
                    "download_format": ["json", "pdf"],
                }
            if response.status_code == HTTP_FORBIDDEN:
                return {
                    "error": "Endpoint bloqueado pelo CloudFront",
                    "error_code": 403,
                    "contract_id": contract_id,
                    "workaround": "Use a listagem de contratos para obter dados",
                }
            return {
                "error": f"HTTP {response.status_code}",
                "contract_id": contract_id,
            }
        except Exception as e:
            return {
                "error": str(e),
                "contract_id": contract_id,
            }

    async def generate_contract_report(
        self, contracts: list[dict[str, Any]], output_format: str = "json"
    ) -> dict[str, Any]:
        """
        Generate a downloadable report from contracts.

        Args:
            contracts: List of contract data
            output_format: Output format (json, csv, txt)

        Returns:
            Report data ready for download
        """
        timestamp = datetime.now(UTC).isoformat()

        if output_format == "json":
            content = json.dumps(
                {
                    "relatorio": "Contratos do Portal da Transparência",
                    "gerado_em": timestamp,
                    "total_contratos": len(contracts),
                    "valor_total": sum(c.get("valor", 0) for c in contracts),
                    "contratos": contracts,
                },
                ensure_ascii=False,
                indent=2,
            )

            return {
                "filename": f"contratos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "content": content,
                "content_type": "application/json",
                "size": len(content),
            }

        if output_format == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=[
                    "id",
                    "numero",
                    "objeto",
                    "valor",
                    "fornecedor",
                    "cnpj_fornecedor",
                    "orgao",
                    "data_assinatura",
                    "situacao",
                ],
            )
            writer.writeheader()

            for contract in contracts:
                writer.writerow(
                    {
                        "id": contract.get("id", ""),
                        "numero": contract.get("numero", ""),
                        "objeto": contract.get("objeto", "")[:100],
                        "valor": contract.get("valor", 0),
                        "fornecedor": contract.get("fornecedor", ""),
                        "cnpj_fornecedor": contract.get("cnpj_fornecedor", ""),
                        "orgao": contract.get("orgao", ""),
                        "data_assinatura": contract.get("data_assinatura", ""),
                        "situacao": contract.get("situacao", ""),
                    }
                )

            content = output.getvalue()

            return {
                "filename": f"contratos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "content": content,
                "content_type": "text/csv",
                "size": len(content),
            }

        if output_format == "txt":
            lines = [
                "=" * 60,
                "RELATÓRIO DE CONTRATOS - PORTAL DA TRANSPARÊNCIA",
                f"Gerado em: {timestamp}",
                f"Total de contratos: {len(contracts)}",
                f"Valor total: R$ {sum(c.get('valor', 0) for c in contracts):,.2f}",
                "=" * 60,
                "",
            ]

            for i, contract in enumerate(contracts, 1):
                lines.extend(
                    [
                        f"CONTRATO {i}",
                        "-" * 40,
                        f"Número: {contract.get('numero', 'N/A')}",
                        f"Objeto: {contract.get('objeto', 'N/A')}",
                        f"Valor: {contract.get('valor_formatado', 'N/A')}",
                        f"Fornecedor: {contract.get('fornecedor', 'N/A')}",
                        f"CNPJ: {contract.get('cnpj_fornecedor', 'N/A')}",
                        f"Órgão: {contract.get('orgao', 'N/A')}",
                        f"Data Assinatura: {contract.get('data_assinatura', 'N/A')}",
                        f"Situação: {contract.get('situacao', 'N/A')}",
                        "",
                    ]
                )

            content = "\n".join(lines)

            return {
                "filename": f"contratos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "content": content,
                "content_type": "text/plain",
                "size": len(content),
            }

        return {"error": f"Formato não suportado: {format}"}

    async def close(self) -> None:
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()


class _ServiceContainer:
    """Container for singleton service instance."""

    _instance: ChatInvestigativeService | None = None

    @classmethod
    def get_instance(cls) -> ChatInvestigativeService:
        """Get or create the investigative service singleton."""
        if cls._instance is None:
            cls._instance = ChatInvestigativeService()
        return cls._instance


def get_investigative_service() -> ChatInvestigativeService:
    """Get or create the investigative service singleton."""
    return _ServiceContainer.get_instance()
