# Status Após Aplicação da Migration

**Data**: 17 de novembro de 2025, 13:05 BRT
**Migration Aplicada**: `0dba430d74c4` - Create investigations table
**Ambiente**: Railway Production PostgreSQL

---

## ✅ O Que Foi Resolvido

### 1. Tabela do Banco de Dados Criada
- ✅ Tabela `investigations` existe no PostgreSQL do Railway
- ✅ 18 campos criados corretamente
- ✅ 10 índices de performance configurados
- ✅ INSERT e SELECT funcionando perfeitamente
- ✅ 69 investigações já foram salvas desde a criação

### 2. Infraestrutura Funcional
- ✅ PostgreSQL Railway acessível
- ✅ Conexão do backend com banco funcionando
- ✅ Dados sendo persistidos corretamente
- ✅ Alembic version registrada: `0dba430d74c4`

---

## ❌ O Que Ainda Está Quebrado

### Problema Principal: R$ 0.00 Persiste

Mesmo após criar a tabela, o sistema ainda retorna:
```
• Registros analisados: 50
• Anomalias detectadas: 0
• Valor total analisado: R$ 0.00
```

### Análise das 69 Investigações Salvas

Todas as investigações no banco mostram o mesmo padrão:
- `total_records_analyzed`: 50
- `anomalies_found`: 0
- Valor total: Provavelmente R$ 0.00

Isso indica que **o problema NÃO era apenas a tabela faltando**.

---

## 🔍 Diagnóstico Atual

### O Que Descobrimos

1. **Intent Classification Errado**
   - Query: "Contratos de saúde em MG acima de 1 milhão em 2024"
   - Intent detectado: `question` (ERRADO - deveria ser `investigate`)
   - Roteamento: Enviado para `drummond` em vez de `zumbi`

2. **Entity Extraction Funcional (Parcialmente)**
   - Estados sendo mapeados corretamente
   - Valores monetários sendo extraídos
   - MAS: Intent classification falha antes de usar as entidades

3. **Orchestrator Disponível (Não Usado)**
   - Orchestrator está carregado em produção
   - Mas queries não chegam até ele
   - Intent classification desvia antes

### Testes em Produção

```
Status: 2/4 testes passando (50%)

✅ PASSOU: Simple Chat (perguntas gerais)
✅ PASSOU: Orchestrator Integration (quando forçado)
❌ FALHOU: Health Check (redirect 307)
❌ FALHOU: Entity Extraction (intent errado)
```

---

## 🎯 Causas Raízes Identificadas

### 1. Intent Classifier Muito Conservador

O sistema está classificando investigações como "perguntas":

```python
# Query do usuário:
"Contratos de saúde em MG acima de 1 milhão em 2024"

# Intent detectado:
{
  "intent_type": "question",  # ❌ ERRADO
  "target_agent": "drummond",  # ❌ ERRADO (deveria ser zumbi/abaporu)
  "confidence": 0.95
}

# Intent esperado:
{
  "intent_type": "investigate",  # ✅ CORRETO
  "target_agent": "abaporu",     # ✅ CORRETO
  "confidence": 0.9
}
```

### 2. Palavras-Chave Não Acionam Investigação

Palavras como "contratos", "acima de", "R$", "milhão" deveriam acionar intent `investigate`, mas não estão.

### 3. Routing Para Agente Errado

Mesmo quando o intent é correto, o sistema às vezes roteia para agentes errados:
- Drummond (escritor) em vez de Zumbi (investigador)
- Sem análise de APIs governamentais
- Sem detecção de anomalias

---

## 🛠️ Próximas Ações Necessárias

### Prioridade ALTA (Fix Imediato)

1. **Revisar Intent Classification**
   - Arquivo: `src/services/orchestration/query_planner/intent_classifier.py`
   - Adicionar patterns para detectar investigações:
     - "contratos", "licitações", "despesas"
     - "acima de", "maior que", valores monetários
     - "investigar", "analisar", "verificar"
   - Aumentar sensibilidade para queries com números/valores

