#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Interface Moderna de IA para Transparência Pública
Sistema avançado de análise com design inspirado nas melhores interfaces de IA
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

# Import local modules for real data integration
try:
    import sys
    sys.path.append('/home/anderson-henrique/Documentos/cidadao.ai')
    from src.tools.data_integrator import DataIntegrator
    from src.tools.api_test import quick_api_test
    from src.tools.ai_analyzer import AIAnalyzer
    REAL_DATA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Real data integration not available: {e}")
    REAL_DATA_AVAILABLE = False

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# CSS ultramoderno inspirado em ChatGPT/Claude/Perplexity
custom_css = """
/* Reset e configurações base */
* {
    box-sizing: border-box;
}

.gradio-container {
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Segoe UI', Roboto, sans-serif;
    background: #0a0a0a;
    min-height: 100vh;
}

/* Layout principal */
.main-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background: #0a0a0a;
}

/* Header minimalista */
.modern-header {
    background: rgba(255, 255, 255, 0.03);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding: 20px 0;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    position: sticky;
    top: 0;
    z-index: 100;
}

.header-content {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.logo-section {
    display: flex;
    align-items: center;
    gap: 16px;
}

.logo-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: white;
    font-weight: bold;
}

.logo-text {
    color: #ffffff;
    font-size: 20px;
    font-weight: 600;
    letter-spacing: -0.5px;
}

.logo-subtitle {
    color: rgba(255, 255, 255, 0.6);
    font-size: 13px;
    font-weight: 400;
    margin-top: 2px;
}

/* Status badge */
.status-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    color: #10b981;
    font-weight: 500;
}

.status-dot {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

/* Hero section */
.hero-section {
    max-width: 900px;
    margin: 60px auto 40px;
    text-align: center;
    padding: 0 24px;
}

.hero-title {
    font-size: 48px;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 16px;
    letter-spacing: -1px;
    line-height: 1.2;
}

.hero-description {
    font-size: 18px;
    color: rgba(255, 255, 255, 0.7);
    line-height: 1.6;
    margin-bottom: 32px;
}

/* Tabs modernos */
.tabs-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 24px;
}

button.tab-button {
    background: transparent !important;
    border: none !important;
    color: rgba(255, 255, 255, 0.6) !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    padding: 12px 20px !important;
    margin: 0 4px !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}

button.tab-button:hover {
    background: rgba(255, 255, 255, 0.05) !important;
    color: rgba(255, 255, 255, 0.9) !important;
}

button.tab-button.selected {
    background: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
}

/* Cards de funcionalidades */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin: 40px 0;
}

.feature-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 24px;
    transition: all 0.3s ease;
    cursor: pointer;
}

.feature-card:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
}

.feature-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-bottom: 16px;
}

.feature-title {
    color: white;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 8px;
}

.feature-description {
    color: rgba(255, 255, 255, 0.6);
    font-size: 14px;
    line-height: 1.5;
}

/* Input area moderna */
.input-container {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 24px;
    margin: 20px 0;
}

textarea {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    color: white !important;
    font-size: 15px !important;
    padding: 16px !important;
    transition: all 0.2s ease !important;
}

textarea:focus {
    border-color: #3b82f6 !important;
    background: rgba(255, 255, 255, 0.08) !important;
    outline: none !important;
}

/* Botões modernos */
.primary-button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 10px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
}

.primary-button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
}

/* Output area */
.output-container {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 24px;
    margin: 20px 0;
    min-height: 200px;
}

.analysis-result {
    color: rgba(255, 255, 255, 0.9);
    font-size: 15px;
    line-height: 1.6;
}

.analysis-result h1, .analysis-result h2, .analysis-result h3 {
    color: white;
    margin-top: 20px;
    margin-bottom: 12px;
}

.analysis-result p {
    margin-bottom: 12px;
    color: rgba(255, 255, 255, 0.8);
}

.analysis-result ul, .analysis-result ol {
    margin: 12px 0;
    padding-left: 24px;
}

.analysis-result li {
    margin-bottom: 8px;
    color: rgba(255, 255, 255, 0.8);
}

.analysis-result strong {
    color: white;
    font-weight: 600;
}

/* Chat interface moderna */
.chat-container {
    max-width: 900px;
    margin: 0 auto;
    height: 600px;
    display: flex;
    flex-direction: column;
}

.messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.message {
    margin-bottom: 24px;
    display: flex;
    gap: 16px;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.message-avatar {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    flex-shrink: 0;
}

.user-avatar {
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
}

.ai-avatar {
    background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
}

.message-content {
    flex: 1;
    color: rgba(255, 255, 255, 0.9);
    font-size: 15px;
    line-height: 1.6;
}

.message-content p {
    margin-bottom: 12px;
}

/* Input area do chat */
.chat-input-area {
    display: flex;
    gap: 12px;
    margin-top: 20px;
    padding: 20px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.chat-input {
    flex: 1;
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    color: white !important;
    padding: 12px 16px !important;
    font-size: 15px !important;
}

/* Examples section */
.examples-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 12px;
    margin: 24px 0;
}

.example-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.example-card:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: #3b82f6;
    transform: translateY(-1px);
}

.example-title {
    color: white;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
}

.example-text {
    color: rgba(255, 255, 255, 0.6);
    font-size: 13px;
    line-height: 1.4;
}

/* Footer moderno */
.modern-footer {
    margin-top: auto;
    padding: 40px 24px;
    background: rgba(255, 255, 255, 0.02);
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.footer-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 24px;
}

.footer-links {
    display: flex;
    gap: 24px;
}

.footer-link {
    color: rgba(255, 255, 255, 0.6);
    text-decoration: none;
    font-size: 14px;
    transition: color 0.2s ease;
}

.footer-link:hover {
    color: white;
}

/* Responsividade */
@media (max-width: 768px) {
    .hero-title {
        font-size: 36px;
    }
    
    .hero-description {
        font-size: 16px;
    }
    
    .feature-grid {
        grid-template-columns: 1fr;
    }
    
    .footer-content {
        flex-direction: column;
        text-align: center;
    }
}

/* Animações suaves */
* {
    transition: color 0.2s ease, background-color 0.2s ease, border-color 0.2s ease;
}

/* Scrollbar customizada */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.2);
}
"""

