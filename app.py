#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Hugging Face Spaces Interface
Plataforma de análise de transparência pública com IA especializada
"""

import gradio as gr
import requests
import json
import time
import os
import asyncio
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Modern AI Interface CSS with Glassmorphism and 2025 Design Trends
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* Base styling with modern variables */
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    --glass-bg: rgba(255, 255, 255, 0.1);
    --glass-border: rgba(255, 255, 255, 0.2);
    --shadow-glass: 0 8px 32px rgba(31, 38, 135, 0.37);
    --text-primary: #1a1a1a;
    --text-secondary: #6b7280;
    --surface-glass: rgba(255, 255, 255, 0.15);
}

/* Global container with enhanced design */
.gradio-container {
    max-width: 1400px !important;
    margin: auto !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
}

/* Animated background particles */
.gradio-container::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%);
    pointer-events: none;
    z-index: -1;
}

/* Main header with glassmorphism */
.main-header {
    text-align: center;
    padding: 3rem 2rem;
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    margin: 2rem 0;
    box-shadow: var(--shadow-glass);
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transform: rotate(45deg);
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0% { transform: translateX(-100%) rotate(45deg); }
    100% { transform: translateX(100%) rotate(45deg); }
}

.main-title {
    font-size: 3.5rem;
    font-weight: 900;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
    letter-spacing: -0.02em;
    position: relative;
    z-index: 2;
}

.main-subtitle {
    font-size: 1.4rem;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 400;
    margin-bottom: 1.5rem;
    position: relative;
    z-index: 2;
}

/* Enhanced status card with glassmorphism */
.status-card {
    background: var(--surface-glass);
    backdrop-filter: blur(15px);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    position: relative;
    z-index: 2;
}

/* Bento grid layout for main content */
.gradio-tabs {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 0;
    margin: 2rem 0;
    box-shadow: var(--shadow-glass);
    overflow: hidden;
}

.gradio-tabitem {
    background: transparent;
    padding: 2rem;
}

/* Enhanced tab buttons */
.gradio-tabs > .tab-nav {
    background: var(--surface-glass);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--glass-border);
    padding: 0.5rem;
}

.gradio-tabs > .tab-nav > button {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.8);
    font-weight: 500;
    padding: 1rem 2rem;
    margin: 0 0.5rem;
    border-radius: 12px;
    transition: all 0.3s ease;
    font-size: 1.1rem;
}

.gradio-tabs > .tab-nav > button:hover {
    background: var(--surface-glass);
    color: white;
    transform: translateY(-2px);
}

.gradio-tabs > .tab-nav > button.selected {
    background: var(--accent-gradient);
    color: white;
    box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
}

/* Modern input fields with glassmorphism */
.gradio-textbox, .gradio-textarea {
    background: var(--surface-glass) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 16px !important;
    color: var(--text-primary) !important;
    font-size: 1rem !important;
    padding: 1rem !important;
    transition: all 0.3s ease !important;
}

.gradio-textbox:focus, .gradio-textarea:focus {
    border-color: rgba(79, 172, 254, 0.5) !important;
    box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.1) !important;
    transform: translateY(-2px) !important;
}

/* Enhanced buttons with micro-interactions */
.gradio-button {
    background: var(--accent-gradient) !important;
    border: none !important;
    border-radius: 16px !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 1rem 2rem !important;
    font-size: 1.1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4) !important;
    cursor: pointer !important;
}

.gradio-button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(79, 172, 254, 0.6) !important;
}

.gradio-button:active {
    transform: translateY(-1px) !important;
}

/* Analysis output with modern card design */
.analysis-output {
    background: var(--surface-glass);
    backdrop-filter: blur(15px);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 2rem;
    margin: 1.5rem 0;
    box-shadow: var(--shadow-glass);
    position: relative;
    overflow: hidden;
}

.analysis-output::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: var(--accent-gradient);
    border-radius: 2px;
}

/* Chat interface with progressive blur */
.gradio-chatbot {
    background: var(--surface-glass) !important;
    backdrop-filter: blur(15px) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 20px !important;
    padding: 1rem !important;
    box-shadow: var(--shadow-glass) !important;
}

.chat-message {
    margin: 1rem 0;
    padding: 1.5rem;
    border-radius: 16px;
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    transition: all 0.3s ease;
}

.chat-message:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.chat-user {
    background: linear-gradient(135deg, rgba(79, 172, 254, 0.2), rgba(0, 242, 254, 0.2));
    margin-left: 2rem;
    border-left: 3px solid #4facfe;
}

.chat-ai {
    background: linear-gradient(135deg, rgba(240, 147, 251, 0.2), rgba(245, 87, 108, 0.2));
    margin-right: 2rem;
    border-left: 3px solid #f093fb;
}

/* Enhanced markdown styling */
.markdown-content h1, .markdown-content h2, .markdown-content h3 {
    color: var(--text-primary);
    font-weight: 700;
    margin-bottom: 1rem;
}

.markdown-content p {
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 1rem;
}

/* Loading animations */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.loading {
    animation: pulse 2s infinite;
}

/* Responsive design */
@media (max-width: 768px) {
    .gradio-container {
        padding: 1rem;
    }
    
    .main-header {
        padding: 2rem 1rem;
    }
    
    .main-title {
        font-size: 2.5rem;
    }
    
    .main-subtitle {
        font-size: 1.2rem;
    }
    
    .gradio-tabitem {
        padding: 1rem;
    }
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--surface-glass);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: var(--accent-gradient);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--primary-gradient);
}

/* Accessibility improvements */
.gradio-button:focus,
.gradio-textbox:focus,
.gradio-textarea:focus {
    outline: 2px solid rgba(79, 172, 254, 0.5);
    outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    :root {
        --glass-bg: rgba(255, 255, 255, 0.9);
        --glass-border: rgba(0, 0, 0, 0.3);
        --text-primary: #000000;
        --text-secondary: #333333;
    }
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
"""

