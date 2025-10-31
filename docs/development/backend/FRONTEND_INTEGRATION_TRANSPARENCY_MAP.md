# Guia de Integração Frontend - Mapa de Transparência

**Data**: 2025-10-23
**Autor**: Anderson Henrique da Silva
**Para**: Equipe Frontend (Next.js)

---

## 🎯 Objetivo

Este documento descreve como o frontend deve consumir os dados do **Mapa de Cobertura de APIs de Transparência** para substituir os dados mockados pelo componente de mapa já implementado.

---

## 📡 Endpoint Principal

### `GET /api/v1/transparency/coverage/map`

**URL Produção**:
```
https://cidadao-api-production.up.railway.app/api/v1/transparency/coverage/map
```

**URL Desenvolvimento Local**:
```
http://localhost:8000/api/v1/transparency/coverage/map
```

### Características
- ✅ **Resposta rápida**: <100ms (dados em cache)
- 🔄 **Atualização automática**: A cada 6 horas via Celery Beat
- 📦 **Cache incluído**: Metadados de idade do cache na resposta
- ❄️ **Cold start**: Primeira requisição pode levar 30-60s (gera cache)

---

## 📊 Estrutura da Resposta JSON

### Exemplo Completo de Resposta

```json
{
  "last_update": "2025-10-23T15:30:00.000000",
  "cache_info": {
    "cached": true,
    "last_update": "2025-10-23T15:30:00.000000",
    "age_minutes": 45,
    "age_hours": 0.8
  },
  "states": {
    "SP": {
      "name": "São Paulo",
      "apis": [
        {
          "id": "SP-tce",
          "name": "TCE São Paulo",
          "type": "tce",
          "status": "healthy",
          "response_time_ms": 234.5,
          "last_check": "2025-10-23T15:29:50.000000",
          "error": null,
          "error_details": {},
          "coverage": ["Contratos", "Despesas", "Receitas"],
          "action": ""
        },
        {
          "id": "SP-ckan",
          "name": "Portal CKAN São Paulo",
          "type": "ckan",
          "status": "healthy",
          "response_time_ms": 156.2,
          "last_check": "2025-10-23T15:29:51.000000",
          "error": null,
          "error_details": {},
          "coverage": ["Datasets diversos"],
          "action": ""
        }
      ],
      "overall_status": "healthy",
      "coverage_percentage": 100.0,
      "color": "#22c55e"
    },
    "MG": {
      "name": "Minas Gerais",
      "apis": [
        {
          "id": "MG-tce",
          "name": "TCE Minas Gerais",
          "type": "tce",
          "status": "unhealthy",
          "response_time_ms": 93018.4,
          "last_check": "2025-10-23T15:28:00.000000",
          "error": "Timeout - Portal redesenhado sem API",
          "error_details": {
            "type": "timeout",
            "legal_violation": "Decreto MG 48.383/2022 Art. 22"
          },
          "coverage": [],
          "action": "Pedido LAI protocolado"
        }
      ],
      "overall_status": "unhealthy",
      "coverage_percentage": 0.0,
      "color": "#ef4444"
    },
    "GO": {
      "name": "Goiás",
      "apis": [
        {
          "id": "GO-ckan",
          "name": "Portal CKAN Goiás",
          "type": "ckan",
          "status": "healthy",
          "response_time_ms": 189.3,
          "last_check": "2025-10-23T15:29:45.000000",
          "error": null,
          "error_details": {},
          "coverage": ["Dados Abertos"],
          "action": ""
        }
      ],
      "overall_status": "healthy",
      "coverage_percentage": 100.0,
      "color": "#22c55e"
    }
  },
  "summary": {
    "total_states": 27,
    "states_with_apis": 13,
    "states_working": 9,
    "states_degraded": 1,
    "states_no_api": 14,
    "overall_coverage_percentage": 52.94,
    "api_breakdown": {
      "healthy": 9,
      "degraded": 2,
      "unhealthy": 6,
      "total": 17
    }
  },
  "issues": [
    {
      "severity": "critical",
      "title": "TCE-MG removeu API no redesign do portal",
      "description": "Portal de Dados Abertos do TCE-MG não oferece API REST, apenas visualização web. Violação do Decreto Estadual 48.383/2022.",
      "affected_states": ["MG"],
      "action": "Pedido LAI protocolado - Acompanhe: github.com/anderson-ufrj/cidadao.ai/issues/MG-TCE",
      "legal_basis": "Decreto MG 48.383/2022, Art. 22"
    },
    {
      "severity": "high",
      "title": "6 estados com problemas de infraestrutura",
      "description": "Múltiplas APIs estaduais offline ou com timeout extremo",
      "affected_states": ["RJ", "PE", "CE", "RO", "BA"],
      "action": "Monitoramento ativo - Problemas de infraestrutura estadual não fixáveis do nosso lado"
    }
  ],
  "call_to_action": {
    "title": "Cobre Transparência do Seu Estado",
    "description": "Seu estado não tem API de transparência? Protocole um pedido via Lei de Acesso à Informação!",
    "guide_url": "https://docs.cidadao.ai/activism/lai-request-guide"
  }
}
```

