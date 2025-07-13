#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Portal da Transparência
Sistema de consulta aos dados do Portal da Transparência
"""

import gradio as gr
import os
import time

# Configurar variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")

# CSS simplificado
custom_css = """
/* Landing page */
.landing-page {
    min-height: 90vh;
    background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.7)),
                url('https://upload.wikimedia.org/wikipedia/commons/e/e3/Congresso_Nacional_-_Brasília_-_panorama.jpg');
    background-size: cover;
    background-position: center;
    color: white;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    margin: 0;
}

.hero-content {
    max-width: 800px;
    padding: 3rem 2rem;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #FFD700, #FFFFFF, #32CD32);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
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
}

.btn-primary {
    background: #0066cc;
    color: white;
    box-shadow: 0 4px 15px rgba(0, 102, 204, 0.3);
}

.btn-primary:hover {
    background: #0052a3;
    transform: translateY(-2px);
}

.btn-secondary {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.footer-content {
    margin-top: 2rem;
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
}

.footer-link:hover {
    color: #FFD700;
}

@media (max-width: 768px) {
    .hero-title { font-size: 2.5rem; }
    .hero-subtitle { font-size: 1.25rem; }
    .hero-content { padding: 2rem 1.5rem; margin: 0 1rem; }
    .action-buttons { flex-direction: column; }
    .btn { width: 100%; max-width: 280px; }
    .footer-links { flex-direction: column; gap: 1rem; }
}
"""

def create_landing_page():
    """Landing page"""
    return """
    <div class="landing-page">
        <div class="hero-content">
            <h1 class="hero-title">Cidadão.AI</h1>
            <h2 class="hero-subtitle">Portal da Transparência Inteligente</h2>
            <p class="hero-description">
                Democratizando o acesso aos dados públicos brasileiros através da inteligência artificial.
                Consulte contratos, licitações e gastos governamentais de forma simples e transparente.
            </p>
            
            <div class="action-buttons">
                <div class="btn btn-primary" style="display: inline-block;">
                    🔍 Busca Avançada
                </div>
                <div class="btn btn-secondary" style="display: inline-block;">
                    💬 Chat com IA
                </div>
            </div>
            
            <div class="footer-content">
                <div class="footer-links">
                    <a href="docs/documentation.html" target="_blank" class="footer-link">
                        📚 Documentação
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

def search_data(data_type, year, search_term):
    """Buscar dados"""
    time.sleep(1)
    
    if not TRANSPARENCY_API_KEY:
        return """
        <div style="background: #fee; padding: 1rem; border-radius: 8px; border-left: 4px solid #f44;">
            <h3>⚠️ API não configurada</h3>
            <p>Configure a variável TRANSPARENCY_API_KEY para usar dados reais.</p>
        </div>
        """
    
    # Dados simulados
    results = [
        {"numero": "001/2024", "empresa": "Tech Solutions", "valor": "R$ 2.500.000", "objeto": "Sistema de TI"},
        {"numero": "002/2024", "empresa": "Construtora XYZ", "valor": "R$ 5.800.000", "objeto": "Reforma predial"}
    ]
    
    html = f"""
    <div style="background: white; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h3>✅ {len(results)} resultados encontrados</h3>
        <p>Dados do Portal da Transparência - {data_type} em {year}</p>
    </div>
    """
    
    html += """<table style="width: 100%; margin-top: 1rem; border-collapse: collapse;">
    <tr style="background: #f5f5f5;">
        <th style="padding: 0.75rem; text-align: left; border: 1px solid #ddd;">Número</th>
        <th style="padding: 0.75rem; text-align: left; border: 1px solid #ddd;">Empresa</th>
        <th style="padding: 0.75rem; text-align: left; border: 1px solid #ddd;">Valor</th>
        <th style="padding: 0.75rem; text-align: left; border: 1px solid #ddd;">Objeto</th>
    </tr>"""
    
    for item in results:
        html += f"""
        <tr>
            <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['numero']}</td>
            <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['empresa']}</td>
            <td style="padding: 0.75rem; border: 1px solid #ddd;"><strong>{item['valor']}</strong></td>
            <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['objeto']}</td>
        </tr>"""
    
    html += "</table>"
    return html

def create_interface():
    """Interface principal"""
    
    with gr.Blocks(css=custom_css, title="Cidadão.AI") as app:
        
        # Landing page como primeira aba
        with gr.Tab("🏠 Cidadão.AI"):
            gr.HTML(create_landing_page())
        
        # Aba de busca
        with gr.Tab("🔍 Busca Avançada"):
            gr.Markdown("## Sistema de Busca")
            
            with gr.Row():
                with gr.Column():
                    data_type = gr.Radio(
                        label="Tipo de Dados",
                        choices=["Contratos", "Despesas", "Licitações"],
                        value="Contratos"
                    )
                    
                    year = gr.Number(
                        label="Ano",
                        value=2024
                    )
                    
                    search_term = gr.Textbox(
                        label="Termo de Busca",
                        placeholder="Digite sua busca..."
                    )
                    
                    search_btn = gr.Button("🔍 Buscar", variant="primary")
                
                with gr.Column():
                    results = gr.HTML(
                        value="<p>Configure os parâmetros e clique em 'Buscar'</p>"
                    )
            
            search_btn.click(
                fn=search_data,
                inputs=[data_type, year, search_term],
                outputs=results
            )
        
        # Aba de chat
        with gr.Tab("💬 Chat com IA"):
            gr.Markdown("## Chat com IA")
            
            chatbot = gr.Chatbot(height=400)
            msg = gr.Textbox(placeholder="Digite sua mensagem...")
            
            def respond(message, history):
                if message:
                    response = f"Você perguntou: '{message}'. Esta é uma demonstração do chat!"
                    history.append([message, response])
                return history, ""
            
            msg.submit(respond, inputs=[msg, chatbot], outputs=[chatbot, msg])
    
    return app

# Executar aplicação
if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI...")
    app = create_interface()
    app.launch()