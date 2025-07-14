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

# CSS moderno para o Spaces
custom_css = """
/* Estilo moderno para o Cidadão.AI */
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header principal */
.main-header {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg, #0049A0 0%, #FFB74D 50%, #00873D 100%);
    color: white;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(0, 73, 160, 0.3);
}

.main-title {
    font-size: 3rem;
    font-weight: 900;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.main-subtitle {
    font-size: 1.2rem;
    opacity: 0.95;
    font-weight: 300;
}

/* Status do modelo */
.status-card {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
}

/* Análise container */
.analysis-output {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 1.5rem;
    margin: 1rem 0;
    border-left: 4px solid #0049A0;
    font-family: 'Inter', sans-serif;
}

/* Chat interface */
.chat-message {
    margin: 1rem 0;
    padding: 1rem;
    border-radius: 10px;
}

.chat-user {
    background: #e3f2fd;
    text-align: right;
}

.chat-ai {
    background: #f1f8e9;
    text-align: left;
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

def chat_with_ai(message: str, history: List[Dict]) -> Tuple[str, List[Dict]]:
    """
    Chat conversacional com a IA
    """
    # Inicializar história se vazia
    if not history:
        history = [{"role": "assistant", "content": """👋 Olá! Sou o **Cidadão.AI**, sua assistente especializada em transparência pública brasileira.

🔍 **Posso ajudar você com:**
- Análise de contratos e licitações
- Explicação de dados do Portal da Transparência  
- Detecção de irregularidades
- Orientações sobre compliance público

Como posso ajudar você hoje?"""}]
    
    if not message.strip():
        return "", history
    
    # Sistema especializado para chat
    system_prompt = """Você é o Cidadão.AI, assistente especializada em transparência pública brasileira."""

    try:
        context_messages = []
        
        # Adicionar histórico recente
        for msg in history[-10:]:
            if msg["role"] == "user":
                context_messages.append(f"Usuário: {msg['content']}")
            elif msg["role"] == "assistant":
                context_messages.append(f"Cidadão.AI: {msg['content']}")
        
        if len(context_messages) > 1:  # Mais que só a mensagem inicial
            context = "\\n".join(context_messages)
            full_prompt = f"""CONTEXTO DA CONVERSA:
{context}

NOVA PERGUNTA: {message}

Responda como Cidadão.AI, mantendo o contexto da conversa:"""
        else:
            full_prompt = f"""PERGUNTA: {message}

Responda como Cidadão.AI, assistente de transparência pública:"""
        
        ai_response = call_groq_api(full_prompt, system_prompt)
        
        # Atualizar histórico
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": ai_response})
        
        return "", history
        
    except Exception as e:
        error_msg = f"❌ Erro: {str(e)}"
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})
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
        
        # Header principal
        gr.HTML(f"""
        <div class="main-header">
            <div class="main-title">🇧🇷 cidadão.ai</div>
            <div class="main-subtitle">Inteligência cidadã para uma nova era de transparência pública</div>
            <div class="status-card">
                <strong>{status_emoji} Status:</strong> {status_text}
            </div>
        </div>
        """)
        
        with gr.Tabs() as tabs:
            
            # Aba 1: Análise de Texto
            with gr.Tab("🔍 Análise de Transparência"):
                gr.Markdown("""
                ### 📝 Análise Especializada de Documentos
                
                Cole aqui textos de contratos, licitações, despesas ou qualquer documento público para análise especializada.
                """)
                
                with gr.Row():
                    with gr.Column(scale=2):
                        text_input = gr.Textbox(
                            label="📄 Documento para Análise",
                            placeholder="Cole aqui o texto de um contrato, despesa, licitação ou qualquer documento público...",
                            lines=8,
                            max_lines=15
                        )
                        
                        analyze_btn = gr.Button("🔍 Analisar com IA", variant="primary", size="lg")
                    
                    with gr.Column(scale=3):
                        analysis_output = gr.Markdown(
                            label="📊 Resultado da Análise",
                            value="""🤖 **Cidadão.AI pronto para análise!**

Insira um documento ou texto ao lado e clique em "Analisar" para receber análise completa.""",
                            elem_classes=["analysis-output"]
                        )
                
                # Conectar análise
                analyze_btn.click(
                    analyze_transparency_text,
                    inputs=[text_input],
                    outputs=[analysis_output]
                )
            
            # Aba 2: Chat Interativo
            with gr.Tab("💬 Chat com IA"):
                gr.Markdown("""
                ### 🤖 Converse com o Cidadão.AI
                
                Faça perguntas sobre transparência pública, contratos, licitações e dados governamentais.
                """)
                
                chatbot = gr.Chatbot(
                    label="Conversa com Cidadão.AI",
                    height=500,
                    type="messages",
                    elem_classes=["chat-container"]
                )
                
                with gr.Row():
                    chat_input = gr.Textbox(
                        label="💬 Sua pergunta",
                        placeholder="Digite sua pergunta sobre transparência pública...",
                        scale=4
                    )
                    chat_btn = gr.Button("📤", scale=1, variant="primary")
                
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
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; padding: 1rem; color: #666; font-size: 0.9rem; border-top: 1px solid #eee; margin-top: 2rem;">
            <p><strong>🤖 Cidadão.AI</strong> - Democratizando a transparência pública com IA</p>
            <p>👨‍💻 Desenvolvido por <strong>Anderson Henrique da Silva</strong></p>
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