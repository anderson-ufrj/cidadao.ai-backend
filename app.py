#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Portal da Transparência
Sistema de consulta aos dados do Portal da Transparência
"""

import gradio as gr
import os
import time
import asyncio
import httpx
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configurar variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def create_visualizations(results, data_type):
    """Criar visualizações interativas avançadas com Plotly"""
    if not results or len(results) == 0:
        return None, None, None, None
    
    # Preparar dados
    df_data = []
    for item in results[:50]:  # Aumentar para 50 itens
        valor = item.get('valor', item.get('valorContrato', item.get('valorInicial', 0)))
        empresa = item.get('nome', item.get('razaoSocial', item.get('fornecedor', 'N/A')))
        numero = item.get('numero', item.get('id', f'REG-{len(df_data)+1:03d}'))
        orgao = item.get('orgao', item.get('nomeOrgao', 'N/A'))
        
        df_data.append({
            'numero': numero,
            'empresa': empresa[:30] + '...' if len(str(empresa)) > 30 else empresa,
            'orgao': orgao[:20] + '...' if len(str(orgao)) > 20 else orgao,
            'valor': float(valor) if isinstance(valor, (int, float)) else 0,
            'valor_formatado': f"R$ {float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if isinstance(valor, (int, float)) else 'N/A'
        })
    
    df = pd.DataFrame(df_data)
    
    if df.empty:
        return None, None, None, None
    
    # Gráfico 1: Top 10 por Valor (Melhorado)
    fig_bar = px.bar(
        df.nlargest(10, 'valor'), 
        x='valor', 
        y='empresa',
        orientation='h',
        title=f'🏆 Top 10 {data_type} por Valor',
        labels={'valor': 'Valor (R$)', 'empresa': 'Empresa/Favorecido'},
        color='valor',
        color_continuous_scale='RdYlBu_r',
        text='valor_formatado',
        hover_data=['orgao']
    )
    fig_bar.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title_font_size=16,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=True
    )
    fig_bar.update_traces(textposition='outside', textfont_size=10)
    
    # Gráfico 2: Distribuição por Valor (Melhorado)
    fig_hist = px.histogram(
        df, 
        x='valor',
        nbins=15,
        title=f'📊 Distribuição de Valores - {data_type}',
        labels={'valor': 'Valor (R$)', 'count': 'Quantidade'},
        color_discrete_sequence=['#1f77b4'],
        marginal='box'  # Adicionar boxplot
    )
    fig_hist.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title_font_size=16
    )
    
    # Gráfico 3: Pizza das Empresas (Melhorado)
    empresas_valor = df.groupby('empresa')['valor'].sum().nlargest(8).reset_index()
    outros_valor = df[~df['empresa'].isin(empresas_valor['empresa'])]['valor'].sum()
    
    if outros_valor > 0:
        empresas_valor = pd.concat([
            empresas_valor,
            pd.DataFrame({'empresa': ['Outros'], 'valor': [outros_valor]})
        ])
    
    fig_pie = px.pie(
        empresas_valor,
        values='valor',
        names='empresa',
        title=f'🥧 Participação por Empresa - {data_type}',
        color_discrete_sequence=px.colors.qualitative.Set3,
        hover_data=['valor']
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(
        height=400,
        font=dict(size=12),
        title_font_size=16
    )
    
    # Gráfico 4: NOVO - Sunburst por Órgão e Empresa
    # Preparar dados para sunburst
    sunburst_data = []
    for orgao in df['orgao'].unique():
        if orgao != 'N/A':
            orgao_data = df[df['orgao'] == orgao]
            orgao_total = orgao_data['valor'].sum()
            
            # Top 5 empresas por órgão
            top_empresas = orgao_data.groupby('empresa')['valor'].sum().nlargest(5)
            
            for empresa, valor in top_empresas.items():
                sunburst_data.append({
                    'orgao': orgao,
                    'empresa': empresa,
                    'valor': valor,
                    'path': f"{orgao} / {empresa}"
                })
    
    if sunburst_data:
        df_sunburst = pd.DataFrame(sunburst_data)
        
        fig_sunburst = px.sunburst(
            df_sunburst,
            path=['orgao', 'empresa'],
            values='valor',
            title=f'🌅 Hierarquia Órgão → Empresa - {data_type}',
            color='valor',
            color_continuous_scale='viridis'
        )
        fig_sunburst.update_layout(
            height=500,
            font=dict(size=12),
            title_font_size=16
        )
    else:
        fig_sunburst = None
    
    return fig_bar, fig_hist, fig_pie, fig_sunburst

async def call_transparency_api(endpoint, params=None):
    """Chamar API do Portal da Transparência"""
    if not TRANSPARENCY_API_KEY:
        return {"error": "API key não configurada"}
    
    base_url = "https://api.portaldatransparencia.gov.br"
    headers = {
        "chave-api-dados": TRANSPARENCY_API_KEY,
        "User-Agent": "CidadaoAI/1.0"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{base_url}{endpoint}",
                headers=headers,
                params=params or {}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": f"Erro na requisição: {str(e)}"}

def search_data(data_type, year, search_term):
    """Buscar dados reais na API do Portal da Transparência"""
    if not search_term:
        return """
        <div style="padding: 2rem; text-align: center;">
            <p style="color: var(--text-secondary);">Digite uma consulta para buscar dados</p>
        </div>
        """, None, None, None
    
    # Mapear tipo de dados para endpoint
    endpoint_map = {
        "Contratos Públicos": "/api-de-dados/contratos",
        "Despesas Orçamentárias": "/api-de-dados/despesas", 
        "Licitações e Pregões": "/api-de-dados/licitacoes"
    }
    
    endpoint = endpoint_map.get(data_type, "/api-de-dados/contratos")
    
    # Parâmetros da consulta
    params = {
        "ano": int(year),
        "pagina": 1,
        "tamanhoPagina": 10
    }
    
    # Executar consulta na API
    try:
        # Usar asyncio para chamar a API assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        api_result = loop.run_until_complete(call_transparency_api(endpoint, params))
        loop.close()
        
        if "error" in api_result:
            return f"""
            <div style="padding: 2rem; text-align: center; color: #DC2626;">
                <h3>Erro na API</h3>
                <p>{api_result['error']}</p>
            </div>
            """, None, None, None
        
        # Processar resultados
        results = api_result if isinstance(api_result, list) else []
        
        if not results:
            return """
            <div style="padding: 2rem; text-align: center;">
                <h3>Nenhum resultado encontrado</h3>
                <p style="color: var(--text-secondary);">Tente ajustar os filtros ou termo de busca</p>
            </div>
            """, None, None, None
        
    except Exception as e:
        return f"""
        <div style="padding: 2rem; text-align: center; color: #DC2626;">
            <h3>Erro na busca</h3>
            <p>{str(e)}</p>
        </div>
        """, None, None, None
    
    # Header do dashboard com resultados
    html = f"""
    <div class="dashboard-results">
        <div class="results-header">
            <h3>📊 Resultados da Investigação</h3>
            <div class="search-info">
                <div class="search-badge">
                    <span class="badge-icon">🔍</span>
                    <span>"{search_term}"</span>
                </div>
                <div class="search-meta">
                    <span>{data_type} • {year} • {len(results)} registros</span>
                </div>
            </div>
        </div>
        
        <div class="results-summary">
            <div class="summary-card">
                <div class="summary-icon">📈</div>
                <div class="summary-content">
                    <h4>Registros Encontrados</h4>
                    <p>{len(results)}</p>
                </div>
            </div>
            <div class="summary-card">
                <div class="summary-icon">💰</div>
                <div class="summary-content">
                    <h4>Valor Total</h4>
                    <p>Calculando...</p>
                </div>
            </div>
            <div class="summary-card">
                <div class="summary-icon">🏢</div>
                <div class="summary-content">
                    <h4>Empresas Únicas</h4>
                    <p>Analisando...</p>
                </div>
            </div>
        </div>
        
        <div class="results-content">
    """
    
    # Processar resultados reais da API
    for i, item in enumerate(results[:5], 1):  # Mostrar apenas 5 primeiros
        # Adaptar campos conforme retorno da API
        numero = item.get('numero', item.get('id', f'REG-{i:03d}'))
        empresa = item.get('nome', item.get('razaoSocial', item.get('fornecedor', 'N/A')))
        valor = item.get('valor', item.get('valorContrato', item.get('valorInicial', 0)))
        objeto = item.get('objeto', item.get('descricao', 'N/A'))
        
        # Formatar valor
        if isinstance(valor, (int, float)):
            valor_fmt = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        else:
            valor_fmt = str(valor)
        
        html += f"""
        <div class="result-card">
            <div class="result-header">
                <div class="result-title">
                    <h4>{data_type} #{numero}</h4>
                    <span class="result-badge">Público</span>
                </div>
                <div class="result-value">{valor_fmt}</div>
            </div>
            
            <div class="result-body">
                <div class="result-field">
                    <strong>Empresa/Favorecido:</strong>
                    <span>{empresa}</span>
                </div>
                <div class="result-field">
                    <strong>Objeto:</strong>
                    <span>{objeto[:150]}{'...' if len(str(objeto)) > 150 else ''}</span>
                </div>
            </div>
            
            <div class="result-actions">
                <button class="btn-action" onclick="analyzeRecord('{numero}')">
                    <span>🔍</span> Analisar
                </button>
                <details class="result-details">
                    <summary>💾 Dados Técnicos</summary>
                    <pre class="json-data">{json.dumps(item, indent=2, ensure_ascii=False)}</pre>
                </details>
            </div>
        </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    # Gerar visualizações
    fig_bar, fig_hist, fig_pie, fig_sunburst = create_visualizations(results, data_type)
    
    return html, fig_bar, fig_hist, fig_pie, fig_sunburst