---

## 🎨 Mapeamento de Cores por Status

### Status do Estado (`overall_status`)

| Status | Cor Hexadecimal | Classe CSS | Descrição |
|--------|----------------|------------|-----------|
| `healthy` | `#22c55e` | `bg-green-500` | 100% das APIs funcionando |
| `degraded` | `#f59e0b` | `bg-yellow-500` | Algumas APIs funcionando |
| `unhealthy` | `#ef4444` | `bg-red-500` | Nenhuma API funcionando |
| `no_api` | `#6b7280` | `bg-gray-500` | Estado sem APIs mapeadas |

### Status Individual da API (`status`)

| Status | Descrição | Cor Sugerida |
|--------|-----------|--------------|
| `healthy` | API operacional | Verde `#22c55e` |
| `degraded` | API lenta ou parcialmente funcional | Amarelo `#f59e0b` |
| `unhealthy` | API com erro ou timeout | Vermelho `#ef4444` |
| `blocked` | API bloqueada (firewall, auth) | Laranja `#f97316` |
| `unknown` | Status desconhecido | Cinza `#94a3b8` |

---

## 🗺️ Como Usar os Dados no Componente de Mapa

### 1. Fetch dos Dados

```typescript
// src/services/transparencyMapService.ts
export interface TransparencyMapData {
  last_update: string;
  cache_info: {
    cached: boolean;
    last_update: string;
    age_minutes: number;
    age_hours?: number;
  };
  states: Record<string, StateData>;
  summary: SummaryStats;
  issues: Issue[];
  call_to_action: CallToAction;
}

export interface StateData {
  name: string;
  apis: APIDetail[];
  overall_status: 'healthy' | 'degraded' | 'unhealthy' | 'no_api';
  coverage_percentage: number;
  color: string;
}

export interface APIDetail {
  id: string;
  name: string;
  type: 'tce' | 'ckan' | 'state_portal' | 'federal';
  status: 'healthy' | 'degraded' | 'unhealthy' | 'blocked' | 'unknown';
  response_time_ms: number | null;
  last_check: string;
  error: string | null;
  error_details: Record<string, any>;
  coverage: string[];
  action: string;
}

export async function fetchTransparencyMap(): Promise<TransparencyMapData> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/transparency/coverage/map`
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch transparency map: ${response.statusText}`);
  }

  return response.json();
}
```

### 2. Aplicar Cores no SVG do Mapa

```tsx
// src/components/BrazilMap.tsx
import { useEffect, useState } from 'react';
import { fetchTransparencyMap, TransparencyMapData } from '@/services/transparencyMapService';

export function BrazilMap() {
  const [mapData, setMapData] = useState<TransparencyMapData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTransparencyMap()
      .then(data => {
        setMapData(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error loading map:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Carregando mapa...</div>;
  }

  if (!mapData) {
    return <div>Erro ao carregar dados</div>;
  }

  return (
    <svg viewBox="0 0 800 600" className="w-full h-full">
      {/* Para cada estado no SVG */}
      {Object.entries(mapData.states).map(([stateCode, stateData]) => (
        <path
          key={stateCode}
          d={STATE_PATHS[stateCode]} // Seus paths SVG existentes
          fill={stateData.color}
          stroke="#fff"
          strokeWidth="2"
          className="cursor-pointer hover:opacity-80 transition-opacity"
          onClick={() => handleStateClick(stateCode)}
        />
      ))}

      {/* Estados sem dados aparecem em cinza */}
      {STATES_WITHOUT_DATA.map(stateCode => (
        <path
          key={stateCode}
          d={STATE_PATHS[stateCode]}
          fill="#6b7280"
          stroke="#fff"
          strokeWidth="2"
          className="cursor-pointer hover:opacity-80"
        />
      ))}
    </svg>
  );
}
```

