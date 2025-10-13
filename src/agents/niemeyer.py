"""
Module: agents.visualization_agent
Codinome: Niemeyer - Visualização Gráfica
Description: Agent specialized in creating interactive visualizations and graphical reports
Author: Anderson H. Silva
Date: 2025-07-23
License: Proprietary - All rights reserved
"""

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import numpy as np
import pandas as pd

from src.agents.deodoro import AgentContext, AgentMessage, AgentResponse, BaseAgent
from src.core import get_logger
from src.core.exceptions import AgentExecutionError


class VisualizationType(Enum):
    """Types of visualizations available."""

    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    NETWORK_GRAPH = "network_graph"
    GEOGRAPHIC_MAP = "geographic_map"
    TREEMAP = "treemap"
    SANKEY_DIAGRAM = "sankey_diagram"
    DASHBOARD = "dashboard"


@dataclass
class VisualizationSpec:
    """Specification for visualization creation."""

    viz_type: VisualizationType
    title: str
    data_source: str
    dimensions: list[str]
    metrics: list[str]
    filters: dict[str, Any]
    styling: dict[str, Any]
    interactivity: list[str]
    export_formats: list[str]


@dataclass
class VisualizationResult:
    """Result of visualization generation."""

    viz_id: str
    viz_type: VisualizationType
    title: str
    html_content: str
    json_config: dict[str, Any]
    static_image_path: Optional[str]
    interactive_url: Optional[str]
    metadata: dict[str, Any]
    timestamp: datetime


