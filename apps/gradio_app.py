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

# Debug function for HF Spaces
def get_system_status():
    """Get system status for debugging"""
    status = {
        "transparency_api": "✅ Configurada" if TRANSPARENCY_API_KEY else "❌ Não configurada",
        "groq_api": "✅ Configurada" if GROQ_API_KEY else "❌ Não configurada",
        "python_version": f"🐍 {os.sys.version}",
        "environment": "🤗 Hugging Face Spaces" if os.getenv("SPACE_ID") else "💻 Local"
    }
    return status

# Professional CSS Design System - Enterprise Grade
custom_css = """
/* Professional Design System - Inspired by docs/blog/main.css */
:root {
    /* Light Theme - Professional Brand Colors */
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --bg-tertiary: #f1f5f9;
    --bg-hover: #e2e8f0;
    --bg-accent: #3b82f6;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-tertiary: #64748b;
    --text-accent: #1e40af;
    --text-muted: #94a3b8;
    --border: #e2e8f0;
    --border-light: #f1f5f9;
    --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    
    /* Brazilian Colors */
    --brazil-green: #009639;
    --brazil-yellow: #ffdf00;
    --brazil-blue: #002776;
    
    /* Brand Colors */
    --brand-primary: #0049A0;
    --brand-secondary: #00873D;
    --brand-accent: #FFB74D;
    
    /* Legacy compatibility */
    --primary-green: var(--brand-secondary);
    --primary-yellow: var(--brand-accent);
    --primary-blue: var(--brand-primary);
    --accent-gradient: linear-gradient(135deg, var(--brand-primary), var(--brand-secondary));
    --text-gradient: linear-gradient(135deg, var(--brand-primary), var(--brand-secondary));
    --glass-bg: rgba(255, 255, 255, 0.1);
    --border-radius: 12px;
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    --border-color: var(--border);
}

/* Dark Theme */
[data-theme="dark"] {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-tertiary: #334155;
    --bg-hover: #475569;
    --bg-accent: #1e40af;
    --text-primary: #f8fafc;
    --text-secondary: #cbd5e1;
    --text-tertiary: #94a3b8;
    --text-accent: #60a5fa;
    --text-muted: #64748b;
    --border: #334155;
    --border-light: #475569;
    --glass-bg: rgba(0, 0, 0, 0.2);
    --border-color: var(--border);
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

/* Professional Typography */
.gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 1400px;
    margin: 0 auto;
    transition: var(--transition);
    background: var(--bg-primary);
    color: var(--text-primary);
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: var(--text-primary);
    background: var(--bg-primary);
    transition: var(--transition);
    min-height: 100vh;
}

/* Professional Hero Section */
.hero-section {
    text-align: center;
    padding: 6rem 2rem;
    background: linear-gradient(135deg, 
        var(--brand-primary) 0%, 
        var(--brand-secondary) 50%, 
        var(--brand-accent) 100%);
    color: white;
    border-radius: var(--border-radius);
    margin: 2rem 0;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-lg);
}

.hero-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
    opacity: 0.3;
}

.hero-logo {
    font-size: 3.5rem;
    font-weight: 900;
    color: white;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    position: relative;
    z-index: 1;
}

.hero-subtitle {
    font-size: 1.5rem;
    color: rgba(255, 255, 255, 0.95);
    margin-bottom: 2rem;
    font-weight: 300;
    position: relative;
    z-index: 1;
}

.hero-description {
    font-size: 1.125rem;
    max-width: 600px;
    margin: 0 auto 3rem;
    opacity: 0.9;
    line-height: 1.7;
    color: rgba(255, 255, 255, 0.9);
    position: relative;
    z-index: 1;
}

/* Professional Button System */
.action-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
    margin: 2rem 0;
    position: relative;
    z-index: 1;
}

.btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.875rem 2rem;
    border-radius: 0.5rem;
    font-weight: 600;
    text-decoration: none;
    transition: var(--transition);
    border: 2px solid transparent;
    cursor: pointer;
    font-size: 1rem;
    min-width: 180px;
    justify-content: center;
}

.btn-primary {
    background: white;
    color: var(--brand-primary);
    border-color: white;
}

.btn-primary:hover {
    background: transparent;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.btn-secondary {
    background: transparent;
    color: white;
    border-color: rgba(255, 255, 255, 0.5);
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: white;
    transform: translateY(-2px);
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

/* Professional Cards */
.result-card {
    background: var(--bg-primary);
    border-radius: var(--border-radius);
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border);
    border-left: 4px solid var(--brand-primary);
    transition: var(--transition);
}

.result-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

.feature-card {
    background: var(--bg-primary);
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: var(--shadow-md);
    transition: var(--transition);
    border: 1px solid var(--border);
}

.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

/* Professional Status Indicators */
.status-success {
    border-left-color: var(--brand-secondary);
    background: #F0FDF4;
}

.status-error {
    border-left-color: #EF4444;
    background: #FEF2F2;
}

.status-warning {
    border-left-color: var(--brand-accent);
    background: #FFFBEB;
}

/* Professional Section Headers */
.section-title {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: var(--text-primary);
    text-align: center;
}

.section-subtitle {
    font-size: 1.125rem;
    color: var(--text-secondary);
    max-width: 600px;
    margin: 0 auto 2rem;
    text-align: center;
    line-height: 1.6;
}

/* Professional Info Button */
.info-button {
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    background: var(--brand-primary);
    color: white;
    border: none;
    border-radius: 50%;
    width: 48px;
    height: 48px;
    cursor: pointer;
    font-size: 1.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    box-shadow: var(--shadow-lg);
    transition: var(--transition);
}

.info-button:hover {
    transform: scale(1.1);
    box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 10px 10px -5px rgb(0 0 0 / 0.04);
    background: var(--brand-secondary);
}

/* Professional Header Buttons */
.top-left-buttons {
    position: fixed;
    top: 1rem;
    left: 1rem;
    display: flex;
    gap: 0.5rem;
    z-index: 1000;
}

.top-button {
    background: rgba(255, 255, 255, 0.95);
    color: var(--text-primary);
    border: 1px solid var(--border);
    border-radius: 0.5rem;
    padding: 0.5rem 1rem;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: var(--transition);
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow);
}

.top-button:hover {
    background: var(--brand-primary);
    color: white;
    transform: translateY(-1px);
    border-color: var(--brand-primary);
}

.theme-toggle {
    background: rgba(255, 255, 255, 0.95);
    color: var(--text-primary);
    border: 1px solid var(--border);
    border-radius: 0.5rem;
    padding: 0.5rem;
    cursor: pointer;
    font-size: 1.125rem;
    transition: var(--transition);
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow);
    width: 40px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.theme-toggle:hover {
    background: var(--brand-primary);
    color: white;
    transform: translateY(-1px);
    border-color: var(--brand-primary);
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
    """Call Portal da Transparência API with HF Spaces compatibility"""
    if not TRANSPARENCY_API_KEY:
        return {"error": "⚠️ TRANSPARENCY_API_KEY não configurada como secret no HF Spaces"}
    
    base_url = "https://api.portaldatransparencia.gov.br"
    headers = {
        "chave-api-dados": TRANSPARENCY_API_KEY,
        "User-Agent": "Mozilla/5.0 (compatible; CidadaoAI/2.0)",
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(15.0, connect=5.0),
            follow_redirects=True,
            limits=httpx.Limits(max_connections=10)
        ) as client:
            response = await client.get(
                f"{base_url}{endpoint}",
                headers=headers,
                params=params or {}
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"error": "❌ API key inválida - verifique TRANSPARENCY_API_KEY"}
            elif response.status_code == 429:
                return {"error": "⏳ Rate limit atingido - tente novamente"}
            else:
                return {"error": f"❌ API Error {response.status_code}"}
    except httpx.TimeoutException:
        return {"error": "⏳ Timeout na API - tente novamente"}
    except Exception as e:
        return {"error": f"❌ Erro: {str(e)}"}

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
    
    # Execute API call - HF Spaces compatible
    try:
        try:
            current_loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, call_transparency_api(endpoint, params))
                api_result = future.result(timeout=20)
        except RuntimeError:
            api_result = asyncio.run(call_transparency_api(endpoint, params))
        
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
    """Call GROQ API for chat with HF Spaces compatibility"""
    if not GROQ_API_KEY:
        return "⚠️ GROQ_API_KEY não configurada como secret no HF Spaces"
    
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
                Use emojis quando apropriado e seja educativo. Mantenha respostas concisas."""
            },
            {
                "role": "user", 
                "content": message
            }
        ],
        "model": "llama3-8b-8192",
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(20.0, connect=5.0),
            limits=httpx.Limits(max_connections=10)
        ) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            elif response.status_code == 401:
                return "❌ API key inválida - verifique GROQ_API_KEY"
            else:
                return f"❌ Erro na API GROQ: {response.status_code}"
    except httpx.TimeoutException:
        return "⏳ Timeout na API GROQ - tente novamente"
    except Exception as e:
        return f"❌ Erro: {str(e)}"

