---
title: Cidadão.AI - Transparência Pública
emoji: 🔍
colorFrom: green
colorTo: yellow
sdk: gradio
sdk_version: 4.44.2
app_file: main.py
pinned: true
license: other
language: pt
tags:
- transparency
- government
- corruption-detection
- anomaly-detection
- brazilian-government
- public-spending
- accountability
- financial-analysis
- legal-compliance
- brazilian-public-data
pipeline_tag: text-classification
library_name: transformers
base_model: gpt2
datasets:
- portal-da-transparencia
- custom
metrics:
- accuracy
- f1
- precision
- recall
widget:
- text: "Contrato emergencial no valor de R$ 25.000.000,00 para aquisição de equipamentos médicos dispensando licitação. Fornecedor: Empresa XYZ LTDA."
  example_title: "Análise de Contrato Público"
- text: "Despesa com diárias de viagem para servidor público em valor de R$ 150.000,00 para participação em evento internacional."
  example_title: "Análise de Despesas"
- text: "Licitação para compra de materiais de escritório no valor de R$ 50.000,00 com processo regular"
  example_title: "Análise de Licitação"
---

# 🇧🇷 Cidadão.AI - Plataforma de Transparência Pública

[![License: All Rights Reserved](https://img.shields.io/badge/License-All%20Rights%20Reserved-red.svg)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/neural-thinker/cidadao-ai)

> **Sistema de IA multi-agente para análise de transparência governamental brasileira**

## 🎯 Visão Geral

O **Cidadão.AI** é uma plataforma inovadora que utiliza inteligência artificial especializada para democratizar o acesso aos dados públicos brasileiros. Desenvolvido especificamente para o contexto brasileiro, o sistema emprega arquitetura multi-agente para analisar contratos, licitações, despesas e outros documentos governamentais.

## 🚀 Acesso Rápido

### 🌐 **Aplicação Online**
- **🤗 Hugging Face Spaces**: [cidadao-ai](https://huggingface.co/spaces/neural-thinker/cidadao-ai)
- **📚 Documentação Técnica**: [anderson-ufrj.github.io/cidadao.ai](https://anderson-ufrj.github.io/cidadao.ai/)
- **💻 Repositório**: [GitHub](https://github.com/anderson-ufrj/cidadao.ai)

### 🔧 **Instalação Local**

```bash
# Clone o repositório
git clone https://github.com/anderson-ufrj/cidadao.ai
cd cidadao.ai

# Instale as dependências
pip install -r requirements/base.txt

# Execute a aplicação
python apps/gradio_app.py
```

## 🌟 Funcionalidades Principais

### 🔍 **Análise Inteligente**
- **Contratos Públicos**: Verificação de valores, fornecedores e conformidade
- **Licitações**: Detecção de irregularidades e padrões suspeitos
- **Despesas**: Identificação de superfaturamento e anomalias
- **Conformidade Legal**: Verificação automática com legislação brasileira

### 🤖 **Sistema Multi-Agente**
- **MasterAgent**: Orquestração de investigações
- **InvestigatorAgent**: Detecção de anomalias
- **AnalystAgent**: Análise de padrões financeiros
- **ReporterAgent**: Geração de relatórios
- **MemoryAgent**: Gestão de contexto e memória

### 📊 **Métricas de Performance**
- **Precisão**: 89.2% em detecção de anomalias
- **Cobertura**: 91.1% de recall em investigações
- **Velocidade**: < 180ms tempo de resposta API
- **Escalabilidade**: > 120 consultas/minuto

## 🛠️ Tecnologias

### **Backend**
- **Python 3.11+** com FastAPI
- **PostgreSQL** + Redis
- **Docker** + Kubernetes

### **Inteligência Artificial**
- **Transformers** (Hugging Face)
- **LangChain** para orquestração
- **Scikit-learn** para ML
- **ChromaDB** para busca vetorial

### **Frontend**
- **Gradio** para interface web
- **Streamlit** para dashboards
- **HTML/CSS/JS** para documentação

## 📖 Documentação

### **Guias de Uso**
- [📋 Guia de Instalação](docs/installation-guide.md)
- [🔧 Guia de Desenvolvimento](docs/development-guide.md)
- [🚀 Guia de Deploy](docs/deployment-guide.md)

### **Documentação Técnica**
- [🏗️ Arquitetura do Sistema](docs/technical-architecture.md)
- [🤖 Sistema Multi-Agente](docs/multi-agent-system.md)
- [🔌 Referência da API](docs/api-reference.md)

### **Documentação Completa**
- [📚 Documentação Técnica Completa](https://anderson-ufrj.github.io/cidadao.ai/)

## 🧪 Testes

```bash
# Executar todos os testes
make test

# Testes específicos
make test-unit          # Testes unitários
make test-integration   # Testes de integração
make test-e2e          # Testes end-to-end

# Cobertura de testes
make test-coverage
```

## 🚀 Deploy

### **Desenvolvimento**
```bash
# Com Docker
make docker-dev

# Local
make run-dev
```

### **Produção**
```bash
# Docker Compose
docker-compose -f deployment/docker-compose.yml up

# Kubernetes
kubectl apply -f deployment/kubernetes/
```

### **Plataformas Cloud**
- **Railway**: `railway.json` configurado
- **Render**: `render.yaml` configurado
- **Hugging Face**: Deploy automático

## 📊 Estrutura do Projeto

```
cidadao.ai/
├── apps/                    # Aplicações (Gradio, Streamlit, API)
├── src/                     # Código fonte
│   ├── agents/             # Sistema multi-agente
│   ├── api/                # API REST
│   ├── ml/                 # Machine Learning
│   └── services/           # Serviços de negócio
├── tests/                  # Testes
├── docs/                   # Documentação
├── deployment/             # Configurações de deploy
├── requirements/           # Dependências
└── scripts/                # Scripts utilitários
```

## 🤝 Contribuindo

1. **Fork** o projeto
2. **Crie um branch** para sua feature
3. **Implemente** seguindo os padrões de código
4. **Execute os testes**: `make test`
5. **Envie um Pull Request**

## 📄 Licença

Este projeto está sob licença **Todos os Direitos Reservados**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

**Anderson Henrique da Silva**
- 💼 [LinkedIn](https://www.linkedin.com/in/anderson-h-silva95)
- 💻 [GitHub](https://github.com/anderson-ufrj)
- 📧 Email: andersonhs27@gmail.com
- 🤗 [Hugging Face](https://huggingface.co/neural-thinker)

**Instituição**: IFSuldeminas Campus Muzambinho  
**Curso**: Bacharelado em Ciência da Computação

---

<div align="center">

## 🇧🇷 Feito com ❤️ para fortalecer a democracia brasileira

**🚀 [Experimente Agora](https://huggingface.co/spaces/neural-thinker/cidadao-ai) | 📚 [Documentação](https://anderson-ufrj.github.io/cidadao.ai/) | 💻 [Código](https://github.com/anderson-ufrj/cidadao.ai)**

</div>