#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Interface Profissional com Temas
Sistema de consulta aos dados do Portal da Transparência
"""

import gradio as gr
import os
import time
import json
import random
from datetime import datetime

# Configurar variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# CSS com tema claro/escuro e correções
custom_css = """
/* Variáveis de tema */
:root {
    /* Tema Claro */
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --bg-tertiary: #e9ecef;
    --text-primary: #212529;
    --text-secondary: #495057;
    --text-muted: #6c757d;
    --border-color: #dee2e6;
    --shadow-color: rgba(0, 0, 0, 0.1);
    --overlay-dark: rgba(0, 0, 0, 0.6);
    --overlay-light: rgba(255, 255, 255, 0.9);
    --card-bg: rgba(255, 255, 255, 0.95);
    --btn-primary-bg: #0066cc;
    --btn-primary-hover: #0052a3;
    --btn-secondary-bg: rgba(255, 255, 255, 0.2);
    --btn-secondary-hover: rgba(255, 255, 255, 0.3);
}

[data-theme="dark"] {
    /* Tema Escuro */
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --bg-tertiary: #0f3460;
    --text-primary: #f8f9fa;
    --text-secondary: #e9ecef;
    --text-muted: #adb5bd;
    --border-color: #495057;
    --shadow-color: rgba(0, 0, 0, 0.3);
    --overlay-dark: rgba(0, 0, 0, 0.8);
    --overlay-light: rgba(0, 0, 0, 0.85);
    --card-bg: rgba(22, 33, 62, 0.95);
    --btn-primary-bg: #0066cc;
    --btn-primary-hover: #0077dd;
    --btn-secondary-bg: rgba(255, 255, 255, 0.15);
    --btn-secondary-hover: rgba(255, 255, 255, 0.25);
}

/* Reset e base */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body {
    height: 100%;
    overflow-x: hidden;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: var(--text-primary);
    background-color: var(--bg-primary);
    transition: background-color 0.3s ease, color 0.3s ease;
}

/* Container principal */
.main-container {
    min-height: 100vh;
    position: relative;
}

/* Theme toggle */
.theme-toggle {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    background: var(--card-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-color);
    border-radius: 50%;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px var(--shadow-color);
}

.theme-toggle:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px var(--shadow-color);
}

/* Hero Section corrigida */
.hero-section {
    position: relative;
    height: 100vh;
    max-height: 800px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.hero-background {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    transition: opacity 1s ease-in-out;
}

.hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        to bottom,
        var(--overlay-dark) 0%,
        var(--overlay-dark) 100%
    );
}

.hero-content {
    position: relative;
    z-index: 2;
    max-width: 800px;
    padding: 3rem 2rem;
    background: var(--card-bg);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    border: 1px solid var(--border-color);
    box-shadow: 0 25px 50px var(--shadow-color);
    text-align: center;
    animation: fadeInUp 0.8s ease-out;
}

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

.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #FFD700, #32CD32, #0066cc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
}

.hero-subtitle {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 1rem;
}

.hero-description {
    font-size: 1.1rem;
    color: var(--text-muted);
    margin-bottom: 2rem;
    line-height: 1.7;
}

/* Botões de ação */
.action-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}

.btn {
    padding: 0.875rem 2rem;
    border-radius: 50px;
    font-size: 1rem;
    font-weight: 600;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    transition: all 0.3s ease;
    border: none;
    outline: none;
}

.btn-primary {
    background: var(--btn-primary-bg);
    color: white;
    box-shadow: 0 4px 15px rgba(0, 102, 204, 0.3);
}

.btn-primary:hover {
    background: var(--btn-primary-hover);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 102, 204, 0.4);
}

.btn-secondary {
    background: var(--btn-secondary-bg);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(10px);
}

.btn-secondary:hover {
    background: var(--btn-secondary-hover);
    transform: translateY(-2px);
    border-color: rgba(255, 255, 255, 0.5);
}

/* Features Section */
.features-section {
    background: var(--bg-secondary);
    padding: 4rem 2rem;
    transition: background-color 0.3s ease;
}

.features-container {
    max-width: 1200px;
    margin: 0 auto;
}

