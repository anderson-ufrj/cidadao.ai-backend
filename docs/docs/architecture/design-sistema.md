---
title: "Design e Arquitetura do Sistema"
sidebar_position: 2
description: "Documentação arquitetural abrangente do sistema multi-agente Cidadão.AI"
---

# Design e Arquitetura do Sistema

## Resumo

Este documento apresenta uma análise arquitetural abrangente do Cidadão.AI, um sistema multi-agente distribuído projetado para análise automatizada de transparência em dados do governo brasileiro. O sistema implementa uma arquitetura de microsserviços com 17 agentes especializados, empregando algoritmos de aprendizado de máquina de última geração, processamento de linguagem natural e técnicas de detecção de anomalias estatísticas. A arquitetura alcança escalabilidade horizontal, tolerância a falhas e mantém tempos de resposta sub-200ms enquanto processa milhões de registros públicos.

## 1. Visão Geral Arquitetural

### 1.1 Limites e Contexto do Sistema

```mermaid
C4Context
    title Diagrama de Contexto do Sistema - Cidadão.AI

    Person(cidadao, "Cidadão Brasileiro", "Usuários buscando transparência")
    Person(analista, "Analista Governamental", "Analistas do setor público")
    Person(jornalista, "Jornalista Investigativo", "Profissionais de mídia")
    
    System_Boundary(cidadao, "Plataforma Cidadão.AI") {
        System(backend, "API Backend", "Sistema de análise multi-agente")
        System(frontend, "Interface Web", "Camada de interação do usuário")
    }
    
    System_Ext(portal, "Portal da Transparência", "Fonte de dados governamentais")
    System_Ext(tcu, "Sistemas TCU", "Dados de auditoria federal")
    System_Ext(cgu, "Base CGU", "Dados da controladoria geral")
    
    Rel(cidadao, frontend, "Acessa", "HTTPS")
    Rel(analista, frontend, "Analisa", "HTTPS")
    Rel(jornalista, frontend, "Investiga", "HTTPS")
    
    Rel(frontend, backend, "Chama", "REST/WebSocket")
    Rel(backend, portal, "Busca", "API")
    Rel(backend, tcu, "Consulta", "API")
    Rel(backend, cgu, "Recupera", "API")
```

### 1.2 Arquitetura de Alto Nível

O sistema segue uma **arquitetura de microsserviços em camadas** com separação clara de responsabilidades:

```
┌─────────────────────────────────────────────────────────┐
│                   Camada de Apresentação                │
│              (Apps Frontend, APIs)                      │
├─────────────────────────────────────────────────────────┤
│                  Camada de Aplicação                    │
│           (Lógica de Negócio, Orquestração)            │
├─────────────────────────────────────────────────────────┤
│                    Camada de Domínio                    │
│         (Sistema Multi-Agente, Entidades Core)         │
├─────────────────────────────────────────────────────────┤
│                Camada de Infraestrutura                 │
│      (Bancos de Dados, Filas, APIs Externas)          │
└─────────────────────────────────────────────────────────┘
```

## 2. Arquitetura de Componentes

### 2.1 Componentes Principais

```mermaid
graph TB
    subgraph "Gateway API"
        GW[Gateway FastAPI]
        Auth[Serviço de Autenticação]
        RL[Limitador de Taxa]
    end
    
    subgraph "Sistema Multi-Agente"
        MA[Agente Mestre - Abaporu]
        IA[Agente Investigador]
        AA[Agente Analista]
        RA[Agente Repórter]
        SA[Auditor de Segurança]
        VA[Agente Validador]
        SR[Roteador Semântico - Senna]
    end
    
    subgraph "Pipeline ML"
        FE[Engenharia de Features]
        AD[Detecção de Anomalias]
        PM[Casamento de Padrões]
        XAI[Módulo de Explicabilidade]
    end
    
    subgraph "Camada de Dados"
        PG[(PostgreSQL)]
        RD[(Redis)]
        CD[(ChromaDB)]
        ES[(Elasticsearch)]
    end
    
    GW --> Auth
    GW --> RL
    GW --> MA
    MA --> SR
    SR --> IA
    SR --> AA
    SR --> RA
    IA --> AD
    AA --> PM
    AD --> XAI
    PM --> XAI
```

