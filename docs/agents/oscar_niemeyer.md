# 🏗️ Oscar Niemeyer - Arquiteto de Dados

**Status**: ⚠️ **90% Completo** (Beta - Pronto para uso com limitações conhecidas)
**Arquivo**: `src/agents/oscar_niemeyer.py`
**Tamanho**: 22KB
**Métodos Implementados**: ~15
**Testes**: ✅ Sim (`tests/unit/agents/test_oscar_niemeyer.py`)
**TODOs**: Alguns (visualizações avançadas 3D, WebGL)
**Última Atualização**: 2025-10-03 09:10:00 -03:00

---

## 🎯 Missão

Agregação inteligente de dados governamentais e geração de metadados otimizados para visualização no frontend, transformando dados brutos em insights visuais compreensíveis. Especialista em preparar dados para dashboards, gráficos e mapas interativos.

**Inspiração Cultural**: Oscar Niemeyer (1907-2012), arquiteto brasileiro modernista, criador de Brasília e ícone do design brasileiro. Conhecido por transformar conceitos abstratos em formas visuais elegantes e funcionais.

---

## 📊 Tipos de Agregação Suportados

```python
class AggregationType(Enum):
    SUM = "sum"              # Soma total
    COUNT = "count"          # Contagem
    AVERAGE = "average"      # Média aritmética
    MEDIAN = "median"        # Mediana
    MIN = "min"              # Mínimo
    MAX = "max"              # Máximo
    PERCENTILE = "percentile"  # Percentis (25, 50, 75, 95, 99)
    STDDEV = "stddev"        # Desvio padrão
    VARIANCE = "variance"    # Variância
```

---

## 📈 Tipos de Visualização

```python
class VisualizationType(Enum):
    LINE_CHART = "line_chart"      # Gráfico de linhas (séries temporais)
    BAR_CHART = "bar_chart"        # Gráfico de barras (comparações)
    PIE_CHART = "pie_chart"        # Gráfico de pizza (proporções)
    SCATTER_PLOT = "scatter_plot"  # Dispersão (correlações)
    HEATMAP = "heatmap"            # Mapa de calor (matriz 2D)
    TREEMAP = "treemap"            # Treemap (hierarquias)
    SANKEY = "sankey"              # Diagrama Sankey (fluxos)
    GAUGE = "gauge"                # Medidor (KPIs)
    MAP = "map"                    # Mapas geográficos
    TABLE = "table"                # Tabela de dados
```

**Total**: 10 tipos de visualização suportados

---

## ⏱️ Granularidades Temporais

```python
class TimeGranularity(Enum):
    MINUTE = "minute"    # Minuto a minuto
    HOUR = "hour"        # Por hora
    DAY = "day"          # Diário
    WEEK = "week"        # Semanal
    MONTH = "month"      # Mensal
    QUARTER = "quarter"  # Trimestral
    YEAR = "year"        # Anual
```

---

## 🧠 Algoritmos e Técnicas

### 1. Agregação de Dados Multidimensional

#### ✅ OLAP Cube Operations
```python
# Slice: Selecionar uma fatia específica
cube.slice(dimension="state", value="SP")

# Dice: Selecionar sub-cubo
cube.dice(state=["SP", "RJ"], year=[2023, 2024])

# Drill-down: Detalhar (estado → município)
cube.drill_down(from_="state", to="municipality")

# Roll-up: Agregar (município → estado)
cube.roll_up(from_="municipality", to="state")
```

#### ✅ Pivot Table Generation
- Múltiplas dimensões (linhas x colunas)
- Agregações aninhadas
- Grand totals e subtotals

#### ✅ Cross-tabulation
- Análise de frequência cruzada
- Chi-square para independência
- Cramér's V para força de associação

#### ✅ Hierarchical Aggregation
```
Município → Microrregião → Mesorregião → Estado → Região → País
```

#### ✅ Window Functions
```sql
-- Moving average (7 dias)
AVG(value) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)

-- Cumulative sum
SUM(value) OVER (ORDER BY date)

-- Rank
RANK() OVER (PARTITION BY category ORDER BY value DESC)
```

---

### 2. Otimização de Dados para Visualização

