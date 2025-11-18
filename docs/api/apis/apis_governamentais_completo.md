# APIs Governamentais Brasileiras - LAI e Acesso Público
## Compilação Completa - Outubro 2025

---

## 🔴 NÍVEL FEDERAL

### 📊 EXECUTIVO

#### 1. Portal Brasileiro de Dados Abertos
**Base Legal**: Lei 12.527/2011 (LAI), Decreto 8.777/2016
- **URL**: `https://dados.gov.br`
- **Swagger Produção**: `https://dados.gov.br/swagger-ui/index.html`
- **Swagger Homologação**: `https://hmg.dados.gov.br/swagger-ui/index.html`
- **Autenticação**: Token OAuth (gerado em https://dados.gov.br/dados/conteudo/como-acessar-a-api-do-portal-de-dados-abertos-com-o-perfil-de-consumidor)
- **Cobertura**: Catálogo nacional de datasets abertos federais

#### 2. Portal da Transparência Federal (CGU)
**Base Legal**: LC 101/2000, LC 131/2009, Lei 12.527/2011
- **Base URL**: `https://api.portaldatransparencia.gov.br/api-de-dados`
- **Documentação**: https://portaldatransparencia.gov.br/api-de-dados
- **Registro**: Enviar email para cadastro de chave API
- **Rate Limit**:
  - 90 req/min (06:00-23:59)
  - 300 req/min (00:00-05:59)

**Endpoints principais**:
```
/bolsa-familia-por-municipio
/auxilio-emergencial
/cartoes
/ceaf (Cadastro de Expulsões)
/ceis (Empresas Inidôneas e Suspensas)
/cnep (Empresas Punidas)
/contratos
/convenios
/despesas
/licitacoes
/servidores
```

#### 3. SICONFI - Sistema de Informações Contábeis e Fiscais
**Órgão**: Secretaria do Tesouro Nacional
- **Base URL**: `https://apidatalake.tesouro.gov.br/`
- **Documentação**: https://www.tesourotransparente.gov.br/consultas/consultas-siconfi/siconfi-api-de-dados-abertos
- **Dados**: MSC (Matriz Saldos Contábeis), RGF, RREO, FINBRA
- **Cobertura**: 5.570 municípios + 27 estados + DF
- **Histórico**: Desde 2013 (alguns dados)

#### 4. ConectaGov.br - Catálogo de APIs
**Órgão**: MGI (Ministério da Gestão e Inovação)
- **URL**: https://www.gov.br/conecta/catalogo/
- **APIs disponíveis**:
  - SIORG (Estruturas Organizacionais)
  - SIAPE (Servidores Públicos Federais)
  - CADIN (Cadastro de Inadimplentes)
  - DOU (Diário Oficial da União)
  - e-Aud (Auditorias CGU)
  - COFIEX (Financiamentos Externos)
  - Obrasgov.br

#### 5. IBGE - Instituto Brasileiro de Geografia e Estatística
**Base URL**: `https://servicodados.ibge.gov.br/api/`
- **Doc Completa**: https://servicodados.ibge.gov.br/api/docs

**APIs por área**:
```
/v1/agregados          # Tabelas SIDRA
/v1/localidades        # Municípios, estados, regiões
/v2/malhas             # Shapefiles geográficos
/v1/projecoes          # Projeções populacionais
/v3/nomes              # Ranking de nomes
/v1/censos             # Dados censitários
```

**Exemplos de uso**:
```bash
# Listar todos os municípios do Brasil
curl https://servicodados.ibge.gov.br/api/v1/localidades/municipios

# PIB per capita por estado
curl https://servicodados.ibge.gov.br/api/v3/agregados/5938/periodos/-6/variaveis/37?localidades=N3[all]
```

#### 6. INEP - Instituto Nacional de Estudos e Pesquisas Educacionais
- **Portal**: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos
- **Dados**: Censo Escolar, ENEM, ENADE, IDEB
- **Formato**: Bulk downloads (CSV, SPSS, Stata)
- **API não-oficial**: http://educacao.dadosabertosbr.org/api (comunidade)

#### 7. INPE - Instituto Nacional de Pesquisas Espaciais
- **Portal Novo**: https://data.inpe.br
- **BDQueimadas**: https://queimadas.dgi.inpe.br/queimadas/bdqueimadas
- **PRODES**: http://terrabrasilis.dpi.inpe.br/
- **Formato**: APIs REST modernas, STAC (SpatioTemporal Asset Catalog)

---

### 🏛️ LEGISLATIVO

#### 8. Câmara dos Deputados
**Base URL**: `https://dadosabertos.camara.leg.br/api/v2`
- **Swagger**: https://dadosabertos.camara.leg.br/swagger/api.html
- **Formatos**: JSON, XML, CSV
- **Autenticação**: Pública (sem chave)

**Endpoints principais**:
```
/deputados                    # Lista deputados
/deputados/{id}              # Dados específicos
/deputados/{id}/despesas     # Cota parlamentar
/proposicoes                 # Projetos de lei
/proposicoes/{id}/votacoes   # Votações
/votacoes                    # Todas votações
/orgaos                      # Comissões
/blocos                      # Blocos parlamentares
/frentes                     # Frentes parlamentares
/partidos                    # Partidos políticos
/legislaturas                # Legislaturas históricas
```

**Exemplo**:
```bash
# Despesas do deputado ID 204521 em 2024
curl 'https://dadosabertos.camara.leg.br/api/v2/deputados/204521/despesas?ano=2024&ordem=ASC&ordenarPor=ano'
```

#### 9. Senado Federal
**Base URL**: `https://legis.senado.leg.br/dadosabertos`
- **Swagger**: https://legis.senado.leg.br/dadosabertos/api-docs/swagger-ui/index.html
- **Documentação**: https://legis.senado.leg.br/dadosabertos/docs/index.html
- **Formato**: XML, JSON
- **Autenticação**: Pública

**Principais serviços**:
```
/senador/lista               # Lista senadores
/materia/pesquisa           # Matérias legislativas
/votacao/lista              # Votações
/comissao/lista             # Comissões
/agenda/dia                 # Agenda diária
```

---

### ⚖️ JUDICIÁRIO

#### 10. CNJ - DataJud (API Pública)
**Base URL**: `https://api-publica.datajud.cnj.jus.br`
- **Documentação**: https://www.cnj.jus.br/sistemas/datajud/api-publica/
- **Base Legal**: Resolução CNJ 331/2020, Portaria 160/2020
- **Autenticação**: Chave pública (fornecida no portal)
- **Chave atual**: Disponível em https://www.cnj.jus.br/sistemas/datajud/api-publica/

**Cobertura**:
- Todos os TJs (Tribunais de Justiça estaduais)
- Todos os TRFs (Tribunais Regionais Federais)
- Todos os TRTs (Tribunais Regionais do Trabalho)
- STJ, STF, TST, TSE, STM

**Endpoint**:
```bash
GET /api_publica_<tribunal>/_search
Authorization: APIKey <chave>

# Exemplo - buscar processos do TJDFT
curl -X GET "https://api-publica.datajud.cnj.jus.br/api_publica_tjdft/_search" \
  -H "Authorization: APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
```

**Painel Estatístico**: https://paineisanalytics.cnj.jus.br/

#### 11. STJ - Superior Tribunal de Justiça
- **Portal**: https://www.stj.jus.br/sites/portalp/Paginas/Comunicacao/Dados-abertos
- **Dados**:
  - Jurisprudência
  - Acórdãos e decisões terminativas
  - DJE (Diário da Justiça Eletrônico)
  - Precedentes qualificados
  - Movimentação processual
- **Formato**: JSON, CSV, XML
- **Download**: Bulk files

#### 12. TCU - Tribunal de Contas da União
**Webservices**: https://sites.tcu.gov.br/dados-abertos/webservices-tcu/

**Endpoints REST**:
```
# Acórdãos do TCU
GET https://contas.tcu.gov.br/ords/api/publica/scn/acordaos

# Processos específicos
GET https://contas.tcu.gov.br/ords/api/publica/scn/pedidos_congresso/{numero}

# Inabilitados para cargo público
GET https://contas.tcu.gov.br/ords/condenacao/consulta/inabilitados
GET https://contas.tcu.gov.br/ords/condenacao/consulta/inabilitados/{CPF}

# Licitações do TCU
GET https://dados-abertos.apps.tcu.gov.br/api/licitacao

# Atos normativos
GET https://dados-abertos.apps.tcu.gov.br/api/atonormativo/recupera-atos-normativos

# Pautas de sessões
GET https://contas.tcu.gov.br/ords/api/publica/scn/pautas_sessoes
```

---

## 🟡 NÍVEL ESTADUAL

### Observação Importante
**A maioria dos estados não possui APIs REST estruturadas**. A implementação é heterogênea:
- Alguns têm portais de dados abertos com downloads bulk
- Poucos têm APIs propriamente ditas
- Muitos só têm portais de transparência HTML

### Estados com APIs Documentadas:

#### 13. São Paulo
**Portal Estadual**: https://dadosabertos.sp.gov.br/
- Formato: Datasets para download
- API: Não documentada publicamente

**Prefeitura de São Paulo - APILIB**:
- **URL**: https://apilib.prefeitura.sp.gov.br/store/
- **APIs disponíveis**:
  - Despesas e Contratos
  - GeoSampa (dados geográficos)
  - SP156 (serviços municipais)
  - Mobilidade Urbana

#### 14. Maranhão
**Portal**: https://www.transparencia.ma.gov.br
- **Base URL**: `/api/`
- **Formato**: JSON
- **Autenticação**: Pública

**Endpoints**:
```
GET /api/consulta-despesas
GET /api/consulta-notas
GET /api/consulta-unidades
```

#### 15. Rio de Janeiro (Municipal)
**Data.rio**: http://www.data.rio/
- Datasets para download
- Algumas APIs REST (variável por secretaria)

---

## 🟢 OUTROS ÓRGÃOS E AUTARQUIAS

#### 16. ANATEL
- Portal de dados: https://informacoes.anatel.gov.br/paineis/
- Formato: Dashboards (sem API pública documentada)

#### 17. ANS (Agência Nacional de Saúde Suplementar)
- Dados Abertos: https://www.gov.br/ans/pt-br/acesso-a-informacao/dados-abertos
- Formato: CSV, XML (downloads)

#### 18. ANVISA
- Dados Abertos: https://dados.gov.br/organization/agencia-nacional-de-vigilancia-sanitaria-anvisa
- Formato: CSV (bulk downloads)

#### 19. BACEN (Banco Central)
**API SGS**: Sistema Gerenciador de Séries Temporais
- **URL**: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados`
- **Documentação**: https://dadosabertos.bcb.gov.br/

**Exemplo**:
```bash
# Selic diária (código 11)
curl "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json"
```

---

## 📋 ANÁLISE TÉCNICA E RECOMENDAÇÕES

### Maturidade das APIs Governamentais Brasileiras

**Alta maturidade** (REST, OpenAPI, rate limiting documentado):
- ✅ Câmara dos Deputados
- ✅ Portal da Transparência Federal
- ✅ DataJud/CNJ
- ✅ IBGE
- ✅ Banco Central

**Média maturidade** (REST, mas documentação incompleta):
- ⚠️ Senado Federal
- ⚠️ TCU
- ⚠️ Portal Dados Abertos (dados.gov.br)
- ⚠️ SICONFI

**Baixa maturidade** (bulk downloads, sem API REST):
- ❌ INEP
- ❌ Maioria das APIs estaduais
- ❌ Maioria das autarquias

### Problemas Identificados

1. **Fragmentação**: Não há padrão único (cada órgão implementa de forma diferente)
2. **Documentação**: Muitas APIs sem swagger/openapi completo
3. **Versionamento**: Pouca clareza sobre deprecation policies
4. **Rate Limiting**: Maioria não documenta limites ou políticas de uso justo
5. **Autenticação**: Mistura de público, OAuth, API keys, sem padrão
6. **Formatos**: JSON dominante, mas XML e CSV ainda presentes
7. **Uptime**: SLAs não documentados, disponibilidade variável
8. **CORS**: Muitas APIs bloqueiam requisições de browsers

### Recomendações Arquiteturais para Cidadão.AI

#### 1. Camada de Abstração
```python
# Criar adapters para cada fonte
class TransparenciaAdapter(BaseAdapter):
    base_url = "https://api.portaldatransparencia.gov.br"
    auth_type = "api_key"
    rate_limit = 90  # req/min

class CamaraAdapter(BaseAdapter):
    base_url = "https://dadosabertos.camara.leg.br/api/v2"
    auth_type = None
    rate_limit = None  # desconhecido
```

#### 2. Caching Estratégico
```python
# Diferentes TTLs baseado em frequência de atualização
CACHE_TTL = {
    'deputados': 86400,        # 1 dia (muda raramente)
    'despesas': 3600,          # 1 hora (atualiza diariamente)
    'votacoes': 1800,          # 30 min (em tempo real)
    'siconfi_balanco': 2592000 # 30 dias (anual)
}
```

#### 3. Circuit Breaker
```python
# Lidar com indisponibilidade
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def fetch_from_gov_api(endpoint):
    # API call here
    pass
```

#### 4. Bulk vs Real-time
Para análises históricas extensas:
- **Preferir**: Downloads bulk do Portal da Transparência
- **Evitar**: Milhares de requisições à API

Para consultas pontuais e atualizações:
- **Usar**: APIs REST

#### 5. Observabilidade
```python
# Métricas essenciais
- api_request_duration_seconds (histogram)
- api_request_total (counter by endpoint, status)
- api_cache_hit_ratio (gauge)
- api_rate_limit_remaining (gauge)
```

### Compliance e Considerações Legais

#### LAI (Lei 12.527/2011)
- Dados devem ser acessíveis sem necessidade de justificativa
- Formato aberto e processável por máquina
- Granularidade primária (não agregados quando possível)

#### LGPD (Lei 13.709/2018)
- Mesmo dados públicos podem conter informações pessoais
- **Cuidado com**: CPFs, nomes completos, endereços residenciais
- **Anonimização**: Considerar para análises agregadas

### Endpoints Prioritários para Cidadão.AI

```python
PRIORITY_APIS = {
    'transparencia': {
        'weight': 10,  # crítico
        'endpoints': ['despesas', 'contratos', 'convenios', 'servidores']
    },
    'camara': {
        'weight': 9,
        'endpoints': ['proposicoes', 'votacoes', 'deputados/despesas']
    },
    'senado': {
        'weight': 9,
        'endpoints': ['materia/pesquisa', 'votacao']
    },
    'datajud': {
        'weight': 8,
        'endpoints': ['processos por tema']
    },
    'siconfi': {
        'weight': 8,
        'endpoints': ['msc', 'rreo', 'rgf']
    },
    'tcu': {
        'weight': 7,
        'endpoints': ['acordaos', 'inabilitados']
    }
}
```

---

## 📚 Referências

### Legislação Base
- **Lei 12.527/2011** - Lei de Acesso à Informação (LAI)
- **LC 101/2000** - Lei de Responsabilidade Fiscal
- **LC 131/2009** - Transparência da Gestão Fiscal
- **Decreto 8.777/2016** - Política de Dados Abertos do Executivo Federal
- **Lei 13.709/2018** - Lei Geral de Proteção de Dados (LGPD)

### Papers e Estudos
- Silva, P. N. (2023). "Observatório de dados governamentais abertos: acesso às APIs brasileiras". *Revista ACB*, v. 28, n. 1.
- Open Knowledge Foundation (2023). "The Open Data Handbook"

### Recursos da Comunidade
- **Brasil.IO**: https://brasil.io/ (datasets limpos e APIs comunitárias)
- **Operação Serenata**: https://serenata.ai/ (análise de gastos públicos)
- **Querido Diário**: https://queridodiario.ok.org.br/ (diários oficiais municipais)

---

## ⚠️ DISCLAIMER

Este documento foi compilado em **outubro de 2025** através de pesquisa na web. APIs governamentais podem:
- Mudar endpoints sem aviso prévio
- Implementar ou remover autenticação
- Ter períodos de indisponibilidade
- Alterar estruturas de dados

**Sempre consulte a documentação oficial** antes de implementar integrações em produção.

Para **atualizações** ou **correções**, contribua com o projeto Cidadão.AI.

---

**Última atualização**: 23 de outubro de 2025
**Compiled by**: Anderson Henrique da Silva
**Licença**: CC BY 4.0
