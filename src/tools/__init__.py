"""
Module: tools
Description: External API integration tools
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from .transparency_api import (
    TransparencyAPIClient,
    TransparencyAPIFilter,
    TransparencyAPIResponse,
    create_transparency_client,
)
from .transparency_models import (
    Agreement,
    Bidding,
    Contract,
    Expense,
    Organization,
    SanctionedCompany,
    Servant,
    Supplier,
    parse_agreement,
    parse_api_data,
    parse_bidding,
    parse_contract,
    parse_expense,
    parse_sanctioned_company,
    parse_servant,
)

__all__ = [
    # API Client
    "TransparencyAPIClient",
    "TransparencyAPIFilter",
    "TransparencyAPIResponse",
    "create_transparency_client",
    # Data Models
    "Contract",
    "Expense",
    "Agreement",
    "Bidding",
    "Servant",
    "SanctionedCompany",
    "Organization",
    "Supplier",
    # Parsing Functions
    "parse_api_data",
    "parse_contract",
    "parse_expense",
    "parse_agreement",
    "parse_bidding",
    "parse_servant",
    "parse_sanctioned_company",
]
