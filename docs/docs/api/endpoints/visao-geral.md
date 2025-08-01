---
title: "Referência de Endpoints"
sidebar_position: 1
description: "Referência completa para todos os endpoints da API com exemplos e especificações"
---

# Referência de Endpoints

## Visão Geral

A API do Cidadão.AI fornece **50+ endpoints** organizados em módulos funcionais. Cada endpoint está documentado com esquemas de requisição/resposta, requisitos de autenticação e exemplos práticos.

## Categorias de Endpoints

### Funcionalidade Principal

| Módulo | Descrição | Endpoints |
|--------|-------------|-----------|
| [**Investigações**](./investigacoes.md) | Detecção de anomalias em dados governamentais | 6 endpoints |
| [**Análises**](./analises.md) | Análise de padrões e correlações | 7 endpoints |
| [**Relatórios**](./relatorios.md) | Geração automatizada de relatórios | 7 endpoints |
| [**Multi-Agente**](./multi-agente.md) | Sistema de orquestração de agentes | 4 endpoints |

### Autenticação e Segurança

| Módulo | Descrição | Endpoints |
|--------|-------------|-----------|
| [**Autenticação**](./autenticacao.md) | Autenticação de usuários e JWT | 9 endpoints |
| [**OAuth**](./oauth.md) | Autenticação de terceiros | 9 endpoints |
| [**Auditoria**](./auditoria.md) | Logs de auditoria de segurança | 10 endpoints |

### Sistema e Monitoramento

| Módulo | Descrição | Endpoints |
|--------|-------------|-----------|
| [**Saúde**](./saude.md) | Monitoramento de saúde do sistema | 4 endpoints |
| [**WebSocket**](./websocket.md) | Comunicações em tempo real | 3 endpoints |

## Padrões Comuns

### Formato de Requisição

Todos os endpoints aceitam payloads JSON com a seguinte estrutura:

```json
{
  "dados": {
    "tipo": "investigacao",
    "atributos": {
      "consulta": "Contratos suspeitos em 2024",
      "filtros": {
        "ano": 2024,
        "valor_minimo": 1000000
      }
    }
  }
}
```

### Formato de Resposta

Respostas bem-sucedidas seguem a especificação JSON:API:

```json
{
  "dados": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "tipo": "investigacao",
    "atributos": {
      "status": "concluida",
      "anomalias_encontradas": 12
    },
    "relacionamentos": {
      "relatorio": {
        "dados": { "tipo": "relatorio", "id": "123" }
      }
    }
  },
  "meta": {
    "id_requisicao": "req_123",
    "duracao_ms": 245
  }
}
```

### Paginação

Endpoints de lista suportam paginação:

```http
GET /api/v1/investigacoes?pagina[numero]=2&pagina[tamanho]=20
```

### Filtragem

Filtragem complexa via parâmetros de consulta:

```http
GET /api/v1/investigacoes?filtro[status]=concluida&filtro[anomalias_encontradas][gte]=5
```

### Ordenação

Ordenação multi-campo:

```http
GET /api/v1/investigacoes?ordenacao=-anomalias_encontradas,criado_em
```

### Seleção de Campos

Fieldsets esparsos para otimização:

```http
GET /api/v1/investigacoes?campos[investigacao]=id,status,anomalias_encontradas
```

## Requisitos de Autenticação

| Símbolo | Requisito | Descrição |
|---------|-----------|-------------|
| 🔓 | Público | Nenhuma autenticação necessária |
| 🔐 | Autenticado | Token JWT válido necessário |
| 👤 | Usuário | Permissões de usuário padrão |
| 👨‍💼 | Analista | Função de analista necessária |
| 🛡️ | Admin | Função de administrador necessária |

## Limitação de Taxa

Todos os endpoints estão sujeitos à limitação de taxa:

| Nível | Limite | Janela | Rajada |
|-------|--------|--------|--------|
| Anônimo | 100 | 1 hora | 10 |
| Autenticado | 1.000 | 1 hora | 100 |
| Premium | 10.000 | 1 hora | 1.000 |

## Respostas de Erro

Formato de erro consistente em todos os endpoints:

```json
{
  "erro": {
    "codigo": "RECURSO_NAO_ENCONTRADO",
    "mensagem": "Investigação não encontrada",
    "detalhes": {
      "id": "550e8400-e29b-41d4-a716-446655440000"
    },
    "id_requisicao": "req_123",
    "timestamp": "2025-01-30T10:15:30Z"
  }
}
```

## Exemplos de SDK

### Python

```python
from cidadao_ai import Cliente

cliente = Cliente(api_key="sua-chave")

# Criar investigação
investigacao = cliente.investigacoes.criar(
    consulta="Contratos suspeitos",
    fonte_dados="portal_transparencia"
)

# Verificar status
status = cliente.investigacoes.obter_status(investigacao.id)
```

### JavaScript/TypeScript

```typescript
import { CidadaoAI } from '@cidadao-ai/sdk';

const cliente = new CidadaoAI({ apiKey: 'sua-chave' });

// Criar investigação
const investigacao = await cliente.investigacoes.criar({
  consulta: 'Contratos suspeitos',
  fonteDados: 'portal_transparencia'
});

// Stream de resultados
const stream = cliente.investigacoes.stream(investigacao.id);
stream.on('dados', (chunk) => console.log(chunk));
```

## Integração com Webhooks

Configure webhooks para eventos assíncronos:

```json
{
  "url": "https://sua-app.com/webhooks/cidadao-ai",
  "eventos": [
    "investigacao.concluida",
    "anomalia.detectada",
    "relatorio.gerado"
  ],
  "segredo": "whsec_..."
}
```

---

Navegue para a documentação específica de endpoints para especificações detalhadas e exemplos.