### 3. Tooltip ao Hover

```tsx
// src/components/StateTooltip.tsx
interface StateTooltipProps {
  stateCode: string;
  stateData: StateData;
}

export function StateTooltip({ stateCode, stateData }: StateTooltipProps) {
  return (
    <div className="bg-white shadow-lg rounded-lg p-4 border border-gray-200">
      <h3 className="font-bold text-lg mb-2">
        {stateData.name} ({stateCode})
      </h3>

      <div className="space-y-2 text-sm">
        <div className="flex items-center gap-2">
          <div
            className="w-4 h-4 rounded-full"
            style={{ backgroundColor: stateData.color }}
          />
          <span className="capitalize">{stateData.overall_status}</span>
        </div>

        <div>
          <span className="font-medium">Cobertura:</span>{' '}
          {stateData.coverage_percentage.toFixed(1)}%
        </div>

        <div>
          <span className="font-medium">APIs:</span>{' '}
          {stateData.apis.length} mapeada{stateData.apis.length !== 1 ? 's' : ''}
        </div>

        <div className="text-xs text-gray-500 mt-2">
          {stateData.apis.filter(api => api.status === 'healthy').length} funcionando,{' '}
          {stateData.apis.filter(api => api.status !== 'healthy').length} com problemas
        </div>
      </div>
    </div>
  );
}
```

### 4. Modal de Detalhes ao Clicar

```tsx
// src/components/StateDetailModal.tsx
interface StateDetailModalProps {
  stateCode: string;
  stateData: StateData;
  onClose: () => void;
}

export function StateDetailModal({ stateCode, stateData, onClose }: StateDetailModalProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-2xl font-bold">
            {stateData.name} ({stateCode})
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>

        {/* Status Geral */}
        <div className="mb-6 p-4 rounded-lg" style={{ backgroundColor: `${stateData.color}20` }}>
          <div className="flex items-center gap-2 mb-2">
            <div
              className="w-6 h-6 rounded-full"
              style={{ backgroundColor: stateData.color }}
            />
            <span className="font-semibold text-lg capitalize">
              {stateData.overall_status}
            </span>
          </div>
          <p className="text-sm text-gray-700">
            Cobertura: {stateData.coverage_percentage.toFixed(1)}%
          </p>
        </div>

        {/* Lista de APIs */}
        <h3 className="font-bold text-lg mb-3">
          APIs Disponíveis ({stateData.apis.length})
        </h3>

        <div className="space-y-4">
          {stateData.apis.map(api => (
            <div key={api.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-semibold">{api.name}</h4>
                  <p className="text-sm text-gray-500">{api.type.toUpperCase()}</p>
                </div>
                <StatusBadge status={api.status} />
              </div>

              {api.response_time_ms && (
                <p className="text-sm text-gray-600">
                  Tempo de resposta: {api.response_time_ms.toFixed(0)}ms
                </p>
              )}

              {api.error && (
                <div className="mt-2 p-2 bg-red-50 rounded text-sm text-red-700">
                  <p className="font-medium">Erro:</p>
                  <p>{api.error}</p>
                </div>
              )}

              {api.action && (
                <div className="mt-2 p-2 bg-blue-50 rounded text-sm text-blue-700">
                  <p className="font-medium">Ação:</p>
                  <p>{api.action}</p>
                </div>
              )}

              {api.coverage.length > 0 && (
                <div className="mt-2">
                  <p className="text-sm font-medium text-gray-700">Dados disponíveis:</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {api.coverage.map(item => (
                      <span key={item} className="text-xs bg-gray-100 px-2 py-1 rounded">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <p className="text-xs text-gray-500 mt-2">
                Última verificação: {new Date(api.last_check).toLocaleString('pt-BR')}
              </p>
            </div>
          ))}
        </div>

        {/* Call to Action para estados sem API */}
        {stateData.overall_status === 'no_api' && (
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h4 className="font-bold text-yellow-900 mb-2">
              Estado sem API de Transparência
            </h4>
            <p className="text-sm text-yellow-800 mb-3">
              Este estado não possui API pública de transparência mapeada.
              Você pode protocolar um pedido via Lei de Acesso à Informação!
            </p>
            <a
              href="https://docs.cidadao.ai/activism/lai-request-guide"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700"
            >
              Ver Guia LAI
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## 📈 Painel de Estatísticas

```tsx
// src/components/TransparencyStats.tsx
interface TransparencyStatsProps {
  summary: SummaryStats;
}