def call_groq_api(message: str, system_prompt: str = None) -> str:
    """
    Chamada real para a API do Groq
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
            return f"❌ **Erro na API**: {response.status_code}\n\n{response.text}"
            
    except Exception as e:
        return f"❌ **Erro de conexão**: {str(e)}\n\nVerifique sua conexão e tente novamente."

async def search_real_data(query: str, data_type: str = "contracts") -> str:
    """
    Search real government data based on query
    """
    if not REAL_DATA_AVAILABLE:
        return "❌ **Dados reais não disponíveis**\n\nIntegração com API governamental não configurada."
    
    try:
        async with DataIntegrator() as integrator:
            # Parse query for search parameters
            query_lower = query.lower()
            
            # Extract CNPJ if present
            import re
            cnpj_match = re.search(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b|\b\d{14}\b', query)
            cnpj = cnpj_match.group() if cnpj_match else None
            
            # Extract year if present
            year_match = re.search(r'\b(20\d{2})\b', query)
            year = int(year_match.group()) if year_match else None
            
            # Extract value if present
            value_match = re.search(r'\b(?:acima|maior|superior)\s+(?:de\s+)?(?:r\$\s*)?([\d.,]+)\b', query_lower)
            min_value = None
            if value_match:
                try:
                    value_str = value_match.group(1).replace(',', '.')
                    min_value = float(value_str)
                except:
                    pass
            
            # Search based on data type
            if data_type == "contracts" or "contrato" in query_lower:
                result = await integrator.search_contracts(
                    cnpj=cnpj, 
                    year=year, 
                    min_value=min_value,
                    limit=10
                )
            elif data_type == "expenses" or "despesa" in query_lower:
                result = await integrator.search_expenses(
                    year=year,
                    min_value=min_value,
                    limit=10
                )
            elif data_type == "biddings" or "licitação" in query_lower:
                result = await integrator.search_biddings(
                    year=year,
                    min_value=min_value,
                    limit=10
                )
            else:
                # Default to contracts
                result = await integrator.search_contracts(
                    cnpj=cnpj,
                    year=year,
                    min_value=min_value,
                    limit=10
                )
            
            # Format for display
            return integrator.format_data_for_display(result)
            
    except Exception as e:
        logger.error(f"Error searching real data: {str(e)}")
        return f"❌ **Erro ao buscar dados**: {str(e)}"

async def comprehensive_analysis(text: str) -> str:
    """
    Comprehensive analysis combining real data and AI
    """
    if not REAL_DATA_AVAILABLE:
        return "❌ **Análise completa indisponível**\n\nIntegração com dados reais não configurada."
    
    try:
        async with AIAnalyzer(groq_api_key=GROQ_API_KEY) as analyzer:
            result = await analyzer.comprehensive_analysis(text)
            return analyzer.format_comprehensive_analysis(result)
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        return f"❌ **Erro na análise**: {str(e)}"

def analyze_transparency_text(text: str) -> str:
    """
    Análise especializada usando IA real e dados governamentais
    """
    if not text.strip():
        return "⚠️ **Texto vazio**\n\nPor favor, insira um texto para análise."
    
    # Check if this is a data search request
    search_keywords = ['buscar', 'procurar', 'encontrar', 'listar', 'cnpj', 'empresa', 'contrato', 'despesa', 'licitação']
    if any(keyword in text.lower() for keyword in search_keywords):
        # This is a comprehensive analysis request
        try:
            # Run async comprehensive analysis in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(comprehensive_analysis(text))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            # Fall back to simple search
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(search_real_data(text))
                loop.close()
                return result
            except Exception as e2:
                logger.error(f"Error in fallback search: {str(e2)}")
                # Fall back to AI analysis
                pass
    
    # Prompt especializado para análise de transparência
    system_prompt = """Você é o Cidadão.AI, um sistema especializado em análise de transparência pública brasileira.