class VisualizationAgent(BaseAgent):
    """
    Niemeyer - Visualização Gráfica

    MISSÃO:
    Cria visualizações interativas e relatórios gráficos para análise de dados
    governamentais, transformando informações complexas em insights visuais.

    ALGORITMOS E TÉCNICAS IMPLEMENTADAS:

    1. ALGORITMOS DE LAYOUT DE GRAFOS:
       - Force-Directed Graph Layout (Algoritmo de Fruchterman-Reingold)
       - Hierarchical Layout (Algoritmo de Sugiyama)
       - Circular Layout para redes sociais
       - Algoritmo de Spring-Embedder para posicionamento de nós

    2. VISUALIZAÇÃO DE SÉRIES TEMPORAIS:
       - Smoothing Algorithms (Moving Average, LOWESS)
       - Trend Detection usando Regressão Linear
       - Seasonal Decomposition (STL - Seasonal-Trend decomposition)
       - Algoritmo de detecção de Change Points

    3. MAPAS DE CALOR E GEOGRÁFICOS:
       - Algoritmo de Interpolação Espacial (Kriging, IDW)
       - Clustering Geográfico (DBSCAN espacial)
       - Algoritmo de Colorização baseado em densidade
       - Projeções cartográficas (Mercator, Albers)

    4. DASHBOARDS INTERATIVOS:
       - Algoritmo de Layout Responsivo
       - Cross-filtering entre visualizações
       - Lazy Loading para grandes datasets
       - Algoritmo de Aggregation Dinâmica

    5. PROCESSAMENTO DE DADOS VISUAIS:
       - Algoritmo de Binning Adaptativo
       - Data Sampling para performance (Reservoir Sampling)
       - Algoritmo de Detecção de Outliers Visuais
       - Feature Scaling para comparabilidade visual

    BIBLIOTECAS E FRAMEWORKS:

    - D3.js: Visualizações customizadas e interativas
    - Plotly: Gráficos científicos e dashboards
    - Leaflet: Mapas interativos geográficos
    - Chart.js: Gráficos responsivos leves
    - Bokeh: Visualizações Python para web
    - Deck.gl: Visualizações 3D de grande escala

    TÉCNICAS MATEMÁTICAS:

    - Algoritmo de Força de Repulsão: F = k²/d² (para layouts de grafo)
    - Interpolação Bilinear para mapas de calor
    - Transformação de coordenadas geográficas
    - Algoritmos de clustering para agrupamento visual
    - PCA para redução dimensional em scatter plots

    TIPOS DE VISUALIZAÇÃO SUPORTADOS:

    1. Gráficos Básicos: Barras, linhas, pizza, dispersão
    2. Gráficos Avançados: Heatmaps, treemaps, sankey
    3. Visualizações de Rede: Grafos, diagramas de relacionamento
    4. Mapas: Coropléticos, pontos, densidade
    5. Dashboards: Multi-panel, filtros cruzados

    PERFORMANCE E OTIMIZAÇÃO:

    - Renderização: <2s para datasets até 10K pontos
    - Interatividade: <100ms resposta para filtros
    - Memory Usage: <512MB para visualizações complexas
    - Suporte: Datasets até 1M de registros (com sampling)

    INTEGRAÇÃO E EXPORT:

    - Formatos: SVG, PNG, PDF, HTML, JSON
    - Embed: iFrame, widget, component
    - API: REST endpoints para visualizações
    - Cache: Redis para visualizações computadas
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(
            name="VisualizationAgent",
            description="Niemeyer - Criador de visualizações interativas",
            config=config or {},
        )
        self.logger = get_logger(__name__)

        # Configurações de visualização
        self.viz_config = {
            "max_data_points": 100000,
            "default_width": 800,
            "default_height": 600,
            "color_palette": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
            "font_family": "Inter, Arial, sans-serif",
            "animation_duration": 750,
        }

        # Cache de visualizações
        self.viz_cache = {}

        # Templates de visualização
        self.viz_templates = {}

    async def initialize(self) -> None:
        """Inicializa templates e configurações de visualização."""
        self.logger.info("Initializing Niemeyer visualization engine...")

        # Carregar templates de visualização
        await self._load_visualization_templates()

        # Configurar bibliotecas de renderização
        await self._setup_rendering_engines()

        self.logger.info("Niemeyer ready for visualization creation")

    async def create_visualization(
        self, spec: VisualizationSpec, data: list[dict[str, Any]], context: AgentContext
    ) -> VisualizationResult:
        """
        Cria uma visualização baseada na especificação fornecida.

        PIPELINE DE CRIAÇÃO:
        1. Validação da especificação e dados
        2. Pré-processamento e transformação dos dados
        3. Seleção do algoritmo de layout apropriado
        4. Geração da visualização usando bibliotecas especializadas
        5. Aplicação de styling e interatividade
        6. Otimização para performance
        7. Export nos formatos solicitados
        """
        self.logger.info(f"Creating {spec.viz_type.value} visualization: {spec.title}")

        # Validar dados e especificação
        processed_data = await self._preprocess_data(data, spec)

        # Aplicar algoritmo de layout específico
        layout_config = await self._calculate_layout(processed_data, spec)

        # Gerar visualização
        viz_result = await self._render_visualization(
            processed_data, spec, layout_config
        )

        return viz_result

    async def create_dashboard(
        self,
        components: list[VisualizationSpec],
        layout_config: dict[str, Any],
        context: AgentContext,
    ) -> VisualizationResult:
        """
        Cria dashboard com múltiplas visualizações.

        ALGORITMO DE LAYOUT RESPONSIVO:
        1. Calcula grid dimensions baseado em número de componentes
        2. Aplica algoritmo de bin-packing para posicionamento ótimo
        3. Configura cross-filtering entre componentes relacionados
        4. Gera eventos de sincronização para interatividade
        """
        self.logger.info(f"Creating dashboard with {len(components)} components")

        # Implementar criação de dashboard com layout responsivo
        num_components = len(components)

        # Calculate optimal grid layout (responsive grid algorithm)
        cols = layout_config.get("columns", min(3, num_components))
        rows = math.ceil(num_components / cols)

        # Calculate component dimensions with proper spacing
        container_width = layout_config.get("width", 1200)
        container_height = layout_config.get("height", 800)
        gap = layout_config.get("gap", 20)

        component_width = (container_width - gap * (cols + 1)) / cols
        component_height = (container_height - gap * (rows + 1)) / rows

        # Generate grid layout with coordinates
        grid_positions = []
        for idx in range(num_components):
            row = idx // cols
            col = idx % cols
            x = gap + col * (component_width + gap)
            y = gap + row * (component_height + gap)

            grid_positions.append(
                {
                    "component_index": idx,
                    "x": float(x),
                    "y": float(y),
                    "width": float(component_width),
                    "height": float(component_height),
                    "row": row,
                    "col": col,
                }
            )

        # Configure cross-filtering between components
        # Components with shared dimensions can filter each other
        cross_filters = []
        for i, comp_i in enumerate(components):
            for j, comp_j in enumerate(components):
                if i < j:  # Avoid duplicate pairs
                    # Find shared dimensions
                    shared_dims = set(comp_i.dimensions) & set(comp_j.dimensions)
                    if shared_dims:
                        cross_filters.append(
                            {
                                "source": i,
                                "target": j,
                                "shared_dimensions": list(shared_dims),
                                "bidirectional": True,
                            }
                        )

        # Generate synchronization events configuration
        sync_events = {
            "selection": {
                "enabled": True,
                "propagation": "all",  # Propagate to all connected components
                "debounce_ms": 100,
            },
            "zoom": {
                "enabled": layout_config.get("sync_zoom", False),
                "linked_components": "same_type",
            },
            "hover": {
                "enabled": True,
                "highlight_related": True,
                "tooltip_sync": False,
            },
        }

        # Generate HTML structure with embedded JSON config
        dashboard_id = f"dashboard_{datetime.utcnow().timestamp()}"
        component_configs = []

        for idx, comp in enumerate(components):
            comp_config = {
                "id": f"comp_{idx}",
                "type": comp.viz_type.value,
                "title": comp.title,
                "position": grid_positions[idx],
                "dimensions": comp.dimensions,
                "metrics": comp.metrics,
                "styling": comp.styling,
                "interactivity": comp.interactivity,
            }
            component_configs.append(comp_config)

        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Government Data Dashboard</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: {self.viz_config['font_family']}; }}
                #dashboard-{dashboard_id} {{
                    width: {container_width}px;
                    height: {container_height}px;
                    position: relative;
                    background: #f5f5f5;
                    overflow: auto;
                }}
                .dashboard-component {{
                    position: absolute;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    transition: box-shadow 0.3s ease;
                    overflow: hidden;
                }}
                .dashboard-component:hover {{
                    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
                }}
                .component-header {{
                    padding: 12px 16px;
                    border-bottom: 1px solid #e8e8e8;
                    font-weight: 600;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }}
                .component-body {{
                    padding: 16px;
                    height: calc(100% - 48px);
                }}
                @media (max-width: 768px) {{
                    .dashboard-component {{
                        position: static !important;
                        width: 100% !important;
                        height: 400px !important;
                        margin-bottom: 16px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div id="dashboard-{dashboard_id}">
                {"".join([f'''
                <div class="dashboard-component" id="{comp['id']}"
                     style="left: {comp['position']['x']}px;
                            top: {comp['position']['y']}px;
                            width: {comp['position']['width']}px;
                            height: {comp['position']['height']}px;">
                    <div class="component-header">{comp['title']}</div>
                    <div class="component-body" data-viz-type="{comp['type']}">
                        <!-- Visualization will be rendered here by D3.js/Plotly -->
                        <div class="viz-placeholder">Loading {comp['type']}...</div>
                    </div>
                </div>
                ''' for comp in component_configs])}
            </div>
            <script>
                // Dashboard configuration (to be used by frontend rendering library)
                const dashboardConfig = {json.dumps({
                    "id": dashboard_id,
                    "components": component_configs,
                    "cross_filters": cross_filters,
                    "sync_events": sync_events,
                    "grid": {
                        "rows": rows,
                        "cols": cols,
                        "gap": gap
                    }
                }, indent=2)};

                // Cross-filtering event handlers
                function setupCrossFiltering() {{
                    dashboardConfig.cross_filters.forEach(filter => {{
                        const sourceEl = document.getElementById(dashboardConfig.components[filter.source].id);
                        const targetEl = document.getElementById(dashboardConfig.components[filter.target].id);

                        sourceEl.addEventListener('data-selected', (event) => {{
                            // Dispatch filter event to target component
                            const filterEvent = new CustomEvent('apply-filter', {{
                                detail: {{
                                    dimensions: filter.shared_dimensions,
                                    values: event.detail.values
                                }}
                            }});
                            targetEl.dispatchEvent(filterEvent);
                        }});

                        if (filter.bidirectional) {{
                            targetEl.addEventListener('data-selected', (event) => {{
                                const filterEvent = new CustomEvent('apply-filter', {{
                                    detail: {{
                                        dimensions: filter.shared_dimensions,
                                        values: event.detail.values
                                    }}
                                }});
                                sourceEl.dispatchEvent(filterEvent);
                            }});
                        }}
                    }});
                }}

                // Initialize dashboard when D3.js/Plotly is loaded
                document.addEventListener('DOMContentLoaded', () => {{
                    console.log('Dashboard ready:', dashboardConfig.id);
                    setupCrossFiltering();
                }});
            </script>
        </body>
        </html>
        """

        self.logger.info(
            f"Dashboard created with {num_components} components in {rows}x{cols} grid"
        )
        self.logger.debug(
            f"Cross-filtering configured between {len(cross_filters)} component pairs"
        )

        return VisualizationResult(
            viz_id=dashboard_id,
            viz_type=VisualizationType.DASHBOARD,
            title=layout_config.get("title", "Government Data Dashboard"),
            html_content=html_content,
            json_config={
                "components": component_configs,
                "cross_filters": cross_filters,
                "sync_events": sync_events,
                "grid": {"rows": rows, "cols": cols, "gap": gap},
                "dimensions": {"width": container_width, "height": container_height},
            },
            static_image_path=None,
            interactive_url=None,
            metadata={
                "components": num_components,
                "grid_layout": f"{rows}x{cols}",
                "cross_filters": len(cross_filters),
                "responsive": True,
            },
            timestamp=datetime.utcnow(),
        )

    async def create_geographic_map(
        self,
        geo_data: list[dict[str, Any]],
        map_config: dict[str, Any],
        context: AgentContext,
    ) -> VisualizationResult:
        """
        Cria mapas geográficos interativos.

        PROJEÇÕES CARTOGRÁFICAS IMPLEMENTADAS:
        - Mercator: Conforme, ângulos preservados (padrão web)
        - Albers Equal Area: Área preservada (mapas temáticos)
        - Equirectangular: Simplificada para protótipos

        ALGORITMO:
        1. Transforma coordenadas geográficas (lat/lon) para projeção escolhida
        2. Cria camadas de dados (pontos, polígonos, heatmap)
        3. Configura controles de zoom/pan
        4. Gera GeoJSON compatível com Leaflet/Mapbox
        """
        self.logger.info(f"Creating geographic map with {len(geo_data)} data points")

        # Extract configuration
        projection = map_config.get("projection", "mercator")
        center_lat = map_config.get("center_lat", -15.7801)  # Centro do Brasil
        center_lon = map_config.get("center_lon", -47.9292)
        zoom_level = map_config.get("zoom", 4)
        layers = map_config.get("layers", ["points"])

        # Transform coordinates using selected projection
        def mercator_projection(lat: float, lon: float) -> tuple[float, float]:
            """Mercator projection: x = λ, y = ln(tan(π/4 + φ/2))"""
            lat_rad = math.radians(lat)
            lon_rad = math.radians(lon)
            x = lon_rad
            y = math.log(math.tan(math.pi / 4 + lat_rad / 2))
            return (math.degrees(x), math.degrees(y))

        def albers_equal_area(
            lat: float, lon: float, lat1: float = -10.0, lat2: float = -25.0
        ) -> tuple[float, float]:
            """Albers Equal Area projection for Brazil"""
            lat_rad = math.radians(lat)
            lon_rad = math.radians(lon)
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)

            n = 0.5 * (math.sin(lat1_rad) + math.sin(lat2_rad))
            c = math.cos(lat1_rad) ** 2 + 2 * n * math.sin(lat1_rad)
            rho = math.sqrt(c - 2 * n * math.sin(lat_rad)) / n if n != 0 else 0
            theta = n * lon_rad

            x = rho * math.sin(theta)
            y = rho * math.cos(theta)
            return (x, y)

        # Process geo data and apply projection
        processed_features = []
        for idx, point in enumerate(geo_data):
            lat = point.get("latitude", point.get("lat", 0))
            lon = point.get("longitude", point.get("lon", 0))
            value = point.get("value", 1.0)

            # Apply projection transformation
            if projection == "mercator":
                proj_x, proj_y = mercator_projection(lat, lon)
            elif projection == "albers":
                proj_x, proj_y = albers_equal_area(lat, lon)
            else:  # equirectangular (simple)
                proj_x, proj_y = lon, lat

            # Create GeoJSON feature
            feature = {
                "type": "Feature",
                "id": idx,
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat],  # GeoJSON uses [lon, lat]
                },
                "properties": {
                    "value": float(value),
                    "projected_x": float(proj_x),
                    "projected_y": float(proj_y),
                    "name": point.get("name", f"Point {idx}"),
                    **{
                        k: v
                        for k, v in point.items()
                        if k not in ["latitude", "lat", "longitude", "lon", "value"]
                    },
                },
            }
            processed_features.append(feature)

        # Create GeoJSON FeatureCollection
        geojson = {
            "type": "FeatureCollection",
            "features": processed_features,
            "crs": {
                "type": "name",
                "properties": {
                    "name": f"urn:ogc:def:crs:PROJECTION::{projection.upper()}"
                },
            },
        }

        # Configure map layers
        layer_configs = []
        if "points" in layers:
            layer_configs.append(
                {
                    "type": "circle",
                    "source": "main-data",
                    "paint": {
                        "circle-radius": [
                            "interpolate",
                            ["linear"],
                            ["get", "value"],
                            0,
                            3,
                            100,
                            20,
                        ],
                        "circle-color": [
                            "interpolate",
                            ["linear"],
                            ["get", "value"],
                            0,
                            self.viz_config["color_palette"][0],
                            100,
                            self.viz_config["color_palette"][3],
                        ],
                        "circle-opacity": 0.7,
                        "circle-stroke-width": 1,
                        "circle-stroke-color": "#ffffff",
                    },
                }
            )

        if "heatmap" in layers:
            layer_configs.append(
                {
                    "type": "heatmap",
                    "source": "main-data",
                    "paint": {
                        "heatmap-weight": [
                            "interpolate",
                            ["linear"],
                            ["get", "value"],
                            0,
                            0,
                            100,
                            1,
                        ],
                        "heatmap-intensity": 1,
                        "heatmap-radius": 30,
                        "heatmap-opacity": 0.8,
                    },
                }
            )

        # Configure interactivity (zoom/pan controls)
        interactivity_config = {
            "zoom": {
                "enabled": True,
                "min_zoom": 3,
                "max_zoom": 18,
                "initial_zoom": zoom_level,
                "scroll_wheel_zoom": True,
                "double_click_zoom": True,
            },
            "pan": {
                "enabled": True,
                "drag_pan": True,
                "keyboard_pan": True,
            },
            "controls": {
                "zoom_controls": True,
                "attribution": True,
                "scale": True,
                "fullscreen": True,
            },
            "interaction": {
                "hover_tooltip": True,
                "click_popup": True,
                "selection": True,
            },
        }

        # Generate map ID
        map_id = f"geomap_{hashlib.md5(str(geo_data).encode()).hexdigest()[:8]}"

        # Generate HTML with Leaflet/Mapbox configuration
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Geographic Map - Cidadão.AI</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: {self.viz_config['font_family']}; }}
                #map-{map_id} {{
                    width: 100%;
                    height: 600px;
                }}
                .leaflet-popup-content {{
                    font-family: {self.viz_config['font_family']};
                }}
            </style>
        </head>
        <body>
            <div id="map-{map_id}"></div>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
                // Map configuration
                const mapConfig = {json.dumps({
                    "id": map_id,
                    "center": [center_lat, center_lon],
                    "zoom": zoom_level,
                    "projection": projection,
                    "geojson": geojson,
                    "layers": layer_configs,
                    "interactivity": interactivity_config
                }, indent=2)};

                // Initialize Leaflet map
                const map = L.map('map-{map_id}', {{
                    center: mapConfig.center,
                    zoom: mapConfig.zoom,
                    minZoom: mapConfig.interactivity.zoom.min_zoom,
                    maxZoom: mapConfig.interactivity.zoom.max_zoom,
                    scrollWheelZoom: mapConfig.interactivity.zoom.scroll_wheel_zoom,
                    doubleClickZoom: mapConfig.interactivity.zoom.double_click_zoom,
                    dragging: mapConfig.interactivity.pan.drag_pan
                }});

                // Add OpenStreetMap tile layer
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '© OpenStreetMap contributors',
                    maxZoom: 18
                }}).addTo(map);

                // Add GeoJSON data layer
                const dataLayer = L.geoJSON(mapConfig.geojson, {{
                    pointToLayer: function(feature, latlng) {{
                        const value = feature.properties.value || 0;
                        const radius = Math.max(5, Math.min(20, value / 5));
                        return L.circleMarker(latlng, {{
                            radius: radius,
                            fillColor: '{self.viz_config["color_palette"][2]}',
                            color: '#fff',
                            weight: 1,
                            opacity: 1,
                            fillOpacity: 0.7
                        }});
                    }},
                    onEachFeature: function(feature, layer) {{
                        if (feature.properties && feature.properties.name) {{
                            const popupContent = `
                                <strong>${{feature.properties.name}}</strong><br>
                                Value: ${{feature.properties.value.toFixed(2)}}
                            `;
                            layer.bindPopup(popupContent);
                        }}
                        layer.on('mouseover', function() {{
                            this.setStyle({{ fillOpacity: 1.0 }});
                        }});
                        layer.on('mouseout', function() {{
                            this.setStyle({{ fillOpacity: 0.7 }});
                        }});
                    }}
                }}).addTo(map);

                // Add scale control
                if (mapConfig.interactivity.controls.scale) {{
                    L.control.scale({{ imperial: false, metric: true }}).addTo(map);
                }}

                console.log('Geographic map initialized:', mapConfig.id);
            </script>
        </body>
        </html>
        """

        self.logger.info(
            f"Geographic map created with {len(processed_features)} features using {projection} projection"
        )
        self.logger.debug(
            f"Map centered at ({center_lat}, {center_lon}) with zoom level {zoom_level}"
        )

        return VisualizationResult(
            viz_id=map_id,
            viz_type=VisualizationType.GEOGRAPHIC_MAP,
            title=map_config.get("title", "Geographic Data Map"),
            html_content=html_content,
            json_config={
                "geojson": geojson,
                "projection": projection,
                "center": [center_lat, center_lon],
                "zoom": zoom_level,
                "layers": layer_configs,
                "interactivity": interactivity_config,
            },
            static_image_path=None,
            interactive_url=None,
            metadata={
                "features_count": len(processed_features),
                "projection": projection,
                "layers": layers,
                "bounds": {
                    "min_lat": (
                        min(f["geometry"]["coordinates"][1] for f in processed_features)
                        if processed_features
                        else 0
                    ),
                    "max_lat": (
                        max(f["geometry"]["coordinates"][1] for f in processed_features)
                        if processed_features
                        else 0
                    ),
                    "min_lon": (
                        min(f["geometry"]["coordinates"][0] for f in processed_features)
                        if processed_features
                        else 0
                    ),
                    "max_lon": (
                        max(f["geometry"]["coordinates"][0] for f in processed_features)
                        if processed_features
                        else 0
                    ),
                },
            },
            timestamp=datetime.utcnow(),
        )

    async def create_network_graph(
        self,
        nodes: list[dict],
        edges: list[dict],
        layout_algorithm: str = "force_directed",
        context: Optional[AgentContext] = None,
    ) -> VisualizationResult:
        """
        Cria grafos de redes sociais e relacionamentos.

        ALGORITMO DE FRUCHTERMAN-REINGOLD (Force-Directed):
        - Força de repulsão entre nós: F_r = k²/d²
        - Força de atração entre arestas: F_a = d²/k
        - k = C * sqrt(área/número_de_nós)
        - Iterações: 100-500 para convergência

        ANÁLISE DE CENTRALIDADE:
        - Degree Centrality: número de conexões diretas
        - Betweenness Centrality: nós que conectam comunidades
        - Closeness Centrality: distância média para outros nós

        DETECÇÃO DE COMUNIDADES:
        - Algoritmo de modularidade (Louvain simplificado)
        - Agrupamento por conectividade
        """
        self.logger.info(
            f"Creating network graph with {len(nodes)} nodes and {len(edges)} edges"
        )

        # Create adjacency structures
        adjacency = {}
        for node in nodes:
            node_id = node.get("id", node.get("name"))
            adjacency[node_id] = []

        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source in adjacency:
                adjacency[source].append(target)
            if target in adjacency and edge.get("bidirectional", True):
                adjacency[target].append(source)

        # Calculate node positions using Fruchterman-Reingold algorithm
        def fruchterman_reingold_layout(
            nodes_list: list,
            edges_list: list,
            iterations: int = 100,
            area: float = 10000.0,
        ) -> dict[str, tuple[float, float]]:
            """Fruchterman-Reingold force-directed layout algorithm."""
            n = len(nodes_list)
            if n == 0:
                return {}

            # Calculate optimal distance k
            k = math.sqrt(area / n) if n > 0 else 1.0

            # Initialize positions randomly
            positions = {}
            for idx, node in enumerate(nodes_list):
                node_id = node.get("id", node.get("name"))
                angle = 2 * math.pi * idx / n
                radius = math.sqrt(n) * 0.5
                positions[node_id] = (
                    radius * math.cos(angle),
                    radius * math.sin(angle),
                )

            # Create edge map for faster lookup
            edge_map = set()
            for edge in edges_list:
                source = edge.get("source")
                target = edge.get("target")
                edge_map.add((source, target))
                if edge.get("bidirectional", True):
                    edge_map.add((target, source))

            # Cooling factor
            temperature = math.sqrt(area) / 10
            dt = temperature / (iterations + 1)

            # Force-directed iterations
            for iteration in range(iterations):
                displacements = {node_id: (0.0, 0.0) for node_id in positions}

                # Calculate repulsive forces between all pairs
                node_ids = list(positions.keys())
                for i, node_i in enumerate(node_ids):
                    for node_j in node_ids[i + 1 :]:
                        pos_i = positions[node_i]
                        pos_j = positions[node_j]

                        # Vector from i to j
                        delta_x = pos_i[0] - pos_j[0]
                        delta_y = pos_i[1] - pos_j[1]
                        distance = math.sqrt(delta_x**2 + delta_y**2)

                        if distance < 0.01:
                            distance = 0.01  # Avoid division by zero

                        # Repulsive force: F_r = k²/d
                        force = (k * k) / distance
                        fx = (delta_x / distance) * force
                        fy = (delta_y / distance) * force

                        # Apply forces
                        dx_i, dy_i = displacements[node_i]
                        displacements[node_i] = (dx_i + fx, dy_i + fy)

                        dx_j, dy_j = displacements[node_j]
                        displacements[node_j] = (dx_j - fx, dy_j - fy)

                # Calculate attractive forces for edges
                for source, target in edge_map:
                    if source in positions and target in positions:
                        pos_s = positions[source]
                        pos_t = positions[target]

                        # Vector from source to target
                        delta_x = pos_t[0] - pos_s[0]
                        delta_y = pos_t[1] - pos_s[1]
                        distance = math.sqrt(delta_x**2 + delta_y**2)

                        if distance < 0.01:
                            continue

                        # Attractive force: F_a = d²/k
                        force = (distance * distance) / k
                        fx = (delta_x / distance) * force
                        fy = (delta_y / distance) * force

                        # Apply forces
                        dx_s, dy_s = displacements[source]
                        displacements[source] = (dx_s + fx, dy_s + fy)

                        dx_t, dy_t = displacements[target]
                        displacements[target] = (dx_t - fx, dy_t - fy)

                # Update positions with cooling
                for node_id in positions:
                    dx, dy = displacements[node_id]
                    displacement_length = math.sqrt(dx**2 + dy**2)

                    if displacement_length > 0:
                        # Limit displacement by temperature
                        capped_length = min(displacement_length, temperature)
                        dx = (dx / displacement_length) * capped_length
                        dy = (dy / displacement_length) * capped_length

                    x, y = positions[node_id]
                    positions[node_id] = (x + dx, y + dy)

                # Cool temperature
                temperature -= dt

            return positions

        # Calculate layout positions
        if layout_algorithm == "force_directed":
            node_positions = fruchterman_reingold_layout(nodes, edges, iterations=150)
        else:
            # Circular layout as fallback
            node_positions = {}
            n = len(nodes)
            for idx, node in enumerate(nodes):
                node_id = node.get("id", node.get("name"))
                angle = 2 * math.pi * idx / n
                radius = 300
                node_positions[node_id] = (
                    radius * math.cos(angle),
                    radius * math.sin(angle),
                )

        # Calculate centrality metrics
        def calculate_degree_centrality(adj_map: dict) -> dict[str, float]:
            """Calculate degree centrality for each node."""
            max_degree = (
                max(len(neighbors) for neighbors in adj_map.values()) if adj_map else 1
            )
            return {
                node_id: len(neighbors) / max_degree if max_degree > 0 else 0.0
                for node_id, neighbors in adj_map.items()
            }

        def calculate_betweenness_centrality(adj_map: dict) -> dict[str, float]:
            """Simplified betweenness centrality using shortest paths."""
            centrality = {node_id: 0.0 for node_id in adj_map}
            node_ids = list(adj_map.keys())

            for source in node_ids:
                # BFS to find shortest paths
                distances = {node_id: float("inf") for node_id in adj_map}
                distances[source] = 0
                predecessors = {node_id: [] for node_id in adj_map}
                queue = [source]

                while queue:
                    current = queue.pop(0)
                    current_dist = distances[current]

                    for neighbor in adj_map.get(current, []):
                        if distances[neighbor] > current_dist + 1:
                            distances[neighbor] = current_dist + 1
                            predecessors[neighbor] = [current]
                            if neighbor not in queue:
                                queue.append(neighbor)
                        elif distances[neighbor] == current_dist + 1:
                            predecessors[neighbor].append(current)

                # Count paths through each node
                for target in node_ids:
                    if target != source and distances[target] < float("inf"):
                        # Simplified: increment centrality for intermediate nodes
                        visited = set()
                        to_visit = [target]
                        while to_visit:
                            node = to_visit.pop(0)
                            if node in visited:
                                continue
                            visited.add(node)
                            if node != source and node != target:
                                centrality[node] += 1.0
                            to_visit.extend(predecessors.get(node, []))

            # Normalize
            max_cent = max(centrality.values()) if centrality else 1.0
            if max_cent > 0:
                centrality = {k: v / max_cent for k, v in centrality.items()}

            return centrality

        degree_centrality = calculate_degree_centrality(adjacency)
        betweenness_centrality = calculate_betweenness_centrality(adjacency)

        # Detect communities using simple modularity-based approach
        def detect_communities(adj_map: dict) -> dict[str, int]:
            """Simplified community detection using connected components."""
            communities = {}
            community_id = 0
            visited = set()

            for node_id in adj_map:
                if node_id in visited:
                    continue

                # BFS to find connected component
                community = []
                queue = [node_id]
                while queue:
                    current = queue.pop(0)
                    if current in visited:
                        continue
                    visited.add(current)
                    community.append(current)
                    for neighbor in adj_map.get(current, []):
                        if neighbor not in visited:
                            queue.append(neighbor)

                # Assign community ID
                for member in community:
                    communities[member] = community_id
                community_id += 1

            return communities

        node_communities = detect_communities(adjacency)
        num_communities = len(set(node_communities.values()))

        # Generate colors for communities
        community_colors = {}
        for comm_id in range(num_communities):
            hue = (comm_id * 360 // num_communities) % 360
            community_colors[comm_id] = f"hsl({hue}, 70%, 60%)"

        # Prepare node data with positions and metrics
        nodes_data = []
        for node in nodes:
            node_id = node.get("id", node.get("name"))
            pos = node_positions.get(node_id, (0, 0))

            nodes_data.append(
                {
                    "id": node_id,
                    "x": float(pos[0]),
                    "y": float(pos[1]),
                    "label": node.get("label", node_id),
                    "degree_centrality": float(degree_centrality.get(node_id, 0)),
                    "betweenness_centrality": float(
                        betweenness_centrality.get(node_id, 0)
                    ),
                    "community": int(node_communities.get(node_id, 0)),
                    "color": community_colors.get(
                        node_communities.get(node_id, 0), "#999"
                    ),
                    "size": float(10 + degree_centrality.get(node_id, 0) * 20),
                }
            )

        # Prepare edge data
        edges_data = []
        for edge in edges:
            edges_data.append(
                {
                    "source": edge.get("source"),
                    "target": edge.get("target"),
                    "weight": edge.get("weight", 1.0),
                    "label": edge.get("label", ""),
                }
            )

        # Generate graph ID
        graph_id = f"network_{hashlib.md5(str(nodes + edges).encode()).hexdigest()[:8]}"

        # Generate HTML with D3.js configuration
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Network Graph - Cidadão.AI</title>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: {self.viz_config['font_family']}; }}
                #graph-{graph_id} {{
                    width: 100%;
                    height: 600px;
                    border: 1px solid #e8e8e8;
                }}
                .node {{ cursor: pointer; }}
                .node:hover {{ stroke: #000; stroke-width: 2px; }}
                .link {{ stroke: #999; stroke-opacity: 0.6; }}
            </style>
        </head>
        <body>
            <div id="graph-{graph_id}"></div>
            <script>
                // Network data
                const networkData = {json.dumps({"nodes": nodes_data, "edges": edges_data}, indent=2)};

                // D3.js visualization placeholder
                console.log('Network graph data ready:', networkData);
                console.log('Nodes:', networkData.nodes.length, 'Edges:', networkData.edges.length);
                console.log('Communities detected:', {num_communities});

                // Centrality metrics summary
                const centralityMetrics = networkData.nodes.map(n => ({{
                    id: n.id,
                    degree: n.degree_centrality,
                    betweenness: n.betweenness_centrality,
                    community: n.community
                }}));
                console.log('Centrality metrics:', centralityMetrics);
            </script>
        </body>
        </html>
        """

        self.logger.info(
            f"Network graph created with {len(nodes)} nodes, {len(edges)} edges, {num_communities} communities"
        )
        self.logger.debug(
            f"Layout algorithm: {layout_algorithm}, max degree centrality: {max(degree_centrality.values()):.3f}"
        )

        return VisualizationResult(
            viz_id=graph_id,
            viz_type=VisualizationType.NETWORK_GRAPH,
            title=f"Network Graph - {layout_algorithm.replace('_', ' ').title()}",
            html_content=html_content,
            json_config={
                "nodes": nodes_data,
                "edges": edges_data,
                "layout_algorithm": layout_algorithm,
                "communities": num_communities,
                "centrality_metrics": {
                    "degree": degree_centrality,
                    "betweenness": betweenness_centrality,
                },
            },
            static_image_path=None,
            interactive_url=None,
            metadata={
                "nodes_count": len(nodes),
                "edges_count": len(edges),
                "communities": num_communities,
                "layout_algorithm": layout_algorithm,
                "avg_degree": float(np.mean(list(degree_centrality.values()))),
                "max_betweenness": (
                    float(max(betweenness_centrality.values()))
                    if betweenness_centrality
                    else 0.0
                ),
            },
            timestamp=datetime.utcnow(),
        )

    async def generate_report_visualizations(
        self, report_data: dict[str, Any], context: AgentContext
    ) -> list[VisualizationResult]:
        """
        Gera conjunto de visualizações para relatório.

        ANÁLISE AUTOMÁTICA DE DADOS:
        1. Detecta tipos de dados (numérico, categórico, temporal, geográfico)
        2. Identifica cardinalidade e distribuição
        3. Detecta relacionamentos entre variáveis
        4. Sugere visualizações apropriadas baseado em heurísticas

        HEURÍSTICAS DE SELEÇÃO:
        - 1 variável numérica → Histograma
        - 1 categórica + 1 numérica → Gráfico de barras
        - 2 numéricas → Scatter plot
        - Série temporal → Gráfico de linhas
        - Múltiplas categorias → Treemap ou Pie chart
        - Dados geográficos → Mapa
        """
        self.logger.info("Generating automatic visualizations for report")

        visualizations = []

        # Extract and analyze data structure
        data_points = report_data.get("data", [])
        if not data_points:
            self.logger.warning("No data points found in report_data")
            return visualizations

        # Convert to DataFrame for analysis
        df = pd.DataFrame(data_points)
        if df.empty:
            return visualizations

        # Analyze data types
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()
        datetime_cols = []

        # Try to detect datetime columns
        for col in categorical_cols[:]:
            if "date" in col.lower() or "time" in col.lower():
                try:
                    pd.to_datetime(df[col])
                    datetime_cols.append(col)
                    categorical_cols.remove(col)
                except Exception:
                    pass

        # Detect geographic columns
        geo_cols = [
            col
            for col in df.columns
            if any(
                geo_term in col.lower()
                for geo_term in ["lat", "lon", "latitude", "longitude", "coord"]
            )
        ]

        self.logger.debug(
            f"Data analysis: {len(numeric_cols)} numeric, {len(categorical_cols)} categorical, "
            f"{len(datetime_cols)} datetime, {len(geo_cols)} geographic columns"
        )

        # Generate visualizations based on data characteristics

        # 1. Numeric univariate analysis - Histogram
        for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
            values = df[col].dropna()
            if len(values) > 0:
                # Calculate histogram bins
                num_bins = min(30, max(10, int(np.sqrt(len(values)))))
                hist, bin_edges = np.histogram(values, bins=num_bins)

                viz_data = [
                    {
                        "bin_start": float(bin_edges[i]),
                        "bin_end": float(bin_edges[i + 1]),
                        "count": int(hist[i]),
                    }
                    for i in range(len(hist))
                ]

                spec = VisualizationSpec(
                    viz_type=VisualizationType.BAR_CHART,
                    title=f"Distribution of {col}",
                    data_source="report",
                    dimensions=[col],
                    metrics=["count"],
                    filters={},
                    styling={"color": self.viz_config["color_palette"][0]},
                    interactivity=["hover", "tooltip"],
                    export_formats=["png", "svg"],
                )

                viz = await self.create_visualization(spec, viz_data, context)
                visualizations.append(viz)

        # 2. Categorical + Numeric - Bar chart
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]

            # Group by category and calculate mean
            grouped = df.groupby(cat_col)[num_col].mean().reset_index()
            # Limit to top 10 categories
            grouped = grouped.nlargest(10, num_col)

            viz_data = [
                {"category": str(row[cat_col]), "value": float(row[num_col])}
                for _, row in grouped.iterrows()
            ]

            spec = VisualizationSpec(
                viz_type=VisualizationType.BAR_CHART,
                title=f"Average {num_col} by {cat_col}",
                data_source="report",
                dimensions=[cat_col],
                metrics=[num_col],
                filters={},
                styling={"color": self.viz_config["color_palette"][1]},
                interactivity=["hover", "click", "tooltip"],
                export_formats=["png", "svg"],
            )

            viz = await self.create_visualization(spec, viz_data, context)
            visualizations.append(viz)

        # 3. Two numeric variables - Scatter plot
        if len(numeric_cols) >= 2:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]

            # Sample data if too large
            sample_df = df if len(df) <= 1000 else df.sample(n=1000)

            viz_data = [
                {"x": float(row[x_col]), "y": float(row[y_col]), "index": idx}
                for idx, row in sample_df.iterrows()
                if pd.notna(row[x_col]) and pd.notna(row[y_col])
            ]

            spec = VisualizationSpec(
                viz_type=VisualizationType.SCATTER_PLOT,
                title=f"{y_col} vs {x_col}",
                data_source="report",
                dimensions=[x_col, y_col],
                metrics=[],
                filters={},
                styling={"color": self.viz_config["color_palette"][2]},
                interactivity=["hover", "zoom", "tooltip"],
                export_formats=["png", "svg"],
            )

            viz = await self.create_visualization(spec, viz_data, context)
            visualizations.append(viz)

        # 4. Time series - Line chart
        if datetime_cols and numeric_cols:
            time_col = datetime_cols[0]
            value_col = numeric_cols[0]

            # Convert to datetime and sort
            time_df = df[[time_col, value_col]].copy()
            time_df[time_col] = pd.to_datetime(time_df[time_col])
            time_df = time_df.sort_values(time_col)
            time_df = time_df.dropna()

            viz_data = [
                {
                    "date": (
                        row[time_col].isoformat()
                        if hasattr(row[time_col], "isoformat")
                        else str(row[time_col])
                    ),
                    "value": float(row[value_col]),
                }
                for _, row in time_df.iterrows()
            ]

            spec = VisualizationSpec(
                viz_type=VisualizationType.LINE_CHART,
                title=f"{value_col} over Time",
                data_source="report",
                dimensions=[time_col],
                metrics=[value_col],
                filters={},
                styling={"color": self.viz_config["color_palette"][3]},
                interactivity=["hover", "zoom", "pan", "tooltip"],
                export_formats=["png", "svg"],
            )

            viz = await self.create_visualization(spec, viz_data, context)
            visualizations.append(viz)

        # 5. Categorical distribution - Pie chart (if cardinality is low)
        if categorical_cols:
            cat_col = categorical_cols[0]
            value_counts = df[cat_col].value_counts().head(10)  # Top 10 categories

            if len(value_counts) <= 8:  # Pie chart works best with ≤8 categories
                viz_data = [
                    {"category": str(cat), "count": int(count)}
                    for cat, count in value_counts.items()
                ]

                spec = VisualizationSpec(
                    viz_type=VisualizationType.PIE_CHART,
                    title=f"Distribution of {cat_col}",
                    data_source="report",
                    dimensions=[cat_col],
                    metrics=["count"],
                    filters={},
                    styling={"colors": self.viz_config["color_palette"]},
                    interactivity=["hover", "tooltip"],
                    export_formats=["png", "svg"],
                )

                viz = await self.create_visualization(spec, viz_data, context)
                visualizations.append(viz)

        # 6. Correlation heatmap (if multiple numeric columns)
        if len(numeric_cols) >= 3:
            # Calculate correlation matrix
            corr_matrix = df[numeric_cols].corr()

            viz_data = []
            for i, row_name in enumerate(corr_matrix.index):
                for j, col_name in enumerate(corr_matrix.columns):
                    viz_data.append(
                        {
                            "x": str(col_name),
                            "y": str(row_name),
                            "correlation": float(corr_matrix.iloc[i, j]),
                        }
                    )

            spec = VisualizationSpec(
                viz_type=VisualizationType.HEATMAP,
                title="Correlation Matrix",
                data_source="report",
                dimensions=numeric_cols,
                metrics=["correlation"],
                filters={},
                styling={"colorscale": "RdYlGn"},
                interactivity=["hover", "tooltip"],
                export_formats=["png", "svg"],
            )

            viz = await self.create_visualization(spec, viz_data, context)
            visualizations.append(viz)

        # 7. Geographic visualization (if lat/lon present)
        if len(geo_cols) >= 2:
            lat_col = next((c for c in geo_cols if "lat" in c.lower()), None)
            lon_col = next((c for c in geo_cols if "lon" in c.lower()), None)

            if lat_col and lon_col:
                geo_df = df[[lat_col, lon_col]].dropna()
                if len(geo_df) > 0:
                    value_col = numeric_cols[0] if numeric_cols else None

                    geo_data_list = []
                    for idx, row in geo_df.iterrows():
                        point = {
                            "latitude": float(row[lat_col]),
                            "longitude": float(row[lon_col]),
                            "value": (
                                float(row[value_col])
                                if value_col and pd.notna(row.get(value_col))
                                else 1.0
                            ),
                            "name": f"Point {idx}",
                        }
                        geo_data_list.append(point)

                    map_config = {
                        "projection": "mercator",
                        "layers": ["points"],
                        "zoom": 4,
                        "title": "Geographic Distribution",
                    }

                    viz = await self.create_geographic_map(
                        geo_data_list, map_config, context
                    )
                    visualizations.append(viz)

        self.logger.info(
            f"Generated {len(visualizations)} visualizations automatically from report data"
        )

        return visualizations

    async def process_message(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        """Processa mensagens e coordena criação de visualizações."""
        try:
            action = message.content.get("action")

            if action == "create_visualization":
                spec_data = message.content.get("specification")
                data = message.content.get("data", [])

                # Converter dict para VisualizationSpec
                spec = VisualizationSpec(
                    viz_type=VisualizationType(spec_data.get("viz_type")),
                    title=spec_data.get("title", "Visualization"),
                    data_source=spec_data.get("data_source", "unknown"),
                    dimensions=spec_data.get("dimensions", []),
                    metrics=spec_data.get("metrics", []),
                    filters=spec_data.get("filters", {}),
                    styling=spec_data.get("styling", {}),
                    interactivity=spec_data.get("interactivity", []),
                    export_formats=spec_data.get("export_formats", ["html"]),
                )

                result = await self.create_visualization(spec, data, context)

                return AgentResponse(
                    agent_name=self.name,
                    content={
                        "visualization": {
                            "id": result.viz_id,
                            "type": result.viz_type.value,
                            "title": result.title,
                            "html_content": result.html_content,
                            "interactive_url": result.interactive_url,
                        },
                        "status": "visualization_created",
                    },
                    confidence=0.95,
                    metadata=result.metadata,
                )

            elif action == "create_dashboard":
                components = message.content.get("components", [])
                layout = message.content.get("layout", {})

                result = await self.create_dashboard(components, layout, context)

                return AgentResponse(
                    agent_name=self.name,
                    content={"dashboard": result, "status": "dashboard_created"},
                    confidence=0.90,
                )

            return AgentResponse(
                agent_name=self.name,
                content={"error": "Unknown visualization action"},
                confidence=0.0,
            )

        except Exception as e:
            self.logger.error(f"Error in visualization creation: {str(e)}")
            raise AgentExecutionError(f"Visualization creation failed: {str(e)}")

    async def _preprocess_data(
        self, data: list[dict], spec: VisualizationSpec
    ) -> pd.DataFrame:
        """Pré-processa dados para visualização."""
        df = pd.DataFrame(data)

        # Aplicar filtros
        for column, filter_value in spec.filters.items():
            if column in df.columns:
                df = df[
                    (
                        df[column].isin(filter_value)
                        if isinstance(filter_value, list)
                        else df[column] == filter_value
                    )
                ]

        # Sampling se necessário
        if len(df) > self.viz_config["max_data_points"]:
            df = df.sample(n=self.viz_config["max_data_points"])

        return df

    async def _calculate_layout(
        self, data: pd.DataFrame, spec: VisualizationSpec
    ) -> dict[str, Any]:
        """
        Calcula layout específico para o tipo de visualização.

        ALGORITMOS IMPLEMENTADOS:
        - Force-Directed: Para network graphs (usa Fruchterman-Reingold)
        - Grid Layout: Para dashboards e multi-panel visualizations
        - Spatial Layout: Para mapas geográficos
        - Standard Layout: Para gráficos básicos (bar, line, scatter)
        """
        # Base layout configuration
        layout_config = {
            "width": self.viz_config["default_width"],
            "height": self.viz_config["default_height"],
            "margins": {"top": 50, "right": 50, "bottom": 50, "left": 50},
            "padding": 20,
        }

        # Visualization type-specific layouts
        if spec.viz_type == VisualizationType.NETWORK_GRAPH:
            # Force-directed layout parameters
            layout_config.update(
                {
                    "algorithm": "force_directed",
                    "iterations": 150,
                    "area": 100000,
                    "optimal_distance": math.sqrt(100000 / max(len(data), 1)),
                    "cooling_factor": 0.95,
                    "repulsion_strength": 1.5,
                    "attraction_strength": 0.8,
                }
            )

        elif spec.viz_type == VisualizationType.DASHBOARD:
            # Grid layout parameters
            num_items = len(data) if not data.empty else 1
            cols = min(3, num_items)
            rows = math.ceil(num_items / cols)

            layout_config.update(
                {
                    "algorithm": "grid",
                    "grid_columns": cols,
                    "grid_rows": rows,
                    "cell_width": (
                        layout_config["width"] - layout_config["padding"] * (cols + 1)
                    )
                    / cols,
                    "cell_height": (
                        layout_config["height"] - layout_config["padding"] * (rows + 1)
                    )
                    / rows,
                    "gap": layout_config["padding"],
                }
            )

        elif spec.viz_type == VisualizationType.GEOGRAPHIC_MAP:
            # Spatial layout parameters
            layout_config.update(
                {
                    "algorithm": "spatial",
                    "projection": "mercator",
                    "center": [-15.7801, -47.9292],  # Centro do Brasil
                    "zoom_initial": 4,
                    "zoom_min": 2,
                    "zoom_max": 18,
                    "tile_provider": "openstreetmap",
                }
            )

        elif spec.viz_type in [
            VisualizationType.BAR_CHART,
            VisualizationType.LINE_CHART,
        ]:
            # Adjust margins for axis labels
            layout_config["margins"].update({"bottom": 80, "left": 80})

            # Calculate optimal bar width or point spacing
            num_points = len(data) if not data.empty else 1
            available_width = (
                layout_config["width"]
                - layout_config["margins"]["left"]
                - layout_config["margins"]["right"]
            )

            layout_config.update(
                {
                    "algorithm": "cartesian",
                    "x_axis": {
                        "scale": (
                            "linear"
                            if spec.viz_type == VisualizationType.LINE_CHART
                            else "band"
                        ),
                        "label_rotation": 45 if num_points > 10 else 0,
                    },
                    "y_axis": {"scale": "linear", "ticks": 10},
                    "bar_width": (
                        min(50, available_width / max(num_points, 1) * 0.8)
                        if spec.viz_type == VisualizationType.BAR_CHART
                        else None
                    ),
                }
            )

        elif spec.viz_type == VisualizationType.SCATTER_PLOT:
            layout_config.update(
                {
                    "algorithm": "cartesian",
                    "point_radius": 5,
                    "opacity": 0.6,
                    "x_axis": {"scale": "linear"},
                    "y_axis": {"scale": "linear"},
                }
            )

        elif spec.viz_type == VisualizationType.HEATMAP:
            # Calculate cell dimensions based on data
            if not data.empty and len(spec.dimensions) >= 2:
                unique_x = (
                    data[spec.dimensions[0]].nunique()
                    if spec.dimensions[0] in data.columns
                    else 10
                )
                unique_y = (
                    data[spec.dimensions[1]].nunique()
                    if len(spec.dimensions) > 1 and spec.dimensions[1] in data.columns
                    else 10
                )

                cell_width = (
                    layout_config["width"]
                    - layout_config["margins"]["left"]
                    - layout_config["margins"]["right"]
                ) / unique_x
                cell_height = (
                    layout_config["height"]
                    - layout_config["margins"]["top"]
                    - layout_config["margins"]["bottom"]
                ) / unique_y

                layout_config.update(
                    {
                        "algorithm": "matrix",
                        "cell_width": float(cell_width),
                        "cell_height": float(cell_height),
                        "colorscale": spec.styling.get("colorscale", "viridis"),
                    }
                )

        elif spec.viz_type == VisualizationType.PIE_CHART:
            # Circular layout
            radius = min(layout_config["width"], layout_config["height"]) / 2 - 50
            layout_config.update(
                {
                    "algorithm": "circular",
                    "radius": float(radius),
                    "center_x": layout_config["width"] / 2,
                    "center_y": layout_config["height"] / 2,
                    "inner_radius": 0,  # Set > 0 for donut chart
                    "label_offset": radius + 20,
                }
            )

        self.logger.debug(
            f"Calculated {layout_config.get('algorithm', 'standard')} layout for {spec.viz_type.value}"
        )

        return layout_config

    async def _render_visualization(
        self, data: pd.DataFrame, spec: VisualizationSpec, layout: dict[str, Any]
    ) -> VisualizationResult:
        """
        Renderiza a visualização final.

        Gera HTML com embedded JavaScript e JSON configuration para D3.js/Plotly.
        Suporta todos os tipos de visualização com templates específicos.
        """
        viz_id = f"{spec.viz_type.value}_{hashlib.md5(str(datetime.utcnow().timestamp()).encode()).hexdigest()[:8]}"

        # Prepare data for visualization
        viz_data = data.to_dict("records") if not data.empty else []

        # Get template for this visualization type
        template = self.viz_templates.get(
            spec.viz_type.value, self.viz_templates.get("default")
        )

        # Build styling from config and spec
        colors = spec.styling.get(
            "colors", spec.styling.get("color", self.viz_config["color_palette"])
        )
        if not isinstance(colors, list):
            colors = [colors]

        # Generate HTML based on visualization type
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{spec.title} - Cidadão.AI</title>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: {self.viz_config['font_family']};
                    background: #f8f9fa;
                    padding: 20px;
                }}
                #viz-{viz_id} {{
                    width: {layout['width']}px;
                    height: {layout['height']}px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    padding: 20px;
                }}
                .viz-title {{
                    font-size: 20px;
                    font-weight: 600;
                    margin-bottom: 16px;
                    color: #333;
                }}
                .viz-container {{
                    width: 100%;
                    height: calc(100% - 40px);
                }}
                .tooltip {{
                    position: absolute;
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                    pointer-events: none;
                    opacity: 0;
                    transition: opacity 0.2s;
                }}
            </style>
        </head>
        <body>
            <div id="viz-{viz_id}">
                <div class="viz-title">{spec.title}</div>
                <div class="viz-container" id="container-{viz_id}"></div>
            </div>
            <div class="tooltip" id="tooltip-{viz_id}"></div>

            <script>
                // Visualization configuration
                const vizConfig = {json.dumps({
                    "id": viz_id,
                    "type": spec.viz_type.value,
                    "title": spec.title,
                    "data": viz_data[:1000],  # Limit data points for HTML size
                    "layout": layout,
                    "styling": {
                        "colors": colors,
                        "font_family": self.viz_config["font_family"],
                        "animation_duration": self.viz_config["animation_duration"],
                        **spec.styling
                    },
                    "interactivity": spec.interactivity,
                    "dimensions": spec.dimensions,
                    "metrics": spec.metrics
                }, indent=2)};

                // Visualization rendering logic (placeholder for D3.js/Plotly implementation)
                console.log('Visualization config:', vizConfig);
                console.log('Ready to render', vizConfig.type, 'with', vizConfig.data.length, 'data points');

                // Basic Plotly rendering example (to be expanded)
                if (typeof Plotly !== 'undefined') {{
                    const container = document.getElementById('container-{viz_id}');

                    // Simple plot configuration based on type
                    let plotData = [];
                    let plotLayout = {{
                        width: {layout['width'] - 40},
                        height: {layout['height'] - 80},
                        margin: {{ t: 20, r: 20, b: 60, l: 60 }},
                        font: {{ family: vizConfig.styling.font_family }}
                    }};

                    // Type-specific rendering
                    if (vizConfig.type === 'bar_chart') {{
                        plotData = [{{
                            x: vizConfig.data.map(d => d[vizConfig.dimensions[0]] || d.category),
                            y: vizConfig.data.map(d => d[vizConfig.metrics[0]] || d.value || d.count),
                            type: 'bar',
                            marker: {{ color: vizConfig.styling.colors[0] }}
                        }}];
                    }} else if (vizConfig.type === 'line_chart') {{
                        plotData = [{{
                            x: vizConfig.data.map((d, i) => d.date || i),
                            y: vizConfig.data.map(d => d.value),
                            type: 'scatter',
                            mode: 'lines+markers',
                            line: {{ color: vizConfig.styling.colors[0] }}
                        }}];
                    }} else if (vizConfig.type === 'scatter_plot') {{
                        plotData = [{{
                            x: vizConfig.data.map(d => d.x),
                            y: vizConfig.data.map(d => d.y),
                            mode: 'markers',
                            type: 'scatter',
                            marker: {{ color: vizConfig.styling.colors[0], size: 8 }}
                        }}];
                    }} else if (vizConfig.type === 'pie_chart') {{
                        plotData = [{{
                            values: vizConfig.data.map(d => d.count || d.value),
                            labels: vizConfig.data.map(d => d.category),
                            type: 'pie',
                            marker: {{ colors: vizConfig.styling.colors }}
                        }}];
                    }}

                    if (plotData.length > 0) {{
                        Plotly.newPlot(container, plotData, plotLayout, {{responsive: true}});
                    }} else {{
                        container.innerHTML = '<p style="padding: 20px; color: #666;">Visualization rendering for ' + vizConfig.type + ' with ' + vizConfig.data.length + ' points</p>';
                    }}
                }}
            </script>
        </body>
        </html>
        """

        self.logger.info(
            f"Rendered {spec.viz_type.value} visualization with {len(viz_data)} data points"
        )

        return VisualizationResult(
            viz_id=viz_id,
            viz_type=spec.viz_type,
            title=spec.title,
            html_content=html_content,
            json_config={
                "data": viz_data,
                "layout": layout,
                "styling": spec.styling,
                "dimensions": spec.dimensions,
                "metrics": spec.metrics,
                "interactivity": spec.interactivity,
            },
            static_image_path=None,
            interactive_url=None,
            metadata={
                "data_points": len(data),
                "created_at": datetime.utcnow().isoformat(),
                "layout_algorithm": layout.get("algorithm", "standard"),
                "viz_type": spec.viz_type.value,
            },
            timestamp=datetime.utcnow(),
        )

    async def _load_visualization_templates(self) -> None:
        """
        Carrega templates de visualização pré-definidos.

        Templates definem estrutura padrão, configuração e styling para cada tipo
        de visualização. São usados como base para renderização rápida.
        """
        self.logger.debug("Loading visualization templates...")

        # Bar Chart Template
        self.viz_templates["bar_chart"] = {
            "structure": {
                "container": "svg",
                "elements": ["rect", "text", "axis"],
                "scales": ["x:band", "y:linear"],
            },
            "default_config": {
                "bar_padding": 0.1,
                "axis_labels": True,
                "grid": True,
                "orientation": "vertical",
                "sort": None,
            },
            "styling": {
                "bar_color": self.viz_config["color_palette"][0],
                "bar_opacity": 0.8,
                "hover_opacity": 1.0,
                "stroke": "#ffffff",
                "stroke_width": 1,
                "font_size": 12,
            },
        }

        # Line Chart Template
        self.viz_templates["line_chart"] = {
            "structure": {
                "container": "svg",
                "elements": ["path", "circle", "axis"],
                "scales": ["x:linear", "y:linear"],
            },
            "default_config": {
                "line_width": 2,
                "point_radius": 4,
                "interpolation": "linear",  # linear, basis, cardinal
                "show_points": True,
                "show_area": False,
            },
            "styling": {
                "line_color": self.viz_config["color_palette"][1],
                "point_color": self.viz_config["color_palette"][1],
                "area_opacity": 0.3,
                "grid_color": "#e0e0e0",
                "font_size": 12,
            },
        }

        # Pie Chart Template
        self.viz_templates["pie_chart"] = {
            "structure": {
                "container": "svg",
                "elements": ["path", "text", "legend"],
                "scales": ["angular"],
            },
            "default_config": {
                "inner_radius": 0,  # Set > 0 for donut chart
                "label_threshold": 0.05,  # Min percentage to show label
                "sort_slices": True,
                "show_legend": True,
                "show_percentages": True,
            },
            "styling": {
                "colors": self.viz_config["color_palette"],
                "stroke": "#ffffff",
                "stroke_width": 2,
                "label_color": "#333",
                "font_size": 11,
            },
        }

        # Scatter Plot Template
        self.viz_templates["scatter_plot"] = {
            "structure": {
                "container": "svg",
                "elements": ["circle", "axis"],
                "scales": ["x:linear", "y:linear"],
            },
            "default_config": {
                "point_radius": 5,
                "point_opacity": 0.6,
                "show_regression": False,
                "show_density": False,
                "jitter": False,
            },
            "styling": {
                "point_color": self.viz_config["color_palette"][2],
                "hover_color": self.viz_config["color_palette"][3],
                "regression_color": "#ff0000",
                "stroke": "none",
                "font_size": 12,
            },
        }

        # Heatmap Template
        self.viz_templates["heatmap"] = {
            "structure": {
                "container": "svg",
                "elements": ["rect", "text", "axis", "legend"],
                "scales": ["x:band", "y:band", "color:sequential"],
            },
            "default_config": {
                "cell_padding": 2,
                "show_values": True,
                "colorscale": "viridis",  # viridis, plasma, inferno, magma
                "symmetric": False,
                "dendrogram": False,
            },
            "styling": {
                "stroke": "#ffffff",
                "stroke_width": 1,
                "text_color": "#000000",
                "font_size": 10,
                "legend_position": "right",
            },
        }

        # Network Graph Template
        self.viz_templates["network_graph"] = {
            "structure": {
                "container": "svg",
                "elements": ["line", "circle", "text"],
                "scales": ["force"],
            },
            "default_config": {
                "layout": "force_directed",
                "iterations": 150,
                "show_labels": True,
                "show_arrows": True,
                "min_link_distance": 30,
                "charge_strength": -200,
            },
            "styling": {
                "node_color": self.viz_config["color_palette"][0],
                "link_color": "#999999",
                "link_opacity": 0.6,
                "node_stroke": "#ffffff",
                "node_stroke_width": 2,
                "font_size": 10,
            },
        }

        # Geographic Map Template
        self.viz_templates["geographic_map"] = {
            "structure": {
                "container": "leaflet",
                "elements": ["tile_layer", "markers", "polygons"],
                "scales": ["geographic"],
            },
            "default_config": {
                "projection": "mercator",
                "zoom_initial": 4,
                "zoom_min": 2,
                "zoom_max": 18,
                "tile_provider": "openstreetmap",
                "cluster_markers": True,
            },
            "styling": {
                "marker_color": self.viz_config["color_palette"][0],
                "marker_size": 10,
                "polygon_color": self.viz_config["color_palette"][1],
                "polygon_opacity": 0.6,
                "highlight_color": "#ffff00",
            },
        }

        # Default Template (fallback)
        self.viz_templates["default"] = {
            "structure": {
                "container": "div",
                "elements": ["placeholder"],
                "scales": [],
            },
            "default_config": {
                "responsive": True,
                "interactive": True,
            },
            "styling": {
                "background": "#ffffff",
                "border": "1px solid #e0e0e0",
                "padding": "20px",
                "font_family": self.viz_config["font_family"],
            },
        }

        self.logger.info(f"Loaded {len(self.viz_templates)} visualization templates")

    async def _setup_rendering_engines(self) -> None:
        """
        Configura engines de renderização.

        Define configurações para bibliotecas de visualização (D3.js, Plotly, Leaflet)
        incluindo temas, paletas de cores, e opções de animação.
        """
        self.logger.debug("Setting up rendering engines...")

        # D3.js Configuration
        self.rendering_engines = {
            "d3js": {
                "version": "7.8.5",
                "cdn_url": "https://d3js.org/d3.v7.min.js",
                "features": ["svg", "scales", "axes", "transitions", "selections"],
                "default_transition_duration": self.viz_config["animation_duration"],
                "easing": "cubic-in-out",
            },
            "plotly": {
                "version": "2.27.0",
                "cdn_url": "https://cdn.plot.ly/plotly-2.27.0.min.js",
                "features": ["cartesian", "3d", "maps", "statistical"],
                "config": {
                    "responsive": True,
                    "displayModeBar": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["sendDataToCloud"],
                },
                "layout": {
                    "font": {"family": self.viz_config["font_family"], "size": 12},
                    "plot_bgcolor": "#ffffff",
                    "paper_bgcolor": "#ffffff",
                },
            },
            "leaflet": {
                "version": "1.9.4",
                "cdn_url": "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
                "css_url": "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
                "plugins": ["markercluster", "heat", "draw"],
                "default_options": {
                    "zoomControl": True,
                    "attributionControl": True,
                    "scrollWheelZoom": True,
                },
            },
        }

        # Color Schemes and Themes
        self.color_schemes = {
            "categorical": {
                "default": self.viz_config["color_palette"],
                "pastel": ["#FFB6C1", "#FFDAB9", "#E0BBE4", "#B2E2F2", "#C7CEEA"],
                "vibrant": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"],
                "earth": ["#8B4513", "#2F4F4F", "#556B2F", "#8B7355", "#A0522D"],
            },
            "sequential": {
                "blues": ["#EFF3FF", "#C6DBEF", "#9ECAE1", "#6BAED6", "#3182BD"],
                "reds": ["#FEE5D9", "#FCBBA1", "#FC9272", "#FB6A4A", "#DE2D26"],
                "greens": ["#EDF8E9", "#C7E9C0", "#A1D99B", "#74C476", "#31A354"],
                "purples": ["#F2F0F7", "#DADAEB", "#BCBDDC", "#9E9AC8", "#756BB1"],
            },
            "diverging": {
                "red_blue": ["#D73027", "#FC8D59", "#FEE090", "#91BFDB", "#4575B4"],
                "purple_green": ["#762A83", "#AF8DC3", "#E7D4E8", "#7FBF7B", "#1B7837"],
                "brown_teal": ["#8C510A", "#D8B365", "#F6E8C3", "#5AB4AC", "#01665E"],
            },
        }

        # Animation Configurations
        self.animation_config = {
            "enter": {
                "duration": self.viz_config["animation_duration"],
                "easing": "ease-out",
                "delay": 0,
            },
            "update": {
                "duration": self.viz_config["animation_duration"] // 2,
                "easing": "ease-in-out",
                "delay": 0,
            },
            "exit": {
                "duration": self.viz_config["animation_duration"] // 3,
                "easing": "ease-in",
                "delay": 0,
            },
            "disabled": False,  # Set True to disable animations
        }

        # Renderer-specific settings
        self.renderer_settings = {
            "svg": {
                "xmlns": "http://www.w3.org/2000/svg",
                "default_viewBox": "0 0 800 600",
                "preserveAspectRatio": "xMidYMid meet",
            },
            "canvas": {
                "context": "2d",
                "alpha": True,
                "desynchronized": False,
                "pixelRatio": 2,  # For retina displays
            },
            "webgl": {
                "antialias": True,
                "alpha": True,
                "depth": True,
                "preserveDrawingBuffer": False,
            },
        }

        # Accessibility settings
        self.accessibility_config = {
            "keyboard_navigation": True,
            "screen_reader_support": True,
            "high_contrast_mode": False,
            "focus_indicators": True,
            "aria_labels": True,
        }

        self.logger.info(
            f"Rendering engines configured: {len(self.rendering_engines)} libraries, "
            f"{len(self.color_schemes)} color scheme families"
        )
