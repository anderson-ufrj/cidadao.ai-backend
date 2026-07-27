# Cookbooks

Cookbooks curtos e práticos pra tarefas comuns no Cidadão.AI — feitas pra
quem quer um exemplo rodável em poucos minutos, sem precisar ler o
codebase inteiro.

## Disponíveis

| Cookbook | O que cobre | Formato |
|----------|-------------|---------|
| [**Invocar um agente via API**](invoke-agent-via-api.md) | `curl` / `httpie`, auth JWT, payload, resposta, erros comuns | Markdown |
| [**Agentes culturais com DSPy**](dspy-cultural-agents/index.ipynb) | Multi-agente com personalidades, routing, colaboração, streaming | Jupyter Notebook |

## Como contribuir

Pra adicionar um cookbook novo:

1. Escolha um escopo bem pequeno (uma tarefa, um endpoint, um padrão).
2. Crie o arquivo em `docs/cookbooks/<nome-kebab>.md` (ou pasta com
   `index.ipynb` se for notebook).
3. Inclua: pré-requisitos, comando(s) executáveis, resposta esperada,
   1-2 erros comuns.
4. Teste manualmente o comando antes de abrir o PR.
5. Adicione uma linha na tabela acima.
6. Commit no padrão Conventional Commits: `docs(cookbooks): adiciona ...`.
