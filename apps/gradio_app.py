#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Compact Professional Interface
UX-optimized following Nielsen Heuristics
"""

import gradio as gr
import os
import time
import asyncio
import httpx
import json
from datetime import datetime

# Environment configuration
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_system_status():
    """Get system status for debugging"""
    status = {
        "transparency_api": "✅ Configurada" if TRANSPARENCY_API_KEY else "❌ Não configurada",
        "groq_api": "✅ Configurada" if GROQ_API_KEY else "❌ Não configurada",
        "environment": "🤗 HF Spaces" if os.getenv("SPACE_ID") else "💻 Local"
    }
    return status

# Clean, focused CSS
custom_css = """
/* Clean UX Design System */
:root {
    --primary: #0066CC;
    --secondary: #00A36C;
    --text: #1A1A1A;
    --text-light: #666666;
    --background: #FFFFFF;
    --surface: #F8F9FA;
    --border: #E5E7EB;
    --success: #10B981;
    --error: #EF4444;
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 1.5rem;
    --space-xl: 2rem;
    --radius: 0.5rem;
    --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --transition: all 0.2s ease;
}

/* Reset and Base */
.gradio-container {
    max-width: 900px !important;
    margin: 0 auto !important;
    background: var(--background) !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    padding: var(--space-lg) !important;
}

/* Hide Gradio Borders */
.gradio-container .block {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    border-radius: 0 !important;
}

/* Clean Tabs */
.tab-nav {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: var(--space-xs) !important;
    margin-bottom: var(--space-lg) !important;
}

.tab-nav button {
    border: none !important;
    background: transparent !important;
    padding: var(--space-sm) var(--space-md) !important;
    border-radius: calc(var(--radius) - 2px) !important;
    color: var(--text-light) !important;
    font-weight: 500 !important;
    transition: var(--transition) !important;
}

.tab-nav button.selected {
    background: var(--background) !important;
    color: var(--text) !important;
    box-shadow: var(--shadow) !important;
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: white;
    padding: var(--space-xl);
    border-radius: var(--radius);
    text-align: center;
    margin-bottom: var(--space-lg);
}

.hero h1 {
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0 0 var(--space-sm) 0;
}

.hero p {
    opacity: 0.9;
    margin: 0;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

/* Action Cards */
.actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-md);
    margin-bottom: var(--space-lg);
}

.action-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: var(--space-lg);
    text-align: center;
    cursor: pointer;
    transition: var(--transition);
    text-decoration: none;
    color: inherit;
}

.action-card:hover {
    box-shadow: var(--shadow);
    transform: translateY(-2px);
    border-color: var(--primary);
}

.action-card h3 {
    font-size: 1.125rem;
    font-weight: 600;
    margin: 0 0 var(--space-sm) 0;
    color: var(--text);
}

.action-card p {
    font-size: 0.875rem;
    color: var(--text-light);
    margin: 0;
}

/* Form Section */
.form-section {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: var(--space-lg);
    margin-bottom: var(--space-lg);
}

.form-section h3 {
    margin: 0 0 var(--space-md) 0;
    color: var(--text);
}

/* Modal System */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: none;
    z-index: 1000;
    align-items: center;
    justify-content: center;
}

.modal {
    background: var(--background);
    border-radius: var(--radius);
    padding: var(--space-xl);
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: var(--shadow);
    position: relative;
}

.modal h3 {
    margin: 0 0 var(--space-md) 0;
    color: var(--text);
}

.modal p {
    margin: 0 0 var(--space-sm) 0;
    color: var(--text-light);
    line-height: 1.5;
}

.modal-close {
    position: absolute;
    top: var(--space-md);
    right: var(--space-md);
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: var(--text-light);
}

/* Header */
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-lg);
    padding-bottom: var(--space-md);
    border-bottom: 1px solid var(--border);
}

.header-left, .header-right {
    display: flex;
    gap: var(--space-sm);
    align-items: center;
}

.btn-header {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: var(--space-sm) var(--space-md);
    font-size: 0.875rem;
    cursor: pointer;
    transition: var(--transition);
    color: var(--text);
}

.btn-header:hover {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
}

.theme-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
}