def create_advanced_search_page():
    """Página de consulta avançada baseada no mockup 2"""
    return """
    <div class="header">
        <div class="logo">
            <span style="font-size: 2rem;">🇧🇷</span>
            <span class="logo-text">Cidadão.AI</span>
        </div>
        <div class="header-actions">
            <button class="theme-toggle" onclick="toggleTheme()" id="theme-toggle-btn-2">
                <span>🌙</span> Modo Escuro
            </button>
        </div>
    </div>
    
    <div class="advanced-search-container">
        <div class="page-title">
            <h1>🔍 Consulta Avançada</h1>
            <p>Dashboard inteligente para investigação de dados públicos</p>
        </div>
    </div>
    """

def create_landing_page():
    """Landing page baseada no mockup 1"""
    return """
    <div class="header">
        <div class="logo">
            <span style="font-size: 2rem;">🇧🇷</span>
            <span class="logo-text">Cidadão.AI</span>
        </div>
        <div style="display: flex; gap: 1rem; align-items: center;">
            <button class="credits-button" onclick="showCreditsModal()" style="background: transparent; border: 2px solid var(--border-color); border-radius: 30px; padding: 0.5rem 1rem; cursor: pointer; transition: all 0.2s ease; color: var(--text-primary); font-weight: 500; display: flex; align-items: center; gap: 0.5rem;">
                <span>ℹ️</span> Créditos
            </button>
            <button class="theme-toggle" onclick="toggleTheme()" id="theme-toggle-btn">
                <span>🌙</span> Modo Escuro
            </button>
        </div>
    </div>
    
    <div class="landing-page">
        <div class="hero-content">
            <h1 class="hero-title">Cidadão.AI</h1>
            <p class="hero-subtitle">
                Plataforma inteligente que facilita a análise de dados públicos brasileiros. Descubra contratos suspeitos, gastos irregulares e licitações problemáticas de forma simples e rápida.
            </p>
            
            <div class="action-buttons">
                <button class="btn btn-primary" id="btnAdvanced">
                    <span>🔍</span> Consulta Avançada
                </button>
                <button class="btn btn-secondary" id="btnChat">
                    <span>💬</span> Pergunte ao Modelo
                </button>
            </div>
        </div>
    </div>
    
    <!-- Modal de Créditos Centralizado -->
    <div id="creditsModal" class="modal-overlay" onclick="handleModalClick(event)" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); z-index: 2000; justify-content: center; align-items: center;">
        <div class="modal-content" style="background: var(--bg-primary); border-radius: 20px; padding: 2.5rem; max-width: 700px; width: 90%; max-height: 85vh; overflow-y: auto; box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3); border: 1px solid var(--border-color); position: relative;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <h2 style="color: var(--text-primary); margin: 0; font-size: 1.75rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem;">
                    <span>🏆</span> Créditos
                </h2>
                <button onclick="hideCreditsModal()" style="background: transparent; border: none; font-size: 1.8rem; cursor: pointer; color: var(--text-secondary); padding: 0.5rem; border-radius: 50%; transition: all 0.2s ease; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">×</button>
            </div>
            
            <div style="color: var(--text-secondary); line-height: 1.7;">
                <!-- Projeto Principal -->
                <div style="margin-bottom: 2rem; padding: 1.5rem; background: var(--bg-secondary); border-radius: 15px; border-left: 4px solid var(--primary-green);">
                    <h3 style="color: var(--text-primary); margin-bottom: 0.75rem; font-size: 1.25rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span>🇧🇷</span> Cidadão.AI
                    </h3>
                    <p style="margin-bottom: 1rem; font-size: 1rem;">Sistema Multi-Agente de Inteligência Artificial para análise de transparência pública no Brasil</p>
                    <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
                        <a href="https://github.com/anderson-ufrj/cidadao.ai" target="_blank" style="color: var(--primary-blue); text-decoration: none; padding: 0.5rem 1rem; border: 1px solid var(--border-color); border-radius: 8px; transition: all 0.2s ease; font-size: 0.9rem; display: flex; align-items: center; gap: 0.5rem;">
                            <span>📚</span> Repositório
                        </a>
                        <a href="https://anderson-ufrj.github.io/cidadao.ai/" target="_blank" style="color: var(--primary-blue); text-decoration: none; padding: 0.5rem 1rem; border: 1px solid var(--border-color); border-radius: 8px; transition: all 0.2s ease; font-size: 0.9rem; display: flex; align-items: center; gap: 0.5rem;">
                            <span>📖</span> Documentação
                        </a>
                        <a href="https://huggingface.co/spaces/neural-thinker/cidadao.ia" target="_blank" style="color: var(--primary-blue); text-decoration: none; padding: 0.5rem 1rem; border: 1px solid var(--border-color); border-radius: 8px; transition: all 0.2s ease; font-size: 0.9rem; display: flex; align-items: center; gap: 0.5rem;">
                            <span>🤗</span> Demo
                        </a>
                    </div>
                </div>
                
                <!-- Curso/Formação -->
                <div style="margin-bottom: 2rem; padding: 1.5rem; background: var(--bg-secondary); border-radius: 15px; border-left: 4px solid var(--primary-blue);">
                    <h3 style="color: var(--text-primary); margin-bottom: 0.75rem; font-size: 1.25rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span>🎓</span> Formação Acadêmica
                    </h3>
                    <p style="margin-bottom: 0.5rem;"><strong>Trabalho de Conclusão de Curso</strong></p>
                    <p style="margin-bottom: 0.5rem;">Bacharelado em Ciência da Computação</p>
                    <p style="margin-bottom: 0.5rem;">Instituto Federal do Sul de Minas Gerais - Campus Muzambinho</p>
                    <p style="margin-bottom: 1rem; font-size: 0.9rem; color: var(--text-secondary);">Orientação: Prof. Dr. [Nome do Orientador]</p>
                    <a href="https://cursos.muz.ifsuldeminas.edu.br/ciencia-da-computacao" target="_blank" style="color: var(--primary-blue); text-decoration: none; padding: 0.5rem 1rem; border: 1px solid var(--border-color); border-radius: 8px; transition: all 0.2s ease; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 0.5rem;">
                        <span>🏫</span> Sobre o Curso
                    </a>
                </div>
                
                <!-- Tecnologias -->
                <div style="margin-bottom: 2rem; padding: 1.5rem; background: var(--bg-secondary); border-radius: 15px; border-left: 4px solid var(--primary-yellow);">
                    <h3 style="color: var(--text-primary); margin-bottom: 0.75rem; font-size: 1.25rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span>🛠️</span> Stack Tecnológica
                    </h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.5rem; margin-bottom: 1rem;">
                        <div style="background: var(--bg-primary); padding: 0.5rem; border-radius: 6px; font-size: 0.85rem; text-align: center;">
                            <strong>Frontend:</strong> Gradio 5.0
                        </div>
                        <div style="background: var(--bg-primary); padding: 0.5rem; border-radius: 6px; font-size: 0.85rem; text-align: center;">
                            <strong>IA:</strong> GROQ & LLaMA
                        </div>
                        <div style="background: var(--bg-primary); padding: 0.5rem; border-radius: 6px; font-size: 0.85rem; text-align: center;">
                            <strong>API:</strong> Portal da Transparência
                        </div>
                        <div style="background: var(--bg-primary); padding: 0.5rem; border-radius: 6px; font-size: 0.85rem; text-align: center;">
                            <strong>Deploy:</strong> HuggingFace Spaces
                        </div>
                    </div>
                </div>
                
                <!-- Agradecimentos -->
                <div style="margin-bottom: 1.5rem; padding: 1.5rem; background: var(--bg-secondary); border-radius: 15px; border-left: 4px solid var(--primary-green);">
                    <h3 style="color: var(--text-primary); margin-bottom: 0.75rem; font-size: 1.25rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span>🙏</span> Agradecimentos
                    </h3>
                    <p style="margin-bottom: 0.5rem;">• IFSuldeminas Campus Muzambinho pelo suporte acadêmico</p>
                    <p style="margin-bottom: 0.5rem;">• Portal da Transparência pela API pública</p>
                    <p style="margin-bottom: 0.5rem;">• Comunidade open source pelas bibliotecas utilizadas</p>
                    <p style="margin-bottom: 0.5rem;">• Hugging Face por hospedar o projeto gratuitamente</p>
                </div>
                
                <!-- Copyright -->
                <div style="text-align: center; padding-top: 1.5rem; border-top: 1px solid var(--border-color);">
                    <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                        <strong>© 2025 Cidadão.AI</strong>
                    </p>
                    <p style="font-size: 0.8rem; color: var(--text-secondary);">
                        Democratizando o acesso à transparência pública brasileira
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Botão de ajuda flutuante -->
    <button class="help-button" onclick="toggleHelpModal()" title="Sobre o Projeto">
        ❓
    </button>
    
    <!-- Modal de Ajuda em formato de balão -->
    <div id="helpModal" class="help-modal" onclick="handleHelpModalClick(event)">
        <div class="help-modal-header">
            <span>🎓</span>
            <h3>Sobre o Projeto</h3>
            <button class="help-modal-close" onclick="hideHelpModal()">×</button>
        </div>
        
        <div class="help-modal-content">
            <!-- Developer Section -->
            <div class="help-section">
                <h4>👨‍💻 Desenvolvedor</h4>
                <div class="help-info">
                    <p><strong>Anderson Henrique da Silva</strong></p>
                    <p>Bacharelado em Ciência da Computação</p>
                    <p>IFSuldeminas Campus Muzambinho</p>
                    
                    <div class="help-links">
                        <a href="https://github.com/anderson-ufrj" target="_blank" class="help-link">
                            <span>🐙</span> GitHub
                        </a>
                        <a href="https://www.linkedin.com/in/anderson-h-silva95/" target="_blank" class="help-link">
                            <span>💼</span> LinkedIn
                        </a>
                        <a href="mailto:andersonhs27@gmail.com" class="help-link">
                            <span>📧</span> Email
                        </a>
                        <a href="https://x.com/neural_thinker" target="_blank" class="help-link">
                            <span>🐦</span> Twitter
                        </a>
                        <a href="https://www.instagram.com/andhenrique_/" target="_blank" class="help-link">
                            <span>📸</span> Instagram
                        </a>
                    </div>
                </div>
            </div>

            <!-- Institution Section -->
            <div class="help-section">
                <h4>🏛️ Instituição</h4>
                <div class="help-info">
                    <p><strong>Instituto Federal do Sul de Minas Gerais</strong></p>
                    <p>Campus Muzambinho</p>
                    <p>Curso: Bacharelado em Ciência da Computação</p>
                    
                    <div class="help-links">
                        <a href="https://cursos.muz.ifsuldeminas.edu.br/ciencia-da-computacao" target="_blank" class="help-link">
                            <span>🏫</span> Curso
                        </a>
                    </div>
                </div>
            </div>

            <!-- Project Section -->
            <div class="help-section">
                <h4>🔍 Projeto</h4>
                <div class="help-info">
                    <p><strong>Cidadão.AI</strong></p>
                    <p>Sistema Multi-Agente de IA para Transparência Pública</p>
                    
                    <div class="help-links">
                        <a href="https://github.com/anderson-ufrj/cidadao.ai" target="_blank" class="help-link">
                            <span>📦</span> Repositório
                        </a>
                        <a href="https://anderson-ufrj.github.io/cidadao.ai/" target="_blank" class="help-link">
                            <span>📖</span> Documentação
                        </a>
                        <a href="https://huggingface.co/spaces/neural-thinker/cidadao.ia" target="_blank" class="help-link">
                            <span>🤗</span> Demo Online
                        </a>
                    </div>
                </div>
            </div>

            <!-- Version Section -->
            <div class="help-section">
                <h4>🏷️ Versão</h4>
                <div class="help-info">
                    <p><strong>v1.0.0</strong> | Todos os direitos reservados</p>
                    <p style="font-size: 0.8rem; margin-top: 10px;">Trabalho de Conclusão de Curso - 2025</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Script DEFINITIVO para navegação das abas -->
    <script>
        (function() {
            console.log('🚀 DEFINITIVE Navigation Script Loaded');
            
            // Variáveis globais para controle
            let navigationReady = false;
            let gradioTabsReady = false;
            let attemptCount = 0;
            const maxAttempts = 50;
            
            // Função para verificar se o Gradio está pronto
            function checkGradioReady() {
                const gradioContainer = document.querySelector('.gradio-container');
                const tabButtons = document.querySelectorAll('button[role="tab"]');
                const hasMainTabs = tabButtons.length >= 3;
                
                console.log('🔍 Gradio Status Check:', {
                    container: !!gradioContainer,
                    tabButtons: tabButtons.length,
                    hasMainTabs: hasMainTabs,
                    attempt: attemptCount + 1
                });
                
                return gradioContainer && hasMainTabs;
            }
            
            // Função DEFINITIVA para navegar para aba
            function navigateToTab(targetTabIndex, tabName) {
                console.log(`🎯 DEFINITIVE Navigation to: ${tabName} (index ${targetTabIndex})`);
                
                // Método 1: Usar seletor role="tab" direto
                const tabButtons = document.querySelectorAll('button[role="tab"]');
                console.log(`📋 Found ${tabButtons.length} tab buttons`);
                
                if (tabButtons.length > targetTabIndex) {
                    const targetTab = tabButtons[targetTabIndex];
                    console.log(`✅ Clicking tab ${targetTabIndex}:`, targetTab.textContent);
                    
                    // Forçar clique com múltiplos métodos
                    targetTab.click();
                    targetTab.focus();
                    
                    // Dispatch event manual
                    targetTab.dispatchEvent(new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    }));
                    
                    // Verificar se funcionou
                    setTimeout(() => {
                        const activeTab = document.querySelector('button[role="tab"][aria-selected="true"]');
                        if (activeTab && activeTab === targetTab) {
                            console.log('✅ SUCCESS: Tab navigation worked!');
                        } else {
                            console.log('❌ FAILED: Tab navigation did not work');
                        }
                    }, 100);
                    
                    return true;
                }
                
                console.log('❌ FAILED: Could not find target tab');
                return false;
            }
            
            // Função para configurar os botões
            function setupButtonsDefinitive() {
                console.log('⚙️ Setting up buttons (DEFINITIVE)');
                
                const btnAdvanced = document.getElementById('btnAdvanced');
                const btnChat = document.getElementById('btnChat');
                
                if (btnAdvanced && !btnAdvanced.hasAttribute('data-definitive-listener')) {
                    console.log('✅ Setting up DEFINITIVE Advanced button');
                    btnAdvanced.setAttribute('data-definitive-listener', 'true');
                    
                    btnAdvanced.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('🔍 DEFINITIVE Advanced button clicked');
                        
                        // Navegar para aba índice 1 (segunda aba)
                        navigateToTab(1, 'Consulta Avançada');
                    });
                }
                
                if (btnChat && !btnChat.hasAttribute('data-definitive-listener')) {
                    console.log('✅ Setting up DEFINITIVE Chat button');
                    btnChat.setAttribute('data-definitive-listener', 'true');
                    
                    btnChat.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('💬 DEFINITIVE Chat button clicked');
                        
                        // Navegar para aba índice 2 (terceira aba)
                        navigateToTab(2, 'Pergunte ao Modelo');
                    });
                }
            }
            
            // Função principal de inicialização
            function initializeDefinitiveNavigation() {
                attemptCount++;
                console.log(`🔄 Initialize attempt ${attemptCount}/${maxAttempts}`);
                
                if (checkGradioReady()) {
                    console.log('✅ Gradio is ready! Setting up navigation...');
                    gradioTabsReady = true;
                    setupButtonsDefinitive();
                    navigationReady = true;
                } else if (attemptCount < maxAttempts) {
                    console.log('⏳ Gradio not ready yet, retrying in 200ms...');
                    setTimeout(initializeDefinitiveNavigation, 200);
                } else {
                    console.log('❌ Max attempts reached, setup may have failed');
                }
            }
            
            // Iniciar imediatamente
            initializeDefinitiveNavigation();
            
            // Backup: Observer para detectar mudanças no DOM
            const observer = new MutationObserver(function(mutations) {
                if (!navigationReady) {
                    console.log('🔄 DOM changed, checking if Gradio is ready...');
                    if (checkGradioReady()) {
                        setupButtonsDefinitive();
                        navigationReady = true;
                    }
                }
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            // Expor função global para debug
            window.testNavigation = function() {
                console.log('🧪 Testing navigation manually...');
                console.log('Gradio ready:', checkGradioReady());
                console.log('Navigation ready:', navigationReady);
                
                const tabs = document.querySelectorAll('button[role="tab"]');
                tabs.forEach((tab, i) => {
                    console.log(`Tab ${i}:`, tab.textContent);
                });
            };
            
            console.log('🚀 DEFINITIVE Navigation Script Setup Complete');
        })();
    </script>
    """

