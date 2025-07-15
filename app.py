#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Landing Page Moderna
Inteligência cidadã a serviço da transparência pública
"""

import gradio as gr
import requests
import json
import time
import os
import logging
import asyncio
import httpx
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")

# CSS moderno com cores verde vibrante + amarelo dourado
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

/* Variáveis de cores inspiradas no Brasil */
:root {
    --primary-green: #16a34a;
    --vibrant-green: #22c55e;
    --golden-yellow: #f59e0b;
    --deep-gold: #d97706;
    --text-primary: #1f2937;
    --text-secondary: #6b7280;
    --text-light: #9ca3af;
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --bg-accent: #f0fdf4;
    --border-light: #e5e7eb;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Base styling */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: var(--text-primary);
    background: var(--bg-primary);
}

/* Container principal */
.gradio-container {
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 25%, #fff7ed 75%, #fef3c7 100%);
    min-height: 100vh;
    position: relative;
}

/* Padrão de fundo sutil */
.gradio-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 20% 20%, rgba(34, 197, 94, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(245, 158, 11, 0.1) 0%, transparent 50%);
    pointer-events: none;
}

/* Header principal */
.main-header {
    text-align: center;
    padding: 4rem 2rem 2rem;
    position: relative;
    z-index: 10;
}

.logo-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 2rem;
}

.logo-flag {
    font-size: 3rem;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

.main-title {
    font-size: 4rem;
    font-weight: 900;
    font-family: 'DM Sans', sans-serif;
    background: linear-gradient(135deg, var(--primary-green) 0%, var(--vibrant-green) 50%, var(--golden-yellow) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 40px rgba(22, 163, 74, 0.3);
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin-bottom: 1.5rem;
}

.main-subtitle {
    font-size: 1.5rem;
    color: var(--text-secondary);
    font-weight: 500;
    margin-bottom: 3rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.5;
}

/* Botões principais */
.buttons-container {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin: 3rem 0;
    flex-wrap: wrap;
}

.primary-button {
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    border-radius: 16px;
    text-decoration: none;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border: none;
    cursor: pointer;
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
    min-width: 240px;
    justify-content: center;
}

.btn-chat {
    background: linear-gradient(135deg, var(--primary-green) 0%, var(--vibrant-green) 100%);
    color: white;
}

.btn-chat:hover {
    background: linear-gradient(135deg, #15803d 0%, #16a34a 100%);
    transform: translateY(-2px);
    box-shadow: 0 25px 50px -12px rgba(22, 163, 74, 0.4);
}

.btn-dashboard {
    background: linear-gradient(135deg, var(--golden-yellow) 0%, var(--deep-gold) 100%);
    color: white;
}

.btn-dashboard:hover {
    background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
    transform: translateY(-2px);
    box-shadow: 0 25px 50px -12px rgba(245, 158, 11, 0.4);
}

.primary-button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
}

.primary-button:hover::before {
    left: 100%;
}

.primary-button:active {
    transform: translateY(0);
}

/* Botão flutuante de documentação */
.docs-button {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary-green) 0%, var(--vibrant-green) 100%);
    color: white;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    box-shadow: var(--shadow-xl);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
}

.docs-button:hover {
    transform: scale(1.1);
    box-shadow: 0 25px 50px -12px rgba(22, 163, 74, 0.5);
}

.docs-button:active {
    transform: scale(0.95);
}

/* Seção de recursos */
.features-section {
    padding: 4rem 2rem;
    max-width: 1200px;
    margin: 0 auto;
    position: relative;
    z-index: 10;
}

.features-title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 3rem;
    font-family: 'DM Sans', sans-serif;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 3rem;
}

.feature-card {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-md);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.feature-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-xl);
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--primary-green), var(--golden-yellow));
}

.feature-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    display: block;
}

.feature-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
}

.feature-description {
    color: var(--text-secondary);
    line-height: 1.6;
}

/* Status badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(22, 163, 74, 0.1);
    color: var(--primary-green);
    padding: 0.5rem 1rem;
    border-radius: 50px;
    font-size: 0.9rem;
    font-weight: 500;
    margin-bottom: 2rem;
    border: 1px solid rgba(22, 163, 74, 0.2);
}

.status-dot {
    width: 8px;
    height: 8px;
    background: var(--vibrant-green);
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Footer */
.footer {
    text-align: center;
    padding: 3rem 2rem;
    background: white;
    border-top: 1px solid var(--border-light);
    margin-top: 4rem;
    position: relative;
    z-index: 10;
}

.footer-content {
    max-width: 800px;
    margin: 0 auto;
}

.footer-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1rem;
    font-family: 'DM Sans', sans-serif;
}

.footer-description {
    color: var(--text-secondary);
    margin-bottom: 2rem;
    line-height: 1.6;
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 2rem;
    flex-wrap: wrap;
    margin-bottom: 2rem;
}

.footer-link {
    color: var(--primary-green);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s;
}

.footer-link:hover {
    color: var(--vibrant-green);
}

.footer-credits {
    color: var(--text-light);
    font-size: 0.9rem;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid var(--border-light);
}

/* Responsividade mobile-first */
@media (max-width: 768px) {
    .main-title {
        font-size: 2.5rem;
    }
    
    .main-subtitle {
        font-size: 1.2rem;
    }
    
    .buttons-container {
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }
    
    .features-grid {
        grid-template-columns: 1fr;
    }
    
    .docs-button {
        bottom: 1rem;
        right: 1rem;
        width: 50px;
        height: 50px;
        font-size: 1.2rem;
    }
}

@media (max-width: 480px) {
    .main-header {
        padding: 2rem 1rem;
    }
    
    .features-section {
        padding: 2rem 1rem;
    }
    
    .footer {
        padding: 2rem 1rem;
    }
}

/* Acessibilidade */
.primary-button:focus,
.docs-button:focus {
    outline: 2px solid var(--primary-green);
    outline-offset: 2px;
}

/* Animações suaves */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
"""

