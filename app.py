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
from datetime import datetime

# Configurar variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# CSS moderno baseado nos mockups
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --primary-green: #10B981;
    --primary-yellow: #F59E0B;
    --primary-blue: #3B82F6;
    --background-light: #FFFFFF;
    --background-dark: #0F172A;
    --surface-light: #F8FAFC;
    --surface-dark: #1E293B;
    --text-primary-light: #0F172A;
    --text-primary-dark: #F1F5F9;
    --text-secondary-light: #64748B;
    --text-secondary-dark: #94A3B8;
    --border-light: #E2E8F0;
    --border-dark: #334155;
    --glass-light: rgba(255, 255, 255, 0.1);
    --glass-dark: rgba(0, 0, 0, 0.1);
    --shadow-light: 0 2px 4px rgba(0, 0, 0, 0.1);
    --shadow-dark: 0 2px 4px rgba(0, 0, 0, 0.3);
}

[data-theme="light"] {
    --bg-primary: var(--background-light);
    --bg-secondary: var(--surface-light);
    --text-primary: var(--text-primary-light);
    --text-secondary: var(--text-secondary-light);
    --border-color: var(--border-light);
    --glass-bg: var(--glass-light);
    --shadow: var(--shadow-light);
}

[data-theme="dark"] {
    --bg-primary: var(--background-dark);
    --bg-secondary: var(--surface-dark);
    --text-primary: var(--text-primary-dark);
    --text-secondary: var(--text-secondary-dark);
    --border-color: var(--border-dark);
    --glass-bg: var(--glass-dark);
    --shadow: var(--shadow-dark);
}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    transition: background-color 0.3s ease, color 0.3s ease;
}

body, .gradio-container {
    background: var(--background-light) !important;
    color: var(--text-primary-light) !important;
}

body[data-theme="dark"], .gradio-container[data-theme="dark"] {
    background: var(--background-dark) !important;
    color: var(--text-primary-dark) !important;
}

/* Header fixo baseado no mockup */
.header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 70px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
    z-index: 1000;
    box-shadow: var(--shadow);
}

