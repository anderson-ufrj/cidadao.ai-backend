# 🔍 Investigação: Portal da Transparência não integrado

**Data**: 2025-10-22
**Investigador**: Anderson Henrique da Silva
**Status**: ✅ **PROBLEMA IDENTIFICADO - SOLUÇÃO CLARA**

---

## 📋 RESUMO EXECUTIVO

O backend **TEM** a `TRANSPARENCY_API_KEY` configurada e a chave **FUNCIONA**, mas o Portal da Transparência Federal **NÃO está integrado** no sistema de roteamento de APIs.

### O que temos:
- ✅ `TRANSPARENCY_API_KEY` configurada no Railway
- ✅ Chave funcionando (testada com sucesso)
- ✅ Serviço `PortalTransparenciaService` implementado (`src/services/portal_transparencia_service.py`)
- ✅ 478 linhas de código para integração com Portal

### O que falta:
- ❌ Portal **não está registrado** no `TransparencyAPIRegistry`
- ❌ Endpoint `/api/v1/transparency/contracts` usa apenas APIs estaduais (CKAN, TCEs)
- ❌ Não há rota direta para Portal da Transparência Federal

---

## 🔬 EVIDÊNCIAS DA INVESTIGAÇÃO

### 1. API Key Funciona ✅

```bash
curl -H 'chave-api-dados: e24f842355f7211a2f4895e301aa5bca' \
  'https://api.portaldatransparencia.gov.br/api-de-dados/contratos?codigoOrgao=26000&pagina=1'
```

**Resultado**: Retorna **contratos reais** do Ministério da Educação em JSON estruturado.

### 2. Registry Não Tem Portal ❌

**Arquivo**: `src/services/transparency_apis/registry.py`

```python
def _register_default_apis(self) -> None:
    """Register all default API clients."""

    # State APIs
    self.register("RO-state", RondoniaAPIClient, APIType.STATE)

    # TCE APIs (6 estados)
    self.register("PE-tce", TCEPernambucoClient, APIType.TCE)
    self.register("CE-tce", TCECearaClient, APIType.TCE)
    # ... etc

    # CKAN states (5 portais)
    ckan_states = {
        "SP": "https://dadosabertos.sp.gov.br",
        # ... etc
    }

    # ❌ PORTAL DA TRANSPARÊNCIA FEDERAL NÃO ESTÁ AQUI!
```

### 3. Endpoint Usa Registry ❌

**Arquivo**: `src/api/routes/transparency.py`

```python
@router.get("/contracts")
async def get_contracts(...):
    collector = get_transparency_collector()  # ← Usa registry
    result = await collector.collect_contracts(...)  # ← Só vê APIs no registry
    return ContractResponse(**result)
```

O `collector` **só consegue ver** as APIs registradas no `registry`:
- 6 TCEs (PE, CE, RJ, SP, MG, BA)
- 5 CKAN (SP, RJ, RS, SC, BA)
- 1 API estadual (RO)

**Total**: 12 fontes, **TODAS estaduais/municipais**. **ZERO federais**.

### 4. Portal Service Existe Mas Não É Usado ❌

**Arquivo**: `src/services/portal_transparencia_service.py` (539 linhas)

```python
class PortalTransparenciaService:
    """Service for fetching real data from Portal da Transparência."""

    BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"

    def __init__(self):
        self.api_key = getattr(settings, "transparency_api_key", None)
        # ✅ Código correto, pega a API key

    async def search_contracts(self, ...):
        if not self.api_key:
            return self._get_demo_contracts()  # ← Demo mode só quando SEM key

        # ✅ Faz requisição real ao Portal
        response = await self.client.get(self.ENDPOINTS["contratos"], ...)
```

**Problema**: Este serviço **existe** e está **correto**, mas **ninguém o usa**!

---

## 🎯 CAUSA RAIZ