async def call_groq_api(message):
    """Chamar API do GROQ para chat"""
    if not GROQ_API_KEY:
        return "API key do GROQ não configurada"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "Você é um assistente especializado em dados do governo brasileiro e transparência pública. Responda de forma clara e objetiva sobre gastos públicos, contratos, licitações e dados governamentais."
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "model": "llama3-8b-8192",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Erro na API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erro na requisição: {str(e)}"

async def run_investigation(query):
    """Executar investigação usando o InvestigatorAgent"""
    try:
        # Import here to avoid circular imports
        from src.agents.investigator_agent import InvestigatorAgent, InvestigationRequest
        from src.agents.base_agent import AgentMessage, AgentContext
        
        # Create investigation request
        request = InvestigationRequest(
            query=query,
            max_records=50  # Limit for chat interface
        )
        
        # Create agent context
        context = AgentContext(
            investigation_id=f"chat_{int(time.time())}",
            user_id="chat_user",
            session_id="chat_session"
        )
        
        # Create message
        message = AgentMessage(
            message_type="investigation_request",
            content=request.dict(),
            metadata={"source": "chat"}
        )
        
        # Run investigation
        agent = InvestigatorAgent()
        result = await agent.execute(message, context)
        
        if result.content.get("status") == "completed":
            anomalies = result.content.get("anomalies", [])
            summary = result.content.get("summary", {})
            
            # Format response
            response = f"🔍 **Investigação Concluída**\n\n"
            response += f"📊 **Resumo:**\n"
            response += f"• Registros analisados: {summary.get('total_records', 0)}\n"
            response += f"• Anomalias encontradas: {len(anomalies)}\n"
            response += f"• Valor total: R$ {summary.get('total_value', 0):,.2f}\n\n"
            
            if anomalies:
                response += "🚨 **Anomalias Detectadas:**\n"
                for i, anomaly in enumerate(anomalies[:3], 1):  # Show top 3
                    response += f"\n{i}. **{anomaly['anomaly_type']}**\n"
                    response += f"   • Severidade: {anomaly['severity']:.2f}\n"
                    response += f"   • Confiança: {anomaly['confidence']:.2f}\n"
                    response += f"   • Descrição: {anomaly['description']}\n"
                    
                    if anomaly.get('financial_impact'):
                        response += f"   • Impacto financeiro: R$ {anomaly['financial_impact']:,.2f}\n"
                
                if len(anomalies) > 3:
                    response += f"\n... e mais {len(anomalies) - 3} anomalias encontradas."
            else:
                response += "✅ **Nenhuma anomalia detectada nos dados analisados.**"
                
            return response
            
        elif result.content.get("status") == "no_data":
            return "ℹ️ Nenhum dado encontrado para os critérios especificados."
            
        else:
            return f"❌ Erro na investigação: {result.content.get('error', 'Erro desconhecido')}"
            
    except Exception as e:
        return f"❌ Erro ao executar investigação: {str(e)}"

