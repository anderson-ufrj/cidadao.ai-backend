---
title: Cidadão.AI Backend
emoji: 🏛️
colorFrom: green
colorTo: blue
sdk: docker
app_file: app.py
pinned: false
license: apache-2.0
---

# 🏛️ Cidadão.AI - Backend

> **Enterprise-grade multi-agent AI backend for Brazilian government transparency analysis**  
> **Backend enterprise de IA multi-agente para análise de transparência governamental brasileira**

[![SDG16](https://img.shields.io/badge/SDG-16-orange.svg)](https://sdgs.un.org/goals/goal16)
[![Open Gov](https://img.shields.io/badge/Open-Government-blue.svg)](https://www.opengovpartnership.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-enabled-blue.svg)](https://www.docker.com/)

📖 **[Complete Documentation Hub](https://anderson-ufrj.github.io/cidadao.ai-docs/)**

## [English](#english) | [Português](#português)

---

## 🇺🇸 English

### Quick Start
```bash
# Clone the repository
git clone https://github.com/anderson-ufrj/cidadao.ai-backend
cd cidadao.ai-backend

# Option 1: Run with start script (recommended)
./start.sh

# Option 2: Run with Docker
docker-compose up -d

# Option 3: Manual start
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-hf.txt
python3 app.py

# Access:
# - Interface: http://localhost:7860
# - API Docs: http://localhost:7860/docs
```

### Features
- Multiple specialized AI agents for transparency analysis
- Enterprise-grade FastAPI backend with 40+ endpoints
- Multi-agent system with Redis communication
- PostgreSQL + Redis + ChromaDB stack
- Production-ready with Docker + Kubernetes

### Links
- 🌐 **Documentation Hub**: https://anderson-ufrj.github.io/cidadao.ai-docs/
- 🚀 **Live API**: https://huggingface.co/spaces/neural-thinker/cidadao.ai-backend

---

## 🇧🇷 Português

### Início Rápido
```bash
# Clone o repositório
git clone https://github.com/anderson-ufrj/cidadao.ai-backend
cd cidadao.ai-backend

# Opção 1: Executar com script (recomendado)
./start.sh

# Opção 2: Executar com Docker
docker-compose up -d

# Opção 3: Iniciar manualmente
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements-hf.txt
python3 app.py

# Acesse:
# - Interface: http://localhost:7860
# - API Docs: http://localhost:7860/docs
```

### Funcionalidades
- Múltiplos agentes de IA especializados para análise de transparência
- Backend FastAPI enterprise com 40+ endpoints
- Sistema multi-agente com comunicação Redis
- Stack PostgreSQL + Redis + ChromaDB
- Pronto para produção com Docker + Kubernetes

### Links
- 🌐 **Hub de Documentação**: https://anderson-ufrj.github.io/cidadao.ai-docs/
- 🚀 **API Online**: https://huggingface.co/spaces/neural-thinker/cidadao.ai-backend


---

## 👨‍💻 Author

**Anderson Henrique da Silva**  
📧 andersonhs27@gmail.com | 💻 [GitHub](https://github.com/anderson-ufrj)