MISSÃO: Analisar documentos governamentais para detectar anomalias, avaliar riscos financeiros e verificar conformidade legal.

EXPERTISE:
- Legislação brasileira (Lei 14.133/2021, Lei 8.666/93)
- Portal da Transparência e dados governamentais
- Detecção de irregularidades em contratos e licitações
- Análise de superfaturamento e fraudes

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

🎯 **CONFIANÇA**: [Porcentagem] - [Justificativa]

INSTRUÇÕES:
- Seja específico e técnico
- Use números e dados quando possível  
- Mencione leis relevantes
- Identifique red flags claramente
- Mantenha tom profissional e imparcial"""

    try:
        # Preparar prompt específico
        user_prompt = f"""Analise o seguinte documento/situação de transparência pública:

DOCUMENTO PARA ANÁLISE:
{text}

Por favor, forneça uma análise completa seguindo o formato estabelecido."""

        return call_groq_api(user_prompt, system_prompt)
        
    except Exception as e:
        return f"❌ **Erro na análise**: {str(e)}\n\nTente novamente em alguns instantes."

def chat_with_ai(message: str, history: List[Dict]) -> Tuple[str, List[Dict]]:
    """
    Chat conversacional com a IA e busca de dados reais
    """
    if not message.strip():
        return "", history
    
    # Check if this is a data search request
    search_keywords = ['buscar', 'procurar', 'encontrar', 'listar', 'cnpj', 'empresa', 'contrato', 'despesa', 'licitação']
    if any(keyword in message.lower() for keyword in search_keywords):
        try:
            # Run async comprehensive analysis in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            ai_response = loop.run_until_complete(comprehensive_analysis(message))
            loop.close()
            
            # Update history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": ai_response})
            
            return "", history
        except Exception as e:
            logger.error(f"Error in chat comprehensive analysis: {str(e)}")
            # Fall back to simple search
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                ai_response = loop.run_until_complete(search_real_data(message))
                loop.close()
                
                # Update history
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": ai_response})
                
                return "", history
            except Exception as e2:
                logger.error(f"Error in fallback search: {str(e2)}")
                # Fall back to regular AI chat
                pass
    
    # Sistema especializado para chat
    system_prompt = """Você é o Cidadão.AI, assistente especializada em transparência pública brasileira.