/* Status Button */
.status-btn {
    position: fixed;
    bottom: var(--space-lg);
    right: var(--space-lg);
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--primary);
    color: white;
    border: none;
    cursor: pointer;
    box-shadow: var(--shadow);
    z-index: 999;
    font-size: 0.875rem;
}

/* Results */
.result-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: var(--space-md);
    margin-bottom: var(--space-md);
}

.result-card.success { border-left: 4px solid var(--success); }
.result-card.error { border-left: 4px solid var(--error); }

/* Chat Examples */
.chat-examples {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: var(--space-lg);
    margin-bottom: var(--space-lg);
}

.chat-examples h4 {
    margin: 0 0 var(--space-md) 0;
    color: var(--text);
}

.chat-examples ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.chat-examples li {
    padding: var(--space-sm) 0;
    color: var(--text-light);
    font-size: 0.875rem;
    border-bottom: 1px solid var(--border);
}

.chat-examples li:last-child {
    border-bottom: none;
}

/* Responsive */
@media (max-width: 768px) {
    .actions {
        grid-template-columns: 1fr;
    }
    
    .header {
        flex-direction: column;
        gap: var(--space-md);
    }
}

/* Dark Theme */
[data-theme="dark"] {
    --text: #FFFFFF;
    --text-light: #B3B3B3;
    --background: #1A1A1A;
    --surface: #2D2D2D;
    --border: #404040;
}