async def run_analysis(query):
    """Executar análise usando o AnalystAgent"""
    try:
        # Import here to avoid circular imports
        from src.agents.analyst_agent import AnalystAgent, AnalysisRequest
        from src.agents.base_agent import AgentMessage, AgentContext
        
        # Create analysis request
        request = AnalysisRequest(
            query=query,
            analysis_types=["pattern_analysis", "correlation_analysis", "trend_analysis"],
            max_records=100
        )
        
        # Create agent context
        context = AgentContext(
            investigation_id=f"analysis_{int(time.time())}",
            user_id="chat_user",
            session_id="chat_session"
        )
        
        # Create message
        message = AgentMessage(
            message_type="analysis_request",
            content=request.dict(),
            metadata={"source": "chat"}
        )
        
        # Run analysis
        agent = AnalystAgent()
        result = await agent.execute(message, context)
        
        if result.content.get("status") == "completed":
            patterns = result.content.get("patterns", [])
            correlations = result.content.get("correlations", [])
            summary = result.content.get("summary", {})
            
            # Format response
            response = f"📊 **Análise Concluída**\n\n"
            response += f"📈 **Resumo:**\n"
            response += f"• Registros analisados: {summary.get('total_records', 0)}\n"
            response += f"• Padrões identificados: {len(patterns)}\n"
            response += f"• Correlações encontradas: {len(correlations)}\n"
            response += f"• Valor médio: R$ {summary.get('average_value', 0):,.2f}\n\n"
            
            if patterns:
                response += "🔍 **Padrões Identificados:**\n"
                for i, pattern in enumerate(patterns[:3], 1):  # Show top 3
                    response += f"\n{i}. **{pattern['pattern_type']}**\n"
                    response += f"   • Significância: {pattern['significance']:.2f}\n"
                    response += f"   • Confiança: {pattern['confidence']:.2f}\n"
                    response += f"   • Descrição: {pattern['description']}\n"
                    
                    if pattern.get('trend_direction'):
                        response += f"   • Tendência: {pattern['trend_direction']}\n"
                
                if len(patterns) > 3:
                    response += f"\n... e mais {len(patterns) - 3} padrões identificados."
            
            if correlations:
                response += "\n\n📊 **Correlações Encontradas:**\n"
                for i, corr in enumerate(correlations[:2], 1):  # Show top 2
                    response += f"\n{i}. **{corr['correlation_type']}**\n"
                    response += f"   • Coeficiente: {corr['correlation_coefficient']:.3f}\n"
                    response += f"   • Significância: {corr['significance_level']}\n"
                    response += f"   • Interpretação: {corr['business_interpretation']}\n"
                
                if len(correlations) > 2:
                    response += f"\n... e mais {len(correlations) - 2} correlações encontradas."
            
            if not patterns and not correlations:
                response += "ℹ️ **Nenhum padrão significativo detectado nos dados analisados.**"
                
            return response
            
        elif result.content.get("status") == "no_data":
            return "ℹ️ Nenhum dado encontrado para análise."
            
        else:
            return f"❌ Erro na análise: {result.content.get('error', 'Erro desconhecido')}"
            
    except Exception as e:
        return f"❌ Erro ao executar análise: {str(e)}"

