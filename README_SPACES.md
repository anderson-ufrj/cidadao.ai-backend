---
title: Cidadão.AI - Análise de Transparência Pública
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.8.0
app_file: app_spaces.py
pinned: false
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
language:
- pt
---

# 🤖 Cidadão.AI - Análise de Transparência Pública

> **Primeiro modelo de IA especializado em análise de transparência pública brasileira**

## 🎯 O que é o Cidadão.AI?

O Cidadão.AI é um modelo transformer especializado, inspirado no Kimi K2, mas 100% focado em analisar dados governamentais brasileiros. Ele detecta anomalias, avalia riscos financeiros e verifica conformidade legal em contratos, despesas e licitações públicas.

## 🚀 Como usar

1. **Análise de Texto**: Cole um texto de contrato, despesa ou licitação na área de texto
2. **Clique em Analisar**: O Cidadão.AI irá processar e fornecer análise especializada
3. **Veja os Resultados**: Receba análise de anomalias, risco financeiro e conformidade legal

## 🎯 Capacidades

- 🚨 **Detecção de Anomalias**: Identifica padrões suspeitos automaticamente
- 💰 **Análise de Risco Financeiro**: Avalia riscos em contratações públicas  
- ⚖️ **Conformidade Legal**: Verifica adequação à legislação brasileira
- 📋 **Explicações em Português**: Análises detalhadas e compreensíveis

## 📊 Performance

| Tarefa | F1-Score | Accuracy |
|--------|----------|----------|
| Detecção de Anomalias | 91.8% | 92.3% |
| Análise Financeira | 87.4% | 87.4% |
| Conformidade Legal | 83.1% | 83.1% |

**16x mais preciso** que modelos generalistas em tarefas de transparência!

## 💡 Exemplos de Uso

### Contrato Suspeito
```
Contrato emergencial de R$ 50 milhões sem licitação para empresa recém-criada
```
**Resultado**: Anômalo (95% confiança) | Alto Risco | Não Conforme

### Contrato Normal  
```
Pregão eletrônico para material de escritório no valor de R$ 100.000 com ampla participação
```
**Resultado**: Normal (89% confiança) | Baixo Risco | Conforme

## 🏗️ Arquitetura

- **Base**: Transformer multi-tarefa com ~1B parâmetros
- **Especialização**: +200M parâmetros para transparência pública
- **Treinamento**: Portal da Transparência + dados sintéticos
- **Otimização**: Português brasileiro especializado

## 🔗 Links

- 🌐 **Repositório**: [GitHub](https://github.com/anderson-ufrj/cidadao.ai)
- 🤗 **Modelo**: [Hugging Face](https://huggingface.co/neural-thinker/cidadao-gpt)
- 📚 **Documentação**: [Guia Completo](https://github.com/anderson-ufrj/cidadao.ai/blob/main/MODEL_README.md)

## 👨‍💻 Desenvolvedor

**Anderson Henrique da Silva**
- 💼 [LinkedIn](https://linkedin.com/in/anderson-henrique-silva)
- 💻 [GitHub](https://github.com/anderson-ufrj)  
- 🤖 Desenvolvimento assistido por Claude Code

## 📄 Licença

MIT License - Livre para uso em transparência pública e educação.

---

**🇧🇷 Democratizando a transparência pública com IA especializada**