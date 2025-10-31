# 🕸️ Setup do Sistema de Grafos de Relacionamento

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

## 📋 Checklist de Implementação

### ✅ Arquivos Criados

```
src/
├── models/
│   └── entity_graph.py              # ✅ Modelos: EntityNode, EntityRelationship, etc.
│
├── services/
│   ├── network_analysis_service.py  # ✅ Análise de rede e detecção de padrões
│   └── graph_integration_service.py # ✅ Integração com investigações
│
├── api/
│   └── routes/
│       └── network.py               # ✅ Endpoints REST para frontend
│
alembic/
└── versions/
    └── 002_add_entity_graph_tables.py  # ✅ Migration do banco

docs/
├── NETWORK_GRAPH_API.md             # ✅ Documentação completa para frontend
└── SETUP_NETWORK_GRAPH.md           # ✅ Este arquivo
```

---

## 🚀 Passos para Ativar

### 1. Aplicar Migration do Banco

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Aplicar migration
alembic upgrade head

# Verificar tabelas criadas
psql $DATABASE_URL -c "\dt entity_*"
```

**Tabelas criadas:**
- `entity_nodes` - Entidades (empresas, pessoas, órgãos)
- `entity_relationships` - Relacionamentos entre entidades
- `entity_investigation_references` - Referências investigação-entidade
- `suspicious_networks` - Redes suspeitas detectadas

---

### 2. Registrar Rotas no App Principal

Editar `src/api/app.py`:

```python
# Adicionar import
from src.api.routes import network

# Registrar router (após outras rotas)
app.include_router(network.router)
```

Ou adicionar em `src/api/__init__.py` se usar lazy loading.

---

### 3. Atualizar Investigation Service

Editar `src/services/investigation_service_supabase.py`:

Adicionar ao final do método `_execute_investigation`:

```python
# Após completar a investigação (linha ~220)

# Build entity graph from investigation results
from src.services.graph_integration_service import get_graph_integration_service

graph_service = get_graph_integration_service(self.db)

# Extract entities from forensic results (se usar ForensicEnrichmentService)
# Ou construir lista de LegalEntity das anomalias

await graph_service.integrate_investigation_with_graph(
    investigation_id=investigation_id,
    forensic_results=forensic_results,  # Lista de ForensicAnomalyResult
    contract_data=contract_data,
)
```

---

### 4. Testar Endpoints

```bash
# Iniciar servidor
make run-dev

# Testar busca de entidades
curl "http://localhost:8000/api/v1/network/entities/search?query=construtora"

# Testar estatísticas
curl http://localhost:8000/api/v1/network/statistics

# Ver documentação
open http://localhost:8000/docs#/Network%20Analysis
```

---

### 5. Verificar Integração

Criar uma investigação e verificar se o grafo é construído:

```python
# Python shell
from src.models.entity_graph import EntityNode
from src.db.session import get_db

async with get_db() as db:
    # Verificar se entidades foram criadas
    result = await db.execute(select(EntityNode).limit(10))
    entities = result.scalars().all()

    for e in entities:
        print(f"{e.name} ({e.entity_type}) - {e.total_investigations} investigações")
```

---

## 📊 Dados para Testes

### Criar Entidades de Teste (Opcional)

```python
from src.services.network_analysis_service import NetworkAnalysisService
from src.models.forensic_investigation import LegalEntity

# Criar entidade de teste
test_entity = LegalEntity(
    name="Construtora Teste LTDA",
    entity_type="empresa",
    cnpj="12.345.678/0001-90",
)

service = NetworkAnalysisService(db)

entity_node = await service.find_or_create_entity(
    legal_entity=test_entity,
    investigation_id="test-inv-123",
    role="supplier",
    contract_value=150000.00,
)
```

---

## 🎨 Integração com Frontend

### React Component Exemplo

```tsx
import { useEffect, useState } from 'react';

export const EntityNetworkGraph = ({ entityId }) => {
  const [networkData, setNetworkData] = useState(null);

  useEffect(() => {
    fetch(`/api/v1/network/entities/${entityId}/network?depth=2`)
      .then(r => r.json())
      .then(data => setNetworkData(data));
  }, [entityId]);

  if (!networkData) return <div>Carregando rede...</div>;

  return (
    <div>
      <h3>Rede de Relacionamentos</h3>
      <p>{networkData.node_count} entidades conectadas</p>
      <p>{networkData.edge_count} relacionamentos</p>

      {/* Renderizar grafo com D3.js ou Cytoscape */}
      <NetworkVisualization data={networkData} />
    </div>
  );
};
```

### Next.js API Route

```typescript
// pages/api/network/[entityId].ts
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { entityId } = req.query;

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/network/entities/${entityId}/network?depth=2`
  );

  const data = await response.json();

  res.status(200).json(data);
}
```

