# ✅ RESOLVIDO: Chat não estava buscando dados reais das APIs

**Data Identificação**: 17 de novembro de 2025
**Data Resolução**: 17 de novembro de 2025
**Status**: ✅ **BUG RESOLVIDO E TESTADO**
**Commits**: `25ec9bd`, `20e5c00`
**Documentação**: `docs/fixes/2025-11/FIX_CHAT_APIS_INTEGRATION.md`

---

> ✅ **NOTA**: Este problema foi **completamente resolvido** em 17/11/2025.
>
> **Correções implementadas**:
> - ✅ Entity extraction melhorada (estados, valores monetários, categorias)
> - ✅ Orchestrator integrado ao chat endpoint (30+ APIs)
> - ✅ Testes automatizados passando (100% sucesso)
>
> **Documentação completa**: [`docs/fixes/2025-11/FIX_CHAT_APIS_INTEGRATION.md`](fixes/2025-11/FIX_CHAT_APIS_INTEGRATION.md)
>
> Este arquivo permanece como **registro histórico** do problema original.

---

## 📊 Sintoma

Quando usuário pergunta:
```
"Quero ver contratos de saúde em Minas Gerais acima de R$ 1 milhão em 2024"
```

**Resposta atual** (ERRADA):
```
Zumbi dos Palmares
• Registros analisados: 18
• Anomalias detectadas: 0
• Valor total analisado: R$ 0.00
```

**Resposta esperada** (CORRETA):
```
Zumbi dos Palmares
• Registros analisados: 47 contratos encontrados
• Valor total: R$ 8.543.200,00
• Anomalias detectadas: 5
• Fraudes suspeitas: 2
```

---

## 🔍 Diagnóstico

### ✅ O que ESTÁ funcionando:

1. ✅ Chat recebe mensagem
2. ✅ Intent Detection funciona (INVESTIGATE_CONTRACTS)
3. ✅ Agente Zumbi é chamado
4. ✅ API key do Portal está configurada (`.env`)
5. ✅ Código de integração existe (`chat_data_integration.py`)

### ❌ O que NÃO está funcionando:

1. ❌ **Extração de entidades incompleta**
   - "Minas Gerais" não é reconhecido (só aceita "MG")
   - Valor "R$ 1 milhão" não é extraído corretamente
   - Estado não é mapeado para código IBGE

2. ❌ **Portal API não é chamada de verdade**
   - Chat chama `chat_data_integration.process_user_query()`
   - Mas os dados não chegam ao agente Zumbi
   - Zumbi recebe apenas dados mockados/vazios

3. ❌ **Orchestrator NÃO é usado**
   - Orquestração completa (30+ APIs) não é acionada
   - Sistema usa apenas Portal da Transparência (1 API)
   - Sem análise multi-agente coordenada

---

## 🔧 Análise Técnica

### Fluxo Atual (INCOMPLETO):

```
Usuário: "Contratos saúde MG > R$ 1M"
    ↓
Chat API (/api/v1/chat/send)
    ↓
Intent Detection ✅ (INVESTIGATE_CONTRACTS)
    ↓
chat_data_integration.process_user_query() ✅
    ↓
Entity Extraction ⚠️ (PARCIAL)
    • Estado: ❌ "Minas Gerais" → Não reconhecido (espera "MG")
    • Valor: ❌ "1 milhão" → Não convertido para 1000000
    • Ano: ✅ 2024 extraído
    ↓
Portal da Transparência ⚠️
    • Chamada: ✅ Código existe
    • Parâmetros: ❌ Vazios (sem estado, sem valor)
    • Resultado: ❌ Dados vazios ou demo mode
    ↓
Zumbi Agent ⚠️
    • Recebe: ❌ Apenas dados vazios
    • Analisa: 18 registros mockados
    • Retorna: R$ 0.00
```

### Fluxo Esperado (CORRETO):

```
Usuário: "Contratos saúde MG > R$ 1M"
    ↓
Chat API (/api/v1/chat/send)
    ↓
Intent Detection ✅ (INVESTIGATE_CONTRACTS)
    ↓
Orchestrator.investigate() ✅
    ↓
Entity Extraction ✅ (COMPLETO)
    • Estado: ✅ "Minas Gerais" → "MG" → Código IBGE 31
    • Valor: ✅ "1 milhão" → 1000000
    • Categoria: ✅ "saúde"
    • Ano: ✅ 2024
    ↓
Execution Plan ✅
    • Stage 1: Portal da Transparência (contratos MG)
    • Stage 2: PNCP (licitações saúde MG)
    • Stage 3: DataSUS (indicadores saúde MG)
    • Stage 4: IBGE (dados MG)
    ↓
Data Federation ✅ (Paralelo)
    • Portal: 47 contratos (R$ 8.5M)
    • PNCP: 23 licitações
    • DataSUS: Indicadores
    • IBGE: População MG
    ↓
Multi-Agent Analysis ✅
    • Zumbi: Detecta 5 anomalias
    • Oxóssi: Encontra 2 fraudes
    • Bonifácio: Verifica legalidade
    • Anita: Estatísticas
    ↓
Response Completa ✅
```

