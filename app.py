#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Landing Page Otimizada para Gradio
Sistema de consulta aos dados do Portal da Transparência
"""

import gradio as gr
import os
import time

# Configurar variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# CSS otimizado para Gradio
custom_css = """
/* Variáveis de tema */
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

/* Container principal do Gradio */
.gradio-container {
    max-height: 100vh;
    overflow-y: auto;
}

/* Landing page dentro do Gradio */
.landing-page {
    min-height: 95vh;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(
        rgba(0, 0, 0, 0.6),
        rgba(0, 0, 0, 0.7)
    );
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: white;
    text-align: center;
    overflow: hidden;
    margin: 0;
    padding: 2rem;
}

/* Theme toggle */
.theme-toggle {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
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

/* Conteúdo principal */
.hero-content {
    max-width: 800px;
    padding: 3rem 2rem;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
    animation: fadeInUp 0.8s ease-out;
}

[data-theme="dark"] .hero-content {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
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

/* Títulos */
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

/* Botões */
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

/* Footer */
.footer-content {
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 2rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;
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

/* Responsivo */
@media (max-width: 768px) {
    .hero-title { 
        font-size: 2.5rem; 
    }
    .hero-subtitle { 
        font-size: 1.25rem; 
    }
    .hero-content { 
        padding: 2rem 1.5rem; 
        margin: 0 1rem;
    }
    .action-buttons { 
        flex-direction: column; 
    }
    .btn { 
        width: 100%; 
        max-width: 280px; 
    }
    .footer-links { 
        flex-direction: column; 
        gap: 1rem; 
    }
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
    const landingPage = document.querySelector('.landing-page');
    if (landingPage) {
        currentSlide = (currentSlide + 1) % slides.length;
        landingPage.style.backgroundImage = `linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.7)), url('${slides[currentSlide]}')`;
    }
}

// Navegação para abas
function showTab(tabName) {
    const tabs = document.querySelectorAll('.tab-nav button');
    tabs.forEach(tab => {
        if (tab.textContent.includes(tabName)) {
            tab.click();
        }
    });
}

// Inicializar quando carregar
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    
    // Configurar slideshow
    const landingPage = document.querySelector('.landing-page');
    if (landingPage && slides.length > 0) {
        landingPage.style.backgroundImage = `linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.7)), url('${slides[0]}')`;
        setInterval(changeBackground, 5000);
    }
    
    // Event listeners para botões
    document.querySelectorAll('.btn-primary').forEach(btn => {
        btn.addEventListener('click', () => showTab('Busca Avançada'));
    });
    
    document.querySelectorAll('.btn-secondary').forEach(btn => {
        btn.addEventListener('click', () => showTab('Chat com IA'));
    });
});
</script>
"""

def create_landing_page():
    """Landing page otimizada para Gradio"""
    return f"""
    <div class="landing-page">
        <div class="theme-toggle" onclick="toggleTheme()">🌙</div>
        
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
            
            <div class="footer-content">
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
                <p style="margin: 1rem 0 0 0; font-size: 0.8rem; opacity: 0.9;">
                    <strong>Desenvolvido por:</strong> Anderson Henrique da Silva | © 2024 Cidadão.AI
                </p>
            </div>
        </div>
    </div>
    """

def search_transparency_data(data_type, year, org_code, search_term):
    """Buscar dados simulados"""
    time.sleep(1)
    
    if not TRANSPARENCY_API_KEY:
        return """
        <div style="background: #fee; padding: 1rem; border-radius: 8px; border-left: 4px solid #f44;">
            <h3>⚠️ API não configurada</h3>
            <p>Configure a variável TRANSPARENCY_API_KEY para usar dados reais.</p>
        </div>
        """
    
    # Dados simulados
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
    <div style="background: white; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h3>✅ {len(data)} resultados encontrados</h3>
        <p>Dados do Portal da Transparência - {data_type} em {year}</p>
    </div>
    """
    
    if data and data_type == "Contratos":
        html += """<table style="width: 100%; margin-top: 1rem; border-collapse: collapse;">
        <tr style="background: #f5f5f5;">
            <th style="padding: 0.75rem; text-align: left; border: 1px solid #ddd;">Número</th>
            <th style="padding: 0.75rem; text-align: left; border: 1px solid #ddd;">Empresa</th>
            <th style="padding: 0.75rem; text-align: left; border: 1px solid #ddd;">Valor</th>
            <th style="padding: 0.75rem; text-align: left; border: 1px solid #ddd;">Objeto</th>
        </tr>"""
        for item in data:
            html += f"""
            <tr>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['numero']}</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['empresa']}</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;"><strong>{item['valor']}</strong></td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['objeto']}</td>
            </tr>"""
        html += "</table>"
    
    return html

def chat_with_ai(message, history):
    """Chat simulado com IA"""
    if not message:
        return history
    
    # Resposta simulada
    response = f"Você perguntou sobre: '{message}'. Esta é uma demonstração do chat com IA especializada em transparência pública. Em breve, terei acesso a dados reais para ajudá-lo!"
    
    history.append([message, response])
    return history

def create_interface():
    """Interface principal do Gradio"""
    
    with gr.Blocks(css=custom_css, title="Cidadão.AI", theme=gr.themes.Soft()) as app:
        
        # JavaScript
        gr.HTML(custom_js)
        
        # Landing page como primeira aba
        with gr.Tab("🏠 Cidadão.AI", id="home"):
            gr.HTML(create_landing_page())
        
        # Aba de busca
        with gr.Tab("🔍 Busca Avançada com IA", id="search"):
            gr.Markdown("## Sistema de Busca Inteligente")
            gr.Markdown("Configure os parâmetros abaixo para buscar dados do Portal da Transparência:")
            
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
                    results = gr.HTML(
                        value="""
                        <div style="background: #f8f9fa; padding: 2rem; border-radius: 8px; text-align: center;">
                            <h3>🚀 Pronto para buscar</h3>
                            <p>Configure os parâmetros ao lado e clique em "Buscar" para ver os resultados.</p>
                        </div>
                        """
                    )
            
            search_btn.click(
                fn=search_transparency_data,
                inputs=[data_type, year, org_code, search_term],
                outputs=results
            )
        
        # Aba de chat
        with gr.Tab("💬 Chat com IA Especializada", id="chat"):
            gr.Markdown("## Converse com o Cidadão-GPT")
            gr.Markdown("Faça perguntas em linguagem natural sobre transparência pública:")
            
            chatbot = gr.Chatbot(
                height=400,
                placeholder="💭 Pergunte algo como: 'Quais foram os maiores contratos de 2024?' ou 'Mostre gastos suspeitos do Ministério da Saúde'"
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Digite sua pergunta sobre transparência pública...",
                    label="Sua mensagem",
                    scale=4
                )
                send_btn = gr.Button("📤 Enviar", variant="primary", scale=1)
            
            gr.Markdown("⚠️ **Nota:** Este é um ambiente de demonstração com respostas simuladas.")
            
            def respond_and_clear(message, history):
                new_history = chat_with_ai(message, history)
                return new_history, ""
            
            send_btn.click(
                fn=respond_and_clear,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg]
            )
            
            msg.submit(
                fn=respond_and_clear,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg]
            )
    
    return app

# Executar aplicação
if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI - Otimizado para Gradio...")
    app = create_interface()
    app.launch()