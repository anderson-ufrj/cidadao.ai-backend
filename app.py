#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Landing Page Fixa
Sistema de consulta aos dados do Portal da Transparência
"""

import gradio as gr
import os
import time

# Configurar variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# CSS FORÇADO para impedir scroll
custom_css = """
/* RESET TOTAL - FORÇA GRADIO A OBEDECER */
* {
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box !important;
}

/* FORÇA HTML/BODY SEM SCROLL */
html, body, #root, .gradio-container, .main, .block, .contain {
    height: 100vh !important;
    max-height: 100vh !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* FORÇA CONTAINER PRINCIPAL */
.gradio-container {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important;
}

/* VARIÁVEIS DE TEMA */
:root {
    --bg-primary: #ffffff;
    --text-primary: #212529;
    --btn-primary: #0066cc;
}

[data-theme="dark"] {
    --bg-primary: #1a1a2e;
    --text-primary: #f8f9fa;
    --btn-primary: #0077dd;
}

/* LANDING PAGE ÚNICA */
.landing-page {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important;
    z-index: 1000 !important;
}

/* BACKGROUND COM SLIDESHOW */
.hero-background {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    transition: background-image 1s ease-in-out;
}

/* OVERLAY ESCURO */
.hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        to bottom,
        rgba(0, 0, 0, 0.6) 0%,
        rgba(0, 0, 0, 0.7) 100%
    );
}

/* CONTEÚDO PRINCIPAL */
.hero-content {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    color: white;
    z-index: 10;
    max-width: 800px;
    padding: 3rem 2rem;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
}

/* TÍTULOS */
.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #FFD700, #FFFFFF, #32CD32);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.hero-subtitle {
    font-size: 1.5rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 1rem;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7);
}

.hero-description {
    font-size: 1.1rem;
    color: #f8f9fa;
    margin-bottom: 2rem;
    line-height: 1.7;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}

/* BOTÕES */
.action-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 2rem;
}

.btn {
    padding: 1rem 2rem;
    border-radius: 50px;
    font-size: 1rem;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.btn-primary {
    background: #0066cc;
    color: white;
    box-shadow: 0 4px 15px rgba(0, 102, 204, 0.3);
}

.btn-primary:hover {
    background: #0052a3;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 102, 204, 0.4);
}

.btn-secondary {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(10px);
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

/* THEME TOGGLE */
.theme-toggle {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1001;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 1.5rem;
    color: white;
    transition: all 0.3s ease;
}

.theme-toggle:hover {
    transform: scale(1.1);
    background: rgba(255, 255, 255, 0.3);
}

/* FOOTER FIXO */
.footer-fixed {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 1rem 2rem;
    text-align: center;
    z-index: 1001;
    backdrop-filter: blur(10px);
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 2rem;
    flex-wrap: wrap;
    margin-bottom: 0.5rem;
}

.footer-link {
    color: white;
    text-decoration: none;
    font-weight: 500;
    font-size: 0.9rem;
    transition: color 0.3s ease;
}

.footer-link:hover {
    color: #FFD700;
}

/* RESPONSIVO */
@media (max-width: 768px) {
    .hero-title { font-size: 2.5rem; }
    .hero-subtitle { font-size: 1.25rem; }
    .hero-content { 
        padding: 2rem 1.5rem; 
        margin: 0 1rem;
    }
    .action-buttons { flex-direction: column; }
    .btn { width: 100%; max-width: 280px; }
    .footer-links { flex-direction: column; gap: 1rem; }
}

/* FORÇA ESCONDER ELEMENTOS DO GRADIO */
.gradio-container > div:not(.landing-page) {
    display: none !important;
}
"""

# JavaScript para funcionalidades
custom_js = """
<script>
// Lista de imagens de fundo
const slides = [
    'https://upload.wikimedia.org/wikipedia/commons/e/e3/Congresso_Nacional_-_Brasília_-_panorama.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Palácio_da_Alvorada_-_Brasília.jpg/1200px-Palácio_da_Alvorada_-_Brasília.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Supremo_Tribunal_Federal_do_Brasil.jpg/1200px-Supremo_Tribunal_Federal_do_Brasil.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Palácio_do_Planalto_-_Brasília_2.jpg/1200px-Palácio_do_Planalto_-_Brasília_2.jpg'
];

let currentSlide = 0;

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
function changeBackground() {
    const heroBackground = document.querySelector('.hero-background');
    if (heroBackground) {
        currentSlide = (currentSlide + 1) % slides.length;
        heroBackground.style.backgroundImage = `url('${slides[currentSlide]}')`;
    }
}

// Forçar estrutura fixa
function forceFixedLayout() {
    // Remove scroll de todos os elementos
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
    
    // Força altura fixa
    const containers = document.querySelectorAll('.gradio-container, .main, .block, .contain');
    containers.forEach(el => {
        el.style.height = '100vh';
        el.style.maxHeight = '100vh';
        el.style.overflow = 'hidden';
    });
}

// Inicializar quando carregar
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    forceFixedLayout();
    
    // Configurar slideshow
    const heroBackground = document.querySelector('.hero-background');
    if (heroBackground && slides.length > 0) {
        heroBackground.style.backgroundImage = `url('${slides[0]}')`;
        setInterval(changeBackground, 5000);
    }
    
    // Reforçar layout a cada segundo
    setInterval(forceFixedLayout, 1000);
});

// Reforçar ao redimensionar
window.addEventListener('resize', forceFixedLayout);
</script>
"""

def create_landing_page():
    """Landing page fixa e única"""
    return f"""
    <div class="landing-page">
        <div class="theme-toggle" onclick="toggleTheme()">🌙</div>
        
        <div class="hero-background"></div>
        <div class="hero-overlay"></div>
        
        <div class="hero-content">
            <h1 class="hero-title">Cidadão.AI</h1>
            <h2 class="hero-subtitle">Portal da Transparência Inteligente</h2>
            <p class="hero-description">
                Democratizando o acesso aos dados públicos brasileiros através da inteligência artificial.
                Consulte contratos, licitações e gastos governamentais de forma simples e transparente.
            </p>
            <div class="action-buttons">
                <button class="btn btn-primary">
                    🔍 Busca Avançada com IA
                </button>
                <button class="btn btn-secondary">
                    💬 Converse com nosso Modelo
                </button>
            </div>
        </div>
        
        <div class="footer-fixed">
            <div class="footer-links">
                <a href="docs/documentation.html" target="_blank" class="footer-link">
                    📚 Documentação Técnica
                </a>
                <a href="https://github.com/anderson-ufrj/cidadao.ai" target="_blank" class="footer-link">
                    💻 GitHub
                </a>
                <a href="https://portaldatransparencia.gov.br" target="_blank" class="footer-link">
                    🔗 Portal da Transparência
                </a>
            </div>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.9;">
                <strong>Desenvolvido por:</strong> Anderson Henrique da Silva | © 2024 Cidadão.AI
            </p>
        </div>
    </div>
    """

def create_interface():
    """Interface com estrutura fixa forçada"""
    
    with gr.Blocks(css=custom_css, title="Cidadão.AI") as app:
        # JavaScript primeiro
        gr.HTML(custom_js)
        # Landing page única
        gr.HTML(create_landing_page())
    
    return app

# Executar aplicação
if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI - Landing Page Fixa...")
    app = create_interface()
    app.launch()