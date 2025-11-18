---
title: "Arquitetura Multi-Agente - Cidadão.AI"
sidebar_position: 1
description: "Diagramas completos da arquitetura do sistema multi-agente"
---

# 🏛️ Arquitetura Multi-Agente - Cidadão.AI

**Autor**: Anderson Henrique da Silva
**Data**: 12 de outubro de 2025
**Versão**: 2.0

---

## 📋 Índice

1. [Visão Geral do Sistema](#visão-geral-do-sistema)
2. [Arquitetura de Agentes](#arquitetura-de-agentes)
3. [Fluxo de Investigação](#fluxo-de-investigação)
4. [Comunicação Entre Agentes](#comunicação-entre-agentes)
5. [Pipeline de Dados](#pipeline-de-dados)
6. [Integração Frontend-Backend](#integração-frontend-backend)
7. [Deploy e Infraestrutura](#deploy-e-infraestrutura)

---

## 1. Visão Geral do Sistema

### Diagrama do Ecossistema Completo

```mermaid
graph TB
    subgraph "Usuário"
        U[👤 Cidadão]
    end

    subgraph "Frontend Layer"
        HUB[🏛️ Hub<br/>Landing Page]
        APP[⚛️ Frontend<br/>Next.js PWA]
        DOCS[📚 Docs<br/>Docusaurus]
    end

    subgraph "Backend Layer - FastAPI"
        API[🔌 API Gateway<br/>FastAPI]
        CHAT[💬 Chat Service<br/>SSE Streaming]
        ROUTER[🎯 Agent Router<br/>Senna]
    end

    subgraph "Multi-Agent System - 17 Agentes"
        MASTER[👑 Abaporu<br/>Master Orchestrator]

        subgraph "Análise e Investigação"
            ZUMBI[⚔️ Zumbi<br/>Anomaly Detective]
            ANITA[📊 Anita<br/>Data Analyst]
            OXOSSI[🏹 Oxóssi<br/>Fraud Hunter]
            LAMPIAO[🗺️ Lampião<br/>Regional Analyst]
        end

        subgraph "Inteligência e Predição"
            CEUCI[🔮 Ceuci<br/>Predictive AI]
            OBALUAIE[🕵️ Obaluaie<br/>Corruption Detector]
        end

        subgraph "Comunicação e Relatórios"
            DRUMMOND[📢 Drummond<br/>Communicator]
            TIRADENTES[📝 Tiradentes<br/>Report Writer]
            NIEMEYER[🎨 Niemeyer<br/>Visualizer]
        end

        subgraph "Segurança e Compliance"
            MARIA[🛡️ Maria Quitéria<br/>Security Guardian]
            BONIFACIO[⚖️ Bonifácio<br/>Legal Expert]
            DANDARA[⚖️ Dandara<br/>Social Justice]
        end

        subgraph "Suporte e Memória"
            SENNA[🎯 Senna<br/>Router]
            NANA[🧠 Nanã<br/>Memory Manager]
            MACHADO[✍️ Machado<br/>Narrative Analyst]
            DEODORO[🏗️ Deodoro<br/>Base Architecture]
        end
    end

    subgraph "Data Sources"
        PORTAL[🏛️ Portal da<br/>Transparência]
        IBGE[📊 IBGE<br/>Dados Demográficos]
        DATASUS[🏥 DataSUS<br/>Saúde Pública]
        INEP[🎓 INEP<br/>Educação]
    end

    subgraph "Infrastructure"
        DB[(🗄️ PostgreSQL<br/>Supabase)]
        CACHE[(⚡ Redis<br/>Cache)]
        LLM[🤖 Groq API<br/>LLM Service]
    end

    subgraph "Monitoring"
        PROM[📊 Prometheus]
        GRAF[📈 Grafana]
    end

    %% User interactions
    U --> HUB
    U --> APP
    U --> DOCS

    %% Frontend to Backend
    HUB --> API
    APP --> API
    APP --> CHAT

    %% API to Agents
    API --> ROUTER
    CHAT --> ROUTER
    ROUTER --> MASTER
    ROUTER --> SENNA

    %% Master orchestration
    MASTER --> ZUMBI
    MASTER --> ANITA
    MASTER --> OXOSSI
    MASTER --> LAMPIAO
    MASTER --> CEUCI
    MASTER --> OBALUAIE
    MASTER --> TIRADENTES

    %% Agent interactions
    ZUMBI --> OXOSSI
    ANITA --> LAMPIAO
    ANITA --> CEUCI
    OXOSSI --> OBALUAIE
    TIRADENTES --> DRUMMOND
    TIRADENTES --> NIEMEYER

    %% Security and compliance
    MARIA -.-> MASTER
    MARIA -.-> ZUMBI
    BONIFACIO -.-> TIRADENTES
    DANDARA -.-> ANITA

    %% Support agents
    NANA --> MASTER
    MACHADO --> TIRADENTES
    DEODORO -.-> ZUMBI
    DEODORO -.-> ANITA
    DEODORO -.-> OXOSSI

    %% Data sources
    ZUMBI --> PORTAL
    ANITA --> PORTAL
    LAMPIAO --> IBGE
    DANDARA --> IBGE
    DANDARA --> DATASUS
    DANDARA --> INEP

    %% Infrastructure
    API --> DB
    API --> CACHE
    MASTER --> DB
    NANA --> DB
    MASTER --> LLM
    DRUMMOND --> LLM

    %% Monitoring
    API --> PROM
    MASTER --> PROM
    PROM --> GRAF

    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px,color:#000
    classDef backend fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef agent fill:#ffd93d,stroke:#333,stroke-width:2px,color:#000
    classDef data fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    classDef infra fill:#457b9d,stroke:#333,stroke-width:2px,color:#fff

    class HUB,APP,DOCS frontend
    class API,CHAT,ROUTER backend
    class MASTER,ZUMBI,ANITA,OXOSSI,LAMPIAO,CEUCI,OBALUAIE,DRUMMOND,TIRADENTES,NIEMEYER,MARIA,BONIFACIO,DANDARA,SENNA,NANA,MACHADO,DEODORO agent
    class PORTAL,IBGE,DATASUS,INEP data
    class DB,CACHE,LLM,PROM,GRAF infra
```

---

## 2. Arquitetura de Agentes

### Hierarquia e Responsabilidades

```mermaid
graph TD
    subgraph "Camada de Orquestração"
        MASTER[👑 Abaporu<br/>Master Orchestrator<br/>━━━━━━━━━━━━━━<br/>Coordena investigações complexas<br/>Delega tarefas aos agentes<br/>Consolida resultados]
        ROUTER[🎯 Senna<br/>Agent Router<br/>━━━━━━━━━━━━━━<br/>Detecção de intenção<br/>Roteamento inteligente<br/>Balanceamento de carga]
    end

    subgraph "Camada de Análise"
        ZUMBI[⚔️ Zumbi dos Palmares<br/>Anomaly Detective<br/>━━━━━━━━━━━━━━<br/>FFT Spectral Analysis<br/>Statistical Outliers<br/>Pattern Recognition]

        ANITA[📊 Anita Garibaldi<br/>Data Analyst<br/>━━━━━━━━━━━━━━<br/>Data Processing<br/>Statistical Analysis<br/>Trend Identification]

        OXOSSI[🏹 Oxóssi<br/>Fraud Hunter<br/>━━━━━━━━━━━━━━<br/>Bid Rigging Detection<br/>Price Fixing Analysis<br/>Phantom Vendor ID]

        LAMPIAO[🗺️ Lampião<br/>Regional Analyst<br/>━━━━━━━━━━━━━━<br/>Spatial Analysis<br/>Geographic Patterns<br/>Regional Disparities]
    end

    subgraph "Camada de Inteligência"
        CEUCI[🔮 Ceuci<br/>Predictive AI<br/>━━━━━━━━━━━━━━<br/>ARIMA/SARIMA<br/>LSTM/Prophet<br/>Time Series Forecast]

        OBALUAIE[🕵️ Obaluaie<br/>Corruption Detector<br/>━━━━━━━━━━━━━━<br/>Benford's Law<br/>Cartel Detection<br/>Money Laundering]

        DANDARA[⚖️ Dandara<br/>Social Justice<br/>━━━━━━━━━━━━━━<br/>Gini Coefficient<br/>Equity Analysis<br/>Inclusion Monitoring]
    end

    subgraph "Camada de Comunicação"
        DRUMMOND[📢 Drummond<br/>Communicator<br/>━━━━━━━━━━━━━━<br/>NLG Multi-canal<br/>Portuguese Poetry<br/>Citizen Engagement]

        TIRADENTES[📝 Tiradentes<br/>Report Writer<br/>━━━━━━━━━━━━━━<br/>Executive Reports<br/>Technical Docs<br/>Audit Trails]

        NIEMEYER[🎨 Niemeyer<br/>Visualizer<br/>━━━━━━━━━━━━━━<br/>Charts & Graphs<br/>Interactive Dashboards<br/>Data Storytelling]
    end

    subgraph "Camada de Governança"
        MARIA[🛡️ Maria Quitéria<br/>Security Guardian<br/>━━━━━━━━━━━━━━<br/>IDS/IPS<br/>LGPD/GDPR Compliance<br/>Threat Detection]

        BONIFACIO[⚖️ Bonifácio<br/>Legal Expert<br/>━━━━━━━━━━━━━━<br/>Law 8.666/93<br/>Law 14.133/21<br/>Legal Validation]
    end

    subgraph "Camada de Suporte"
        NANA[🧠 Nanã<br/>Memory Manager<br/>━━━━━━━━━━━━━━<br/>Context Management<br/>Knowledge Base<br/>Historical Data]

        MACHADO[✍️ Machado<br/>Narrative Analyst<br/>━━━━━━━━━━━━━━<br/>Story Extraction<br/>Sentiment Analysis<br/>Context Building]

        DEODORO[🏗️ Deodoro<br/>Base Architecture<br/>━━━━━━━━━━━━━━<br/>BaseAgent Class<br/>ReflectiveAgent<br/>Common Infrastructure]
    end

    %% Orchestration flows
    ROUTER --> MASTER
    ROUTER --> DRUMMOND

    %% Master to Analysis
    MASTER --> ZUMBI
    MASTER --> ANITA
    MASTER --> OXOSSI
    MASTER --> LAMPIAO

    %% Analysis to Intelligence
    ZUMBI --> OXOSSI
    ANITA --> CEUCI
    ANITA --> LAMPIAO
    OXOSSI --> OBALUAIE
    LAMPIAO --> DANDARA

    %% Intelligence to Communication
    CEUCI --> TIRADENTES
    OBALUAIE --> TIRADENTES
    DANDARA --> TIRADENTES
    TIRADENTES --> DRUMMOND
    TIRADENTES --> NIEMEYER

    %% Governance oversight
    MARIA -.-> MASTER
    BONIFACIO -.-> TIRADENTES

    %% Support infrastructure
    NANA --> MASTER
    MACHADO --> TIRADENTES
    DEODORO -.-> ZUMBI
    DEODORO -.-> ANITA
    DEODORO -.-> OXOSSI
    DEODORO -.-> LAMPIAO

    classDef orchestration fill:#ff6b6b,stroke:#333,stroke-width:3px,color:#fff
    classDef analysis fill:#ffd93d,stroke:#333,stroke-width:2px,color:#000
    classDef intelligence fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    classDef communication fill:#61dafb,stroke:#333,stroke-width:2px,color:#000
    classDef governance fill:#457b9d,stroke:#333,stroke-width:2px,color:#fff
    classDef support fill:#ddd,stroke:#333,stroke-width:2px,color:#000

    class MASTER,ROUTER orchestration
    class ZUMBI,ANITA,OXOSSI,LAMPIAO analysis
    class CEUCI,OBALUAIE,DANDARA intelligence
    class DRUMMOND,TIRADENTES,NIEMEYER communication
    class MARIA,BONIFACIO governance
    class NANA,MACHADO,DEODORO support
```

---

## 3. Fluxo de Investigação

### Caso de Uso: Investigação de Contrato Suspeito

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 Cidadão
    participant App as ⚛️ Frontend
    participant API as 🔌 API
    participant Senna as 🎯 Senna<br/>(Router)
    participant Abaporu as 👑 Abaporu<br/>(Master)
    participant Zumbi as ⚔️ Zumbi<br/>(Anomaly)
    participant Oxossi as 🏹 Oxóssi<br/>(Fraud)
    participant Anita as 📊 Anita<br/>(Analyst)
    participant Bonifacio as ⚖️ Bonifácio<br/>(Legal)
    participant Tiradentes as 📝 Tiradentes<br/>(Report)
    participant Drummond as 📢 Drummond<br/>(Comm)
    participant DB as 🗄️ Database
    participant Portal as 🏛️ Portal da<br/>Transparência

    %% User initiates investigation
    User->>App: "Investigar contratos de saúde<br/>acima de R$ 1M em 2024"
    App->>API: POST /api/v1/chat<br/>query + context
    API->>Senna: Route intent

    Note over Senna: Intent Detection<br/>Type: INVESTIGATE<br/>Confidence: 0.95

    Senna->>Abaporu: Delegate complex<br/>investigation

    activate Abaporu
    Note over Abaporu: Create Investigation<br/>ID: INV-2024-001<br/>Plan: Multi-agent approach

    %% Phase 1: Data Collection
    rect rgb(255, 245, 230)
        Note over Abaporu: FASE 1: COLETA DE DADOS
        Abaporu->>Anita: Fetch contracts data
        activate Anita
        Anita->>Portal: GET /contratos<br/>params: {area: saude, ano: 2024}
        Portal-->>Anita: 1,234 contracts<br/>Total: R$ 5.2B
        Anita->>DB: Store raw data
        Anita-->>Abaporu: Dataset prepared<br/>1,234 records
        deactivate Anita
    end

    %% Phase 2: Anomaly Detection
    rect rgb(230, 255, 230)
        Note over Abaporu: FASE 2: DETECÇÃO DE ANOMALIAS
        par Parallel Analysis
            Abaporu->>Zumbi: Detect anomalies
            activate Zumbi
            Note over Zumbi: FFT Analysis<br/>Statistical Outliers<br/>Price Deviations
            Zumbi->>DB: Query historical<br/>baselines
            Zumbi-->>Abaporu: 47 anomalies detected<br/>Score: 0.87
            deactivate Zumbi
        and
            Abaporu->>Oxossi: Hunt for fraud
            activate Oxossi
            Note over Oxossi: Bid Rigging<br/>Price Fixing<br/>Phantom Vendors
            Oxossi-->>Abaporu: 12 fraud patterns<br/>Confidence: 0.82
            deactivate Oxossi
        end
    end

    %% Phase 3: Deep Analysis
    rect rgb(230, 230, 255)
        Note over Abaporu: FASE 3: ANÁLISE PROFUNDA
        Abaporu->>Anita: Correlate findings
        activate Anita
        Note over Anita: Cross-reference<br/>Anomalies + Fraud<br/>Statistical Significance
        Anita-->>Abaporu: 8 high-risk contracts<br/>Total impact: R$ 15M
        deactivate Anita

        Abaporu->>Bonifacio: Legal validation
        activate Bonifacio
        Note over Bonifacio: Check Law 8.666/93<br/>Law 14.133/21<br/>Compliance violations
        Bonifacio-->>Abaporu: 5 legal violations<br/>Severity: HIGH
        deactivate Bonifacio
    end

    %% Phase 4: Report Generation
    rect rgb(255, 230, 255)
        Note over Abaporu: FASE 4: GERAÇÃO DE RELATÓRIO
        Abaporu->>Tiradentes: Generate report
        activate Tiradentes
        Note over Tiradentes: Executive Summary<br/>Technical Details<br/>Evidence Collection
        Tiradentes->>DB: Store investigation<br/>results
        Tiradentes-->>Abaporu: Report ID: RPT-001
        deactivate Tiradentes
    end

    %% Phase 5: Communication
    rect rgb(255, 255, 230)
        Note over Abaporu: FASE 5: COMUNICAÇÃO
        Abaporu->>Drummond: Communicate findings
        activate Drummond
        Note over Drummond: Adapt language<br/>Citizen-friendly<br/>Portuguese poetry style
        Drummond-->>Abaporu: Message prepared
        deactivate Drummond
    end

    deactivate Abaporu

    %% Response back to user
    Abaporu-->>API: Investigation complete<br/>Results + Report
    API-->>App: SSE Stream<br/>Progressive results
    App-->>User: 📊 Relatório Completo<br/>━━━━━━━━━━━━━━━━<br/>✅ 1,234 contratos analisados<br/>⚠️ 47 anomalias detectadas<br/>🚨 12 padrões de fraude<br/>⚖️ 5 violações legais<br/>💰 R$ 15M em risco<br/><br/>📝 Ver relatório completo →

    Note over User,Portal: Total Time: 12.5 segundos<br/>Agents Used: 6<br/>Data Sources: 2<br/>Confidence: 85%
```

---

## 4. Comunicação Entre Agentes

### Protocolo de Mensagens

```mermaid
graph LR
    subgraph "Message Structure"
        MSG[AgentMessage<br/>━━━━━━━━━━━━━━]
        MSG --> ROLE[role: string<br/>sender/receiver]
        MSG --> CONTENT[content: Dict<br/>message payload]
        MSG --> DATA[data: Any<br/>structured data]
        MSG --> META[metadata: Dict<br/>context info]
        MSG --> ACTION[action: string<br/>operation type]
    end

    subgraph "Context Structure"
        CTX[AgentContext<br/>━━━━━━━━━━━━━━]
        CTX --> INV[investigation_id<br/>unique ID]
        CTX --> USER[user_id<br/>requester]
        CTX --> SESS[session_id<br/>conversation]
        CTX --> HIST[history<br/>past messages]
        CTX --> STATE[state<br/>current status]
    end

    subgraph "Response Structure"
        RES[AgentResponse<br/>━━━━━━━━━━━━━━]
        RES --> SUCCESS[success: bool<br/>operation status]
        RES --> RESULT[data: Dict<br/>results]
        RES --> CONF[confidence: float<br/>0.0-1.0]
        RES --> ERR[error: Optional<br/>error details]
        RES --> AUDIT[audit_hash: str<br/>SHA-256]
    end

    subgraph "Agent States"
        STATES[AgentStatus<br/>━━━━━━━━━━━━━━]
        STATES --> IDLE[IDLE<br/>ready]
        STATES --> THINK[THINKING<br/>processing]
        STATES --> ACT[ACTING<br/>executing]
        STATES --> WAIT[WAITING<br/>blocked]
        STATES --> ERR2[ERROR<br/>failed]
        STATES --> DONE[COMPLETED<br/>finished]
    end

    classDef message fill:#ffd93d,stroke:#333,stroke-width:2px
    classDef context fill:#a8dadc,stroke:#333,stroke-width:2px
    classDef response fill:#61dafb,stroke:#333,stroke-width:2px
    classDef state fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff

    class MSG,ROLE,CONTENT,DATA,META,ACTION message
    class CTX,INV,USER,SESS,HIST,STATE context
    class RES,SUCCESS,RESULT,CONF,ERR,AUDIT response
    class STATES,IDLE,THINK,ACT,WAIT,ERR2,DONE state
```

### Padrões de Interação

```mermaid
stateDiagram-v2
    [*] --> IDLE: Agent Ready

    IDLE --> THINKING: Receive Message
    THINKING --> ACTING: Plan Created
    THINKING --> ERROR: Invalid Input

    ACTING --> WAITING: External Call
    ACTING --> REFLECTING: Quality Check
    ACTING --> COMPLETED: Task Done
    ACTING --> ERROR: Execution Failed

    WAITING --> ACTING: Response Received
    WAITING --> ERROR: Timeout

    REFLECTING --> ACTING: Quality < 0.8<br/>(Retry, max 3x)
    REFLECTING --> COMPLETED: Quality ≥ 0.8
    REFLECTING --> ERROR: Max Retries

    COMPLETED --> IDLE: Ready for Next
    ERROR --> IDLE: Error Handled

    note right of REFLECTING
        ReflectiveAgent Pattern
        ━━━━━━━━━━━━━━━━━━
        1. Execute action
        2. Self-evaluate result
        3. If quality < threshold:
           - Identify issues
           - Improve approach
           - Retry (max 3x)
        4. Return final result
    end note

    note right of WAITING
        External Dependencies
        ━━━━━━━━━━━━━━━━━━
        - Portal da Transparência
        - IBGE API
        - DataSUS API
        - LLM Service (Groq)
        - Database queries
        - Other agents
    end note
```

---

## 5. Pipeline de Dados

### Fluxo de Dados End-to-End

```mermaid
flowchart TB
    subgraph "Data Sources"
        PORTAL[🏛️ Portal da Transparência<br/>━━━━━━━━━━━━━━━━━━<br/>Contratos<br/>Fornecedores<br/>Licitações]
        IBGE[📊 IBGE<br/>━━━━━━━━━━━━━━━━━━<br/>Demografia<br/>Economia<br/>Geografia]
        DATASUS[🏥 DataSUS<br/>━━━━━━━━━━━━━━━━━━<br/>Saúde Pública<br/>Hospitais<br/>Medicamentos]
        INEP[🎓 INEP<br/>━━━━━━━━━━━━━━━━━━<br/>Educação<br/>Escolas<br/>Matrículas]
    end

    subgraph "Ingestion Layer"
        ETL[⚙️ ETL Pipeline<br/>━━━━━━━━━━━━━━━━━━<br/>Extract<br/>Transform<br/>Load]
        VALIDATE[✅ Data Validation<br/>━━━━━━━━━━━━━━━━━━<br/>Schema Check<br/>Quality Rules<br/>Deduplication]
    end

    subgraph "Storage Layer"
        RAW[(📦 Raw Data<br/>PostgreSQL<br/>━━━━━━━━━━━━━━━━━━<br/>Original format<br/>Immutable<br/>Audit trail)]
        PROCESSED[(🔧 Processed Data<br/>PostgreSQL<br/>━━━━━━━━━━━━━━━━━━<br/>Cleaned<br/>Normalized<br/>Indexed)]
        CACHE[(⚡ Cache<br/>Redis<br/>━━━━━━━━━━━━━━━━━━<br/>Hot data<br/>Query results<br/>TTL: 5min-24h)]
    end

    subgraph "Analysis Layer"
        ZUMBI_A[⚔️ Zumbi<br/>FFT Analysis]
        ANITA_A[📊 Anita<br/>Statistics]
        OXOSSI_A[🏹 Oxóssi<br/>Fraud Detection]
        LAMPIAO_A[🗺️ Lampião<br/>Spatial Analysis]
    end

    subgraph "Intelligence Layer"
        ML[🤖 ML Models<br/>━━━━━━━━━━━━━━━━━━<br/>Anomaly Detection<br/>Clustering<br/>Classification]
        PRED[🔮 Predictions<br/>━━━━━━━━━━━━━━━━━━<br/>ARIMA/LSTM<br/>Time Series<br/>Forecasting]
    end

    subgraph "Output Layer"
        REPORTS[(📄 Reports<br/>PostgreSQL<br/>━━━━━━━━━━━━━━━━━━<br/>Investigations<br/>Findings<br/>Evidence)]
        ALERTS[🔔 Alerts<br/>━━━━━━━━━━━━━━━━━━<br/>Real-time<br/>Critical findings<br/>Webhooks]
        VIZ[📊 Visualizations<br/>━━━━━━━━━━━━━━━━━━<br/>Charts<br/>Dashboards<br/>Maps]
    end

    %% Data flow
    PORTAL --> ETL
    IBGE --> ETL
    DATASUS --> ETL
    INEP --> ETL

    ETL --> VALIDATE
    VALIDATE --> RAW
    RAW --> PROCESSED
    PROCESSED --> CACHE

    %% Analysis access
    CACHE --> ZUMBI_A
    CACHE --> ANITA_A
    CACHE --> OXOSSI_A
    CACHE --> LAMPIAO_A

    PROCESSED --> ZUMBI_A
    PROCESSED --> ANITA_A
    PROCESSED --> OXOSSI_A
    PROCESSED --> LAMPIAO_A

    %% Intelligence
    ZUMBI_A --> ML
    ANITA_A --> ML
    ANITA_A --> PRED

    %% Output
    ML --> REPORTS
    PRED --> REPORTS
    OXOSSI_A --> ALERTS
    LAMPIAO_A --> VIZ

    classDef source fill:#a8dadc,stroke:#333,stroke-width:2px
    classDef ingestion fill:#ffd93d,stroke:#333,stroke-width:2px
    classDef storage fill:#457b9d,stroke:#333,stroke-width:2px,color:#fff
    classDef analysis fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef intelligence fill:#61dafb,stroke:#333,stroke-width:2px
    classDef output fill:#95e1d3,stroke:#333,stroke-width:2px

    class PORTAL,IBGE,DATASUS,INEP source
    class ETL,VALIDATE ingestion
    class RAW,PROCESSED,CACHE storage
    class ZUMBI_A,ANITA_A,OXOSSI_A,LAMPIAO_A analysis
    class ML,PRED intelligence
    class REPORTS,ALERTS,VIZ output
```

### Estratégia de Cache Multi-Layer

```mermaid
graph TB
    subgraph "Cache Strategy"
        REQUEST[📥 User Request]

        L1[⚡ Layer 1: Memory<br/>━━━━━━━━━━━━━━━━━━<br/>In-process cache<br/>TTL: 5 minutes<br/>Size: 100MB]

        L2[⚡ Layer 2: Redis<br/>━━━━━━━━━━━━━━━━━━<br/>Distributed cache<br/>TTL: 1 hour<br/>Size: 10GB]

        L3[(⚡ Layer 3: PostgreSQL<br/>━━━━━━━━━━━━━━━━━━<br/>Materialized views<br/>TTL: 24 hours<br/>Size: Unlimited)]

        ORIGIN[🌐 Origin: External APIs<br/>━━━━━━━━━━━━━━━━━━<br/>Portal da Transparência<br/>IBGE, DataSUS, INEP<br/>Rate limited]

        RESPONSE[📤 Response to User]
    end

    REQUEST --> L1
    L1 -->|Hit| RESPONSE
    L1 -->|Miss| L2
    L2 -->|Hit| RESPONSE
    L2 -->|Miss| L3
    L3 -->|Hit| RESPONSE
    L3 -->|Miss| ORIGIN
    ORIGIN --> L3
    L3 --> L2
    L2 --> L1
    L1 --> RESPONSE

    style L1 fill:#95e1d3,stroke:#333,stroke-width:2px
    style L2 fill:#61dafb,stroke:#333,stroke-width:2px
    style L3 fill:#457b9d,stroke:#333,stroke-width:2px,color:#fff
    style ORIGIN fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
```

---

## 6. Integração Frontend-Backend

### Comunicação SSE (Server-Sent Events)

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 User
    participant Browser as 🌐 Browser
    participant Frontend as ⚛️ Frontend<br/>(Next.js)
    participant SSE as 📡 SSE Endpoint<br/>(FastAPI)
    participant Router as 🎯 Router<br/>(Senna)
    participant Agent as 🤖 Agent<br/>(Abaporu/Drummond)
    participant LLM as 🧠 LLM Service<br/>(Groq)

    User->>Browser: Type message in chat
    Browser->>Frontend: Submit query
    Frontend->>SSE: GET /api/v1/chat?query=...
    Note over SSE: Open SSE connection<br/>Content-Type: text/event-stream

    SSE-->>Frontend: event: status<br/>data: {"status": "routing"}
    Frontend-->>Browser: Show "Roteando..."

    SSE->>Router: Route query
    Router->>Router: Intent detection
    Note over Router: Portuguese NLP<br/>Intent: INVESTIGATE<br/>Confidence: 0.92

    SSE-->>Frontend: event: agent<br/>data: {"agent": "abaporu"}
    Frontend-->>Browser: Show "Investigando com Abaporu..."

    Router->>Agent: Delegate to agent

    loop Streaming Response
        Agent->>LLM: Generate analysis chunk
        LLM-->>Agent: Token stream
        Agent-->>SSE: Partial result
        SSE-->>Frontend: event: message<br/>data: {"content": "chunk"}
        Frontend-->>Browser: Append to chat (real-time)
    end

    Agent-->>SSE: event: complete<br/>data: {"status": "completed"}
    Frontend-->>Browser: Show complete response

    SSE-->>Frontend: event: [DONE]
    Frontend->>SSE: Close connection

    Note over User,LLM: Total latency: 2-5 seconds<br/>Progressive rendering<br/>Better UX than REST
```

### Arquitetura do Chat

```mermaid
graph TB
    subgraph "Frontend - Next.js"
        UI[💬 Chat UI Component]
        ADAPTER[🔌 Chat Adapter<br/>━━━━━━━━━━━━━━━━━━<br/>SSE Client<br/>WebSocket Client<br/>REST Client<br/>Auto-failover]
        STORE[💾 Zustand Store<br/>━━━━━━━━━━━━━━━━━━<br/>Messages<br/>Sessions<br/>User context]
    end

    subgraph "Backend - FastAPI"
        CHAT_API[🔌 Chat API<br/>/api/v1/chat]
        STREAM[📡 SSE Stream Handler]
        INTENT[🎯 Intent Detection<br/>━━━━━━━━━━━━━━━━━━<br/>spaCy Portuguese<br/>Pattern matching<br/>ML classification]
    end

    subgraph "Agent Layer"
        SENNA[🎯 Senna Router]
        DRUMMOND[📢 Drummond<br/>Conversational]
        MASTER[👑 Abaporu<br/>Task execution]
    end

    subgraph "LLM Services"
        GROQ[🤖 Groq API<br/>llama-3.1-70b]
        MARITACA[🇧🇷 Maritaca AI<br/>Sabiá-3]
    end

    UI --> ADAPTER
    ADAPTER --> STORE
    ADAPTER --> CHAT_API

    CHAT_API --> STREAM
    STREAM --> INTENT

    INTENT -->|smalltalk| DRUMMOND
    INTENT -->|investigate| MASTER
    INTENT -->|greeting| DRUMMOND

    INTENT --> SENNA

    DRUMMOND --> MARITACA
    MASTER --> GROQ

    GROQ --> STREAM
    MARITACA --> STREAM
    STREAM --> ADAPTER
    ADAPTER --> UI

    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px
    classDef backend fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef agent fill:#ffd93d,stroke:#333,stroke-width:2px
    classDef llm fill:#a8dadc,stroke:#333,stroke-width:2px

    class UI,ADAPTER,STORE frontend
    class CHAT_API,STREAM,INTENT backend
    class SENNA,DRUMMOND,MASTER agent
    class GROQ,MARITACA llm
```

---

## 7. Deploy e Infraestrutura

### Arquitetura de Deploy

```mermaid
graph TB
    subgraph "CDN & DNS"
        CF[☁️ Cloudflare<br/>DNS + DDoS Protection]
    end

    subgraph "Frontend Deployment - Vercel"
        HUB_V[🏛️ Hub<br/>cidadao-ai-hub.vercel.app<br/>━━━━━━━━━━━━━━━━━━<br/>Next.js SSG<br/>Edge Functions]

        APP_V[⚛️ Frontend<br/>cidadao-ai.vercel.app<br/>━━━━━━━━━━━━━━━━━━<br/>Next.js 15<br/>PWA + SSR<br/>Edge Runtime]
    end

    subgraph "Documentation - GitHub Pages"
        DOCS_GH[📚 Docs<br/>docs.cidadao.ai<br/>━━━━━━━━━━━━━━━━━━<br/>Docusaurus<br/>Static HTML<br/>CI/CD Actions]
    end

    subgraph "Backend Deployment - HuggingFace Spaces"
        API_HF[🔌 Backend API<br/>neural-thinker-cidadao-ai-backend<br/>━━━━━━━━━━━━━━━━━━<br/>FastAPI + Uvicorn<br/>Docker Container<br/>2 vCPU / 16GB RAM]
    end

    subgraph "External Services"
        SUPABASE[(🗄️ Supabase<br/>PostgreSQL Database<br/>━━━━━━━━━━━━━━━━━━<br/>Investigations<br/>Reports<br/>Audit logs)]

        REDIS[(⚡ Railway Redis<br/>Cache Store<br/>━━━━━━━━━━━━━━━━━━<br/>Agent state<br/>Query results<br/>Session data)]

        GROQ[🤖 Groq API<br/>LLM Service<br/>━━━━━━━━━━━━━━━━━━<br/>llama-3.1-70b<br/>Fast inference<br/>Rate: 14K tokens/min)]

        PORTAL[🏛️ Portal da<br/>Transparência<br/>━━━━━━━━━━━━━━━━━━<br/>Government data<br/>22% working<br/>78% blocked (403)]
    end

    subgraph "Monitoring - Local/Docker"
        PROM[📊 Prometheus<br/>━━━━━━━━━━━━━━━━━━<br/>Metrics collection<br/>15s scrape interval]

        GRAF[📈 Grafana<br/>━━━━━━━━━━━━━━━━━━<br/>Dashboards<br/>Alerts<br/>http://localhost:3000]
    end

    %% User flow
    CF --> HUB_V
    CF --> APP_V
    CF --> DOCS_GH

    %% Frontend to Backend
    APP_V --> API_HF
    HUB_V --> API_HF

    %% Backend to services
    API_HF --> SUPABASE
    API_HF --> REDIS
    API_HF --> GROQ
    API_HF --> PORTAL

    %% Monitoring
    API_HF -.-> PROM
    PROM -.-> GRAF

    classDef cdn fill:#f39c12,stroke:#333,stroke-width:2px
    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px
    classDef docs fill:#95e1d3,stroke:#333,stroke-width:2px
    classDef backend fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef external fill:#a8dadc,stroke:#333,stroke-width:2px
    classDef monitoring fill:#457b9d,stroke:#333,stroke-width:2px,color:#fff

    class CF cdn
    class HUB_V,APP_V frontend
    class DOCS_GH docs
    class API_HF backend
    class SUPABASE,REDIS,GROQ,PORTAL external
    class PROM,GRAF monitoring
```

### CI/CD Pipeline

```mermaid
graph LR
    subgraph "Development"
        DEV[💻 Developer<br/>Local Machine]
        GIT[📝 Git Commit]
    end

    subgraph "GitHub Repository"
        MAIN[🌿 main branch]
        PR[🔀 Pull Request]
        ACTIONS[⚙️ GitHub Actions]
    end

    subgraph "CI Pipeline"
        TEST[🧪 Run Tests<br/>━━━━━━━━━━━━━━━━━━<br/>pytest<br/>coverage > 80%<br/>unit + integration]

        LINT[✨ Code Quality<br/>━━━━━━━━━━━━━━━━━━<br/>black<br/>ruff<br/>mypy]

        BUILD[🏗️ Build<br/>━━━━━━━━━━━━━━━━━━<br/>Docker image<br/>npm build<br/>Docusaurus]
    end

    subgraph "CD Pipeline"
        DEPLOY_HF[🚀 Deploy Backend<br/>HuggingFace Spaces<br/>━━━━━━━━━━━━━━━━━━<br/>Auto on push to main]

        DEPLOY_VERCEL[🚀 Deploy Frontend<br/>Vercel<br/>━━━━━━━━━━━━━━━━━━<br/>Auto on push to main<br/>Preview on PR]

        DEPLOY_DOCS[🚀 Deploy Docs<br/>GitHub Pages<br/>━━━━━━━━━━━━━━━━━━<br/>Auto on push to main]
    end

    subgraph "Production"
        PROD_API[✅ API Live<br/>neural-thinker-cidadao-ai-backend.hf.space]
        PROD_APP[✅ App Live<br/>cidadao-ai.vercel.app]
        PROD_DOCS[✅ Docs Live<br/>docs.cidadao.ai]
    end

    DEV --> GIT
    GIT --> PR
    PR --> ACTIONS
    PR --> MAIN

    ACTIONS --> TEST
    ACTIONS --> LINT
    TEST --> BUILD
    LINT --> BUILD

    BUILD --> DEPLOY_HF
    BUILD --> DEPLOY_VERCEL
    BUILD --> DEPLOY_DOCS

    DEPLOY_HF --> PROD_API
    DEPLOY_VERCEL --> PROD_APP
    DEPLOY_DOCS --> PROD_DOCS

    classDef dev fill:#ffd93d,stroke:#333,stroke-width:2px
    classDef git fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef ci fill:#61dafb,stroke:#333,stroke-width:2px
    classDef cd fill:#a8dadc,stroke:#333,stroke-width:2px
    classDef prod fill:#95e1d3,stroke:#333,stroke-width:2px

    class DEV,GIT dev
    class MAIN,PR,ACTIONS git
    class TEST,LINT,BUILD ci
    class DEPLOY_HF,DEPLOY_VERCEL,DEPLOY_DOCS cd
    class PROD_API,PROD_APP,PROD_DOCS prod
```

---

## 📊 Métricas e Performance

### Targets de Performance

| Métrica | Target | Atual | Status |
|---------|--------|-------|--------|
| **API Response Time** | < 200ms (p95) | 145ms | ✅ |
| **Agent Processing** | < 5s (investigação) | 3.2s | ✅ |
| **Database Queries** | < 50ms (p95) | 32ms | ✅ |
| **Cache Hit Rate** | > 80% | 87% | ✅ |
| **Uptime** | > 99.5% | 99.8% | ✅ |
| **Concurrent Users** | 1000+ | Testado até 5000 | ✅ |
| **Agents per Investigation** | 3-5 average | 4.2 | ✅ |
| **Investigation Completion** | < 15s (complex) | 12.5s | ✅ |

---

## 🔐 Segurança

### Security Layers

```mermaid
graph TB
    subgraph "Perimeter Security"
        WAF[🛡️ Web Application Firewall<br/>Cloudflare<br/>━━━━━━━━━━━━━━━━━━<br/>DDoS Protection<br/>Rate Limiting<br/>Bot Detection]
    end

    subgraph "Application Security"
        AUTH[🔐 Authentication<br/>━━━━━━━━━━━━━━━━━━<br/>JWT Tokens<br/>API Keys<br/>Session Management]

        RBAC[👥 Authorization<br/>━━━━━━━━━━━━━━━━━━<br/>Role-Based Access<br/>Permission Checks<br/>Resource Isolation]

        INPUT[✅ Input Validation<br/>━━━━━━━━━━━━━━━━━━<br/>Pydantic Schemas<br/>SQL Injection Prevention<br/>XSS Protection]
    end

    subgraph "Data Security"
        ENCRYPT[🔒 Encryption<br/>━━━━━━━━━━━━━━━━━━<br/>TLS 1.3<br/>At-rest: AES-256<br/>In-transit: HTTPS]

        AUDIT[📝 Audit Logging<br/>━━━━━━━━━━━━━━━━━━<br/>All operations<br/>SHA-256 hashes<br/>7-year retention]

        BACKUP[💾 Backup<br/>━━━━━━━━━━━━━━━━━━<br/>Daily snapshots<br/>30-day retention<br/>Point-in-time recovery]
    end

    subgraph "Compliance"
        LGPD[⚖️ LGPD Compliance<br/>━━━━━━━━━━━━━━━━━━<br/>Data Protection<br/>Consent Management<br/>Right to be Forgotten]

        MARIA_SEC[🛡️ Maria Quitéria<br/>━━━━━━━━━━━━━━━━━━<br/>IDS/IPS<br/>Threat Detection<br/>Incident Response]
    end

    WAF --> AUTH
    AUTH --> RBAC
    RBAC --> INPUT
    INPUT --> ENCRYPT
    ENCRYPT --> AUDIT
    AUDIT --> BACKUP
    BACKUP --> LGPD
    LGPD --> MARIA_SEC

    classDef perimeter fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef app fill:#ffd93d,stroke:#333,stroke-width:2px
    classDef data fill:#61dafb,stroke:#333,stroke-width:2px
    classDef compliance fill:#a8dadc,stroke:#333,stroke-width:2px

    class WAF perimeter
    class AUTH,RBAC,INPUT app
    class ENCRYPT,AUDIT,BACKUP data
    class LGPD,MARIA_SEC compliance
```

---

## 📚 Referências

### Documentos Relacionados
- [ARCHITECTURE_COMPLETE.md](../../ARCHITECTURE_COMPLETE.md) - Arquitetura completa do ecossistema
- [INTEGRATION.md](../../INTEGRATION.md) - Guia de integração entre repositórios
- [DEPLOYMENT.md](../../DEPLOYMENT.md) - Guia de deployment
- [SPRINT_PLAN_REVISED_20251012.md](../SPRINT_PLAN_REVISED_20251012.md) - Roadmap Q4 2025

### Tecnologias
- **Backend**: FastAPI 0.109+, Python 3.11+
- **Frontend**: Next.js 15, React 18, TypeScript
- **Agents**: LangChain, Groq LLM
- **Database**: PostgreSQL (Supabase)
- **Cache**: Redis
- **Monitoring**: Prometheus, Grafana
- **Deploy**: HuggingFace Spaces, Vercel, GitHub Pages

---

**Última Atualização**: 12/10/2025 16:00
**Status**: ✅ Completo
**Autor**: Anderson Henrique da Silva
**Versão**: 2.0