#### ✅ Data Sampling
```python
# Para datasets > 10k pontos
if len(data) > 10000:
    # LTTB (Largest Triangle Three Buckets)
    sampled_data = downsample_lttb(data, target_points=1000)
```

#### ✅ Binning Strategies
```python
# Equal-width bins
bins = pd.cut(data, bins=10)

# Equal-frequency bins (quantiles)
bins = pd.qcut(data, q=10)

# Custom bins
bins = [0, 1000, 10000, 100000, float('inf')]
```

#### ✅ Outlier Detection
```python
# IQR method
Q1, Q3 = data.quantile([0.25, 0.75])
IQR = Q3 - Q1
outliers = (data < Q1 - 1.5*IQR) | (data > Q3 + 1.5*IQR)

# Z-score method
z_scores = (data - data.mean()) / data.std()
outliers = np.abs(z_scores) > 3
```

#### ✅ Data Normalization
```python
# Min-Max scaling (0-1)
normalized = (data - data.min()) / (data.max() - data.min())

# Z-score standardization
standardized = (data - data.mean()) / data.std()

# Log transformation
log_data = np.log1p(data)  # log(1 + x)
```

#### ✅ Missing Value Interpolation
```python
# Linear interpolation
data_filled = data.interpolate(method='linear')

# Spline interpolation
data_filled = data.interpolate(method='spline', order=3)

# Forward fill
data_filled = data.ffill()
```

---

### 3. Análise de Séries Temporais

#### ✅ Time Series Decomposition
```python
# STL (Seasonal-Trend decomposition using Loess)
decomposition = seasonal_decompose(timeseries, model='additive')
trend = decomposition.trend
seasonal = decomposition.seasonal
residual = decomposition.resid
```

#### ✅ Moving Averages
```python
# Simple Moving Average (SMA)
sma = data.rolling(window=7).mean()

# Exponential Moving Average (EMA)
ema = data.ewm(span=7, adjust=False).mean()

# Weighted Moving Average (WMA)
weights = np.arange(1, window+1)
wma = data.rolling(window).apply(lambda x: np.dot(x, weights)/weights.sum())
```

#### ✅ Autocorrelation Analysis
- ACF (Autocorrelation Function)
- PACF (Partial Autocorrelation Function)
- Identificação de lags significativos

#### ✅ Change Point Detection
- CUSUM (Cumulative Sum)
- Bayesian change point detection
- Detecção de mudanças abruptas em tendências

---

### 4. Geração de Metadados Inteligentes

#### ✅ Automatic Axis Range Detection
```python
# Detecção inteligente de escala
if data_range < 100:
    tick_interval = 10
elif data_range < 1000:
    tick_interval = 100
else:
    tick_interval = 10 ** int(np.log10(data_range) - 1)
```

#### ✅ Color Palette Suggestions
```python
# Baseado no tipo de dados
if data_type == "diverging":
    palette = "RdYlGn"  # Vermelho-Amarelo-Verde
elif data_type == "sequential":
    palette = "Blues"
elif data_type == "categorical":
    palette = "Set3"
```

#### ✅ Chart Type Recommendations
```python
def recommend_chart(data_characteristics):
    if temporal and continuous:
        return VisualizationType.LINE_CHART
    elif categorical and numerical:
        return VisualizationType.BAR_CHART
    elif proportions:
        return VisualizationType.PIE_CHART
    elif correlation:
        return VisualizationType.SCATTER_PLOT
```

#### ✅ Data Density Analysis
```python
# Decidir visualização baseado em densidade
data_density = len(data) / (x_range * y_range)

if data_density > 0.5:
    recommended = VisualizationType.HEATMAP
else:
    recommended = VisualizationType.SCATTER_PLOT
```

---

### 5. Agregação Espacial (Geospatial)

#### ✅ Geospatial Clustering
```python
# DBSCAN para pontos geográficos
from sklearn.cluster import DBSCAN

coords = np.array([[lat, lon] for lat, lon in data])
clustering = DBSCAN(eps=0.01, min_samples=5).fit(coords)
```

#### ✅ Hexbin Aggregation
```python
# Hexagonal binning para mapas
hexbin = plt.hexbin(x=lon, y=lat, C=values, gridsize=50, reduce_C_function=np.mean)
```

#### ✅ Regional Boundary Aggregation
- Agregação por polígonos (estados, municípios)
- Spatial join operations
- Choropleth map data preparation