2. **Melhorar Agent Routing**
   - Arquivo: `src/services/orchestration/query_planner/agent_router.py`
   - Garantir que intent `investigate` sempre vai para Zumbi/Abaporu
   - Nunca rotear investigações para Drummond

3. **Testar Queries Específicas**
   - "INVESTIGAR contratos de saúde em MG acima de 1 milhão"
   - "ANALISAR despesas públicas em SP 2024"
   - Usar verbos de ação explícitos

### Prioridade MÉDIA (Melhorias)

4. **Adicionar Logs de Debug**
   - Logar intent classification detalhada
   - Mostrar por que cada intent foi escolhido
   - Ajudar a debugar problemas de routing

5. **Criar Testes de Intent**
   - Testar que queries de investigação retornam intent correto
   - Prevenir regressões futuras

### Prioridade BAIXA (Otimizações)

6. **Melhorar Prompts do LLM**
   - Tornar mais claro quando é investigação vs pergunta
   - Adicionar exemplos no prompt

---

## 📊 Métricas Atuais

### Banco de Dados
- Total de investigações: 69
- Investigações com valor > 0: Provavelmente 0
- Taxa de sucesso: ~0%

### API Produção
- Health check: Redirect 307 (problema de routing)
- Chat simples: 100% funcional
- Investigações: 0% retornando dados reais

### Infrastructure
- PostgreSQL: ✅ 100% funcional
- Backend deployment: ✅ 100% funcional
- Migration system: ✅ 100% funcional

---

## 🔬 Testes Para Validar Fix

Quando corrigir intent classification, estes testes devem passar:

```python
# Test 1: Query explícita deve acionar investigação
query = "INVESTIGAR contratos de saúde em MG acima de 1 milhão em 2024"
intent = classify_intent(query)
assert intent.type == IntentType.INVESTIGATE
assert intent.target_agent == "abaporu"

# Test 2: Query implícita com palavras-chave
query = "Contratos de saúde em Minas Gerais acima de R$ 1 milhão"
intent = classify_intent(query)
assert intent.type == IntentType.INVESTIGATE
assert intent.target_agent in ["abaporu", "zumbi"]

# Test 3: Valores numéricos indicam investigação
query = "Despesas públicas em SP maiores que 500 mil reais"
intent = classify_intent(query)
assert intent.type == IntentType.INVESTIGATE

# Test 4: Pergunta geral NÃO deve ser investigação
query = "Como funciona o sistema de transparência?"
intent = classify_intent(query)
assert intent.type == IntentType.QUESTION
assert intent.target_agent == "drummond"
```

---

## 📝 Conclusão

### Resumo

1. ✅ **Migration aplicada com sucesso** - Tabela existe e funciona
2. ✅ **Infraestrutura funcional** - PostgreSQL, backend, deployment OK
3. ❌ **Intent classification quebrada** - Queries não acionam investigações
4. ❌ **Dados reais não retornam** - Sistema sempre retorna R$ 0.00

### Próximo Passo Crítico

**FIX: Intent Classifier**

O problema mudou de:
- ~~Tabela do banco faltando~~ ✅ RESOLVIDO
- **Para**: Intent classification não detecta investigações ❌ PENDENTE

### Tempo Estimado

- Revisar intent classifier: 1-2 horas
- Adicionar patterns de detecção: 30min
- Testes e validação: 1 hora
- **Total**: 2-3 horas de desenvolvimento

---

**Status**: 🟡 Parcialmente Resolvido
**Próxima Ação**: Revisar `src/services/orchestration/query_planner/intent_classifier.py`
**Urgência**: 🔴 ALTA (funcionalidade core ainda quebrada)

---

**Atualizado por**: Anderson Henrique da Silva
**Data**: 17/11/2025 13:05 BRT