def call_groq_api(message: str, system_prompt: str = None) -> str:
    """
    Chamada real para a API do Groq
    """
    if not GROQ_API_KEY:
        return "❌ **API Key não configurada**\\n\\nPara usar a IA, configure a variável GROQ_API_KEY no ambiente."
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user", 
            "content": message
        })
        
        data = {
            "model": "mixtral-8x7b-32768",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": False
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"❌ **Erro na API**: {response.status_code}\\n\\n{response.text}"
            
    except Exception as e:
        return f"❌ **Erro de conexão**: {str(e)}\\n\\nVerifique sua conexão e tente novamente."

def analyze_transparency_text(text: str) -> str:
    """
    Análise especializada usando IA real
    """
    if not text.strip():
        return "⚠️ **Texto vazio**\\n\\nPor favor, insira um texto para análise."
    
    # Prompt especializado para análise de transparência
    system_prompt = """Você é o Cidadão.AI, um sistema especializado em análise de transparência pública brasileira.

MISSÃO: Analisar documentos governamentais para detectar anomalias, avaliar riscos financeiros e verificar conformidade legal.

FORMATO DE RESPOSTA:
Use sempre este formato estruturado:

🚨 **NÍVEL DE RISCO**: [Baixo/Médio/Alto/Crítico]

🔍 **ANÁLISE DE ANOMALIAS**:
[Descreva padrões suspeitos encontrados]

💰 **ANÁLISE FINANCEIRA**:
[Avalie valores, preços e questões econômicas]

⚖️ **CONFORMIDADE LEGAL**:
[Verifique aderência às normas brasileiras]

📋 **RECOMENDAÇÕES**:
[Sugira ações específicas]

🎯 **CONFIANÇA**: [Porcentagem] - [Justificativa]"""

    try:
        user_prompt = f"""Analise o seguinte documento/situação de transparência pública:

DOCUMENTO PARA ANÁLISE:
{text}

Por favor, forneça uma análise completa seguindo o formato estabelecido."""

        return call_groq_api(user_prompt, system_prompt)
        
    except Exception as e:
        return f"❌ **Erro na análise**: {str(e)}\\n\\nTente novamente em alguns instantes."

def chat_with_ai(message: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
    """
    Chat conversacional com a IA - Formato Gradio compatível
    """
    # Inicializar história se vazia
    if not history:
        welcome_msg = """👋 Hello! I'm **Cidadão.AI**, your specialized AI assistant for Brazilian public transparency and government accountability.

🔍 **I can help you with:**
- Government contract and procurement analysis
- Public transparency portal data interpretation
- Anomaly detection in public spending
- Legal compliance guidance for public administration
- Financial risk assessment in government operations

🚀 **Advanced capabilities:**
- Real-time document analysis
- Pattern recognition in public data
- Regulatory compliance verification
- Anti-corruption insights

How can I assist you today with public transparency analysis?"""
        history = [["", welcome_msg]]
    
    if not message.strip():
        return "", history
    
    # Sistema especializado para chat
    system_prompt = """Você é o Cidadão.AI, assistente especializada em transparência pública brasileira."""

    try:
        # Construir contexto do histórico (formato [user, assistant])
        context_messages = []
        for chat_pair in history[-5:]:  # Últimas 5 conversas
            if len(chat_pair) >= 2 and chat_pair[0]:  # Se tem pergunta do usuário
                context_messages.append(f"Usuário: {chat_pair[0]}")
                context_messages.append(f"Cidadão.AI: {chat_pair[1]}")
        
        if len(context_messages) > 2:  # Mais que só a mensagem inicial
            context = "\\n".join(context_messages)
            full_prompt = f"""CONTEXTO DA CONVERSA:
{context}

NOVA PERGUNTA: {message}

Responda como Cidadão.AI, mantendo o contexto da conversa:"""
        else:
            full_prompt = f"""PERGUNTA: {message}

Responda como Cidadão.AI, assistente de transparência pública:"""
        
        ai_response = call_groq_api(full_prompt, system_prompt)
        
        # Adicionar nova conversa no formato [user, assistant]
        history.append([message, ai_response])
        
        return "", history
        
    except Exception as e:
        error_msg = f"❌ Erro: {str(e)}"
        history.append([message, error_msg])
        return "", history

def get_status_info() -> Tuple[str, str]:
    """
    Informações de status do sistema
    """
    status_emoji = "✅"
    status_text = "Sistema Online"
    
    if GROQ_API_KEY:
        status_text += " - IA Ativa (Groq)"
    else:
        status_emoji = "⚠️"
        status_text += " - IA Limitada (sem API key)"
    
    return status_emoji, status_text

def create_main_interface():
    """
    Interface principal do Gradio
    """
    status_emoji, status_text = get_status_info()
    
    with gr.Blocks(css=custom_css, title="Cidadão.AI - Transparência Pública", theme=gr.themes.Soft()) as app:
        
        # Enhanced header with modern design
        gr.HTML(f"""
        <div class="main-header">
            <div class="main-title">🇧🇷 Cidadão.AI</div>
            <div class="main-subtitle">Advanced AI-powered transparency platform for democratizing access to Brazilian public data</div>
            <div class="status-card">
                <div style="display: flex; align-items: center; justify-content: center; gap: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite;"></div>
                        <span style="font-weight: 500; color: rgba(255, 255, 255, 0.9);">{status_emoji} {status_text}</span>
                    </div>
                    <div style="height: 20px; width: 1px; background: rgba(255, 255, 255, 0.3);"></div>
                    <div style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7);">
                        🚀 Production Ready | 🔒 Secure | ⚡ Real-time Analysis
                    </div>
                </div>
            </div>
        </div>
        """)
        
        with gr.Tabs() as tabs:
            
            # Tab 1: Advanced Document Analysis
            with gr.Tab("🔍 Transparency Analysis"):
                gr.Markdown("""
                ### 📊 AI-Powered Document Analysis
                
                **Transform government documents into actionable insights**
                
                Our advanced AI system analyzes contracts, procurement data, public expenses, and legal documents to detect anomalies, assess financial risks, and ensure regulatory compliance with Brazilian public administration standards.
                
                **Key Features:**
                - 🚨 Anomaly detection in public contracts
                - 💰 Financial risk assessment
                - ⚖️ Legal compliance verification
                - 📈 Pattern recognition and trend analysis
                """)
                
                with gr.Row():
                    with gr.Column(scale=2):
                        text_input = gr.Textbox(
                            label="📄 Government Document Input",
                            placeholder="Paste your government document here - contracts, procurement data, public expenses, or any official document for AI-powered analysis...",
                            lines=10,
                            max_lines=20,
                            elem_classes=["modern-input"]
                        )
                        
                        analyze_btn = gr.Button("🚀 Analyze with AI", variant="primary", size="lg")
                    
                    with gr.Column(scale=3):
                        analysis_output = gr.Markdown(
                            label="📊 Analysis Results",
                            value="""
## 🤖 **Cidadão.AI Ready for Analysis**

**Welcome to the next generation of government transparency analysis**

🔍 **What you can expect:**
- Comprehensive risk assessment
- Detailed anomaly detection
- Legal compliance verification
- Financial pattern analysis
- Actionable recommendations

**Getting started:** Insert your government document in the input field and click "Analyze with AI" to receive a comprehensive analysis powered by advanced machine learning algorithms.

*Your document will be processed securely and analyzed in real-time.*
                            """,
                            elem_classes=["analysis-output"]
                        )
                
                # Conectar análise
                analyze_btn.click(
                    analyze_transparency_text,
                    inputs=[text_input],
                    outputs=[analysis_output]
                )
            
            # Tab 2: Interactive AI Assistant
            with gr.Tab("💬 AI Assistant"):
                gr.Markdown("""
                ### 🤖 Interactive AI Assistant
                
                **Get instant answers about public transparency, government contracts, and Brazilian public data**
                
                Ask questions about procurement processes, legal compliance, financial analysis, or any aspect of government transparency. Our AI assistant provides expert guidance based on Brazilian public administration standards.
                
                **Examples you can ask:**
                - *"How do I identify red flags in a government contract?"*
                - *"What are the legal requirements for public procurement in Brazil?"*
                - *"Explain the transparency portal data structure"*
                - *"How to analyze suspicious spending patterns?"*
                """)
                
                chatbot = gr.Chatbot(
                    label="AI Assistant Conversation",
                    height=600,
                    elem_classes=["chat-container", "modern-chat"]
                )
                
                with gr.Row():
                    chat_input = gr.Textbox(
                        label="💬 Your Question",
                        placeholder="Ask anything about public transparency, government contracts, or data analysis...",
                        scale=4,
                        elem_classes=["modern-input"]
                    )
                    chat_btn = gr.Button("🚀 Send", scale=1, variant="primary")
                
                # Conectar chat
                chat_btn.click(
                    chat_with_ai,
                    inputs=[chat_input, chatbot],
                    outputs=[chat_input, chatbot]
                )
                
                chat_input.submit(
                    chat_with_ai,
                    inputs=[chat_input, chatbot], 
                    outputs=[chat_input, chatbot]
                )
        
        # Modern footer with glassmorphism
        gr.HTML("""
        <div style="
            text-align: center; 
            padding: 2rem; 
            margin-top: 3rem;
            background: var(--surface-glass);
            backdrop-filter: blur(15px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            color: rgba(255, 255, 255, 0.9);
        ">
            <div style="margin-bottom: 1rem;">
                <h3 style="margin: 0; font-size: 1.4rem; font-weight: 700; color: white;">
                    🤖 Cidadão.AI
                </h3>
                <p style="margin: 0.5rem 0; font-size: 1rem; color: rgba(255, 255, 255, 0.8);">
                    Democratizing public transparency through advanced AI technology
                </p>
            </div>
            
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin: 1.5rem 0;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: #10b981;">🚀</span>
                    <span style="font-size: 0.9rem;">Production Ready</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: #3b82f6;">🔒</span>
                    <span style="font-size: 0.9rem;">Enterprise Security</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: #8b5cf6;">⚡</span>
                    <span style="font-size: 0.9rem;">Real-time Analysis</span>
                </div>
            </div>
            
            <div style="border-top: 1px solid rgba(255, 255, 255, 0.2); padding-top: 1rem; margin-top: 1rem;">
                <p style="margin: 0; font-size: 0.9rem; color: rgba(255, 255, 255, 0.7);">
                    👨‍💻 Developed by <strong style="color: white;">Anderson Henrique da Silva</strong>
                </p>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; color: rgba(255, 255, 255, 0.6);">
                    Powered by advanced machine learning and natural language processing
                </p>
            </div>
        </div>
        """)
    
    return app

# Criar e lançar aplicação
if __name__ == "__main__":
    logger.info("🚀 Iniciando Cidadão.AI v2.1 - Sistema de Transparência...")
    
    # Verificar configuração
    if GROQ_API_KEY:
        logger.info("✅ API Groq configurada")
    else:
        logger.warning("⚠️ API Groq não configurada - funcionalidade limitada")
    
    # Criar interface
    app = create_main_interface()
    
    # Configurar e lançar (SEM concurrency_count)
    app.queue(max_size=20)
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        favicon_path=None,
        auth=None
    )