---
title: "Swagger UI - API Interativa"
sidebar_position: 4
description: "Interface interativa da API do Cidadão.AI"
---

# 🔌 Swagger UI - API Interativa

Explore e teste todos os endpoints da API do Cidadão.AI diretamente no navegador.

## 📊 Interface Interativa

<iframe 
  src="https://petstore.swagger.io/?url=https://raw.githubusercontent.com/anderson-ufrj/cidadao.ai-backend/main/openapi.json"
  width="100%" 
  height="600px" 
  frameBorder="0"
  title="Cidadão.AI API Documentation"
>
</iframe>

:::tip Dica
Você pode testar diretamente os endpoints usando a interface acima. Clique em "Try it out" para fazer requisições reais.
:::

## 🚀 Links Diretos

- **📄 OpenAPI Spec**: [Download JSON](https://raw.githubusercontent.com/anderson-ufrj/cidadao.ai-backend/main/openapi.json)
- **🌐 Swagger UI**: [Interface Completa](https://petstore.swagger.io/?url=https://raw.githubusercontent.com/anderson-ufrj/cidadao.ai-backend/main/openapi.json)
- **📚 Redoc**: [Documentação Alternativa](https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/anderson-ufrj/cidadao.ai-backend/main/openapi.json)

## 🔑 Autenticação

Para testar endpoints protegidos:

1. **Obtenha um token JWT** via `/auth/login`
2. **Configure Authorization**: `Bearer <seu-token>`
3. **Teste os endpoints** protegidos

## 📈 Endpoints Principais

### 🔍 Investigações
- `POST /investigations/start` - Iniciar investigação
- `GET /investigations/{id}` - Status da investigação
- `GET /investigations/{id}/results` - Resultados

### 🤖 Agentes
- `GET /agents` - Lista todos os agentes
- `POST /agents/{name}/query` - Consultar agente específico
- `GET /agents/{name}/status` - Status do agente

### 📊 Análises
- `POST /analysis/contracts` - Análise de contratos
- `POST /analysis/expenses` - Análise de despesas
- `GET /analysis/{id}/report` - Relatório da análise