---
title: "Documentação"
sidebar_position: 1
description: "Documentação técnica do Cidadão.AI"
---

# 🤖 Agentes Especializados — Visão Geral
:::info **Sistema Multi-Agente com Identidade Brasileira**
O Cidadão.AI implementa **17 agentes especializados** com personas históricas brasileiras, cada um dedicado a aspectos específicos da análise de transparência pública.
:::
## 🏛️ Filosofia dos Agentes
### **Identidade Cultural Brasileira**
Cada agente possui uma **persona histórica brasileira**, promovendo **conexão cultural** e **engajamento cívico**:
| Agente | Persona Histórica | Especialização | Status |
|--------|-------------------|----------------|--------|
| <img src="/img/agents/abaporu.png" width="40" height="40" style={{borderRadius: '50%'}} /> **Abaporu** | Tarsila do Amaral | MasterAgent + Auto-reflexão | ✅ Ativo |
| <img src="/img/agents/zumbi.jpeg" width="40" height="40" style={{borderRadius: '50%'}} /> **Zumbi** | Zumbi dos Palmares | Investigação de anomalias | ✅ Ativo |
| <img src="/img/agents/anita.png" width="40" height="40" style={{borderRadius: '50%'}} /> **Anita** | Anita Garibaldi | Análise de dados | ✅ Ativo |
| <img src="/img/agents/tiradentes.png" width="40" height="40" style={{borderRadius: '50%'}} /> **Tiradentes** | Joaquim José da Silva Xavier | Geração de relatórios | ✅ Ativo |
| <img src="/img/agents/senna.png" width="40" height="40" style={{borderRadius: '50%'}} /> **Senna** | Ayrton Senna | Roteamento semântico | ✅ Ativo |
| <img src="/img/agents/nana.png" width="40" height="40" style={{borderRadius: '50%'}} /> **Nanã** | Divindade Iorubá | Gestão de memória | ✅ Ativo |
| <img src="/img/agents/bonifacio.png" width="40" height="40" style={{borderRadius: '50%'}} /> **Bonifácio** | José Bonifácio | Políticas públicas | ✅ Ativo |
| <img src="/img/agents/dandara.png" width="40" height="40" style={{borderRadius: '50%'}} /> **Dandara** | Dandara dos Palmares | Justiça social | ✅ Ativo |
| <img src="/img/agents/machado.png" width="40" height="40" style={{borderRadius: '50%'}} /> **Machado** | Machado de Assis | Processamento de linguagem | ✅ Ativo |
| <img src="/img/agents/obaluaie.png" width="40" height="40" style={{borderRadius: '50%'}} /> **Obaluaiê** | Divindade Iorubá | Detecção de corrupção | ✅ Ativo |
| <img src="/img/agents/niemeyer.png" width="40" height="40" style={{borderRadius: '50%'}} /> **Niemeyer** | Oscar Niemeyer | Visualização de dados | ✅ Ativo |
| <img src="/img/agents/lampiao.png" width="40" height="40" style={{borderRadius: '50%'}} /> **Lampião** | Virgulino Ferreira da Silva | Executor ETL | ✅ Ativo |
| <img src="/img/agents/ceuci.png" width="40" height="40" style={{borderRadius: '50%'}} /> **Ceuci** | Personagem do Saci | Análise preditiva | ✅ Ativo |
| <img src="/img/agents/carlos-drummond.png" width="40" height="40" style={{borderRadius: '50%'}} /> **Drummond** | Carlos Drummond de Andrade | Comunicação cidadã | ✅ Ativo |
| <img src="/img/agents/maria-quiteria.png" width="40" height="40" style={{borderRadius: '50%'}} /> **Quitéria** | Maria Quitéria | Auditoria de segurança | ✅ Ativo |
## 🧠 Arquitetura Cognitiva
```mermaid
graph TB
subgraph "🎨 MasterAgent Layer"
MA[Abaporu - Master Controller]
MA --> SR[Self-Reflection Engine]
MA --> QA[Quality Assessment]
MA --> AP[Adaptive Planning]
end
subgraph "🔍 Investigation Layer"
IA[Zumbi - Investigator]
AA[Anita - Analyst]
RA[Tiradentes - Reporter]
end
subgraph "🧠 Cognitive Layer"
SRA[Senna - Semantic Router]
MMA[Nanã - Memory Manager]
NLP[Machado - NLP Processor]
end
subgraph "🏛️ Domain Layer"
PA[Bonifácio - Policy Analyst]
JA[Dandara - Justice Advocate]
CD[Obaluaiê - Corruption Detector]
end
subgraph "🔧 Technical Layer"
DV[Niemeyer - Data Visualizer]
ETL[Lampião - ETL Executor]
PRED[Ceuci - Predictive Analyst]
COMM[Drummond - Communicator]
SEC[Quitéria - Security Auditor]
end
MA --> IA
MA --> AA
MA --> RA
SRA --> PA
SRA --> JA
SRA --> CD
MMA --> DV
MMA --> ETL
MMA --> PRED
NLP --> COMM
NLP --> SEC
```
## 📋 Próximas Seções
1. **[🎨 MasterAgent (Abaporu)](./master-agent.md)** - Orquestração e auto-reflexão
2. **[⚔️ InvestigatorAgent (Zumbi)](./investigator-agent.md)** - Detecção de anomalias
3. **[🏃‍♀️ AnalystAgent (Anita)](./analyst-agent.md)** - Análise de dados
4. **[🗡️ ReporterAgent (Tiradentes)](./reporter-agent.md)** - Geração de relatórios
5. **[🏁 SemanticRouter (Senna)](./semantic-router.md)** - Roteamento inteligente
6. **[👵 MemoryAgent (Nanã)](./memory-agent.md)** - Gestão de memória
7. **[🔧 Agentes Especializados](./specialized-agents.md)** - Demais agentes
8. **[💬 Sistema de Comunicação](./communication.md)** - Protocolos inter-agente
9. **[🪞 Sistema de Reflexão](./reflection-system.md)** - Auto-otimização
---
**Próximo:** [🎨 MasterAgent (Abaporu)](./master-agent.md) →
