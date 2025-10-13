# 🎯 Sprint Plan - 2025-10-13

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Data**: 2025-10-13 07:15:00 -03:00
**Duração Estimada**: 2h 15min (135 minutos)
**Status**: 🚀 PRONTO PARA EXECUÇÃO

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [FASE 0: Organização do Workspace](#fase-0-organização-do-workspace)
3. [SPRINT 1: Federal APIs - Correção de Bugs](#sprint-1-federal-apis---correção-de-bugs)
4. [SPRINT 2: Federal APIs - REST Endpoints](#sprint-2-federal-apis---rest-endpoints)
5. [SPRINT 3: Warm-up Job para Métricas](#sprint-3-warm-up-job-para-métricas)
6. [SPRINT 4: Alertas Prometheus](#sprint-4-alertas-prometheus)
7. [SPRINT 5: Validação Final e Documentação](#sprint-5-validação-final-e-documentação)
8. [Critérios de Sucesso](#critérios-de-sucesso)

---

## 🎯 Visão Geral

### Objetivo Principal
Transformar o sistema de monitoramento de infraestrutura básica em produção completa, com Federal APIs funcionais, métricas em tempo real, e alertas configurados.

### Contexto
- ✅ Stack de monitoramento (Prometheus + Grafana) testado e funcional
- ✅ Dashboard Federal APIs criado com 17 painéis
- ✅ 12 métricas instrumentadas no código
- ⚠️ Bugs identificados: IBGE (Pydantic), INEP (método faltando), DataSUS (403/404)
- ⚠️ Métricas não populadas (processo separado)

### Entregas Esperadas
1. Workspace organizado (testes, scripts, documentação)
2. Federal APIs 100% funcionais (bugs corrigidos)
3. REST endpoints públicos para todas as Federal APIs
4. Job de warm-up mantendo métricas atualizadas
5. Alertas Prometheus configurados e testados
6. Dashboard Grafana mostrando dados reais
7. Documentação completa atualizada

---

## 📦 FASE 0: Organização do Workspace

**Duração**: 30 minutos
**Prioridade**: Alta
**Objetivo**: Limpar e organizar estrutura do projeto

### FASE 0.1: Análise e Planejamento (5 min)

#### Checklist Cirúrgico
- [ ] Listar todos os arquivos de teste na raiz
- [ ] Verificar estrutura existente em tests/
- [ ] Verificar estrutura existente em scripts/
- [ ] Identificar arquivos temporários
- [ ] Criar plano de movimentação

#### Arquivos Identificados na Raiz
```
✗ test_celery_beat.py          → tests/manual/celery/
✗ test_celery_persistence.py   → tests/manual/celery/
✗ test_direct_supabase.py      → tests/manual/database/
✗ test_federal_apis.py         → tests/manual/federal_apis/
✗ test_public_endpoint.py      → tests/manual/api/
✗ check_celery_status.py       → scripts/monitoring/
✗ cidadao_ai.db               → .gitignore (já ignorado)
✗ audit_logs/                  → logs/audit/
```

#### Comandos de Análise
```bash
# 1. Verificar arquivos de teste na raiz
find . -maxdepth 1 -name "test_*.py" -o -name "check_*.py"

# 2. Verificar tamanho dos arquivos temporários
du -sh cidadao_ai.db audit_logs/ __pycache__/

# 3. Verificar estrutura de tests/
ls -la tests/

# 4. Verificar estrutura de scripts/
ls -la scripts/
```

---

### FASE 0.2: Mover Arquivos de Teste (10 min)

#### Estrutura de Destino
```
tests/
├── manual/                    # Novos testes manuais
│   ├── __init__.py
│   ├── celery/
│   │   ├── __init__.py
│   │   ├── test_beat.py       # test_celery_beat.py
│   │   └── test_persistence.py # test_celery_persistence.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── test_supabase.py   # test_direct_supabase.py
│   ├── federal_apis/
│   │   ├── __init__.py
│   │   └── test_apis.py       # test_federal_apis.py
│   └── api/
│       ├── __init__.py
│       └── test_public.py     # test_public_endpoint.py
├── unit/                      # Existente
├── integration/               # Existente
└── ...
```

#### Checklist de Execução
- [ ] Criar diretórios tests/manual/ com subdiretórios
- [ ] Criar todos os __init__.py necessários
- [ ] Mover test_celery_beat.py → tests/manual/celery/test_beat.py
- [ ] Mover test_celery_persistence.py → tests/manual/celery/test_persistence.py
- [ ] Mover test_direct_supabase.py → tests/manual/database/test_supabase.py
- [ ] Mover test_federal_apis.py → tests/manual/federal_apis/test_apis.py
- [ ] Mover test_public_endpoint.py → tests/manual/api/test_public.py
- [ ] Atualizar imports se necessário
- [ ] Adicionar README.md em tests/manual/ explicando uso

#### Comandos de Execução
```bash
# 1. Criar estrutura de diretórios
mkdir -p tests/manual/{celery,database,federal_apis,api}

# 2. Criar __init__.py em todos os diretórios
touch tests/manual/__init__.py
touch tests/manual/celery/__init__.py
touch tests/manual/database/__init__.py
touch tests/manual/federal_apis/__init__.py
touch tests/manual/api/__init__.py

# 3. Mover arquivos com git mv (mantém histórico)
git mv test_celery_beat.py tests/manual/celery/test_beat.py
git mv test_celery_persistence.py tests/manual/celery/test_persistence.py
git mv test_direct_supabase.py tests/manual/database/test_supabase.py
git mv test_federal_apis.py tests/manual/federal_apis/test_apis.py
git mv test_public_endpoint.py tests/manual/api/test_public.py

# 4. Verificar movimentação
git status
```

#### Validação
```bash
# Confirmar que arquivos foram movidos
ls -la tests/manual/*/

# Confirmar que raiz está limpa
ls -la *.py | grep test_

# Resultado esperado: nenhum arquivo test_*.py na raiz
```

---

### FASE 0.3: Organizar Scripts (10 min)

#### Checklist de Execução
- [ ] Mover check_celery_status.py → scripts/monitoring/check_celery.py
- [ ] Consolidar scripts de teste de DB em scripts/testing/database/
- [ ] Atualizar scripts/testing/README.md
- [ ] Adicionar comentários nos scripts movidos

#### Comandos de Execução
```bash
# 1. Mover script de monitoramento
git mv check_celery_status.py scripts/monitoring/check_celery.py

# 2. Organizar scripts de teste de DB existentes em scripts/
mkdir -p scripts/testing/database
git mv scripts/test_db_connection.py scripts/testing/database/
git mv scripts/test_auth_db.py scripts/testing/database/
git mv scripts/simple_db_test.py scripts/testing/database/
git mv scripts/test_supabase_connection.py scripts/testing/database/

# 3. Verificar
ls -la scripts/monitoring/
ls -la scripts/testing/database/
```

---

### FASE 0.4: Limpar Arquivos Temporários (5 min)

#### Checklist de Execução
- [ ] Mover audit_logs/ → logs/audit/
- [ ] Adicionar cidadao_ai.db ao .gitignore se não estiver
- [ ] Remover todos os __pycache__ recursivamente
- [ ] Remover .pytest_cache se houver
- [ ] Verificar .coverage não está commitado

#### Comandos de Execução
```bash
# 1. Mover audit logs
mkdir -p logs/audit
mv audit_logs/* logs/audit/ 2>/dev/null || true
rmdir audit_logs

# 2. Verificar .gitignore
grep -q "cidadao_ai.db" .gitignore || echo "cidadao_ai.db" >> .gitignore
grep -q "__pycache__" .gitignore || echo "__pycache__/" >> .gitignore
grep -q ".pytest_cache" .gitignore || echo ".pytest_cache/" >> .gitignore

# 3. Limpar pycache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# 4. Verificar status git
git status
```

#### Validação
```bash
# Confirmar limpeza
ls -la | grep -E "(pycache|pytest_cache|audit_logs)"
# Resultado esperado: nada encontrado
```

---

### FASE 0.5: Commit de Organização (5 min)

#### Checklist de Commit
- [ ] Revisar todas as mudanças com git status
- [ ] Verificar que todos os testes movidos estão tracked
- [ ] Criar commit descritivo
- [ ] Atualizar README.md com nova estrutura

#### Comandos
```bash
# 1. Verificar mudanças
git status

# 2. Adicionar novos arquivos
git add tests/manual/
git add scripts/testing/database/
git add scripts/monitoring/check_celery.py

# 3. Commit
git commit -m "refactor: organize workspace structure

Move test files to dedicated directories:
- Manual tests moved to tests/manual/ with categorization
- Celery tests → tests/manual/celery/
- Database tests → tests/manual/database/
- Federal API tests → tests/manual/federal_apis/
- API tests → tests/manual/api/

Organize scripts:
- Monitoring scripts consolidated in scripts/monitoring/
- Testing scripts organized in scripts/testing/database/

Clean temporary files:
- Move audit logs to logs/audit/
- Remove __pycache__ and .pytest_cache
- Update .gitignore for temporary files

Improves project maintainability and clarity."

# 4. Verificar commit
git log -1 --stat
```

---

## 🐛 SPRINT 1: Federal APIs - Correção de Bugs

**Duração**: 40 minutos
**Prioridade**: Crítica
**Objetivo**: Resolver todos os bugs identificados no teste de monitoramento

### Contexto dos Bugs

#### BUG 1: IBGE - Pydantic Validation Error
```
ValidationError: 1 validation error for IBGELocation
id
  Input should be a valid string [type=string_type, input_value=11, input_type=int]
```

**Causa**: API do IBGE retorna IDs como integers, mas modelo Pydantic espera string.

**Arquivo**: `src/services/transparency_apis/federal_apis/ibge_client.py`

**Linha**: Models de resposta (IBGELocation, IBGEMunicipality, etc.)

---

#### BUG 2: INEP - Método Não Implementado
```
AttributeError: 'INEPClient' object has no attribute 'search_institutions'
```

**Causa**: Método search_institutions não existe na classe INEPClient.

**Arquivo**: `src/services/transparency_apis/federal_apis/inep_client.py`

**Método Faltando**: `async def search_institutions(self, state: str, limit: int)`

---

#### BUG 3: DataSUS - Endpoints Retornam 403/404
```
2/4 operações bem-sucedidas
403 Forbidden em alguns endpoints
404 Not Found em outros
```

**Causa**: Endpoints podem estar incorretos ou precisar autenticação especial.

**Arquivo**: `src/services/transparency_apis/federal_apis/datasus_client.py`

**Investigação necessária**: Verificar documentação oficial da API DataSUS.

---

### SPRINT 1.1: Corrigir IBGE Pydantic Validation (15 min)

#### Checklist Cirúrgico
- [ ] Ler arquivo ibge_client.py completo
- [ ] Identificar todos os modelos Pydantic
- [ ] Verificar tipos dos campos `id`
- [ ] Alterar Field com coerção int → str
- [ ] Adicionar validator personalizado se necessário
- [ ] Testar com dados reais da API
- [ ] Atualizar testes unitários

#### Implementação Detalhada

**Passo 1: Ler modelo atual**
```bash
# Ver modelos Pydantic no arquivo
grep -A 10 "class IBGE" src/services/transparency_apis/federal_apis/ibge_client.py
```

**Passo 2: Identificar problema**
```python
# Modelo atual (errado):
class IBGELocation(BaseModel):
    id: str  # API retorna int, mas esperamos str
    nome: str
```

**Passo 3: Solução 1 - Field com validator**
```python
from pydantic import BaseModel, Field, field_validator

class IBGELocation(BaseModel):
    id: str = Field(..., description="ID do estado/município")
    nome: str

    @field_validator('id', mode='before')
    @classmethod
    def coerce_id_to_str(cls, v):
        """Convert integer IDs from IBGE API to strings."""
        return str(v) if isinstance(v, int) else v
```

**Passo 4: Solução 2 - Union type (alternativa)**
```python
from typing import Union

class IBGELocation(BaseModel):
    id: Union[str, int]  # Aceita ambos
    nome: str

    @field_validator('id', mode='after')
    @classmethod
    def ensure_str(cls, v):
        return str(v)
```

#### Arquivos a Modificar
```
src/services/transparency_apis/federal_apis/ibge_client.py
└── Models:
    ├── IBGELocation
    ├── IBGEMunicipality
    ├── IBGEState
    └── Qualquer outro com campo 'id'
```

#### Comandos de Teste
```bash
# 1. Testar IBGE client isoladamente
python -c "
import asyncio
from src.services.transparency_apis.federal_apis.ibge_client import IBGEClient

async def test():
    async with IBGEClient() as client:
        states = await client.get_states()
        print(f'✅ States: {len(states)}')

        munis = await client.get_municipalities('33')
        print(f'✅ Municipalities: {len(munis)}')

asyncio.run(test())
"

# 2. Rodar teste manual movido
python -m pytest tests/manual/federal_apis/test_apis.py::test_ibge -v
```

#### Validação de Sucesso
- [ ] `get_states()` retorna lista sem erro
- [ ] `get_municipalities()` funciona para todos os estados
- [ ] `get_population()` não lança ValidationError
- [ ] Testes passam sem warnings

---

### SPRINT 1.2: Implementar INEP search_institutions (15 min)

#### Checklist Cirúrgico
- [ ] Ler documentação da API INEP
- [ ] Verificar endpoints disponíveis
- [ ] Implementar método search_institutions
- [ ] Adicionar modelo de resposta Pydantic
- [ ] Instrumentar com métricas Prometheus
- [ ] Adicionar cache com TTL
- [ ] Testar com dados reais
- [ ] Atualizar docstring

#### Implementação Detalhada

**Passo 1: Pesquisar endpoint INEP**
```bash
# Verificar base_url e endpoints existentes
grep -n "base_url\|endpoint" src/services/transparency_apis/federal_apis/inep_client.py
```

**Passo 2: Analisar métodos existentes**
```python
# Ver como outros métodos estão implementados
# Exemplo de get_education_indicators para usar como template
```

**Passo 3: Implementar método search_institutions**
```python
async def search_institutions(
    self,
    state: Optional[str] = None,
    city: Optional[str] = None,
    name: Optional[str] = None,
    limit: int = 20,
    page: int = 1
) -> Dict[str, Any]:
    """
    Search educational institutions.

    Args:
        state: State code (UF) - e.g., 'RJ', 'SP'
        city: City name
        name: Institution name (partial match)
        limit: Max results per page (default: 20)
        page: Page number (default: 1)

    Returns:
        Dict with:
            - total: Total institutions found
            - page: Current page
            - limit: Results per page
            - results: List of institutions

    Example:
        >>> async with INEPClient() as client:
        >>>     results = await client.search_institutions(state="RJ", limit=10)
        >>>     print(f"Found {results['total']} institutions")
    """
    endpoint = "/instituicoes"  # Verificar endpoint real na documentação

    params = {
        "limit": limit,
        "page": page
    }

    if state:
        params["uf"] = state.upper()
    if city:
        params["municipio"] = city
    if name:
        params["nome"] = name

    # Usar método _make_request existente
    response = await self._make_request(
        method="GET",
        endpoint=endpoint,
        params=params
    )

    return {
        "total": response.get("total", 0),
        "page": page,
        "limit": limit,
        "results": response.get("data", [])
    }
```

**Passo 4: Adicionar modelo Pydantic (opcional)**
```python
class INEPInstitution(BaseModel):
    """Educational institution data model."""
    codigo: str
    nome: str
    uf: str
    municipio: str
    rede: Optional[str] = None  # pública/privada
    tipo: Optional[str] = None  # federal/estadual/municipal
    dependencia: Optional[str] = None
```

#### Arquivos a Modificar
```
src/services/transparency_apis/federal_apis/inep_client.py
└── Adicionar:
    ├── search_institutions() method
    └── INEPInstitution model (opcional)
```

#### Comandos de Teste
```bash
# 1. Testar método novo
python -c "
import asyncio
from src.services.transparency_apis.federal_apis.inep_client import INEPClient

async def test():
    async with INEPClient() as client:
        results = await client.search_institutions(state='RJ', limit=5)
        print(f'✅ Institutions found: {results[\"total\"]}')
        print(f'✅ Results: {len(results[\"results\"])}')

asyncio.run(test())
"

# 2. Rodar teste manual
python -m pytest tests/manual/federal_apis/test_apis.py::test_inep -v
```

#### Validação de Sucesso
- [ ] Método search_institutions existe e não lança AttributeError
- [ ] Retorna estrutura de dados esperada
- [ ] Funciona com diferentes combinações de parâmetros
- [ ] Métricas Prometheus são registradas
- [ ] Testes passam

---

### SPRINT 1.3: Investigar e Corrigir DataSUS (10 min)

#### Checklist Cirúrgico
- [ ] Ler erro completo dos testes anteriores
- [ ] Verificar endpoints que falharam (403/404)
- [ ] Pesquisar documentação oficial DataSUS
- [ ] Verificar se precisa autenticação especial
- [ ] Ajustar endpoints ou parâmetros
- [ ] Adicionar tratamento de erro específico
- [ ] Testar com dados reais
- [ ] Documentar limitações conhecidas

#### Investigação Detalhada

**Passo 1: Analisar logs do teste anterior**
```bash
# Revisar MONITORING_TEST_RESULTS.md
grep -A 5 "DataSUS" MONITORING_TEST_RESULTS.md
```

**Passo 2: Identificar endpoints problemáticos**
```python
# Ver quais endpoints retornaram 403/404
# Provavelmente:
# - get_health_indicators() → 403
# - get_hospital_data() → 404
```

**Passo 3: Pesquisar documentação**
```bash
# URLs de referência DataSUS:
# - https://datasus.saude.gov.br/
# - http://tabnet.datasus.gov.br/
# - API docs (se existir)
```

**Passo 4: Implementar tratamento de erro robusto**
```python
async def get_health_indicators(self, state_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Get health indicators.

    Note: This endpoint may have restricted access.
    Returns cached or mock data if API returns 403/404.
    """
    try:
        endpoint = "/indicadores-saude"
        params = {"uf": state_code} if state_code else {}

        response = await self._make_request(
            method="GET",
            endpoint=endpoint,
            params=params
        )
        return response

    except HTTPStatusError as e:
        if e.response.status_code in (403, 404):
            # Log warning but don't fail
            logger.warning(
                f"DataSUS endpoint restricted: {endpoint} "
                f"(status {e.response.status_code})"
            )

            # Return structure with limitation note
            return {
                "status": "limited_access",
                "message": "Endpoint requires special authorization",
                "state_code": state_code,
                "indicators": []
            }
        raise
```

**Passo 5: Documentar limitações**
```python
# Adicionar ao docstring da classe:
"""
DataSUS Client - Brazilian Health Data System

Known Limitations:
- Some endpoints require special authorization (403)
- Hospital data endpoint may be unavailable (404)
- Recommend using search_datasets() for reliable access
"""
```

#### Arquivos a Modificar
```
src/services/transparency_apis/federal_apis/datasus_client.py
└── Métodos a ajustar:
    ├── get_health_indicators()
    ├── get_hospital_data() (se existir)
    └── Adicionar error handling robusto
```

#### Comandos de Teste
```bash
# 1. Testar endpoints conhecidos
python -c "
import asyncio
from src.services.transparency_apis.federal_apis.datasus_client import DataSUSClient

async def test():
    async with DataSUSClient() as client:
        # Teste search (sabemos que funciona)
        datasets = await client.search_datasets('saúde', limit=5)
        print(f'✅ Datasets: {datasets.get(\"result\", {}).get(\"count\", 0)}')

        # Teste indicators (pode retornar limited_access)
        indicators = await client.get_health_indicators(state_code='RJ')
        print(f'✅ Indicators status: {indicators.get(\"status\", \"ok\")}')

asyncio.run(test())
"

# 2. Rodar teste manual completo
python -m pytest tests/manual/federal_apis/test_apis.py::test_datasus -v
```

#### Validação de Sucesso
- [ ] Nenhum endpoint lança exceção não tratada
- [ ] 403/404 são tratados graciosamente
- [ ] Retorna estrutura de dados consistente
- [ ] Logs indicam claramente limitações
- [ ] Testes passam sem falhas críticas

---

### SPRINT 1.4: Commit de Correções (5 min)

#### Checklist de Commit
- [ ] Rodar todos os testes das Federal APIs
- [ ] Verificar que não quebrou nada existente
- [ ] Verificar cobertura de testes se aumentou
- [ ] Criar commit descritivo
- [ ] Atualizar CHANGELOG (se existir)

#### Comandos
```bash
# 1. Rodar testes completos das Federal APIs
python -m pytest tests/manual/federal_apis/ -v

# 2. Rodar testes unitários se existirem
python -m pytest tests/unit/services/transparency_apis/ -v --cov

# 3. Verificar mudanças
git status
git diff

# 4. Commit
git add src/services/transparency_apis/federal_apis/

git commit -m "fix(federal-apis): resolve critical bugs in IBGE, INEP, and DataSUS clients

IBGE Client:
- Fix Pydantic validation error for integer IDs
- Add field validator to coerce int to str
- Update IBGELocation, IBGEMunicipality, IBGEState models
- All endpoints now work without ValidationError

INEP Client:
- Implement missing search_institutions method
- Add support for filtering by state, city, name
- Include pagination parameters (limit, page)
- Add comprehensive docstring with examples

DataSUS Client:
- Add robust error handling for 403/404 responses
- Return graceful degradation for restricted endpoints
- Document known API limitations
- Prevent exceptions from blocking metrics collection

Testing:
- All Federal API manual tests now pass
- Verified with real API calls to production endpoints

Related to: MONITORING_TEST_RESULTS.md findings"

# 5. Verificar commit
git log -1 --stat
```

---

## 🔌 SPRINT 2: Federal APIs - REST Endpoints

**Duração**: 30 minutos
**Prioridade**: Alta
**Objetivo**: Expor Federal APIs via REST para gerar métricas e facilitar uso externo

### Contexto
Atualmente as Federal APIs são apenas clientes internos. Precisamos criar endpoints REST públicos que:
1. Permitam acesso via HTTP
2. Gerem métricas automaticamente quando chamados
3. Facilitem testes e uso externo
4. Mantenham mesma estrutura de resposta

### Estrutura de Endpoints

```
POST /api/v1/federal/ibge/states
POST /api/v1/federal/ibge/municipalities
POST /api/v1/federal/ibge/population

POST /api/v1/federal/datasus/search
POST /api/v1/federal/datasus/indicators

POST /api/v1/federal/inep/search-institutions
POST /api/v1/federal/inep/indicators
```

---

### SPRINT 2.1: Criar Arquivo de Rotas (10 min)

#### Checklist Cirúrgico
- [ ] Criar arquivo src/api/routes/federal_apis.py
- [ ] Importar APIRouter do FastAPI
- [ ] Importar clientes das Federal APIs
- [ ] Definir modelos Pydantic de request/response
- [ ] Adicionar tags para documentação OpenAPI
- [ ] Implementar endpoints básicos
- [ ] Adicionar tratamento de erros

#### Implementação Detalhada

**Passo 1: Criar arquivo base**
```python
"""
Federal APIs REST Endpoints

Exposes Brazilian government APIs as REST endpoints.
Generates Prometheus metrics automatically on each call.

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brasil
Date: 2025-10-13
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.services.transparency_apis.federal_apis.ibge_client import IBGEClient
from src.services.transparency_apis.federal_apis.datasus_client import DataSUSClient
from src.services.transparency_apis.federal_apis.inep_client import INEPClient

router = APIRouter(
    prefix="/api/v1/federal",
    tags=["Federal APIs"]
)
```

**Passo 2: Definir modelos de request**
```python
# Request Models
class IBGEMunicipalitiesRequest(BaseModel):
    """Request model for IBGE municipalities."""
    state_code: str = Field(..., description="State code (2 digits)", example="33")

class IBGEPopulationRequest(BaseModel):
    """Request model for IBGE population data."""
    state_code: Optional[str] = Field(None, description="State code (2 digits)", example="33")
    municipality_code: Optional[str] = Field(None, description="Municipality code", example="3304557")

class DataSUSSearchRequest(BaseModel):
    """Request model for DataSUS search."""
    query: str = Field(..., description="Search query", example="saúde")
    limit: int = Field(10, ge=1, le=100, description="Max results")

class DataSUSIndicatorsRequest(BaseModel):
    """Request model for DataSUS health indicators."""
    state_code: Optional[str] = Field(None, description="State code (UF)", example="RJ")

class INEPSearchRequest(BaseModel):
    """Request model for INEP institution search."""
    state: Optional[str] = Field(None, description="State code (UF)", example="RJ")
    city: Optional[str] = Field(None, description="City name", example="Rio de Janeiro")
    name: Optional[str] = Field(None, description="Institution name", example="UFRJ")
    limit: int = Field(20, ge=1, le=100, description="Max results")
    page: int = Field(1, ge=1, description="Page number")

class INEPIndicatorsRequest(BaseModel):
    """Request model for INEP education indicators."""
    state: Optional[str] = Field(None, description="State code (UF)", example="RJ")
    year: Optional[int] = Field(None, description="Year", example=2023)
```

**Passo 3: Implementar endpoints IBGE**
```python
@router.get(
    "/ibge/states",
    summary="Get Brazilian States",
    description="Retrieve all Brazilian states from IBGE API"
)
async def get_ibge_states() -> Dict[str, Any]:
    """Get all Brazilian states."""
    try:
        async with IBGEClient() as client:
            states = await client.get_states()
            return {
                "success": True,
                "total": len(states),
                "data": states
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/ibge/municipalities",
    summary="Get Municipalities by State",
    description="Retrieve municipalities for a specific state"
)
async def get_ibge_municipalities(request: IBGEMunicipalitiesRequest) -> Dict[str, Any]:
    """Get municipalities for a state."""
    try:
        async with IBGEClient() as client:
            municipalities = await client.get_municipalities(state_code=request.state_code)
            return {
                "success": True,
                "state_code": request.state_code,
                "total": len(municipalities),
                "data": municipalities
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/ibge/population",
    summary="Get Population Data",
    description="Retrieve population data from IBGE"
)
async def get_ibge_population(request: IBGEPopulationRequest) -> Dict[str, Any]:
    """Get population data."""
    try:
        async with IBGEClient() as client:
            population = await client.get_population(
                state_code=request.state_code,
                municipality_code=request.municipality_code
            )
            return {
                "success": True,
                "state_code": request.state_code,
                "municipality_code": request.municipality_code,
                "data": population
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Arquivo a Criar
```
src/api/routes/federal_apis.py  (novo arquivo ~300 linhas)
```

---

### SPRINT 2.2: Implementar Endpoints DataSUS e INEP (10 min)

#### Implementação Detalhada

**Passo 1: Endpoints DataSUS**
```python
@router.post(
    "/datasus/search",
    summary="Search DataSUS Datasets",
    description="Search health datasets in DataSUS"
)
async def search_datasus_datasets(request: DataSUSSearchRequest) -> Dict[str, Any]:
    """Search DataSUS datasets."""
    try:
        async with DataSUSClient() as client:
            results = await client.search_datasets(
                query=request.query,
                limit=request.limit
            )
            return {
                "success": True,
                "query": request.query,
                "data": results
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/datasus/indicators",
    summary="Get Health Indicators",
    description="Retrieve health indicators from DataSUS"
)
async def get_datasus_indicators(request: DataSUSIndicatorsRequest) -> Dict[str, Any]:
    """Get health indicators."""
    try:
        async with DataSUSClient() as client:
            indicators = await client.get_health_indicators(
                state_code=request.state_code
            )
            return {
                "success": True,
                "state_code": request.state_code,
                "data": indicators
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Passo 2: Endpoints INEP**
```python
@router.post(
    "/inep/search-institutions",
    summary="Search Educational Institutions",
    description="Search institutions in INEP database"
)
async def search_inep_institutions(request: INEPSearchRequest) -> Dict[str, Any]:
    """Search educational institutions."""
    try:
        async with INEPClient() as client:
            results = await client.search_institutions(
                state=request.state,
                city=request.city,
                name=request.name,
                limit=request.limit,
                page=request.page
            )
            return {
                "success": True,
                "filters": {
                    "state": request.state,
                    "city": request.city,
                    "name": request.name
                },
                "pagination": {
                    "page": request.page,
                    "limit": request.limit
                },
                "data": results
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/inep/indicators",
    summary="Get Education Indicators",
    description="Retrieve education indicators from INEP"
)
async def get_inep_indicators(request: INEPIndicatorsRequest) -> Dict[str, Any]:
    """Get education indicators."""
    try:
        async with INEPClient() as client:
            indicators = await client.get_education_indicators(
                state=request.state,
                year=request.year
            )
            return {
                "success": True,
                "state": request.state,
                "year": request.year,
                "data": indicators
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### SPRINT 2.3: Registrar Router no App Principal (5 min)

#### Checklist Cirúrgico
- [ ] Abrir src/api/app.py
- [ ] Importar router de federal_apis
- [ ] Registrar router no app FastAPI
- [ ] Verificar ordem de registro (antes de outros)
- [ ] Testar que endpoints aparecem no /docs

#### Implementação

**Passo 1: Localizar imports no app.py**
```bash
grep -n "from.*routes import" src/api/app.py
```

**Passo 2: Adicionar import**
```python
# Em src/api/app.py, na seção de imports
from src.api.routes import federal_apis
```

**Passo 3: Registrar router**
```python
# Na função create_app() ou onde routers são registrados
app.include_router(federal_apis.router)
```

**Passo 4: Verificar ordem**
```python
# Ordem recomendada:
app.include_router(federal_apis.router)  # Federal APIs primeiro
app.include_router(agents.router)        # Depois agentes
app.include_router(chat.router)          # Depois chat
# ...outros routers
```

#### Arquivos a Modificar
```
src/api/app.py
└── Adicionar:
    ├── Import: from src.api.routes import federal_apis
    └── Register: app.include_router(federal_apis.router)
```

---

### SPRINT 2.4: Testar Endpoints (5 min)

#### Checklist de Testes
- [ ] Iniciar backend localmente
- [ ] Acessar /docs e verificar novos endpoints
- [ ] Testar cada endpoint via Swagger UI
- [ ] Testar via curl ou httpie
- [ ] Verificar métricas em /health/metrics
- [ ] Verificar Prometheus coletou métricas

#### Comandos de Teste

**Passo 1: Iniciar backend**
```bash
# Se ainda não está rodando
make run-dev
# OU
python -m src.api.app
```

**Passo 2: Testar endpoints via curl**
```bash
# 1. IBGE - Get States
curl -X GET http://localhost:8000/api/v1/federal/ibge/states

# 2. IBGE - Get Municipalities
curl -X POST http://localhost:8000/api/v1/federal/ibge/municipalities \
  -H "Content-Type: application/json" \
  -d '{"state_code": "33"}'

# 3. DataSUS - Search
curl -X POST http://localhost:8000/api/v1/federal/datasus/search \
  -H "Content-Type: application/json" \
  -d '{"query": "saúde", "limit": 5}'

# 4. INEP - Search Institutions
curl -X POST http://localhost:8000/api/v1/federal/inep/search-institutions \
  -H "Content-Type: application/json" \
  -d '{"state": "RJ", "limit": 5}'
```

**Passo 3: Verificar métricas**
```bash
# Verificar que métricas foram geradas
curl http://localhost:8000/health/metrics | grep federal_api

# Deve mostrar:
# federal_api_requests_total{...} 4
# federal_api_request_duration_seconds_count{...} 4
# etc.
```

**Passo 4: Verificar no Prometheus**
```bash
# Abrir Prometheus: http://localhost:9090
# Query: federal_api_requests_total
# Deve mostrar dados!
```

#### Validação de Sucesso
- [ ] Todos os endpoints respondem com 200 OK
- [ ] Dados retornados estão corretos
- [ ] Swagger UI (/docs) mostra endpoints corretamente
- [ ] Métricas aparecem em /health/metrics
- [ ] Prometheus está coletando métricas

---

### SPRINT 2.5: Commit REST Endpoints (5 min)

```bash
git add src/api/routes/federal_apis.py
git add src/api/app.py

git commit -m "feat(api): add REST endpoints for Federal APIs

Expose Federal APIs as public REST endpoints:

IBGE Endpoints:
- GET /api/v1/federal/ibge/states - All Brazilian states
- POST /api/v1/federal/ibge/municipalities - Municipalities by state
- POST /api/v1/federal/ibge/population - Population data

DataSUS Endpoints:
- POST /api/v1/federal/datasus/search - Search health datasets
- POST /api/v1/federal/datasus/indicators - Health indicators

INEP Endpoints:
- POST /api/v1/federal/inep/search-institutions - Search schools/universities
- POST /api/v1/federal/inep/indicators - Education indicators

Features:
- Automatic Prometheus metrics generation on each call
- Comprehensive request/response models with Pydantic
- Error handling with appropriate HTTP status codes
- Full OpenAPI documentation in Swagger UI
- Async/await for optimal performance

Benefits:
- Enables dashboard metrics population
- Facilitates external integrations
- Provides consistent API interface
- Improves system observability

Related to: MONITORING_TEST_RESULTS.md recommendations"
```

---

## ⚡ SPRINT 3: Warm-up Job para Métricas

**Duração**: 20 minutos
**Prioridade**: Média
**Objetivo**: Criar job agendado que mantém métricas sempre atualizadas

### Contexto
Com os REST endpoints implementados, precisamos de um job que:
1. Chama os endpoints periodicamente
2. Mantém métricas sempre populadas
3. Valida disponibilidade das APIs
4. Pode rodar como cronjob ou background task

---

### SPRINT 3.1: Criar Script Warm-up (15 min)

#### Checklist Cirúrgico
- [ ] Criar arquivo scripts/monitoring/warmup_federal_apis.py
- [ ] Importar httpx para chamadas HTTP
- [ ] Implementar função de warm-up para cada API
- [ ] Adicionar logging detalhado
- [ ] Adicionar tratamento de erros
- [ ] Adicionar métricas de saúde do warm-up
- [ ] Criar função main com schedule

#### Implementação Detalhada

```python
#!/usr/bin/env python3
"""
Federal APIs Warm-up Job

Periodically calls Federal API endpoints to:
- Keep metrics updated in Prometheus
- Validate API availability
- Pre-warm caches

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brasil
Date: 2025-10-13

Usage:
    # Run once
    python scripts/monitoring/warmup_federal_apis.py

    # Run continuously (every 5 minutes)
    python scripts/monitoring/warmup_federal_apis.py --daemon

    # Custom interval
    python scripts/monitoring/warmup_federal_apis.py --daemon --interval 300
"""

import asyncio
import logging
import sys
import time
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

import httpx
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Backend URL (adjust if needed)
BACKEND_URL = "http://localhost:8000"

# Warm-up endpoints to call
WARMUP_ENDPOINTS = [
    {
        "name": "IBGE States",
        "method": "GET",
        "url": f"{BACKEND_URL}/api/v1/federal/ibge/states",
        "data": None
    },
    {
        "name": "IBGE Municipalities (RJ)",
        "method": "POST",
        "url": f"{BACKEND_URL}/api/v1/federal/ibge/municipalities",
        "data": {"state_code": "33"}
    },
    {
        "name": "DataSUS Search",
        "method": "POST",
        "url": f"{BACKEND_URL}/api/v1/federal/datasus/search",
        "data": {"query": "saúde", "limit": 5}
    },
    {
        "name": "INEP Search (RJ)",
        "method": "POST",
        "url": f"{BACKEND_URL}/api/v1/federal/inep/search-institutions",
        "data": {"state": "RJ", "limit": 5}
    }
]


async def call_endpoint(
    client: httpx.AsyncClient,
    endpoint: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Call a single endpoint and return result.

    Args:
        client: Async HTTP client
        endpoint: Endpoint configuration

    Returns:
        Dict with result details
    """
    start_time = time.time()

    try:
        if endpoint["method"] == "GET":
            response = await client.get(endpoint["url"], timeout=10.0)
        else:
            response = await client.post(
                endpoint["url"],
                json=endpoint["data"],
                timeout=10.0
            )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            logger.info(
                f"✅ {endpoint['name']}: {response.status_code} "
                f"({elapsed:.2f}s)"
            )
            return {
                "name": endpoint["name"],
                "status": "success",
                "status_code": response.status_code,
                "elapsed": elapsed
            }
        else:
            logger.warning(
                f"⚠️  {endpoint['name']}: {response.status_code} "
                f"({elapsed:.2f}s)"
            )
            return {
                "name": endpoint["name"],
                "status": "error",
                "status_code": response.status_code,
                "elapsed": elapsed
            }

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ {endpoint['name']}: {str(e)} ({elapsed:.2f}s)")
        return {
            "name": endpoint["name"],
            "status": "failed",
            "error": str(e),
            "elapsed": elapsed
        }


async def warmup_cycle() -> Dict[str, Any]:
    """
    Execute one warmup cycle calling all endpoints.

    Returns:
        Summary of warmup cycle
    """
    logger.info("=" * 60)
    logger.info(f"🔥 Starting Federal APIs Warm-up - {datetime.now()}")
    logger.info("=" * 60)

    results: List[Dict[str, Any]] = []

    async with httpx.AsyncClient() as client:
        # Call all endpoints
        for endpoint in WARMUP_ENDPOINTS:
            result = await call_endpoint(client, endpoint)
            results.append(result)
            # Small delay between calls
            await asyncio.sleep(0.5)

    # Calculate summary
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")
    failed_count = sum(1 for r in results if r["status"] == "failed")
    total_time = sum(r["elapsed"] for r in results)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_endpoints": len(results),
        "success": success_count,
        "errors": error_count,
        "failed": failed_count,
        "total_time": total_time,
        "results": results
    }

    logger.info("=" * 60)
    logger.info(f"📊 Warmup Summary:")
    logger.info(f"   ✅ Success: {success_count}/{len(results)}")
    logger.info(f"   ⚠️  Errors:  {error_count}/{len(results)}")
    logger.info(f"   ❌ Failed:  {failed_count}/{len(results)}")
    logger.info(f"   ⏱️  Total:   {total_time:.2f}s")
    logger.info("=" * 60)

    return summary


async def daemon_mode(interval: int = 300):
    """
    Run warmup in daemon mode with periodic execution.

    Args:
        interval: Seconds between warmup cycles (default: 300 = 5 min)
    """
    logger.info(f"🚀 Starting daemon mode (interval: {interval}s)")

    cycle_count = 0

    while True:
        try:
            cycle_count += 1
            logger.info(f"\n🔄 Cycle #{cycle_count}")

            await warmup_cycle()

            logger.info(f"😴 Sleeping for {interval}s until next cycle...\n")
            await asyncio.sleep(interval)

        except KeyboardInterrupt:
            logger.info("\n⚠️  Interrupted by user. Exiting...")
            break
        except Exception as e:
            logger.error(f"❌ Error in daemon loop: {e}")
            logger.info(f"😴 Waiting {interval}s before retry...")
            await asyncio.sleep(interval)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Federal APIs Warm-up Job")
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run continuously in daemon mode"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval between cycles in seconds (default: 300)"
    )
    parser.add_argument(
        "--backend-url",
        type=str,
        default="http://localhost:8000",
        help="Backend URL (default: http://localhost:8000)"
    )

    args = parser.parse_args()

    # Update backend URL if provided
    if args.backend_url != "http://localhost:8000":
        global BACKEND_URL
        BACKEND_URL = args.backend_url
        # Update all endpoint URLs
        for endpoint in WARMUP_ENDPOINTS:
            endpoint["url"] = endpoint["url"].replace(
                "http://localhost:8000",
                args.backend_url
            )

    if args.daemon:
        await daemon_mode(interval=args.interval)
    else:
        await warmup_cycle()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")
        sys.exit(0)
```

#### Arquivo a Criar
```
scripts/monitoring/warmup_federal_apis.py  (~250 linhas)
```

---

### SPRINT 3.2: Criar Arquivo Systemd (opcional, 5 min)

#### Para rodar como serviço Linux

```bash
# Criar arquivo /etc/systemd/system/cidadao-warmup.service
sudo nano /etc/systemd/system/cidadao-warmup.service
```

```ini
[Unit]
Description=Cidadão.AI Federal APIs Warm-up Job
After=network.target

[Service]
Type=simple
User=anderson-henrique
WorkingDirectory=/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend
ExecStart=/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend/venv/bin/python \
    scripts/monitoring/warmup_federal_apis.py --daemon --interval 300
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar e iniciar serviço
sudo systemctl enable cidadao-warmup.service
sudo systemctl start cidadao-warmup.service
sudo systemctl status cidadao-warmup.service
```

---

### SPRINT 3.3: Testar Warm-up (5 min)

#### Comandos de Teste

```bash
# 1. Rodar uma vez
python scripts/monitoring/warmup_federal_apis.py

# Deve mostrar:
# ✅ IBGE States: 200 (0.45s)
# ✅ IBGE Municipalities (RJ): 200 (0.32s)
# ✅ DataSUS Search: 200 (0.78s)
# ✅ INEP Search (RJ): 200 (0.56s)

# 2. Testar modo daemon por 1 minuto
timeout 60 python scripts/monitoring/warmup_federal_apis.py --daemon --interval 30

# 3. Verificar métricas geradas
curl http://localhost:8000/health/metrics | grep federal_api_requests_total

# 4. Verificar no Grafana
# Abrir http://localhost:3000
# Dashboard Federal APIs deve mostrar dados agora!
```

#### Validação de Sucesso
- [ ] Script roda sem erros
- [ ] Todos os endpoints são chamados
- [ ] Métricas aparecem em /health/metrics
- [ ] Grafana dashboard mostra dados
- [ ] Prometheus tem métricas crescendo

---

### SPRINT 3.4: Commit Warm-up Job (5 min)

```bash
git add scripts/monitoring/warmup_federal_apis.py

git commit -m "feat(monitoring): add Federal APIs warm-up job

Create automated warm-up job to maintain metrics:

Features:
- Periodically calls all Federal API endpoints
- Keeps Prometheus metrics always updated
- Validates API availability continuously
- Supports one-time and daemon modes

Usage:
  # Run once
  python scripts/monitoring/warmup_federal_apis.py

  # Run continuously (5 min interval)
  python scripts/monitoring/warmup_federal_apis.py --daemon

  # Custom interval
  python scripts/monitoring/warmup_federal_apis.py --daemon --interval 600

Implementation:
- Async HTTP calls with httpx
- Detailed logging with timestamps
- Error handling and retries
- Cycle summary with success/error counts
- Can run as systemd service

Benefits:
- Dashboard always shows current data
- Early detection of API issues
- Pre-warmed caches improve performance
- Automated health monitoring

Related to: MONITORING_TEST_RESULTS.md - Sprint 3"
```

---

## 🔔 SPRINT 4: Alertas Prometheus

**Duração**: 20 minutos
**Prioridade**: Média
**Objetivo**: Configurar regras de alerta para monitoramento proativo

### Contexto
Precisamos de alertas para detectar problemas antes que afetem usuários:
- Taxa de erro elevada (>5%)
- Latência alta (P95 > 5s)
- Taxa de cache baixa (<50%)
- APIs indisponíveis

---

### SPRINT 4.1: Criar Regras de Alerta (10 min)

#### Checklist Cirúrgico
- [ ] Criar arquivo monitoring/prometheus/alerts.yml
- [ ] Definir alertas para taxa de erro
- [ ] Definir alertas para latência
- [ ] Definir alertas para cache
- [ ] Definir alertas para disponibilidade
- [ ] Adicionar labels e annotations
- [ ] Documentar thresholds

#### Implementação Detalhada

```yaml
# monitoring/prometheus/alerts.yml
#
# Prometheus Alert Rules for Cidadão.AI
#
# Author: Anderson Henrique da Silva
# Location: Minas Gerais, Brasil
# Date: 2025-10-13

groups:
  - name: federal_apis_alerts
    interval: 30s
    rules:
      # Alert: High Error Rate
      - alert: FederalAPIHighErrorRate
        expr: |
          (
            sum(rate(federal_api_errors_total[5m])) by (api_name)
            /
            sum(rate(federal_api_requests_total[5m])) by (api_name)
          ) > 0.05
        for: 2m
        labels:
          severity: warning
          component: federal_apis
        annotations:
          summary: "High error rate on {{ $labels.api_name }}"
          description: |
            {{ $labels.api_name }} API has error rate of {{ $value | humanizePercentage }}
            over the last 5 minutes (threshold: 5%).
          runbook_url: https://docs.cidadao.ai/runbooks/high-error-rate

      # Alert: Critical Error Rate
      - alert: FederalAPICriticalErrorRate
        expr: |
          (
            sum(rate(federal_api_errors_total[5m])) by (api_name)
            /
            sum(rate(federal_api_requests_total[5m])) by (api_name)
          ) > 0.25
        for: 1m
        labels:
          severity: critical
          component: federal_apis
        annotations:
          summary: "CRITICAL: {{ $labels.api_name }} failing"
          description: |
            {{ $labels.api_name }} API has error rate of {{ $value | humanizePercentage }}
            over the last 5 minutes (threshold: 25%).
            IMMEDIATE ACTION REQUIRED!
          runbook_url: https://docs.cidadao.ai/runbooks/critical-error-rate

      # Alert: High Latency (P95)
      - alert: FederalAPIHighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(federal_api_request_duration_seconds_bucket[5m])) by (api_name, le)
          ) > 5
        for: 3m
        labels:
          severity: warning
          component: federal_apis
        annotations:
          summary: "High latency on {{ $labels.api_name }}"
          description: |
            {{ $labels.api_name }} API P95 latency is {{ $value | humanizeDuration }}
            (threshold: 5s). Users may experience slow responses.
          runbook_url: https://docs.cidadao.ai/runbooks/high-latency

      # Alert: Very High Latency
      - alert: FederalAPIVeryHighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(federal_api_request_duration_seconds_bucket[5m])) by (api_name, le)
          ) > 10
        for: 1m
        labels:
          severity: critical
          component: federal_apis
        annotations:
          summary: "CRITICAL: Extreme latency on {{ $labels.api_name }}"
          description: |
            {{ $labels.api_name }} API P95 latency is {{ $value | humanizeDuration }}
            (threshold: 10s). Service severely degraded!
          runbook_url: https://docs.cidadao.ai/runbooks/extreme-latency

      # Alert: Low Cache Hit Rate
      - alert: FederalAPILowCacheHitRate
        expr: |
          (
            sum(rate(federal_api_cache_operations_total{operation="hit"}[10m])) by (api_name)
            /
            sum(rate(federal_api_cache_operations_total[10m])) by (api_name)
          ) < 0.50
        for: 5m
        labels:
          severity: info
          component: federal_apis
        annotations:
          summary: "Low cache hit rate on {{ $labels.api_name }}"
          description: |
            {{ $labels.api_name }} cache hit rate is {{ $value | humanizePercentage }}
            (threshold: 50%). Consider adjusting TTL or cache strategy.
          runbook_url: https://docs.cidadao.ai/runbooks/low-cache-hit

      # Alert: API Down
      - alert: FederalAPIDown
        expr: |
          up{job="cidadao-ai-backend"} == 0
        for: 1m
        labels:
          severity: critical
          component: backend
        annotations:
          summary: "Backend API is DOWN"
          description: |
            Backend API ({{ $labels.instance }}) is not responding.
            All Federal APIs are unavailable!
          runbook_url: https://docs.cidadao.ai/runbooks/api-down

      # Alert: High Retry Rate
      - alert: FederalAPIHighRetryRate
        expr: |
          sum(rate(federal_api_retries_total[5m])) by (api_name) > 1
        for: 3m
        labels:
          severity: warning
          component: federal_apis
        annotations:
          summary: "High retry rate on {{ $labels.api_name }}"
          description: |
            {{ $labels.api_name }} is experiencing {{ $value }} retries/sec
            over the last 5 minutes. Upstream API may be unstable.
          runbook_url: https://docs.cidadao.ai/runbooks/high-retry-rate

      # Alert: Excessive Active Requests
      - alert: FederalAPIExcessiveActiveRequests
        expr: |
          federal_api_active_requests > 20
        for: 2m
        labels:
          severity: warning
          component: federal_apis
        annotations:
          summary: "Many concurrent requests to {{ $labels.api_name }}"
          description: |
            {{ $labels.api_name }} has {{ $value }} active requests.
            May indicate slow responses or traffic spike.
          runbook_url: https://docs.cidadao.ai/runbooks/excessive-requests

  - name: system_alerts
    interval: 30s
    rules:
      # Alert: Prometheus Scrape Failures
      - alert: PrometheusScrapeFailing
        expr: |
          up{job="cidadao-ai-backend"} == 0
          or
          up{job="prometheus"} == 0
        for: 2m
        labels:
          severity: critical
          component: monitoring
        annotations:
          summary: "Prometheus cannot scrape {{ $labels.job }}"
          description: |
            Prometheus failed to scrape {{ $labels.job }} at {{ $labels.instance }}
            for more than 2 minutes. Metrics may be stale!
          runbook_url: https://docs.cidadao.ai/runbooks/scrape-failure

      # Alert: Grafana Down
      - alert: GrafanaDown
        expr: |
          up{job="grafana"} == 0
        for: 5m
        labels:
          severity: warning
          component: monitoring
        annotations:
          summary: "Grafana dashboard is DOWN"
          description: |
            Grafana is not responding. Dashboards unavailable.
          runbook_url: https://docs.cidadao.ai/runbooks/grafana-down
```

#### Arquivo a Criar
```
monitoring/prometheus/alerts.yml  (~200 linhas)
```

---

### SPRINT 4.2: Atualizar prometheus.yml (5 min)

#### Verificar que alerts.yml está sendo carregado

```bash
# Verificar se prometheus.yml já tem rule_files
grep -n "rule_files" monitoring/prometheus/prometheus.yml
```

Se não tiver ou não incluir alerts.yml, adicionar:

```yaml
# Em monitoring/prometheus/prometheus.yml
rule_files:
  - "rules/*.yml"
  - "alerts.yml"  # ← Garantir que esta linha existe
```

#### Validar configuração
```bash
# Validar sintaxe do prometheus.yml
docker run --rm -v $(pwd)/monitoring/prometheus:/etc/prometheus \
  prom/prometheus:v2.49.1 \
  promtool check config /etc/prometheus/prometheus.yml

# Deve retornar: SUCCESS
```

---

### SPRINT 4.3: Recarregar Prometheus (3 min)

#### Comandos de Reload

```bash
# Opção 1: Reload via API (recomendado)
curl -X POST http://localhost:9090/-/reload

# Opção 2: Restart container
docker restart cidadao-prometheus

# Opção 3: Docker compose restart
sudo docker-compose -f config/docker/docker-compose.monitoring-minimal.yml restart prometheus
```

#### Validação
```bash
# 1. Verificar que Prometheus recarregou
curl http://localhost:9090/api/v1/status/config | jq '.status'
# Deve retornar: "success"

# 2. Verificar regras carregadas
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].name'
# Deve incluir: "federal_apis_alerts" e "system_alerts"

# 3. Abrir UI do Prometheus
# http://localhost:9090/alerts
# Deve mostrar todos os alertas definidos
```

---

### SPRINT 4.4: Commit Alertas (2 min)

```bash
git add monitoring/prometheus/alerts.yml
git add monitoring/prometheus/prometheus.yml  # se modificado

git commit -m "feat(monitoring): add comprehensive Prometheus alert rules

Configure proactive monitoring with 11 alert rules:

Federal APIs Alerts:
- High Error Rate (>5% for 2min) - WARNING
- Critical Error Rate (>25% for 1min) - CRITICAL
- High Latency P95 (>5s for 3min) - WARNING
- Very High Latency P95 (>10s for 1min) - CRITICAL
- Low Cache Hit Rate (<50% for 5min) - INFO
- High Retry Rate (>1/s for 3min) - WARNING
- Excessive Active Requests (>20 for 2min) - WARNING

System Alerts:
- API Down (>1min) - CRITICAL
- Prometheus Scrape Failing (>2min) - CRITICAL
- Grafana Down (>5min) - WARNING

Features:
- Severity levels: INFO, WARNING, CRITICAL
- Detailed annotations with thresholds
- Runbook URLs for incident response
- Appropriate for expressions to avoid flapping
- Component labels for routing

Next Steps:
- Configure Alertmanager for notifications
- Add Slack/Email integrations
- Create runbook documentation

Related to: MONITORING_TEST_RESULTS.md - Sprint 4"
```

---

## ✅ SPRINT 5: Validação Final e Documentação

**Duração**: 15 minutos
**Prioridade**: Alta
**Objetivo**: Testar tudo end-to-end e documentar

### SPRINT 5.1: Testes End-to-End (10 min)

#### Checklist Completo de Validação

**Backend e APIs**
- [ ] Backend rodando sem erros
- [ ] Todos os endpoints REST respondem
- [ ] Federal APIs não têm bugs (IBGE, INEP, DataSUS)
- [ ] Métricas sendo geradas em /health/metrics

**Monitoramento**
- [ ] Prometheus coletando métricas
- [ ] Grafana mostrando dados no dashboard
- [ ] Alertas carregados no Prometheus
- [ ] Warm-up job populando métricas

**Testes Automatizados**
- [ ] Testes manuais passam (tests/manual/federal_apis/)
- [ ] Cobertura de testes mantida ou aumentada
- [ ] Nenhum teste quebrado por mudanças

#### Comandos de Validação Completa

```bash
# 1. Verificar backend
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/federal/ibge/states | jq '.success'

# 2. Gerar métricas com warm-up
python scripts/monitoring/warmup_federal_apis.py

# 3. Verificar métricas
curl http://localhost:8000/health/metrics | grep federal_api | head -20

# 4. Verificar Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[].health'

# 5. Verificar alertas
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[].name'

# 6. Rodar testes
python -m pytest tests/manual/federal_apis/ -v
python -m pytest tests/unit/services/transparency_apis/ -v --cov

# 7. Verificar no Grafana
# Abrir http://localhost:3000
# Dashboard "Federal APIs Monitoring" deve mostrar dados reais!
```

---

### SPRINT 5.2: Atualizar Documentação (5 min)

#### Arquivos a Atualizar

**1. README.md - Seção de Monitoramento**
```markdown
## 📊 Monitoring & Observability

### Stack
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization dashboards
- **Federal APIs Dashboard**: Real-time monitoring

### Quick Start
```bash
# Start monitoring stack
sudo docker-compose -f config/docker/docker-compose.monitoring-minimal.yml up -d

# Start backend
make run-dev

# Run warm-up job (keeps metrics updated)
python scripts/monitoring/warmup_federal_apis.py --daemon
```

### Accessing Dashboards
- **Grafana**: http://localhost:3000 (admin/cidadao123)
- **Prometheus**: http://localhost:9090
- **Metrics**: http://localhost:8000/health/metrics

### Federal APIs Endpoints
```bash
# IBGE
GET  /api/v1/federal/ibge/states
POST /api/v1/federal/ibge/municipalities
POST /api/v1/federal/ibge/population

# DataSUS
POST /api/v1/federal/datasus/search
POST /api/v1/federal/datasus/indicators

# INEP
POST /api/v1/federal/inep/search-institutions
POST /api/v1/federal/inep/indicators
```

### Alerts Configured
- High error rate (>5%)
- High latency P95 (>5s)
- Low cache hit rate (<50%)
- API unavailability
- Prometheus scrape failures
```

**2. Criar docs/monitoring/README.md**
```markdown
# Monitoring Guide

Complete guide for Cidadão.AI monitoring infrastructure.

## Architecture

```
User Requests
      ↓
Backend API (FastAPI)
      ↓
Federal APIs (IBGE, DataSUS, INEP)
      ↓
Prometheus Metrics
      ↓
Grafana Dashboards
```

## Dashboards

### Federal APIs Monitoring
- **Location**: Grafana > Dashboards > Federal APIs Monitoring
- **UID**: `federal-apis`
- **Panels**: 17 visualization panels

#### Key Metrics
1. **Request Rate**: Requests/sec per API
2. **Error Rate**: Percentage of failed requests
3. **Latency**: P50, P95, P99 response times
4. **Cache Performance**: Hit rate, operations
5. **Retry Rate**: Upstream API stability

## Alerts

### Severity Levels
- **INFO**: Informational, no action required
- **WARNING**: Requires attention, not urgent
- **CRITICAL**: Immediate action required

### Alert Rules

#### FederalAPIHighErrorRate (WARNING)
- **Threshold**: >5% errors for 2 minutes
- **Action**: Check logs, investigate errors

#### FederalAPICriticalErrorRate (CRITICAL)
- **Threshold**: >25% errors for 1 minute
- **Action**: IMMEDIATE - Check backend health, upstream APIs

#### FederalAPIHighLatency (WARNING)
- **Threshold**: P95 >5s for 3 minutes
- **Action**: Check backend performance, database queries

## Warm-up Job

### Purpose
Maintains metrics by periodically calling Federal API endpoints.

### Usage
```bash
# Run once
python scripts/monitoring/warmup_federal_apis.py

# Run continuously (5 min interval)
python scripts/monitoring/warmup_federal_apis.py --daemon

# Custom interval (10 min)
python scripts/monitoring/warmup_federal_apis.py --daemon --interval 600
```

### As Systemd Service
```bash
sudo systemctl enable cidadao-warmup.service
sudo systemctl start cidadao-warmup.service
```

## Troubleshooting

### No data in Grafana
1. Check backend is running: `curl http://localhost:8000/health`
2. Check Prometheus scraping: http://localhost:9090/targets
3. Generate metrics: `python scripts/monitoring/warmup_federal_apis.py`
4. Wait 15-30s for Prometheus to collect

### Alerts always firing
1. Check thresholds are appropriate for your load
2. Adjust `for:` duration in alerts.yml
3. Verify upstream APIs are stable

### High error rate
1. Check backend logs
2. Verify Federal API availability
3. Check network connectivity
4. Review MONITORING_TEST_RESULTS.md for known issues

## Related Files
- `monitoring/prometheus/prometheus.yml` - Scrape config
- `monitoring/prometheus/alerts.yml` - Alert rules
- `monitoring/grafana/dashboards/federal-apis-dashboard.json` - Dashboard
- `scripts/monitoring/warmup_federal_apis.py` - Warm-up job
- `MONITORING_TEST_RESULTS.md` - Test results documentation
```

#### Commit Documentação

```bash
git add README.md
git add docs/monitoring/

git commit -m "docs: update monitoring documentation

Add comprehensive monitoring documentation:

README Updates:
- Add Monitoring & Observability section
- Document quick start commands
- List all Federal API endpoints
- Document configured alerts

New Documentation:
- docs/monitoring/README.md with complete guide
- Architecture diagrams
- Dashboard usage instructions
- Alert severity levels and actions
- Warm-up job documentation
- Troubleshooting guide

Covers:
- Sprint 1-5 implementations
- Federal APIs REST endpoints
- Warm-up job setup and usage
- Alert rules and responses
- Common issues and solutions

Related to: SPRINT_PLAN_2025-10-13.md completion"
```

---

## 🎯 Critérios de Sucesso

### Deve Funcionar
- ✅ Workspace organizado (testes em tests/manual/, scripts organizados)
- ✅ Federal APIs sem bugs (IBGE, INEP, DataSUS funcionando)
- ✅ REST endpoints respondendo corretamente
- ✅ Métricas sendo geradas em /health/metrics
- ✅ Prometheus coletando métricas (targets UP)
- ✅ Grafana mostrando dados no dashboard
- ✅ Warm-up job executando sem erros
- ✅ Alertas carregados no Prometheus
- ✅ Testes passando (manual e unitários)
- ✅ Documentação atualizada

### Métricas de Qualidade
- Cobertura de testes: mantida ou aumentada (target: >80%)
- Zero bugs críticos introduzidos
- Todas as Federal APIs operacionais
- Tempo de resposta P95 < 5s
- Taxa de erro < 5%
- Cache hit rate > 50%

### Entregas Documentadas
- SPRINT_PLAN_2025-10-13.md (este arquivo)
- Commits descritivos em inglês
- README.md atualizado
- docs/monitoring/README.md criado
- MONITORING_TEST_RESULTS.md (já existe)

---

## 📊 Timeline Resumido

| Fase | Descrição | Duração | Status |
|------|-----------|---------|--------|
| FASE 0 | Organização Workspace | 30 min | ⏳ Pendente |
| SPRINT 1 | Correção de Bugs | 40 min | ⏳ Pendente |
| SPRINT 2 | REST Endpoints | 30 min | ⏳ Pendente |
| SPRINT 3 | Warm-up Job | 20 min | ⏳ Pendente |
| SPRINT 4 | Alertas Prometheus | 20 min | ⏳ Pendente |
| SPRINT 5 | Validação e Docs | 15 min | ⏳ Pendente |
| **TOTAL** | | **2h 15min** | **0% Completo** |

---

## 🚀 Como Executar Este Plano

### Pré-requisitos
```bash
# 1. Backend rodando
make run-dev

# 2. Monitoring stack rodando
sudo docker-compose -f config/docker/docker-compose.monitoring-minimal.yml up -d

# 3. Ambiente virtual ativo
source venv/bin/activate
```

### Execução
```bash
# 1. Abrir este plano no editor
code SPRINT_PLAN_2025-10-13.md

# 2. Seguir cada seção sequencialmente
# 3. Marcar checkboxes conforme avança
# 4. Executar comandos listados
# 5. Validar cada etapa antes de próxima
# 6. Fazer commits ao final de cada sprint
```

### Dicas
- ⏱️ Usar timer para manter foco e ritmo
- ✅ Marcar checkboxes conforme completa
- 🔍 Validar cada etapa antes de avançar
- 📝 Fazer commits descritivos (em inglês)
- 🐛 Se encontrar bugs, documentar e continuar
- ⚡ Pedir ajuda se travar >15min em algo

---

**FIM DO PLANO DE SPRINT**

Pronto para começar? 🚀