PERSONALIDADE:
- Profissional, mas acessível
- Especialista em dados governamentais
- Focada em transparência e accountability
- Conhece profundamente a legislação brasileira

CAPACIDADES:
- Explicar dados do Portal da Transparência
- Analisar contratos e licitações
- Detectar irregularidades
- Orientar sobre compliance público
- Interpretar legislação (Lei 14.133/2021, etc.)

ESTILO DE RESPOSTA:
- Use emojis apropriados
- Seja didática e clara
- Cite fontes quando relevante
- Ofereça exemplos práticos
- Mantenha foco na transparência

LIMITAÇÕES:
- Não acuse pessoas específicas
- Baseie-se em dados públicos
- Seja imparcial e técnica"""

    try:
        # Construir contexto do histórico
        context_messages = []
        
        # Adicionar histórico recente (últimas 10 mensagens)
        for msg in history[-10:]:
            if msg["role"] == "user":
                context_messages.append(f"Usuário: {msg['content']}")
            elif msg["role"] == "assistant":
                context_messages.append(f"Cidadão.AI: {msg['content']}")
        
        # Preparar prompt com contexto
        if context_messages:
            context = "\n".join(context_messages)
            full_prompt = f"""CONTEXTO DA CONVERSA:
{context}

NOVA PERGUNTA: {message}

Responda como Cidadão.AI, mantendo o contexto da conversa:"""
        else:
            full_prompt = f"""Olá! Sou o Cidadão.AI. Como posso ajudar você com transparência pública?

PERGUNTA: {message}