```
Fluxo Atual (INCORRETO):
User → /api/v1/transparency/contracts
     → TransparencyDataCollector
     → TransparencyAPIRegistry
     → [PE-tce, CE-tce, RJ-tce, SP-ckan, ...]  ← Só APIs estaduais
     → Retorna CKAN metadata (não contratos reais)

Fluxo Esperado (CORRETO):
User → /api/v1/transparency/contracts
     → TransparencyDataCollector
     → TransparencyAPIRegistry
     → [PORTAL-federal, PE-tce, CE-tce, ...]  ← Portal incluído!
     → Retorna contratos reais do Portal da Transparência
```

---

## 💡 SOLUÇÃO

### Opção 1: Adicionar Portal ao Registry (Recomendado)

**Vantagens**:
- ✅ Integra Portal com sistema existente
- ✅ Dados federais + estaduais em uma chamada
- ✅ Aproveita cache, validação, health check
- ✅ Consistente com arquitetura atual

**Implementação**:

1. **Criar adapter do Portal para interface do Registry**

**Arquivo**: `src/services/transparency_apis/federal_apis/portal_adapter.py`

```python
from typing import Any, Optional
from src.services.portal_transparencia_service import portal_transparencia
from ..base import TransparencyAPIClient

class PortalTransparenciaAdapter(TransparencyAPIClient):
    """Adapter for Portal da Transparência to work with registry."""

    def __init__(self):
        self.portal_service = portal_transparencia
        self.api_type = "federal"
        self.coverage = "national"

    async def get_contracts(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        year: Optional[int] = None,
        **kwargs
    ) -> list[dict[str, Any]]:
        """Get contracts from Portal da Transparência."""
        result = await self.portal_service.search_contracts(
            data_inicial=start_date,
            data_final=end_date,
            **kwargs
        )
        return result.get("contratos", [])

    async def health_check(self) -> bool:
        """Check if Portal API is accessible."""
        try:
            result = await self.portal_service.search_contracts(page=1, size=1)
            return bool(result.get("contratos"))
        except Exception:
            return False
```

2. **Registrar no Registry**

**Arquivo**: `src/services/transparency_apis/registry.py`

```python
from .federal_apis.portal_adapter import PortalTransparenciaAdapter

class TransparencyAPIRegistry:
    def _register_default_apis(self) -> None:
        # ✅ ADICIONAR ESTA LINHA
        self.register("FEDERAL-portal", PortalTransparenciaAdapter, APIType.FEDERAL)

        # State APIs
        self.register("RO-state", RondoniaAPIClient, APIType.STATE)
        # ... resto do código
```

3. **Atualizar Collector para priorizar Portal**

**Arquivo**: `src/services/transparency_apis/agent_integration.py`

```python
async def collect_contracts(self, ...):
    # Priorize federal API
    api_keys = ["FEDERAL-portal"]  # ← Portal primeiro!

    # Add state APIs if specified
    if state:
        state_apis = registry.get_state_apis(state)
        api_keys.extend([...])
    else:
        # If no state specified, get from all registered APIs
        api_keys.extend(registry.list_available_apis())
```

### Opção 2: Criar Rota Dedicada (Alternativa)

**Arquivo**: `src/api/routes/transparency.py`

```python
@router.get(
    "/contracts/federal",
    summary="Get contracts from Portal da Transparência Federal",
)
async def get_federal_contracts(
    orgao: Optional[str] = Query(None, description="Código do órgão"),
    ano: Optional[int] = Query(None, description="Ano"),
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=500),
):
    """Get contracts directly from Portal da Transparência Federal."""
    from src.services.portal_transparencia_service import portal_transparencia

    result = await portal_transparencia.search_contracts(
        orgao=orgao,
        data_inicial=f"{ano}-01-01" if ano else None,
        data_final=f"{ano}-12-31" if ano else None,
        page=page,
        size=size,
    )

    return {
        "contracts": result.get("contratos", []),
        "total": result.get("total", 0),
        "source": "Portal da Transparência Federal",
        "demo_mode": result.get("demo_mode", False),
    }
```

**Uso**:
```bash
# Contratos do Ministério da Saúde em 2024
curl 'https://cidadao-api-production.up.railway.app/api/v1/transparency/contracts/federal?orgao=26000&ano=2024'
```

