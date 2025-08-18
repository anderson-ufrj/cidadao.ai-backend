---
title: Cidadão.AI Backend
emoji: 🏛️
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
pinned: false
license: mit
---

# 🏛️ Cidadão.AI - Backend

> **Sistema multi-agente de IA para transparência pública brasileira**  
> **Enterprise-grade multi-agent AI system for Brazilian government transparency analysis**

[![Open Gov](https://img.shields.io/badge/Open-Government-blue.svg)](https://www.opengovpartnership.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

## 🚀 Quick Start

### 🔑 **Dados Reais vs Demo**

O sistema detecta automaticamente se você tem acesso à API do Portal da Transparência:

- **✅ Com `TRANSPARENCY_API_KEY`**: Análise de **dados reais** de contratos públicos
- **🔄 Sem chave API**: Funciona com **dados demo** para demonstração

### API Endpoints

```bash
# Status do sistema (mostra tipo de dados)
GET /api/status

# Obter dados de teste
GET /api/agents/zumbi/test

# Executar investigação com detecção de anomalias
POST /api/agents/zumbi/investigate
{
  "query": "Analisar contratos de informática com valores suspeitos",
  "data_source": "contracts", 
  "max_results": 100
}

# Acessar métricas Prometheus
GET /metrics
```

## 🤖 Agente Zumbi dos Palmares - Investigador

### 🎯 **Capacidades de Análise**
- **Detecção de preços suspeitos** usando análise estatística Z-score
- **Concentração de fornecedores** (threshold 40% = suspeito)
- **Análise de outliers** em contratos públicos
- **Processamento em tempo real** de dados governamentais

### 📊 **Tipos de Anomalias Detectadas**
- `price_suspicious` - Contratos com preços muito acima da média
- `price_critical` - Contratos com preços extremamente elevados  
- `vendor_concentration` - Concentração excessiva de um fornecedor

## 🔍 Exemplo de Investigação

### Request
```json
{
  "query": "Investigar contratos de informática suspeitos",
  "data_source": "contracts",
  "max_results": 50
}
```

### Response (Dados Reais)
```json
{
  "status": "completed",
  "query": "Investigar contratos de informática suspeitos", 
  "anomalies_found": 3,
  "confidence_score": 0.87,
  "processing_time_ms": 2340,
  "results": [
    {
      "contract_id": "12345",
      "description": "Aquisição de servidores de alta performance",
      "value": 850000.00,
      "supplier": "TechCorp Solutions LTDA",
      "organization": "26000",
      "anomaly_type": "price_critical",
      "risk_level": "high", 
      "explanation": "Valor R$ 850.000,00 está 3.2 desvios padrão acima da média (R$ 420.000,00)",
      "z_score": 3.2,
      "mean_value": 420000.00
    }
  ]
}
```

## 🛡️ Recursos Enterprise

### 🏗️ **Arquitetura**
- **Detecção de anomalias baseada em estatística** com algoritmos Z-score
- **Sistema de fallback inteligente** para demonstrações
- **API REST assíncrona** com FastAPI de alta performance
- **Métricas Prometheus** para observabilidade completa

### 🔒 **Segurança**
- **Autenticação via environment variables** para APIs governamentais
- **Rate limiting** automático para APIs externas
- **Error handling** robusto com fallback gracioso
- **Logging estruturado** para auditoria

### 📊 **Observabilidade** 
- **Métricas Prometheus implementadas**:
  - `cidadao_ai_requests_total` - Total de requisições
  - `cidadao_ai_investigations_total` - Investigações realizadas
  - `cidadao_ai_anomalies_detected_total` - Anomalias detectadas
- **Health checks** em `/health` e `/api/status`
- **Documentação automática** em `/docs`

## 🎯 Casos de Uso

### Detecção de Anomalias em Contratos Públicos
- **Superfaturamento**: Contratos com valores muito acima da média de mercado
- **Direcionamento**: Concentração excessiva de contratos em poucos fornecedores
- **Padrões suspeitos**: Análise estatística de distribuições de preços

### Análise de Transparência
- 🏛️ **Ministério da Saúde** (código 26000)
- 🏢 **Presidência da República** (código 20000)  
- 📚 **Ministério da Educação** (código 25000)
- 📊 **Análise customizada** por órgão e período

## 📈 Performance

- **Latência**: <2s para análise de contratos reais (~50ms para dados cached)
- **Cache Inteligente**: TTL de 1 hora reduz chamadas à API em até 100%
- **Throughput**: Suporte a análise de até 1000 contratos
- **Confiabilidade**: Sistema de fallback para alta disponibilidade
- **Escalabilidade**: Arquitetura assíncrona para múltiplas investigações

## 🔗 Links

- 📚 **API Docs**: `/docs` (documentação interativa)
- 📊 **Status**: `/api/status` (tipo de dados e capacidades)
- 🔍 **Test Data**: `/api/agents/zumbi/test` (dados para testes)  
- 📈 **Metrics**: `/metrics` (métricas Prometheus)
- 💾 **Cache Stats**: `/api/cache/stats` (estatísticas de performance)

## 👨‍💻 Autor

**Anderson Henrique da Silva**  
📧 andersonhs27@gmail.com | 💻 [GitHub](https://github.com/anderson-ufrj)

---

<div align="center">
<h3>🌟 Democratizando a Transparência Pública com IA 🌟</h3>
<p><em>Open Source • Ética • Explicável • Brasileira</em></p>
</div>