### 2.2 Arquitetura de Agentes

Cada agente segue um padrão arquitetural padronizado:

```python
class AgenteBase(ABC):
    """Classe base abstrata para todos os agentes do sistema."""
    
    def __init__(self, nome: str, capacidades: List[str]):
        self.nome = nome
        self.capacidades = capacidades
        self.estado = EstadoAgente.IDLE
        self.memoria = SistemaMemoria()
        self.logger = LoggerEstruturado(agente=nome)
    
    @abstractmethod
    async def processar(self, mensagem: MensagemAgente) -> RespostaAgente:
        """Processar mensagem recebida e retornar resposta."""
        pass
    
    @abstractmethod
    async def refletir(self, resultado: RespostaAgente) -> ResultadoReflexao:
        """Mecanismo de auto-reflexão para melhoria contínua."""
        pass
```

## 3. Arquitetura de Fluxo de Dados

### 3.1 Pipeline de Processamento de Requisições

```mermaid
sequenceDiagram
    participant Cliente
    participant Gateway
    participant Auth
    participant Roteador
    participant Agente
    participant ML
    participant BD
    participant Cache
    
    Cliente->>Gateway: Requisição HTTP
    Gateway->>Auth: Validar JWT
    Auth-->>Gateway: Token Válido
    
    Gateway->>Cache: Verificar Cache
    Cache-->>Gateway: Cache Miss
    
    Gateway->>Roteador: Rotear Requisição
    Roteador->>Agente: Atribuir ao Agente
    
    Agente->>ML: Processar Dados
    ML->>BD: Consultar Dados Históricos
    BD-->>ML: Retornar Dados
    
    ML-->>Agente: Resultados de Análise
    Agente-->>Roteador: Resposta do Agente
    Roteador-->>Gateway: Resposta Agregada
    
    Gateway->>Cache: Armazenar em Cache
    Gateway-->>Cliente: Resposta HTTP
```

### 3.2 Processamento Assíncrono

Para operações de longa duração, o sistema implementa uma arquitetura orientada a eventos:

```python
class OrquestradorInvestigacao:
    """Orquestra investigações multi-agente complexas."""
    
    async def iniciar_investigacao(self, requisicao: RequisicaoInvestigacao) -> str:
        # 1. Validar e enfileirar
        id_investigacao = uuid4()
        await self.fila.enfileirar(id_investigacao, requisicao)
        
        # 2. Distribuir para agentes
        tarefas = self.criar_tarefas_agente(requisicao)
        await self.distribuir_tarefas(tarefas)
        
        # 3. Retornar imediatamente
        return id_investigacao
    
    async def monitorar_progresso(self, id_investigacao: str) -> Progresso:
        # Rastreamento de progresso em tempo real
        return await self.gerenciador_estado.obter_progresso(id_investigacao)
```

## 4. Arquitetura de Escalabilidade

### 4.1 Estratégia de Escalonamento Horizontal

```yaml
# Configuração de Deploy Kubernetes
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cidadao-ai-backend
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      containers:
      - name: api
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

### 4.2 Distribuição de Carga

```mermaid
graph LR
    subgraph "Balanceador de Carga"
        LB[NGINX/Traefik]
    end
    
    subgraph "Instâncias API"
        API1[Instância API 1]
        API2[Instância API 2]
        API3[Instância API 3]
    end
    
    subgraph "Pool de Agentes"
        AP1[Pool de Agentes 1]
        AP2[Pool de Agentes 2]
        AP3[Pool de Agentes 3]
    end
    
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> AP1
    API2 --> AP2
    API3 --> AP3
