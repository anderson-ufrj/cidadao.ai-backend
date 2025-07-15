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
    --primary-green: #00A86B;
    --primary-yellow: #F59E0B;
    --primary-blue: #0066CC;
    --primary-navy: #003366;
    --primary-light-blue: #4DA6FF;
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
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.gradio-container {
    transition: background-color 0.3s ease, color 0.3s ease;
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

.theme-toggle:hover, .credits-button:hover {
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
    padding: 1.2rem 2.5rem;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    min-width: 200px;
    justify-content: center;
    position: relative;
    overflow: hidden;
}

.btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s ease;
}

.btn:hover::before {
    left: 100%;
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary-blue), var(--primary-light-blue));
    color: white;
    box-shadow: 0 4px 15px rgba(0, 102, 204, 0.3);
}

.btn-primary:hover {
    background: linear-gradient(135deg, var(--primary-navy), var(--primary-blue));
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 102, 204, 0.4);
}

.btn-secondary {
    background: linear-gradient(135deg, var(--primary-green), #00D084);
    color: white;
    box-shadow: 0 4px 15px rgba(0, 168, 107, 0.3);
}

.btn-secondary:hover {
    background: linear-gradient(135deg, #008A5A, var(--primary-green));
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 168, 107, 0.4);
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

/* Forçar tema escuro nos componentes */
[data-theme="dark"] .gr-textbox,
[data-theme="dark"] .gr-number,
[data-theme="dark"] .gr-radio {
    background: var(--surface-dark) !important;
    color: var(--text-primary-dark) !important;
    border-color: var(--border-dark) !important;
}

[data-theme="dark"] .gr-form {
    background: var(--surface-dark) !important;
    border-color: var(--border-dark) !important;
}

/* CSS alternativo para modo escuro */
.dark-mode {
    background: #0F172A !important;
    color: #F1F5F9 !important;
}

.dark-mode .header {
    background: #1E293B !important;
    border-color: #334155 !important;
}

.dark-mode .landing-page {
    background: #0F172A !important;
}

.dark-mode .theme-toggle {
    color: #F1F5F9 !important;
    border-color: #334155 !important;
}

/* Ocultar loading do Gradio */
.gradio-container .wrap.default,
.gradio-container .loading,
.gradio-container .eta-bar,
.gradio-container .progress-bar,
.gradio-container .uploading,
.gradio-container .pending {
    display: none !important;
    opacity: 0 !important;
    visibility: hidden !important;
}

/* Ocultar logo do Gradio durante loading */
.gradio-container .logo:not(.header .logo),
.gradio-container svg[alt="logo"],
.gradio-container img[alt="logo"] {
    display: none !important;
    opacity: 0 !important;
    visibility: hidden !important;
}

/* Ocultar splash screen e loading inicial */
.gradio-container > div:first-child:not(.tab-nav):not(.tabitem) {
    display: none !important;
}

/* Ocultar qualquer div que contenha apenas o logo */
.gradio-container > div:empty,
.gradio-container > div:has(> svg),
.gradio-container > div:has(> img[alt="logo"]) {
    display: none !important;
}

/* Forçar exibição do conteúdo principal */
.gradio-container .tab-nav,
.gradio-container .tabitem,
.gradio-container .block {
    display: block !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Acelerar carregamento */
.gradio-container {
    opacity: 1 !important;
    visibility: visible !important;
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

/* Botão de ajuda flutuante */
.help-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 65px;
    height: 65px;
    background: linear-gradient(135deg, var(--primary-blue), var(--primary-light-blue));
    border: none;
    border-radius: 50%;
    color: white;
    font-size: 2rem;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0, 102, 204, 0.3);
    z-index: 1000;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.help-button:hover {
    transform: scale(1.1);
    box-shadow: 0 8px 25px rgba(0, 102, 204, 0.4);
    background: linear-gradient(135deg, var(--primary-navy), var(--primary-blue));
}

.help-button:active {
    transform: scale(0.95);
}

/* Modal de ajuda em formato de balão */
.help-modal {
    position: fixed;
    bottom: 95px;
    right: 20px;
    width: 400px;
    max-height: 550px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 15px;
    box-shadow: var(--shadow-xl);
    z-index: 1001;
    opacity: 0;
    transform: translateY(20px) scale(0.9);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: none;
    overflow: hidden;
    display: none;
}

.help-modal.open {
    opacity: 1;
    transform: translateY(0) scale(1);
    pointer-events: all;
    display: block;
}

/* Seta do balão */
.help-modal::after {
    content: '';
    position: absolute;
    bottom: -10px;
    right: 32px;
    width: 20px;
    height: 20px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-top: none;
    border-left: none;
    transform: rotate(45deg);
    z-index: -1;
}

.help-modal-header {
    background: linear-gradient(135deg, var(--primary-blue), var(--primary-light-blue));
    color: white;
    padding: 15px 20px;
    border-radius: 15px 15px 0 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.help-modal-header h3 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
}

.help-modal-close {
    background: none;
    border: none;
    color: white;
    font-size: 1.2rem;
    cursor: pointer;
    margin-left: auto;
    padding: 5px;
    border-radius: 50%;
    width: 25px;
    height: 25px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.help-modal-close:hover {
    background: rgba(255, 255, 255, 0.2);
}

.help-modal-content {
    padding: 20px;
    max-height: 400px;
    overflow-y: auto;
}

.help-section {
    margin-bottom: 20px;
}

.help-section h4 {
    color: var(--text-primary);
    margin-bottom: 10px;
    font-size: 1rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
}

.help-info {
    background: var(--bg-secondary);
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
}

.help-info p {
    margin: 5px 0;
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.help-info strong {
    color: var(--text-primary);
}

.help-links {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}

.help-link {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 6px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    color: var(--primary-blue);
    text-decoration: none;
    font-size: 0.85rem;
    transition: all 0.2s ease;
}

.help-link:hover {
    background: var(--primary-blue);
    color: white;
    transform: translateY(-1px);
}

@media (max-width: 768px) {
    .help-button {
        width: 55px;
        height: 55px;
        bottom: 15px;
        right: 15px;
        font-size: 1.5rem;
    }
    
    .help-modal {
        bottom: 80px;
        right: 15px;
        width: 350px;
    }
}
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
            console.log('Toggle theme called');
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            console.log('Switching from', currentTheme, 'to', newTheme);
            
            // Apply theme to document root
            document.documentElement.setAttribute('data-theme', newTheme);
            document.body.setAttribute('data-theme', newTheme);
            
            // Apply to all containers
            const containers = document.querySelectorAll('.gradio-container, .header, .landing-page');
            containers.forEach(container => {
                container.setAttribute('data-theme', newTheme);
            });
            
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
            console.log('Init theme called');
            const savedTheme = localStorage.getItem('theme') || 'light';
            console.log('Saved theme:', savedTheme);
            
            // Apply to all relevant elements
            document.documentElement.setAttribute('data-theme', savedTheme);
            document.body.setAttribute('data-theme', savedTheme);
            
            // Apply to all containers
            const containers = document.querySelectorAll('.gradio-container, .header, .landing-page');
            containers.forEach(container => {
                container.setAttribute('data-theme', savedTheme);
            });
            
            // Update toggle buttons
            const toggles = document.querySelectorAll('.theme-toggle');
            console.log('Found toggles:', toggles.length);
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
        setTimeout(initTheme, 1000);
        setTimeout(initTheme, 2000);
        
        // Force hide Gradio loading elements
        function hideGradioLoading() {
            const loadingElements = document.querySelectorAll('.loading, .eta-bar, .wrap.default');
            loadingElements.forEach(el => {
                el.style.display = 'none';
            });
            
            // Hide any Gradio logos or loading screens
            const gradioLogos = document.querySelectorAll('.gradio-container .logo, .gradio-container > div:first-child');
            gradioLogos.forEach(el => {
                if (el.tagName !== 'DIV' || !el.classList.contains('header')) {
                    el.style.display = 'none';
                }
            });
        }
        
        // Run multiple times to ensure it works
        setTimeout(hideGradioLoading, 0);
        setTimeout(hideGradioLoading, 100);
        setTimeout(hideGradioLoading, 500);
        setTimeout(hideGradioLoading, 1000);
        
        // Also run on window load
        window.addEventListener('load', hideGradioLoading);
        
        // Global function accessible from anywhere
        window.toggleTheme = toggleTheme;
        window.initTheme = initTheme;
        
        // Credits modal functionality
        function showCreditsModal() {
            const modal = document.getElementById('creditsModal');
            if (modal) {
                modal.style.display = 'flex';
                document.body.style.overflow = 'hidden';
            }
        }
        
        function hideCreditsModal() {
            const modal = document.getElementById('creditsModal');
            if (modal) {
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        }
        
        // Close modal when clicking outside
        function handleModalClick(event) {
            if (event.target.classList.contains('modal-overlay')) {
                hideCreditsModal();
            }
        }
        
        // Help button functionality - formato balão
        function toggleHelpModal() {
            const modal = document.getElementById('helpModal');
            if (modal) {
                const isOpen = modal.classList.contains('open');
                if (isOpen) {
                    modal.classList.remove('open');
                    setTimeout(() => {
                        modal.style.display = 'none';
                    }, 300);
                } else {
                    modal.style.display = 'block';
                    // Force reflow to ensure the element is rendered
                    modal.offsetHeight;
                    modal.classList.add('open');
                }
            }
        }
        
        function hideHelpModal() {
            const modal = document.getElementById('helpModal');
            if (modal) {
                modal.classList.remove('open');
                setTimeout(() => {
                    modal.style.display = 'none';
                }, 300);
            }
        }
        
        // Close help modal when clicking outside
        function handleHelpModalClick(event) {
            // Only close if clicking on the modal itself, not its content
            if (event.target.classList.contains('help-modal')) {
                hideHelpModal();
            }
        }
        
        window.showCreditsModal = showCreditsModal;
        window.hideCreditsModal = hideCreditsModal;
        window.handleModalClick = handleModalClick;
        window.toggleHelpModal = toggleHelpModal;
        window.hideHelpModal = hideHelpModal;
        window.handleHelpModalClick = handleHelpModalClick;
        
        console.log('Theme script loaded');
    </script>
    
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
                <button class="btn btn-primary" onclick="document.querySelector('.gradio-container .tabs button:nth-child(2)').click()">
                    <span>🔍</span> Consulta Avançada
                </button>
                <button class="btn btn-secondary" onclick="document.querySelector('.gradio-container .tabs button:nth-child(3)').click()">
                    <span>💬</span> Pergunte ao Modelo
                </button>
            </div>
            
            
        </div>
    </div>
    
    <!-- Modal de Créditos -->
    <div id="creditsModal" class="modal-overlay" onclick="handleModalClick(event)" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); z-index: 2000; justify-content: center; align-items: center;">
        <div class="modal-content" style="background: var(--bg-primary); border-radius: 12px; padding: 2rem; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto; box-shadow: var(--shadow-xl); border: 1px solid var(--border-color);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h2 style="color: var(--text-primary); margin: 0; font-size: 1.5rem; font-weight: 600;">Créditos</h2>
                <button onclick="hideCreditsModal()" style="background: transparent; border: none; font-size: 1.5rem; cursor: pointer; color: var(--text-secondary); padding: 0.5rem;">×</button>
            </div>
            
            <div style="color: var(--text-secondary); line-height: 1.6;">
                <div style="margin-bottom: 1.5rem;">
                    <h3 style="color: var(--text-primary); margin-bottom: 0.5rem; font-size: 1.125rem;">🇧🇷 Cidadão.AI</h3>
                    <p style="margin-bottom: 1rem;">Plataforma inteligente para análise de dados públicos brasileiros</p>
                </div>
                
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">🔗 Links Importantes</h4>
                    <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem;">
                        <a href="https://github.com/anderson-ufrj/cidadao.ai" target="_blank" style="color: var(--primary-blue); text-decoration: none; padding: 0.5rem 1rem; border: 1px solid var(--border-color); border-radius: 6px; transition: all 0.2s ease;">
                            <span>📚</span> GitHub
                        </a>
                        <a href="https://huggingface.co/spaces/neural-thinker/cidadao.ia" target="_blank" style="color: var(--primary-blue); text-decoration: none; padding: 0.5rem 1rem; border: 1px solid var(--border-color); border-radius: 6px; transition: all 0.2s ease;">
                            <span>🤗</span> Hugging Face
                        </a>
                        <a href="https://anderson-ufrj.github.io/cidadao.ai/" target="_blank" style="color: var(--primary-blue); text-decoration: none; padding: 0.5rem 1rem; border: 1px solid var(--border-color); border-radius: 6px; transition: all 0.2s ease;">
                            <span>📖</span> Documentação Técnica
                        </a>
                        <a href="https://gradio.app" target="_blank" style="color: var(--primary-blue); text-decoration: none; padding: 0.5rem 1rem; border: 1px solid var(--border-color); border-radius: 6px; transition: all 0.2s ease;">
                            <span>🎨</span> Made with Gradio
                        </a>
                        <a href="https://api.portaldatransparencia.gov.br" target="_blank" style="color: var(--primary-blue); text-decoration: none; padding: 0.5rem 1rem; border: 1px solid var(--border-color); border-radius: 6px; transition: all 0.2s ease;">
                            <span>🔌</span> Use via API
                        </a>
                    </div>
                </div>
                
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">🎓 Projeto Acadêmico</h4>
                    <p style="background: var(--bg-secondary); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--primary-green);">
                        Feito com carinho para Trabalho de Conclusão de Curso - Bacharelado em Ciência da Computação
                    </p>
                </div>
                
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">🛠️ Tecnologias Utilizadas</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.5rem;">
                        <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: 6px; font-size: 0.875rem;">
                            <strong>Interface:</strong> Gradio 5.0
                        </div>
                        <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: 6px; font-size: 0.875rem;">
                            <strong>API:</strong> Portal da Transparência
                        </div>
                        <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: 6px; font-size: 0.875rem;">
                            <strong>IA:</strong> GROQ & LLaMA
                        </div>
                        <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: 6px; font-size: 0.875rem;">
                            <strong>Deploy:</strong> Hugging Face Spaces
                        </div>
                    </div>
                </div>
                
                <div style="text-align: center; padding-top: 1rem; border-top: 1px solid var(--border-color);">
                    <p style="font-size: 0.875rem; color: var(--text-tertiary);">
                        © 2025 Cidadão.AI - Democratizando o acesso à transparência pública
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
    """

def create_interface():
    """Interface principal"""
    
    with gr.Blocks(
        css=custom_css, 
        title="Cidadão.AI",
        theme=gr.themes.Base(),
        head="<style>body { margin: 0; padding: 0; }</style>"
    ) as app:
        
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
                    <button class="theme-toggle" onclick="toggleTheme()" id="theme-toggle-btn-2">
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
                    <button class="theme-toggle" onclick="toggleTheme()" id="theme-toggle-btn-2">
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
    print("🚀 Iniciando Cidadão.AI - Loading Otimizado...")
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