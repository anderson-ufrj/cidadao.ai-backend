---
title: Cidadão.AI - Transparência Pública
emoji: 🔍
colorFrom: green
colorTo: yellow
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: true
license: mit
---

# 🇧🇷 Cidadão.AI - Plataforma de Inteligência para Transparência Pública

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-FF6B6B.svg)](https://streamlit.io)
[![Gradio](https://img.shields.io/badge/Gradio-4.8.0-orange.svg)](https://gradio.app)
[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/neural-thinker/cidadao-ai)

> **Democratizando o acesso aos dados governamentais brasileiros através de inteligência artificial especializada**

## 🎯 Visão Geral

O **Cidadão.AI** é uma plataforma inovadora que combina inteligência artificial especializada com dados públicos brasileiros para promover transparência governamental e accountability democrático. Desenvolvido especificamente para o contexto brasileiro, o sistema utiliza técnicas avançadas de machine learning para analisar contratos, licitações, despesas e outros documentos públicos.

### 🌟 Principais Diferenciais

- **🤖 IA Especializada**: Modelo treinado especificamente para transparência pública brasileira
- **⚖️ Conformidade Legal**: Verificação automática com legislação brasileira (Lei 14.133/2021, Lei 8.666/93)
- **🔍 Detecção Inteligente**: Algoritmos avançados para identificar anomalias e irregularidades
- **📊 Interface Intuitiva**: Design moderno e responsivo com cores da bandeira brasileira
- **🌐 Multiplataforma**: Disponível via web, API REST e integração com sistemas existentes

## 🚀 Funcionalidades Principais

### 🔍 **Análise de Documentos**
- Contratos públicos e aditivos contratuais
- Licitações e processos de compra
- Despesas e empenhos orçamentários
- Convênios e termos de parceria
- Relatórios de prestação de contas

### 🚨 **Detecção de Irregularidades**
- Superfaturamento e preços abusivos
- Empresas fantasma ou com capacidade técnica questionável
- Processos sem licitação inadequados ou injustificados
- Concentração excessiva de fornecedores
- Descumprimento de prazos e procedimentos legais

### 💰 **Análise Financeira**
- Avaliação de riscos em contratações públicas
- Comparação de preços entre órgãos e regiões
- Identificação de padrões de gastos suspeitos
- Análise de capacidade orçamentária
- Projeções e tendências de gastos

### ⚖️ **Conformidade Legal**
- Verificação com Nova Lei de Licitações (Lei 14.133/2021)
- Conformidade com Lei 8.666/93 (licitações anteriores)
- Aderência à Lei de Acesso à Informação
- Compliance com normas do TCU e órgãos de controle
- Análise de fundamentação jurídica

## 🏗️ Arquitetura do Sistema

### 📱 **Interface Usuário**
- **Streamlit App**: Interface principal com design brasileiro moderno
- **Gradio Interface**: Versão para Hugging Face Spaces
- **Busca Avançada**: Filtros por órgão, ano, valor, localização
- **Chat Inteligente**: Conversação natural sobre transparência

### 🤖 **Sistema Multi-Agente**
- **MasterAgent**: Orquestração de investigações complexas
- **InvestigatorAgent**: Detecção de anomalias especializadas
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

## 📊 Como Usar

### 🌐 **Acesso Online (Recomendado)**

1. **Acesse a Plataforma**: [Cidadão.AI no Hugging Face Spaces](https://huggingface.co/spaces/neural-thinker/cidadao-ai)
2. **Escolha uma Funcionalidade**:
   - 🔍 **Busca Avançada**: Para consultas específicas com filtros
   - 💬 **Chat com IA**: Para perguntas em linguagem natural
3. **Digite sua Consulta** ou use os exemplos predefinidos
4. **Analise os Resultados** gerados pela IA especializada

### 💻 **Instalação Local**

```bash
# 1. Clone o repositório
git clone https://github.com/anderson-ufrj/cidadao.ai
cd cidadao.ai

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves API

# 5. Execute a aplicação
streamlit run app.py
```

### 🔧 **Instalação Completa (Desenvolvedores)**

```bash
# Instalar todas as dependências
pip install -e ".[dev]"

# Executar API completa
make run-dev

# Executar testes
make test

# Verificar qualidade do código
make lint
```

## 💡 Exemplos de Uso

### 🔍 **Consultas Típicas**

```
"Quanto foi gasto com educação no estado de SP em 2023?"
"Qual o histórico de contratos da empresa X com o governo?"
"Mostre licitações suspeitas acima de R$ 10 milhões em 2024"
"Analise os gastos com saúde durante a pandemia"
"Há concentração de fornecedores no Ministério Y?"
```

### 📊 **Tipos de Análise**

- **Análise de Risco**: Avaliação automática de irregularidades
- **Comparativo**: Comparação entre órgãos, períodos e regiões
- **Tendências**: Identificação de padrões temporais
- **Correlações**: Relações entre diferentes variáveis
- **Conformidade**: Verificação legal automatizada

## 🛠️ Stack Tecnológico

### 🖥️ **Backend**
- **Python 3.11+**: Linguagem principal
- **FastAPI**: Framework web moderno e assíncrono
- **LangChain**: Orquestração de LLMs
- **PostgreSQL + Redis**: Persistência e cache
- **Celery**: Processamento assíncrono

### 🤖 **Inteligência Artificial**
- **Transformers**: Modelos de linguagem especializados
- **FAISS/ChromaDB**: Busca vetorial e memória semântica
- **Scikit-learn**: Algoritmos de machine learning
- **SHAP/LIME**: Explicabilidade das decisões da IA
- **Groq API**: Inferência rápida de LLMs

### 🎨 **Frontend**
- **Streamlit**: Interface principal moderna
- **Gradio**: Interface para Hugging Face Spaces
- **CSS3**: Design responsivo com cores brasileiras
- **JavaScript**: Interatividade e animações

### 🚀 **Deploy e DevOps**
- **Docker**: Containerização e orquestração
- **Kubernetes**: Escalabilidade e alta disponibilidade
- **GitHub Actions**: CI/CD automatizado
- **Hugging Face Spaces**: Deploy simplificado

## 📈 Performance e Qualidade

### ⚡ **Métricas de Performance**
- **Tempo de Resposta**: < 3s para análises simples
- **Throughput**: > 100 consultas/minuto
- **Disponibilidade**: 99.9% SLA
- **Precisão**: 88.9% F1-Score em detecção de anomalias

### 🧪 **Cobertura de Testes**
- **Testes Unitários**: 85%+ cobertura
- **Testes de Integração**: API e componentes
- **Testes E2E**: Fluxos completos de usuário
- **Benchmarks**: Performance e qualidade

## 🤝 Como Contribuir

### 🛠️ **Para Desenvolvedores**

1. **Fork** o repositório
2. **Crie um branch** para sua feature: `git checkout -b feature/amazing-feature`
3. **Implemente** seguindo nossos padrões de código
4. **Execute testes**: `make test`
5. **Verifique qualidade**: `make lint`
6. **Commit**: `git commit -m "feat: add amazing feature"`
7. **Push**: `git push origin feature/amazing-feature`
8. **Abra um Pull Request**

### 💡 **Áreas de Contribuição**
- 🔍 **Novos Data Sources**: Integração com APIs adicionais
- 🤖 **Modelos ML**: Algoritmos de detecção aprimorados
- 🎨 **UI/UX**: Melhorias na interface e experiência
- 📚 **Documentação**: Tutoriais e exemplos
- 🧪 **Testes**: Cobertura e cenários adicionais
- 🌐 **Internacionalização**: Suporte a outros idiomas

## 📊 Dados e Fontes

### 🏛️ **Fontes Oficiais**
- [Portal da Transparência](https://portaldatransparencia.gov.br)
- [Dados Abertos do Governo](https://dados.gov.br)
- [TCU - Tribunal de Contas da União](https://portal.tcu.gov.br)
- [CEAF - Cadastro de Entidades Sem Fins Lucrativos](https://www.portaltransparencia.gov.br/sancoes/ceaf)

### 📋 **Tipos de Dados Analisados**
- Contratos e aditivos (R$ 2.1 trilhões/ano)
- Licitações e pregões (>500 mil/ano)
- Despesas diretas (>100 milhões registros/ano)
- Convênios e parcerias (>50 mil ativos)
- Sanções e impedimentos (CEIS/CNEP)

## ⚖️ Aspectos Legais e Éticos

### 📋 **Conformidade**
- **LGPD**: Compliance com Lei Geral de Proteção de Dados
- **LAI**: Aderência à Lei de Acesso à Informação
- **Marco Civil**: Respeito ao Marco Civil da Internet
- **Transparência**: Uso exclusivo de dados públicos

### 🛡️ **Limitações e Responsabilidades**
- **Ferramenta de Apoio**: Não substitui análise humana especializada
- **Validação Necessária**: Resultados devem ser verificados por especialistas
- **Uso Responsável**: Não acusar pessoas sem evidências conclusivas
- **Dados Públicos**: Baseado exclusivamente em informações oficiais

## 🔗 Links Importantes

- 🌐 **Aplicação Web**: [Hugging Face Spaces](https://huggingface.co/spaces/neural-thinker/cidadao-ai)
- 💻 **Código Fonte**: [GitHub Repository](https://github.com/anderson-ufrj/cidadao.ai)
- 📚 **Documentação Completa**: [Manual Técnico](./docs/documentation.html)
- 🤖 **Modelo de IA**: [Hugging Face Model](https://huggingface.co/neural-thinker/cidadao-gpt)
- 📄 **Paper/Artigo**: [Arxiv](https://arxiv.org/abs/placeholder) *(em preparação)*

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

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<div align="center">

**🇧🇷 Feito com ❤️ para fortalecer a democracia brasileira**

[![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/neural-thinker/cidadao-ai)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black)](https://github.com/anderson-ufrj/cidadao.ai)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

*"A transparência é a luz que ilumina os caminhos da democracia"*

</div>