```

## 5. Arquitetura de Segurança

### 5.1 Defesa em Profundidade

```
┌─────────────────────────────────────────┐
│          WAF (Web Application Firewall) │
├─────────────────────────────────────────┤
│          Terminação SSL/TLS             │
├─────────────────────────────────────────┤
│          Segurança do Gateway API       │
│    - Limitação de Taxa                  │
│    - Proteção DDoS                      │
│    - Lista Branca de IPs               │
├─────────────────────────────────────────┤
│        Camada de Autenticação           │
│    - Validação JWT                      │
│    - OAuth 2.0                         │
│    - Suporte MFA                       │
├─────────────────────────────────────────┤
│        Camada de Autorização            │
│    - RBAC                              │
│    - Permissões de Nível de Recurso    │
├─────────────────────────────────────────┤
│         Segurança da Aplicação          │
│    - Validação de Entrada              │
│    - Prevenção de SQL Injection        │
│    - Proteção XSS                      │
├─────────────────────────────────────────┤
│          Segurança de Dados             │
│    - Criptografia em Repouso           │
│    - Criptografia em Trânsito          │
│    - Anonimização de Dados            │
└─────────────────────────────────────────┘
```

### 5.2 Arquitetura de Auditoria

```python
class SistemaAuditoria:
    """Sistema abrangente de log de auditoria."""
    
    def __init__(self):
        self.logger = LoggerEstruturado("auditoria")
        self.armazenamento = ArmazenamentoAuditoria()
        self.analisador = AnalisadorAnomalias()
    
    async def registrar_evento(self, evento: EventoAuditoria) -> None:
        # Enriquecer evento com contexto
        evento.timestamp = datetime.utcnow()
        evento.id_correlacao = obter_id_correlacao()
        evento.contexto_usuario = obter_contexto_usuario()
        
        # Armazenar de forma imutável
        await self.armazenamento.anexar(evento)
        
        # Análise em tempo real
        if await self.analisador.eh_suspeito(evento):
            await self.alertar_equipe_seguranca(evento)
```

## 6. Arquitetura de Performance

### 6.1 Estratégia de Cache

```python
class CacheMultiCamada:
    """Implementa estratégia de cache L1/L2/L3."""
    
    def __init__(self):
        self.cache_l1 = CacheMemoria(tamanho_max=1000)  # Dados quentes
        self.cache_l2 = CacheRedis()                     # Dados mornos
        self.cache_l3 = CacheBancoDados()                # Dados frios
    
    async def obter(self, chave: str) -> Optional[Any]:
        # Tentar L1 primeiro
        if valor := self.cache_l1.obter(chave):
            return valor
        
        # Tentar L2
        if valor := await self.cache_l2.obter(chave):
            self.cache_l1.definir(chave, valor)
            return valor
        
        # Tentar L3
        if valor := await self.cache_l3.obter(chave):
            await self.cache_l2.definir(chave, valor)
            self.cache_l1.definir(chave, valor)
            return valor
        
        return None
```

### 6.2 Otimização de Consultas

```sql
-- Consulta otimizada com indexação adequada
CREATE INDEX CONCURRENTLY idx_investigacoes_usuario_status_criado 
ON investigacoes(usuario_id, status, criado_em DESC)
WHERE deletado_em IS NULL;

-- View materializada para agregações custosas
CREATE MATERIALIZED VIEW mv_estatisticas_anomalias AS
SELECT 
    DATE_TRUNC('day', criado_em) as data,
    tipo_anomalia,
    severidade,
    COUNT(*) as contagem,
    AVG(pontuacao_confianca) as confianca_media
FROM anomalias
GROUP BY 1, 2, 3
WITH DATA;

-- Estratégia de atualização
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_estatisticas_anomalias;
```

## 7. Padrões de Resiliência

### 7.1 Padrão Circuit Breaker

```python
class CircuitBreaker:
    """Previne falhas em cascata no sistema distribuído."""
    
    def __init__(self, limite_falhas: int = 5, timeout: int = 60):
        self.limite_falhas = limite_falhas
        self.timeout = timeout
        self.falhas = 0
        self.ultima_falha = None
        self.estado = EstadoCircuito.FECHADO
    
    async def chamar(self, func: Callable, *args, **kwargs) -> Any:
        if self.estado == EstadoCircuito.ABERTO:
            if self._deve_tentar_reset():
                self.estado = EstadoCircuito.MEIO_ABERTO
            else:
                raise ErroCircuitoAberto("Circuit breaker está ABERTO")
        
        try:
            resultado = await func(*args, **kwargs)
            self._ao_sucesso()
            return resultado
        except Exception as e:
            self._ao_falha()
            raise e