---

## 🔍 Código Problemático

### Problema 1: Entity Extraction não mapeia estado

**Arquivo**: `src/services/chat_data_integration.py:99-165`

```python
async def _extract_entities(self, message: str) -> dict[str, Any]:
    entities = {}

    # Extract CNPJ - ✅ OK
    cnpj_match = re.search(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b", message)

    # Extract state - ❌ PROBLEMA: Só aceita siglas
    # NÃO MAPEIA "Minas Gerais" → "MG"
    # NÃO MAPEIA "MG" → código IBGE "31"

    # Extract value - ❌ PROBLEMA: Não converte "milhão"
    value_patterns = [
        r"R\$\s*([\d.,]+)",  # ❌ Não captura "milhão"
        r"([\d.,]+)\s*reais",
        r"([\d.,]+)\s*mil\s*reais",  # ✅ Captura "mil"
    ]
    # Faltando: r"([\d.,]+)\s*milhão"
```

### Problema 2: Portal API requer `codigoOrgao`

**Arquivo**: `src/services/portal_transparencia_service.py:122-133`

```python
# Portal API requires at least one filter (date or orgao)
# If no filters provided, use last 30 days as default
has_filter = any([
    orgao,           # ❌ Não extrai corretamente
    cnpj_fornecedor,
    data_inicial,
    data_final,
    valor_minimo,    # ❌ Não extrai de "milhão"
    valor_maximo,
])
if not has_filter:
    # ❌ Usa período padrão sem filtros do usuário
    return self._get_demo_contracts(params)
```

### Problema 3: Chat não usa Orchestrator

**Arquivo**: `src/api/routes/chat.py:263-272`

```python
# ❌ USA: chat_data_integration (1 API apenas)
portal_result = await chat_data_integration.process_user_query(
    request.message, request.context
)

# ✅ DEVERIA USAR: Orchestrator (30+ APIs)
from src.services.orchestration.orchestrator import InvestigationOrchestrator
orchestrator = InvestigationOrchestrator()
result = await orchestrator.investigate(
    query=request.message,
    user_id=current_user.id
)
```

---

## 🛠️ Soluções Necessárias

### Solução 1: Melhorar Entity Extraction

**Arquivo**: `src/services/chat_data_integration.py`

```python
async def _extract_entities(self, message: str) -> dict[str, Any]:
    entities = {}

    # 1. Mapear nomes de estados para siglas
    STATES_MAP = {
        "minas gerais": "MG",
        "são paulo": "SP",
        "rio de janeiro": "RJ",
        "bahia": "BA",
        # ... todos os 27 estados
    }

    # 2. Mapear siglas para códigos IBGE
    IBGE_CODES = {
        "MG": "31",
        "SP": "35",
        "RJ": "33",
        # ... todos
    }

    # 3. Extrair estado por nome completo OU sigla
    for state_name, state_code in STATES_MAP.items():
        if state_name in message.lower():
            entities["estado"] = state_code
            entities["codigo_uf"] = IBGE_CODES[state_code]
            break

    # 4. Extrair valores com "milhão", "mil", "bilhão"
    value_patterns = [
        (r"R\$\s*([\d.,]+)\s*bilhão", 1000000000),
        (r"R\$\s*([\d.,]+)\s*milhão", 1000000),
        (r"R\$\s*([\d.,]+)\s*mil", 1000),
        (r"R\$\s*([\d.,]+)", 1),
    ]

    for pattern, multiplier in value_patterns:
        match = re.search(pattern, message, re.IGNORECASE):
            if match:
                value_str = match.group(1).replace(".", "").replace(",", ".")
                value = float(value_str) * multiplier
                entities["valor"] = value
                break

    return entities
```

### Solução 2: Integrar Orchestrator no Chat

**Arquivo**: `src/api/routes/chat.py`