Resposta:"""
        
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
    
    # Check API status
    if GROQ_API_KEY:
        status_text += " - IA Ativa"
    else:
        status_emoji = "⚠️"
        status_text += " - IA Limitada"
    
    # Check real data availability
    if REAL_DATA_AVAILABLE:
        status_text += " - Dados Reais"
    else:
        status_text += " - Dados Simulados"
    
    return status_emoji, status_text

def create_main_interface():
    """
    Interface principal moderna do Gradio
    """
    status_emoji, status_text = get_status_info()
    
    with gr.Blocks(css=custom_css, title="Cidadão.AI - Transparência Pública com IA", theme=gr.themes.Base()) as app:
        
        # Container principal
        with gr.Column(elem_classes=["main-container"]):
            
            # Header moderno
            gr.HTML(f"""
            <div class="modern-header">
                <div class="header-content">
                    <div class="logo-section">
                        <div class="logo-icon">🇧🇷</div>
                        <div>
                            <div class="logo-text">Cidadão.AI</div>
                            <div class="logo-subtitle">Inteligência para transparência pública</div>
                        </div>
                    </div>
                    <div class="status-badge">
                        <div class="status-dot"></div>
                        <span>{status_text}</span>
                    </div>
                </div>
            </div>
            """)
            
            # Hero Section
            gr.HTML("""
            <div class="hero-section">
                <h1 class="hero-title">Análise Inteligente de Transparência Pública</h1>
                <p class="hero-description">
                    Transforme documentos governamentais complexos em insights claros. 
                    Nossa IA especializada detecta irregularidades, analisa contratos e 
                    monitora gastos públicos em tempo real.
                </p>
            </div>
            """)
            
            # Feature Cards
            gr.HTML("""
            <div class="tabs-container">
                <div class="feature-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🔍</div>
                        <div class="feature-title">Análise de Documentos</div>
                        <div class="feature-description">
                            Detecte automaticamente irregularidades em contratos, 
                            licitações e despesas públicas
                        </div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">⚖️</div>
                        <div class="feature-title">Conformidade Legal</div>
                        <div class="feature-description">
                            Verifique aderência às leis 14.133/2021, 8.666/93 
                            e normas do TCU
                        </div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">💬</div>
                        <div class="feature-title">Chat Especializado</div>
                        <div class="feature-description">
                            Converse com nossa IA sobre transparência, 
                            legislação e dados públicos
                        </div>
                    </div>
                </div>
            </div>
            """)
            
            # Tabs principais
            with gr.Tabs(elem_classes=["tabs-container"]):
                
                # Tab de Análise
                with gr.Tab("🔍 Analisar Documento", elem_classes=["tab-button"]):
                    with gr.Column(elem_classes=["tabs-container"]):
                        
                        # Examples section
                        gr.HTML("""
                        <div class="examples-grid">
                            <div class="example-card" onclick="document.querySelector('textarea').value = 'Buscar contratos da empresa CNPJ 12.345.678/0001-90 em 2024'">
                                <div class="example-title">🔍 Busca por CNPJ</div>
                                <div class="example-text">Contratos de empresa específica</div>
                            </div>
                            <div class="example-card" onclick="document.querySelector('textarea').value = 'Listar despesas acima de R$ 1.000.000 em 2024'">
                                <div class="example-title">💰 Busca por Valor</div>
                                <div class="example-text">Despesas de alto valor</div>
                            </div>
                            <div class="example-card" onclick="document.querySelector('textarea').value = 'Encontrar licitações em andamento no ministério da saúde'">
                                <div class="example-title">🏛️ Busca por Órgão</div>
                                <div class="example-text">Licitações de órgão específico</div>
                            </div>
                            <div class="example-card" onclick="document.querySelector('textarea').value = 'Contrato emergencial de R$ 50 milhões sem licitação para empresa recém-criada'">
                                <div class="example-title">🤖 Análise de Texto</div>
                                <div class="example-text">Análise de documento suspeito</div>
                            </div>
                        </div>
                        """)
                        
                        # Input area
                        with gr.Column(elem_classes=["input-container"]):
                            text_input = gr.Textbox(
                                label="",
                                placeholder="Cole um documento para análise OU digite uma busca como: 'buscar contratos da empresa CNPJ 12.345.678/0001-90' ou 'listar despesas acima de R$ 1.000.000'...",
                                lines=6,
                                max_lines=15,
                                elem_classes=["modern-input"]
                            )
                            
                            analyze_btn = gr.Button(
                                "Analisar/Buscar",
                                variant="primary",
                                elem_classes=["primary-button"]
                            )
                        
                        # Output area
                        with gr.Column(elem_classes=["output-container"]):
                            analysis_output = gr.Markdown(
                                value="""### 🤖 Aguardando análise ou busca...

Você pode:

🔍 **Buscar dados reais**:
- "buscar contratos da empresa CNPJ 12.345.678/0001-90"
- "listar despesas acima de R$ 1.000.000 em 2024"
- "encontrar licitações do ministério da saúde"

🤖 **Analisar documentos**:
- Cole texto de contratos, licitações ou despesas
- Receba análise de anomalias e conformidade
- Obtenha recomendações práticas""",
                                elem_classes=["analysis-result"]
                            )
                        
                        # Conectar análise
                        analyze_btn.click(
                            analyze_transparency_text,
                            inputs=[text_input],
                            outputs=[analysis_output]
                        )
                
                # Tab de Chat
                with gr.Tab("💬 Chat com IA", elem_classes=["tab-button"]):
                    with gr.Column(elem_classes=["chat-container"]):
                        
                        chatbot = gr.Chatbot(
                            value=[{"role": "assistant", "content": """👋 Olá! Sou o **Cidadão.AI**, sua assistente especializada em transparência pública brasileira.

