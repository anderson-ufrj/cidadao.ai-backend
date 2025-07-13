---
title: Cidadão.AI - Análise de Transparência Pública
emoji: 🔍
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.8.0
app_file: app_spaces.py
pinned: true
license: mit
models:
- neural-thinker/cidadao-gpt
datasets:
- portal-da-transparencia
tags:
- transparency
- government
- corruption-detection
- brazilian-public-data
- specialized-ai
- multi-agent-ai
- fastapi
- langchain
language:
- pt
---

# 🇧🇷 Cidadão.AI - Plataforma de Inteligência para Transparência Pública

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Gradio](https://img.shields.io/badge/Gradio-4.8.0-orange.svg)](https://gradio.app)

> **Democratizando o acesso aos dados governamentais brasileiros através de inteligência artificial especializada**

## 🎯 Visão Geral

O **Cidadão.AI** é uma plataforma inovadora de inteligência artificial especializada em transparência pública brasileira. Utilizando arquitetura multi-agente avançada e modelos LLM especializados, o sistema analisa contratos, licitações, despesas e outros documentos públicos para detectar anomalias, avaliar riscos e verificar conformidade legal.

### 🌟 Principais Diferenciais

- **🤖 Sistema Multi-Agente**: MasterAgent, InvestigatorAgent, AnalystAgent e ReporterAgent
- **⚖️ Conformidade Legal**: Verificação automática com legislação brasileira (Lei 14.133/2021)
- **🔍 Detecção Inteligente**: Algoritmos avançados para identificar anomalias e irregularidades
- **📊 Interface Moderna**: Design responsivo com cores da bandeira brasileira
- **🌐 API Completa**: REST API com streaming e múltiplos formatos de saída

## 🚀 Como Usar Esta Demonstração

### 📊 **Aba Análise**
1. Cole texto de um contrato, licitação ou despesa pública
2. Clique em "🔍 Analisar Documento"
3. Visualize a análise detalhada com indicadores de risco

### 💬 **Aba Chat**
1. Faça perguntas sobre transparência pública em linguagem natural
2. Use exemplos como: "Analise gastos com educação em 2024"
3. Receba respostas contextualizadas e especializadas

### ℹ️ **Aba Sobre**
- Informações detalhadas sobre a plataforma
- Links para repositório, documentação e recursos

## 🎯 Capacidades Técnicas

### 🔍 **Análise de Documentos**
- Contratos públicos e aditivos contratuais
- Licitações e processos de compra
- Despesas e empenhos orçamentários
- Convênios e termos de parceria
- Relatórios de prestação de contas

### 🚨 **Detecção de Irregularidades**
- Superfaturamento e preços abusivos
- Empresas fantasma ou sem capacidade técnica
- Processos sem licitação inadequados
- Concentração excessiva de fornecedores
- Descumprimento de prazos e procedimentos

### 💰 **Análise Financeira**
- Avaliação de riscos em contratações
- Comparação de preços entre órgãos
- Identificação de padrões suspeitos
- Análise de capacidade orçamentária
- Projeções e tendências de gastos

## 🏗️ Arquitetura do Sistema

### 🤖 **Sistema Multi-Agente**
- **MasterAgent**: Orquestração de investigações complexas
- **InvestigatorAgent**: Detecção especializada de anomalias
- **AnalystAgent**: Análise de padrões e correlações
- **ReporterAgent**: Geração de relatórios em linguagem natural
- **ContextMemoryAgent**: Memória semântica e episódica

### 🔗 **API REST Completa**
- Endpoints para investigações em tempo real
- Streaming de resultados via Server-Sent Events
- Autenticação JWT e rate limiting
- Documentação automática OpenAPI/Swagger
- Formatos múltiplos (JSON, Markdown, HTML)

### 🗄️ **Integração de Dados**
- **Portal da Transparência**: API oficial do governo federal
- **Dados Abertos**: Integração com dados.gov.br
- **TCU**: Dados do Tribunal de Contas da União
- **CEAF/CEIS/CNEP**: Registros de empresas sancionadas

## 📊 Performance e Qualidade

### ⚡ **Métricas de Performance**
- **Tempo de Resposta**: < 3s para análises simples
- **Throughput**: > 100 consultas/minuto
- **Disponibilidade**: 99.9% SLA
- **Precisão**: 88.9% F1-Score em detecção de anomalias

### 🛠️ **Stack Tecnológico**
- **Backend**: FastAPI + LangChain + PostgreSQL + Redis
- **AI/ML**: Transformers + FAISS + Scikit-learn + SHAP/LIME
- **Frontend**: Gradio + Streamlit + CSS3 responsivo
- **Deploy**: Docker + Kubernetes + GitHub Actions

## 💡 Exemplos de Consultas

### 🔍 **Análise de Documentos**
```
"Contrato emergencial de R$ 50 milhões sem licitação para empresa criada há 1 mês"
```
**Resultado**: Anômalo (95% confiança) | Alto Risco | Não Conforme

### 💬 **Perguntas no Chat**
```
"Quanto foi gasto com educação no estado de SP em 2023?"
"Qual o histórico de contratos da empresa X com o governo?"
"Mostre licitações suspeitas acima de R$ 10 milhões em 2024"
"Analise os gastos com saúde durante a pandemia"
```

## 🔗 Links e Recursos

### 📚 **Principais Links**
- 🌐 **Aplicação Completa**: [Streamlit Interface](https://github.com/anderson-ufrj/cidadao.ai)
- 💻 **Código Fonte**: [GitHub Repository](https://github.com/anderson-ufrj/cidadao.ai)
- 📚 **Documentação**: [Manual Técnico](https://github.com/anderson-ufrj/cidadao.ai/blob/main/docs/documentation.html)
- 🤖 **Modelo de IA**: [Hugging Face Model](https://huggingface.co/neural-thinker/cidadao-gpt)

### 🛠️ **Para Desenvolvedores**
- **API REST**: Endpoints para integração
- **Multi-Agent Framework**: Sistema extensível
- **Real-time Streaming**: WebSocket e SSE
- **Docker Support**: Containerização completa

## 👨‍💻 Autor e Créditos

**Anderson Henrique da Silva**
- 💼 LinkedIn: [anderson-henrique-silva](https://linkedin.com/in/anderson-henrique-silva)
- 💻 GitHub: [anderson-ufrj](https://github.com/anderson-ufrj)
- 📧 Email: andersonhs27@gmail.com

### 🙏 **Agradecimentos**
- Portal da Transparência (Controladoria-Geral da União)
- Tribunal de Contas da União (TCU)
- Comunidade OpenAI e Hugging Face
- Contribuidores da comunidade open source

## ⚖️ Aspectos Legais

### 📋 **Conformidade**
- **LGPD**: Compliance com Lei Geral de Proteção de Dados
- **LAI**: Aderência à Lei de Acesso à Informação
- **Marco Civil**: Respeito ao Marco Civil da Internet
- **Transparência**: Uso exclusivo de dados públicos

### 🛡️ **Limitações**
- **Ferramenta de Apoio**: Não substitui análise humana especializada
- **Validação Necessária**: Resultados devem ser verificados por especialistas
- **Uso Responsável**: Não acusar pessoas sem evidências conclusivas
- **Dados Públicos**: Baseado exclusivamente em informações oficiais

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](https://github.com/anderson-ufrj/cidadao.ai/blob/main/LICENSE) para detalhes.

---

<div align="center">

**🇧🇷 Feito com ❤️ para fortalecer a democracia brasileira**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black)](https://github.com/anderson-ufrj/cidadao.ai)
[![License](https://img.shields.io/badge/License-MIT-green)](https://github.com/anderson-ufrj/cidadao.ai/blob/main/LICENSE)

*"A transparência é a luz que ilumina os caminhos da democracia"*

</div>