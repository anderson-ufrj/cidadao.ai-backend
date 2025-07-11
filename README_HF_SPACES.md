---
title: Cidadão AI
emoji: 🏛️
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.19.0
app_file: app.py
pinned: true
license: mit
short_description: Plataforma de transparência pública que usa IA para detectar anomalias em gastos governamentais brasileiros
---

# 🏛️ Cidadão.AI

> Transparência pública com Inteligência Artificial

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Gradio](https://img.shields.io/badge/Gradio-4.19.0-orange.svg)](https://gradio.app/)

## 🎯 Sobre

O **Cidadão.AI** é uma plataforma open-source que democratiza o acesso a dados de gastos públicos brasileiros, utilizando Inteligência Artificial para detectar anomalias, padrões suspeitos e irregularidades em contratos, licitações e despesas governamentais.

## 🚀 Funcionalidades

- **🔍 Investigação Inteligente**: Analise gastos públicos com perguntas em linguagem natural
- **🚨 Detecção de Anomalias**: Identifique automaticamente padrões suspeitos e irregularidades
- **📊 Análises Avançadas**: Visualize tendências, concentrações e correlações nos dados
- **📄 Relatórios Automáticos**: Gere relatórios profissionais com insights e recomendações
- **🌐 Dados Públicos**: Integração com Portal da Transparência e outras fontes oficiais

## 💻 Como Usar

### Interface Web (Hugging Face Spaces)

Acesse diretamente: [https://huggingface.co/spaces/neural-thinker/cidadao-ai](https://huggingface.co/spaces/neural-thinker/cidadao-ai)

### Instalação Local

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/cidadao-ai.git
cd cidadao-ai

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python app.py
```

## 📖 Documentação

- [Manual do Usuário (PT-BR)](docs/MANUAL_PT.md)
- [User Manual (EN)](docs/MANUAL_EN.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](DEPLOYMENT.md)

## 🤖 Tecnologia

- **Frontend**: Gradio para interface web interativa
- **Backend**: FastAPI + Python 3.10+
- **IA/ML**: LangChain, Transformers, Groq, Together AI
- **Dados**: Portal da Transparência API
- **Infraestrutura**: Docker, PostgreSQL, Redis

## 🛡️ Segurança e Privacidade

- ✅ Usa apenas dados públicos oficiais
- ✅ Não coleta ou armazena dados pessoais
- ✅ Código-fonte 100% aberto e auditável
- ✅ Segue as melhores práticas de segurança

## 📊 Exemplos de Uso

1. **Investigar contratos suspeitos**:
   - "Contratos emergenciais com valores acima de 1 milhão"
   - "Empresas com múltiplos contratos pequenos no mesmo órgão"

2. **Analisar tendências**:
   - "Evolução dos gastos com terceirização nos últimos 3 meses"
   - "Órgãos com maior crescimento de despesas"

3. **Detectar anomalias**:
   - "Contratos com valores 200% acima da média"
   - "Fornecedores que aparecem apenas em contratações diretas"

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja nosso [guia de contribuição](CONTRIBUTING.md) para começar.

### Como contribuir:

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🏆 Reconhecimentos

- Portal da Transparência por disponibilizar os dados públicos
- Comunidade open-source brasileira
- Todos os contribuidores e usuários

## 📞 Contato

- **Email**: contato@cidadao.ai
- **GitHub**: [@seu-usuario/cidadao-ai](https://github.com/seu-usuario/cidadao-ai)
- **Twitter**: [@cidadaoai](https://twitter.com/cidadaoai)

---

**Feito com ❤️ para promover transparência no Brasil**

*"A transparência é a alma da democracia"*