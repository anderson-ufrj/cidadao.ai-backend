---
title: Cidadao AI
emoji: 🏛️
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "4.44.1"
app_file: app.py
pinned: false
license: mit
short_description: AI transparency for Brazilian public spending data
---

<div align="center">

# 🤖 Cidadão.AI

**Plataforma de Transparência Governamental com IA | AI-Powered Government Transparency Platform**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![API Status](https://img.shields.io/badge/API-Complete-brightgreen.svg)](#api-endpoints)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/neural-thinker/cidadao-ai)

### 🌍 Language / Idioma

**[🇧🇷 Português](#português) | [🇺🇸 English](#english)**

*"O que Brasília esconde, nossa IA revela" | "What Brasília hides, our AI reveals"*

</div>

---

## 🇧🇷 Português

### 📚 Índice
- [🎯 Missão](#-missão)
- [🚀 Status Atual](#-status-atual)
- [🏗️ Arquitetura Multi-Agente](#%EF%B8%8F-arquitetura-multi-agente)
- [🛠️ Stack Tecnológico](#%EF%B8%8F-stack-tecnológico)
- [⚡ Quick Start](#-quick-start)
- [🌐 API Endpoints](#-api-endpoints)
- [💻 Exemplos de Uso](#-exemplos-de-uso)
- [🔗 Integração Portal da Transparência](#-integração-portal-da-transparência)
- [📊 Recursos Principais](#-recursos-principais)
- [🚀 Deploy](#-deploy)
- [📖 Documentação Completa](#-documentação-completa)
- [🤝 Contribuindo](#-contribuindo)
- [👨‍💻 Autor](#-autor)

### 🎯 Missão

**Cidadão.AI** é uma plataforma revolucionária que utiliza Inteligência Artificial para democratizar o acesso aos dados de gastos públicos brasileiros. Transformamos dados brutos do Portal da Transparência em investigações inteligentes através de um sistema multi-agente avançado.

> **"Bilhões em recursos públicos. Milhões de registros. Zero transparência real."**

Nossa missão é quebrar essas barreiras tecnológicas e burocráticas, oferecendo uma IA que não apenas lê dados públicos — ela **investiga**, **questiona** e **explica** como um auditor veterano.

### 🚀 Status Atual

| Componente | Status | Descrição |
|------------|--------|-----------|
| 🛠️ **API REST** | ✅ **Completa** | Sistema multi-agente com API REST abrangente |
| 🧠 **Backend** | ✅ **Implementado** | Python 3.11+, FastAPI, LangChain, PostgreSQL, Redis |
| 🤖 **IA/ML** | ✅ **Operacional** | Múltiplos provedores LLM, detecção de anomalias |
| 🌐 **Frontend** | 🔄 **Em Progresso** | Interface web interativa em desenvolvimento |

### 🏗️ Arquitetura Multi-Agente

O sistema é construído como uma arquitetura sofisticada de múltiplos agentes especializados:

```
🎯 MasterAgent          → Orquestra investigações com planejamento e reflexão
🧠 ContextMemoryAgent   → Gerencia memória episódica, semântica e conversacional  
🔍 InvestigatorAgent    → Detecta anomalias com IA explicável
📊 AnalystAgent         → Correlaciona dados e identifica padrões
📝 ReporterAgent        → Gera relatórios em linguagem natural
🧭 SemanticRouter       → Roteamento inteligente baseado na intenção da consulta
```

### 🛠️ Stack Tecnológico

#### Backend Implementado
- **Python 3.11+** com framework FastAPI
- **LangChain** para orquestração de LLM
- **PostgreSQL + Redis** para armazenamento de dados
- **Celery** para processamento assíncrono
- **API REST completa** com autenticação JWT
- **Endpoints de streaming** em tempo real
- **Stack de middleware** abrangente

#### IA/ML Implementado
- **Hugging Face Transformers**
- **Múltiplos provedores LLM** (Groq, Together AI, HuggingFace)
- **FAISS/ChromaDB** para armazenamento vetorial
- **SHAP/LIME** para IA explicável
- **Algoritmos avançados** de detecção de anomalias
- **Análise de padrões** e detecção de correlações

### ⚡ Quick Start

```bash
# 1. Clone o repositório
git clone https://github.com/anderson-ufrj/cidadao.ai.git
cd cidadao.ai

# 2. Configure o ambiente
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -e ".[dev]"

# 3. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves de API

# 4. Execute o servidor API
python -m src.api.app
# ou
uvicorn src.api.app:app --reload

# 5. Acesse a documentação
open http://localhost:8000/docs
```

### 🌐 API Endpoints

#### 🏥 Health & Monitoramento
- `GET /health` - Status básico do sistema
- `GET /health/detailed` - Informações detalhadas do sistema
- `GET /health/ready` - Probe de prontidão para Kubernetes

#### 🔍 Investigações
- `POST /api/v1/investigations` - Iniciar nova investigação
- `GET /api/v1/investigations/{id}/stream` - Stream em tempo real
- `GET /api/v1/investigations/{id}` - Obter resultados completos
- `GET /api/v1/investigations` - Listar investigações do usuário

#### 📊 Análises
- `POST /api/v1/analysis/spending-trends` - Análise de tendências de gastos
- `POST /api/v1/analysis/vendor-patterns` - Padrões de fornecedores
- `POST /api/v1/analysis/correlations` - Análise de correlações
- `POST /api/v1/analysis/organizational` - Comportamento organizacional

#### 📄 Relatórios
- `POST /api/v1/reports/executive` - Relatório executivo
- `POST /api/v1/reports/detailed` - Relatório detalhado
- `GET /api/v1/reports/{id}/download` - Download do relatório

### 💻 Exemplos de Uso

#### CLI (Planejado)
```bash
# Investigar anomalias
cidadao investigate "contratos emergenciais suspeitos em 2024"

# Analisar padrões
cidadao analyze --org "ministerio-saude" --type patterns

# Gerar relatório
cidadao report --format pdf --investigation-id inv_123

# Monitoramento em tempo real
cidadao watch --threshold 0.8 --notify
```

#### Python SDK (Planejado)
```python
from cidadao_ai import CidadaoAI

client = CidadaoAI(api_key="sua_api_key")

# Iniciar investigação
investigation = await client.investigate(
    "contratos suspeitos de emergência",
    filters={"ano": 2024, "orgao": "26000"}
)

# Acompanhar progresso em tempo real
async for update in investigation.stream():
    print(f"Progresso: {update.progress}%")
    
# Obter resultados
results = await investigation.get_results()
```

#### API REST
```bash
# Iniciar investigação
curl -X POST "http://localhost:8000/api/v1/investigations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "query": "contratos suspeitos do ministério da saúde",
    "filters": {"ano": 2024, "orgao": "26000"},
    "options": {"anomaly_threshold": 0.8}
  }'

# Stream de resultados
curl "http://localhost:8000/api/v1/investigations/{id}/stream"
```

### 🔗 Integração Portal da Transparência

Integração completa com a API oficial do Portal da Transparência:

- **📊 Tipos de Dados:** Contratos, Despesas, Convênios, Licitações, Servidores, Empresas Sancionadas
- **⚡ Recursos:** Cache inteligente, retry automático, rate limiting, normalização de dados
- **🔍 Filtros Avançados:** Datas, valores, órgãos, modalidades, situações
- **🛡️ Segurança:** Tratamento de erros, validação de dados, logging abrangente

### 📊 Recursos Principais

- 🔍 **Investigações em Tempo Real** - Sistema de investigação com streaming ao vivo
- 📊 **Análise de Padrões** - Detecção inteligente de padrões suspeitos
- 📝 **Relatórios Automáticos** - Geração em múltiplos formatos (Markdown, HTML, JSON)
- 🤖 **IA Explicável** - Todas as detecções incluem explicações claras
- 🔐 **Segurança** - Autenticação JWT, limitação de taxa, trilha de auditoria
- ⚡ **Performance** - API < 200ms, streaming LLM < 3s

### 🚀 Deploy

```bash
# Docker
docker build -t cidadao-ai .
docker run -p 8000:8000 cidadao-ai

# Docker Compose
make docker-up

# Desenvolvimento
make run

# Testes
make test

# Lint e formatação
make lint
make format
```

### 📖 Documentação Completa

Acesse nossa documentação bilíngue completa:

- **🌐 [Documentação Interativa](docs/index.html)** - Hub principal com navegação por abas
- **📖 [Visão Geral do Projeto](docs/overview_pt.html)** - Arquitetura e tecnologias
- **🔧 [Documentação da API](docs/api_pt.html)** - Endpoints e exemplos
- **💻 [Guia de Desenvolvimento](docs/development_pt.html)** - Setup e workflow
- **🚀 [Deploy e Produção](docs/DEPLOYMENT.md)** - Instruções de implantação

### 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### 👨‍💻 Autor

**Anderson H. Silva**  
*Arquiteto de Inteligência Digital | Filosofia + ML + Ética*

- 🔗 [LinkedIn](https://www.linkedin.com/in/anderson-h-silva95/)
- 🐦 [X/Twitter](https://twitter.com/neural_thinker)
- 📧 andersonhs27@gmail.com

---

## 🇺🇸 English

### 📚 Table of Contents
- [🎯 Mission](#-mission)
- [🚀 Current Status](#-current-status-1)
- [🏗️ Multi-Agent Architecture](#%EF%B8%8F-multi-agent-architecture-1)
- [🛠️ Technology Stack](#%EF%B8%8F-technology-stack-1)
- [⚡ Quick Start](#-quick-start-1)
- [🌐 API Endpoints](#-api-endpoints-1)
- [💻 Usage Examples](#-usage-examples)
- [🔗 Transparency Portal Integration](#-transparency-portal-integration)
- [📊 Key Features](#-key-features)
- [🚀 Deployment](#-deployment)
- [📖 Complete Documentation](#-complete-documentation)
- [🤝 Contributing](#-contributing-1)
- [👨‍💻 Author](#-author-1)

### 🎯 Mission

**Cidadão.AI** is a revolutionary platform that uses Artificial Intelligence to democratize access to Brazilian public spending data. We transform raw data from the Portal da Transparência into intelligent investigations through an advanced multi-agent system.

> **"Billions in public resources. Millions of records. Zero real transparency."**

Our mission is to break these technological and bureaucratic barriers, offering an AI that doesn't just read public data — it **investigates**, **questions**, and **explains** like a veteran auditor.

### 🚀 Current Status

| Component | Status | Description |
|-----------|--------|-------------|
| 🛠️ **REST API** | ✅ **Complete** | Multi-agent system with comprehensive REST API |
| 🧠 **Backend** | ✅ **Implemented** | Python 3.11+, FastAPI, LangChain, PostgreSQL, Redis |
| 🤖 **AI/ML** | ✅ **Operational** | Multiple LLM providers, anomaly detection |
| 🌐 **Frontend** | 🔄 **In Progress** | Interactive web interface under development |

### 🏗️ Multi-Agent Architecture

The system is built as a sophisticated architecture of multiple specialized agents:

```
🎯 MasterAgent          → Orchestrates investigations with planning and reflection
🧠 ContextMemoryAgent   → Manages episodic, semantic, and conversational memory
🔍 InvestigatorAgent    → Detects anomalies with explainable AI
📊 AnalystAgent         → Correlates data and identifies patterns
📝 ReporterAgent        → Generates natural language reports
🧭 SemanticRouter       → Intelligent routing based on query intent
```

### 🛠️ Technology Stack

#### Implemented Backend
- **Python 3.11+** with FastAPI framework
- **LangChain** for LLM orchestration
- **PostgreSQL + Redis** for data storage
- **Celery** for async processing
- **Complete REST API** with JWT authentication
- **Real-time streaming** endpoints
- **Comprehensive middleware** stack

#### Implemented AI/ML
- **Hugging Face Transformers**
- **Multiple LLM providers** (Groq, Together AI, HuggingFace)
- **FAISS/ChromaDB** for vector storage
- **SHAP/LIME** for explainable AI
- **Advanced algorithms** for anomaly detection
- **Pattern analysis** and correlation detection

### ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/anderson-ufrj/cidadao.ai.git
cd cidadao.ai

# 2. Setup environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -e ".[dev]"

# 3. Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# 4. Run API server
python -m src.api.app
# or
uvicorn src.api.app:app --reload

# 5. Access documentation
open http://localhost:8000/docs
```

### 🌐 API Endpoints

#### 🏥 Health & Monitoring
- `GET /health` - Basic system status
- `GET /health/detailed` - Detailed system information
- `GET /health/ready` - Kubernetes readiness probe

#### 🔍 Investigations
- `POST /api/v1/investigations` - Start new investigation
- `GET /api/v1/investigations/{id}/stream` - Real-time stream
- `GET /api/v1/investigations/{id}` - Get complete results
- `GET /api/v1/investigations` - List user investigations

#### 📊 Analysis
- `POST /api/v1/analysis/spending-trends` - Spending trends analysis
- `POST /api/v1/analysis/vendor-patterns` - Vendor patterns
- `POST /api/v1/analysis/correlations` - Correlation analysis
- `POST /api/v1/analysis/organizational` - Organizational behavior

#### 📄 Reports
- `POST /api/v1/reports/executive` - Executive report
- `POST /api/v1/reports/detailed` - Detailed report
- `GET /api/v1/reports/{id}/download` - Download report

### 💻 Usage Examples

#### CLI (Planned)
```bash
# Investigate anomalies
cidadao investigate "suspicious emergency contracts in 2024"

# Analyze patterns
cidadao analyze --org "ministry-of-health" --type patterns

# Generate report
cidadao report --format pdf --investigation-id inv_123

# Real-time monitoring
cidadao watch --threshold 0.8 --notify
```

#### Python SDK (Planned)
```python
from cidadao_ai import CidadaoAI

client = CidadaoAI(api_key="your_api_key")

# Start investigation
investigation = await client.investigate(
    "suspicious emergency contracts",
    filters={"year": 2024, "organization": "26000"}
)

# Follow progress in real-time
async for update in investigation.stream():
    print(f"Progress: {update.progress}%")
    
# Get results
results = await investigation.get_results()
```

#### REST API
```bash
# Start investigation
curl -X POST "http://localhost:8000/api/v1/investigations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "query": "suspicious ministry of health contracts",
    "filters": {"year": 2024, "organization": "26000"},
    "options": {"anomaly_threshold": 0.8}
  }'

# Stream results
curl "http://localhost:8000/api/v1/investigations/{id}/stream"
```

### 🔗 Transparency Portal Integration

Complete integration with the official Portal da Transparência API:

- **📊 Data Types:** Contracts, Expenses, Agreements, Biddings, Public Servants, Sanctioned Companies
- **⚡ Features:** Intelligent caching, automatic retry, rate limiting, data normalization
- **🔍 Advanced Filters:** Dates, values, organizations, modalities, statuses
- **🛡️ Security:** Error handling, data validation, comprehensive logging

### 📊 Key Features

- 🔍 **Real-time Investigations** - Investigation system with live streaming
- 📊 **Pattern Analysis** - Intelligent detection of suspicious patterns
- 📝 **Automated Reports** - Generation in multiple formats (Markdown, HTML, JSON)
- 🤖 **Explainable AI** - All detections include clear explanations
- 🔐 **Security** - JWT authentication, rate limiting, audit trail
- ⚡ **Performance** - API < 200ms, LLM streaming < 3s

### 🚀 Deployment

```bash
# Docker
docker build -t cidadao-ai .
docker run -p 8000:8000 cidadao-ai

# Docker Compose
make docker-up

# Development
make run

# Tests
make test

# Lint and format
make lint
make format
```

### 📖 Complete Documentation

Access our complete bilingual documentation:

- **🌐 [Interactive Documentation](docs/index.html)** - Main hub with tab navigation
- **📖 [Project Overview](docs/overview_en.html)** - Architecture and technologies
- **🔧 [API Documentation](docs/api_en.html)** - Endpoints and examples
- **💻 [Development Guide](docs/development_en.html)** - Setup and workflow
- **🚀 [Deployment & Production](docs/DEPLOYMENT.md)** - Deployment instructions

### 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 👨‍💻 Author

**Anderson H. Silva**  
*Digital Intelligence Architect | Philosophy + ML + Ethics*

- 🔗 [LinkedIn](https://www.linkedin.com/in/anderson-h-silva95/)
- 🐦 [X/Twitter](https://twitter.com/neural_thinker)
- 📧 andersonhs27@gmail.com

---

<div align="center">

**🔒 Licença | License:** MIT

**⭐ Star este projeto se você acredita em transparência real!**  
**⭐ Star this project if you believe in real transparency!**

*"A máquina que não apenas entende o Estado — mas o interroga."*  
*"The machine that doesn't just understand the State — but interrogates it."*

</div>