async def call_transparency_api(endpoint: str, params: dict = None) -> dict:
    """
    Chamada para a API do Portal da Transparência
    """
    if not TRANSPARENCY_API_KEY:
        return {"error": "API Key não configurada"}
    
    try:
        base_url = "https://api.portaldatransparencia.gov.br/api-de-dados"
        url = f"{base_url}/{endpoint}"
        
        headers = {
            "chave-api-dados": TRANSPARENCY_API_KEY,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params or {}, timeout=30)
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"error": f"Erro na API: {response.status_code} - {response.text}"}
                
    except Exception as e:
        return {"error": f"Erro de conexão: {str(e)}"}

def call_groq_api(message: str, system_prompt: str = None) -> str:
    """
    Chamada para a API do Groq
    """
    if not GROQ_API_KEY:
        return "❌ **API Key não configurada**\n\nPara usar a IA, configure a variável GROQ_API_KEY no ambiente."
    
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
            "model": "meta-llama/llama-3.1-8b-instant",
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
            return f"❌ **Erro na API**: {response.status_code}\n\n{response.text}"
            
    except Exception as e:
        return f"❌ **Erro de conexão**: {str(e)}\n\nVerifique sua conexão e tente novamente."

def chatbot():
    """
    Função para abrir o chatbot
    """
    return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)

def dashboard():
    """
    Função para abrir o dashboard
    """
    return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)

def api_portal():
    """
    Função para abrir a API do portal
    """
    return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)

def back_to_home():
    """
    Função para voltar à landing page
    """
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

def analyze_transparency_text(text: str) -> str:
    """
    Análise de transparência usando IA
    """
    if not text.strip():
        return "⚠️ **Texto vazio**\n\nPor favor, insira um texto para análise."
    
    system_prompt = """Você é o Cidadão.AI, especialista em transparência pública brasileira.

FORMATO DE RESPOSTA:
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
        user_prompt = f"""Analise o seguinte documento de transparência pública:

DOCUMENTO:
{text}

Forneça uma análise completa seguindo o formato estabelecido."""

        return call_groq_api(user_prompt, system_prompt)
        
    except Exception as e:
        return f"❌ **Erro na análise**: {str(e)}\n\nTente novamente."

def chat_with_ai(message: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
    """
    Chat com a IA
    """
    if not history:
        welcome_msg = """👋 Olá! Sou o **Cidadão.AI**, sua assistente especializada em transparência pública brasileira.

🔍 **Posso ajudar você com:**
- Análise de contratos governamentais
- Interpretação de dados de transparência
- Detecção de irregularidades
- Orientações sobre compliance público
- Análise de riscos financeiros