/* Utility */
.hidden { display: none !important; }
.text-center { text-align: center; }
"""

# API Functions (simplified for compact interface)
async def call_transparency_api(endpoint, params):
    """Call Portal da Transparência API"""
    if not TRANSPARENCY_API_KEY:
        return {"error": "API key não configurada"}
    
    base_url = "https://api.portaldatransparencia.gov.br/api-de-dados"
    url = f"{base_url}{endpoint}"
    
    headers = {
        "chave-api-dados": TRANSPARENCY_API_KEY,
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API retornou status {response.status_code}"}
    except Exception as e:
        return {"error": f"Erro na conexão: {str(e)}"}

async def call_groq_api(message):
    """Call GROQ API for chat"""
    if not GROQ_API_KEY:
        return "⚠️ GROQ API não configurada"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {"role": "system", "content": "Você é um assistente especializado em transparência pública brasileira. Responda de forma clara e objetiva."},
            {"role": "user", "content": message}
        ],
        "model": "llama3-8b-8192",
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        async with httpx.AsyncClient(timeout=20) as client:
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
        return f"❌ Erro: {str(e)}"

def search_data(data_type, year, search_term):
    """Search transparency data"""
    endpoint_map = {
        "Contratos": "/contratos",
        "Despesas": "/despesas", 
        "Licitações": "/licitacoes"
    }
    
    endpoint = endpoint_map.get(data_type, "/contratos")
    params = {"ano": int(year), "pagina": 1, "tamanhoPagina": 10}
    
    try:
        # HF Spaces compatible async execution
        try:
            current_loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, call_transparency_api(endpoint, params))
                result = future.result(timeout=15)
        except RuntimeError:
            result = asyncio.run(call_transparency_api(endpoint, params))
        
        if "error" in result:
            return f"""
            <div class="result-card error">
                <h4>❌ Erro na consulta</h4>
                <p>{result['error']}</p>
            </div>
            """
        
        results = result if isinstance(result, list) else []
        count = len(results)
        
        if count == 0:
            return """
            <div class="result-card">
                <h4>📭 Nenhum resultado encontrado</h4>
                <p>Tente ajustar os filtros de busca.</p>
            </div>
            """
        
        # Format results
        html = f"""
        <div class="result-card success">
            <h4>✅ {count} resultados encontrados</h4>
            <p><strong>{data_type}</strong> - Ano {year}</p>
        </div>
        """
        
        for i, item in enumerate(results[:5], 1):
            valor = item.get('valor', item.get('valorContrato', 0))
            valor_fmt = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if isinstance(valor, (int, float)) else "N/A"
            
            html += f"""
            <div class="result-card">
                <h5>#{i} {item.get('nome', item.get('razaoSocial', 'N/A'))}</h5>
                <p><strong>Valor:</strong> {valor_fmt}</p>
                <p><strong>Objeto:</strong> {str(item.get('objeto', item.get('descricao', 'N/A')))[:100]}...</p>
            </div>
            """
        
        return html
        
    except Exception as e:
        return f"""
        <div class="result-card error">
            <h4>❌ Erro na busca</h4>
            <p>{str(e)}</p>
        </div>
        """

def chat_function(message, history):
    """Chat function for AI assistant"""
    if not message.strip():
        return history, ""
    
    try:
        # HF Spaces compatible async execution
        try:
            current_loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, call_groq_api(message))
                response = future.result(timeout=20)
        except RuntimeError:
            response = asyncio.run(call_groq_api(message))
        
        # Add to history
        history = history or []
        history.append((message, response))
        
        return history, ""
        
    except Exception as e:
        history = history or []
        history.append((message, f"❌ Erro: {str(e)}"))
        return history, ""

def create_interface():
    """Create the compact, professional interface"""
    
    # Clean theme
    theme = gr.themes.Soft(
        primary_hue=gr.themes.colors.blue,
        secondary_hue=gr.themes.colors.green,
        neutral_hue=gr.themes.colors.slate,
        font=[gr.themes.GoogleFont('Inter'), 'system-ui', 'sans-serif']
    )
    
    with gr.Blocks(
        css=custom_css,
        title="Cidadão.AI - Transparência Pública",
        theme=theme
    ) as app:
        
        # Header
        gr.HTML("""
        <div class="header">
            <div class="header-left">
                <button class="btn-header" onclick="showAbout()">📜 Sobre</button>
            </div>
            <div class="header-right">
                <button class="btn-header theme-btn" onclick="toggleTheme()" title="Alternar tema">🌙</button>
            </div>
        </div>
        """)
        
        # Hero Section
        gr.HTML("""
        <div class="hero">
            <h1>🏛️ Cidadão.AI</h1>
            <p>Sistema de IA para análise de transparência governamental brasileira</p>
        </div>
        """)
        
        # Main Content with Tabs
        with gr.Tabs():
            # Dashboard Tab
            with gr.Tab("🏠 Início"):
                gr.HTML("""
                <div class="actions">
                    <div class="action-card" onclick="document.querySelector('[id*=\"tab_1\"]').click()">
                        <h3>🔍 Consultar Dados</h3>
                        <p>Busque contratos, despesas e licitações públicas</p>
                    </div>
                    <div class="action-card" onclick="document.querySelector('[id*=\"tab_2\"]').click()">
                        <h3>💬 Conversar com IA</h3>
                        <p>Tire dúvidas sobre transparência pública</p>
                    </div>
                </div>
                """)
                
                # Quick stats
                status = get_system_status()
                gr.HTML(f"""
                <div class="form-section">
                    <h3>⚡ Status do Sistema</h3>
                    <p><strong>Portal da Transparência:</strong> {status['transparency_api']}</p>
                    <p><strong>IA Assistant:</strong> {status['groq_api']}</p>
                    <p><strong>Ambiente:</strong> {status['environment']}</p>
                </div>
                """)
            
            # Data Search Tab
            with gr.Tab("🔍 Consultar Dados"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML('<div class="form-section"><h3>Filtros de Busca</h3></div>')
                        
                        data_type = gr.Radio(
                            label="Tipo de Dados",
                            choices=["Contratos", "Despesas", "Licitações"],
                            value="Contratos"
                        )
                        
                        year = gr.Number(
                            label="Ano",
                            value=2024,
                            minimum=2020,
                            maximum=2025,
                            precision=0
                        )
                        
                        search_term = gr.Textbox(
                            label="Termo de Busca (opcional)",
                            placeholder="Digite um termo..."
                        )
                        
                        search_btn = gr.Button("🔍 Buscar", variant="primary")
                    
                    with gr.Column(scale=2):
                        results_display = gr.HTML("""
                        <div class="form-section">
                            <h3>📊 Resultados da Consulta</h3>
                            <p>Use os filtros ao lado para buscar dados públicos.</p>
                        </div>
                        """)
                
                # Connect search function
                search_btn.click(
                    search_data,
                    inputs=[data_type, year, search_term],
                    outputs=[results_display]
                )
            
            # Chat Tab
            with gr.Tab("💬 Chat com IA"):
                gr.HTML("""
                <div class="chat-examples">
                    <h4>💡 Exemplos de perguntas:</h4>
                    <ul>
                        <li>"Quais são os maiores contratos do governo federal em 2024?"</li>
                        <li>"Como funciona o processo de licitação no Brasil?"</li>
                        <li>"Explique o Portal da Transparência"</li>
                        <li>"Quais órgãos gastam mais recursos públicos?"</li>
                    </ul>
                </div>
                """)
                
                chatbot = gr.Chatbot(height=400)
                msg = gr.Textbox(
                    label="Sua pergunta",
                    placeholder="Digite sua pergunta sobre transparência pública...",
                    lines=2
                )
                
                msg.submit(chat_function, [msg, chatbot], [chatbot, msg])
        
        # Modals and JavaScript
        gr.HTML("""
        <!-- About Modal -->
        <div class="modal-overlay" id="aboutModal">
            <div class="modal">
                <button class="modal-close" onclick="hideModal('aboutModal')">&times;</button>
                <h3>🏛️ Sobre o Cidadão.AI</h3>
                <p><strong>Sistema de transparência pública brasileira</strong></p>
                <p>Democratizando o acesso aos dados governamentais através de inteligência artificial.</p>
                <p><strong>Recursos:</strong></p>
                <ul>
                    <li>📊 Portal da Transparência API</li>
                    <li>🤖 Assistente IA especializado</li>
                    <li>🔍 Busca inteligente de dados</li>
                    <li>📈 Análise de anomalias</li>
                </ul>
                <p><strong>Desenvolvido por:</strong> Anderson Henrique da Silva</p>
                <p><strong>Licença:</strong> Apache 2.0</p>
            </div>
        </div>
        
        <!-- Status Button -->
        <button class="status-btn" onclick="showSystemStatus()" title="Status do Sistema">ℹ️</button>
        
        <script>
            // Modal functions
            function showModal(id) {
                document.getElementById(id).style.display = 'flex';
            }
            
            function hideModal(id) {
                document.getElementById(id).style.display = 'none';
            }
            
            function showAbout() {
                showModal('aboutModal');
            }
            
            function showSystemStatus() {
                const status = `ℹ️ Status do Sistema\\n\\nCidadão.AI v2.0\\nAmbiente: """ + ("HF Spaces" if os.getenv("SPACE_ID") else "Local") + f"""\\n\\nPortal da Transparência: {status['transparency_api']}\\nIA Assistant: {status['groq_api']}\\n\\n⚙️ Configure as APIs como secrets no HF Spaces`;
                alert(status);
            }
            
            // Theme toggle
            function toggleTheme() {
                const html = document.documentElement;
                const current = html.getAttribute('data-theme') || 'light';
                const newTheme = current === 'light' ? 'dark' : 'light';
                
                html.setAttribute('data-theme', newTheme);
                
                // Update button
                const btn = document.querySelector('.theme-btn');
                btn.innerHTML = newTheme === 'light' ? '🌙' : '☀️';
                btn.title = newTheme === 'light' ? 'Modo escuro' : 'Modo claro';
                
                // Save preference
                localStorage.setItem('theme', newTheme);
            }
            
            // Initialize theme
            function initTheme() {
                const saved = localStorage.getItem('theme') || 'light';
                document.documentElement.setAttribute('data-theme', saved);
                
                const btn = document.querySelector('.theme-btn');
                if (btn) {
                    btn.innerHTML = saved === 'light' ? '🌙' : '☀️';
                    btn.title = saved === 'light' ? 'Modo escuro' : 'Modo claro';
                }
            }
            
            // Close modals on background click
            document.addEventListener('click', function(e) {
                if (e.target.classList.contains('modal-overlay')) {
                    e.target.style.display = 'none';
                }
            });
            
            // Initialize on load
            setTimeout(initTheme, 100);
        </script>
        """)
    
    return app

if __name__ == "__main__":
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False
    )