---

## 🔍 Debugging

### Verificar Entidades Criadas

```sql
-- Contar entidades por tipo
SELECT entity_type, COUNT(*)
FROM entity_nodes
GROUP BY entity_type;

-- Ver entidades mais conectadas
SELECT name, entity_type, degree_centrality, total_investigations
FROM entity_nodes
ORDER BY degree_centrality DESC
LIMIT 10;
```

### Verificar Relacionamentos

```sql
-- Relacionamentos por tipo
SELECT relationship_type, COUNT(*)
FROM entity_relationships
GROUP BY relationship_type;

-- Relacionamentos suspeitos
SELECT
  er.relationship_type,
  e1.name as source_name,
  e2.name as target_name,
  er.suspicion_reasons
FROM entity_relationships er
JOIN entity_nodes e1 ON er.source_entity_id = e1.id
JOIN entity_nodes e2 ON er.target_entity_id = e2.id
WHERE er.is_suspicious = true;
```

### Verificar Redes Suspeitas

```sql
-- Redes suspeitas ativas
SELECT
  network_name,
  network_type,
  severity,
  entity_count,
  confidence_score
FROM suspicious_networks
WHERE is_active = true
ORDER BY confidence_score DESC;
```

---

## 📈 Monitoramento

### Métricas Importantes

```python
# Adicionar ao Prometheus/Grafana
from prometheus_client import Counter, Histogram

graph_entities_total = Counter(
    'graph_entities_total',
    'Total de entidades no grafo'
)

graph_relationships_total = Counter(
    'graph_relationships_total',
    'Total de relacionamentos'
)

suspicious_networks_detected = Counter(
    'suspicious_networks_detected',
    'Redes suspeitas detectadas',
    ['network_type', 'severity']
)
```

---

## 🐛 Troubleshooting

### Problema: Entidades não sendo criadas

**Solução:**
1. Verificar se `graph_integration_service` está sendo chamado
2. Verificar logs: `grep "graph_integration" logs/app.log`
3. Confirmar que `LegalEntity` tem CNPJ ou CPF preenchido

### Problema: Métricas de rede em zero

**Solução:**
1. Executar cálculo manual:
```python
from src.services.network_analysis_service import NetworkAnalysisService
service = NetworkAnalysisService(db)
await service.calculate_network_metrics()
```

### Problema: Visualização não renderiza

**Solução:**
1. Verificar formato do JSON retornado
2. Testar endpoints diretamente: `/api/v1/network/export/d3/{id}`
3. Validar bibliotecas frontend (D3.js, Cytoscape.js)

---

## 📚 Recursos Adicionais

### Documentação
- **API Completa**: `NETWORK_GRAPH_API.md`
- **Swagger UI**: `http://localhost:8000/docs#/Network%20Analysis`

### Exemplos
- **Cytoscape.js**: https://js.cytoscape.org/
- **D3.js Force Graph**: https://d3-graph-gallery.com/network.html
- **React Flow**: https://reactflow.dev/

### Bibliotecas Recomendadas (Frontend)

```json
{
  "dependencies": {
    "cytoscape": "^3.26.0",
    "d3": "^7.8.5",
    "reactflow": "^11.10.1",
    "vis-network": "^9.1.9"
  }
}
```

---

## ✅ Checklist Final

- [ ] Migration aplicada (`alembic upgrade head`)
- [ ] Rotas registradas no app
- [ ] Investigation service integrado
- [ ] Endpoints testados
- [ ] Frontend conectado
- [ ] Visualizações funcionando
- [ ] Métricas sendo calculadas
- [ ] Redes suspeitas sendo detectadas

---

## 🎯 Próximos Passos (Melhorias Futuras)

1. **ML para Detecção**
   - Treinar modelo para detectar padrões suspeitos
   - Usar embeddings de grafos (Node2Vec, GraphSAGE)

2. **Análise Temporal**
   - Evolução de redes ao longo do tempo
   - Detecção de padrões sazonais

3. **Alerts Automáticos**
   - Notificar investigadores quando nova rede suspeita é detectada
   - Webhooks para sistemas externos

4. **Export Avançado**
   - Exportar grafos para Gephi
   - Gerar relatórios PDF com visualizações

5. **Análise Preditiva**
   - Prever próximas conexões
   - Identificar entidades que podem se conectar

---

**🇧🇷 Sistema pronto para detectar cartéis, laranjas e redes de corrupção! 🕵️**