---

## 📋 Estrutura de Dados

### DataAggregationResult
```python
@dataclass
class DataAggregationResult:
    aggregation_id: str
    data_type: str
    aggregation_type: AggregationType
    time_granularity: Optional[TimeGranularity]
    dimensions: List[str]  # ex: ['state', 'category']
    metrics: Dict[str, float]  # ex: {'total': 1000, 'avg': 50}
    data_points: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    timestamp: datetime
```

### VisualizationMetadata
```python
@dataclass
class VisualizationMetadata:
    visualization_id: str
    title: str
    subtitle: Optional[str]
    visualization_type: VisualizationType
    x_axis: Dict[str, Any]  # {label, min, max, ticks}
    y_axis: Dict[str, Any]
    series: List[Dict[str, Any]]  # Múltiplas séries de dados
    filters: Dict[str, Any]  # Filtros aplicáveis
    options: Dict[str, Any]  # Configurações do chart
    data_url: str  # URL para buscar dados
    timestamp: datetime
```

### TimeSeriesData
```python
@dataclass
class TimeSeriesData:
    series_id: str
    metric_name: str
    time_points: List[datetime]
    values: List[float]
    aggregation_type: AggregationType
    granularity: TimeGranularity
    metadata: Dict[str, Any]
```

---

## 💻 Exemplos de Uso

### Agregar Despesas Mensais por Estado

```python
from src.agents.oscar_niemeyer import OscarNiemeyerAgent, AggregationType, TimeGranularity

# Inicializar agente
oscar = OscarNiemeyerAgent()
await oscar.initialize()

# Dados brutos de despesas
message = AgentMessage(
    content="Agregar despesas mensais por estado",
    data={
        "raw_data": expenses_dataframe,  # DataFrame com colunas: date, state, value
        "aggregation": AggregationType.SUM,
        "dimensions": ["state"],
        "time_dimension": "date",
        "time_granularity": TimeGranularity.MONTH
    }
)

response = await oscar.process(message, context)

# Resultado
print(response.data["aggregated"])
# {
#   "dimensions": ["state"],
#   "time_granularity": "MONTH",
#   "data_points": [
#     {"state": "SP", "month": "2025-01", "total": 50_000_000},
#     {"state": "SP", "month": "2025-02", "total": 48_000_000},
#     {"state": "RJ", "month": "2025-01", "total": 35_000_000},
#     ...
#   ],
#   "metrics": {
#     "total_overall": 1_500_000_000,
#     "avg_per_state": 55_555_555,
#     "max_month": 120_000_000
#   }
# }
```

### Gerar Metadados para Visualização

```python
message = AgentMessage(
    content="Gerar metadados para gráfico de linha de despesas",
    data={
        "aggregated_data": aggregation_result,
        "visualization_type": VisualizationType.LINE_CHART,
        "title": "Evolução de Despesas Públicas por Estado"
    }
)

response = await oscar.process(message, context)

# Metadados prontos para frontend
print(response.data["visualization_metadata"])
# {
#   "visualization_type": "line_chart",
#   "title": "Evolução de Despesas Públicas por Estado",
#   "x_axis": {
#     "label": "Mês",
#     "type": "datetime",
#     "min": "2025-01-01",
#     "max": "2025-12-31",
#     "format": "%b %Y"
#   },
#   "y_axis": {
#     "label": "Total de Despesas (R$)",
#     "type": "linear",
#     "min": 0,
#     "max": 60_000_000,
#     "format": ",.0f"
#   },
#   "series": [
#     {"name": "SP", "data": [...], "color": "#1f77b4"},
#     {"name": "RJ", "data": [...], "color": "#ff7f0e"},
#     {"name": "MG", "data": [...], "color": "#2ca02c"}
#   ],
#   "options": {
#     "legend": {"position": "top"},
#     "tooltip": {"enabled": True},
#     "responsive": True
#   }
# }
```

### Otimizar Dados para Mapa de Calor

