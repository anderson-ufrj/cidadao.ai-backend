"""
Organization name to code mapping for Brazilian government entities
Enables natural language queries like "Ministério da Saúde" -> code "26000"
"""

import re

from unidecode import unidecode

# Complete mapping of Brazilian federal government organizations
# Source: Portal da Transparência Federal API
FEDERAL_ORGANIZATIONS = {
    # Ministérios e Órgãos Superiores
    "20000": {
        "official_name": "Presidência da República",
        "aliases": [
            "presidência",
            "presidencia",
            "presidência da república",
            "presidencia da republica",
            "pr",
        ],
    },
    "22000": {
        "official_name": "Ministério da Agricultura e Pecuária",
        "aliases": [
            "agricultura",
            "mapa",
            "ministério da agricultura",
            "ministerio da agricultura",
        ],
    },
    "24000": {
        "official_name": "Ministério da Ciência, Tecnologia e Inovação",
        "aliases": [
            "ciência e tecnologia",
            "ciencia e tecnologia",
            "mcti",
            "ministério da ciência",
        ],
    },
    "25000": {
        "official_name": "Ministério da Educação",
        "aliases": [
            "educação",
            "educacao",
            "mec",
            "ministério da educação",
            "ministerio da educacao",
        ],
    },
    "26000": {
        "official_name": "Ministério da Saúde",
        "aliases": [
            "saúde",
            "saude",
            "ms",
            "ministério da saúde",
            "ministerio da saude",
            "sus",
        ],
    },
    "28000": {
        "official_name": "Ministério do Desenvolvimento e Assistência Social",
        "aliases": [
            "desenvolvimento social",
            "assistência social",
            "assistencia social",
            "mds",
        ],
    },
    "30000": {
        "official_name": "Ministério da Justiça e Segurança Pública",
        "aliases": [
            "justiça",
            "justica",
            "mj",
            "ministério da justiça",
            "ministerio da justica",
            "segurança pública",
        ],
    },
    "32000": {
        "official_name": "Ministério de Minas e Energia",
        "aliases": [
            "minas e energia",
            "mme",
            "ministério de minas",
            "ministerio de minas",
        ],
    },
    "35000": {
        "official_name": "Ministério das Relações Exteriores",
        "aliases": ["relações exteriores", "relacoes exteriores", "itamaraty", "mre"],
    },
    "36000": {
        "official_name": "Ministério da Defesa",
        "aliases": [
            "defesa",
            "md",
            "ministério da defesa",
            "ministerio da defesa",
            "forças armadas",
        ],
    },
    "39000": {
        "official_name": "Ministério da Fazenda",
        "aliases": ["fazenda", "mf", "ministério da fazenda", "ministerio da fazenda"],
    },
    "41000": {
        "official_name": "Ministério do Trabalho e Emprego",
        "aliases": [
            "trabalho",
            "emprego",
            "mte",
            "ministério do trabalho",
            "ministerio do trabalho",
        ],
    },
    "42000": {
        "official_name": "Ministério da Cultura",
        "aliases": [
            "cultura",
            "minc",
            "ministério da cultura",
            "ministerio da cultura",
        ],
    },
    "44000": {
        "official_name": "Ministério do Meio Ambiente",
        "aliases": [
            "meio ambiente",
            "mma",
            "ministério do meio ambiente",
            "ministerio do meio ambiente",
        ],
    },
    "49000": {
        "official_name": "Ministério do Desenvolvimento Agrário",
        "aliases": ["desenvolvimento agrário", "desenvolvimento agrario", "mda"],
    },
    "52000": {
        "official_name": "Ministério do Esporte",
        "aliases": ["esporte", "me", "ministério do esporte", "ministerio do esporte"],
    },
    "53000": {
        "official_name": "Ministério da Integração Nacional",
        "aliases": ["integração nacional", "integracao nacional", "mi"],
    },
    "54000": {
        "official_name": "Ministério do Turismo",
        "aliases": [
            "turismo",
            "mtur",
            "ministério do turismo",
            "ministerio do turismo",
        ],
    },
    "55000": {
        "official_name": "Ministério do Desenvolvimento Regional",
        "aliases": ["desenvolvimento regional", "mdr"],
    },
    "56000": {
        "official_name": "Ministério das Cidades",
        "aliases": [
            "cidades",
            "mcidades",
            "ministério das cidades",
            "ministerio das cidades",
        ],
    },
    "57000": {
        "official_name": "Ministério dos Transportes",
        "aliases": [
            "transportes",
            "mt",
            "ministério dos transportes",
            "ministerio dos transportes",
        ],
    },
    "58000": {
        "official_name": "Ministério das Comunicações",
        "aliases": [
            "comunicações",
            "comunicacoes",
            "mcom",
            "ministério das comunicações",
        ],
    },
    "60000": {
        "official_name": "Controladoria-Geral da União",
        "aliases": [
            "cgu",
            "controladoria",
            "controladoria-geral",
            "controladoria geral",
        ],
    },
    "62000": {
        "official_name": "Advocacia-Geral da União",
        "aliases": ["agu", "advocacia-geral", "advocacia geral"],
    },
}


