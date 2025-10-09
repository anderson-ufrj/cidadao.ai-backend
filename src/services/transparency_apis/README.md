# Transparency APIs Integration

**Author:** Anderson Henrique da Silva
**Created:** 2025-10-09 (Minas Gerais, Brazil)
**Version:** 1.0.0

Módulo de integração unificada com APIs de transparência pública brasileira.

## 📊 Cobertura Atual

### APIs Implementadas
- **1 Estado:** Rondônia (API REST direta)
- **6 TCEs:** Pernambuco, Ceará, Rio de Janeiro, São Paulo, Minas Gerais, Bahia
- **5 CKAN:** São Paulo, Rio de Janeiro, Rio Grande do Sul, Santa Catarina, Bahia

### Estatísticas
- **12 APIs** ativas
- **2.500+ municípios** com dados fiscais (TCEs)
- **8 estados** com cobertura total (TCEs + CKAN + diretos)

## 🚀 Uso Rápido

```python
from src.services.transparency_apis import registry

# Listar todas as APIs disponíveis
apis = registry.list_available_apis()
print(apis)  # ['RO-state', 'PE-tce', 'CE-tce', 'SP-ckan', ...]

# Obter cliente específico
pe_tce = registry.get_client('PE-tce')
contracts = await pe_tce.get_contracts(year=2024)

# Obter todas as APIs de um estado
sp_apis = registry.get_state_apis('SP')  # Retorna [CKANClient]
```

## 📚 APIs Disponíveis

### 1. Rondônia (Estado)
**Chave:** `RO-state`
**Base:** `http://portaldatransparencia.ro.gov.br/DadosAbertos`
**Métodos:**
- `get_contracts(start_date, end_date)` - Contratos
- `get_expenses(start_date, end_date)` - Despesas
- `get_purchases(limit, offset)` - Compras e materiais

**Características:**
- ✅ Sem autenticação
- ✅ REST API direta
- Rate limit: 60 req/min

### 2. TCE Pernambuco
**Chave:** `PE-tce`
**Base:** `https://sistemas.tce.pe.gov.br/DadosAbertos`
**Métodos:**
- `get_contracts(year, municipality_code)` - Contratos
- `get_suppliers(municipality_code)` - Fornecedores
- `get_bidding_processes(year, municipality_code)` - Licitações
- `get_expenses(year, municipality_code)` - Despesas

**Características:**
- ✅ 184 municípios de PE
- Formato: JSON, XML, HTML
- Schema: `/Entity!Format?filters`

### 3. TCE Ceará
**Chave:** `CE-tce`
**Base:** `https://api.tce.ce.gov.br/sim/1_0`
**Métodos:**
- `get_municipalities()` - Lista municípios CE
- `get_contracts(municipality_code)` - Contratos
- `get_suppliers(municipality_code)` - Negociantes
- `get_bidding_processes(municipality_code)` - Licitações

**Características:**
- ✅ 184 municípios do CE
- Formato: JSON, XML, CSV, HTML
- Schema: `/method.format?params`

### 4. TCE Rio de Janeiro
**Chave:** `RJ-tce`
**Base:** `https://www.tcerj.tc.br/portaldados/api`
**Métodos:**
- `get_contracts(year, municipality_code)` - Contratos
- `get_suppliers(municipality_code)` - Fornecedores
- `get_bidding_processes(year, municipality_code)` - Licitações
- `get_expenses(year, municipality_code)` - Despesas
- `get_revenue(year, municipality_code)` - Receitas

**Características:**
- ✅ 92 municípios do RJ
- Formato: JSON
- RESTful API padrão

### 5. TCE São Paulo
**Chave:** `SP-tce`
**Base:** `https://transparencia.tce.sp.gov.br/api`
**Métodos:**
- `get_municipalities()` - Lista 645 municípios SP
- `get_contracts(year, municipality_code)` - Contratos
- `get_suppliers(municipality_code)` - Fornecedores
- `get_bidding_processes(year, municipality_code)` - Licitações
- `get_expenses(year, municipality_code)` - Despesas
- `get_government_entities(municipality_code)` - Órgãos

**Características:**
- ✅ 645 municípios de SP
- Formato: JSON
- API mais completa do Brasil

### 6. TCE Minas Gerais
**Chave:** `MG-tce`
**Base:** `https://www.tce.mg.gov.br/TCETransparenciaAPI/api`
**Métodos:**
- `get_municipalities()` - Lista 853 municípios MG
- `get_contracts(year, municipality_code)` - Contratos
- `get_suppliers(municipality_code)` - Fornecedores
- `get_bidding_processes(year, municipality_code)` - Licitações
- `get_expenses(year, municipality_code)` - Despesas
- `get_revenue(year, municipality_code)` - Receitas
- `get_public_works(year, municipality_code)` - Obras públicas

