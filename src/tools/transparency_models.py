"""
Module: tools.transparency_models
Description: Data models for Portal da Transparência API responses
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, field_validator
from pydantic import Field as PydanticField


class Organization(BaseModel):
    """Government organization model."""

    codigo: str | None = PydanticField(default=None, description="Organization code")
    nome: str | None = PydanticField(default=None, description="Organization name")
    sigla: str | None = PydanticField(default=None, description="Organization acronym")
    descricao: str | None = PydanticField(
        default=None, description="Organization description"
    )


class Supplier(BaseModel):
    """Supplier/contractor model."""

    cnpj: str | None = PydanticField(default=None, description="CNPJ")
    cpf: str | None = PydanticField(default=None, description="CPF")
    nome: str | None = PydanticField(default=None, description="Name")
    razao_social: str | None = PydanticField(default=None, description="Corporate name")
    municipio: str | None = PydanticField(default=None, description="Municipality")
    uf: str | None = PydanticField(default=None, description="State")

    @field_validator("cnpj", "cpf")
    @classmethod
    def validate_document_format(cls, v):
        """Validate document format."""
        if v:
            # Remove common formatting characters
            v = v.replace(".", "").replace("/", "").replace("-", "").replace(" ", "")

            # Basic length validation
            if v and not v.isdigit():
                return None

            if v and len(v) not in [11, 14]:  # CPF or CNPJ
                return None

        return v


class Contract(BaseModel):
    """Government contract model."""

    id: str | None = PydanticField(default=None, description="Contract ID")
    numero: str | None = PydanticField(default=None, description="Contract number")
    ano: int | None = PydanticField(default=None, description="Year")
    mes: int | None = PydanticField(default=None, description="Month")

    # Dates
    data_assinatura: str | date | None = PydanticField(
        default=None, description="Signature date"
    )
    data_inicio_vigencia: str | date | None = PydanticField(
        default=None, description="Start date"
    )
    data_fim_vigencia: str | date | None = PydanticField(
        default=None, description="End date"
    )
    data_publicacao: str | date | None = PydanticField(
        default=None, description="Publication date"
    )

    # Financial
    valor_inicial: Decimal | None = PydanticField(
        default=None, description="Initial value"
    )
    valor_global: Decimal | None = PydanticField(
        default=None, description="Global value"
    )
    valor_acumulado: Decimal | None = PydanticField(
        default=None, description="Accumulated value"
    )

    # Description
    objeto: str | None = PydanticField(default=None, description="Contract object")
    objeto_resumido: str | None = PydanticField(
        default=None, description="Contract summary"
    )

    # Classification
    modalidade_contratacao: int | str | None = PydanticField(
        default=None, description="Contracting modality"
    )
    modalidade_licitacao: int | str | None = PydanticField(
        default=None, description="Bidding modality"
    )
    situacao: str | None = PydanticField(default=None, description="Status")

    # Related entities
    orgao: Organization | None = PydanticField(default=None, description="Organization")
    fornecedor: Supplier | None = PydanticField(default=None, description="Supplier")

    # Additional fields
    fundamento_legal: str | None = PydanticField(
        default=None, description="Legal basis"
    )
    origem_recurso: str | None = PydanticField(
        default=None, description="Resource origin"
    )

    @field_validator(
        "data_assinatura",
        "data_inicio_vigencia",
        "data_fim_vigencia",
        "data_publicacao",
    )
    @classmethod
    def parse_date(cls, v):
        """Parse date from various formats."""
        if isinstance(v, str):
            # Try different date formats
            for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            return None
        return v

    @field_validator("valor_inicial", "valor_global", "valor_acumulado")
    @classmethod
    def parse_decimal(cls, v):
        """Parse decimal values."""
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            # Remove common formatting
            v = v.replace(",", ".").replace(" ", "")
            try:
                return Decimal(v)
            except:
                return None
        return v


class Expense(BaseModel):
    """Government expense model."""

    id: str | None = PydanticField(default=None, description="Expense ID")
    ano: int | None = PydanticField(default=None, description="Year")
    mes: int | None = PydanticField(default=None, description="Month")

    # Dates
    data_pagamento: str | date | None = PydanticField(
        default=None, description="Payment date"
    )
    data_documento: str | date | None = PydanticField(
        default=None, description="Document date"
    )

    # Financial
    valor: Decimal | None = PydanticField(default=None, description="Amount")
    valor_empenhado: Decimal | None = PydanticField(
        default=None, description="Committed amount"
    )
    valor_liquidado: Decimal | None = PydanticField(
        default=None, description="Liquidated amount"
    )
    valor_pago: Decimal | None = PydanticField(default=None, description="Paid amount")

    # Classification
    funcao: str | None = PydanticField(default=None, description="Function")
    subfuncao: str | None = PydanticField(default=None, description="Subfunction")
    programa: str | None = PydanticField(default=None, description="Program")
    acao: str | None = PydanticField(default=None, description="Action")
    elemento_despesa: str | None = PydanticField(
        default=None, description="Expense element"
    )

    # Description
    descricao: str | None = PydanticField(default=None, description="Description")
    documento: str | None = PydanticField(default=None, description="Document")

    # Related entities
    orgao: Organization | None = PydanticField(default=None, description="Organization")
    favorecido: Supplier | None = PydanticField(default=None, description="Beneficiary")

    @field_validator("data_pagamento", "data_documento")
    @classmethod
    def parse_date(cls, v):
        """Parse date from various formats."""
        if isinstance(v, str):
            for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            return None
        return v

    @field_validator("valor", "valor_empenhado", "valor_liquidado", "valor_pago")
    @classmethod
    def parse_decimal(cls, v):
        """Parse decimal values."""
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            v = v.replace(",", ".").replace(" ", "")
            try:
                return Decimal(v)
            except:
                return None
        return v


class Agreement(BaseModel):
    """Government agreement (convênio) model."""

    id: str | None = PydanticField(default=None, description="Agreement ID")
    numero: str | None = PydanticField(default=None, description="Agreement number")
    ano: int | None = PydanticField(default=None, description="Year")

    # Dates
    data_assinatura: str | date | None = PydanticField(
        default=None, description="Signature date"
    )
    data_inicio_vigencia: str | date | None = PydanticField(
        default=None, description="Start date"
    )
    data_fim_vigencia: str | date | None = PydanticField(
        default=None, description="End date"
    )
    data_publicacao: str | date | None = PydanticField(
        default=None, description="Publication date"
    )

    # Financial
    valor_global: Decimal | None = PydanticField(
        default=None, description="Global value"
    )
    valor_repasse: Decimal | None = PydanticField(
        default=None, description="Transfer value"
    )
    valor_contrapartida: Decimal | None = PydanticField(
        default=None, description="Counterpart value"
    )

    # Description
    objeto: str | None = PydanticField(default=None, description="Agreement object")
    situacao: str | None = PydanticField(default=None, description="Status")

    # Related entities
    orgao_superior: Organization | None = PydanticField(
        default=None, description="Superior organization"
    )
    orgao_vinculado: Organization | None = PydanticField(
        default=None, description="Linked organization"
    )
    convenente: Supplier | None = PydanticField(
        default=None, description="Agreement partner"
    )

    @field_validator(
        "data_assinatura",
        "data_inicio_vigencia",
        "data_fim_vigencia",
        "data_publicacao",
    )
    @classmethod
    def parse_date(cls, v):
        """Parse date from various formats."""
        if isinstance(v, str):
            for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            return None
        return v

    @field_validator("valor_global", "valor_repasse", "valor_contrapartida")
    @classmethod
    def parse_decimal(cls, v):
        """Parse decimal values."""
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            v = v.replace(",", ".").replace(" ", "")
            try:
                return Decimal(v)
            except:
                return None
        return v


class Bidding(BaseModel):
    """Government bidding (licitação) model."""

    id: str | None = PydanticField(default=None, description="Bidding ID")
    numero: str | None = PydanticField(default=None, description="Bidding number")
    ano: int | None = PydanticField(default=None, description="Year")

    # Dates
    data_abertura: str | date | None = PydanticField(
        default=None, description="Opening date"
    )
    data_homologacao: str | date | None = PydanticField(
        default=None, description="Approval date"
    )
    data_publicacao: str | date | None = PydanticField(
        default=None, description="Publication date"
    )

    # Financial
    valor_estimado: Decimal | None = PydanticField(
        default=None, description="Estimated value"
    )
    valor_homologado: Decimal | None = PydanticField(
        default=None, description="Approved value"
    )

    # Classification
    modalidade: str | None = PydanticField(default=None, description="Modality")
    situacao: str | None = PydanticField(default=None, description="Status")
    tipo: str | None = PydanticField(default=None, description="Type")

    # Description
    objeto: str | None = PydanticField(default=None, description="Bidding object")
    edital: str | None = PydanticField(default=None, description="Notice")

    # Related entities
    orgao: Organization | None = PydanticField(default=None, description="Organization")
    vencedor: Supplier | None = PydanticField(default=None, description="Winner")

    @field_validator("data_abertura", "data_homologacao", "data_publicacao")
    @classmethod
    def parse_date(cls, v):
        """Parse date from various formats."""
        if isinstance(v, str):
            for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            return None
        return v

    @field_validator("valor_estimado", "valor_homologado")
    @classmethod
    def parse_decimal(cls, v):
        """Parse decimal values."""
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            v = v.replace(",", ".").replace(" ", "")
            try:
                return Decimal(v)
            except:
                return None
        return v


class Servant(BaseModel):
    """Government servant model."""

    id: str | None = PydanticField(default=None, description="Servant ID")
    cpf: str | None = PydanticField(default=None, description="CPF")
    nome: str | None = PydanticField(default=None, description="Name")

    # Employment
    cargo: str | None = PydanticField(default=None, description="Position")
    funcao: str | None = PydanticField(default=None, description="Function")
    situacao: str | None = PydanticField(default=None, description="Status")
    regime_juridico: str | None = PydanticField(
        default=None, description="Legal regime"
    )

    # Financial
    remuneracao_basica: Decimal | None = PydanticField(
        default=None, description="Basic salary"
    )
    remuneracao_total: Decimal | None = PydanticField(
        default=None, description="Total salary"
    )

    # Dates
    data_ingresso: str | date | None = PydanticField(
        default=None, description="Entry date"
    )
    data_diploma_ingresso: str | date | None = PydanticField(
        default=None, description="Diploma date"
    )

    # Related entities
    orgao: Organization | None = PydanticField(default=None, description="Organization")

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v):
        """Validate CPF format."""
        if v:
            v = v.replace(".", "").replace("-", "").replace(" ", "")
            if v and (not v.isdigit() or len(v) != 11):
                return None
        return v

    @field_validator("data_ingresso", "data_diploma_ingresso")
    @classmethod
    def parse_date(cls, v):
        """Parse date from various formats."""
        if isinstance(v, str):
            for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            return None
        return v

    @field_validator("remuneracao_basica", "remuneracao_total")
    @classmethod
    def parse_decimal(cls, v):
        """Parse decimal values."""
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            v = v.replace(",", ".").replace(" ", "")
            try:
                return Decimal(v)
            except:
                return None
        return v


class SanctionedCompany(BaseModel):
    """Sanctioned company model (CEAF, CEIS, CNEP)."""

    cnpj: str | None = PydanticField(default=None, description="CNPJ")
    nome: str | None = PydanticField(default=None, description="Company name")
    razao_social: str | None = PydanticField(default=None, description="Corporate name")

    # Location
    municipio: str | None = PydanticField(default=None, description="Municipality")
    uf: str | None = PydanticField(default=None, description="State")

    # Sanction details
    tipo_sancao: str | None = PydanticField(default=None, description="Sanction type")
    data_inicio_sancao: str | date | None = PydanticField(
        default=None, description="Sanction start date"
    )
    data_fim_sancao: str | date | None = PydanticField(
        default=None, description="Sanction end date"
    )
    data_publicacao: str | date | None = PydanticField(
        default=None, description="Publication date"
    )

    # Legal details
    fundamentacao_legal: str | None = PydanticField(
        default=None, description="Legal basis"
    )
    descricao_fundamentacao: str | None = PydanticField(
        default=None, description="Basis description"
    )

    # Related entities
    orgao_sancionador: Organization | None = PydanticField(
        default=None, description="Sanctioning organization"
    )

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, v):
        """Validate CNPJ format."""
        if v:
            v = v.replace(".", "").replace("/", "").replace("-", "").replace(" ", "")
            if v and (not v.isdigit() or len(v) != 14):
                return None
        return v

    @field_validator("data_inicio_sancao", "data_fim_sancao", "data_publicacao")
    @classmethod
    def parse_date(cls, v):
        """Parse date from various formats."""
        if isinstance(v, str):
            for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            return None
        return v


# Helper functions for parsing API responses


def parse_contract(data: dict[str, Any]) -> Contract:
    """Parse contract data from API response."""
    return Contract(**data)


def parse_expense(data: dict[str, Any]) -> Expense:
    """Parse expense data from API response."""
    return Expense(**data)


def parse_agreement(data: dict[str, Any]) -> Agreement:
    """Parse agreement data from API response."""
    return Agreement(**data)


def parse_bidding(data: dict[str, Any]) -> Bidding:
    """Parse bidding data from API response."""
    return Bidding(**data)


def parse_servant(data: dict[str, Any]) -> Servant:
    """Parse servant data from API response."""
    return Servant(**data)


def parse_sanctioned_company(data: dict[str, Any]) -> SanctionedCompany:
    """Parse sanctioned company data from API response."""
    return SanctionedCompany(**data)


# Type mappings for easier parsing
MODEL_MAPPING = {
    "contracts": Contract,
    "contratos": Contract,
    "expenses": Expense,
    "despesas": Expense,
    "agreements": Agreement,
    "convenios": Agreement,
    "biddings": Bidding,
    "licitacoes": Bidding,
    "servants": Servant,
    "servidores": Servant,
    "ceaf": SanctionedCompany,
    "ceis": SanctionedCompany,
    "cnep": SanctionedCompany,
    "cepim": SanctionedCompany,
}


def parse_api_data(data: list[dict[str, Any]], data_type: str) -> list[BaseModel]:
    """
    Parse API data into appropriate models.

    Args:
        data: Raw API data
        data_type: Type of data (contracts, expenses, etc.)

    Returns:
        List of parsed models
    """
    model_class = MODEL_MAPPING.get(data_type.lower())
    if not model_class:
        raise ValueError(f"Unknown data type: {data_type}")

    parsed_data = []
    for item in data:
        try:
            parsed_item = model_class(**item)
            parsed_data.append(parsed_item)
        except Exception:
            # Log error but continue processing
            continue

    return parsed_data