```python
message = AgentMessage(
    content="Preparar heatmap de contratos por região",
    data={
        "raw_data": contracts_by_municipality,  # 5570 municípios
        "visualization_type": VisualizationType.HEATMAP,
        "optimize": True  # Aplicar binning e agregação espacial
    }
)

response = await oscar.process(message, context)

# Dados otimizados
print(response.data["optimized_data"])
# {
#   "grid_size": [50, 50],  # 2500 células vs 5570 municípios
#   "cells": [
#     {"lat_bin": 0, "lon_bin": 0, "value": 150, "count": 23},
#     {"lat_bin": 0, "lon_bin": 1, "value": 230, "count": 45},
#     ...
#   ],
#   "color_scale": {
#     "min": 0,
#     "max": 1000,
#     "palette": "YlOrRd",
#     "bins": [0, 100, 250, 500, 750, 1000]
#   }
# }
```

---

## 🧪 Testes

### Cobertura
- ✅ Testes unitários: `tests/unit/agents/test_oscar_niemeyer.py`
- ✅ Testes de integração: Visualização com dados reais
- ✅ Performance: Agregação de 100k+ registros

### Cenários Testados
1. **Agregação temporal** (dia, semana, mês, ano)
2. **Pivot tables** multidimensionais
3. **Data sampling** (LTTB) para grandes datasets
4. **Geração de metadados** para todos tipos de chart
5. **Otimização espacial** para mapas

---

## ⚠️ Limitações Conhecidas

### TODOs Pendentes

1. **Visualizações 3D** (não implementadas)
   - Surface plots, 3D scatter
   - WebGL rendering metadata

2. **Animações** (parcial)
   - Transições temporais
   - Animated transitions metadata

3. **Dashboards Compostos**
   - Layout automático de múltiplos charts
   - Responsive grid generation

### Performance

- ✅ Otimizado até 100k pontos
- ⚠️ >1M pontos: requer sampling agressivo
- ✅ Caching de agregações frequentes

---

## 🔄 Integração com Outros Agentes

### Consumidores

1. **Tiradentes (Reporter)**
   - Recebe dados agregados
   - Gera relatórios visuais

2. **Lampião (Regional)**
   - Usa agregação geográfica
   - Mapas choropleth

3. **Anita (Analyst)**
   - Consome séries temporais agregadas
   - Análise de tendências

### Saída para Frontend

- ✅ JSON estruturado otimizado
- ✅ Metadados compatíveis com Chart.js, D3.js, Plotly
- ✅ URLs de dados paginados

---

## 📊 Métricas Prometheus

```python
# Agregações realizadas
oscar_aggregations_total{type="sum", granularity="month"}

# Tempo de processamento
oscar_aggregation_duration_seconds

# Pontos de dados processados
oscar_datapoints_processed_total

# Cache hit rate
oscar_cache_hit_rate
```

---

## 🚀 Roadmap para 100%

### Alta Prioridade

1. **Implementar visualizações 3D** (Surface, 3D scatter)
2. **Adicionar animation metadata** generation
3. **Dashboard layout** automático

### Média Prioridade

4. **Integração com Superset/Metabase**
5. **Real-time streaming** data aggregation
6. **Custom color palettes** por tema governamental

---

## 📚 Referências

### Cultural
- **Oscar Niemeyer**: Arquiteto brasileiro (1907-2012)
- **Obras**: Brasília, Congresso Nacional, Museu de Arte Contemporânea de Niterói

### Técnicas
- **OLAP**: Codd et al. (1993)
- **LTTB Downsampling**: Sveinn Steinarsson (2013)
- **STL Decomposition**: Cleveland et al. (1990)

---

## 🤝 Contribuindo

Para completar os 10% restantes:

1. **Implementar 3D visualization** metadata
2. **Adicionar animation** support
3. **Dashboard composer** com layout automático

---

## ✅ Status de Produção

**Deploy**: ⚠️ Beta - Pronto para visualizações 2D
**Testes**: ✅ 90% dos cenários cobertos
**Performance**: ✅ 100k+ pontos otimizados
**Frontend Ready**: ✅ Metadados compatíveis com libs populares

**Aprovado para uso em**:
- ✅ Dashboards 2D (line, bar, pie, scatter, heatmap)
- ✅ Mapas geográficos (choropleth, hexbin)
- ✅ Tabelas de dados agregados
- ⚠️ Visualizações 3D (em desenvolvimento)

---

**Autor**: Anderson Henrique da Silva
**Manutenção**: Ativa
**Versão**: 0.90 (Beta)
**License**: Proprietary
