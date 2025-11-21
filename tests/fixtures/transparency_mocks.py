"""
Mock fixtures for Portal da Transparência API responses.

These mocks simulate real API responses for testing without hitting the actual API.
Based on real responses from Portal da Transparência.
"""

from typing import Any

# Mock responses for various API endpoints
MOCK_CONTRATOS_RESPONSE = {
    "status": 200,
    "data": [
        {
            "id": 1234567,
            "numero": "2025/001234",
            "dataAssinatura": "2025-01-15",
            "dataVigenciaInicio": "2025-01-20",
            "dataVigenciaFim": "2026-01-20",
            "valorInicial": 150000.00,
            "valorAtual": 165000.00,
            "objeto": "Serviços de consultoria em TI para modernização de sistemas",
            "fornecedor": {
                "id": 98765,
                "nome": "Tech Solutions LTDA",
                "cnpj": "12.345.678/0001-90",
                "municipio": "São Paulo",
                "uf": "SP",
            },
            "orgao": {
                "codigo": "26000",
                "nome": "Ministério da Educação",
                "sigla": "MEC",
            },
            "modalidadeLicitacao": {"codigo": 6, "descricao": "Pregão Eletrônico"},
            "situacao": "Ativo",
            "aditivos": [
                {
                    "numero": 1,
                    "data": "2025-10-15",
                    "valor": 15000.00,
                    "justificativa": "Acréscimo de serviços",
                }
            ],
        },
        {
            "id": 1234568,
            "numero": "2025/001235",
            "dataAssinatura": "2025-02-01",
            "dataVigenciaInicio": "2025-02-10",
            "dataVigenciaFim": "2025-08-10",
            "valorInicial": 75000.00,
            "valorAtual": 75000.00,
            "objeto": "Fornecimento de material de escritório",
            "fornecedor": {
                "id": 98766,
                "nome": "Papelaria Central ME",
                "cnpj": "98.765.432/0001-10",
                "municipio": "Brasília",
                "uf": "DF",
            },
            "orgao": {
                "codigo": "25000",
                "nome": "Ministério da Economia",
                "sigla": "ME",
            },
            "modalidadeLicitacao": {"codigo": 6, "descricao": "Pregão Eletrônico"},
            "situacao": "Ativo",
            "aditivos": [],
        },
    ],
    "count": 2,
    "hasMore": False,
}

MOCK_LICITACOES_RESPONSE = {
    "status": 200,
    "data": [
        {
            "id": 555666,
            "numero": "PE-2025-001",
            "dataAbertura": "2025-03-15T10:00:00",
            "dataPublicacao": "2025-03-01",
            "objeto": "Contratação de serviços de desenvolvimento de software",
            "valorEstimado": 500000.00,
            "modalidade": {"codigo": 6, "descricao": "Pregão Eletrônico"},
            "situacao": {"codigo": 1, "descricao": "Em andamento"},
            "orgao": {"codigo": "30000", "nome": "Ministério da Saúde", "sigla": "MS"},
            "itens": [
                {
                    "numero": 1,
                    "descricao": "Desenvolvimento de sistema web",
                    "quantidade": 1,
                    "unidade": "Serviço",
                    "valorEstimado": 300000.00,
                },
                {
                    "numero": 2,
                    "descricao": "Desenvolvimento de aplicativo mobile",
                    "quantidade": 1,
                    "unidade": "Serviço",
                    "valorEstimado": 200000.00,
                },
            ],
            "participantes": [],
        }
    ],
    "count": 1,
    "hasMore": True,
}

MOCK_SERVIDORES_RESPONSE = {
    "status": 200,
    "data": [
        {
            "id": 111222,
            "nome": "João da Silva Santos",
            "cpf": "***.456.789-**",
            "matricula": "1234567",
            "cargo": {
                "codigo": "414210",
                "descricao": "ANALISTA DE TECNOLOGIA DA INFORMACAO",
            },
            "funcao": {"codigo": "FCT-15", "descricao": "Coordenador de TI"},
            "orgaoLotacao": {
                "codigo": "26000",
                "nome": "Ministério da Educação",
                "sigla": "MEC",
            },
            "orgaoExercicio": {
                "codigo": "26000",
                "nome": "Ministério da Educação",
                "sigla": "MEC",
            },
            "remuneracaoBasica": 8500.00,
            "gratificacoes": 2500.00,
            "auxilios": 1200.00,
            "totalBruto": 12200.00,
            "descontos": 2800.00,
            "totalLiquido": 9400.00,
            "dataReferencia": "2025-10",
        }
    ],
    "count": 1,
    "hasMore": True,
}

