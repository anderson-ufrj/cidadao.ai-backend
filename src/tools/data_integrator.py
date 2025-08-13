"""
Module: tools.data_integrator
Description: Integration layer for government data with AI analysis
Author: Anderson H. Silva
Date: 2025-01-15
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import logging

from .transparency_api import TransparencyAPIClient, TransparencyAPIFilter
from ..core.config import settings
from ..core.exceptions import TransparencyAPIError, DataNotFoundError

logger = logging.getLogger(__name__)


class DataIntegrator:
    """Integrates government data with AI analysis capabilities."""
    
    def __init__(self):
        self.client = TransparencyAPIClient()
        self.cache = {}
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()
    
    def _format_currency(self, value: Union[str, float, int]) -> str:
        """Format currency values for display."""
        try:
            if isinstance(value, str):
                # Try to extract numeric value
                import re
                numeric = re.sub(r'[^\d,.-]', '', value)
                numeric = numeric.replace(',', '.')
                value = float(numeric)
            
            return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            return str(value)
    
    def _format_date(self, date_str: str) -> str:
        """Format date for display."""
        try:
            # Try different date formats
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%dT%H:%M:%S']
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%d/%m/%Y')
                except:
                    continue
            return date_str
        except:
            return date_str
    
    def _extract_key_info(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """Extract key information from government data."""
        if data_type == "contracts":
            return {
                "id": data.get("id", "N/A"),
                "number": data.get("numero", data.get("numeroContrato", "N/A")),
                "object": data.get("objeto", data.get("objetoContrato", "N/A")),
                "value": self._format_currency(data.get("valorInicial", data.get("valor", 0))),
                "contractor": data.get("nomeRazaoSocialFornecedor", data.get("fornecedor", "N/A")),
                "cnpj": data.get("cnpjContratado", data.get("cnpj", "N/A")),
                "start_date": self._format_date(data.get("dataInicioVigencia", data.get("dataAssinatura", "N/A"))),
                "organ": data.get("nomeOrgao", data.get("orgao", "N/A")),
                "modality": data.get("modalidadeContrato", data.get("modalidade", "N/A"))
            }
        
        elif data_type == "expenses":
            return {
                "id": data.get("id", "N/A"),
                "document": data.get("numeroDocumento", data.get("documento", "N/A")),
                "value": self._format_currency(data.get("valorDocumento", data.get("valor", 0))),
                "date": self._format_date(data.get("dataDocumento", data.get("data", "N/A"))),
                "beneficiary": data.get("nomeFavorecido", data.get("favorecido", "N/A")),
                "cnpj": data.get("codigoFavorecido", data.get("cnpj", "N/A")),
                "organ": data.get("nomeOrgao", data.get("orgao", "N/A")),
                "function": data.get("nomeFuncao", data.get("funcao", "N/A")),
                "action": data.get("nomeAcao", data.get("acao", "N/A"))
            }
        
        elif data_type == "biddings":
            return {
                "id": data.get("id", "N/A"),
                "number": data.get("numero", data.get("numeroLicitacao", "N/A")),
                "object": data.get("objeto", data.get("objetoLicitacao", "N/A")),
                "value": self._format_currency(data.get("valorEstimado", data.get("valor", 0))),
                "modality": data.get("modalidade", data.get("modalidadeLicitacao", "N/A")),
                "situation": data.get("situacao", data.get("situacaoLicitacao", "N/A")),
                "organ": data.get("nomeOrgao", data.get("orgao", "N/A")),
                "opening_date": self._format_date(data.get("dataAbertura", data.get("data", "N/A"))),
                "uasg": data.get("uasg", "N/A")
            }
        
        return data
    
    async def search_contracts(
        self,
        cnpj: Optional[str] = None,
        year: Optional[int] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        organ_code: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search government contracts with filters."""
        try:
            filters = TransparencyAPIFilter(
                ano=year or datetime.now().year,
                cnpj_contratado=cnpj,
                valor_inicial=min_value,
                valor_final=max_value,
                codigo_orgao=organ_code,
                tamanho_pagina=min(limit, 100)
            )
            
            response = await self.client.get_contracts(filters)
            
            # Process and format data
            formatted_data = []
            for item in response.data:
                formatted_data.append(self._extract_key_info(item, "contracts"))
            
            return {
                "success": True,
                "data_type": "contracts",
                "total_records": response.total_records,
                "returned_records": len(formatted_data),
                "data": formatted_data,
                "filters_applied": filters.dict(exclude_none=True),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error searching contracts: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data_type": "contracts",
                "data": [],
                "timestamp": datetime.now().isoformat()
            }
    
    async def search_expenses(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        organ_code: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search government expenses with filters."""
        try:
            filters = TransparencyAPIFilter(
                ano=year or datetime.now().year,
                mes=month,
                valor_inicial=min_value,
                valor_final=max_value,
                codigo_orgao=organ_code,
                tamanho_pagina=min(limit, 100)
            )
            
            response = await self.client.get_expenses(filters)
            
            # Process and format data
            formatted_data = []
            for item in response.data:
                formatted_data.append(self._extract_key_info(item, "expenses"))
            
            return {
                "success": True,
                "data_type": "expenses",
                "total_records": response.total_records,
                "returned_records": len(formatted_data),
                "data": formatted_data,
                "filters_applied": filters.dict(exclude_none=True),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error searching expenses: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data_type": "expenses",
                "data": [],
                "timestamp": datetime.now().isoformat()
            }
    
    async def search_biddings(
        self,
        year: Optional[int] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        organ_code: Optional[str] = None,
        modality: Optional[int] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search government biddings with filters."""
        try:
            filters = TransparencyAPIFilter(
                ano=year or datetime.now().year,
                valor_inicial=min_value,
                valor_final=max_value,
                codigo_orgao=organ_code,
                modalidade=modality,
                tamanho_pagina=min(limit, 100)
            )
            
            response = await self.client.get_biddings(filters)
            
            # Process and format data
            formatted_data = []
            for item in response.data:
                formatted_data.append(self._extract_key_info(item, "biddings"))
            
            return {
                "success": True,
                "data_type": "biddings",
                "total_records": response.total_records,
                "returned_records": len(formatted_data),
                "data": formatted_data,
                "filters_applied": filters.dict(exclude_none=True),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error searching biddings: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data_type": "biddings",
                "data": [],
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_company_overview(self, cnpj: str) -> Dict[str, Any]:
        """Get comprehensive overview of a company's government interactions."""
        try:
            # Search contracts and expenses for this CNPJ
            contracts_task = self.search_contracts(cnpj=cnpj, limit=50)
            expenses_task = self.search_expenses(limit=50)  # Expenses don't filter by CNPJ directly
            
            contracts_data, expenses_data = await asyncio.gather(
                contracts_task, expenses_task, return_exceptions=True
            )
            
            # Calculate totals
            total_contracts = 0
            total_contract_value = 0
            
            if contracts_data.get("success") and contracts_data.get("data"):
                total_contracts = len(contracts_data["data"])
                for contract in contracts_data["data"]:
                    try:
                        value_str = contract.get("value", "R$ 0,00")
                        # Extract numeric value
                        import re
                        numeric = re.sub(r'[^\d,.-]', '', value_str)
                        numeric = numeric.replace(',', '.')
                        total_contract_value += float(numeric)
                    except:
                        pass
            
            return {
                "success": True,
                "cnpj": cnpj,
                "summary": {
                    "total_contracts": total_contracts,
                    "total_contract_value": self._format_currency(total_contract_value),
                    "has_recent_activity": total_contracts > 0
                },
                "contracts": contracts_data.get("data", [])[:10],  # Top 10 contracts
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting company overview: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "cnpj": cnpj,
                "timestamp": datetime.now().isoformat()
            }
    
    def format_data_for_display(self, data: Dict[str, Any]) -> str:
        """Format government data for display in chat interface."""
        if not data.get("success"):
            return f"❌ **Erro ao buscar dados**: {data.get('error', 'Erro desconhecido')}"
        
        data_type = data.get("data_type", "unknown")
        items = data.get("data", [])
        total = data.get("total_records", 0)
        returned = data.get("returned_records", 0)
        
        if not items:
            return f"🔍 **Nenhum resultado encontrado** para {data_type}"
        
        # Build formatted response
        response = f"📊 **Resultados de {data_type.title()}**\n\n"
        response += f"📈 **Total de registros**: {total:,}\n"
        response += f"📋 **Exibindo**: {returned} registros\n\n"
        
        # Format individual items
        for i, item in enumerate(items[:10], 1):  # Show max 10 items
            response += f"**{i}. "
            
            if data_type == "contracts":
                response += f"Contrato {item.get('number', 'N/A')}**\n"
                response += f"   🏢 **Contratado**: {item.get('contractor', 'N/A')}\n"
                response += f"   💰 **Valor**: {item.get('value', 'N/A')}\n"
                response += f"   📅 **Início**: {item.get('start_date', 'N/A')}\n"
                response += f"   🎯 **Objeto**: {item.get('object', 'N/A')[:100]}...\n"
                response += f"   🏛️ **Órgão**: {item.get('organ', 'N/A')}\n"
            
            elif data_type == "expenses":
                response += f"Despesa {item.get('document', 'N/A')}**\n"
                response += f"   👤 **Favorecido**: {item.get('beneficiary', 'N/A')}\n"
                response += f"   💰 **Valor**: {item.get('value', 'N/A')}\n"
                response += f"   📅 **Data**: {item.get('date', 'N/A')}\n"
                response += f"   🏛️ **Órgão**: {item.get('organ', 'N/A')}\n"
                response += f"   🎯 **Função**: {item.get('function', 'N/A')}\n"
            
            elif data_type == "biddings":
                response += f"Licitação {item.get('number', 'N/A')}**\n"
                response += f"   📝 **Modalidade**: {item.get('modality', 'N/A')}\n"
                response += f"   💰 **Valor Estimado**: {item.get('value', 'N/A')}\n"
                response += f"   📅 **Abertura**: {item.get('opening_date', 'N/A')}\n"
                response += f"   🎯 **Objeto**: {item.get('object', 'N/A')[:100]}...\n"
                response += f"   🏛️ **Órgão**: {item.get('organ', 'N/A')}\n"
                response += f"   📊 **Situação**: {item.get('situation', 'N/A')}\n"
            
            response += "\n"
        
        if len(items) > 10:
            response += f"... e mais {len(items) - 10} registros\n\n"
        
        response += f"🕐 **Consultado em**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        
        return response


# Factory function
def create_data_integrator() -> DataIntegrator:
    """Create a data integrator instance."""
    return DataIntegrator()