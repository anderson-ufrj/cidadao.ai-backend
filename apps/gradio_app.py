#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Modern Interface Following Mockups
Page-based navigation (no tabs) - Landing → Search or Chat
"""

import gradio as gr
import os
import time
import asyncio
import httpx
import json
from datetime import datetime

# Configurar variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Modern CSS following mockups exactly
custom_css = """
/* Modern Design System - Following Mockups */
:root {
    --primary-green: #10B981;
    --primary-yellow: #F59E0B;
    --primary-blue: #3B82F6;
    --accent-gradient: linear-gradient(135deg, var(--primary-green), var(--primary-yellow));
    --text-gradient: linear-gradient(135deg, #059669, #D97706);
    --glass-bg: rgba(255, 255, 255, 0.1);
    --shadow-soft: 0 4px 20px rgba(0, 0, 0, 0.1);
    --shadow-strong: 0 8px 32px rgba(0, 0, 0, 0.2);
    --border-radius: 12px;
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    /* Theme variables */
    --text-primary: #0F172A;
    --border-color: #E2E8F0;
}

/* Dark theme */
[data-theme="dark"] {
    --glass-bg: rgba(0, 0, 0, 0.2);
    --text-primary: #F1F5F9;
    --border-color: #334155;
}

body[data-theme="dark"], .gradio-container[data-theme="dark"] {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
    color: #F1F5F9 !important;
}

[data-theme="dark"] .hero-section {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .credits-section {
    background: rgba(30, 41, 59, 0.8);
}

[data-theme="dark"] .top-button,
[data-theme="dark"] .theme-toggle {
    background: rgba(30, 41, 59, 0.9);
    color: #F1F5F9;
    border-color: #334155;
}

/* Clean Typography */
.gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    max-width: 1400px;
    margin: 0 auto;
    transition: var(--transition);
}

body {
    transition: var(--transition);
}

/* Landing Page Hero - Mockup 1 */
.hero-section {
    text-align: center;
    padding: 4rem 2rem;
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border-radius: var(--border-radius);
    margin: 2rem 0;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.hero-logo {
    font-size: 4rem;
    font-weight: 900;
    background: var(--text-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1rem;
    animation: subtle-pulse 3s ease-in-out infinite;
}

.hero-subtitle {
    font-size: 1.25rem;
    color: #64748B;
    margin-bottom: 3rem;
    font-weight: 400;
}

/* Modern Buttons */
.action-buttons {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
    margin: 2rem 0;
}

.btn-modern {
    padding: 1rem 2rem;
    border-radius: var(--border-radius);
    font-weight: 600;
    font-size: 1rem;
    border: none;
    cursor: pointer;
    transition: var(--transition);
    min-width: 200px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    text-decoration: none;
}

.btn-primary {
    background: var(--accent-gradient);
    color: white;
    box-shadow: var(--shadow-soft);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-strong);
}

.btn-secondary {
    background: transparent;
    color: var(--primary-blue);
    border: 2px solid var(--primary-blue);
}

.btn-secondary:hover {
    background: var(--primary-blue);
    color: white;
}

/* Sidebar Filters - Mockup 2 */
.filter-sidebar {
    background: rgba(248, 250, 252, 0.8);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    border: 1px solid #E2E8F0;
    backdrop-filter: blur(10px);
}

/* Dashboard Area - Mockup 2 */
.dashboard-area {
    background: rgba(255, 255, 255, 0.9);
    border-radius: var(--border-radius);
    padding: 2rem;
    border: 1px solid #E2E8F0;
    backdrop-filter: blur(10px);
    min-height: 500px;
}

/* Results Cards */
.result-card {
    background: white;
    border-radius: var(--border-radius);
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: var(--shadow-soft);
    border-left: 4px solid var(--primary-blue);
    transition: var(--transition);
}

.result-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-strong);
}

/* Status Indicators */
.status-success {
    border-left-color: var(--primary-green);
    background: #F0FDF4;
}

.status-error {
    border-left-color: #EF4444;
    background: #FEF2F2;
}