export function TransparencyStats({ summary }: TransparencyStatsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <StatCard
        title="Estados Mapeados"
        value={summary.states_with_apis}
        total={summary.total_states}
        color="blue"
      />

      <StatCard
        title="APIs Funcionando"
        value={summary.api_breakdown.healthy}
        total={summary.api_breakdown.total}
        color="green"
      />

      <StatCard
        title="Cobertura Geral"
        value={`${summary.overall_coverage_percentage.toFixed(1)}%`}
        color="purple"
      />

      <StatCard
        title="Estados sem API"
        value={summary.states_no_api}
        color="gray"
      />
    </div>
  );
}
```

---

## ⚠️ Tratamento de Erros

### Cenários a Considerar

1. **Cold Start (primeira requisição)**:
```typescript
// Mostrar loading por até 60 segundos
const [isFirstLoad, setIsFirstLoad] = useState(true);

useEffect(() => {
  const timeout = setTimeout(() => setIsFirstLoad(false), 60000);
  return () => clearTimeout(timeout);
}, []);
```

2. **API Offline**:
```typescript
try {
  const data = await fetchTransparencyMap();
  setMapData(data);
} catch (error) {
  // Mostrar mapa com dados em cache do localStorage
  const cachedData = localStorage.getItem('transparencyMapCache');
  if (cachedData) {
    setMapData(JSON.parse(cachedData));
    setShowCacheWarning(true);
  }
}
```

3. **Cache Expirado**:
```typescript
if (mapData.cache_info.age_hours > 12) {
  // Mostrar aviso: "Dados podem estar desatualizados"
}
```

---

## 🔄 Atualização Automática (Opcional)

```typescript
// Recarregar dados a cada 30 minutos
useEffect(() => {
  const interval = setInterval(() => {
    fetchTransparencyMap().then(setMapData);
  }, 30 * 60 * 1000);

  return () => clearInterval(interval);
}, []);
```

---

## 🧪 Testando a Integração

### 1. Verificar Endpoint em Produção

```bash
curl https://cidadao-api-production.up.railway.app/api/v1/transparency/coverage/map | jq '.summary'
```

**Resposta esperada**:
```json
{
  "total_states": 27,
  "states_with_apis": 13,
  "states_working": 9,
  "overall_coverage_percentage": 52.94
}
```

### 2. Testar no Navegador

```javascript
// Console do navegador
fetch('https://cidadao-api-production.up.railway.app/api/v1/transparency/coverage/map')
  .then(r => r.json())
  .then(data => console.log('Map data:', data));
```

---

## 📦 Dados Mockados vs Dados Reais

### Substituir Mock por Dados Reais

**Antes (mockado)**:
```typescript
const mockData = {
  SP: { status: 'healthy', apis: 2 },
  RJ: { status: 'unhealthy', apis: 2 },
  // ...
};
```

**Depois (real)**:
```typescript
const { data: mapData } = useSWR(
  '/api/v1/transparency/coverage/map',
  fetchTransparencyMap,
  {
    refreshInterval: 30 * 60 * 1000, // 30 minutos
    revalidateOnFocus: false
  }
);
```

---

## 📞 Suporte

**Backend Team**:
- Endpoint: https://cidadao-api-production.up.railway.app/api/v1/transparency/coverage/map
- Documentação: `docs/technical/TRANSPARENCY_COVERAGE_MAP.md`
- Issues: GitHub Issues com tag `transparency-map`

**Atualização**: A cada 6 horas via Celery Beat (00:00, 06:00, 12:00, 18:00 UTC)

---

## 🚀 Checklist de Integração

- [ ] Criar interface TypeScript para `TransparencyMapData`
- [ ] Implementar `fetchTransparencyMap()` service
- [ ] Atualizar componente de mapa para usar cores da API
- [ ] Implementar tooltip ao hover
- [ ] Implementar modal de detalhes ao clicar
- [ ] Adicionar painel de estatísticas
- [ ] Implementar tratamento de erros
- [ ] Testar com dados reais de produção
- [ ] Adicionar loading states
- [ ] Implementar cache local (opcional)

---

**Última Atualização**: 2025-10-23
**Versão da API**: v1
**Status**: ✅ Pronto para Integração