async def run_complex_investigation(query):
    """Executar investigação complexa usando o MasterAgent"""
    try:
        # Create a comprehensive investigation using multiple agents
        investigation_id = f"master_{int(time.time())}"
        
        # Run both investigation and analysis
        investigation_task = run_investigation(query)
        analysis_task = run_analysis(query)
        
        # Execute both in parallel
        investigation_result, analysis_result = await asyncio.gather(
            investigation_task, 
            analysis_task,
            return_exceptions=True
        )
        
        # Format comprehensive response
        response = f"🎯 **Investigação Completa Executada**\n\n"
        response += f"🔍 **ID da Investigação**: {investigation_id}\n"
        response += f"📋 **Consulta**: {query}\n\n"
        
        # Add investigation results
        if isinstance(investigation_result, str) and not investigation_result.startswith("❌"):
            response += "## 🔍 **INVESTIGAÇÃO DE ANOMALIAS**\n"
            response += investigation_result + "\n\n"
        elif isinstance(investigation_result, Exception):
            response += f"⚠️ **Erro na Investigação**: {str(investigation_result)}\n\n"
        
        # Add analysis results  
        if isinstance(analysis_result, str) and not analysis_result.startswith("❌"):
            response += "## 📊 **ANÁLISE DE PADRÕES**\n"
            response += analysis_result + "\n\n"
        elif isinstance(analysis_result, Exception):
            response += f"⚠️ **Erro na Análise**: {str(analysis_result)}\n\n"
        
        # Add coordination summary
        response += "## 🤖 **Coordenação Multi-Agente**\n"
        response += f"• **InvestigatorAgent**: {'✅ Executado' if isinstance(investigation_result, str) else '❌ Falhou'}\n"
        response += f"• **AnalystAgent**: {'✅ Executado' if isinstance(analysis_result, str) else '❌ Falhou'}\n"
        response += f"• **MasterAgent**: ✅ Coordenação concluída\n\n"
        
        # Add recommendations
        response += "## 💡 **Recomendações**\n"
        response += "• Revise os resultados de anomalias para priorizar investigações\n"
        response += "• Analise os padrões identificados para entender tendências\n"
        response += "• Considere expandir a investigação para períodos anteriores\n"
        response += "• Documente achados para futuras referências\n\n"
        
        response += f"⏱️ **Processamento**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        
        return response
        
    except Exception as e:
        return f"❌ Erro na investigação complexa: {str(e)}"