**Características:**
- ✅ 853 municípios de MG
- Formato: JSON
- Endpoint exclusivo de obras públicas

### 7. TCE Bahia
**Chave:** `BA-tce`
**Base:** `https://sistemas.tce.ba.gov.br/egestaoapi`
**Métodos:**
- `get_municipalities()` - Lista 417 municípios BA
- `get_contracts(year, municipality_code)` - Contratos
- `get_suppliers(municipality_code)` - Fornecedores
- `get_bidding_processes(year, municipality_code)` - Licitações
- `get_expenses(year, municipality_code)` - Despesas
- `get_revenue(year, municipality_code)` - Receitas

**Características:**
- ✅ 417 municípios da BA
- Formato: JSON
- API versionada (v1)

### 8. CKAN Portals (5 estados)
**Chaves:** `SP-ckan`, `RJ-ckan`, `RS-ckan`, `SC-ckan`, `BA-ckan`
**Métodos:**
- `list_datasets(limit, offset)` - Lista datasets
- `get_dataset(dataset_id)` - Detalhes de dataset
- `search_datasets(query, filters)` - Busca full-text
- `query_datastore(resource_id, filters)` - Query em datastore
- `get_contracts()` - Busca datasets de contratos

**Características:**
- ✅ API CKAN v3 padrão
- ✅ Token opcional
- Múltiplos formatos de dados

## 🔧 Features Técnicas

### Rate Limiting
Todas as APIs implementam rate limiting automático:
- **60 req/min** padrão (conservador)
- Timestamps tracking
- Wait automático quando limite atingido

### Circuit Breaker
Proteção contra APIs instáveis:
- Abre após **5 falhas consecutivas**
- Cooldown de **5 minutos**
- Reset automático

### Retry Logic
Retry automático com exponential backoff:
- **3 tentativas** por padrão
- Espera: 1s, 2s, 4s
- Logging de todas as tentativas

### Normalização de Dados
Todos os clientes normalizam dados para formato comum:
```python
{
    "source": "TCE-PE",
    "contract_id": "123/2024",
    "supplier_name": "Fornecedor XYZ",
    "supplier_id": "12.345.678/0001-90",
    "value": 50000.00,
    "date": "2024-01-15",
    "object": "Aquisição de materiais",
    "municipality": "Recife",
    "raw_data": {...}  # Dados originais preservados
}
```

## 📖 Exemplos

### Exemplo 1: Buscar contratos de Pernambuco
```python
from src.services.transparency_apis import registry

# Get TCE-PE client
pe = registry.get_client('PE-tce')

# Test connection
if await pe.test_connection():
    # Fetch contracts from 2024
    contracts = await pe.get_contracts(year=2024)

    for contract in contracts[:10]:
        print(f"Contrato: {contract['contract_id']}")
        print(f"Fornecedor: {contract['supplier_name']}")
        print(f"Valor: R$ {contract['value']:,.2f}")
        print(f"Município: {contract['municipality']}")
        print("---")
```

### Exemplo 2: Buscar datasets no CKAN de SP
```python
from src.services.transparency_apis import registry

# Get SP CKAN client
sp = registry.get_client('SP-ckan')

# Search for contract-related datasets
datasets = await sp.search_datasets("contratos", limit=20)

for dataset in datasets:
    print(f"Dataset: {dataset.get('title')}")
    print(f"Recursos: {len(dataset.get('resources', []))}")
```

### Exemplo 3: Usar múltiplas APIs de um estado
```python
from src.services.transparency_apis import registry

# Get all APIs for Pernambuco
pe_apis = registry.get_state_apis('PE')

for api in pe_apis:
    print(f"Testing {api.name}...")
    if await api.test_connection():
        print(f"✅ {api.name} OK")

        # Get contracts from each API
        contracts = await api.get_contracts()
        print(f"Found {len(contracts)} contracts")
```

## 🎯 Próximas Integrações

### Estados Prioritários
- [x] TCE Rio de Janeiro ✅
- [x] TCE São Paulo ✅
- [x] TCE Minas Gerais ✅
- [x] TCE Bahia ✅
- [ ] TCE Rio Grande do Sul
- [ ] TCE Santa Catarina
- [ ] Amazonas (Estado)
- [ ] Minas Gerais (Estado)

### Funcionalidades
- [ ] Bulk data export
- [ ] Data caching layer (em progresso)
- [ ] Health check endpoints (em progresso)
- [ ] Webhook notifications
- [ ] GraphQL unified API

## 📝 Licença

Proprietary - All rights reserved
© 2025 Anderson Henrique da Silva
