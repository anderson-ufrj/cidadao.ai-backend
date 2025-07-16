#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Portal da Transparência
Sistema de consulta aos dados do Portal da Transparência
VERSÃO CORRIGIDA - Navegação baseada em mockups
"""

import gradio as gr
import os
import time
import asyncio
import httpx
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configurar variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def create_landing_page():
    """Landing page baseada no mockup 1"""
    return """
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
                <button class="btn btn-primary" id="btnAdvanced">
                    <span>🔍</span> Consulta Avançada
                </button>
                <button class="btn btn-secondary" id="btnChat">
                    <span>💬</span> Pergunte ao Modelo
                </button>
            </div>
        </div>
    </div>
    """

def create_advanced_search_page():
    """Página de consulta avançada baseada no mockup 2"""
    return """
    <div class="header">
        <div class="logo">
            <span style="font-size: 2rem;">🇧🇷</span>
            <span class="logo-text">Cidadão.AI</span>
        </div>
        <div style="display: flex; gap: 1rem; align-items: center;">
            <button class="btn btn-outline" onclick="navigateToHome()" style="padding: 0.5rem 1rem; font-size: 0.9rem;">
                <span>🏠</span> Voltar
            </button>
            <button class="theme-toggle" onclick="toggleTheme()" id="theme-toggle-btn-2">
                <span>🌙</span> Modo Escuro
            </button>
        </div>
    </div>
    
    <div style="padding-top: 100px;">
        <h2 style="text-align: center; margin-bottom: 2rem;">🔍 Consulta Avançada</h2>
        <div style="display: flex; gap: 2rem; max-width: 1200px; margin: 0 auto;">
            <div style="flex: 1; background: var(--bg-secondary); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-color);">
                <h3 style="margin-bottom: 1.5rem;">≡ Menu lateral & filtros</h3>
                <p style="color: var(--text-secondary); margin-bottom: 1rem;">Controles aparecerão aqui quando implementados</p>
                <div style="background: var(--bg-primary); padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color);">
                    <p style="font-size: 0.9rem; color: var(--text-secondary);">📊 Filtros de dados</p>
                    <p style="font-size: 0.9rem; color: var(--text-secondary);">📅 Seletor de período</p>
                    <p style="font-size: 0.9rem; color: var(--text-secondary);">🔍 Busca avançada</p>
                </div>
            </div>
            <div style="flex: 3; background: var(--bg-secondary); padding: 2rem; border-radius: 12px; border: 1px solid var(--border-color); min-height: 400px;">
                <h3 style="margin-bottom: 1.5rem;">📊 Área do Dashboard</h3>
                <p style="color: var(--text-secondary); margin-bottom: 1rem;">(na página inicial, descrição e como usar, guiado, explicando como usar)</p>
                <div style="background: var(--bg-primary); padding: 2rem; border-radius: 8px; border: 1px solid var(--border-color); text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">📈</div>
                    <p style="color: var(--text-secondary);">Dashboard será exibido aqui</p>
                </div>
                <p style="color: var(--text-secondary); margin-top: 1rem; font-size: 0.9rem;">(créditos)</p>
            </div>
        </div>
    </div>
    """

def create_chat_page():
    """Página de chat baseada no mockup 3"""
    return """
    <div class="header">
        <div class="logo">
            <span style="font-size: 2rem;">🇧🇷</span>
            <span class="logo-text">Cidadão.AI</span>
        </div>
        <div style="display: flex; gap: 1rem; align-items: center;">
            <button class="btn btn-outline" onclick="navigateToHome()" style="padding: 0.5rem 1rem; font-size: 0.9rem;">
                <span>🏠</span> Voltar
            </button>
            <button class="theme-toggle" onclick="toggleTheme()" id="theme-toggle-btn-3">
                <span>🌙</span> Modo Escuro
            </button>
        </div>
    </div>
    
    <div style="padding-top: 100px; text-align: center;">
        <h2 style="margin-bottom: 2rem;">💬 Pergunte ao Modelo</h2>
        <p style="color: var(--text-secondary); margin-bottom: 2rem; max-width: 600px; margin-left: auto; margin-right: auto;">
            Exemplos do que pode ser perguntado: breve descrição de como funciona
        </p>
        <div style="max-width: 800px; margin: 0 auto; background: var(--bg-secondary); padding: 2rem; border-radius: 12px; border: 1px solid var(--border-color);">
            <div style="background: var(--bg-primary); padding: 1.5rem; border-radius: 8px; border: 1px solid var(--border-color); min-height: 300px; margin-bottom: 1rem;">
                <p style="color: var(--text-secondary); text-align: center;">💬 Área de conversação</p>
            </div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <div style="flex: 1; background: var(--bg-primary); padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color);">
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">Caixa de texto dinâmica p/ perguntas</p>
                </div>
                <button class="btn btn-primary" style="padding: 1rem 2rem;">
                    <span>✈️</span> Enviar
                </button>
            </div>
        </div>
    </div>
    """

# Função de chat simples
def chat_fn(message, history):
    """Função de chat básica"""
    if not message:
        return history, ""
    
    # Simular resposta
    response = f"Entendi sua pergunta sobre: '{message}'. Esta é uma resposta simulada do modelo de transparência pública."
    
    history.append((message, response))
    return history, ""

# Função de busca simples
def search_data(data_type, year, search_term):
    """Função de busca básica"""
    if not search_term:
        return "Digite um termo de busca para começar..."
    
    return f"""
    <div class="search-results">
        <h3>🔍 Resultados para: "{search_term}"</h3>
        <p><strong>Tipo:</strong> {data_type}</p>
        <p><strong>Ano:</strong> {year}</p>
        <div style="background: var(--bg-primary); padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color); margin-top: 1rem;">
            <p>Resultados da busca aparecerão aqui...</p>
        </div>
    </div>
    """

def create_interface():
    """Cria a interface principal"""
    
    # CSS da aplicação
    css_content = """
    :root {
        --primary-blue: #0066CC;
        --primary-green: #00A86B;
        --bg-primary: #FFFFFF;
        --bg-secondary: #F8FAFC;
        --text-primary: #0F172A;
        --text-secondary: #64748B;
        --border-color: #E2E8F0;
    }
    
    .header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 80px;
        background: var(--bg-primary);
        border-bottom: 1px solid var(--border-color);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
        z-index: 1000;
    }
    
    .logo {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-green);
    }
    
    .landing-page {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 2rem;
        text-align: center;
    }
    
    .hero-content {
        max-width: 800px;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        color: var(--primary-green);
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--text-secondary);
        margin-bottom: 3rem;
        line-height: 1.6;
    }
    
    .action-buttons {
        display: flex;
        gap: 1.5rem;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .btn {
        padding: 1.2rem 2.5rem;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        min-width: 200px;
        justify-content: center;
        pointer-events: auto !important;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, var(--primary-blue), #4DA6FF);
        color: white;
        box-shadow: 0 4px 15px rgba(0, 102, 204, 0.3);
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 102, 204, 0.4);
    }
    
    .btn-secondary {
        background: linear-gradient(135deg, var(--primary-green), #00D084);
        color: white;
        box-shadow: 0 4px 15px rgba(0, 168, 107, 0.3);
    }
    
    .btn-secondary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 168, 107, 0.4);
    }
    
    .btn-outline {
        background: transparent;
        border: 2px solid var(--border-color);
        color: var(--text-primary);
    }
    
    .btn-outline:hover {
        background: var(--bg-secondary);
        transform: translateY(-1px);
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
        background: var(--bg-secondary);
        transform: translateY(-1px);
    }
    
    .gradio-container {
        max-width: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    """
    
    # JavaScript para navegação
    js_content = """
    // Variáveis globais
    let currentPage = 'landing';
    
    // Funções de navegação
    function navigateToHome() {
        console.log('Navegando para home');
        // Trigger o botão oculto do Gradio
        const homeBtn = document.querySelector('[data-testid="navigate-home"]');
        if (homeBtn) homeBtn.click();
    }
    
    function navigateToAdvanced() {
        console.log('Navegando para consulta avançada');
        // Trigger o botão oculto do Gradio
        const advBtn = document.querySelector('[data-testid="navigate-advanced"]');
        if (advBtn) advBtn.click();
    }
    
    function navigateToChat() {
        console.log('Navegando para chat');
        // Trigger o botão oculto do Gradio
        const chatBtn = document.querySelector('[data-testid="navigate-chat"]');
        if (chatBtn) chatBtn.click();
    }
    
    // Configurar navegação dos botões
    function setupNavigation() {
        setTimeout(function() {
            const btnAdvanced = document.getElementById('btnAdvanced');
            const btnChat = document.getElementById('btnChat');
            
            if (btnAdvanced) {
                btnAdvanced.addEventListener('click', function(e) {
                    e.preventDefault();
                    navigateToAdvanced();
                });
            }
            
            if (btnChat) {
                btnChat.addEventListener('click', function(e) {
                    e.preventDefault();
                    navigateToChat();
                });
            }
        }, 500);
    }
    
    // Inicializar quando a página carregar
    document.addEventListener('DOMContentLoaded', setupNavigation);
    
    // Observar mudanças no DOM
    const observer = new MutationObserver(function(mutations) {
        setupNavigation();
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Função de toggle de tema (básica)
    function toggleTheme() {
        console.log('Toggle theme');
        // Implementar mudança de tema aqui
    }
    
    // Função de créditos (básica)
    function showCreditsModal() {
        console.log('Show credits modal');
        // Implementar modal de créditos aqui
    }
    """
    
    with gr.Blocks(
        css=css_content,
        title="Cidadão.AI",
        theme=gr.themes.Base(),
        head=f"""
        <style>body {{ margin: 0; padding: 0; }}</style>
        <script>{js_content}</script>
        """
    ) as app:
        
        # Container principal - navegação por troca de conteúdo
        main_content = gr.HTML(value=create_landing_page(), elem_id="main-content")
        
        # Container oculto para controles da consulta avançada
        with gr.Row(visible=False, elem_id="advanced-controls") as advanced_controls:
            with gr.Column(scale=1):
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
                
                search_btn = gr.Button("Buscar", variant="primary")
                
            with gr.Column(scale=3):
                results = gr.HTML(value="<p>Resultados aparecerão aqui...</p>")
        
        # Container oculto para chat
        with gr.Row(visible=False, elem_id="chat-controls") as chat_controls:
            with gr.Column():
                chatbot = gr.Chatbot(
                    height=400,
                    show_label=False,
                    avatar_images=("👤", "🤖")
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Digite sua pergunta sobre transparência pública...",
                        show_label=False,
                        scale=4,
                        lines=1
                    )
                    send_btn = gr.Button("Enviar", variant="primary", scale=1)
        
        # Função para navegar para consulta avançada
        def navigate_to_advanced():
            return {
                main_content: gr.HTML(value=create_advanced_search_page()),
                advanced_controls: gr.Row(visible=True),
                chat_controls: gr.Row(visible=False)
            }
        
        # Função para navegar para chat
        def navigate_to_chat():
            return {
                main_content: gr.HTML(value=create_chat_page()),
                advanced_controls: gr.Row(visible=False), 
                chat_controls: gr.Row(visible=True)
            }
        
        # Função para voltar ao início
        def navigate_to_home():
            return {
                main_content: gr.HTML(value=create_landing_page()),
                advanced_controls: gr.Row(visible=False),
                chat_controls: gr.Row(visible=False)
            }
        
        # Botões ocultos para navegação
        nav_advanced = gr.Button("", visible=False, elem_id="navigate-advanced")
        nav_chat = gr.Button("", visible=False, elem_id="navigate-chat")  
        nav_home = gr.Button("", visible=False, elem_id="navigate-home")
        
        # Conectar navegação
        nav_advanced.click(
            fn=navigate_to_advanced,
            inputs=[],
            outputs=[main_content, advanced_controls, chat_controls]
        )
        
        nav_chat.click(
            fn=navigate_to_chat,
            inputs=[],
            outputs=[main_content, advanced_controls, chat_controls]
        )
        
        nav_home.click(
            fn=navigate_to_home,
            inputs=[],
            outputs=[main_content, advanced_controls, chat_controls]
        )
        
        # Conectar funcionalidades
        search_btn.click(
            fn=search_data,
            inputs=[data_type, year, search_term],
            outputs=[results]
        )
        
        msg.submit(fn=chat_fn, inputs=[msg, chatbot], outputs=[chatbot, msg])
        send_btn.click(fn=chat_fn, inputs=[msg, chatbot], outputs=[chatbot, msg])
    
    return app

# Executar aplicação
if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI - Versão Corrigida...")
    app = create_interface()
    app.launch(
        show_error=True,
        quiet=False,
        share=False,
        server_name="0.0.0.0",
        server_port=7860
    )