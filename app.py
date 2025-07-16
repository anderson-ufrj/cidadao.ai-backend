#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Portal da Transparência
GRADIO NATIVO - Fidelidade extrema aos mockups
"""

import gradio as gr
import os
from datetime import datetime

# Configurar variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Função de chat básica
def chat_fn(message, history):
    """Função de chat básica"""
    if not message:
        return history, ""
    
    # Simular resposta do modelo
    response = f"Entendi sua pergunta sobre transparência: '{message}'. Esta é uma demonstração da funcionalidade de chat especializada em dados públicos brasileiros."
    
    history.append((message, response))
    return history, ""

# Função de busca básica
def search_data(data_type, year, search_term):
    """Função de busca básica"""
    if not search_term:
        return "Digite um termo de busca para começar a investigação..."
    
    # Simular resultados de busca
    results = f"""
    # 🔍 Resultados da Investigação
    
    **Termo buscado:** {search_term}  
    **Tipo de dados:** {data_type}  
    **Ano:** {year}  
    **Encontrados:** 156 registros
    
    ---
    
    ## 📊 Principais Achados:
    
    1. **Contrato #2024001** - R$ 2.500.000,00
       - Fornecedor: Empresa ABC Ltda
       - Modalidade: Dispensa de Licitação
       - Status: ⚠️ Verificar valores
    
    2. **Contrato #2024002** - R$ 850.000,00
       - Fornecedor: Empresa XYZ S/A
       - Modalidade: Pregão Eletrônico
       - Status: ✅ Regular
    
    3. **Contrato #2024003** - R$ 1.200.000,00
       - Fornecedor: Empresa 123 Ltda
       - Modalidade: Concorrência
       - Status: ⚠️ Análise requerida
    
    ---
    
    💡 **Dica:** Use filtros mais específicos para refinar os resultados.
    """
    
    return results

def create_interface():
    """Cria interface nativa do Gradio seguindo os mockups"""
    
    # Tema customizado baseado no mockup
    cidadao_theme = gr.themes.Base(
        primary_hue="green",      # Verde para elementos principais
        secondary_hue="blue",     # Azul para elementos secundários
        neutral_hue="slate",      # Cinza neutro
        font=gr.themes.GoogleFont("Inter"),  # Fonte moderna
    ).set(
        # Cores personalizadas baseadas no mockup
        body_background_fill="white",
        body_text_color="#0F172A",
        button_primary_background_fill="#00A86B",
        button_primary_background_fill_hover="#008A5A",
        button_secondary_background_fill="#0066CC",
        button_secondary_background_fill_hover="#004B99",
        block_background_fill="white",
        block_border_color="#E2E8F0",
        block_title_text_color="#0F172A",
        input_background_fill="white",
        input_border_color="#E2E8F0",
    )
    
    # CSS customizado para fidelidade ao mockup
    custom_css = """
    /* Hide Gradio footer */
    .gradio-container .footer {
        display: none !important;
    }
    
    /* Custom header styling */
    .header-container {
        background: white;
        border-bottom: 1px solid #E2E8F0;
        padding: 1rem 2rem;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.5rem;
        font-weight: 700;
        color: #00A86B;
    }
    
    /* Landing page styling */
    .landing-hero {
        text-align: center;
        padding: 4rem 2rem;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        color: #00A86B;
        margin-bottom: 1rem;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: #64748B;
        margin-bottom: 3rem;
        line-height: 1.6;
    }
    
    /* Button styling */
    .primary-button {
        background: linear-gradient(135deg, #0066CC, #4DA6FF) !important;
        color: white !important;
        border: none !important;
        padding: 1.2rem 2.5rem !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        min-width: 200px !important;
        margin: 0.5rem !important;
    }
    
    .secondary-button {
        background: linear-gradient(135deg, #00A86B, #00D084) !important;
        color: white !important;
        border: none !important;
        padding: 1.2rem 2.5rem !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        min-width: 200px !important;
        margin: 0.5rem !important;
    }
    
    /* Advanced search page styling */
    .page-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 2rem;
    }
    
    .sidebar {
        background: #F8FAFC;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        padding: 1.5rem;
    }
    
    .dashboard-area {
        background: #F8FAFC;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        padding: 2rem;
        min-height: 500px;
    }
    
    /* Chat page styling */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .chat-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 1rem;
    }
    
    .chat-subtitle {
        text-align: center;
        color: #64748B;
        margin-bottom: 2rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Hide Gradio branding */
    .gradio-container .version {
        display: none !important;
    }
    
    .gradio-container .footer {
        display: none !important;
    }
    
    .gradio-container .built-with {
        display: none !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hero-subtitle {
            font-size: 1.1rem;
        }
        
        .primary-button, .secondary-button {
            min-width: 150px !important;
            padding: 1rem 1.5rem !important;
        }
    }
    """
    
    with gr.Blocks(
        theme=cidadao_theme,
        css=custom_css,
        title="Cidadão.AI - Transparência Pública",
        head="""
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Plataforma de transparência pública brasileira">
        """
    ) as app:
        
        # Estado da aplicação
        current_page = gr.State("landing")
        
        # Header fixo
        with gr.Row(elem_classes="header-container"):
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="logo-container">
                    <span style="font-size: 2rem;">🇧🇷</span>
                    <span>Cidadão.AI</span>
                </div>
                """)
            
            with gr.Column(scale=1):
                with gr.Row():
                    credits_btn = gr.Button(
                        "ℹ️ Créditos", 
                        variant="secondary",
                        size="sm",
                        visible=True
                    )
                    theme_btn = gr.Button(
                        "🌙 Modo Escuro", 
                        variant="secondary", 
                        size="sm",
                        visible=True
                    )
                    back_btn = gr.Button(
                        "🏠 Voltar",
                        variant="secondary",
                        size="sm", 
                        visible=False
                    )
        
        # Container principal - Landing Page
        with gr.Column(visible=True) as landing_page:
            gr.HTML("""
            <div class="landing-hero">
                <h1 class="hero-title">Cidadão.AI</h1>
                <p class="hero-subtitle">
                    Plataforma inteligente que facilita a análise de dados públicos brasileiros. 
                    Descubra contratos suspeitos, gastos irregulares e licitações problemáticas 
                    de forma simples e rápida.
                </p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column():
                    advanced_nav_btn = gr.Button(
                        "🔍 Consulta Avançada",
                        variant="primary",
                        size="lg",
                        elem_classes="primary-button"
                    )
                
                with gr.Column():
                    chat_nav_btn = gr.Button(
                        "💬 Pergunte ao Modelo",
                        variant="secondary", 
                        size="lg",
                        elem_classes="secondary-button"
                    )
        
        # Container - Advanced Search Page
        with gr.Column(visible=False) as advanced_page:
            gr.HTML('<h2 class="page-title">🔍 Consulta Avançada</h2>')
            
            with gr.Row():
                # Sidebar
                with gr.Column(scale=1, elem_classes="sidebar"):
                    gr.HTML("<h3>≡ Menu lateral & filtros</h3>")
                    
                    data_type = gr.Radio(
                        label="📊 Tipo de Dados",
                        choices=["Contratos Públicos", "Despesas Orçamentárias", "Licitações e Pregões"],
                        value="Contratos Públicos"
                    )
                    
                    year = gr.Number(
                        label="📅 Ano",
                        value=2024,
                        minimum=2000,
                        maximum=2024
                    )
                    
                    search_term = gr.Textbox(
                        label="🔍 Busca",
                        placeholder="Digite sua consulta...",
                        lines=2
                    )
                    
                    search_btn = gr.Button(
                        "Buscar",
                        variant="primary",
                        size="lg"
                    )
                
                # Dashboard Area
                with gr.Column(scale=3, elem_classes="dashboard-area"):
                    gr.HTML("<h3>📊 Área do Dashboard</h3>")
                    gr.HTML("<p style='color: #64748B;'>(Dashboard interativo será exibido aqui)</p>")
                    
                    results = gr.Markdown(
                        value="💡 **Dica:** Use os filtros ao lado para começar sua investigação.",
                        elem_classes="results-area"
                    )
        
        # Container - Chat Page  
        with gr.Column(visible=False) as chat_page:
            gr.HTML("""
            <div class="chat-container">
                <h2 class="chat-title">💬 Pergunte ao Modelo</h2>
                <p class="chat-subtitle">
                    Faça perguntas sobre transparência pública, contratos, licitações e gastos governamentais. 
                    O modelo foi treinado para ajudar cidadãos a entender dados públicos.
                </p>
            </div>
            """)
            
            chatbot = gr.Chatbot(
                height=400,
                show_label=False,
                avatar_images=("👤", "🤖"),
                bubble_full_width=False,
                show_copy_button=True,
                elem_classes="chat-interface"
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Digite sua pergunta sobre transparência pública...",
                    show_label=False,
                    scale=4,
                    lines=1
                )
                send_btn = gr.Button(
                    "✈️ Enviar",
                    variant="primary",
                    scale=1
                )
        
        # Funções de navegação
        def show_advanced():
            return {
                landing_page: gr.Column(visible=False),
                advanced_page: gr.Column(visible=True),
                chat_page: gr.Column(visible=False),
                back_btn: gr.Button(visible=True),
                current_page: "advanced"
            }
        
        def show_chat():
            return {
                landing_page: gr.Column(visible=False),
                advanced_page: gr.Column(visible=False),
                chat_page: gr.Column(visible=True),
                back_btn: gr.Button(visible=True),
                current_page: "chat"
            }
        
        def show_landing():
            return {
                landing_page: gr.Column(visible=True),
                advanced_page: gr.Column(visible=False),
                chat_page: gr.Column(visible=False),
                back_btn: gr.Button(visible=False),
                current_page: "landing"
            }
        
        # Event handlers
        advanced_nav_btn.click(
            fn=show_advanced,
            outputs=[landing_page, advanced_page, chat_page, back_btn, current_page]
        )
        
        chat_nav_btn.click(
            fn=show_chat,
            outputs=[landing_page, advanced_page, chat_page, back_btn, current_page]
        )
        
        back_btn.click(
            fn=show_landing,
            outputs=[landing_page, advanced_page, chat_page, back_btn, current_page]
        )
        
        # Funcionalidades
        search_btn.click(
            fn=search_data,
            inputs=[data_type, year, search_term],
            outputs=[results]
        )
        
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
        
        # Placeholder para créditos e tema
        credits_btn.click(
            lambda: gr.Info("💡 Créditos: Anderson H. Silva - IFSuldeminas")
        )
        
        theme_btn.click(
            lambda: gr.Info("🌙 Modo escuro será implementado em breve")
        )
    
    return app

if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI - Gradio Nativo...")
    app = create_interface()
    app.launch(
        show_error=True,
        quiet=False,
        share=False,
        server_name="0.0.0.0",
        server_port=7860
    )