```

### 7.2 Retry com Backoff Exponencial

```python
class PoliticaRetry:
    """Implementa lógica inteligente de retry."""
    
    def __init__(self, max_tentativas: int = 3, delay_base: float = 1.0):
        self.max_tentativas = max_tentativas
        self.delay_base = delay_base
    
    async def executar(self, func: Callable) -> Any:
        ultima_excecao = None
        
        for tentativa in range(self.max_tentativas):
            try:
                return await func()
            except ErroRecuperavel as e:
                ultima_excecao = e
                delay = self.delay_base * (2 ** tentativa)
                await asyncio.sleep(delay + random.uniform(0, 0.1))
        
        raise MaxTentativasExcedidas(f"Falhou após {self.max_tentativas} tentativas") from ultima_excecao
```

## 8. Arquitetura de Observabilidade

### 8.1 Coleta de Métricas

```python
# Métricas Prometheus
duracao_investigacao = Histogram(
    'duracao_investigacao_segundos',
    'Tempo gasto processando investigações',
    labelnames=['agente', 'tipo_anomalia']
)

anomalias_detectadas = Counter(
    'anomalias_detectadas_total',
    'Número total de anomalias detectadas',
    labelnames=['tipo', 'severidade']
)

utilizacao_agente = Gauge(
    'utilizacao_agente_ratio',
    'Utilização atual do agente',
    labelnames=['nome_agente']
)
```

### 8.2 Rastreamento Distribuído

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class AgenteRastreado(AgenteBase):
    """Agente com capacidades de rastreamento distribuído."""
    
    async def processar(self, mensagem: MensagemAgente) -> RespostaAgente:
        with tracer.start_as_current_span(
            f"{self.nome}.processar",
            attributes={
                "agente.nome": self.nome,
                "mensagem.tipo": mensagem.tipo,
                "mensagem.id": mensagem.id
            }
        ) as span:
            try:
                resultado = await self._processar_interno(mensagem)
                span.set_status(Status(StatusCode.OK))
                return resultado
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR))
                raise
```

## 9. Arquitetura de Deploy

### 9.1 Orquestração de Containers

```yaml
# Docker Compose para Desenvolvimento
version: '3.8'
services:
  api:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/cidadao
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
      - elasticsearch
    
  postgres:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    
  elasticsearch:
    image: elasticsearch:8.11.3
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
```

### 9.2 Deploy de Produção

```mermaid
graph TB
    subgraph "Internet"
        Usuarios[Usuários]
    end
    
    subgraph "CDN"
        CF[Cloudflare]
    end
    
    subgraph "Balanceador de Carga"
        NLB[Network LB]
    end
    
    subgraph "Cluster Kubernetes"
        subgraph "Ingress"
            NG[NGINX Ingress]
        end
        
        subgraph "Serviços"
            API[Pods API]
            WS[Pods WebSocket]
            WK[Pods Worker]
        end
        
        subgraph "Dados"
            PG[PostgreSQL]
            RD[Redis]
            ES[Elasticsearch]
        end
    end
    
    Usuarios --> CF
    CF --> NLB
    NLB --> NG
    NG --> API
    NG --> WS
    API --> WK
    API --> PG
    API --> RD
    WK --> ES
```

## 10. Considerações Arquiteturais Futuras

### 10.1 Caminho de Migração para Microsserviços

1. **Fase 1**: Extrair serviço de autenticação
2. **Fase 2**: Separar orquestração de agentes
3. **Fase 3**: Serviço independente de pipeline ML
4. **Fase 4**: Serviço dedicado de relatórios

### 10.2 Evolução Tecnológica

- **Gateway GraphQL**: Para consultas flexíveis do cliente
- **gRPC**: Para comunicação inter-serviços
- **Apache Kafka**: Para streaming de eventos
- **Operadores Kubernetes**: Para gerenciamento automatizado

---

Esta documentação arquitetural serve como referência autoritativa para decisões de design do sistema, padrões de implementação e evolução futura da plataforma Cidadão.AI.