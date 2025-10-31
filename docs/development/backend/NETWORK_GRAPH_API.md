# Network Graph Api

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

##  🕸️ API de Grafos de Relacionamento - Guia para Frontend

**Sistema de análise de rede cross-investigation para detecção de padrões suspeitos**

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Endpoints Principais](#endpoints-principais)
3. [Modelos de Dados](#modelos-de-dados)
4. [Exemplos de Uso](#exemplos-de-uso)
5. [Visualizações](#visualizações)
6. [Integração Automática](#integração-automática)

---

## 🎯 Visão Geral

O sistema de grafos conecta **empresas**, **pessoas** e **órgãos públicos** através de **investigações**, criando uma **rede persistente de relacionamentos** que permite:

- ✅ **Análise cross-investigation**: Ver histórico completo de uma entidade
- ✅ **Detecção de redes suspeitas**: Cartéis, laranjas, concentração
- ✅ **Visualização de relacionamentos**: Grafos interativos D3.js/Cytoscape
- ✅ **Métricas de rede**: Centralidade, influência, pontes
- ✅ **Relatórios enriquecidos**: Insights baseados em investigações anteriores

---

## 🔗 Endpoints Principais

### 1. **Buscar Entidades**

```http
GET /api/v1/network/entities/search?query={texto}&limit=20
```

**Parâmetros:**
- `query` (string): Nome, CNPJ ou CPF (mínimo 3 caracteres)
- `entity_type` (opcional): `empresa`, `pessoa_fisica`, `orgao_publico`
- `limit` (int): Máximo de resultados (padrão: 20, max: 100)

**Resposta:**
```json
[
  {
    "id": "uuid-entidade",
    "entity_type": "empresa",
    "name": "Construtora XYZ LTDA",
    "cnpj": "12.345.678/0001-90",
    "total_investigations": 5,
    "total_contracts": 12,
    "total_contract_value": 1500000.50,
    "risk_score": 7.3,
    "is_sanctioned": true
  }
]
```

---

### 2. **Obter Rede de uma Entidade**

```http
GET /api/v1/network/entities/{entity_id}/network?depth=2
```

**Parâmetros:**
- `depth` (int): Profundidade da rede (1-3 níveis)

**Resposta:**
```json
{
  "nodes": [
    {
      "id": "uuid-1",
      "name": "Construtora ABC",
      "entity_type": "empresa",
      "risk_score": 7.5,
      "total_investigations": 3
    },
    {
      "id": "uuid-2",
      "name": "João Silva",
      "entity_type": "pessoa_fisica",
      "risk_score": 5.2,
      "total_investigations": 2
    }
  ],
  "edges": [
    {
      "id": "rel-uuid",
      "source": "uuid-1",
      "target": "uuid-2",
      "relationship_type": "owns",
      "strength": 0.9,
      "is_suspicious": false
    }
  ],
  "node_count": 15,
  "edge_count": 20
}
```

---

### 3. **Visualização Cytoscape.js**

```http
GET /api/v1/network/export/cytoscape/{entity_id}?depth=2
```

**Retorna JSON pronto para Cytoscape.js:**
```json
{
  "elements": {
    "nodes": [
      {
        "data": {
          "id": "uuid-1",
          "label": "Empresa ABC",
          "type": "empresa",
          "risk_score": 7.5
        }
      }
    ],
    "edges": [
      {
        "data": {
          "id": "rel-1",
          "source": "uuid-1",
          "target": "uuid-2",
          "label": "owns",
          "strength": 0.9
        }
      }
    ]
  },
  "layout": {
    "name": "cose",
    "animate": true
  },
  "style": [
    {
      "selector": "node",
      "style": {
        "label": "data(label)",
        "background-color": "#009B3A"
      }
    }
  ]
}
```

---

### 4. **Visualização D3.js Force Graph**

```http
GET /api/v1/network/export/d3/{entity_id}?depth=2
```

**Retorna JSON para D3.js:**
```json
{
  "nodes": [
    {
      "id": "uuid-1",
      "name": "Empresa ABC",
      "type": "empresa",
      "risk_score": 7.5,
      "radius": 10
    }
  ],
  "links": [
    {
      "source": "uuid-1",
      "target": "uuid-2",
      "type": "owns",
      "strength": 0.9,
      "value": 9
    }
  ]
}
```

---

### 5. **Redes Suspeitas Detectadas**

```http
GET /api/v1/network/suspicious-networks?severity=high&active_only=true
```

**Parâmetros:**
- `network_type`: `cartel`, `shell_network`, `concentration`, `fraud_ring`, `collusion`
- `severity`: `low`, `medium`, `high`, `critical`
- `active_only` (bool): Apenas redes ativas (padrão: true)

**Resposta:**
```json
[
  {
    "id": "network-uuid",
    "network_name": "Possível Cartel - Agência 12345",
    "network_type": "cartel",
    "entity_count": 5,
    "detection_reason": "5 fornecedores concentrados contratando com mesma agência",
    "confidence_score": 0.85,
    "severity": "high",
    "total_contract_value": 2500000.00,
    "suspicious_value": 500000.00,
    "investigation_ids": ["inv-1", "inv-2"],
    "is_active": true,
    "reviewed": false
  }
]
```

---

### 6. **Investigações de uma Entidade**

```http
GET /api/v1/network/entities/{entity_id}/investigations
```

**Resposta:**
```json
[
  {
    "id": "ref-uuid",
    "investigation_id": "inv-uuid",
    "role": "supplier",
    "contract_id": "contract-123",
    "contract_value": 150000.00,
    "involved_in_anomalies": true,
    "anomaly_ids": ["anomaly-1", "anomaly-2"],
    "detected_at": "2025-10-01T10:30:00Z"
  }
]
```

---

### 7. **Estatísticas Gerais**

```http
GET /api/v1/network/statistics
```

**Resposta:**
```json
{
  "total_entities": 1523,
  "total_relationships": 3456,
  "total_suspicious_networks": 12,
  "entity_types": {
    "empresa": 890,
    "pessoa_fisica": 423,
    "orgao_publico": 210
  },
  "top_entities_by_centrality": [
    {
      "id": "uuid",
      "name": "Empresa ABC",
      "entity_type": "empresa",
      "degree_centrality": 25,
      "total_investigations": 8
    }
  ],
  "recent_suspicious_networks": [
    {
      "id": "net-uuid",
      "network_name": "Cartel XYZ",
      "network_type": "cartel",
      "severity": "critical",
      "entity_count": 7
    }
  ]
}
```

---

### 8. **Revisar Rede Suspeita (Admin)**

```http
POST /api/v1/network/suspicious-networks/{network_id}/review
```

**Body:**
```json
{
  "review_notes": "Investigado pela equipe forense. Cartel confirmado. Denunciado ao MPF."
}
```

**Resposta:**
```json
{
  "status": "reviewed",
  "network_id": "net-uuid",
  "message": "Rede suspeita marcada como revisada com sucesso"
}
```

---

## 📊 Modelos de Dados

### EntityNode (Entidade)

```typescript
interface EntityNode {
  id: string;
  entity_type: 'empresa' | 'pessoa_fisica' | 'orgao_publico';
  name: string;
  cnpj?: string;
  cpf?: string;
  agency_code?: string;

  statistics: {
    total_investigations: number;
    total_contracts: number;
    total_contract_value: number;
    total_anomalies: number;
  };

  risk_score: number; // 0-10
  is_sanctioned: boolean;
  sanction_details: object;

  network_metrics: {
    degree_centrality: number;
    betweenness_centrality: number;
    closeness_centrality: number;
    eigenvector_centrality: number;
  };
}
```

### EntityRelationship (Relacionamento)

```typescript
interface EntityRelationship {
  id: string;
  source_entity_id: string;
  target_entity_id: string;
  relationship_type: 'owns' | 'manages' | 'contracts_with' | 'partners_with' | 'employs';

  strength: number; // 0-1
  confidence: number; // 0-1
  detection_count: number;

  investigation_ids: string[];
  evidence: object;

  is_suspicious: boolean;
  suspicion_reasons: string[];
}
```

### SuspiciousNetwork (Rede Suspeita)

```typescript
interface SuspiciousNetwork {
  id: string;
  network_name: string;
  network_type: 'cartel' | 'shell_network' | 'concentration' | 'fraud_ring' | 'collusion';

  entity_ids: string[];
  entity_count: number;

  detection_reason: string;
  confidence_score: number; // 0-1
  severity: 'low' | 'medium' | 'high' | 'critical';

  financial_impact: {
    total_contract_value: number;
    suspicious_value: number;
  };

  investigation_ids: string[];

  is_active: boolean;
  reviewed: boolean;
  review_notes?: string;

  graph_data: object; // Dados para visualização
}
```

---

## 💡 Exemplos de Uso

### Exemplo 1: Buscar e Visualizar Rede

```typescript
// 1. Buscar entidade
const response = await fetch('/api/v1/network/entities/search?query=Construtora ABC');
const entities = await response.json();
const entity = entities[0];

// 2. Obter rede da entidade
const networkResponse = await fetch(`/api/v1/network/entities/${entity.id}/network?depth=2`);
const networkData = await networkResponse.json();

// 3. Visualizar com D3.js
const d3Data = await fetch(`/api/v1/network/export/d3/${entity.id}?depth=2`).then(r => r.json());

// Renderizar grafo D3
const svg = d3.select('#graph');
const simulation = d3.forceSimulation(d3Data.nodes)
  .force('link', d3.forceLink(d3Data.links).id(d => d.id))
  .force('charge', d3.forceManyBody())
  .force('center', d3.forceCenter(width / 2, height / 2));
```

### Exemplo 2: Listar Redes Suspeitas

```typescript
const suspiciousResponse = await fetch('/api/v1/network/suspicious-networks?severity=high&active_only=true');
const networks = await suspiciousResponse.json();

// Exibir alertas
networks.forEach(net => {
  if (net.severity === 'critical') {
    showAlert(`🚨 ${net.network_name}: ${net.detection_reason}`);
  }
});
```

### Exemplo 3: Ver Histórico de Entidade

```typescript
const entityId = 'uuid-da-entidade';

// Detalhes completos
const entity = await fetch(`/api/v1/network/entities/${entityId}`).then(r => r.json());

// Todas as investigações
const investigations = await fetch(`/api/v1/network/entities/${entityId}/investigations`).then(r => r.json());

// Exibir linha do tempo
investigations.sort((a, b) => new Date(a.detected_at) - new Date(b.detected_at));
```

---

## 🎨 Visualizações Recomendadas

### Opção 1: Cytoscape.js (Recomendado)

```html
<div id="cy" style="width: 100%; height: 600px;"></div>

<script src="https://unpkg.com/cytoscape/dist/cytoscape.min.js"></script>
<script>
fetch(`/api/v1/network/export/cytoscape/${entityId}?depth=2`)
  .then(r => r.json())
  .then(data => {
    const cy = cytoscape({
      container: document.getElementById('cy'),
      elements: data.elements,
      style: data.style,
      layout: data.layout
    });
  });
</script>
```

### Opção 2: D3.js Force Graph

```typescript
const d3Data = await fetch(`/api/v1/network/export/d3/${entityId}?depth=2`).then(r => r.json());

const svg = d3.select('#graph')
  .attr('width', width)
  .attr('height', height);

const simulation = d3.forceSimulation(d3Data.nodes)
  .force('link', d3.forceLink(d3Data.links).id(d => d.id).distance(100))
  .force('charge', d3.forceManyBody().strength(-300))
  .force('center', d3.forceCenter(width / 2, height / 2));

// Renderizar nós e arestas...
```

### Opção 3: React Flow (Moderno)

```tsx
import ReactFlow from 'reactflow';

const NetworkGraph = ({ entityId }) => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  useEffect(() => {
    fetch(`/api/v1/network/entities/${entityId}/network?depth=2`)
      .then(r => r.json())
      .then(data => {
        const flowNodes = data.nodes.map(n => ({
          id: n.id,
          data: { label: n.name },
          position: { x: Math.random() * 500, y: Math.random() * 500 }
        }));

        const flowEdges = data.edges.map(e => ({
          id: e.id,
          source: e.source,
          target: e.target,
          label: e.type
        }));

        setNodes(flowNodes);
        setEdges(flowEdges);
      });
  }, [entityId]);

  return <ReactFlow nodes={nodes} edges={edges} />;
};
```

---

## 🤖 Integração Automática

O sistema **constrói grafos automaticamente** após cada investigação:

### Fluxo Automático:

```
Investigação Concluída
         ↓
Extração de Entidades
         ↓
Criação/Atualização de Nós no Grafo
         ↓
Criação de Relacionamentos
         ↓
Cálculo de Métricas de Rede
         ↓
Detecção de Redes Suspeitas
         ↓
Enriquecimento de Relatórios
```

### Dados Enriquecidos em Relatórios:

Quando uma entidade é encontrada em múltiplas investigações, o relatório inclui:

```json
{
  "anomaly_id": "...",
  "network_analysis": [
    {
      "entity_name": "Construtora XYZ",
      "historical_data": {
        "total_investigations": 5,
        "total_contracts": 12,
        "total_contract_value": 1500000.00,
        "risk_score": 7.3,
        "is_sanctioned": true
      },
      "network_metrics": {
        "degree_centrality": 15,
        "betweenness_centrality": 0.65
      },
      "connections": {
        "node_count": 8,
        "immediate_connections": [
          {"name": "João Silva", "type": "pessoa_fisica"},
          {"name": "Agência ABC", "type": "orgao_publico"}
        ]
      }
    }
  ],
  "cross_investigation_insights": [
    "⚠️ **Entidade Recorrente**: Construtora XYZ aparece em 5 investigações anteriores, totalizando R$ 1.500.000,00 em contratos.",
    "🚨 **Alto Risco**: Construtora XYZ tem score de risco 7.3/10, indicando histórico de irregularidades.",
    "🕸️ **Altamente Conectada**: Construtora XYZ possui 15 conexões diretas, indicando posição central na rede."
  ]
}
```

---

## 🔐 Permissões

- **GET** endpoints: Qualquer usuário autenticado
- **POST /review**: Apenas administradores
- **Network metrics**: Calculados automaticamente pelo sistema

---

## 📈 Métricas de Rede Explicadas

| Métrica | O que Significa | Uso no Frontend |
|---------|-----------------|-----------------|
| **Degree Centrality** | Número de conexões diretas | Tamanho do nó no grafo |
| **Betweenness Centrality** | Ponte entre redes | Cor especial (intermediário) |
| **Closeness Centrality** | Proximidade média | Posição no layout |
| **Eigenvector Centrality** | Influência (baseada em conexões influentes) | Destaque visual |

---

## 🎯 Casos de Uso para Frontend

### Dashboard Principal
- Mostrar estatísticas gerais (`/network/statistics`)
- Listar redes suspeitas ativas
- Top entidades por centralidade

### Página de Investigação
- Grafo de entidades da investigação específica
- Insights cross-investigation
- Links para entidades relacionadas

### Página de Entidade
- Detalhes completos da entidade
- Rede de relacionamentos interativa (Cytoscape/D3)
- Lista de todas as investigações envolvendo a entidade
- Timeline de atividades

### Página de Redes Suspeitas
- Lista filtrada de redes
- Visualização do grafo de cada rede
- Ferramenta de revisão para investigadores

---

## 🚀 Deploy

### Migration do Banco:
```bash
# Aplicar migration
alembic upgrade head

# Criar índices (já incluídos na migration)
```

### Registrar Rotas no App:
```python
# src/api/app.py
from src.api.routes import network

app.include_router(network.router)
```

---

## 📞 Suporte

Para questões sobre a API de grafos:
- **Documentação Swagger**: `/docs#/Network%20Analysis`
- **Exemplos completos**: Ver seção "Exemplos de Uso" acima

---

**🇧🇷 Feito com 💚 para investigadores brasileiros 💛**
