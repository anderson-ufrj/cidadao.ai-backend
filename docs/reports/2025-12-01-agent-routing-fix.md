# Relatório: Correção do Roteamento de Agentes

**Data:** 2025-12-01
**Autor:** Backend Team
**Status:** ✅ Implementado e Testado em Produção

---

## Problema Reportado

O frontend identificou que quando nenhum `agent_id` era enviado (modo Automático), o backend selecionava a **Anita** em vez do **Abaporu** (orquestrador master).

> "O backend deveria usar o Abaporu (orquestrador) como padrão quando nenhum agente é especificado, e o Abaporu deveria então decidir qual agente é mais apropriado para a pergunta."

## Solução Implementada

Criamos um **módulo centralizado de roteamento** (`src/services/agent_routing.py`) que é agora a única fonte de verdade para seleção de agentes em todos os endpoints.

### Commits

```
d29814f test(routing): add comprehensive tests for agent routing module
f65615a refactor(chat-service): use centralized agent routing
c04f73e refactor(chat): use centralized routing in /message endpoint
2d781a2 refactor(chat): use centralized routing in /stream endpoint
9190eee feat(routing): add centralized agent routing module
```

## Comportamento Atual (Após Correção)

### Modo Automático (sem `agent_id`)

| Intent Detectado | Agente Selecionado | Razão |
|------------------|-------------------|-------|
| `investigate` | **Abaporu** | Orquestrador coordena investigações |
| `question` | **Drummond** | Comunicador para perguntas gerais |
| `greeting` | **Drummond** | Comunicador para saudações |
| `analyze` | **Anita** | Analista para análises estatísticas |
| `report` | **Tiradentes** | Relator para geração de relatórios |
| `unknown` (baixa confiança) | **Drummond** | Fallback conversacional |
| `unknown` (alta confiança) | **Abaporu** | Orquestrador decide |

### Modo Manual (com `agent_id`)

Quando o frontend envia `agent_id` explicitamente, o agente solicitado é **sempre respeitado**.

## Testes em Produção

### Teste 1: Modo Automático (sem agent_id)
```bash
curl -X POST ".../api/v1/chat/stream" \
  -d '{"message": "Ola, como funciona o sistema?"}'
```
**Resultado:**
```json
{"type":"agent_selected","agent_id":"abaporu","agent_name":"Abaporu"}
```
✅ **Abaporu selecionado corretamente**

### Teste 2: Intent de Investigação
```bash
curl -X POST ".../api/v1/chat/stream" \
  -d '{"message": "Quero investigar contratos do Ministerio da Saude"}'
```
**Resultado:**
```json
{"type":"intent","intent":"investigate","confidence":0.85}
{"type":"agent_selected","agent_id":"abaporu","agent_name":"Abaporu"}
```
✅ **Abaporu orquestra investigações**

### Teste 3: Modo Manual (agent_id explícito)
```bash
curl -X POST ".../api/v1/chat/stream" \
  -d '{"message": "Ola", "agent_id": "zumbi"}'
```
**Resultado:**
```json
{"type":"agent_selected","agent_id":"zumbi","agent_name":"Zumbi dos Palmares"}
```
✅ **Agente explícito respeitado**

## Ações Necessárias no Frontend

### ✅ Nenhuma alteração obrigatória

O frontend **não precisa mais** enviar `agent_id: "abaporu"` para o modo Automático. Basta omitir o campo `agent_id` que o backend usará o Abaporu automaticamente.

### Opcional: Remover workaround

Se o frontend estava enviando `agent_id: "abaporu"` como workaround, isso pode ser removido:

```javascript
// ANTES (workaround)
const payload = {
  message: userMessage,
  agent_id: isAutomatic ? "abaporu" : selectedAgent
};

// DEPOIS (mais limpo)
const payload = {
  message: userMessage,
  ...(selectedAgent && { agent_id: selectedAgent })
};
```

## Cobertura de Testes

- **26 testes unitários** adicionados em `tests/unit/services/test_agent_routing.py`
- Todos passando ✅
- Cobertura inclui:
  - Estrutura do registry de agentes
  - Mapeamento intent → agente
  - Função `resolve_agent_id()`
  - Funções auxiliares
  - Cenários de integração frontend

## Arquivos Modificados

| Arquivo | Mudança |
|---------|---------|
| `src/services/agent_routing.py` | **Novo** - Módulo centralizado |
| `src/api/routes/chat.py` | Refatorado para usar módulo centralizado |
| `src/services/chat_service.py` | Refatorado para usar módulo centralizado |
| `tests/unit/services/test_agent_routing.py` | **Novo** - 26 testes |

---

**Contato:** Backend Team
**Deploy:** Railway Production (https://cidadao-api-production.up.railway.app)
