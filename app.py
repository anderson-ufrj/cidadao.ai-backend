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
    """Criar visualizações interativas com Plotly"""
    if not results or len(results) == 0:
        return None, None, None
    
    # Preparar dados
    df_data = []
    for item in results[:20]:  # Limitar a 20 itens para performance
        valor = item.get('valor', item.get('valorContrato', item.get('valorInicial', 0)))
        empresa = item.get('nome', item.get('razaoSocial', item.get('fornecedor', 'N/A')))
        numero = item.get('numero', item.get('id', f'REG-{len(df_data)+1:03d}'))
        
        df_data.append({
            'numero': numero,
            'empresa': empresa[:30] + '...' if len(str(empresa)) > 30 else empresa,
            'valor': float(valor) if isinstance(valor, (int, float)) else 0,
            'valor_formatado': f"R$ {float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if isinstance(valor, (int, float)) else 'N/A'
        })
    
    df = pd.DataFrame(df_data)
    
    if df.empty:
        return None, None, None
    
    # Gráfico 1: Top 10 por Valor
    fig_bar = px.bar(
        df.nlargest(10, 'valor'), 
        x='valor', 
        y='empresa',
        orientation='h',
        title=f'🏆 Top 10 {data_type} por Valor',
        labels={'valor': 'Valor (R$)', 'empresa': 'Empresa/Favorecido'},
        color='valor',
        color_continuous_scale='viridis',
        text='valor_formatado'
    )
    fig_bar.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title_font_size=16,
        yaxis={'categoryorder': 'total ascending'}
    )
    fig_bar.update_traces(textposition='outside')
    
    # Gráfico 2: Distribuição por Valor
    fig_hist = px.histogram(
        df, 
        x='valor',
        nbins=10,
        title=f'📊 Distribuição de Valores - {data_type}',
        labels={'valor': 'Valor (R$)', 'count': 'Quantidade'},
        color_discrete_sequence=['#0066CC']
    )
    fig_hist.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title_font_size=16
    )
    
    # Gráfico 3: Pizza das Empresas
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
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title_font_size=16
    )
    
    return fig_bar, fig_hist, fig_pie

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
    fig_bar, fig_hist, fig_pie = create_visualizations(results, data_type)
    
    return html, fig_bar, fig_hist, fig_pie

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
    
    <!-- Script inline para garantir que os botões funcionem -->
    <script>
        (function() {
            console.log('🚀 Landing page inline script loaded');
            console.log('📊 Current URL:', window.location.href);
            console.log('📊 Gradio container:', document.querySelector('.gradio-container'));
            
            // Função de debugging aprimorada
            function debugDOMStructure() {
                console.log('🔍 === DEBUG DOM STRUCTURE ===');
                
                // Buscar todos os possíveis containers de tabs
                const possibleSelectors = [
                    '[role="tablist"]',
                    '.tabs',
                    '.tab-nav',
                    '.gradio-tabs',
                    'div[data-testid*="tab"]',
                    '.svelte-kqij2n', // Gradio 5 sometimes uses svelte classes
                    '[class*="tab"]'
                ];
                
                possibleSelectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        console.log(`✅ Found ${elements.length} elements with selector: ${selector}`);
                        elements.forEach((el, i) => {
                            console.log(`  Element ${i}:`, {
                                tagName: el.tagName,
                                className: el.className,
                                role: el.getAttribute('role'),
                                children: el.children.length
                            });
                        });
                    }
                });
                
                // Buscar todos os botões
                const allButtons = document.querySelectorAll('button');
                console.log(`🔘 Total buttons found: ${allButtons.length}`);
                
                // Filtrar botões que parecem ser tabs
                const tabButtons = Array.from(allButtons).filter(btn => {
                    const text = btn.textContent || '';
                    const role = btn.getAttribute('role');
                    const className = btn.className || '';
                    return role === 'tab' || 
                           className.includes('tab') || 
                           text.includes('🏠') || 
                           text.includes('🔍') || 
                           text.includes('💬') ||
                           text.includes('Cidadão') ||
                           text.includes('Consulta') ||
                           text.includes('Pergunte');
                });
                
                console.log(`📑 Tab-like buttons found: ${tabButtons.length}`);
                tabButtons.forEach((btn, i) => {
                    console.log(`  Tab ${i}:`, {
                        text: btn.textContent?.trim(),
                        role: btn.getAttribute('role'),
                        className: btn.className,
                        ariaSelected: btn.getAttribute('aria-selected'),
                        parent: btn.parentElement?.className
                    });
                });
            }
            
            // Função para adicionar eventos aos botões
            function setupButtons() {
                console.log('⚙️ setupButtons called at', new Date().toISOString());
                
                // Debug DOM structure every time
                debugDOMStructure();
                
                const btnAdvanced = document.getElementById('btnAdvanced');
                const btnChat = document.getElementById('btnChat');
                
                if (btnAdvanced && !btnAdvanced.hasAttribute('data-listener')) {
                    console.log('✅ Setting up Advanced button');
                    btnAdvanced.setAttribute('data-listener', 'true');
                    btnAdvanced.addEventListener('click', function(e) {
                        e.preventDefault();
                        console.log('🔍 Advanced button clicked - inline');
                        
                        // Tentar usar a função global primeiro
                        if (typeof window.navigateToAdvanced === 'function') {
                            window.navigateToAdvanced();
                        } else {
                            // Nova estratégia: usar índice direto do Gradio
                            console.log('🔍 Using Gradio 5.0 tab navigation strategy...');
                            
                            // Primeiro, executar o debug para entender a estrutura
                            debugDOMStructure();
                            
                            // Estratégia 1: Buscar o container de tabs do Gradio 5
                            let tabContainer = document.querySelector('[role="tablist"]');
                            if (!tabContainer) {
                                // Buscar por classes do Gradio 5
                                tabContainer = document.querySelector('.tabs') || 
                                             document.querySelector('[class*="tab-nav"]') ||
                                             document.querySelector('div.gradio-container div.tabs');
                            }
                            
                            if (tabContainer) {
                                console.log('📦 Found tab container:', tabContainer.className);
                                const tabs = tabContainer.querySelectorAll('button');
                                console.log(`🔘 Found ${tabs.length} buttons in tab container`);
                                
                                // Tentar encontrar por texto
                                for (let i = 0; i < tabs.length; i++) {
                                    const tab = tabs[i];
                                    const text = tab.textContent || '';
                                    console.log(`Tab ${i}: "${text.trim()}"`);
                                    
                                    if (text.includes('Consulta Avançada') || text.includes('🔍')) {
                                        console.log('✅ Clicking Advanced tab by text match');
                                        tab.click();
                                        // Force focus
                                        tab.focus();
                                        // Dispatch events
                                        tab.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                                        tab.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                                        tab.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                                        return;
                                    }
                                }
                                
                                // Se não encontrou por texto, tentar por índice (segunda aba)
                                if (tabs.length >= 2) {
                                    console.log('📍 Clicking second tab by index');
                                    tabs[1].click();
                                    tabs[1].focus();
                                }
                            } else {
                                console.warn('⚠️ No tab container found');
                                
                                // Última tentativa: buscar qualquer botão com texto
                                const allButtons = Array.from(document.querySelectorAll('button'));
                                const advancedButton = allButtons.find(btn => 
                                    btn.textContent && (
                                        btn.textContent.includes('Consulta Avançada') || 
                                        btn.textContent.includes('🔍 Consulta')
                                    )
                                );
                                
                                if (advancedButton) {
                                    console.log('✅ Found button by global search');
                                    advancedButton.click();
                                    advancedButton.focus();
                                }
                            }
                        }
                    });
                }
                
                if (btnChat && !btnChat.hasAttribute('data-listener')) {
                    console.log('✅ Setting up Chat button');
                    btnChat.setAttribute('data-listener', 'true');
                    btnChat.addEventListener('click', function(e) {
                        e.preventDefault();
                        console.log('💬 Chat button clicked - inline');
                        
                        // Tentar usar a função global primeiro
                        if (typeof window.navigateToChat === 'function') {
                            window.navigateToChat();
                        } else {
                            // Nova estratégia: usar índice direto do Gradio
                            console.log('💬 Using Gradio 5.0 chat tab navigation strategy...');
                            
                            // Primeiro, executar o debug para entender a estrutura
                            debugDOMStructure();
                            
                            // Estratégia 1: Buscar o container de tabs do Gradio 5
                            let tabContainer = document.querySelector('[role="tablist"]');
                            if (!tabContainer) {
                                // Buscar por classes do Gradio 5
                                tabContainer = document.querySelector('.tabs') || 
                                             document.querySelector('[class*="tab-nav"]') ||
                                             document.querySelector('div.gradio-container div.tabs');
                            }
                            
                            if (tabContainer) {
                                console.log('📦 Found tab container:', tabContainer.className);
                                const tabs = tabContainer.querySelectorAll('button');
                                console.log(`🔘 Found ${tabs.length} buttons in tab container`);
                                
                                // Tentar encontrar por texto
                                for (let i = 0; i < tabs.length; i++) {
                                    const tab = tabs[i];
                                    const text = tab.textContent || '';
                                    console.log(`Tab ${i}: "${text.trim()}"`);
                                    
                                    if (text.includes('Pergunte ao Modelo') || text.includes('💬')) {
                                        console.log('✅ Clicking Chat tab by text match');
                                        tab.click();
                                        // Force focus
                                        tab.focus();
                                        // Dispatch events
                                        tab.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                                        tab.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                                        tab.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                                        return;
                                    }
                                }
                                
                                // Se não encontrou por texto, tentar por índice (terceira aba)
                                if (tabs.length >= 3) {
                                    console.log('📍 Clicking third tab by index');
                                    tabs[2].click();
                                    tabs[2].focus();
                                }
                            } else {
                                console.warn('⚠️ No tab container found');
                                
                                // Última tentativa: buscar qualquer botão com texto
                                const allButtons = Array.from(document.querySelectorAll('button'));
                                const chatButton = allButtons.find(btn => 
                                    btn.textContent && (
                                        btn.textContent.includes('Pergunte ao Modelo') || 
                                        btn.textContent.includes('💬 Pergunte')
                                    )
                                );
                                
                                if (chatButton) {
                                    console.log('✅ Found button by global search');
                                    chatButton.click();
                                    chatButton.focus();
                                }
                            }
                        }
                    });
                }
            }
            
            // Executar imediatamente
            setupButtons();
            
            // E também após um delay para garantir que Gradio carregou
            setTimeout(setupButtons, 500);
            setTimeout(setupButtons, 1000);
            setTimeout(setupButtons, 2000);
            setTimeout(setupButtons, 3000);
            setTimeout(setupButtons, 5000);
            setTimeout(setupButtons, 8000);
            setTimeout(setupButtons, 10000);
            setTimeout(setupButtons, 15000);
            setTimeout(setupButtons, 20000);
            
            
            // Observer para elementos dinâmicos
            const observer = new MutationObserver(function(mutations) {
                setupButtons();
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
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
        
        is_investigation_request = any(keyword in message.lower() for keyword in investigation_keywords)
        is_analysis_request = any(keyword in message.lower() for keyword in analysis_keywords)
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if is_investigation_request:
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
            
            search_btn.click(
                fn=search_data,
                inputs=[data_type, year, search_term],
                outputs=[results, chart_bar, chart_hist, chart_pie]
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