.status-warning {
    border-left-color: var(--primary-yellow);
    background: #FFFBEB;
}

/* Info Button - Bottom Right Corner */
.info-button {
    position: fixed;
    bottom: 1rem;
    right: 1rem;
    background: var(--primary-blue);
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    cursor: pointer;
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    box-shadow: var(--shadow-soft);
    transition: var(--transition);
}

.info-button:hover {
    transform: scale(1.1);
    box-shadow: var(--shadow-strong);
}

/* Top Right Buttons - About and Theme */
.top-right-buttons {
    position: fixed;
    top: 1rem;
    right: 1rem;
    display: flex;
    gap: 0.5rem;
    z-index: 1000;
}

.top-button {
    background: rgba(255, 255, 255, 0.9);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 0.5rem 1rem;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: var(--transition);
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow-soft);
}

.top-button:hover {
    background: var(--primary-blue);
    color: white;
    transform: translateY(-1px);
}

.theme-toggle {
    background: rgba(255, 255, 255, 0.9);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 0.5rem;
    cursor: pointer;
    font-size: 1rem;
    transition: var(--transition);
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow-soft);
    width: 40px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.theme-toggle:hover {
    background: var(--primary-blue);
    color: white;
    transform: translateY(-1px);
}

/* Credits Section */
.credits-section {
    text-align: center;
    padding: 2rem;
    background: rgba(248, 250, 252, 0.8);
    border-radius: var(--border-radius);
    margin-top: 2rem;
    border: 1px solid #E2E8F0;
}

.credits-text {
    font-size: 0.875rem;
    color: #64748B;
    margin: 0.5rem 0;
}

/* Chat Interface - Mockup 3 */
.chat-container {
    background: rgba(255, 255, 255, 0.9);
    border-radius: var(--border-radius);
    border: 1px solid #E2E8F0;
    backdrop-filter: blur(10px);
}

/* Animations */
@keyframes subtle-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

@keyframes fade-in-up {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in {
    animation: fade-in-up 0.6s ease-out;
}

/* Modern Tables */
.data-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: var(--shadow-soft);
}

.data-table th {
    background: #F8FAFC;
    padding: 1rem;
    text-align: left;
    font-weight: 600;
    color: #374151;
    border-bottom: 2px solid #E2E8F0;
}

.data-table td {
    padding: 1rem;
    border-bottom: 1px solid #F1F5F9;
}

.data-table tr:hover {
    background: #F8FAFC;
}

/* Responsive Design */
@media (max-width: 768px) {
    .hero-logo {
        font-size: 2.5rem;
    }
    
    .action-buttons {
        flex-direction: column;
        align-items: center;
    }
    
    .btn-modern {
        width: 100%;
        max-width: 300px;
    }
    
    .hero-section {
        padding: 2rem 1rem;
    }
}

/* Override Gradio Defaults */
.gradio-container .prose {
    max-width: none;
}

.gradio-container button {
    transition: var(--transition);
}

.gr-form {
    background: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: var(--border-radius) !important;
    backdrop-filter: blur(10px);
}

.gr-textbox, .gr-number, .gr-radio, .gr-dropdown {
    border-radius: 8px !important;
    border: 1px solid #D1D5DB !important;
    transition: var(--transition) !important;
}

.gr-textbox:focus, .gr-number:focus {
    border-color: var(--primary-blue) !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}
