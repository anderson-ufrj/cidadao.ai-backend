"""
Module: tools.transparency_models
Description: Data models for Portal da Transparência API responses
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional, Union

from pydantic import BaseModel
from pydantic import Field as PydanticField
from pydantic import field_field_field_validator


class Organization(BaseModel):
    """Government organization model."""

    codigo: Optional[str] = PydanticField(default=None, description="Organization code")
    nome: Optional[str] = PydanticField(default=None, description="Organization name")
    sigla: Optional[str] = PydanticField(
        default=None, description="Organization acronym"
    )
    descricao: Optional[str] = PydanticField(
        default=None, description="Organization description"
    )


class Supplier(BaseModel):
    """Supplier/contractor model."""

    cnpj: Optional[str] = PydanticField(default=None, description="CNPJ")
    cpf: Optional[str] = PydanticField(default=None, description="CPF")
    nome: Optional[str] = PydanticField(default=None, description="Name")
    razao_social: Optional[str] = PydanticField(
        default=None, description="Corporate name"
    )
    municipio: Optional[str] = PydanticField(default=None, description="Municipality")
    uf: Optional[str] = PydanticField(default=None, description="State")

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

    id: Optional[str] = PydanticField(default=None, description="Contract ID")
    numero: Optional[str] = PydanticField(default=None, description="Contract number")
    ano: Optional[int] = PydanticField(default=None, description="Year")
    mes: Optional[int] = PydanticField(default=None, description="Month")

    # Dates
    data_assinatura: Optional[Union[str, date]] = PydanticField(
        default=None, description="Signature date"
    )
    data_inicio_vigencia: Optional[Union[str, date]] = PydanticField(
        default=None, description="Start date"
    )
    data_fim_vigencia: Optional[Union[str, date]] = PydanticField(
        default=None, description="End date"
    )
    data_publicacao: Optional[Union[str, date]] = PydanticField(
        default=None, description="Publication date"
    )

    # Financial
    valor_inicial: Optional[Decimal] = PydanticField(
        default=None, description="Initial value"
    )
    valor_global: Optional[Decimal] = PydanticField(
        default=None, description="Global value"
    )
    valor_acumulado: Optional[Decimal] = PydanticField(
        default=None, description="Accumulated value"
    )

    # Description
    objeto: Optional[str] = PydanticField(default=None, description="Contract object")
    objeto_resumido: Optional[str] = PydanticField(
        default=None, description="Contract summary"
    )

    # Classification
    modalidade_contratacao: Optional[Union[int, str]] = PydanticField(
        default=None, description="Contracting modality"
    )
    modalidade_licitacao: Optional[Union[int, str]] = PydanticField(
        default=None, description="Bidding modality"
    )
    situacao: Optional[str] = PydanticField(default=None, description="Status")

    # Related entities
    orgao: Optional[Organization] = PydanticField(
        default=None, description="Organization"
    )
    fornecedor: Optional[Supplier] = PydanticField(default=None, description="Supplier")

    # Additional fields
    fundamento_legal: Optional[str] = PydanticField(
        default=None, description="Legal basis"
    )
    origem_recurso: Optional[str] = PydanticField(
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
        elif isinstance(v, str):
            # Remove common formatting
            v = v.replace(",", ".").replace(" ", "")
            try:
                return Decimal(v)
            except:
                return None
        return v


class Expense(BaseModel):
    """Government expense model."""

    id: Optional[str] = PydanticField(default=None, description="Expense ID")
    ano: Optional[int] = PydanticField(default=None, description="Year")
    mes: Optional[int] = PydanticField(default=None, description="Month")

    # Dates
    data_pagamento: Optional[Union[str, date]] = PydanticField(
        default=None, description="Payment date"
    )
    data_documento: Optional[Union[str, date]] = PydanticField(
        default=None, description="Document date"
    )

    # Financial
    valor: Optional[Decimal] = PydanticField(default=None, description="Amount")
    valor_empenhado: Optional[Decimal] = PydanticField(
        default=None, description="Committed amount"
    )
    valor_liquidado: Optional[Decimal] = PydanticField(
        default=None, description="Liquidated amount"
    )
    valor_pago: Optional[Decimal] = PydanticField(
        default=None, description="Paid amount"
    )

    # Classification
    funcao: Optional[str] = PydanticField(default=None, description="Function")
    subfuncao: Optional[str] = PydanticField(default=None, description="Subfunction")
    programa: Optional[str] = PydanticField(default=None, description="Program")
    acao: Optional[str] = PydanticField(default=None, description="Action")
    elemento_despesa: Optional[str] = PydanticField(
        default=None, description="Expense element"
    )

    # Description
    descricao: Optional[str] = PydanticField(default=None, description="Description")
    documento: Optional[str] = PydanticField(default=None, description="Document")

    # Related entities
    orgao: Optional[Organization] = PydanticField(
        default=None, description="Organization"
    )
    favorecido: Optional[Supplier] = PydanticField(
        default=None, description="Beneficiary"
    )

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
        elif isinstance(v, str):
            v = v.replace(",", ".").replace(" ", "")
            try:
                return Decimal(v)
            except:
                return None
        return v


class Agreement(BaseModel):
    """Government agreement (convênio) model."""

    id: Optional[str] = PydanticField(default=None, description="Agreement ID")
    numero: Optional[str] = PydanticField(default=None, description="Agreement number")
    ano: Optional[int] = PydanticField(default=None, description="Year")

    # Dates
    data_assinatura: Optional[Union[str, date]] = PydanticField(
        default=None, description="Signature date"
    )
    data_inicio_vigencia: Optional[Union[str, date]] = PydanticField(
        default=None, description="Start date"
    )
    data_fim_vigencia: Optional[Union[str, date]] = PydanticField(
        default=None, description="End date"
    )
    data_publicacao: Optional[Union[str, date]] = PydanticField(
        default=None, description="Publication date"
    )

    # Financial
    valor_global: Optional[Decimal] = PydanticField(
        default=None, description="Global value"
    )
    valor_repasse: Optional[Decimal] = PydanticField(
        default=None, description="Transfer value"
    )
    valor_contrapartida: Optional[Decimal] = PydanticField(
        default=None, description="Counterpart value"
    )

    # Description
    objeto: Optional[str] = PydanticField(default=None, description="Agreement object")
    situacao: Optional[str] = PydanticField(default=None, description="Status")

    # Related entities
    orgao_superior: Optional[Organization] = PydanticField(
        default=None, description="Superior organization"
    )
    orgao_vinculado: Optional[Organization] = PydanticField(
        default=None, description="Linked organization"
    )
    convenente: Optional[Supplier] = PydanticField(
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
        elif isinstance(v, str):
            v = v.replace(",", ".").replace(" ", "")
            try:
                return Decimal(v)
            except:
                return None
        return v


class Bidding(BaseModel):
    """Government bidding (licitação) model."""

    id: Optional[str] = PydanticField(default=None, description="Bidding ID")
    numero: Optional[str] = PydanticField(default=None, description="Bidding number")
    ano: Optional[int] = PydanticField(default=None, description="Year")

    # Dates
    data_abertura: Optional[Union[str, date]] = PydanticField(
        default=None, description="Opening date"
    )
    data_homologacao: Optional[Union[str, date]] = PydanticField(
        default=None, description="Approval date"
    )
    data_publicacao: Optional[Union[str, date]] = PydanticField(
        default=None, description="Publication date"
    )

    # Financial
    valor_estimado: Optional[Decimal] = PydanticField(
        default=None, description="Estimated value"
    )
    valor_homologado: Optional[Decimal] = PydanticField(
        default=None, description="Approved value"
    )

    # Classification
    modalidade: Optional[str] = PydanticField(default=None, description="Modality")
    situacao: Optional[str] = PydanticField(default=None, description="Status")
    tipo: Optional[str] = PydanticField(default=None, description="Type")

    # Description
    objeto: Optional[str] = PydanticField(default=None, description="Bidding object")
    edital: Optional[str] = PydanticField(default=None, description="Notice")

    # Related entities
    orgao: Optional[Organization] = PydanticField(
        default=None, description="Organization"
    )
    vencedor: Optional[Supplier] = PydanticField(default=None, description="Winner")

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
        elif isinstance(v, str):
            v = v.replace(",", ".").replace(" ", "")
            try:
                return Decimal(v)
            except:
                return None
        return v


class Servant(BaseModel):
    """Government servant model."""

    id: Optional[str] = PydanticField(default=None, description="Servant ID")
    cpf: Optional[str] = PydanticField(default=None, description="CPF")
    nome: Optional[str] = PydanticField(default=None, description="Name")

    # Employment
    cargo: Optional[str] = PydanticField(default=None, description="Position")
    funcao: Optional[str] = PydanticField(default=None, description="Function")
    situacao: Optional[str] = PydanticField(default=None, description="Status")
    regime_juridico: Optional[str] = PydanticField(
        default=None, description="Legal regime"
    )

    # Financial
    remuneracao_basica: Optional[Decimal] = PydanticField(
        default=None, description="Basic salary"
    )
    remuneracao_total: Optional[Decimal] = PydanticField(
        default=None, description="Total salary"
    )

    # Dates
    data_ingresso: Optional[Union[str, date]] = PydanticField(
        default=None, description="Entry date"
    )
    data_diploma_ingresso: Optional[Union[str, date]] = PydanticField(
        default=None, description="Diploma date"
    )

    # Related entities
    orgao: Optional[Organization] = PydanticField(
        default=None, description="Organization"
    )

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
        elif isinstance(v, str):
            v = v.replace(",", ".").replace(" ", "")
            try:
                return Decimal(v)
            except:
                return None
        return v


class SanctionedCompany(BaseModel):
    """Sanctioned company model (CEAF, CEIS, CNEP)."""

    cnpj: Optional[str] = PydanticField(default=None, description="CNPJ")
    nome: Optional[str] = PydanticField(default=None, description="Company name")
    razao_social: Optional[str] = PydanticField(
        default=None, description="Corporate name"
    )

    # Location
    municipio: Optional[str] = PydanticField(default=None, description="Municipality")
    uf: Optional[str] = PydanticField(default=None, description="State")

    # Sanction details
    tipo_sancao: Optional[str] = PydanticField(
        default=None, description="Sanction type"
    )
    data_inicio_sancao: Optional[Union[str, date]] = PydanticField(
        default=None, description="Sanction start date"
    )
    data_fim_sancao: Optional[Union[str, date]] = PydanticField(
        default=None, description="Sanction end date"
    )
    data_publicacao: Optional[Union[str, date]] = PydanticField(
        default=None, description="Publication date"
    )

    # Legal details
    fundamentacao_legal: Optional[str] = PydanticField(
        default=None, description="Legal basis"
    )
    descricao_fundamentacao: Optional[str] = PydanticField(
        default=None, description="Basis description"
    )

    # Related entities
    orgao_sancionador: Optional[Organization] = PydanticField(
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
