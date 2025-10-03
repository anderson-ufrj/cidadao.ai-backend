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

[![Open Gov](https://img.shields.io/badge/Open-Government-blue.svg)](https://www.opengovpartnership.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Test Coverage](https://img.shields.io/badge/coverage-80%25-brightgreen.svg)](./tests)
[![Security](https://img.shields.io/badge/security-A+-brightgreen.svg)](./tests/unit/test_security_middleware.py)

**Autor**: Anderson Henrique da Silva
**Última Atualização**: 2025-10-03 08:31:53 -03:00 (São Paulo, Brasil)

[English version below](#-cidadãoai---backend-english)

## 📊 Estado Atual da Implementação

> 💡 **Status Real**: Veja [docs/reports/REAL_IMPLEMENTATION_STATUS.md](./docs/reports/REAL_IMPLEMENTATION_STATUS.md) para análise detalhada do código vs documentação

### ✅ O que está funcionando

- **8 agentes 100% operacionais** + **5 agentes 90-95% prontos** (13 agentes utilizáveis!)
- **218 endpoints REST API** organizados em 34 routers especializados
- **Integração com Portal da Transparência** (22% endpoints funcionando) + dados.gov.br
- **PostgreSQL implementado** com connection pooling (fallback in-memory opcional)
- **Redis multi-layer cache** funcionando em produção
- **Chat em tempo real** com detecção de intenções em português
- **Análise espectral FFT** para detecção de padrões periódicos
- **Monitoramento completo** - Prometheus, Grafana, OpenTelemetry, tracing
- **Deploy em produção** no HuggingFace Spaces

### 🚧 Em desenvolvimento ativo

- **4 agentes** em estágio Alpha/inicial (Dandara, Niemeyer, Ceuci, Obaluaié)
- **Modelos ML avançados** (arquitetura definida, treinamento pendente)
- **WebSocket para investigações** (60% implementado)
- **GraphQL API** (50% implementado)

## 🚀 Início Rápido

### 🎯 Como executar

**Desenvolvimento Local:**
```bash
# Clone o repositório
git clone https://github.com/anderson-ufrj/cidadao.ai-backend
cd cidadao.ai-backend

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale dependências
make install-dev

# Execute o servidor
make run-dev
# Acesse: http://localhost:8000/docs
```

**Deploy no HuggingFace Spaces:**
```bash
# Usa app.py simplificado para deploy rápido
# Deploy automático via push para HuggingFace
git push huggingface main
```

### 🔑 Configuração da API

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Configure as variáveis essenciais:
TRANSPARENCY_API_KEY=sua-chave  # Para dados reais do Portal da Transparência
JWT_SECRET_KEY=gere-uma-chave-segura
GROQ_API_KEY=sua-chave-groq     # Para LLM dos agentes
```

**Importante**: 
- ✅ **Com API key**: Análise de dados reais do governo
- 🔄 **Sem API key**: Funciona com dados demo para teste

## 🤖 Agentes Implementados

> 📚 **Documentação Completa**: Veja [docs/agents/](./docs/agents/) para guias detalhados de cada agente

### ✅ Produção - 100% Operacionais (8)

1. **🎯 Abaporu** - Mestre orquestrador de investigações ([docs](./docs/agents/abaporu.md))
2. **🔍 Zumbi dos Palmares** - Detecção de anomalias com análise espectral ([docs](./docs/agents/zumbi.md))
3. **📊 Anita Garibaldi** - Análise de padrões e tendências
4. **📝 Tiradentes** - Geração de relatórios multi-formato
5. **🏎️ Ayrton Senna** - Roteamento semântico inteligente
6. **🧠 Nanã** - Memória episódica, semântica e conversacional
7. **⚖️ José Bonifácio** - Avaliação de eficácia de políticas
8. **📚 Machado de Assis** - Análise textual avançada com NER ([docs](./docs/agents/machado.md))

### ⚠️ Beta - 90-95% Prontos (5)

9. **🏹 Oxóssi** - Caçador de fraudes (100% implementado!) ([docs](./docs/agents/oxossi.md))
10. **📢 Carlos Drummond** - Comunicador multi-canal (95%) ([docs](./docs/agents/drummond.md))
11. **🏜️ Lampião** - Análise regional/geográfica (95%) ([docs](./docs/agents/lampiao.md))
12. **🛡️ Maria Quitéria** - Auditoria e segurança (95%)
13. **🏗️ Oscar Niemeyer** - Visualização de dados (90%)

### 🚧 Alpha - Em Desenvolvimento (4)

- **Dandara** (Justiça Social, 70%), **Niemeyer** (Visualização Alt, 50%)
- **Ceúci** (ETL, 60%), **Obaluaié** (Detecção Corrupção, 40%)

## 📡 API Endpoints Principais

### 💬 Chat e Conversação
```
POST /api/v1/chat/message         # Enviar mensagem
POST /api/v1/chat/stream          # Resposta em streaming (SSE)
GET  /api/v1/chat/suggestions     # Sugestões de ações
GET  /api/v1/chat/history/{id}    # Histórico paginado
```

### 🔍 Investigações
```
POST /api/v1/investigations/analyze  # Iniciar investigação
GET  /api/v1/investigations/{id}     # Status da investigação
POST /api/agents/zumbi              # Análise de anomalias direta
```

### 📊 Portal da Transparência
```
GET /api/v1/transparency/contracts     # Contratos (funciona!)
GET /api/v1/transparency/servants      # Servidores públicos (funciona!)
GET /api/v1/transparency/expenses      # Despesas (bloqueado - 403)
GET /api/v1/transparency/suppliers     # Fornecedores (bloqueado - 403)
```

**Nota**: Descobrimos que 78% dos endpoints da API oficial retornam 403 Forbidden

### 🏥 Monitoramento
```
GET /health                    # Health check básico
GET /health/detailed           # Status detalhado do sistema
GET /api/v1/chat/cache/stats   # Estatísticas de cache
GET /metrics                   # Métricas Prometheus
```

## 🏗️ Arquitetura Técnica

### 🧠 Sistema Multi-Agente
```
Usuário → API → Agente Mestre (Abaporu)
                       ↓
              Orquestração de Agentes
                       ↓
      Investigação (Zumbi) + Análise (Anita)
                       ↓
           Geração de Relatório (Tiradentes)
```

### 🛠️ Stack Tecnológico
- **Backend**: FastAPI + Python 3.11
- **Agentes**: Classes base com reflexão e retry
- **ML**: Análise espectral FFT + detecção por threshold
- **Cache**: Redis (quando disponível) + memória
- **Deploy**: Docker + HuggingFace Spaces
- **Monitoramento**: Prometheus + Grafana

### 📊 Capacidades de ML/IA
- **Detecção de Anomalias**: Z-score (2.5 desvios padrão)
- **Análise Espectral**: FFT para padrões periódicos
- **Análise de Fornecedores**: Concentração > 70%
- **Detecção de Duplicatas**: Similaridade > 85%
- **Classificação de Despesas**: Baseada em palavras-chave

## 🧪 Testes e Qualidade

```bash
# Executar todos os testes
make test

# Com cobertura
make test-coverage

# Verificar qualidade
make check  # lint + type-check + test
```

- **Cobertura**: ~70-80% (meta em progresso)
- **51 arquivos de teste** (27 unit agents + 24 integration)
- **423 métodos test_*** (289 unit + 134 integration)
- **Categorias**: unit, integration, e2e, performance, multiagent

## 📚 Documentação

- **API Interativa**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Arquitetura**: [docs/architecture/](./docs/architecture/)
- **Guias**: [docs/development/](./docs/development/)

## 🚀 Deployment

### Docker Local
```bash
docker-compose up -d
```

### Com Monitoramento
```bash
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
# Grafana: http://localhost:3000 (admin/cidadao123)
```

### HuggingFace Spaces
```bash
git remote add hf https://huggingface.co/spaces/SEU_USUARIO/cidadao-ai
git push hf main
```

## 🤝 Como Contribuir

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/NovaFuncionalidade`)
3. Escreva testes
4. Commit suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade'`)
5. Push para a branch (`git push origin feature/NovaFuncionalidade`)
6. Abra um Pull Request

## 📄 Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais informações.

## 🙏 Agradecimentos

- Portal da Transparência pelo acesso aos dados públicos
- Comunidade open source brasileira
- Todas as figuras históricas que inspiram nossos agentes

---

# 🏛️ Cidadão.AI - Backend (English)

> **Multi-agent AI system for Brazilian government transparency analysis**

**Author**: Anderson Henrique da Silva  
**Last Updated**: 2025-09-25 18:05:00 -03:00 (São Paulo, Brazil)

## 📊 Current Implementation Status

### ✅ What's Working

- **8 of 17 agents operational** with Brazilian cultural identities
- **Portal da Transparência integration** (real with API key, demo without)
- **Complete RESTful API** with 40+ implemented endpoints
- **Real-time chat** with Portuguese intent detection
- **FFT spectral analysis** for periodic pattern detection
- **Multi-layer cache system** (memory → Redis → database)
- **Monitoring** with Prometheus and Grafana configured
- **Production deployment** on HuggingFace Spaces

### 🚧 In Development

- **9 partially implemented agents** (structure ready, logic incomplete)
- **Advanced ML models** (architecture defined, training pending)
- **Complete PostgreSQL integration** (currently using memory)
- **WebSocket for investigations** (partially implemented)

## 🚀 Quick Start

### 🎯 How to Run

**Local Development:**
```bash
# Clone repository
git clone https://github.com/anderson-ufrj/cidadao.ai-backend
cd cidadao.ai-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
make install-dev

# Run server
make run-dev
# Access: http://localhost:8000/docs
```

**Deploy to HuggingFace Spaces:**
```bash
# Uses simplified app.py for quick deployment
# Automatic deployment via push to HuggingFace
git push huggingface main
```

### 🔑 API Configuration

```bash
# Copy example file
cp .env.example .env

# Configure essential variables:
TRANSPARENCY_API_KEY=your-key  # For real Portal da Transparência data
JWT_SECRET_KEY=generate-secure-key
GROQ_API_KEY=your-groq-key     # For agent LLM
```

**Important**: 
- ✅ **With API key**: Real government data analysis
- 🔄 **Without API key**: Works with demo data for testing

## 🤖 Implemented Agents

### ✅ Fully Operational (8)

1. **🎯 Abaporu** - Master investigation orchestrator
2. **🔍 Zumbi dos Palmares** - Anomaly detection with spectral analysis
3. **📊 Anita Garibaldi** - Pattern and trend analysis
4. **📝 Tiradentes** - Multi-format report generation
5. **🏎️ Ayrton Senna** - Intelligent semantic routing
6. **🧠 Nanã** - Episodic, semantic and conversational memory
7. **⚖️ José Bonifácio** - Policy effectiveness evaluation
8. **📚 Machado de Assis** - Advanced text analysis with NER

### 🚧 In Development (9)

- Dandara (Social Justice), Lampião (Regional Analysis), Maria Quitéria (Security)
- Oscar Niemeyer (Visualization), Drummond (Communication), Ceúci (ETL)
- Obaluaié (Health), Oxossi (Data Hunter), Drummond Simple (Basic chat)

## 📡 Main API Endpoints

### 💬 Chat and Conversation
```
POST /api/v1/chat/message         # Send message
POST /api/v1/chat/stream          # Streaming response (SSE)
GET  /api/v1/chat/suggestions     # Action suggestions
GET  /api/v1/chat/history/{id}    # Paginated history
```

### 🔍 Investigations
```
POST /api/v1/investigations/analyze  # Start investigation
GET  /api/v1/investigations/{id}     # Investigation status
POST /api/agents/zumbi              # Direct anomaly analysis
```

### 📊 Portal da Transparência
```
GET /api/v1/transparency/contracts     # Contracts (works!)
GET /api/v1/transparency/servants      # Public servants (works!)
GET /api/v1/transparency/expenses      # Expenses (blocked - 403)
GET /api/v1/transparency/suppliers     # Suppliers (blocked - 403)
```

**Note**: We discovered that 78% of official API endpoints return 403 Forbidden

### 🏥 Monitoring
```
GET /health                    # Basic health check
GET /health/detailed           # Detailed system status
GET /api/v1/chat/cache/stats   # Cache statistics
GET /metrics                   # Prometheus metrics
```

## 🏗️ Technical Architecture

### 🧠 Multi-Agent System
```
User → API → Master Agent (Abaporu)
                    ↓
            Agent Orchestration
                    ↓
    Investigation (Zumbi) + Analysis (Anita)
                    ↓
         Report Generation (Tiradentes)
```

### 🛠️ Tech Stack
- **Backend**: FastAPI + Python 3.11
- **Agents**: Base classes with reflection and retry
- **ML**: FFT spectral analysis + threshold detection
- **Cache**: Redis (when available) + memory
- **Deploy**: Docker + HuggingFace Spaces
- **Monitoring**: Prometheus + Grafana

### 📊 ML/AI Capabilities
- **Anomaly Detection**: Z-score (2.5 standard deviations)
- **Spectral Analysis**: FFT for periodic patterns
- **Supplier Analysis**: Concentration > 70%
- **Duplicate Detection**: Similarity > 85%
- **Expense Classification**: Keyword-based

## 🧪 Testing and Quality

```bash
# Run all tests
make test

# With coverage
make test-coverage

# Check quality
make check  # lint + type-check + test
```

- **Coverage**: 80% (goal achieved!)
- **96 test files**
- **Categories**: unit, integration, e2e, performance

## 📚 Documentation

- **Interactive API**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Architecture**: [docs/architecture/](./docs/architecture/)
- **Guides**: [docs/development/](./docs/development/)

## 🚀 Deployment

### Local Docker
```bash
docker-compose up -d
```

### With Monitoring
```bash
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
# Grafana: http://localhost:3000 (admin/cidadao123)
```

### HuggingFace Spaces
```bash
git remote add hf https://huggingface.co/spaces/YOUR_USER/cidadao-ai
git push hf main
```

## 🤝 How to Contribute

1. Fork the project
2. Create your feature branch (`git checkout -b feature/NewFeature`)
3. Write tests
4. Commit your changes (`git commit -m 'feat: add new feature'`)
5. Push to the branch (`git push origin feature/NewFeature`)
6. Open a Pull Request

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## 🙏 Acknowledgments

- Portal da Transparência for public data access
- Brazilian open source community
- All historical figures that inspire our agents

---

<div align="center">
  <strong>🇧🇷 Made with ❤️ for Brazilian public transparency 🇧🇷</strong>
</div>