# 🏛️ APIs Governamentais Brasileiras - Guia Completo 2025

**Autor**: Anderson Henrique da Silva
**Data**: 2025-10-14
**Versão**: 1.0.0
**Localização**: Minas Gerais, Brasil

---

## 📋 Índice

1. [APIs Já Integradas](#apis-já-integradas)
2. [APIs Federais Prioritárias para Integração](#apis-federais-prioritárias)
3. [APIs Financeiras e Econômicas](#apis-financeiras-e-econômicas)
4. [APIs Eleitorais e Políticas](#apis-eleitorais-e-políticas)
5. [APIs de Compras e Contratações](#apis-de-compras-e-contratações)
6. [APIs Trabalhistas e Sociais](#apis-trabalhistas-e-sociais)
7. [APIs de Identificação](#apis-de-identificação)
8. [APIs Estaduais e Municipais](#apis-estaduais-e-municipais)
9. [Plano de Integração Priorizado](#plano-de-integração)
10. [Considerações Técnicas](#considerações-técnicas)

---

## ✅ APIs Já Integradas (13)

### APIs Federais Implementadas (4)

#### 1. **IBGE** - Instituto Brasileiro de Geografia e Estatística
- **URL Base**: https://servicodados.ibge.gov.br/api/v3
- **Status**: ✅ FUNCIONAL
- **Cliente**: `src/services/transparency_apis/federal_apis/ibge_client.py` (743 linhas)
- **Cache**: 1-24h TTL
- **Endpoints**:
  - Demografia (população, raça, idade)
  - Economia (PIB per capita, renda)
  - Pobreza (linha de pobreza, Gini)
  - Educação (analfabetismo, escolaridade)
  - Habitação (água, esgoto, energia)
- **Limitação**: Dados em agregados, não microdata

#### 2. **DataSUS** - Ministério da Saúde
- **URL Base**: https://opendatasus.saude.gov.br/api/3/action
- **Status**: ✅ FUNCIONAL
- **Cliente**: `src/services/transparency_apis/federal_apis/datasus_client.py` (553 linhas)
- **Cache**: 1-24h TTL
- **Endpoints**:
  - Mortalidade (SIM)
  - Internações hospitalares (SIH)
  - Vacinação (SI-PNI)
  - Estabelecimentos de saúde (CNES)
- **Limitação**: Datasets para download (CSVs grandes)

#### 3. **INEP** - Instituto Nacional de Estudos e Pesquisas
- **URL Base**: https://dados.gov.br/api/3/action (datasets INEP)
- **Status**: ✅ FUNCIONAL
- **Cliente**: `src/services/transparency_apis/federal_apis/inep_client.py` (695 linhas)
- **Cache**: 2-24h TTL
- **Endpoints**:
  - Censo Escolar
  - IDEB (Índice de Desenvolvimento da Educação Básica)
  - ENEM (Exame Nacional do Ensino Médio)
  - Infraestrutura escolar
  - Estatísticas de professores
- **Limitação**: Microdata em CSVs para download

#### 4. **Portal da Transparência Federal (CGU)**
- **URL Base**: https://api.portaldatransparencia.gov.br
- **Status**: ⚠️ PARCIAL (22% funcional, 78% retornam 403)
- **Cliente**: `src/tools/transparency_api.py`
- **Rate Limit**: 90 req/min (6h-23h59), 300 req/min (0h-5h59)
- **Endpoints Funcionais**:
  - ✅ Contratos (requer codigoOrgao)
  - ✅ Servidores (requer CPF)
  - ✅ Órgãos públicos
- **Endpoints Bloqueados (403)**:
  - ❌ Despesas
  - ❌ Fornecedores
  - ❌ Emendas parlamentares
  - ❌ Auxílios (Bolsa Família, BPC)
  - ❌ Cartões de pagamento
  - ❌ Viagens

### APIs de LLM (2)
5. ✅ **GROQ API** - Provedor LLM (obrigatório)
6. ✅ **Maritaca AI** - LLM brasileiro

### APIs de Dados Abertos (1)
7. ✅ **Dados.gov.br** - Portal unificado de dados abertos

### TCEs Implementados (6)
8-13. ✅ **TCE-SP, TCE-RJ, TCE-MG, TCE-BA, TCE-CE, TCE-PE**

---

## 🔥 APIs Federais Prioritárias para Integração

### 1. **Catálogo de APIs Governamentais (Conecta Gov.br)**
- **URL**: https://www.gov.br/conecta/catalogo/
- **Descrição**: Catálogo unificado com 100+ APIs do governo federal
- **Prioridade**: 🔥🔥🔥 ALTA
- **Valor**: Descoberta de novas APIs governamentais
- **Complexidade**: Baixa (metadados JSON)

### 2. **Portal de Dados Abertos (dados.gov.br)**
- **URL**: https://dados.gov.br/api/3/action
- **API Documentation**: https://docs.ckan.org/en/latest/api/
- **Prioridade**: 🔥🔥🔥 ALTA
- **Status**: Parcialmente integrado
- **Endpoints Principais**:
  - `package_search` - Buscar datasets
  - `package_show` - Detalhes de dataset
  - `organization_list` - Listar órgãos
  - `tag_list` - Listar tags
- **Autenticação**: Token opcional (melhora rate limits)
- **Formato**: JSON
- **Complexidade**: Baixa

---

## 💰 APIs Financeiras e Econômicas

### 3. **Banco Central do Brasil**
- **URL Base**: https://api.bcb.gov.br/dados/serie/bcdata.sgs
- **Portal**: https://dadosabertos.bcb.gov.br/
- **Prioridade**: 🔥🔥🔥 ALTA
- **Autenticação**: Não requer
- **Formato**: JSON, XML
- **Limitação**: Consultas limitadas a 10 anos

**Endpoints Principais**:
1. **Taxa SELIC**
   - Endpoint: `/dados/serie/bcdata.sgs.{codigo}/dados`
   - Códigos: 11 (SELIC), 4390 (SELIC acumulada), 1178 (SELIC anualizada)
   - Parâmetros: dataInicial, dataFinal, formato=json

2. **Taxa de Câmbio**
   - URL: https://dadosabertos.bcb.gov.br/dataset/taxas-de-cambio-todos-os-boletins-diarios
   - Protocolo: OData
   - Formato: JSON, XML

3. **Estatísticas PIX**
   - URL: https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata/
   - Formato: JSON
   - Dados: Transações, volume, estabelecimentos

**Casos de Uso**:
- Análise econômica de contratos (correlação com SELIC)
- Conversão de valores históricos (câmbio)
- Análise de adoção de PIX em pagamentos governamentais

---

### 4. **Tesouro Nacional**
- **URL Base**: https://www.gov.br/tesouronacional/pt-br/central-de-conteudo/apis
- **Prioridade**: 🔥🔥🔥 ALTA
- **Autenticação**: Não requer (dados abertos)

**Principais APIs**:

#### 4.1 **SICONFI API** (Sistema de Informações Contábeis e Fiscais)
- **URL**: http://apidatalake.tesouro.gov.br/docs/siconfi/
- **Formato**: JSON (5.000 itens por página)
- **Dados**:
  - Execução orçamentária de estados e municípios
  - Balanços anuais
  - Receitas e despesas públicas
  - Dívida pública
- **Casos de Uso**:
  - Análise fiscal de entes federativos
  - Comparação de gastos municipais
  - Monitoramento de dívida pública

#### 4.2 **INTEGRA SIAFI** (integração com SIAFI)
- **URL**: Acesso via catálogo gov.br
- **Descrição**: Comunicação online com SIAFI para consulta de documentos orçamentários
- **Complexidade**: Alta (requer credenciais específicas)

#### 4.3 **Custos do Governo Federal**
- **URL**: https://www.tesourotransparente.gov.br/consultas/custos-api-de-dados-abertos
- **Dados**: Custos por órgão, programa, ação governamental
- **Casos de Uso**: Análise de eficiência de políticas públicas

---

## 🗳️ APIs Eleitorais e Políticas

### 5. **TSE - Tribunal Superior Eleitoral**
- **Portal**: https://dadosabertos.tse.jus.br/
- **Repositório**: https://www.tse.jus.br/eleicoes/estatisticas/repositorio-de-dados-eleitorais-1
- **Prioridade**: 🔥🔥 MÉDIA-ALTA
- **Formato**: CSV (datasets), API (consultas)
- **Autenticação**: Não requer

**Dados Disponíveis**:
1. **Candidatos** (desde 1950)
   - Dados biográficos
   - Bens declarados
   - Histórico eleitoral

2. **Prestação de Contas** (desde 2002)
   - Receitas de campanha
   - Despesas de campanha
   - CNPJs de campanha
   - Extratos bancários

3. **Resultados Eleitorais**
   - Votos por seção
   - Votos por zona
   - Abstenções

4. **Sistema DivulgaCandContas**
   - Atualizado 3x ao dia (8h, 14h, 20h)
   - Dados de sistemas Cand e SPCE

**API de Acesso**:
- Endpoint: Consultar documentação do portal
- Ver: https://dadosabertos.tse.jus.br/dataset/?q=candidatos

**Casos de Uso**:
- Análise de financiamento de campanhas
- Cruzamento: políticos × contratos públicos
- Rastreamento de patrimônio de candidatos

---

## 🛒 APIs de Compras e Contratações

### 6. **Compras Governamentais (Compras.gov.br)**
- **URL**: https://compras.dados.gov.br/docs/home.html
- **Manual**: https://www.gov.br/compras/pt-br/acesso-a-informacao/manuais/manual-dados-abertos/manual-api-compras.pdf
- **Prioridade**: 🔥🔥🔥 ALTA
- **Autenticação**: Não requer
- **Formato**: XML, JSON, CSV

**Módulos Disponíveis**:
1. **CATMAT/CATSER** - Catálogo de materiais e serviços
2. **Licitações** - Processos licitatórios
3. **SICAF** - Cadastro de fornecedores
4. **Contratos** - Gestão de contratos
5. **ARP** - Atas de Registro de Preços

**Sistemas**:
- **SIASG** - Sistema Integrado de Administração de Serviços Gerais
- **Comprasnet** - Portal de compras (legado)

**Casos de Uso**:
- Análise de preços de mercado
- Identificação de fornecedores frequentes
- Rastreamento de processos licitatórios

---

### 7. **PNCP - Portal Nacional de Contratações Públicas**
- **URL Base**: https://pncp.gov.br/pncp-api/v1/
- **Portal**: https://www.gov.br/pncp/pt-br
- **Prioridade**: 🔥🔥🔥 CRÍTICA
- **Lei**: 14.133/2021 (Nova Lei de Licitações)
- **Status**: Obrigatório desde 2023

**Estrutura da API**:
- Endpoint exemplo: `/orgaos/{cnpj}/compras/{ano}/{numero}/arquivos/{id}`
- Formato: JSON
- Dados:
  - Editais de licitação
  - Resultados de contratações (Lei 14.133)
  - Atas de registro de preço
  - Contratos firmados

**Casos de Uso**:
- Compliance com nova Lei de Licitações
- Análise de transparência nos processos
- Integração obrigatória para órgãos públicos

---

### 8. **Painel de Preços**
- **URL**: https://paineldeprecos.planejamento.gov.br/
- **Prioridade**: 🔥🔥 MÉDIA
- **Dados**: Preços praticados em compras governamentais
- **Formato**: Web scraping ou API (verificar documentação)

**Casos de Uso**:
- Benchmarking de preços
- Detecção de sobrepreço
- Análise de mercado

---

## 👷 APIs Trabalhistas e Sociais

### 9. **RAIS / CAGED - Ministério do Trabalho**
- **URL Base**: FTP ftp://ftp.mtps.gov.br/pdet/microdados/
- **Portal**: https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho/
- **Prioridade**: 🔥🔥 MÉDIA
- **Formato**: Arquivos TXT delimitados (;)
- **Autenticação**: Acesso público (microdata não identificado)

**Dados RAIS (Relação Anual de Informações Sociais)**:
- Estabelecimentos (por setor, tamanho)
- Empregados (por idade, gênero, escolaridade)
- Remuneração média (por ocupação, setor)
- Período: Anual (snapshot 31/dez)

**Dados CAGED (Cadastro Geral de Empregados e Desempregados)**:
- Admissões e desligamentos mensais
- Saldo de empregos
- Setores de atividade

**PDET** (Programa de Disseminação das Estatísticas do Trabalho):
- Interface web para consultas
- Alternativa ao FTP

**Limitações**:
- ❌ Não é API REST
- ⚠️ Arquivos grandes (microdata)
- ⚠️ Dados identificados requerem LGPD compliance

**Alternativa**:
- **Base dos Dados**: https://basedosdados.org/ (dados tratados, acesso via SQL/Python/R)

**Casos de Uso**:
- Análise de mercado de trabalho por setor
- Correlação empregos × contratos públicos
- Análise salarial por região

---

## 🆔 APIs de Identificação

### 10. **Receita Federal - CNPJ/CPF**

⚠️ **Importante**: Receita Federal NÃO oferece API oficial pública

**Opções Disponíveis**:

#### 10.1 **Minha Receita** (Open Source, Gratuita)
- **URL**: https://minhareceita.org/
- **GitHub**: https://github.com/cuducos/minha-receita
- **Prioridade**: 🔥🔥🔥 ALTA
- **Status**: ✅ Iniciativa da sociedade civil
- **Formato**: JSON
- **Endpoint**: `https://minhareceita.org/{CNPJ}`
- **Autenticação**: Não requer
- **Dados**:
  - Razão social
  - Situação cadastral
  - Endereço
  - Atividade econômica (CNAE)
  - Quadro societário
  - Capital social

**Vantagens**:
- ✅ Gratuita
- ✅ Sem CAPTCHA
- ✅ API REST padrão
- ✅ Dados consolidados

#### 10.2 **Dados Públicos CNPJ (Receita Federal)**
- **URL**: https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/cadastros/consultas/dados-publicos-cnpj
- **Formato**: CSVs atualizados mensalmente
- **Prioridade**: 🔥🔥 MÉDIA (alternativa offline)
- **Tamanho**: ~100GB+ (todos CNPJs do Brasil)

#### 10.3 **APIs Comerciais** (Pagas)
- CPF.CNPJ (https://cpfcnpj.com.br)
- DBDireto
- SintegraWS
- Infosimples

**Recomendação**: Usar **Minha Receita** para cidadao.ai

---

## 🏛️ APIs Estaduais e Municipais

### Tribunais de Contas Estaduais (TCEs)

**Já implementados** (estrutura básica):
- ✅ TCE-SP, TCE-RJ, TCE-MG, TCE-BA, TCE-CE, TCE-PE

**Para implementar**:
- TCE-RS, TCE-PR, TCE-SC (Sul)
- TCE-AM, TCE-PA (Norte)
- TCE-GO, TCE-DF (Centro-Oeste)
- Demais TCEs do Nordeste

**Desafio**: Cada TCE tem estrutura de API diferente

### Portais de Transparência Municipais

**API padrão CKAN**:
- Muitos municípios usam CKAN (mesmo sistema do dados.gov.br)
- Endpoints padrão: `/api/3/action/package_search`

**Principais cidades**:
- São Paulo: https://dados.prefeitura.sp.gov.br/
- Rio de Janeiro: https://www.data.rio/
- Belo Horizonte, Curitiba, Porto Alegre, etc.

---

## 📋 Plano de Integração Priorizado

### 🔥 Fase 1: CRÍTICO (2-4 semanas)

#### 1.1 **PNCP** (Portal Nacional de Contratações Públicas)
- **Justificativa**: Obrigatório por lei (14.133/2021), dados centralizados
- **Esforço**: Médio (API REST padrão)
- **Impacto**: Alto (todas contratações pós-2023)
- **Cliente**: `src/services/transparency_apis/federal_apis/pncp_client.py`

#### 1.2 **Compras Governamentais (Compras.gov.br)**
- **Justificativa**: Dados históricos de licitações
- **Esforço**: Alto (múltiplos módulos)
- **Impacto**: Alto (integração com PNCP)
- **Cliente**: `src/services/transparency_apis/federal_apis/compras_gov_client.py`

#### 1.3 **Banco Central**
- **Justificativa**: Dados econômicos para contextualizar contratos
- **Esforço**: Baixo (API bem documentada)
- **Impacto**: Médio (análises econômicas)
- **Cliente**: `src/services/transparency_apis/federal_apis/bcb_client.py`

#### 1.4 **Minha Receita** (CNPJ)
- **Justificativa**: Essencial para verificar fornecedores
- **Esforço**: Baixo (API simples)
- **Impacto**: Alto (enriquecimento de dados)
- **Cliente**: `src/services/transparency_apis/federal_apis/minha_receita_client.py`

---

### 🔥 Fase 2: ALTA PRIORIDADE (1-2 meses)

#### 2.1 **TSE** (Dados Eleitorais)
- **Justificativa**: Cruzamento políticos × contratos
- **Esforço**: Médio (datasets CSV + API)
- **Impacto**: Alto (transparência política)
- **Cliente**: `src/services/transparency_apis/federal_apis/tse_client.py`

#### 2.2 **Tesouro Nacional (SICONFI)**
- **Justificativa**: Finanças públicas municipais/estaduais
- **Esforço**: Médio
- **Impacto**: Alto (análise fiscal)
- **Cliente**: `src/services/transparency_apis/federal_apis/siconfi_client.py`

#### 2.3 **Catálogo de APIs Gov.br**
- **Justificativa**: Descoberta de novas APIs
- **Esforço**: Baixo
- **Impacto**: Médio (expansão futura)
- **Cliente**: `src/services/transparency_apis/federal_apis/catalogo_apis_client.py`

---

### 🔥 Fase 3: MÉDIA PRIORIDADE (2-3 meses)

#### 3.1 **RAIS/CAGED** (via Base dos Dados)
- **Justificativa**: Dados trabalhistas
- **Esforço**: Médio (integração SQL/API)
- **Impacto**: Médio
- **Cliente**: `src/services/transparency_apis/federal_apis/base_dados_client.py`

#### 3.2 **Expansão TCEs**
- **Justificativa**: Cobertura estadual completa
- **Esforço**: Alto (APIs heterogêneas)
- **Impacto**: Alto (fiscalização estadual)
- **Clientes**: `src/services/transparency_apis/tce_apis/tce_*.py`

#### 3.3 **Portais Municipais** (Grandes Capitais)
- **Justificativa**: Dados municipais detalhados
- **Esforço**: Médio (API CKAN padrão)
- **Impacto**: Médio
- **Clientes**: `src/services/transparency_apis/municipal_apis/*.py`

---

## 🛠️ Considerações Técnicas

### Padrões de Implementação

Todos os clientes devem seguir o padrão enterprise já estabelecido:

```python
# Template: src/services/transparency_apis/federal_apis/template_client.py

import httpx
from typing import Any, Optional
from functools import wraps
from datetime import datetime

from src.core import get_logger
from .exceptions import NetworkError, ServerError, TimeoutError
from .metrics import FederalAPIMetrics
from .retry import retry_with_backoff

class APIClient:
    """API Client following enterprise pattern."""

    BASE_URL = "https://api.example.gov.br"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )
        self.logger = get_logger(__name__)

    @retry_with_backoff(max_attempts=3, base_delay=1.0, max_delay=30.0)
    async def _make_request(self, url: str, method: str = "GET", **kwargs) -> dict[str, Any]:
        """Make HTTP request with retry, metrics, error handling."""
        # Implementation with FederalAPIMetrics integration
        pass

    @cache_with_ttl(ttl_seconds=3600)
    async def get_data(self, params: dict) -> dict[str, Any]:
        """Get data with caching."""
        pass
```

### Checklist de Implementação

Para cada nova API:

- [ ] **Cliente Base**
  - [ ] Classe com `__init__`, `close`, `__aenter__`, `__aexit__`
  - [ ] `_make_request` com retry, timeouts, error handling
  - [ ] Integração com `FederalAPIMetrics`
  - [ ] Type hints completos

- [ ] **Cache**
  - [ ] Decorator `@cache_with_ttl`
  - [ ] TTL adequado por endpoint (1h-24h)
  - [ ] Hash de cache keys (MD5 de parâmetros)

- [ ] **Tratamento de Erros**
  - [ ] NetworkError, TimeoutError, ServerError
  - [ ] Logging estruturado
  - [ ] Mensagens de erro claras

- [ ] **Testes**
  - [ ] `tests/unit/services/transparency_apis/test_{api}_client.py`
  - [ ] Mocks de respostas HTTP
  - [ ] Testes de retry, timeout, cache
  - [ ] Coverage >80%

- [ ] **Documentação**
  - [ ] Docstrings completos
  - [ ] README em `docs/apis/{API}.md`
  - [ ] Exemplos de uso
  - [ ] Rate limits documentados

- [ ] **Integração com Agentes**
  - [ ] Adicionar ao agente relevante (Dandara, Lampião, etc.)
  - [ ] Casos de uso documentados
  - [ ] Testes end-to-end

---

## 📊 Métricas de Sucesso

### KPIs de Integração

| Métrica | Meta | Status Atual |
|---------|------|--------------|
| APIs Federais Integradas | 15 | 4 (27%) |
| APIs Estaduais (TCEs) | 27 | 6 (22%) |
| Cobertura de Dados | 80% endpoints | 22% Portal, 100% IBGE/INEP/DataSUS |
| Uptime das APIs | >99% | Monitorar |
| Cache Hit Rate | >85% | 85%+ (IBGE) |
| Response Time (p95) | <500ms | ~200ms (cached) |

### Roadmap 2025

- **Q1 2025**: PNCP, Compras.gov.br, BCB, Minha Receita ✅
- **Q2 2025**: TSE, SICONFI, Catálogo APIs
- **Q3 2025**: RAIS/CAGED, TCEs expansão
- **Q4 2025**: Municipais (capitais), otimizações

---

## 🔗 Referências

### Documentação Oficial
- Portal de Dados Abertos: https://dados.gov.br/
- Catálogo de APIs Gov.br: https://www.gov.br/conecta/catalogo/
- Portal da Transparência: https://portaldatransparencia.gov.br/api-de-dados

### Comunidade e Open Source
- Minha Receita: https://github.com/cuducos/minha-receita
- Base dos Dados: https://basedosdados.org/
- Brasil.IO: https://brasil.io/

### Legislação
- Lei de Acesso à Informação (12.527/2011)
- Decreto de Dados Abertos (8.777/2016)
- Lei de Licitações (14.133/2021)
- LGPD (13.709/2018)

---

**Última Atualização**: 2025-10-14 (Minas Gerais, Brasil)
**Versão**: 1.0.0 - Levantamento Inicial Completo