.logo {
    font-size: 1.75rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.logo-text {
    background: linear-gradient(135deg, var(--primary-green), var(--primary-yellow));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.theme-toggle {
    background: transparent;
    border: 2px solid var(--border-color);
    border-radius: 30px;
    padding: 0.5rem 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
    color: var(--text-primary);
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.theme-toggle:hover {
    background: var(--primary-blue);
    color: white;
    border-color: var(--primary-blue);
}

/* Landing page baseada no mockup */
.landing-page {
    min-height: 100vh;
    background: var(--bg-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    padding-top: 100px;
}

.hero-content {
    max-width: 900px;
    text-align: center;
    position: relative;
    z-index: 2;
}

.hero-title {
    font-size: 4rem;
    font-weight: 800;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, var(--primary-green), var(--primary-yellow));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}

.hero-subtitle {
    font-size: 1.25rem;
    font-weight: 400;
    color: var(--text-secondary);
    margin-bottom: 3rem;
}

.hero-description {
    font-size: 1.125rem;
    color: var(--text-secondary);
    margin-bottom: 3rem;
    line-height: 1.7;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.action-buttons {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 3rem;
}

.btn {
    padding: 1rem 2rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    min-width: 180px;
    justify-content: center;
}

.btn-primary {
    background: var(--primary-blue);
    color: white;
}

.btn-primary:hover {
    background: #2563EB;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
    background: transparent;
    color: var(--text-primary);
    border: 2px solid var(--border-color);
}

.btn-secondary:hover {
    background: var(--bg-secondary);
    border-color: var(--primary-blue);
}

/* Logo dinâmico simples */
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.logo-text {
    animation: pulse 3s ease-in-out infinite;
}

/* Filtros laterais */
.filter-sidebar {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    height: fit-content;
    position: sticky;
    top: 90px;
}

.filter-group {
    margin-bottom: 1.5rem;
}

.filter-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
    display: block;
}

/* Tabs personalizadas */
.tab-nav {
    background: var(--bg-secondary);
    border-radius: 20px;
    padding: 0.5rem;
    margin-bottom: 2rem;
    border: 1px solid var(--border-color);
}

/* Componentes Gradio */
.gr-button {
    background: var(--primary-blue) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.gr-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0, 82, 204, 0.3) !important;
}

.gr-form {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 15px !important;
    padding: 2rem !important;
}

.gr-textbox, .gr-number, .gr-radio {
    border-radius: 10px !important;
    border: 1px solid var(--border-color) !important;
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* Responsivo aprimorado */
@media (max-width: 768px) {
    .header {
        padding: 0 1rem;
    }
    
    .landing-page {
        padding: 1rem;
        padding-top: 80px;
    }
    
    .action-buttons {
        flex-direction: column;
        align-items: center;
    }
    
    .btn {
        width: 100%;
        max-width: 280px;
    }
    
    .stats-section {
        grid-template-columns: 1fr;
    }
    
    .footer-links {
        flex-direction: column;
        gap: 1rem;
    }
}

/* Animações */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.hero-content > * {
    animation: fadeInUp 0.6s ease forwards;
}

.hero-title { animation-delay: 0.1s; }
.hero-subtitle { animation-delay: 0.2s; }
.hero-description { animation-delay: 0.3s; }
.action-buttons { animation-delay: 0.4s; }
.stats-section { animation-delay: 0.5s; }
"""

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
        """
    
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
            """
        
        # Processar resultados
        results = api_result if isinstance(api_result, list) else []
        
        if not results:
            return """
            <div style="padding: 2rem; text-align: center;">
                <h3>Nenhum resultado encontrado</h3>
                <p style="color: var(--text-secondary);">Tente ajustar os filtros ou termo de busca</p>
            </div>
            """
        
    except Exception as e:
        return f"""
        <div style="padding: 2rem; text-align: center; color: #DC2626;">
            <h3>Erro na busca</h3>
            <p>{str(e)}</p>
        </div>
        """
    
    # Header simples
    html = f"""
    <div style="padding: 1.5rem;">
        <h3 style="margin-bottom: 1.5rem;">Resultados da busca</h3>
        <p style="color: var(--text-secondary); margin-bottom: 2rem;">Busca por: "{search_term}" - {data_type} ({year})</p>
        <p style="color: var(--text-secondary); margin-bottom: 2rem;">Encontrados: {len(results)} registros</p>
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
        <div style="border: 1px solid var(--border-color); border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
            <h4 style="color: var(--primary-blue); margin: 0 0 0.5rem 0;">{data_type} #{numero}</h4>
            <p><strong>Empresa/Favorecido:</strong> {empresa}</p>
            <p><strong>Valor:</strong> {valor_fmt}</p>
            <p><strong>Objeto:</strong> {objeto[:100]}{'...' if len(str(objeto)) > 100 else ''}</p>
            <details style="margin-top: 0.5rem;">
                <summary style="cursor: pointer; color: var(--primary-blue);">Ver dados completos</summary>
                <pre style="background: var(--bg-secondary); padding: 1rem; border-radius: 4px; overflow-x: auto; font-size: 0.8rem;">{json.dumps(item, indent=2, ensure_ascii=False)}</pre>
            </details>
        </div>
        """
    
    html += """
    </div>
    """
    
    return html

def create_landing_page():
    """Landing page baseada no mockup 1"""
    return """
    <script>
        // Theme toggle functionality
        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            // Apply theme to document root
            document.documentElement.setAttribute('data-theme', newTheme);
            
            // Apply theme to body and gradio container
            document.body.setAttribute('data-theme', newTheme);
            const gradioContainer = document.querySelector('.gradio-container');
            if (gradioContainer) {
                gradioContainer.setAttribute('data-theme', newTheme);
            }
            
            // Save theme preference
            localStorage.setItem('theme', newTheme);
            
            // Update toggle text
            const toggles = document.querySelectorAll('.theme-toggle');
            toggles.forEach(toggle => {
                toggle.innerHTML = newTheme === 'light' ? '<span>🌙</span> Modo Escuro' : '<span>☀️</span> Modo Claro';
            });
        }
        
        // Set initial theme
        function initTheme() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            
            // Apply to all relevant elements
            document.documentElement.setAttribute('data-theme', savedTheme);
            document.body.setAttribute('data-theme', savedTheme);
            
            const gradioContainer = document.querySelector('.gradio-container');
            if (gradioContainer) {
                gradioContainer.setAttribute('data-theme', savedTheme);
            }
            
            // Update toggle buttons
            const toggles = document.querySelectorAll('.theme-toggle');
            toggles.forEach(toggle => {
                toggle.innerHTML = savedTheme === 'light' ? '<span>🌙</span> Modo Escuro' : '<span>☀️</span> Modo Claro';
                toggle.addEventListener('click', toggleTheme);
            });
        }
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initTheme);
        } else {
            initTheme();
        }
        
        // Also try to initialize after a short delay for Gradio
        setTimeout(initTheme, 100);
        setTimeout(initTheme, 500);
    </script>
    
    <div class="header">
        <div class="logo">
            <span style="font-size: 2rem;">🇧🇷</span>
            <span class="logo-text">Cidadão.AI</span>
        </div>
        <button class="theme-toggle" onclick="toggleTheme()">
            <span>🌙</span> Modo Escuro
        </button>
    </div>
    
    <div class="landing-page">
        <div class="hero-content">
            <h1 class="hero-title">Cidadão.AI</h1>
            <p class="hero-subtitle">
                (breve descrição)
            </p>
            
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="document.querySelector('.gradio-container .tabs button:nth-child(2)').click()">
                    Consulta Avançada
                </button>
                <button class="btn btn-secondary" onclick="document.querySelector('.gradio-container .tabs button:nth-child(3)').click()">
                    Pergunte ao Modelo
                </button>
            </div>
            
            <div style="margin-top: 3rem; text-align: center; color: var(--text-secondary);">
                <p style="font-size: 0.875rem;">OBS: Botões 1 & 2 idênticos ao Landing Page</p>
            </div>
            
            <div style="margin-top: 3rem; text-align: center; color: var(--text-secondary); font-size: 0.875rem;">
                <p style="margin-bottom: 1rem;">(Créditos: API - gradio - hugging face)</p>
            </div>
        </div>
    </div>
    """

def create_interface():
    """Interface principal"""
    
    with gr.Blocks(css=custom_css, title="Cidadão.AI") as app:
        
        # Landing page como primeira aba
        with gr.Tab("🏠 Cidadão.AI"):
            gr.HTML(create_landing_page())
        
        # Aba de consulta avançada
        with gr.Tab("🔍 Consulta Avançada"):
            gr.HTML("""
                <div class="header">
                    <div class="logo">
                        <span style="font-size: 2rem;">🇧🇷</span>
                        <span class="logo-text">Cidadão.AI</span>
                    </div>
                    <button class="theme-toggle" onclick="toggleTheme()">
                        <span>🌙</span> Modo Escuro
                    </button>
                </div>
                <div style="padding-top: 100px;">
                    <h2 style="text-align: center; margin-bottom: 2rem;">Página: consulta avançada</h2>
                </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-color);">
                        <h3 style="margin-bottom: 1.5rem;">Menu lateral & filtros</h3>
                        <p style="color: var(--text-secondary);">apareceu quando clicados</p>
                    </div>
                    """)
                    
                    data_type = gr.Radio(
                        label="Tipo de Dados",
                        choices=["Contratos Públicos", "Despesas Orçamentárias", "Licitações e Pregões"],
                        value="Contratos Públicos"
                    )
                    
                    year = gr.Number(
                        label="Ano",
                        value=2024,
                        minimum=2000,
                        maximum=2024
                    )
                    
                    search_term = gr.Textbox(
                        label="Busca",
                        placeholder="Digite sua consulta...",
                        lines=2
                    )
                    
                    search_btn = gr.Button(
                        "Buscar", 
                        variant="primary"
                    )
                
                with gr.Column(scale=2):
                    results = gr.HTML(
                        value="""
                        <div style="background: var(--bg-secondary); padding: 2rem; border-radius: 12px; border: 1px solid var(--border-color); min-height: 400px;">
                            <h3 style="margin-bottom: 1.5rem;">Área do dashboard</h3>
                            <p style="color: var(--text-secondary);">(na página inicial, descrição e como usar, guiado, explicando como usar)</p>
                            <p style="color: var(--text-secondary); margin-top: 1rem;">(créditos)</p>
                        </div>
                        """
                    )
            
            search_btn.click(
                fn=search_data,
                inputs=[data_type, year, search_term],
                outputs=results
            )
        
        # Aba de perguntas ao modelo
        with gr.Tab("💬 Pergunte ao Modelo"):
            gr.HTML("""
                <div class="header">
                    <div class="logo">
                        <span style="font-size: 2rem;">🇧🇷</span>
                        <span class="logo-text">Cidadão.AI</span>
                    </div>
                    <button class="theme-toggle" onclick="toggleTheme()">
                        <span>🌙</span> Modo Escuro
                    </button>
                </div>
                <div style="padding-top: 100px; text-align: center;">
                    <h2 style="margin-bottom: 2rem;">Pergunte ao Modelo:</h2>
                </div>
            """)
            
            chatbot = gr.Chatbot(
                height=400,
                show_label=False,
                bubble_full_width=False,
                avatar_images=("👤", "🤖")
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="exemplos do que pode ser perguntado - breve descrição de como funciona",
                    show_label=False,
                    scale=4,
                    lines=1,
                    elem_id="chat-input"
                )
                send_btn = gr.Button(">", variant="primary", scale=1)
            
            gr.HTML("""
                <div style="margin-top: 1rem; text-align: center; color: var(--text-secondary); font-size: 0.875rem;">
                    <p>Botões perguntar</p>
                </div>
            """)
            
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
            
            def chat_fn(message, history):
                if message:
                    history = history or []
                    
                    # Chamar API do GROQ
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        response = loop.run_until_complete(call_groq_api(message))
                        loop.close()
                    except Exception as e:
                        response = f"Erro ao processar mensagem: {str(e)}"
                    
                    history.append((message, response))
                    return history, ""
                return history, ""
            
            msg.submit(
                fn=chat_fn,
                inputs=[msg, chatbot], 
                outputs=[chatbot, msg]
            )
            
            send_btn.click(
                fn=chat_fn,
                inputs=[msg, chatbot], 
                outputs=[chatbot, msg]
            )
    
    return app

# Executar aplicação
if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI...")
    app = create_interface()
    app.launch()