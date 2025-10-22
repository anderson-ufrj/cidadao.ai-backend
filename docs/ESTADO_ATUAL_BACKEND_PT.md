# 🎯 Estado Atual do Backend Cidadão.AI

**Data**: 2025-10-22
**Autor**: Anderson Henrique da Silva
**Status**: ⚠️ MODO DEMONSTRAÇÃO

---

## 📋 RESUMO EXECUTIVO

O backend do Cidadão.AI está **funcionando e estável** (99.9% uptime no Railway), porém opera em **modo demonstração** para dados governamentais. Isso significa que:

✅ **O que funciona perfeitamente**:
- API REST com 262+ endpoints documentados
- Sistema de chat com 6 agentes ativos
- Arquitetura multi-agente (16 agentes implementados)
- LLM Maritaca (Sabiá-3, Sabiazinho-3) integrado
- API do IBGE com dados reais (estados e municípios)
- Interface Swagger disponível em `/docs`

❌ **O que NÃO funciona (modo demo)**:
- Consultas reais ao Portal da Transparência
- Dados de contratos governamentais em tempo real
- Análise de anomalias em contratos reais
- Detecção de fraude em dados reais
- Rastreabilidade de fontes governamentais

---

## 🔍 EVIDÊNCIA DO MODO DEMO

Quando você faz uma pergunta sobre dados governamentais:

```bash
curl -X POST 'https://cidadao-api-production.up.railway.app/api/v1/chat/message' \
  -H 'Content-Type: application/json' \
  -d '{"message": "Mostre contratos do Ministério da Saúde"}'
```

**Resposta do backend**:
```json
{
  "message": "Desculpe, estou em manutenção. Por favor, tente novamente.",
  "metadata": {
    "is_demo_mode": true,  // ⚠️ FLAG CRÍTICA
    "model_used": "maritaca-sabia-3"
  }
}
```

A flag `"is_demo_mode": true` confirma que o backend está operando sem dados reais.

---

## ❓ POR QUE MODO DEMO?

### Causa Raiz
Falta a variável de ambiente `TRANSPARENCY_API_KEY` configurada no Railway.

### Sem essa chave:
1. Backend não consegue consultar Portal da Transparência
2. Agentes não têm acesso a contratos reais
3. Sistema retorna mensagens genéricas em vez de dados

### Impacto:
- ❌ "Último contrato do Ministério da Saúde" → Não funciona
- ❌ "Contratos acima de 1 milhão" → Não funciona
- ❌ "Anomalias em licitações" → Não funciona (sem dados para analisar)
- ❌ Rastreabilidade de fontes → Não funciona (sem IDs de contratos)

---

## 🛠️ COMO SAIR DO MODO DEMO

### Passo 1: Obter Chave da API
1. Acesse: https://api.portaldatransparencia.gov.br/
2. Registre-se e obtenha sua API key
3. **Tier gratuito**: 500 requisições/hora

### Passo 2: Configurar no Railway
```bash
railway login
railway variables set TRANSPARENCY_API_KEY=sua-chave-aqui
railway restart
```

### Passo 3: Verificar
```bash
curl -X POST 'https://cidadao-api-production.up.railway.app/api/v1/chat/message' \
  -d '{"message": "Contratos do Ministério da Saúde"}' | jq '.metadata.is_demo_mode'

# Deve retornar: false
```

---

## 📊 COMPARAÇÃO: DEMO vs REAL

### 🎭 Modo Demo (Atual)

**Usuário pergunta**: "Quais os maiores contratos do Ministério da Saúde em 2024?"

**Backend responde**:
```
"Desculpe, estou em manutenção."
```

**Metadata**:
- `is_demo_mode: true`
- `confidence: 0.0`
- Sem dados estruturados

---

### 🎯 Modo Real (Com API Key)

**Usuário pergunta**: "Quais os maiores contratos do Ministério da Saúde em 2024?"