---

## 📊 IMPACTO DA SOLUÇÃO

### Antes (Atual)
```json
{
  "contracts": [
    {
      "name": "contratos-der-sp",  ← CKAN metadata
      "resources": [{
        "url": "https://.../Contratos.xlsx"  ← Link para Excel
      }]
    }
  ],
  "sources": ["SP-ckan", "RJ-tce"],  ← Só estaduais
  "total": 31
}
```

### Depois (Com Portal)
```json
{
  "contracts": [
    {
      "id": 671463116,  ← Dados estruturados reais
      "numero": "322005",
      "objeto": "Fornecimento de energia elétrica...",
      "valorFinalCompra": 7273922.58,
      "fornecedor": {
        "cnpjFormatado": "00.070.698/0001-11",
        "nome": "COMPANHIA ENERGETICA DE BRASILIA"
      },
      "orgaoMaximo": {
        "codigo": "26000",
        "nome": "Ministério da Educação"
      }
    }
  ],
  "sources": ["FEDERAL-portal", "SP-tce", "RJ-ckan"],  ← Portal incluído!
  "total": 15847,  ← Muito mais contratos!
  "demo_mode": false  ← Dados reais!
}
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Opção 1: Integração com Registry (Recomendado)

- [ ] Criar `src/services/transparency_apis/federal_apis/portal_adapter.py`
- [ ] Implementar `PortalTransparenciaAdapter` com métodos:
  - [ ] `get_contracts()`
  - [ ] `get_servants()`
  - [ ] `get_expenses()`
  - [ ] `health_check()`
- [ ] Atualizar `registry.py` para registrar `FEDERAL-portal`
- [ ] Modificar `agent_integration.py` para priorizar Portal
- [ ] Adicionar testes em `tests/unit/transparency_apis/test_portal_adapter.py`
- [ ] Testar em produção com Railway
- [ ] Atualizar documentação

### Opção 2: Rota Dedicada (Alternativa)

- [ ] Adicionar rota `/transparency/contracts/federal` em `routes/transparency.py`
- [ ] Criar rota `/transparency/servants/federal`
- [ ] Criar rota `/transparency/expenses/federal`
- [ ] Adicionar testes de integração
- [ ] Atualizar Swagger docs
- [ ] Testar em produção

---

## 🎓 LIÇÕES APRENDIDAS

1. **Ter API key ≠ estar integrado**: A key existe e funciona, mas o código não a usa
2. **Arquitetura em camadas**: `PortalTransparenciaService` existe mas não está no `registry`
3. **Rotas delegam para registry**: Endpoint `/contracts` só vê o que está registrado
4. **CKAN vs Portal**: CKAN retorna **metadata**, Portal retorna **dados estruturados**

---

## 📚 ARQUIVOS ENVOLVIDOS

### Funcionam Corretamente ✅
- `src/services/portal_transparencia_service.py` (539 linhas)
- `src/core/config.py` (transparency_api_key definido)
- `.env` e Railway (API key configurada)

### Precisam de Modificação 🔧
- `src/services/transparency_apis/registry.py` (adicionar Portal)
- `src/services/transparency_apis/agent_integration.py` (priorizar Portal)

### Precisam Ser Criados ➕
- `src/services/transparency_apis/federal_apis/portal_adapter.py` (novo)
- `tests/unit/transparency_apis/test_portal_adapter.py` (novo)

---

## 🚀 PRÓXIMOS PASSOS

1. **Implementar Opção 1** (integração com registry) - **RECOMENDADO**
2. Testar localmente:
   ```bash
   JWT_SECRET_KEY=test SECRET_KEY=test make run-dev
   curl 'http://localhost:8000/api/v1/transparency/contracts?codigoOrgao=26000'
   ```
3. Verificar que `demo_mode` não aparece na resposta
4. Deploy para Railway
5. Testar em produção
6. Atualizar documentação e CLAUDE.md

---

**Conclusão**: O problema **não é** falta de API key. É falta de **integração** do Portal no sistema de roteamento de APIs. A solução é clara e direta.