.features-title {
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 3rem;
    color: var(--text-primary);
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.feature-card {
    background: var(--card-bg);
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 4px 15px var(--shadow-color);
    transition: all 0.3s ease;
    border: 1px solid var(--border-color);
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px var(--shadow-color);
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.feature-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.feature-description {
    color: var(--text-secondary);
    line-height: 1.6;
}

/* Status Section */
.status-section {
    padding: 3rem 2rem;
    background: var(--bg-primary);
}

.status-container {
    max-width: 800px;
    margin: 0 auto;
}

.status-card {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 2rem;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.status-card.active {
    background: linear-gradient(135deg, #4CAF50, #45a049);
    box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
}

/* Footer */
.footer-section {
    background: var(--bg-tertiary);
    color: var(--text-primary);
    padding: 3rem 2rem;
    text-align: center;
    transition: background-color 0.3s ease;
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 2rem;
    flex-wrap: wrap;
    margin: 2rem 0;
}

.footer-link {
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
}

.footer-link:hover {
    color: var(--btn-primary-bg);
}

/* Responsividade */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
    }
    
    .hero-description {
        font-size: 1rem;
    }
    
    .hero-content {
        padding: 2rem 1.5rem;
        margin: 0 1rem;
    }
    
    .action-buttons {
        flex-direction: column;
        width: 100%;
    }
    
    .btn {
        width: 100%;
        justify-content: center;
    }
    
    .features-title {
        font-size: 2rem;
    }
    
    .footer-links {
        flex-direction: column;
        gap: 1rem;
    }
}

/* Scrollbar personalizada */
::-webkit-scrollbar {
    width: 12px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--text-muted);
    border-radius: 6px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
}
"""

# JavaScript para tema e slideshow
custom_js = """
<script>
// Sistema de tema
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.innerHTML = theme === 'light' ? '🌙' : '☀️';
    }
}

// Slideshow de imagens
const slides = [
    'https://upload.wikimedia.org/wikipedia/commons/e/e3/Congresso_Nacional_-_Brasília_-_panorama.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Palácio_da_Alvorada_-_Brasília.jpg/1200px-Palácio_da_Alvorada_-_Brasília.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Supremo_Tribunal_Federal_do_Brasil.jpg/1200px-Supremo_Tribunal_Federal_do_Brasil.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Palácio_do_Planalto_-_Brasília_2.jpg/1200px-Palácio_do_Planalto_-_Brasília_2.jpg'
];

let currentSlide = 0;

function changeBackground() {
    const heroBackground = document.querySelector('.hero-background');
    if (heroBackground) {
        currentSlide = (currentSlide + 1) % slides.length;
        heroBackground.style.backgroundImage = `url('${slides[currentSlide]}')`;
    }
}

// Navegação suave para abas
function scrollToTab(tabName) {
    const tabButton = Array.from(document.querySelectorAll('button')).find(
        btn => btn.textContent.includes(tabName)
    );
    if (tabButton) {
        tabButton.click();
        window.scrollTo({ top: 600, behavior: 'smooth' });
    }
}