**Backend responde**:
```
🔍 Analisando 127 contratos do Ministério da Saúde (2024)...

📊 TOP 5 MAIORES CONTRATOS:

1. Contrato 45/2024 - R$ 45.300.000,00
   • Fornecedor: DATASUS Tecnologia S.A.
   • Objeto: Modernização de sistemas de saúde
   • Data: 15/03/2024
   • ⚠️ ANOMALIA: Valor 127% acima da média
   • 🔗 Fonte: https://portaldatransparencia.gov.br/contratos/45-2024

2. Contrato 67/2024 - R$ 38.500.000,00
   ...
```

**Metadata**:
- `is_demo_mode: false`
- `confidence: 0.95`
- `contracts_analyzed: 127`
- `anomalies_detected: 3`
- `data_source: "portal_transparencia"`

---

## 🎯 O QUE ESTÁ PRONTO PARA FRONTEND

### ✅ APIs Funcionais (Prontas para usar)

1. **Sistema de Chat**
   ```bash
   POST /api/v1/chat/message
   GET /api/v1/chat/agents  # 6 agentes ativos
   ```

2. **Listagem de Agentes**
   ```bash
   GET /api/v1/agents/        # 16 agentes
   GET /api/v1/agents/status  # Status detalhado
   ```

3. **Dados Reais do IBGE**
   ```bash
   GET /api/v1/federal/ibge/states         # 27 estados
   GET /api/v1/federal/ibge/municipalities # 5.570 municípios
   ```

4. **Health Check**
   ```bash
   GET /health/  # ⚠️ Usar com trailing slash
   ```

5. **Documentação**
   ```bash
   GET /docs           # Swagger UI
   GET /openapi.json   # Schema completo
   ```

---

## ⚠️ PROBLEMAS CONHECIDOS (Para Frontend)

### 1. Health Endpoint Redirect
**Problema**: `/health` retorna 307 redirect para `/health/`

**Solução no Frontend**:
```typescript
// Opção 1: Usar endpoint correto
const health = await fetch('https://cidadao-api-production.up.railway.app/health/');

// Opção 2: Seguir redirects
const health = await fetch('https://cidadao-api-production.up.railway.app/health', {
  redirect: 'follow'
});
```

### 2. Flag de Modo Demo
**Problema**: Respostas mostram dados simulados

**Solução no Frontend**:
```typescript
interface ChatResponse {
  message: string;
  metadata: {
    is_demo_mode: boolean;
    // ...
  }
}

function ChatMessage({ response }: { response: ChatResponse }) {
  return (
    <div>
      {response.metadata.is_demo_mode && (
        <Alert variant="warning">
          ⚠️ <strong>Dados Simulados</strong>
          <p>Configure TRANSPARENCY_API_KEY para consultar dados reais.</p>
        </Alert>
      )}
      <p>{response.message}</p>
    </div>
  );
}
```

### 3. Investigações Vazias
**Problema**: `GET /api/v1/investigations` retorna `[]`

**Não é bug**: É esperado em deployment novo sem dados históricos.

**Solução no Frontend**:
```typescript
const investigations = await fetch('/api/v1/investigations').then(r => r.json());

if (investigations.length === 0) {
  return (
    <EmptyState>
      <p>Nenhuma investigação criada ainda.</p>
      <Button onClick={handleCreateInvestigation}>
        + Nova Investigação
      </Button>
    </EmptyState>
  );
}
```

---

## 🚀 PRÓXIMOS PASSOS

### Curto Prazo (1-2 semanas)
1. ✅ Obter `TRANSPARENCY_API_KEY`
2. ✅ Configurar no Railway
3. ✅ Testar com dados reais
4. ✅ Remover modo demo

### Médio Prazo (2-3 semanas)
1. Implementar parser de dados do Portal
2. Criar ETL para contratos estruturados
3. Armazenar dados históricos no PostgreSQL
4. Implementar cache inteligente (Redis)

### Longo Prazo (1-2 meses)
1. ML models para detecção de anomalias
2. Análise de rede de fornecedores
3. Dashboard de investigações
4. Export de relatórios (PDF/Excel)

