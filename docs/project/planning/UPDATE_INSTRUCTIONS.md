# 📋 Instruções para Atualizar cidadao.ai-technical-docs

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

## 🎯 Arquivos Criados/Atualizados

Todos os arquivos estão em `/docs/technical-docs-updates/` para você copiar:

### 1. **agents/overview.md** ✅
- Atualizado com status real: 8 funcionais, 7 parciais, 1 planejado
- Tabela completa com porcentagem de implementação
- Diagrama Mermaid separando agentes operacionais dos em desenvolvimento
- Roadmap realista de implementação

### 2. **agents/abaporu.md** ✅
- Documentação completa do Master Agent
- Exemplos de código reais
- Métricas de performance
- Sistema de reflexão detalhado

### 3. **agents/zumbi.md** ✅
- Documentação completa do Investigator
- Todos os tipos de anomalias detectadas
- Configurações e thresholds
- Exemplos de FFT e análise espectral

### 4. **agents/machado.md** ✅ (NOVO)
- Documentação do agente de análise textual
- NER e processamento de linguagem natural
- Análise de conformidade legal
- Padrões suspeitos em contratos

## 🚀 Próximos Passos

### Documentação dos Outros Agentes Funcionais:
1. **anita.md** - Pattern Analyst (análise de tendências)
2. **tiradentes.md** - Reporter (geração multi-formato)
3. **senna.md** - Semantic Router (roteamento inteligente)
4. **nana.md** - Memory Agent (memória episódica/semântica)
5. **dandara.md** - Social Justice (coeficientes de desigualdade)

### Documentação dos Agentes Parciais:
- Marcar claramente como "⚠️ Em Desenvolvimento"
- Mostrar o que já está implementado
- Indicar o que falta implementar
- Link para CONTRIBUTING.md

### Atualização da Arquitetura:
1. Remover menções a componentes não implementados
2. Adicionar Prometheus/Grafana na stack
3. Atualizar diagramas de fluxo de dados
4. Incluir cache multi-layer (Memory → Redis → DB)

### Atualização da API:
1. Endpoints reais: `/api/v1/investigations`, `/api/v1/agents/*`
2. Autenticação JWT implementada
3. Rate limiting configurado
4. Métricas em `/health/metrics`

## 📝 Template para Agentes Parciais

```markdown
---
title: "Nome do Agente"
sidebar_position: X
description: "Descrição"
---

# 🎯 Nome - Tipo Agent

:::warning **Status: ⚠️ Parcialmente Implementado**
Estrutura básica em `src/agents/arquivo.py`. Implementação em progresso.
:::

## 📋 Visão Geral
[Descrição do propósito]

## 🚧 Estado Atual

### ✅ Implementado
- Estrutura da classe
- Interface básica
- Integração com BaseAgent

### ❌ Pendente
- Lógica principal de processamento
- Integração com APIs externas
- Testes unitários completos
- Documentação detalhada

## 🎯 Capacidades Planejadas
[Lista do que o agente fará quando completo]

## 🤝 Como Contribuir
Veja [CONTRIBUTING.md](https://github.com/anderson-ntlabs/cidadao.ai-backend/blob/main/CONTRIBUTING.md)
para implementar este agente.

---
**Status**: Em desenvolvimento
```

## ⚡ Comandos para Copiar Arquivos

```bash
# No repositório cidadao.ai-technical-docs:

# 1. Copiar o overview atualizado
cp ../cidadao.ai-backend/docs/technical-docs-updates/agents/overview.md docs/agents/

# 2. Renomear arquivos existentes
mv docs/agents/master-agent.md docs/agents/abaporu.md
mv docs/agents/investigator-agent.md docs/agents/zumbi.md
# ... etc

# 3. Copiar novos arquivos
cp ../cidadao.ai-backend/docs/technical-docs-updates/agents/*.md docs/agents/

# 4. Commit das mudanças
git add .
git commit -m "docs: update agent documentation to reflect actual implementation status

- Update overview with real status (8 functional, 7 partial)
- Add documentation for Machado and Dandara agents
- Update existing agent docs with current implementation
- Add clear status indicators for all agents"
```

## 🎨 Estilo e Consistência

Mantenha:
1. **Emojis** no início de cada seção principal
2. **Status boxes** do Docusaurus (:::info, :::warning)
3. **Tabelas** para métricas e comparações
4. **Diagramas Mermaid** para fluxos
5. **Exemplos de código** funcionais
6. **Links** entre documentos relacionados

## 📊 Prioridades

1. **URGENTE**: Atualizar overview.md (informação incorreta)
2. **ALTA**: Documentar os 8 agentes funcionais
3. **MÉDIA**: Documentar status dos parciais
4. **BAIXA**: Adicionar mais exemplos e casos de uso

---

Boa sorte com as atualizações! 🚀