Posso ajudar você com:
- 🔍 **Busca de dados reais** do Portal da Transparência
- 📊 **Análise de contratos** e licitações
- 🔍 **Detecção de irregularidades**
- ⚖️ **Interpretação da legislação**
- 💡 **Orientações sobre compliance**

🔍 **Exemplos de busca**:
- "buscar contratos da empresa CNPJ 12.345.678/0001-90"
- "listar despesas acima de R$ 1.000.000 em 2024"
- "encontrar licitações do ministério da saúde"

Como posso ajudar você hoje?"""}],
                            height=500,
                            type="messages",
                            elem_classes=["messages-container"],
                            show_label=False
                        )
                        
                        with gr.Row(elem_classes=["chat-input-area"]):
                            chat_input = gr.Textbox(
                                label="",
                                placeholder="Digite sua pergunta sobre transparência pública...",
                                scale=4,
                                elem_classes=["chat-input"]
                            )
                            chat_btn = gr.Button("Enviar", scale=1, elem_classes=["primary-button"])
                        
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
                
                # Tab Sobre
                with gr.Tab("ℹ️ Sobre", elem_classes=["tab-button"]):
                    with gr.Column(elem_classes=["tabs-container"]):
                        gr.Markdown(f"""
                        ## 🇧🇷 Sobre o Cidadão.AI

                        ### Missão
                        Democratizar o acesso aos dados governamentais brasileiros através de inteligência artificial especializada, 
                        tornando a transparência pública acessível a todos os cidadãos.

                        ### Capacidades do Sistema

                        **Análise de Documentos**
                        - Contratos públicos e aditivos
                        - Licitações e processos de compra
                        - Despesas e empenhos governamentais
                        - Convênios e parcerias público-privadas

                        **Detecção de Irregularidades**
                        - Identificação de superfaturamento
                        - Detecção de empresas fantasma
                        - Análise de processos sem licitação
                        - Verificação de prazos legais

                        **Conformidade Legal**
                        - Lei 14.133/2021 (Nova Lei de Licitações)
                        - Lei 8.666/93 (Lei de Licitações)
                        - Lei de Acesso à Informação
                        - Normas do TCU e órgãos de controle

                        ### Tecnologia
                        - **IA Especializada**: Modelo treinado em transparência pública
                        - **Status**: {status_emoji} {status_text}
                        - **Processamento**: Análise em tempo real
                        - **Segurança**: Dados processados com total privacidade

                        ### Aviso Legal
                        Este sistema é uma ferramenta de apoio para análise de transparência pública. 
                        Os resultados devem ser validados por especialistas antes de serem utilizados 
                        para tomada de decisões ou denúncias formais.
                        """, elem_classes=["analysis-result"])
            
            # Footer moderno
            gr.HTML(f"""
            <div class="modern-footer">
                <div class="footer-content">
                    <div>
                        <strong>Cidadão.AI</strong> - Democratizando a transparência pública
                    </div>
                    <div class="footer-links">
                        <a href="https://github.com/anderson-henrique-da-silva/cidadao.ai" class="footer-link">GitHub</a>
                        <a href="https://portaldatransparencia.gov.br" class="footer-link">Portal da Transparência</a>
                        <a href="https://dados.gov.br" class="footer-link">Dados Abertos</a>
                    </div>
                </div>
            </div>
            """)
    
    return app

# Criar e lançar aplicação
if __name__ == "__main__":
    logger.info("🚀 Iniciando Cidadão.AI v3.0 - Interface Moderna...")
    
    # Verificar configuração
    if GROQ_API_KEY:
        logger.info("✅ API Groq configurada")
    else:
        logger.warning("⚠️ API Groq não configurada - funcionalidade limitada")
    
    # Criar interface
    app = create_main_interface()
    
    # Configurar e lançar
    app.queue(max_size=20)
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        enable_queue=True,
        show_error=True,
        favicon_path=None,
        auth=None
    )