class OrganizationMapper:
    """Maps organization names to official codes for API queries"""

    def __init__(self):
        self.orgs = FEDERAL_ORGANIZATIONS
        # Build reverse index for fast lookup
        self._build_reverse_index()

    def _build_reverse_index(self):
        """Build reverse index from aliases to codes"""
        self.alias_to_code = {}

        for code, org_data in self.orgs.items():
            # Add official name
            normalized = self._normalize(org_data["official_name"])
            self.alias_to_code[normalized] = code

            # Add all aliases
            for alias in org_data["aliases"]:
                normalized = self._normalize(alias)
                self.alias_to_code[normalized] = code

    def _normalize(self, text: str) -> str:
        """Normalize text for comparison (lowercase, no accents, no special chars)"""
        if not text:
            return ""
        # Remove accents
        text = unidecode(text)
        # Lowercase
        text = text.lower()
        # Remove special characters except spaces
        text = re.sub(r"[^a-z0-9\s]", "", text)
        # Normalize whitespace
        text = " ".join(text.split())
        return text

    def find_organization_code(self, query: str) -> str | None:
        """
        Find organization code from natural language query.

        Args:
            query: Natural language query (e.g., "Ministério da Saúde")

        Returns:
            Organization code (e.g., "26000") or None if not found

        Examples:
            >>> mapper = OrganizationMapper()
            >>> mapper.find_organization_code("Ministério da Saúde")
            "26000"
            >>> mapper.find_organization_code("saude")
            "26000"
            >>> mapper.find_organization_code("MEC")
            "25000"
        """
        if not query:
            return None

        normalized = self._normalize(query)

        # Direct match
        if normalized in self.alias_to_code:
            return self.alias_to_code[normalized]

        # Partial match - find if query contains any alias
        for alias, code in self.alias_to_code.items():
            if alias in normalized or normalized in alias:
                return code

        return None

    def extract_organizations_from_text(self, text: str) -> list[dict]:
        """
        Extract all organization mentions from text.

        Args:
            text: Text to search for organization mentions

        Returns:
            List of dicts with 'code', 'name', 'matched_text'

        Example:
            >>> mapper = OrganizationMapper()
            >>> mapper.extract_organizations_from_text(
            ...     "Contratos do Ministério da Saúde e da Educação"
            ... )
            [
                {"code": "26000", "name": "Ministério da Saúde", "matched_text": "saúde"},
                {"code": "25000", "name": "Ministério da Educação", "matched_text": "educação"}
            ]
        """
        if not text:
            return []

        found = []
        normalized_text = self._normalize(text)

        # Search for each alias in the text
        for alias, code in self.alias_to_code.items():
            if alias in normalized_text:
                # Avoid duplicates
                if not any(org["code"] == code for org in found):
                    found.append(
                        {
                            "code": code,
                            "name": self.orgs[code]["official_name"],
                            "matched_text": alias,
                        }
                    )

        return found

    def get_organization_info(self, code: str) -> dict | None:
        """Get full organization information by code"""
        return self.orgs.get(code)

    def list_all_organizations(self) -> list[dict]:
        """List all available organizations"""
        return [
            {
                "code": code,
                "name": data["official_name"],
                "aliases": data["aliases"],
            }
            for code, data in self.orgs.items()
        ]


# Global singleton instance
_mapper_instance = None


def get_organization_mapper() -> OrganizationMapper:
    """Get global organization mapper instance"""
    global _mapper_instance
    if _mapper_instance is None:
        _mapper_instance = OrganizationMapper()
    return _mapper_instance
