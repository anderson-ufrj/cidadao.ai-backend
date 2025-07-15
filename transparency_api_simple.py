"""
Versão simplificada da API de Transparência para Hugging Face Spaces
Otimizada para funcionar sem dependências pesadas
"""

import os
import json
import time
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações da API
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
TRANSPARENCY_API_BASE_URL = "https://api.portaldatransparencia.gov.br"
TRANSPARENCY_API_HEADER = "chave-api-dados"

# Documentação da API: https://api.portaldatransparencia.gov.br/swagger-ui.html
# Endpoints testados:
# - /api-de-dados/contratos
# - /api-de-dados/despesas  
# - /api-de-dados/convenios
# - /api-de-dados/licitacoes

# Cache simples em memória
_cache = {}
_cache_timestamps = {}
CACHE_DURATION = 300  # 5 minutos

# Rate limiting simples
_last_request_time = 0
MIN_REQUEST_INTERVAL = 0.7  # ~90 requests per minute


class TransparencyAPIClient:
    """Cliente simplificado para a API do Portal da Transparência"""
    
    def __init__(self):
        self.api_key = TRANSPARENCY_API_KEY
        self.base_url = TRANSPARENCY_API_BASE_URL
        self.headers = {
            TRANSPARENCY_API_HEADER: self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "CidadaoAI/1.0.0"
        }
        
        if not self.api_key:
            logger.error("❌ TRANSPARENCY_API_KEY não configurada")
            raise ValueError("TRANSPARENCY_API_KEY não configurada")
        
        logger.info("✅ API client inicializado")
    
    def _wait_for_rate_limit(self):
        """Aguarda para respeitar rate limit"""
        global _last_request_time
        current_time = time.time()
        time_since_last = current_time - _last_request_time
        
        if time_since_last < MIN_REQUEST_INTERVAL:
            sleep_time = MIN_REQUEST_INTERVAL - time_since_last
            logger.info(f"⏱️ Aguardando {sleep_time:.2f}s para rate limit")
            time.sleep(sleep_time)
        
        _last_request_time = time.time()
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Gera chave de cache"""
        params_str = json.dumps(params, sort_keys=True)
        return f"{endpoint}:{hash(params_str)}"
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Recupera resposta do cache se válida"""
        if cache_key in _cache:
            timestamp = _cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < CACHE_DURATION:
                logger.info(f"📦 Cache hit: {cache_key}")
                return _cache[cache_key]
            else:
                # Cache expirado
                del _cache[cache_key]
                del _cache_timestamps[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: Dict):
        """Salva resposta no cache"""
        _cache[cache_key] = response
        _cache_timestamps[cache_key] = time.time()
        logger.info(f"💾 Cache saved: {cache_key}")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Faz requisição para a API"""
        if params is None:
            params = {}
        
        # Verificar cache
        cache_key = self._get_cache_key(endpoint, params)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Rate limit
        self._wait_for_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"🌐 Fazendo requisição: {endpoint}")
            logger.info(f"🔑 Usando chave: {self.api_key[:10]}...")
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            logger.info(f"📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Salvar no cache
                self._cache_response(cache_key, data)
                
                logger.info(f"✅ Sucesso: {len(data) if isinstance(data, list) else 1} registros")
                return data
            
            elif response.status_code == 429:
                logger.warning("⚠️ Rate limit excedido")
                time.sleep(60)  # Aguardar 1 minuto
                return self._make_request(endpoint, params)  # Retry
            
            elif response.status_code == 401:
                logger.error("🔐 Erro de autenticação - chave inválida")
                return {
                    "error": "Chave API inválida",
                    "message": "Verifique se a chave está correta e se você tem permissão para acessar a API",
                    "help": "Registre-se em: https://api.portaldatransparencia.gov.br/api-de-dados/swagger-ui.html"
                }
            
            else:
                logger.error(f"❌ Erro HTTP {response.status_code}: {response.text}")
                return {
                    "error": f"Erro HTTP {response.status_code}",
                    "message": response.text
                }
        
        except requests.exceptions.Timeout:
            logger.error("⏰ Timeout na requisição")
            return {"error": "Timeout na requisição"}
        
        except Exception as e:
            logger.error(f"💥 Erro na requisição: {str(e)}")
            return {"error": f"Erro na requisição: {str(e)}"}
    
    def get_contracts(self, **params) -> Dict:
        """Busca contratos"""
        return self._make_request("/api-de-dados/contratos", params)
    
    def get_expenses(self, **params) -> Dict:
        """Busca despesas"""
        return self._make_request("/api-de-dados/despesas", params)
    
    def get_agreements(self, **params) -> Dict:
        """Busca convênios"""
        return self._make_request("/api-de-dados/convenios", params)
    
    def get_biddings(self, **params) -> Dict:
        """Busca licitações"""
        return self._make_request("/api-de-dados/licitacoes", params)
    
    def search_by_cnpj(self, cnpj: str, data_type: str = "contracts") -> Dict:
        """Busca por CNPJ"""
        params = {"cnpjContratado": cnpj}
        
        if data_type == "contracts":
            return self.get_contracts(**params)
        elif data_type == "expenses":
            return self.get_expenses(**params)
        elif data_type == "agreements":
            return self.get_agreements(**params)
        else:
            return {"error": f"Tipo de dados não suportado: {data_type}"}
    
    def search_by_value(self, min_value: float, max_value: float = None, data_type: str = "contracts") -> Dict:
        """Busca por valor"""
        params = {"valorInicial": min_value}
        if max_value:
            params["valorFinal"] = max_value
        
        if data_type == "contracts":
            return self.get_contracts(**params)
        elif data_type == "expenses":
            return self.get_expenses(**params)
        elif data_type == "agreements":
            return self.get_agreements(**params)
        else:
            return {"error": f"Tipo de dados não suportado: {data_type}"}
    
    def search_by_year(self, year: int, data_type: str = "contracts") -> Dict:
        """Busca por ano"""
        params = {"ano": year}
        
        if data_type == "contracts":
            return self.get_contracts(**params)
        elif data_type == "expenses":
            return self.get_expenses(**params)
        elif data_type == "agreements":
            return self.get_agreements(**params)
        else:
            return {"error": f"Tipo de dados não suportado: {data_type}"}


def format_results_for_display(data: Dict, data_type: str = "contracts") -> str:
    """Formata resultados para exibição"""
    if "error" in data:
        return f"❌ **Erro**: {data['error']}"
    
    if not data or (isinstance(data, list) and len(data) == 0):
        return "⚠️ **Nenhum resultado encontrado**"
    
    results = data if isinstance(data, list) else [data]
    
    if len(results) == 0:
        return "⚠️ **Nenhum resultado encontrado**"
    
    # Formatação básica
    formatted = f"📊 **Encontrados {len(results)} registro(s)**\n\n"
    
    for i, item in enumerate(results[:10]):  # Limitar a 10 resultados
        formatted += f"**{i+1}. "
        
        if data_type == "contracts":
            formatted += f"Contrato**\n"
            if "objeto" in item:
                formatted += f"🎯 **Objeto**: {item['objeto'][:100]}...\n"
            if "valor" in item:
                formatted += f"💰 **Valor**: R$ {item['valor']:,.2f}\n"
            if "fornecedor" in item:
                formatted += f"🏢 **Fornecedor**: {item['fornecedor']}\n"
            if "dataAssinatura" in item:
                formatted += f"📅 **Data**: {item['dataAssinatura']}\n"
        
        elif data_type == "expenses":
            formatted += f"Despesa**\n"
            if "descricao" in item:
                formatted += f"📝 **Descrição**: {item['descricao'][:100]}...\n"
            if "valor" in item:
                formatted += f"💰 **Valor**: R$ {item['valor']:,.2f}\n"
            if "orgao" in item:
                formatted += f"🏛️ **Órgão**: {item['orgao']}\n"
            if "data" in item:
                formatted += f"📅 **Data**: {item['data']}\n"
        
        formatted += "\n"
    
    if len(results) > 10:
        formatted += f"... e mais {len(results) - 10} registros\n"
    
    return formatted


def quick_search(query: str) -> str:
    """Busca rápida interpretando query em linguagem natural"""
    if not TRANSPARENCY_API_KEY:
        return "❌ **API não configurada**\n\nConfigure a variável TRANSPARENCY_API_KEY."
    
    try:
        client = TransparencyAPIClient()
        
        # Análise simples da query
        query_lower = query.lower()
        
        # Buscar por CNPJ
        if "cnpj" in query_lower:
            import re
            cnpj_match = re.search(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{14})', query)
            if cnpj_match:
                cnpj = cnpj_match.group(1)
                logger.info(f"🔍 Buscando por CNPJ: {cnpj}")
                results = client.search_by_cnpj(cnpj)
                return format_results_for_display(results, "contracts")
        
        # Buscar por valor
        if "valor" in query_lower or "r$" in query_lower:
            import re
            value_match = re.search(r'(\d+(?:\.\d+)*(?:,\d+)?)', query)
            if value_match:
                value_str = value_match.group(1).replace('.', '').replace(',', '.')
                try:
                    value = float(value_str)
                    logger.info(f"🔍 Buscando por valor: R$ {value:,.2f}")
                    results = client.search_by_value(value)
                    return format_results_for_display(results, "contracts")
                except:
                    pass
        
        # Buscar por ano
        if "ano" in query_lower or "202" in query:
            import re
            year_match = re.search(r'(202\d)', query)
            if year_match:
                year = int(year_match.group(1))
                logger.info(f"🔍 Buscando por ano: {year}")
                results = client.search_by_year(year)
                return format_results_for_display(results, "contracts")
        
        # Busca padrão - contratos recentes
        logger.info("🔍 Buscando contratos recentes")
        results = client.get_contracts(tamanhoPagina=20)
        return format_results_for_display(results, "contracts")
    
    except Exception as e:
        logger.error(f"💥 Erro na busca: {str(e)}")
        return f"❌ **Erro na busca**: {str(e)}"


# Teste básico da API
if __name__ == "__main__":
    print("🧪 Testando API de Transparência...")
    
    if not TRANSPARENCY_API_KEY:
        print("❌ TRANSPARENCY_API_KEY não configurada")
        exit(1)
    
    try:
        client = TransparencyAPIClient()
        
        # Teste básico
        print("\n📊 Testando busca de contratos...")
        results = client.get_contracts(tamanhoPagina=5)
        
        if "error" in results:
            print(f"❌ Erro: {results['error']}")
        else:
            print(f"✅ Sucesso: {len(results)} contratos encontrados")
            
            # Mostrar primeiro resultado
            if results and len(results) > 0:
                first = results[0]
                print("\n🔍 Primeiro resultado:")
                for key, value in first.items():
                    print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"💥 Erro no teste: {str(e)}")