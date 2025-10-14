"""
API Registry Implementation

Central registry for all government APIs with capability-based discovery.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.core import get_logger

logger = get_logger(__name__)


class APICapability(str, Enum):
    """Capabilities that APIs can provide."""

    # Company & Person Data
    CNPJ_LOOKUP = "cnpj_lookup"
    CPF_LOOKUP = "cpf_lookup"
    COMPANY_PARTNERS = "company_partners"

    # Procurement & Contracts
    BIDDING_SEARCH = "bidding_search"
    CONTRACT_SEARCH = "contract_search"
    PRICE_REGISTRATION = "price_registration"
    ANNUAL_PROCUREMENT_PLAN = "annual_procurement_plan"
    SUPPLIER_SEARCH = "supplier_search"

    # Financial & Economic
    ECONOMIC_INDICATORS = "economic_indicators"
    INTEREST_RATES = "interest_rates"
    EXCHANGE_RATES = "exchange_rates"
    INFLATION_DATA = "inflation_data"
    BUDGET_DATA = "budget_data"
    PUBLIC_EXPENSES = "public_expenses"

    # Health
    HEALTH_STATISTICS = "health_statistics"
    HOSPITAL_DATA = "hospital_data"
    VACCINATION_DATA = "vaccination_data"
    MORTALITY_DATA = "mortality_data"

    # Education
    EDUCATION_STATISTICS = "education_statistics"
    SCHOOL_DATA = "school_data"
    EDUCATION_INDICATORS = "education_indicators"

    # Demographics
    POPULATION_DATA = "population_data"
    DEMOGRAPHIC_INDICATORS = "demographic_indicators"

    # Legal & Compliance
    CRIMINAL_RECORDS = "criminal_records"
    TAX_COMPLIANCE = "tax_compliance"
    LEGAL_DOCUMENTS = "legal_documents"


@dataclass
class APIRegistration:
    """Registration of an API in the catalog."""

    api_name: str
    display_name: str
    client_class: str  # Full path to client class
    capabilities: list[APICapability]

    # Configuration
    base_url: str
    requires_auth: bool = False
    auth_type: str | None = None  # api_key, oauth2, none

    # Performance characteristics
    default_timeout: int = 30
    rate_limit_per_minute: int | None = None
    cache_ttl_seconds: int = 3600

    # Reliability
    fallback_apis: list[str] = None
    circuit_breaker_threshold: int = 5

    # Metadata
    description: str = ""
    documentation_url: str | None = None
    status: str = "active"  # active, deprecated, beta

    def __post_init__(self) -> None:
        if self.fallback_apis is None:
            self.fallback_apis = []


class APIRegistry:
    """
    Central registry of all available government APIs.

    Provides capability-based discovery and unified access to API clients.
    """

    def __init__(self) -> None:
        self._apis: dict[str, APIRegistration] = {}
        self._capability_index: dict[APICapability, list[str]] = {}
        self.logger = get_logger(__name__)

        # Register all APIs
        self._register_all_apis()

    def _register_all_apis(self) -> None:
        """Register all available APIs."""

        # Federal Government APIs
        self._register_minha_receita()
        self._register_banco_central()
        self._register_pncp()
        self._register_compras_gov()
        self._register_ibge()
        self._register_datasus()
        self._register_inep()
        self._register_portal_transparencia()

    def _register_minha_receita(self) -> None:
        """Register Minha Receita API."""
        self.register(
            APIRegistration(
                api_name="minha_receita",
                display_name="Minha Receita (CNPJ)",
                client_class="src.services.transparency_apis.federal_apis.minha_receita_client.MinhaReceitaClient",
                capabilities=[
                    APICapability.CNPJ_LOOKUP,
                    APICapability.COMPANY_PARTNERS,
                ],
                base_url="https://minhareceita.org",
                requires_auth=False,
                cache_ttl_seconds=86400,  # 24 hours
                description="Open-source CNPJ data from Receita Federal without CAPTCHA",
                documentation_url="https://docs.minhareceita.org",
            )
        )

    def _register_banco_central(self) -> None:
        """Register Banco Central API."""
        self.register(
            APIRegistration(
                api_name="banco_central",
                display_name="Banco Central do Brasil",
                client_class="src.services.transparency_apis.federal_apis.bcb_client.BancoCentralClient",
                capabilities=[
                    APICapability.ECONOMIC_INDICATORS,
                    APICapability.INTEREST_RATES,
                    APICapability.EXCHANGE_RATES,
                    APICapability.INFLATION_DATA,
                ],
                base_url="https://api.bcb.gov.br",
                requires_auth=False,
                cache_ttl_seconds=3600,  # 1 hour
                description="Brazilian Central Bank open data APIs (SELIC, exchange rates, PIX statistics)",
                documentation_url="https://dadosabertos.bcb.gov.br/",
            )
        )

    def _register_pncp(self) -> None:
        """Register PNCP API."""
        self.register(
            APIRegistration(
                api_name="pncp",
                display_name="PNCP - Portal Nacional de Contratações",
                client_class="src.services.transparency_apis.federal_apis.pncp_client.PNCPClient",
                capabilities=[
                    APICapability.BIDDING_SEARCH,
                    APICapability.CONTRACT_SEARCH,
                    APICapability.PRICE_REGISTRATION,
                    APICapability.ANNUAL_PROCUREMENT_PLAN,
                ],
                base_url="https://pncp.gov.br/api/consulta/v1",
                requires_auth=False,
                cache_ttl_seconds=3600,  # 1 hour
                description="Mandatory national portal for all public procurement (Law 14.133/2021)",
                documentation_url="https://pncp.gov.br/api/pncp/swagger-ui/index.html",
            )
        )

    def _register_compras_gov(self) -> None:
        """Register Compras.gov.br API."""
        self.register(
            APIRegistration(
                api_name="compras_gov",
                display_name="Compras.gov.br",
                client_class="src.services.transparency_apis.federal_apis.compras_gov_client.ComprasGovClient",
                capabilities=[
                    APICapability.BIDDING_SEARCH,
                    APICapability.CONTRACT_SEARCH,
                    APICapability.SUPPLIER_SEARCH,
                ],
                base_url="http://compras.dados.gov.br",
                requires_auth=False,
                cache_ttl_seconds=86400,  # 24 hours (historical data)
                fallback_apis=[
                    "pncp"
                ],  # PNCP can provide similar data for recent years
                description="Historical government procurement data (until 2022)",
                documentation_url="https://compras.dados.gov.br/docs/home.html",
            )
        )

    def _register_ibge(self) -> None:
        """Register IBGE API."""
        self.register(
            APIRegistration(
                api_name="ibge",
                display_name="IBGE - Instituto Brasileiro de Geografia e Estatística",
                client_class="src.services.transparency_apis.federal_apis.ibge_client.IBGEClient",
                capabilities=[
                    APICapability.POPULATION_DATA,
                    APICapability.DEMOGRAPHIC_INDICATORS,
                    APICapability.ECONOMIC_INDICATORS,
                ],
                base_url="https://servicodados.ibge.gov.br/api/v3",
                requires_auth=False,
                cache_ttl_seconds=86400,  # 24 hours
                description="Brazilian Institute of Geography and Statistics - demographics, economy, poverty",
                documentation_url="https://servicodados.ibge.gov.br/api/docs",
            )
        )

    def _register_datasus(self) -> None:
        """Register DataSUS API."""
        self.register(
            APIRegistration(
                api_name="datasus",
                display_name="DataSUS - Ministério da Saúde",
                client_class="src.services.transparency_apis.federal_apis.datasus_client.DataSUSClient",
                capabilities=[
                    APICapability.HEALTH_STATISTICS,
                    APICapability.HOSPITAL_DATA,
                    APICapability.VACCINATION_DATA,
                    APICapability.MORTALITY_DATA,
                ],
                base_url="https://opendatasus.saude.gov.br/api/3/action",
                requires_auth=False,
                cache_ttl_seconds=3600,  # 1 hour
                description="Ministry of Health open data - SUS, vaccination, mortality",
                documentation_url="https://opendatasus.saude.gov.br/",
            )
        )

    def _register_inep(self) -> None:
        """Register INEP API."""
        self.register(
            APIRegistration(
                api_name="inep",
                display_name="INEP - Instituto Nacional de Estudos e Pesquisas",
                client_class="src.services.transparency_apis.federal_apis.inep_client.INEPClient",
                capabilities=[
                    APICapability.EDUCATION_STATISTICS,
                    APICapability.SCHOOL_DATA,
                    APICapability.EDUCATION_INDICATORS,
                ],
                base_url="https://dados.gov.br/api/3/action",
                requires_auth=False,
                cache_ttl_seconds=86400,  # 24 hours
                description="National Institute of Studies and Research - IDEB, ENEM, school census",
                documentation_url="https://dados.gov.br/",
            )
        )

    def _register_portal_transparencia(self) -> None:
        """Register Portal da Transparência API."""
        self.register(
            APIRegistration(
                api_name="portal_transparencia",
                display_name="Portal da Transparência Federal",
                client_class="src.tools.transparency_api.TransparencyAPIClient",
                capabilities=[
                    APICapability.PUBLIC_EXPENSES,
                    APICapability.CONTRACT_SEARCH,
                ],
                base_url="https://api.portaldatransparencia.gov.br",
                requires_auth=True,
                auth_type="api_key",
                cache_ttl_seconds=3600,  # 1 hour
                circuit_breaker_threshold=3,  # Strict - API is unstable
                fallback_apis=["pncp", "compras_gov"],
                description="Federal transparency portal (22% endpoints working, 78% return 403)",
                documentation_url="https://api.portaldatransparencia.gov.br/swagger-ui/index.html",
                status="partial",  # Many endpoints blocked
            )
        )

    def register(self, registration: APIRegistration) -> None:
        """Register an API in the catalog."""
        self._apis[registration.api_name] = registration

        # Index by capabilities
        for capability in registration.capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = []
            self._capability_index[capability].append(registration.api_name)

        self.logger.info(f"Registered API: {registration.display_name}")

    def get_api(self, api_name: str) -> APIRegistration | None:
        """Get API registration by name."""
        return self._apis.get(api_name)

    def find_apis_by_capability(
        self, capability: APICapability
    ) -> list[APIRegistration]:
        """Find all APIs that provide a specific capability."""
        api_names = self._capability_index.get(capability, [])
        return [self._apis[name] for name in api_names if name in self._apis]

    def get_all_apis(self) -> list[APIRegistration]:
        """Get all registered APIs."""
        return list(self._apis.values())

    def get_client(self, api_name: str) -> Any:  # noqa: ANN401
        """
        Get API client instance.

        Returns:
            Instantiated API client
        """
        registration = self.get_api(api_name)
        if not registration:
            raise ValueError(f"API not registered: {api_name}")

        # Dynamic import and instantiation
        module_path, class_name = registration.client_class.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name])
        client_class = getattr(module, class_name)

        return client_class(timeout=registration.default_timeout)

    def get_fallback_api(self, api_name: str) -> str | None:
        """Get fallback API for a failed API."""
        registration = self.get_api(api_name)
        if not registration or not registration.fallback_apis:
            return None
        return registration.fallback_apis[0]

    def get_apis_for_investigation(self, intent: str) -> list[APIRegistration]:
        """
        Get recommended APIs for an investigation intent.

        Returns APIs ordered by relevance.
        """
        # Map intents to required capabilities
        intent_capabilities = {
            "supplier_investigation": [
                APICapability.CNPJ_LOOKUP,
                APICapability.CONTRACT_SEARCH,
                APICapability.BIDDING_SEARCH,
                APICapability.TAX_COMPLIANCE,
            ],
            "contract_anomaly_detection": [
                APICapability.CONTRACT_SEARCH,
                APICapability.ECONOMIC_INDICATORS,
                APICapability.CNPJ_LOOKUP,
            ],
            "budget_analysis": [
                APICapability.BUDGET_DATA,
                APICapability.PUBLIC_EXPENSES,
                APICapability.ECONOMIC_INDICATORS,
            ],
            "health_budget_analysis": [
                APICapability.BUDGET_DATA,
                APICapability.HEALTH_STATISTICS,
                APICapability.DEMOGRAPHIC_INDICATORS,
            ],
        }

        required_capabilities = intent_capabilities.get(intent, [])

        # Find APIs that provide these capabilities
        api_names = set()
        for capability in required_capabilities:
            api_names.update(self._capability_index.get(capability, []))

        return [self._apis[name] for name in api_names if name in self._apis]
