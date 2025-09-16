# 🔄 Sincronização com cidadao.ai-technical-docs

**Data**: Janeiro 2025  
**Status**: Documentação técnica DESATUALIZADA

## 📋 Problemas Identificados

### 1. **Status Incorreto dos Agentes**
A documentação técnica mostra TODOS os 15 agentes como "✅ Ativo", mas a realidade é:
- ✅ **8 agentes funcionais** (47%)
- ⚠️ **7 agentes parcialmente implementados**
- ❌ **1 agente faltando**

### 2. **Informações Desatualizadas**
- Arquitetura não reflete implementação real
- Falta documentação sobre Prometheus/Grafana
- APIs documentadas não correspondem aos endpoints reais
- Estrutura de diretórios diferente da atual

## 🎯 Atualizações Necessárias

### 1. **docs/agents/overview.md**
Atualizar tabela de status para:

```markdown
| Agente | Persona Histórica | Especialização | Status |
|--------|-------------------|----------------|--------|
| Abaporu | Tarsila do Amaral | MasterAgent + Auto-reflexão | ✅ Funcional |
| Zumbi | Zumbi dos Palmares | Investigação de anomalias | ✅ Funcional |
| Anita | Anita Garibaldi | Análise de dados | ✅ Funcional |
| Tiradentes | Joaquim José | Geração de relatórios | ✅ Funcional |
| Senna | Ayrton Senna | Roteamento semântico | ✅ Funcional |
| Nanã | Divindade Iorubá | Gestão de memória | ✅ Funcional |
| Machado | Machado de Assis | Processamento textual | ✅ Funcional |
| Dandara | Dandara dos Palmares | Justiça social | ✅ Funcional |
| Bonifácio | José Bonifácio | Políticas públicas | ⚠️ Parcial |
| Drummond | Carlos Drummond | Comunicação | ⚠️ Parcial |
| Quitéria | Maria Quitéria | Auditoria segurança | ⚠️ Parcial |
| Niemeyer | Oscar Niemeyer | Visualização | ⚠️ Parcial |
| Ceuci | Personagem folclórico | ETL | ⚠️ Parcial |
| Obaluaiê | Divindade Iorubá | Monitor saúde | ⚠️ Parcial |
| Lampião | Virgulino Ferreira | Análise regional | ⚠️ Parcial |
```

### 2. **Documentação Individual dos Agentes**

#### Agentes Funcionais (precisam docs completas):
1. **master-agent.md** (Abaporu) ✅
2. **investigator-agent.md** (Zumbi) ✅
3. **analyst-agent.md** (Anita) ✅
4. **reporter-agent.md** (Tiradentes) ✅
5. **semantic-router.md** (Senna) ✅
6. **memory-agent.md** (Nanã) ✅
7. **textual-agent.md** (Machado) - CRIAR
8. **social-justice-agent.md** (Dandara) - CRIAR

#### Agentes Parciais (marcar como "Em Desenvolvimento"):
- Todos os outros devem ter nota indicando implementação parcial

### 3. **docs/architecture/**
Atualizar com:
- Arquitetura real de 8 agentes funcionais
- Sistema de memória com ChromaDB
- Integração Prometheus/Grafana
- Pipeline de ML com SHAP/LIME
- Cache multi-camada (Memory → Redis → DB)

### 4. **docs/api/**
Sincronizar com endpoints reais:
- `/api/v1/investigations`
- `/api/v1/agents/*`
- `/health/metrics`
- Autenticação JWT real
- Rate limiting implementado

### 5. **docs/ml/**
Adicionar documentação sobre:
- Detecção de anomalias com FFT
- Análise espectral implementada
- Coeficientes sociais (Gini, Atkinson, etc.)
- SHAP/LIME para interpretabilidade

## 🚀 Plano de Ação

### Opção 1: Migração Completa (Recomendada)
1. Mover Docusaurus para `cidadao.ai-backend/docs-site/`
2. Automatizar geração de docs do código
3. GitHub Actions para deploy automático
4. Remover repositório separado

### Opção 2: Sincronização Manual
1. Criar script de sincronização
2. GitHub Actions para verificar consistência
3. Atualizar manualmente conforme mudanças

### Opção 3: Documentação Unificada
1. Manter apenas docs técnicas no backend
2. Usar MkDocs ou similar (mais simples)
3. Deploy junto com o backend

## 📝 Exemplo de Documentação Atualizada

### Para Agente Funcional:
```markdown
# 🔍 Zumbi dos Palmares - Investigator Agent

**Status**: ✅ Totalmente Funcional  
**Implementado em**: `src/agents/zumbi.py`

## Capacidades
- Detecção de anomalias estatísticas (Z-score > 2.5)
- Análise espectral com FFT
- Detecção de concentração de fornecedores
- Identificação de contratos duplicados
- Análise de padrões temporais

## Exemplo de Uso
\```python
from src.agents.zumbi import InvestigatorAgent

agent = InvestigatorAgent()
response = await agent.process(message)
\```

## Métricas de Performance
- Tempo médio de resposta: <2s
- Taxa de detecção: 85%
- Falsos positivos: <5%
```

### Para Agente Parcial:
```markdown
# 🏛️ José Bonifácio - Policy Analyst

**Status**: ⚠️ Parcialmente Implementado  
**Arquivo**: `src/agents/bonifacio.py`

## Estado Atual
- ✅ Estrutura de classes completa
- ✅ Interface definida
- ❌ Lógica de análise não implementada
- ❌ Integração com APIs governamentais pendente

## Como Contribuir
Veja [CONTRIBUTING.md](../CONTRIBUTING.md) para implementar este agente.
```

## 🔧 Ferramentas de Sincronização

### Script para Verificar Consistência:
```python
# tools/check_docs_sync.py
import os
import glob

def check_agent_docs():
    # Lista agentes no código
    code_agents = glob.glob("src/agents/*.py")
    
    # Lista docs de agentes
    doc_agents = glob.glob("../cidadao.ai-technical-docs/docs/agents/*.md")
    
    # Compara e reporta diferenças
    # ...
```

## 📅 Timeline Sugerida

1. **Semana 1**: Atualizar status dos agentes
2. **Semana 2**: Corrigir arquitetura e APIs
3. **Semana 3**: Adicionar docs dos 8 agentes funcionais
4. **Semana 4**: Implementar solução de sincronização

---

**Nota**: Este documento deve ser usado como guia para atualizar o repositório `cidadao.ai-technical-docs` ou para planejar uma migração completa.