"""

def show_search_page():
    """Show search page and hide others"""
    return (
        gr.update(visible=False),  # Hide landing
        gr.update(visible=True),   # Show search
        gr.update(visible=False)   # Hide chat
    )

def show_chat_page():
    """Show chat page and hide others"""
    return (
        gr.update(visible=False),  # Hide landing
        gr.update(visible=False),  # Hide search
        gr.update(visible=True)    # Show chat
    )

def show_home_page():
    """Show landing page and hide others"""
    return (
        gr.update(visible=True),   # Show landing
        gr.update(visible=False),  # Hide search
        gr.update(visible=False)   # Hide chat
    )

async def call_transparency_api(endpoint, params=None):
    """Call Portal da Transparência API"""
    if not TRANSPARENCY_API_KEY:
        return {"error": "API key não configurada"}
    
    base_url = "https://api.portaldatransparencia.gov.br"
    headers = {
        "chave-api-dados": TRANSPARENCY_API_KEY,
        "User-Agent": "CidadaoAI/2.0"
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
                return {"error": f"Status {response.status_code}: {response.text[:200]}"}
    except Exception as e:
        return {"error": f"Erro na requisição: {str(e)}"}

def search_transparency_data(data_type, year, search_term, page_size=5):
    """Search real data from Portal da Transparência API following mockup requirements"""
    
    if not search_term and not data_type:
        return """
        <div class="dashboard-area">
            <h3>📊 Área do dashboard</h3>
            <p>(na página inicial, descrição e como usar, guiado, explicando como usar)</p>
            <div class="result-card">
                <h4>Como usar o sistema:</h4>
                <ol>
                    <li>Selecione o tipo de dados desejado</li>
                    <li>Escolha o ano de interesse</li>
                    <li>Digite um termo de busca (opcional)</li>
                    <li>Clique em "Buscar Dados"</li>
                </ol>
            </div>
            <div class="credits-section">
                <div class="credits-text">(créditos)</div>
            </div>
        </div>
        """
    
    # Endpoint mapping
    endpoint_map = {
        "Contratos Públicos": "/api-de-dados/contratos",
        "Despesas Orçamentárias": "/api-de-dados/despesas", 
        "Licitações e Pregões": "/api-de-dados/licitacoes"
    }
    
    endpoint = endpoint_map.get(data_type, "/api-de-dados/contratos")
    
    # Query parameters
    params = {
        "ano": int(year) if year else 2024,
        "pagina": 1,
        "tamanhoPagina": page_size
    }
    
    # Execute API call
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        api_result = loop.run_until_complete(call_transparency_api(endpoint, params))
        loop.close()
        
        if "error" in api_result:
            return f"""
            <div class="result-card status-error">
                <h3>❌ Erro na API</h3>
                <p>{api_result['error']}</p>
                <div style="margin-top: 1rem; padding: 1rem; background: #FEF2F2; border-radius: 8px;">
                    <strong>Como configurar a API:</strong>
                    <ol>
                        <li>Acesse <a href="https://portaldatransparencia.gov.br/api-de-dados" target="_blank">Portal da Transparência - API</a></li>
                        <li>Faça o cadastro gratuito</li>
                        <li>Configure a chave como secret no Hugging Face Spaces</li>
                    </ol>
                </div>
            </div>
            """
        
        # Process results
        results = api_result if isinstance(api_result, list) else []
        
        if not results:
            return """
            <div class="result-card status-warning">
                <h3>📭 Nenhum resultado encontrado</h3>
                <p>Tente ajustar os filtros ou termo de busca.</p>
            </div>
            """
        
        # Create results HTML
        html = f"""
        <div class="result-card status-success">
            <h3>✅ {len(results)} resultados encontrados</h3>
            <p>Dados do Portal da Transparência - {data_type} ({year})</p>
        </div>
        """
        
        # Create table
        html += f'<div class="result-card"><h4>📊 {data_type}</h4>'
        html += '<table class="data-table">'
        
        # Add headers based on data type
        if data_type == "Contratos Públicos":
            html += """
            <thead>
                <tr>
                    <th>Número</th>
                    <th>Empresa</th>
                    <th>Valor</th>
                    <th>Objeto</th>
                    <th>Data</th>
                </tr>
            </thead>
            <tbody>
            """
            for item in results[:page_size]:
                numero = item.get('numero', item.get('id', 'N/A'))
                empresa = item.get('nome', item.get('razaoSocial', 'N/A'))
                valor = item.get('valor', item.get('valorContrato', 0))
                objeto = item.get('objeto', item.get('descricao', 'N/A'))
                data = item.get('dataAssinatura', item.get('data', 'N/A'))
                
                valor_fmt = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if isinstance(valor, (int, float)) else str(valor)
                
                html += f"""
                <tr>
                    <td>{numero}</td>
                    <td>{empresa}</td>
                    <td><strong>{valor_fmt}</strong></td>
                    <td>{str(objeto)[:80]}{'...' if len(str(objeto)) > 80 else ''}</td>
                    <td>{data}</td>
                </tr>
                """
        
        html += '</tbody></table></div>'
        return html
        
    except Exception as e:
        return f"""
        <div class="result-card status-error">
            <h3>❌ Erro na busca</h3>
            <p>{str(e)}</p>
        </div>
        """

async def call_groq_api(message):
    """Call GROQ API for chat"""
    if not GROQ_API_KEY:
        return "⚠️ API key do GROQ não configurada. Configure GROQ_API_KEY como secret."
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": """Você é um assistente especializado em transparência pública brasileira. 
                Responda de forma clara e objetiva sobre gastos públicos, contratos, licitações e dados governamentais.
                Use emojis quando apropriado e seja educativo."""
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
                return f"❌ Erro na API: {response.status_code}"
    except Exception as e:
        return f"❌ Erro na requisição: {str(e)}"

def chat_function(message, history):
    """Chat function for the AI assistant following mockup 3"""
    if not message.strip():
        return history, ""
    
    try:
        # Call GROQ API
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(call_groq_api(message))
        loop.close()
        
        # Add to history (messages format)
        history = history or []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        
        return history, ""
        
    except Exception as e:
        history = history or []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": f"❌ Erro: {str(e)}"})
        return history, ""

def create_interface():
    """Create the main interface with page-based navigation following mockups"""
    
    # Create custom theme following Gradio 5.x best practices
    theme = gr.themes.Soft(
        primary_hue=gr.themes.colors.blue,
        secondary_hue=gr.themes.colors.green,
        neutral_hue=gr.themes.colors.slate,
        font=[gr.themes.GoogleFont('Inter'), 'ui-sans-serif', 'system-ui', 'sans-serif'],
        font_mono=[gr.themes.GoogleFont('JetBrains Mono'), 'Consolas', 'monospace']
    ).set(
        body_background_fill='linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        block_background_fill='rgba(255, 255, 255, 0.9)',
        block_border_width='1px',
        block_border_color='#e2e8f0',
        block_radius='12px',
        button_primary_background_fill='linear-gradient(135deg, #10B981, #F59E0B)',
        button_primary_text_color='white'
    )
    
    with gr.Blocks(
        css=custom_css,
        title="Cidadão.AI - Transparência Pública",
        theme=theme
    ) as app:
        
        # Landing Page (Following Mockup 1)
        with gr.Column(visible=True) as landing_page:
            gr.HTML("""
            <!-- Top Right Buttons -->
            <div class="top-right-buttons">
                <button class="top-button" onclick="alert('📜 Sobre o Cidadão.AI\\n\\nSistema de transparência pública brasileira\\nDesenvolvido para democratizar o acesso aos dados governamentais\\n\\n🔗 Portal da Transparência API\\n🤖 Inteligência Artificial\\n🇧🇷 Feito no Brasil')" title="Sobre o projeto">
                    Sobre
                </button>
                <button class="theme-toggle" onclick="toggleTheme()" title="Alternar tema">
                    🌙
                </button>
            </div>
            
            <div class="hero-section fade-in">
                <div class="hero-logo">Cidadão.AI</div>
                <div class="hero-subtitle">(breve descrição)</div>
            </div>
            
            <div class="credits-section">
                <div class="credits-text">
                    <strong>Créditos:</strong> API - Gradio - Hugging Face
                </div>
                <div class="credits-text">
                    🤖 Desenvolvido por Anderson Henrique da Silva | 🇧🇷 Feito para o Brasil
                </div>
            </div>
            
            <!-- Info Button - Bottom Right -->
            <button class="info-button" onclick="alert('ℹ️ Informações do Sistema\\n\\nCidadão.AI v2.0\\nStatus: Operacional\\n\\n📊 Portal da Transparência: Conectado\\n🤖 IA: Disponível\\n🔒 Segurança: Ativa')" title="Informações do Sistema">
                ℹ️
            </button>
            
            <script>
                // Theme toggle functionality
                function toggleTheme() {
                    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
                    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                    
                    // Apply theme to document root
                    document.documentElement.setAttribute('data-theme', newTheme);
                    document.body.setAttribute('data-theme', newTheme);
                    
                    // Update toggle icon
                    const toggles = document.querySelectorAll('.theme-toggle');
                    toggles.forEach(toggle => {
                        toggle.innerHTML = newTheme === 'light' ? '🌙' : '☀️';
                        toggle.title = newTheme === 'light' ? 'Modo escuro' : 'Modo claro';
                    });
                    
                    // Save preference
                    localStorage.setItem('theme', newTheme);
                }
                
                // Initialize theme on load
                function initTheme() {
                    const savedTheme = localStorage.getItem('theme') || 'light';
                    document.documentElement.setAttribute('data-theme', savedTheme);
                    document.body.setAttribute('data-theme', savedTheme);
                    
                    // Update toggle buttons
                    const toggles = document.querySelectorAll('.theme-toggle');
                    toggles.forEach(toggle => {
                        toggle.innerHTML = savedTheme === 'light' ? '🌙' : '☀️';
                        toggle.title = savedTheme === 'light' ? 'Modo escuro' : 'Modo claro';
                    });
                }
                
                // Initialize when ready
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', initTheme);
                } else {
                    initTheme();
                }
                setTimeout(initTheme, 100);
            </script>
            """)
            
            with gr.Row():
                search_page_btn = gr.Button(
                    "🔍 Consulta Avançada",
                    variant="primary",
                    size="lg",
                    elem_classes=["btn-modern", "btn-primary"]
                )
                chat_page_btn = gr.Button(
                    "💬 Pergunte ao Modelo",
                    variant="secondary",
                    size="lg",
                    elem_classes=["btn-modern", "btn-secondary"]
                )
        
        # Search Page (Following Mockup 2)
        with gr.Column(visible=False) as search_page:
            gr.HTML("""
            <!-- Top Right Buttons -->
            <div class="top-right-buttons">
                <button class="top-button" onclick="alert('📜 Sobre o Cidadão.AI\\n\\nSistema de transparência pública brasileira\\nDesenvolvido para democratizar o acesso aos dados governamentais\\n\\n🔗 Portal da Transparência API\\n🤖 Inteligência Artificial\\n🇧🇷 Feito no Brasil')" title="Sobre o projeto">
                    Sobre
                </button>
                <button class="theme-toggle" onclick="toggleTheme()" title="Alternar tema">
                    🌙
                </button>
            </div>
            """)
            
            with gr.Row():
                home_btn_1 = gr.Button("🏠 Voltar ao Início", variant="secondary", size="sm")
            
            gr.HTML('<div class="fade-in"><h2 style="text-align: center; margin: 2rem 0;">📊 Consulta Avançada</h2></div>')
            
            with gr.Row():
                # Left Sidebar (Menu lateral & filtros)
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div class="filter-sidebar">
                        <h3>🎛️ Menu lateral & filtros</h3>
                        <p style="color: #64748B; font-size: 0.875rem;">aparecem quando clicados</p>
                    </div>
                    """)
                    
                    data_type = gr.Radio(
                        label="Tipo de Dados",
                        choices=["Contratos Públicos", "Despesas Orçamentárias", "Licitações e Pregões"],
                        value="Contratos Públicos",
                        container=True
                    )
                    
                    year = gr.Number(
                        label="Ano",
                        value=2024,
                        minimum=2020,
                        maximum=2025,
                        precision=0
                    )
                    
                    search_term = gr.Textbox(
                        label="Termo de Busca",
                        placeholder="Digite sua consulta...",
                        lines=2
                    )
                    
                    search_btn = gr.Button(
                        "🔍 Buscar Dados",
                        variant="primary",
                        size="lg"
                    )
                
                # Right Dashboard Area
                with gr.Column(scale=2):
                    results_display = gr.HTML(
                        value="""
                        <div class="dashboard-area">
                            <h3>📊 Área do dashboard</h3>
                            <p>(na página inicial, descrição e como usar, guiado, explicando como usar)</p>
                            <p style="margin-top: 2rem; color: #64748B;">(créditos)</p>
                        </div>
                        """
                    )
        
        # Chat Page (Following Mockup 3)
        with gr.Column(visible=False) as chat_page:
            gr.HTML("""
            <!-- Top Right Buttons -->
            <div class="top-right-buttons">
                <button class="top-button" onclick="alert('📜 Sobre o Cidadão.AI\\n\\nSistema de transparência pública brasileira\\nDesenvolvido para democratizar o acesso aos dados governamentais\\n\\n🔗 Portal da Transparência API\\n🤖 Inteligência Artificial\\n🇧🇷 Feito no Brasil')" title="Sobre o projeto">
                    Sobre
                </button>
                <button class="theme-toggle" onclick="toggleTheme()" title="Alternar tema">
                    🌙
                </button>
            </div>
            """)
            
            with gr.Row():
                home_btn_2 = gr.Button("🏠 Voltar ao Início", variant="secondary", size="sm")
            
            gr.HTML('<div class="fade-in"><h2 style="text-align: center; margin: 2rem 0;">🤖 Pergunte ao Modelo</h2></div>')
            
            gr.HTML("""
            <div class="result-card">
                <h4>💡 Exemplos do que pode ser perguntado:</h4>
                <ul>
                    <li>"Quais são os maiores contratos do governo federal em 2024?"</li>
                    <li>"Como funciona o processo de licitação no Brasil?"</li>
                    <li>"Explique o Portal da Transparência"</li>
                    <li>"Quais órgãos gastam mais recursos públicos?"</li>
                </ul>
                <p style="color: #64748B; font-size: 0.875rem; margin-top: 1rem;">
                    <strong>Breve descrição:</strong> Sistema de IA para análise de dados públicos brasileiros
                </p>
            </div>
            """)
            
            # Chat interface
            chatbot = gr.Chatbot(
                height=500,
                show_label=False,
                avatar_images=("👤", "🤖"),
                show_copy_button=True,
                container=True,
                elem_classes=["chat-container"],
                type="messages"
            )
            
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Digite sua pergunta sobre transparência pública...",
                    show_label=False,
                    scale=4,
                    lines=1,
                    container=False
                )
                send_btn = gr.Button(">>", variant="primary", scale=1, size="lg")
            
            gr.HTML("""
            <div style="text-align: center; margin-top: 1rem; color: #64748B; font-size: 0.875rem;">
                <p>🔘 Botões perguntar | 🎯 Sistema alimentado por IA</p>
            </div>
            """)
        
        # Navigation Events
        search_page_btn.click(
            fn=show_search_page,
            outputs=[landing_page, search_page, chat_page]
        )
        
        chat_page_btn.click(
            fn=show_chat_page,
            outputs=[landing_page, search_page, chat_page]
        )
        
        home_btn_1.click(
            fn=show_home_page,
            outputs=[landing_page, search_page, chat_page]
        )
        
        home_btn_2.click(
            fn=show_home_page,
            outputs=[landing_page, search_page, chat_page]
        )
        
        # Connect search function
        search_btn.click(
            fn=search_transparency_data,
            inputs=[data_type, year, search_term],
            outputs=results_display
        )
        
        # Connect chat function
        msg_input.submit(
            fn=chat_function,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        send_btn.click(
            fn=chat_function,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )
    
    return app

if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI - Interface Moderna...")
    
    # Check API status
    api_status = "✅" if TRANSPARENCY_API_KEY else "❌"
    ai_status = "✅" if GROQ_API_KEY else "⚠️"
    
    print(f"📊 Portal da Transparência API: {api_status}")
    print(f"🤖 GROQ AI API: {ai_status}")
    
    app = create_interface()
    
    # Launch with modern settings
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False,
        show_api=False
    )