```python
from src.services.orchestration.orchestrator import InvestigationOrchestrator

# Criar instância global
orchestrator = InvestigationOrchestrator()

@router.post("/message")
async def send_message(request: ChatRequest, current_user=...):
    # ...

    # Se for investigação, usar Orchestrator completo
    if intent.type in [IntentType.INVESTIGATE, IntentType.ANALYZE]:
        logger.info(f"Using full orchestration for: {request.message}")

        # Chamar orchestrator (30+ APIs, multi-agent)
        investigation = await orchestrator.investigate(
            query=request.message,
            user_id=current_user.id if current_user else None,
            session_id=session_id
        )

        # Formatar resposta com resultados completos
        response_text = format_investigation_response(investigation)

        return ChatResponse(
            response=response_text,
            investigation_id=investigation.investigation_id,
            metadata={
                "apis_called": len(investigation.plan.stages),
                "total_results": len(investigation.entities_found),
                "anomalies": investigation.metadata.get("anomaly_detection"),
            }
        )
```

### Solução 3: Usar APIs Federais Alternativas

**Arquivo**: `src/services/chat_data_integration.py`

```python
async def _search_contracts(self, message: str, entities: dict) -> dict:
    # Tentar múltiplas APIs em paralelo
    results = await asyncio.gather(
        # Portal da Transparência
        self.portal.search_contracts(**entities),

        # PNCP (Portal Nacional de Contratações)
        self.pncp_client.search(**entities),

        # Compras.gov
        self.compras_gov_client.search(**entities),

        return_exceptions=True
    )

    # Consolidar resultados de todas as APIs
    all_contracts = []
    for result in results:
        if isinstance(result, dict):
            all_contracts.extend(result.get("contratos", []))

    return {
        "tipo": "contratos",
        "dados": all_contracts,
        "total": len(all_contracts),
        "fontes": ["portal", "pncp", "compras_gov"]
    }
```

---

## ✅ Checklist de Correção

### Urgente (Fix Imediato):
- [ ] **1. Melhorar entity extraction**
  - [ ] Mapear "Minas Gerais" → "MG" → código "31"
  - [ ] Extrair "R$ 1 milhão" → 1000000
  - [ ] Mapear categorias (saúde, educação, etc.)

- [ ] **2. Usar Orchestrator no chat**
  - [ ] Substituir `chat_data_integration` por `InvestigationOrchestrator`
  - [ ] Chamar 30+ APIs em paralelo
  - [ ] Análise multi-agente (Zumbi + Oxóssi + Bonifácio + etc.)

- [ ] **3. Verificar API key do Portal**
  - [ ] Testar se key `e24f842355f7211a2f4895e301aa5bca` funciona
  - [ ] Fazer chamada HTTP direta para validar
  - [ ] Se não funcionar, usar PNCP como alternativa

### Médio Prazo:
- [ ] **4. Adicionar fallback entre APIs**
  - [ ] Se Portal falha → tentar PNCP
  - [ ] Se PNCP falha → tentar Compras.gov
  - [ ] Circuit breaker para resiliência

- [ ] **5. Melhorar response formatting**
  - [ ] Mostrar fonte dos dados (qual API)
  - [ ] Incluir estatísticas (X contratos, Y APIs)
  - [ ] Links para visualização detalhada

---

## 📝 Próximos Passos Recomendados

### Passo 1: Testar Portal API diretamente

```bash
# Testar se API key funciona
curl -X GET "https://api.portaldatransparencia.gov.br/api-de-dados/contratos" \
  -H "chave-api-dados: e24f842355f7211a2f4895e301aa5bca" \
  -d "codigoOrgao=26000&dataInicial=01/01/2024&dataFinal=31/12/2024"
```

### Passo 2: Implementar melhorias no código

1. Editar `src/services/chat_data_integration.py`:
   - Adicionar mapeamento de estados
   - Melhorar extração de valores

2. Editar `src/api/routes/chat.py`:
   - Integrar `InvestigationOrchestrator`
   - Substituir chamada simples por orquestração completa

3. Testar localmente:
   ```bash
   make run-dev
   curl -X POST http://localhost:8000/api/v1/chat/send \
     -d '{"message": "Contratos saúde MG > R$ 1M"}'
   ```

### Passo 3: Validar resultado

Resposta esperada:
```json
{
  "response": "Encontrei 47 contratos de saúde em Minas Gerais acima de R$ 1 milhão",
  "metadata": {
    "apis_called": 4,
    "total_results": 47,
    "total_value": 8543200.00,
    "anomalies_detected": 5,
    "fraud_patterns": 2
  }
}
```

---

## 🎯 Conclusão

**O sistema TEM toda a infraestrutura pronta (Orchestrator, 30+ APIs, 7 agentes), mas o CHAT não está usando.**

**Fix**: Conectar o chat ao Orchestrator em vez de usar apenas `chat_data_integration`.

**Tempo estimado**: 2-4 horas de desenvolvimento + testes

**Prioridade**: 🔴 ALTA (funcionalidade core quebrada)

---

**Autor**: Anderson Henrique da Silva
**Data**: 17 de novembro de 2025
**Status**: 🐛 Bug identificado, solução mapeada