Como posso ajudar você hoje?"""
        history = [["", welcome_msg]]
    
    if not message.strip():
        return "", history
    
    system_prompt = """Você é o Cidadão.AI, assistente especializada em transparência pública brasileira."""

    try:
        context_messages = []
        for chat_pair in history[-5:]:
            if len(chat_pair) >= 2 and chat_pair[0]:
                context_messages.append(f"Usuário: {chat_pair[0]}")
                context_messages.append(f"Cidadão.AI: {chat_pair[1]}")
        
        if len(context_messages) > 2:
            context = "\n".join(context_messages)
            full_prompt = f"""CONTEXTO:
{context}

NOVA PERGUNTA: {message}

Responda como Cidadão.AI:"""
        else:
            full_prompt = f"""PERGUNTA: {message}

Responda como Cidadão.AI:"""
        
        ai_response = call_groq_api(full_prompt, system_prompt)
        history.append([message, ai_response])
        
        return "", history
        
    except Exception as e:
        error_msg = f"❌ Erro: {str(e)}"
        history.append([message, error_msg])
        return "", history

def query_transparency_api(query_type: str, param1: str = "", param2: str = "", param3: str = "") -> str:
    """
    Consulta à API do Portal da Transparência
    """
    if not TRANSPARENCY_API_KEY:
        return "❌ **API Key não configurada**\n\nConfigure a chave TRANSPARENCY_API_KEY no ambiente."
    
    try:
        # Executar consulta assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        params = {}
        endpoint = ""
        
        if query_type == "contratos":
            endpoint = "contratos"
            if param1:  # Código do órgão
                params["codigoOrgao"] = param1
            if param2:  # Ano
                params["ano"] = param2
            params["tamanhoPagina"] = "10"
            
        elif query_type == "despesas":
            endpoint = "despesas"
            if param1:  # Código do órgão
                params["codigoOrgao"] = param1
            if param2:  # Ano
                params["ano"] = param2
            if param3:  # Mês
                params["mes"] = param3
            params["tamanhoPagina"] = "10"
            
        elif query_type == "licitacoes":
            endpoint = "licitacoes"
            if param1:  # Código do órgão
                params["codigoOrgao"] = param1
            if param2:  # Ano
                params["ano"] = param2
            params["tamanhoPagina"] = "10"
            
        elif query_type == "servidores":
            endpoint = "servidores"
            if param1:  # Nome do servidor
                params["nome"] = param1
            if param2:  # Órgão
                params["orgao"] = param2
            params["tamanhoPagina"] = "10"
        
        # Fazer chamada à API
        result = loop.run_until_complete(call_transparency_api(endpoint, params))
        loop.close()
        
        if "error" in result:
            return f"❌ **Erro na consulta**: {result['error']}"
        
        data = result.get("data", [])
        if not data:
            return "ℹ️ **Nenhum resultado encontrado**\n\nTente ajustar os parâmetros de busca."
        
        # Formatar resultados
        formatted_result = f"✅ **Consulta realizada com sucesso!**\n\n"
        formatted_result += f"🔍 **Tipo**: {query_type.capitalize()}\n"
        formatted_result += f"📊 **Resultados encontrados**: {len(data)}\n\n"
        
        # Exibir primeiros resultados
        for i, item in enumerate(data[:5], 1):
            formatted_result += f"### 📋 **Resultado {i}**\n"
            
            if query_type == "contratos":
                formatted_result += f"**Objeto**: {item.get('objeto', 'N/A')}\n"
                formatted_result += f"**Fornecedor**: {item.get('fornecedor', {}).get('nome', 'N/A')}\n"
                formatted_result += f"**Valor**: R$ {item.get('valor', 'N/A')}\n"
                formatted_result += f"**Data**: {item.get('dataAssinatura', 'N/A')}\n"
                
            elif query_type == "despesas":
                formatted_result += f"**Favorecido**: {item.get('favorecido', {}).get('nome', 'N/A')}\n"
                formatted_result += f"**Valor**: R$ {item.get('valor', 'N/A')}\n"
                formatted_result += f"**Data**: {item.get('data', 'N/A')}\n"
                formatted_result += f"**Função**: {item.get('funcao', {}).get('nome', 'N/A')}\n"
                
            elif query_type == "licitacoes":
                formatted_result += f"**Objeto**: {item.get('objeto', 'N/A')}\n"
                formatted_result += f"**Modalidade**: {item.get('modalidade', {}).get('nome', 'N/A')}\n"
                formatted_result += f"**Valor**: R$ {item.get('valor', 'N/A')}\n"
                formatted_result += f"**Data**: {item.get('dataAbertura', 'N/A')}\n"
                
            elif query_type == "servidores":
                formatted_result += f"**Nome**: {item.get('nome', 'N/A')}\n"
                formatted_result += f"**Órgão**: {item.get('orgao', {}).get('nome', 'N/A')}\n"
                formatted_result += f"**Cargo**: {item.get('cargo', 'N/A')}\n"
                formatted_result += f"**Remuneração**: R$ {item.get('remuneracao', 'N/A')}\n"
            
            formatted_result += "\n---\n\n"
        
        if len(data) > 5:
            formatted_result += f"*... e mais {len(data) - 5} resultados encontrados*\n\n"
        
        formatted_result += "💡 **Dica**: Refine sua busca para obter resultados mais específicos."
        
        return formatted_result
        
    except Exception as e:
        return f"❌ **Erro inesperado**: {str(e)}\n\nTente novamente em alguns instantes."

def get_status_info() -> str:
    """
    Status do sistema
    """
    status_parts = []
    
    if GROQ_API_KEY:
        status_parts.append("IA Ativa")
    else:
        status_parts.append("IA Limitada")
    
    if TRANSPARENCY_API_KEY:
        status_parts.append("API Transparência Ativa")
    else:
        status_parts.append("API Transparência Limitada")
    
    return f"Sistema Online - {' | '.join(status_parts)}"

def create_main_interface():
    """
    Interface principal moderna
    """
    status_text = get_status_info()
    
    with gr.Blocks(css=custom_css, title="Cidadão.AI - Transparência Pública", theme=gr.themes.Soft()) as app:
        
        # Landing Page
        with gr.Column(visible=True, elem_id="landing-page") as landing:
            
            # Header com título centralizado
            gr.HTML(f"""
            <div class="main-header">
                <div class="logo-container">
                    <div class="logo-flag">🇧🇷</div>
                </div>
                <h1 class="main-title">cidadao.ia</h1>
                <p class="main-subtitle">Inteligência cidadã a serviço da transparência pública</p>
                <div class="status-badge">
                    <div class="status-dot"></div>
                    <span>{status_text}</span>
                </div>
            </div>
            """)
            
            # Botões principais centralizados
            with gr.Column():
                chat_btn = gr.Button("🧠 Conversar com nosso modelo", elem_classes=["primary-button", "btn-chat"], size="lg")
                dashboard_btn = gr.Button("📊 Ferramenta de análise avançada", elem_classes=["primary-button", "btn-dashboard"], size="lg")
                api_btn = gr.Button("🔍 Consultar API Portal da Transparência", elem_classes=["primary-button", "btn-dashboard"], size="lg")
            
            # Seção de recursos
            gr.HTML("""
            <div class="features-section">
                <h2 class="features-title">Recursos Principais</h2>
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🔍</div>
                        <h3 class="feature-title">Análise Inteligente</h3>
                        <p class="feature-description">
                            Detecte automaticamente irregularidades em contratos, 
                            licitações e despesas públicas usando IA avançada.
                        </p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">⚖️</div>
                        <h3 class="feature-title">Conformidade Legal</h3>
                        <p class="feature-description">
                            Verifique aderência às leis brasileiras e normas 
                            do TCU para garantir compliance total.
                        </p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">💬</div>
                        <h3 class="feature-title">Chat Especializado</h3>
                        <p class="feature-description">
                            Converse com nossa IA sobre transparência, 
                            legislação e análise de dados governamentais.
                        </p>
                    </div>
                </div>
            </div>
            """)
            
            # Footer
            gr.HTML("""
            <div class="footer">
                <div class="footer-content">
                    <h3 class="footer-title">🤖 Cidadão.AI</h3>
                    <p class="footer-description">
                        Democratizando o acesso à transparência pública através de 
                        inteligência artificial especializada em dados governamentais brasileiros.
                    </p>
                    <div class="footer-links">
                        <a href="https://github.com/anderson-ufrj/cidadao.ai" class="footer-link">GitHub</a>
                        <a href="https://portaldatransparencia.gov.br" class="footer-link">Portal da Transparência</a>
                        <a href="https://dados.gov.br" class="footer-link">Dados Abertos</a>
                    </div>
                    <div class="footer-credits">
                        <p>👨‍💻 Desenvolvido por <strong>Anderson Henrique da Silva</strong></p>
                        <p>Powered by advanced AI and machine learning</p>
                    </div>
                </div>
            </div>
            """)
        
        # Chatbot Interface
        with gr.Column(visible=False) as chatbot_interface:
            gr.HTML("""
            <div style="text-align: center; padding: 2rem;">
                <h2 style="color: #16a34a; margin-bottom: 1rem;">🧠 Conversar com nosso modelo</h2>
                <p style="color: #6b7280;">Converse com nossa IA especializada em transparência pública</p>
            </div>
            """)
            
            chatbot_component = gr.Chatbot(height=500, label="Conversação com IA")
            
            with gr.Row():
                chat_input = gr.Textbox(
                    placeholder="Digite sua pergunta sobre transparência pública...",
                    scale=4,
                    label="Sua mensagem"
                )
                send_btn = gr.Button("Enviar", scale=1, variant="primary")
            
            back_btn_1 = gr.Button("← Voltar ao Início", variant="secondary")
        
        # Dashboard Interface
        with gr.Column(visible=False) as dashboard_interface:
            gr.HTML("""
            <div style="text-align: center; padding: 2rem;">
                <h2 style="color: #f59e0b; margin-bottom: 1rem;">📊 Ferramenta de análise avançada</h2>
                <p style="color: #6b7280;">Análise especializada de documentos governamentais</p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    text_input = gr.Textbox(
                        label="Documento para análise",
                        placeholder="Cole aqui o documento governamental para análise...",
                        lines=10,
                        max_lines=20
                    )
                    
                    analyze_btn = gr.Button("🚀 Analisar", variant="primary", size="lg")
                
                with gr.Column(scale=3):
                    analysis_output = gr.Markdown(
                        label="Resultado da análise",
                        value="### 🤖 Aguardando análise...\n\nInsira um documento e clique em 'Analisar' para receber uma análise detalhada."
                    )
            
            back_btn_2 = gr.Button("← Voltar ao Início", variant="secondary")
        
        # API Portal da Transparência Interface
        with gr.Column(visible=False) as api_interface:
            gr.HTML("""
            <div style="text-align: center; padding: 2rem;">
                <h2 style="color: #16a34a; margin-bottom: 1rem;">🔍 API Portal da Transparência</h2>
                <p style="color: #6b7280;">Consulte dados reais do governo brasileiro em tempo real</p>
            </div>
            """)
            
            with gr.Tabs():
                with gr.Tab("📋 Contratos"):
                    gr.Markdown("""
                    ### Consultar Contratos Públicos
                    Busque contratos governamentais por órgão e período.
                    """)
                    
                    with gr.Row():
                        contracts_organ = gr.Textbox(
                            label="Código do Órgão",
                            placeholder="Ex: 20000 (Presidência da República)",
                            value="20000"
                        )
                        contracts_year = gr.Textbox(
                            label="Ano",
                            placeholder="Ex: 2024",
                            value="2024"
                        )
                    
                    contracts_btn = gr.Button("🔍 Consultar Contratos", variant="primary")
                    contracts_output = gr.Markdown(
                        label="Resultados",
                        value="### 📊 Pronto para consultar contratos\n\nDigite o código do órgão e ano para buscar contratos públicos."
                    )
                
                with gr.Tab("💰 Despesas"):
                    gr.Markdown("""
                    ### Consultar Despesas Públicas
                    Busque despesas governamentais por órgão, ano e mês.
                    """)
                    
                    with gr.Row():
                        expenses_organ = gr.Textbox(
                            label="Código do Órgão",
                            placeholder="Ex: 20000",
                            value="20000"
                        )
                        expenses_year = gr.Textbox(
                            label="Ano",
                            placeholder="Ex: 2024",
                            value="2024"
                        )
                        expenses_month = gr.Textbox(
                            label="Mês",
                            placeholder="Ex: 01",
                            value="01"
                        )
                    
                    expenses_btn = gr.Button("💰 Consultar Despesas", variant="primary")
                    expenses_output = gr.Markdown(
                        label="Resultados",
                        value="### 📊 Pronto para consultar despesas\n\nDigite o código do órgão, ano e mês para buscar despesas públicas."
                    )
                
                with gr.Tab("🏛️ Licitações"):
                    gr.Markdown("""
                    ### Consultar Licitações
                    Busque licitações públicas por órgão e período.
                    """)
                    
                    with gr.Row():
                        biddings_organ = gr.Textbox(
                            label="Código do Órgão",
                            placeholder="Ex: 20000",
                            value="20000"
                        )
                        biddings_year = gr.Textbox(
                            label="Ano",
                            placeholder="Ex: 2024",
                            value="2024"
                        )
                    
                    biddings_btn = gr.Button("🏛️ Consultar Licitações", variant="primary")
                    biddings_output = gr.Markdown(
                        label="Resultados",
                        value="### 📊 Pronto para consultar licitações\n\nDigite o código do órgão e ano para buscar licitações públicas."
                    )
                
                with gr.Tab("👥 Servidores"):
                    gr.Markdown("""
                    ### Consultar Servidores Públicos
                    Busque informações sobre servidores públicos federais.
                    """)
                    
                    with gr.Row():
                        servers_name = gr.Textbox(
                            label="Nome do Servidor",
                            placeholder="Ex: João Silva",
                            value=""
                        )
                        servers_organ = gr.Textbox(
                            label="Órgão",
                            placeholder="Ex: Presidência da República",
                            value=""
                        )
                    
                    servers_btn = gr.Button("👥 Consultar Servidores", variant="primary")
                    servers_output = gr.Markdown(
                        label="Resultados",
                        value="### 📊 Pronto para consultar servidores\n\nDigite o nome do servidor ou órgão para buscar informações."
                    )
            
            back_btn_3 = gr.Button("← Voltar ao Início", variant="secondary")
        
        # Botão flutuante de docs
        gr.HTML("""
        <a href="https://docs.cidadao.ai" class="docs-button" target="_blank" title="Documentação">
            📚
        </a>
        """)
        
        # Conectar eventos
        chat_btn.click(
            chatbot,
            inputs=[],
            outputs=[landing, chatbot_interface, api_interface]
        )
        
        dashboard_btn.click(
            dashboard,
            inputs=[],
            outputs=[landing, dashboard_interface, api_interface]
        )
        
        api_btn.click(
            api_portal,
            inputs=[],
            outputs=[landing, dashboard_interface, api_interface]
        )
        
        back_btn_1.click(
            back_to_home,
            inputs=[],
            outputs=[landing, chatbot_interface, api_interface]
        )
        
        back_btn_2.click(
            back_to_home,
            inputs=[],
            outputs=[landing, dashboard_interface, api_interface]
        )
        
        back_btn_3.click(
            back_to_home,
            inputs=[],
            outputs=[landing, dashboard_interface, api_interface]
        )
        
        send_btn.click(
            chat_with_ai,
            inputs=[chat_input, chatbot_component],
            outputs=[chat_input, chatbot_component]
        )
        
        chat_input.submit(
            chat_with_ai,
            inputs=[chat_input, chatbot_component],
            outputs=[chat_input, chatbot_component]
        )
        
        analyze_btn.click(
            analyze_transparency_text,
            inputs=[text_input],
            outputs=[analysis_output]
        )
        
        # Conectar eventos da API
        contracts_btn.click(
            query_transparency_api,
            inputs=[gr.State("contratos"), contracts_organ, contracts_year],
            outputs=[contracts_output]
        )
        
        expenses_btn.click(
            query_transparency_api,
            inputs=[gr.State("despesas"), expenses_organ, expenses_year, expenses_month],
            outputs=[expenses_output]
        )
        
        biddings_btn.click(
            query_transparency_api,
            inputs=[gr.State("licitacoes"), biddings_organ, biddings_year],
            outputs=[biddings_output]
        )
        
        servers_btn.click(
            query_transparency_api,
            inputs=[gr.State("servidores"), servers_name, servers_organ],
            outputs=[servers_output]
        )
    
    return app

# Lançar aplicação
if __name__ == "__main__":
    logger.info("🚀 Iniciando Cidadão.AI - Landing Page Moderna...")
    
    if GROQ_API_KEY:
        logger.info("✅ API Groq configurada")
    else:
        logger.warning("⚠️ API Groq não configurada")
    
    app = create_main_interface()
    
    app.queue(max_size=20)
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        favicon_path=None,
        auth=None
    )