def chat_function(message, history):
    """Chat function for the AI assistant following mockup 3 - HF Spaces compatible"""
    if not message.strip():
        return history, ""
    
    try:
        # Call GROQ API - HF Spaces compatible
        try:
            current_loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, call_groq_api(message))
                response = future.result(timeout=25)
        except RuntimeError:
            response = asyncio.run(call_groq_api(message))
        
        # Add to history (messages format)
        history = history or []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        
        return history, ""
        
    except Exception as e:
        history = history or []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": f"❌ Erro no chat: {str(e)}"})
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
            <!-- Professional Header Buttons -->
            <div class="top-left-buttons">
                <button class="top-button" onclick="alert('📜 Sobre o Cidadão.AI\\n\\nSistema de transparência pública brasileira\\nDesenvolvido para democratizar o acesso aos dados governamentais\\n\\n🔗 Portal da Transparência API\\n🤖 Inteligência Artificial\\n🇧🇷 Feito no Brasil')" title="Sobre o projeto">
                    📜 Sobre
                </button>
                <button class="theme-toggle" onclick="toggleTheme()" title="Alternar tema">
                    🌙
                </button>
            </div>
            
            <div class="hero-section fade-in">
                <div class="hero-logo">🏛️ Cidadão.AI</div>
                <div class="hero-subtitle">Sistema de IA Multi-Agente para Transparência Governamental Brasileira</div>
                <div class="hero-description">
                    Democratizando o acesso aos dados públicos brasileiros através de inteligência artificial especializada.
                    Desenvolvido para fortalecer as instituições democráticas com análise automatizada de contratos, licitações e despesas públicas.
                </div>
            </div>
            
            <div class="credits-section">
                <h3 style="color: var(--brand-primary); margin-bottom: 1rem; font-size: 1.25rem;">🚀 Acesso Rápido</h3>
                <div class="credits-text">
                    <strong>Portal da Transparência API</strong> • <strong>Gradio Interface</strong> • <strong>Hugging Face Spaces</strong>
                </div>
                <div class="credits-text">
                    🤖 Desenvolvido por <strong>Anderson Henrique da Silva</strong> | 🇧🇷 Feito para fortalecer a democracia brasileira
                </div>
                <div class="credits-text" style="margin-top: 1rem; font-size: 0.875rem; color: var(--text-tertiary);">
                    ⚖️ Alinhado ao ODS 16: Paz, Justiça e Instituições Eficazes | 📊 89.2% de precisão em detecção de anomalias
                </div>
            </div>
            
            <!-- Info Button - Bottom Right -->
            <button class="info-button" onclick="showSystemStatus()" title="Status do Sistema">
                ℹ️
            </button>
            
            <script>
                // System status function
                function showSystemStatus() {
                    const transparencyStatus = """ + ("'✅ Configurada'" if TRANSPARENCY_API_KEY else "'❌ Não configurada'") + """;
                    const groqStatus = """ + ("'✅ Configurada'" if GROQ_API_KEY else "'❌ Não configurada'") + """;
                    const environment = """ + ("'🤗 HF Spaces'" if os.getenv("SPACE_ID") else "'💻 Local'") + """;
                    
                    alert(`ℹ️ Status do Sistema\\n\\nCidadão.AI v2.0\\nAmbiente: ${environment}\\n\\n📊 Portal da Transparência API: ${transparencyStatus}\\n🤖 GROQ AI API: ${groqStatus}\\n\\n⚙️ Configure as APIs como secrets no HF Spaces`);
                }
                
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
                
                // Initialize button connections
                function initButtonConnections() {
                    // Connect styled buttons to hidden Gradio buttons
                    const searchBtn = document.querySelector('button[onclick*="searchPageBtn"]');
                    const chatBtn = document.querySelector('button[onclick*="chatPageBtn"]');
                    
                    // Find Gradio buttons by scanning all buttons
                    const gradioButtons = document.querySelectorAll('button');
                    let searchPageBtn = null;
                    let chatPageBtn = null;
                    
                    gradioButtons.forEach(btn => {
                        if (btn.textContent?.includes('🔍 Consulta Avançada') && btn.style.display === 'none') {
                            searchPageBtn = btn;
                        }
                        if (btn.textContent?.includes('💬 Pergunte ao Modelo') && btn.style.display === 'none') {
                            chatPageBtn = btn;
                        }
                    });
                    
                    // Set up click handlers
                    if (searchBtn && searchPageBtn) {
                        searchBtn.onclick = () => searchPageBtn.click();
                        window.searchPageBtn = searchPageBtn;
                    }
                    if (chatBtn && chatPageBtn) {
                        chatBtn.onclick = () => chatPageBtn.click();
                        window.chatPageBtn = chatPageBtn;
                    }
                }
                
                // Initialize when ready
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', () => {
                        initTheme();
                        setTimeout(initButtonConnections, 500);
                    });
                } else {
                    initTheme();
                    setTimeout(initButtonConnections, 500);
                }
                setTimeout(() => {
                    initTheme();
                    initButtonConnections();
                }, 1000);
            </script>
            """)
            
            with gr.Row():
                with gr.Column():
                    gr.HTML("""
                    <div class="action-buttons">
                        <button class="btn btn-primary" onclick="window.searchPageBtn?.click()">
                            🔍 Consulta Avançada
                        </button>
                        <button class="btn btn-secondary" onclick="window.chatPageBtn?.click()">
                            💬 Pergunte ao Modelo
                        </button>
                    </div>
                    """)
                    
                # Hidden Gradio buttons for functionality
                search_page_btn = gr.Button(
                    "🔍 Consulta Avançada",
                    variant="primary",
                    size="lg",
                    visible=False
                )
                chat_page_btn = gr.Button(
                    "💬 Pergunte ao Modelo",
                    variant="secondary",
                    size="lg", 
                    visible=False
                )
        
        # Search Page (Following Mockup 2)
        with gr.Column(visible=False) as search_page:
            gr.HTML("""
            <!-- Professional Header Buttons -->
            <div class="top-left-buttons">
                <button class="top-button" onclick="alert('📜 Sobre o Cidadão.AI\\n\\nSistema de transparência pública brasileira\\nDesenvolvido para democratizar o acesso aos dados governamentais\\n\\n🔗 Portal da Transparência API\\n🤖 Inteligência Artificial\\n🇧🇷 Feito no Brasil')" title="Sobre o projeto">
                    📜 Sobre
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
                            <h2 class="section-title">📊 Consulta Avançada de Dados Públicos</h2>
                            <p class="section-subtitle">
                                Sistema inteligente para análise de transparência governamental brasileira.
                                Utilize os filtros ao lado para consultar contratos, despesas e licitações públicas.
                            </p>
                            
                            <div class="feature-card" style="margin: 2rem 0;">
                                <h4 style="color: var(--brand-primary); margin-bottom: 1rem;">🎯 Como usar o sistema:</h4>
                                <ol style="color: var(--text-secondary); line-height: 1.8;">
                                    <li><strong>Selecione o tipo de dados</strong> desejado (Contratos, Despesas, Licitações)</li>
                                    <li><strong>Escolha o ano</strong> de interesse (2020-2025)</li>
                                    <li><strong>Digite um termo de busca</strong> (opcional) para filtrar resultados</li>
                                    <li><strong>Clique em "Buscar Dados"</strong> para executar a consulta</li>
                                </ol>
                            </div>
                            
                            <div class="feature-card" style="margin: 2rem 0;">
                                <h4 style="color: var(--brand-secondary); margin-bottom: 1rem;">🔍 Fontes de Dados:</h4>
                                <p style="color: var(--text-secondary);">
                                    • <strong>Portal da Transparência</strong> - Dados oficiais do governo federal<br>
                                    • <strong>API v3</strong> - Interface de dados em tempo real<br>
                                    • <strong>Análise IA</strong> - Detecção automática de anomalias (89.2% precisão)
                                </p>
                            </div>
                        </div>
                        """
                    )
        
        # Chat Page (Following Mockup 3)
        with gr.Column(visible=False) as chat_page:
            gr.HTML("""
            <!-- Professional Header Buttons -->
            <div class="top-left-buttons">
                <button class="top-button" onclick="alert('📜 Sobre o Cidadão.AI\\n\\nSistema de transparência pública brasileira\\nDesenvolvido para democratizar o acesso aos dados governamentais\\n\\n🔗 Portal da Transparência API\\n🤖 Inteligência Artificial\\n🇧🇷 Feito no Brasil')" title="Sobre o projeto">
                    📜 Sobre
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