async def generate_pdf_report(query, investigation_data=None, analysis_data=None):
    """Gerar relatório PDF usando o ReporterAgent"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        import io
        import base64
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center
        )
        
        story.append(Paragraph("🇧🇷 Cidadão.AI - Relatório de Transparência", title_style))
        story.append(Spacer(1, 12))
        
        # Metadata
        meta_style = styles['Normal']
        story.append(Paragraph(f"<b>Data:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", meta_style))
        story.append(Paragraph(f"<b>Consulta:</b> {query}", meta_style))
        story.append(Spacer(1, 20))
        
        # Investigation Results
        if investigation_data:
            story.append(Paragraph("🔍 INVESTIGAÇÃO DE ANOMALIAS", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Clean and format investigation data
            clean_text = investigation_data.replace("**", "").replace("##", "").replace("•", "-")
            story.append(Paragraph(clean_text, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Analysis Results
        if analysis_data:
            story.append(Paragraph("📊 ANÁLISE DE PADRÕES", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Clean and format analysis data
            clean_text = analysis_data.replace("**", "").replace("##", "").replace("•", "-")
            story.append(Paragraph(clean_text, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Summary Table
        story.append(Paragraph("📋 RESUMO EXECUTIVO", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        summary_data = [
            ['Aspecto', 'Status', 'Observações'],
            ['Dados Coletados', '✅ Sucesso', 'Portal da Transparência'],
            ['Anomalias', '🔍 Analisadas', 'Detecção automática'],
            ['Padrões', '📊 Identificados', 'Análise estatística'],
            ['Recomendações', '💡 Geradas', 'Baseadas em evidências']
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=1
        )
        story.append(Paragraph("Relatório gerado automaticamente pelo sistema Cidadão.AI", footer_style))
        story.append(Paragraph("Sistema de Transparência Pública com Inteligência Artificial", footer_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Encode to base64 for download
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        
        return pdf_base64, len(pdf_data)
        
    except ImportError:
        return None, 0  # ReportLab not available
    except Exception as e:
        raise Exception(f"Erro ao gerar PDF: {str(e)}")

async def run_investigation_with_pdf(query):
    """Executar investigação e gerar PDF"""
    try:
        # Run complex investigation
        investigation_result = await run_complex_investigation(query)
        
        # Try to generate PDF
        try:
            pdf_data, pdf_size = await generate_pdf_report(query, investigation_result)
            
            if pdf_data:
                # Add download link to response
                download_link = f"data:application/pdf;base64,{pdf_data}"
                investigation_result += f"\n\n📄 **Relatório PDF Gerado**\n"
                investigation_result += f"• Tamanho: {pdf_size:,} bytes\n"
                investigation_result += f"• [📥 Baixar Relatório PDF]({download_link})\n"
                investigation_result += f"• Clique no link acima para fazer download do relatório completo em PDF"
            else:
                investigation_result += f"\n\n⚠️ **PDF não disponível** (ReportLab não instalado)"
                
        except Exception as e:
            investigation_result += f"\n\n❌ **Erro ao gerar PDF**: {str(e)}"
        
        return investigation_result
        
    except Exception as e:
        return f"❌ Erro na investigação com PDF: {str(e)}"

def chat_fn(message, history):
    if message:
        history = history or []
        
        # Check if message requests investigation or analysis
        investigation_keywords = [
            "investiga", "anomalia", "suspeito", "irregular", "detectar", "verificar", 
            "auditor", "fraude", "corrupção", "contratos suspeitos"
        ]
        
        analysis_keywords = [
            "analise", "análise", "padrão", "padroes", "tendência", "tendencia",
            "correlação", "correlacao", "estatística", "estatistica", "relatório", 
            "relatorio", "dashboard", "gráfico", "grafico", "comparar", "comparação"
        ]
        
        complex_keywords = [
            "investigação completa", "análise completa", "estudo detalhado", "auditoria completa",
            "coordene", "combine", "multi-agente", "múltiplos", "profundo", "abrangente",
            "orquestre", "planeje", "estratégia", "plano de investigação"
        ]
        
        pdf_keywords = [
            "relatório", "relatorio", "pdf", "documento", "gerar pdf", "exportar",
            "download", "baixar", "salvar", "gerar documento", "criar relatório"
        ]
        
        is_investigation_request = any(keyword in message.lower() for keyword in investigation_keywords)
        is_analysis_request = any(keyword in message.lower() for keyword in analysis_keywords)
        is_complex_request = any(keyword in message.lower() for keyword in complex_keywords)
        is_pdf_request = any(keyword in message.lower() for keyword in pdf_keywords)
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if is_pdf_request:
                # Generate PDF report with investigation
                response = loop.run_until_complete(run_investigation_with_pdf(message))
            elif is_complex_request:
                # Use MasterAgent for complex investigations
                response = loop.run_until_complete(run_complex_investigation(message))
            elif is_investigation_request:
                # Use InvestigatorAgent for investigation requests
                response = loop.run_until_complete(run_investigation(message))
            elif is_analysis_request:
                # Use AnalystAgent for analysis requests
                response = loop.run_until_complete(run_analysis(message))
            else:
                # Use GROQ API for general questions
                response = loop.run_until_complete(call_groq_api(message))
            
            loop.close()
        except Exception as e:
            response = f"Erro ao processar mensagem: {str(e)}"
        
        history.append((message, response))
        return history, ""
    return history, ""

def create_interface():
    """Interface principal"""
    
    # Carregar CSS e JS externos
    with open('static/css/main.css', 'r') as f:
        css_content = f.read()
    
    with open('static/js/main.js', 'r') as f:
        js_content = f.read()
    
    with gr.Blocks(
        css=css_content,
        title="Cidadão.AI",
        theme=gr.themes.Base(),
        head=f"""
        <style>body {{ margin: 0; padding: 0; }}</style>
        <script>{js_content}</script>
        """
    ) as app:
        
        # Landing page como primeira aba
        with gr.Tab("🏠 Cidadão.AI"):
            gr.HTML(create_landing_page())
        
        # Aba de consulta avançada
        with gr.Tab("🔍 Consulta Avançada"):
            gr.HTML(create_advanced_search_page())
            
            with gr.Row():
                # Sidebar lateral com menu e filtros
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div class="sidebar-container">
                        <div class="sidebar-header">
                            <h3>🎛️ Painel de Controle</h3>
                        </div>
                        
                        <div class="sidebar-section">
                            <h4>📊 Tipo de Análise</h4>
                        </div>
                    </div>
                    """)
                    
                    data_type = gr.Radio(
                        label="Fonte de Dados",
                        choices=["Contratos Públicos", "Despesas Orçamentárias", "Licitações e Pregões"],
                        value="Contratos Públicos"
                    )
                    
                    gr.HTML("""
                    <div class="sidebar-section">
                        <h4>📅 Período</h4>
                    </div>
                    """)
                    
                    year = gr.Number(
                        label="Ano",
                        value=2024,
                        minimum=2000,
                        maximum=2024
                    )
                    
                    gr.HTML("""
                    <div class="sidebar-section">
                        <h4>🔍 Busca</h4>
                    </div>
                    """)
                    
                    search_term = gr.Textbox(
                        label="Termo de Busca",
                        placeholder="Ex: 'contrato suspeito', 'empresa XYZ'...",
                        lines=3
                    )
                    
                    search_btn = gr.Button("🚀 Iniciar Investigação", variant="primary", size="lg")
                
                # Dashboard central
                with gr.Column(scale=3):
                    gr.HTML("""
                    <div class="dashboard-container">
                        <div class="dashboard-header">
                            <h2>📈 Dashboard de Análise</h2>
                            <p>Área principal para visualização dos resultados da investigação</p>
                        </div>
                    </div>
                    """)
                    
                    # Abas para organizar resultados e gráficos
                    with gr.Tabs():
                        with gr.Tab("📋 Resultados"):
                            results = gr.HTML(
                                value="""
                                <div class="dashboard-main">
                                    <div class="dashboard-welcome">
                                        <div class="welcome-icon">🎯</div>
                                        <h3>Bem-vindo ao Dashboard de Transparência</h3>
                                        <p>Configure os filtros na lateral e inicie sua investigação para ver os resultados aqui.</p>
                                        
                                        <div class="dashboard-stats">
                                            <div class="stat-card">
                                                <div class="stat-icon">📊</div>
                                                <div class="stat-content">
                                                    <h4>Dados Disponíveis</h4>
                                                    <p>Portal da Transparência</p>
                                                </div>
                                            </div>
                                            
                                            <div class="stat-card">
                                                <div class="stat-icon">🤖</div>
                                                <div class="stat-content">
                                                    <h4>IA Especializada</h4>
                                                    <p>Análise Inteligente</p>
                                                </div>
                                            </div>
                                            
                                            <div class="stat-card">
                                                <div class="stat-icon">📈</div>
                                                <div class="stat-content">
                                                    <h4>Relatórios</h4>
                                                    <p>Insights Automatizados</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                """
                            )
                        
                        with gr.Tab("📊 Top 10 por Valor"):
                            chart_bar = gr.Plot(label="Gráfico de Barras")
                        
                        with gr.Tab("📈 Distribuição"):
                            chart_hist = gr.Plot(label="Histograma")
                        
                        with gr.Tab("🥧 Participação"):
                            chart_pie = gr.Plot(label="Gráfico Pizza")
                        
                        with gr.Tab("🌅 Hierarquia"):
                            chart_sunburst = gr.Plot(label="Sunburst Órgão-Empresa")
            
            search_btn.click(
                fn=search_data,
                inputs=[data_type, year, search_term],
                outputs=[results, chart_bar, chart_hist, chart_pie, chart_sunburst]
            )
        
        # Aba de perguntas ao modelo
        with gr.Tab("💬 Pergunte ao Modelo"):
            gr.HTML("""
                <div class="header">
                    <div class="logo">
                        <span style="font-size: 2rem;">🇧🇷</span>
                        <span class="logo-text">Cidadão.AI</span>
                    </div>
                    <button class="theme-toggle" onclick="toggleTheme()" id="theme-toggle-btn-3">
                        <span>🌙</span> Modo Escuro
                    </button>
                </div>
                <div style="padding-top: 100px; text-align: center;">
                    <h2 style="margin-bottom: 2rem;">Pergunte ao Modelo</h2>
                </div>
            """)
            
            chatbot = gr.Chatbot(
                height=400,
                show_label=False,
                avatar_images=("👤", "🤖")
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Digite sua pergunta sobre transparência pública...",
                    show_label=False,
                    scale=4,
                    lines=1
                )
                send_btn = gr.Button("Enviar", variant="primary", scale=1)
            
            msg.submit(fn=chat_fn, inputs=[msg, chatbot], outputs=[chatbot, msg])
            send_btn.click(fn=chat_fn, inputs=[msg, chatbot], outputs=[chatbot, msg])
    
    return app

# Executar aplicação
if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI - Versão Refatorada...")
    app = create_interface()
    app.launch(
        show_error=True,
        quiet=False,
        favicon_path=None,
        app_kwargs={
            "docs_url": None,
            "redoc_url": None,
        }
    )