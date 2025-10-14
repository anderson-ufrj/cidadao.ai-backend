"""
Entity Extractor

Extracts entities from user queries (CNPJ, CPF, dates, locations, etc.).

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

import re
from datetime import datetime
from typing import Any

from src.core import get_logger

logger = get_logger(__name__)


class EntityExtractor:
    """
    Extracts structured entities from user queries.

    Identifies: CNPJ, CPF, dates, year, state, city, company names, agency names.
    """

    # Brazilian entity patterns
    CNPJ_PATTERN = r"\b\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}\b"
    CPF_PATTERN = r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"
    YEAR_PATTERN = r"\b(19|20)\d{2}\b"
    DATE_PATTERN = r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"

    # Brazilian states
    BRAZILIAN_STATES = [
        "AC",
        "AL",
        "AP",
        "AM",
        "BA",
        "CE",
        "DF",
        "ES",
        "GO",
        "MA",
        "MT",
        "MS",
        "MG",
        "PA",
        "PB",
        "PR",
        "PE",
        "PI",
        "RJ",
        "RN",
        "RS",
        "RO",
        "RR",
        "SC",
        "SP",
        "SE",
        "TO",
    ]

    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def extract(self, query: str) -> dict[str, Any]:
        """
        Extract all entities from query.

        Args:
            query: User query in Portuguese

        Returns:
            Dict with extracted entities
        """
        entities: dict[str, Any] = {}

        # Extract CNPJ
        cnpj = self._extract_cnpj(query)
        if cnpj:
            entities["cnpj"] = cnpj

        # Extract CPF
        cpf = self._extract_cpf(query)
        if cpf:
            entities["cpf"] = cpf

        # Extract dates
        dates = self._extract_dates(query)
        if dates:
            entities.update(dates)

        # Extract year
        year = self._extract_year(query)
        if year:
            entities["year"] = year

        # Extract state
        state = self._extract_state(query)
        if state:
            entities["state"] = state

        # Extract company/agency names (heuristic-based)
        names = self._extract_names(query)
        if names.get("company_name"):
            entities["company_name"] = names["company_name"]
        if names.get("agency_name"):
            entities["agency_name"] = names["agency_name"]

        self.logger.debug(f"Extracted entities: {entities}")
        return entities

    def _extract_cnpj(self, query: str) -> str | None:
        """Extract and normalize CNPJ."""
        match = re.search(self.CNPJ_PATTERN, query)
        if match:
            # Normalize: remove formatting
            cnpj = re.sub(r"[^\d]", "", match.group())
            if len(cnpj) == 14:  # noqa: PLR2004
                return cnpj
        return None

    def _extract_cpf(self, query: str) -> str | None:
        """Extract and normalize CPF."""
        match = re.search(self.CPF_PATTERN, query)
        if match:
            # Normalize: remove formatting
            cpf = re.sub(r"[^\d]", "", match.group())
            if len(cpf) == 11:  # noqa: PLR2004
                return cpf
        return None

    def _extract_dates(self, query: str) -> dict[str, str]:
        """Extract start and end dates."""
        dates = {}
        matches = re.findall(self.DATE_PATTERN, query)

        if matches:
            # Try to parse dates
            parsed_dates = []
            for match in matches:
                try:
                    # Try different formats
                    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"]:
                        try:
                            date = datetime.strptime(match, fmt)
                            parsed_dates.append(date.strftime("%Y-%m-%d"))
                            break
                        except ValueError:
                            continue
                except Exception:  # noqa: S112
                    continue

            if parsed_dates:
                dates["start_date"] = min(parsed_dates)
                if len(parsed_dates) > 1:
                    dates["end_date"] = max(parsed_dates)

        return dates

    def _extract_year(self, query: str) -> int | None:
        """Extract year."""
        match = re.search(self.YEAR_PATTERN, query)
        if match:
            year = int(match.group())
            current_year = datetime.now().year
            # Validate reasonable year range
            if 1990 <= year <= current_year:  # noqa: PLR2004
                return year
        return None

    def _extract_state(self, query: str) -> str | None:
        """Extract Brazilian state code."""
        query_upper = query.upper()

        for state in self.BRAZILIAN_STATES:
            # Look for state code as whole word
            if re.search(rf"\b{state}\b", query_upper):
                return state

        return None

    def _extract_names(self, query: str) -> dict[str, str]:
        """
        Extract company and agency names using heuristics.

        This is a simplified version. In production, you might want to use NER.
        """
        names = {}

        # Common indicators for company names
        company_indicators = [
            "empresa",
            "fornecedor",
            "fornecedora",
            "companhia",
            "ltda",
            "s/a",
            "s.a.",
            "eireli",
            "mei",
        ]

        # Common indicators for agency names
        agency_indicators = [
            "prefeitura",
            "câmara",
            "assembleia",
            "governo",
            "ministério",
            "secretaria",
            "autarquia",
            "fundação",
        ]

        query_lower = query.lower()

        # Extract company name (very basic heuristic)
        for indicator in company_indicators:
            if indicator in query_lower:
                # Try to extract capitalized words near indicator
                pattern = rf"{indicator}\s+([A-Z][a-zA-Z\s]+(?:Ltda|S/A|EIRELI)?)"
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    names["company_name"] = match.group(1).strip()
                    break

        # Extract agency name
        for indicator in agency_indicators:
            if indicator in query_lower:
                pattern = rf"({indicator}\s+[A-Za-z\s]+)"
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    names["agency_name"] = match.group(1).strip()
                    break

        return names