MOCK_CONVENIOS_RESPONSE = {
    "status": 200,
    "data": [
        {
            "id": 888999,
            "numero": "900123/2025",
            "dataAssinatura": "2025-01-10",
            "dataVigenciaInicio": "2025-01-15",
            "dataVigenciaFim": "2026-01-15",
            "valorTotal": 1000000.00,
            "valorRepassado": 250000.00,
            "valorContrapartida": 50000.00,
            "objeto": "Construção de quadra poliesportiva",
            "concedente": {
                "codigo": "51000",
                "nome": "Ministério do Esporte",
                "sigla": "MESP",
            },
            "convenente": {
                "codigo": "00000000000191",
                "nome": "Município de Exemplo",
                "tipo": "Município",
            },
            "situacao": {"codigo": 2, "descricao": "Em execução"},
            "percentualExecutado": 25.0,
            "prestacaoContas": {"situacao": "Em dia", "dataUltima": "2025-10-30"},
        }
    ],
    "count": 1,
    "hasMore": False,
}

# Error responses
MOCK_ERROR_403 = {
    "status": 403,
    "error": "Forbidden",
    "message": "Access denied. Invalid API key or insufficient permissions.",
}

MOCK_ERROR_404 = {
    "status": 404,
    "error": "Not Found",
    "message": "The requested resource was not found.",
}

MOCK_ERROR_500 = {
    "status": 500,
    "error": "Internal Server Error",
    "message": "An error occurred processing your request. Please try again later.",
}

# Aggregated data for analysis
MOCK_ANOMALY_DATA = {
    "contratos_suspeitos": [
        {
            "contrato_id": 1234567,
            "razao": "Aditivo aumentou valor em 10% sem justificativa adequada",
            "score_anomalia": 0.85,
            "tipo_anomalia": "valor_suspeito",
        },
        {
            "contrato_id": 999888,
            "razao": "Múltiplos contratos com mesmo fornecedor em curto período",
            "score_anomalia": 0.72,
            "tipo_anomalia": "concentracao_fornecedor",
        },
    ],
    "estatisticas": {
        "total_contratos": 150,
        "valor_total": 15000000.00,
        "contratos_suspeitos": 12,
        "percentual_suspeito": 8.0,
    },
}


class TransparencyAPIMock:
    """Mock class for Portal da Transparência API client."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.call_count = 0
        self.last_endpoint = None

    async def get_contratos(self, **kwargs) -> dict[str, Any]:
        """Mock get_contratos method."""
        self.call_count += 1
        self.last_endpoint = "contratos"

        # Simulate API key validation
        if not self.api_key:
            return MOCK_ERROR_403

        # Simulate random failures (10% chance)
        import random

        if random.random() < 0.1:
            return MOCK_ERROR_500

        return MOCK_CONTRATOS_RESPONSE

    async def get_licitacoes(self, **kwargs) -> dict[str, Any]:
        """Mock get_licitacoes method."""
        self.call_count += 1
        self.last_endpoint = "licitacoes"

        if not self.api_key:
            return MOCK_ERROR_403

        return MOCK_LICITACOES_RESPONSE

    async def get_servidores(self, **kwargs) -> dict[str, Any]:
        """Mock get_servidores method."""
        self.call_count += 1
        self.last_endpoint = "servidores"

        if not self.api_key:
            return MOCK_ERROR_403

        return MOCK_SERVIDORES_RESPONSE

    async def get_convenios(self, **kwargs) -> dict[str, Any]:
        """Mock get_convenios method."""
        self.call_count += 1
        self.last_endpoint = "convenios"

        if not self.api_key:
            return MOCK_ERROR_403

        return MOCK_CONVENIOS_RESPONSE

    async def detect_anomalies(self, data: list[dict]) -> dict[str, Any]:
        """Mock anomaly detection."""
        self.call_count += 1
        self.last_endpoint = "anomalies"

        return MOCK_ANOMALY_DATA

    async def close(self):
        """Mock cleanup method."""
        pass


def get_mock_transparency_client(api_key: str = "test_key") -> TransparencyAPIMock:
    """Factory function to create mock transparency client."""
    return TransparencyAPIMock(api_key)


# Pytest fixtures
import pytest


@pytest.fixture
def mock_transparency_client():
    """Pytest fixture for mock transparency client."""
    return TransparencyAPIMock(api_key="test_key")


@pytest.fixture
def mock_contratos():
    """Pytest fixture for mock contratos response."""
    return MOCK_CONTRATOS_RESPONSE


@pytest.fixture
def mock_licitacoes():
    """Pytest fixture for mock licitacoes response."""
    return MOCK_LICITACOES_RESPONSE


@pytest.fixture
def mock_servidores():
    """Pytest fixture for mock servidores response."""
    return MOCK_SERVIDORES_RESPONSE


@pytest.fixture
def mock_convenios():
    """Pytest fixture for mock convenios response."""
    return MOCK_CONVENIOS_RESPONSE


@pytest.fixture
def mock_anomaly_data():
    """Pytest fixture for mock anomaly data."""
    return MOCK_ANOMALY_DATA