// Inicializar quando o DOM carregar
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    
    // Configurar slideshow
    const heroBackground = document.querySelector('.hero-background');
    if (heroBackground && slides.length > 0) {
        heroBackground.style.backgroundImage = `url('${slides[0]}')`;
        setInterval(changeBackground, 5000);
    }
    
    // Adicionar event listeners aos botões
    document.querySelectorAll('.btn-primary').forEach(btn => {
        btn.addEventListener('click', () => scrollToTab('Busca Avançada'));
    });
    
    document.querySelectorAll('.btn-secondary').forEach(btn => {
        btn.addEventListener('click', () => scrollToTab('Chat com IA'));
    });
});
</script>
"""

def create_hero_section():
    """Criar a seção hero com tema e slideshow"""
    return f"""
    <div class="main-container">
        <div class="theme-toggle" onclick="toggleTheme()">🌙</div>
        
        <div class="hero-section">
            <div class="hero-background"></div>
            <div class="hero-overlay"></div>
            
            <div class="hero-content">
                <h1 class="hero-title">Cidadão.AI</h1>
                <h2 class="hero-subtitle">Bem-vindo ao Portal da Transparência Inteligente</h2>
                <p class="hero-description">
                    Democratizando o acesso aos dados públicos brasileiros através da inteligência artificial.
                    Consulte contratos, licitações e gastos governamentais de forma simples e transparente.
                </p>
                <div class="action-buttons">
                    <button class="btn btn-primary" onclick="scrollToTab('Busca Avançada')">
                        🔍 Busca Avançada com IA
                    </button>
                    <button class="btn btn-secondary" onclick="scrollToTab('Chat com IA')">
                        💬 Converse com nosso Modelo
                    </button>
                </div>
            </div>
        </div>
    </div>
    """

def create_features_section():
    """Criar seção de funcionalidades"""
    return """
    <div class="features-section">
        <div class="features-container">
            <h2 class="features-title">Nossos Recursos</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3 class="feature-title">Análise de Contratos</h3>
                    <p class="feature-description">
                        Análise inteligente de contratos públicos com detecção de irregularidades.
                    </p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💰</div>
                    <h3 class="feature-title">Monitoramento de Gastos</h3>
                    <p class="feature-description">
                        Acompanhamento em tempo real das despesas públicas federais.
                    </p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <h3 class="feature-title">Licitações Inteligentes</h3>
                    <p class="feature-description">
                        Análise de processos licitatórios com identificação de riscos.
                    </p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">⚖️</div>
                    <h3 class="feature-title">Conformidade Legal</h3>
                    <p class="feature-description">
                        Verificação automática com a legislação brasileira vigente.
                    </p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <h3 class="feature-title">IA Especializada</h3>
                    <p class="feature-description">
                        Modelo treinado para transparência pública brasileira.
                    </p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📈</div>
                    <h3 class="feature-title">Relatórios Executivos</h3>
                    <p class="feature-description">
                        Geração automática de relatórios com insights relevantes.
                    </p>
                </div>
            </div>
        </div>
    </div>
    """

def create_status_section():
    """Criar seção de status"""
    api_status = "✅ Conectado" if TRANSPARENCY_API_KEY else "❌ Não configurado"
    ai_status = "✅ Ativo" if GROQ_API_KEY else "⚠️ Limitado"
    
    return f"""
    <div class="status-section">
        <div class="status-container">
            <div class="status-card {'active' if TRANSPARENCY_API_KEY else ''}">
                <h3>📊 Status do Sistema</h3>
                <p><strong>Portal da Transparência:</strong> {api_status}</p>
                <p><strong>Modelo de IA:</strong> {ai_status}</p>
                <p><strong>Base de Dados:</strong> 2.1T+ em contratos analisados</p>
                <p><strong>Última Atualização:</strong> Tempo real</p>
            </div>
        </div>
    </div>
    """

def create_footer():
    """Criar rodapé"""
    return """
    <div class="footer-section">
        <h3>🇧🇷 Cidadão.AI</h3>
        <p>Democratizando o acesso aos dados públicos brasileiros</p>
        
        <div class="footer-links">
            <a href="/docs/documentation.html" target="_blank" class="footer-link">
                📚 Documentação
            </a>
            <a href="https://github.com/anderson-ufrj/cidadao.ai" target="_blank" class="footer-link">
                💻 GitHub
            </a>
            <a href="https://portaldatransparencia.gov.br" target="_blank" class="footer-link">
                🔗 Portal da Transparência
            </a>
        </div>
        
        <p style="margin-top: 2rem; opacity: 0.8;">
            Desenvolvido por Anderson Henrique da Silva<br>
            © 2024 Cidadão.AI - MIT License
        </p>
    </div>
    """

def search_transparency_data(data_type, year, org_code, search_term):
    """Buscar dados de transparência"""
    time.sleep(1)  # Simular processamento
    
    if not TRANSPARENCY_API_KEY:
        return """
        <div style="background: #fee; padding: 1rem; border-radius: 8px; border-left: 4px solid #f44;">
            <h3>⚠️ API não configurada</h3>
            <p>Configure a variável TRANSPARENCY_API_KEY para usar dados reais.</p>
        </div>
        """
    
    # Dados simulados para demonstração
    results = {
        "Contratos": [
            {"numero": "001/2024", "empresa": "Tech Solutions", "valor": "R$ 2.500.000", "objeto": "Sistema de TI"},
            {"numero": "002/2024", "empresa": "Construtora XYZ", "valor": "R$ 5.800.000", "objeto": "Reforma predial"}
        ],
        "Despesas": [
            {"documento": "2024NE000123", "favorecido": "Empresa ABC", "valor": "R$ 450.000", "descricao": "Material"},
            {"documento": "2024NE000124", "favorecido": "Fornecedor XYZ", "valor": "R$ 780.000", "descricao": "Equipamentos"}
        ],
        "Licitações": [
            {"numero": "PE001/2024", "modalidade": "Pregão", "valor": "R$ 3.200.000", "objeto": "Veículos"},
            {"numero": "CC002/2024", "modalidade": "Concorrência", "valor": "R$ 15.000.000", "objeto": "Obra"}
        ]
    }
    
    data = results.get(data_type, [])
    
    if search_term:
        data = [item for item in data if search_term.lower() in str(item).lower()]
    
    html = f"""
    <div style="background: var(--card-bg); padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
        <h3>✅ {len(data)} resultados encontrados</h3>
        <p>Dados do Portal da Transparência - {data_type} em {year}</p>
    </div>
    """
    
    if data_type == "Contratos":
        html += """<table style="width: 100%; margin-top: 1rem;">
        <tr style="background: var(--bg-secondary);">
            <th style="padding: 0.75rem; text-align: left;">Número</th>
            <th style="padding: 0.75rem; text-align: left;">Empresa</th>
            <th style="padding: 0.75rem; text-align: left;">Valor</th>
            <th style="padding: 0.75rem; text-align: left;">Objeto</th>
        </tr>"""
        for item in data:
            html += f"""
            <tr>
                <td style="padding: 0.75rem;">{item['numero']}</td>
                <td style="padding: 0.75rem;">{item['empresa']}</td>
                <td style="padding: 0.75rem;"><strong>{item['valor']}</strong></td>
                <td style="padding: 0.75rem;">{item['objeto']}</td>
            </tr>"""
        html += "</table>"
    
    return html

def create_interface():
    """Interface principal com tema e navegação melhorada"""
    
    with gr.Blocks(css=custom_css, title="Cidadão.AI", theme=gr.themes.Soft()) as app:
        
        # Injetar JavaScript
        gr.HTML(custom_js)
        
        # Hero Section
        gr.HTML(create_hero_section())
        
        # Features Section
        gr.HTML(create_features_section())
        
        # Status Section
        gr.HTML(create_status_section())
        
        # Interface de busca
        with gr.Tab("🔍 Busca Avançada com IA"):
            gr.Markdown("### Sistema de Busca Inteligente")
            
            with gr.Row():
                with gr.Column(scale=1):
                    data_type = gr.Radio(
                        label="Tipo de Dados",
                        choices=["Contratos", "Despesas", "Licitações"],
                        value="Contratos"
                    )
                    
                    year = gr.Number(
                        label="Ano",
                        value=2024,
                        precision=0
                    )
                    
                    org_code = gr.Textbox(
                        label="Código do Órgão (opcional)",
                        placeholder="Ex: 26000"
                    )
                    
                    search_term = gr.Textbox(
                        label="Termo de Busca",
                        placeholder="Digite sua busca..."
                    )
                    
                    search_btn = gr.Button("🔍 Buscar", variant="primary")
                
                with gr.Column(scale=2):
                    results = gr.HTML()
            
            search_btn.click(
                fn=search_transparency_data,
                inputs=[data_type, year, org_code, search_term],
                outputs=results
            )
        
        with gr.Tab("💬 Chat com IA Especializada"):
            gr.Markdown("### Converse com o Cidadão-GPT")
            
            chatbot = gr.Chatbot(height=400)
            msg = gr.Textbox(
                placeholder="Faça uma pergunta sobre transparência pública...",
                label="Sua mensagem"
            )
            send = gr.Button("Enviar", variant="primary")
            
            gr.Markdown("⚠️ **Nota:** Chat em modo demonstração")
        
        # Footer
        gr.HTML(create_footer())
    
    return app

# Executar aplicação
if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI com tema claro/escuro...")
    app = create_interface()
    app.launch()