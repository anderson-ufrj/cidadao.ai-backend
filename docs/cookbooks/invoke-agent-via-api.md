# Como invocar um agente do Cidadão.AI via API

Vamos usar o **José Bonifácio** (análise legal/compliance).

> Se preferir outro agente, troque `bonifacio` pelo slug do endpoint
> desejado. A lista completa está em `GET /api/v1/agents/` ou no arquivo
> `src/api/routes/agents.py`.

---

## Pré-requisitos

1. **API rodando** — local (`make run-dev`, porta `8000`) ou produção.
2. **`curl`** (já vem no Linux/macOS/Windows 10+) **ou** **`httpie`**
   (`pip install httpie`).
3. **Variáveis de ambiente obrigatórias** (mesmo em dev):
   - `JWT_SECRET_KEY`
   - `SECRET_KEY`
   - `API_SECRET_KEY`

Em **`APP_ENV=development`** o middleware libera requests sem token,
mas o resto da stack ainda precisa das variáveis acima carregadas.

---

## Autenticação

Três caminhos suportados pelo middleware em
`src/api/middleware/authentication.py`:

| Modo | Header | Quando usar |
|------|--------|-------------|
| **JWT Bearer** | `Authorization: Bearer <token>` | Frontend, usuários humanos |
| **API Key** | `X-API-Key: <key>` | Integrações server-to-server |
| **Sem auth** | — | Apenas se `APP_ENV=development` |

### Obtendo um JWT

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"sua-senha"}'
```

Resposta contém `access_token` — guarda numa variável de shell:

```bash
TOKEN=$(curl -sX POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"sua-senha"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
```

> Em PowerShell:
> ```powershell
> $TOKEN = (Invoke-RestMethod -Method Post `
>   -Uri http://localhost:8000/api/v1/auth/login `
>   -ContentType 'application/json' `
>   -Body '{"email":"admin@example.com","password":"sua-senha"}').access_token
> ```

---

## Chamando o agente — `curl`

```bash
curl -X POST http://localhost:8000/api/v1/agents/bonifacio \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Avalie a conformidade legal do Programa Bolsa Família em relação à LRF",
    "context": {
      "session_id": "demo-session-1"
    },
    "options": {
      "data": {
        "policy_name": "Bolsa Família",
        "legal_framework": ["Lei 10.836/2004", "LRF"]
      }
    }
  }'
```

## Chamando o agente — `httpie`

```bash
http POST localhost:8000/api/v1/agents/bonifacio \
  Authorization:"Bearer $TOKEN" \
  query="Avalie a conformidade legal do Programa Bolsa Família em relação à LRF" \
  context:='{"session_id":"demo-session-1"}' \
  options:='{"data":{"policy_name":"Bolsa Família","legal_framework":["Lei 10.836/2004","LRF"]}}'
```

### Payload (request body)

Definido em `AgentRequest` (`src/api/routes/agents.py`):

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `query` | `string` | ✅ | Pergunta ou comando em linguagem natural |
| `context` | `object` | ❌ | Metadados (ex.: `session_id`, `request_id`) |
| `options` | `object` | ❌ | Parâmetros específicos do agente (ex.: `data`) |

---

## Resposta esperada

Sucesso retorna `200 OK` com o shape de `AgentResponse`:

```json
{
  "agent": "jose_bonifacio",
  "result": {
    "analysis": "...conteúdo da análise legal produzida pelo agente..."
  },
  "metadata": {
    "processing_time": 1.42,
    "compliance_issues": 0,
    "legal_risks": []
  },
  "success": true,
  "message": "Legal and compliance analysis completed successfully"
}
```

Campos-chave:

- `result` — payload variável, depende do agente. Para Bonifácio inclui
  análise legal; pra Zumbi traria anomalias detectadas; etc.
- `metadata` — métricas/contadores. Sempre tem `processing_time`.
- `success` + `message` — flag e descrição human-readable.

---

## Erros comuns

### 1. `401 Unauthorized` — token ausente, expirado ou inválido

```json
{ "detail": "Authentication required" }
```

ou

```json
{ "detail": "Token has expired" }
```

**Como resolver:**

- Confirme o header (`Authorization: Bearer ...` ou `X-API-Key: ...`).
- Refresque o token via `POST /api/v1/auth/refresh` com o
  `refresh_token` recebido no login.
- Em produção, verifique se `JWT_SECRET_KEY` no servidor bate com o
  segredo que assinou o token.

### 2. `422 Unprocessable Entity` — payload mal formado

Acontece quando `query` está faltando ou o JSON tem tipo errado:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "query"],
      "msg": "Field required"
    }
  ]
}
```

**Como resolver:**

- Garanta o header `Content-Type: application/json`.
- O `query` é obrigatório. `context` e `options` são opcionais, mas se
  enviados precisam ser **objetos** JSON (não strings).
- No `httpie`, use `:=` (não `=`) pra valores que não são string.

### 3. `500 Internal Server Error` — falha no agente

```json
{ "detail": "Bonifacio agent processing failed: <stack trace>" }
```

**Como resolver:**

- Veja o log do servidor (`make run-dev` mostra no stdout). Normalmente
  é falta de dependência externa (LLM provider sem `MARITACA_API_KEY`
  nem `ANTHROPIC_API_KEY`) ou dado inesperado dentro de `options.data`.
- Pra agentes que dependem de orchestration (Abaporu) ou memória
  (Nanã), confira `REDIS_URL` apontando pra um Redis acessível.

---

## Próximos passos

- Lista todos endpoints: `GET /api/v1/agents/`
- Status detalhado dos agentes: `GET /api/v1/agents/status`
- Pra fluxos multi-agente (investigação completa), use Abaporu
  (`/api/v1/agents/abaporu`) — ele orquestra o restante.
- Tutorial mais profundo sobre identidade cultural dos agentes:
  [`dspy-cultural-agents/index.ipynb`](dspy-cultural-agents/index.ipynb)