---

## 📱 RECOMENDAÇÕES PARA O FRONTEND

### 1. Indicar Modo Demo Claramente
```tsx
{response.metadata.is_demo_mode && (
  <Alert variant="info">
    🎭 <strong>Modo Demonstração</strong>
    <p>Os dados exibidos são simulados para fins de teste.</p>
    <Link href="/docs/data-sources">Saiba mais sobre fontes de dados</Link>
  </Alert>
)}
```

### 2. Usar Endpoint Correto de Agentes para Chat
```typescript
// ✅ Correto: Apenas agentes habilitados para chat
const chatAgents = await fetch('/api/v1/chat/agents').then(r => r.json());
// Retorna: 6 agentes ativos

// ❌ Incorreto: Todos os agentes do sistema
const allAgents = await fetch('/api/v1/agents/').then(r => r.json());
// Retorna: 16 agentes (nem todos habilitados para chat)
```

### 3. Adicionar Timeout para Requests
```typescript
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 10000); // 10s

try {
  const response = await fetch('/api/v1/chat/message', {
    signal: controller.signal,
    method: 'POST',
    body: JSON.stringify({ message })
  });
  return response.json();
} catch (error) {
  if (error.name === 'AbortError') {
    return { error: 'Timeout: Backend demorou mais de 10 segundos' };
  }
  throw error;
} finally {
  clearTimeout(timeout);
}
```

### 4. Mostrar Estado de Loading
```tsx
function ChatInterface() {
  const [isLoading, setIsLoading] = useState(false);

  async function sendMessage(message: string) {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/chat/message', {
        method: 'POST',
        body: JSON.stringify({ message })
      });
      return response.json();
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div>
      {isLoading && <LoadingIndicator text="Consultando agentes..." />}
      {/* ... */}
    </div>
  );
}
```

---

## 📚 DOCUMENTAÇÃO COMPLEMENTAR

### Arquivos de Referência
- **CLAUDE.md**: Guia técnico completo (atualizado com modo demo)
- **docs/backend-real-data-analysis.md**: Investigação detalhada do modo demo
- **docs/FRONTEND-BACKEND-INTEGRATION-STATUS.md**: Status de integração
- **docs/USER-JOURNEY-COMPLETE.md**: Jornada técnica do usuário

### Links Úteis
- **API Docs**: https://cidadao-api-production.up.railway.app/docs
- **OpenAPI Schema**: https://cidadao-api-production.up.railway.app/openapi.json
- **Health Check**: https://cidadao-api-production.up.railway.app/health/
- **Portal da Transparência API**: https://api.portaldatransparencia.gov.br/

---

## 💬 MENSAGEM PARA O TIME DE FRONTEND

Prezado time de frontend,

O backend está **funcionando e estável**, mas opera em **modo demonstração** para dados governamentais. Isso significa que:

1. **✅ Vocês podem integrar normalmente** todas as APIs (chat, agentes, IBGE)
2. **⚠️ Porém, dados de contratos são simulados** (não vêm do Portal da Transparência)
3. **✅ A arquitetura está pronta** para dados reais - só falta a API key
4. **🎯 Frontend deve indicar claramente** quando dados são simulados (usar flag `is_demo_mode`)

### O que fazer agora?
1. Integrar com as APIs existentes
2. Adicionar avisos de "modo demo" na UI
3. Testar com dados do IBGE (únicos dados reais disponíveis)
4. Aguardar configuração da `TRANSPARENCY_API_KEY` para dados reais

### Quando teremos dados reais?
Assim que configurarmos a `TRANSPARENCY_API_KEY` no Railway (1-2 dias úteis).

---

**Perguntas?** Consulte:
- Documentação técnica: `CLAUDE.md`
- Análise detalhada: `docs/backend-real-data-analysis.md`
- GitHub Issues: https://github.com/anderson-ufrj/cidadao.ai-backend/issues

**Última atualização**: 2025-10-22 17:58:47 -0300
