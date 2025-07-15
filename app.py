#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Portal da Transparência
Sistema de consulta aos dados do Portal da Transparência
"""

import gradio as gr
import os
import time
import asyncio
import httpx
import json
from datetime import datetime

# Configurar variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def call_transparency_api(endpoint, params=None):
    """Chamar API do Portal da Transparência"""
    if not TRANSPARENCY_API_KEY:
        return {"error": "API key não configurada"}
    
    base_url = "https://api.portaldatransparencia.gov.br"
    headers = {
        "chave-api-dados": TRANSPARENCY_API_KEY,
        "User-Agent": "CidadaoAI/1.0"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{base_url}{endpoint}",
                headers=headers,
                params=params or {}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": f"Erro na requisição: {str(e)}"}

def search_data(data_type, year, search_term):
    """Buscar dados reais na API do Portal da Transparência"""
    if not search_term:
        return """
        <div style="padding: 2rem; text-align: center;">
            <p style="color: var(--text-secondary);">Digite uma consulta para buscar dados</p>
        </div>
        """
    
    # Mapear tipo de dados para endpoint
    endpoint_map = {
        "Contratos Públicos": "/api-de-dados/contratos",
        "Despesas Orçamentárias": "/api-de-dados/despesas", 
        "Licitações e Pregões": "/api-de-dados/licitacoes"
    }
    
    endpoint = endpoint_map.get(data_type, "/api-de-dados/contratos")
    
    # Parâmetros da consulta
    params = {
        "ano": int(year),
        "pagina": 1,
        "tamanhoPagina": 10
    }
    
    # Executar consulta na API
    try:
        # Usar asyncio para chamar a API assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        api_result = loop.run_until_complete(call_transparency_api(endpoint, params))
        loop.close()
        
        if "error" in api_result:
            return f"""
            <div style="padding: 2rem; text-align: center; color: #DC2626;">
                <h3>Erro na API</h3>
                <p>{api_result['error']}</p>
            </div>
            """
        
        # Processar resultados
        results = api_result if isinstance(api_result, list) else []
        
        if not results:
            return """
            <div style="padding: 2rem; text-align: center;">
                <h3>Nenhum resultado encontrado</h3>
                <p style="color: var(--text-secondary);">Tente ajustar os filtros ou termo de busca</p>
            </div>
            """
        
    except Exception as e:
        return f"""
        <div style="padding: 2rem; text-align: center; color: #DC2626;">
            <h3>Erro na busca</h3>
            <p>{str(e)}</p>
        </div>
        """
    
    # Header simples
    html = f"""
    <div style="padding: 1.5rem;">
        <h3 style="margin-bottom: 1.5rem;">Resultados da busca</h3>
        <p style="color: var(--text-secondary); margin-bottom: 2rem;">Busca por: "{search_term}" - {data_type} ({year})</p>
        <p style="color: var(--text-secondary); margin-bottom: 2rem;">Encontrados: {len(results)} registros</p>
    """
    
    # Processar resultados reais da API
    for i, item in enumerate(results[:5], 1):  # Mostrar apenas 5 primeiros
        # Adaptar campos conforme retorno da API
        numero = item.get('numero', item.get('id', f'REG-{i:03d}'))
        empresa = item.get('nome', item.get('razaoSocial', item.get('fornecedor', 'N/A')))
        valor = item.get('valor', item.get('valorContrato', item.get('valorInicial', 0)))
        objeto = item.get('objeto', item.get('descricao', 'N/A'))
        
        # Formatar valor
        if isinstance(valor, (int, float)):
            valor_fmt = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        else:
            valor_fmt = str(valor)
        
        html += f"""
        <div style="border: 1px solid var(--border-color); border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
            <h4 style="color: var(--primary-blue); margin: 0 0 0.5rem 0;">{data_type} #{numero}</h4>
            <p><strong>Empresa/Favorecido:</strong> {empresa}</p>
            <p><strong>Valor:</strong> {valor_fmt}</p>
            <p><strong>Objeto:</strong> {objeto[:100]}{'...' if len(str(objeto)) > 100 else ''}</p>
            <details style="margin-top: 0.5rem;">
                <summary style="cursor: pointer; color: var(--primary-blue);">Ver dados completos</summary>
                <pre style="background: var(--bg-secondary); padding: 1rem; border-radius: 4px; overflow-x: auto; font-size: 0.8rem;">{json.dumps(item, indent=2, ensure_ascii=False)}</pre>
            </details>
        </div>
        """
    
    html += """
    </div>
    """
    
    return html

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
                <button class="btn btn-primary" onclick="navigateToAdvanced()">
                    <span>🔍</span> Consulta Avançada
                </button>
                <button class="btn btn-secondary" onclick="navigateToChat()">
                    <span>💬</span> Pergunte ao Modelo
                </button>
            </div>
        </div>
    </div>
    
    <!-- Modal de Créditos -->
    <div id="creditsModal" class="modal-overlay" onclick="handleModalClick(event)" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); z-index: 2000; justify-content: center; align-items: center;">
        <div class="modal-content" style="background: var(--bg-primary); border-radius: 12px; padding: 2rem; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto; box-shadow: var(--shadow-xl); border: 1px solid var(--border-color);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h2 style="color: var(--text-primary); margin: 0; font-size: 1.5rem; font-weight: 600;">Créditos</h2>
                <button onclick="hideCreditsModal()" style="background: transparent; border: none; font-size: 1.5rem; cursor: pointer; color: var(--text-secondary); padding: 0.5rem;">×</button>
            </div>
            
            <div style="color: var(--text-secondary); line-height: 1.6;">
                <div style="margin-bottom: 1.5rem;">
                    <h3 style="color: var(--text-primary); margin-bottom: 0.5rem; font-size: 1.125rem;">🇧🇷 Cidadão.AI</h3>
                    <p style="margin-bottom: 1rem;">Plataforma inteligente para análise de dados públicos brasileiros</p>
                </div>
                
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">🔗 Links Importantes</h4>
                    <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem;">
                        <a href="https://github.com/anderson-ufrj/cidadao.ai" target="_blank" style="color: var(--primary-blue); text-decoration: none; padding: 0.5rem 1rem; border: 1px solid var(--border-color); border-radius: 6px; transition: all 0.2s ease;">
                            <span>📚</span> GitHub
                        </a>
                        <a href="https://huggingface.co/spaces/neural-thinker/cidadao.ia" target="_blank" style="color: var(--primary-blue); text-decoration: none; padding: 0.5rem 1rem; border: 1px solid var(--border-color); border-radius: 6px; transition: all 0.2s ease;">
                            <span>🤗</span> Hugging Face
                        </a>
                        <a href="https://anderson-ufrj.github.io/cidadao.ai/" target="_blank" style="color: var(--primary-blue); text-decoration: none; padding: 0.5rem 1rem; border: 1px solid var(--border-color); border-radius: 6px; transition: all 0.2s ease;">
                            <span>📖</span> Documentação Técnica
                        </a>
                    </div>
                </div>
                
                <div style="text-align: center; padding-top: 1rem; border-top: 1px solid var(--border-color);">
                    <p style="font-size: 0.875rem; color: var(--text-tertiary);">
                        © 2025 Cidadão.AI - Democratizando o acesso à transparência pública
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Botão de ajuda flutuante -->
    <button class="help-button" onclick="toggleHelpModal()" title="Sobre o Projeto">
        ❓
    </button>
    
    <!-- Modal de Ajuda em formato de balão -->
    <div id="helpModal" class="help-modal" onclick="handleHelpModalClick(event)">
        <div class="help-modal-header">
            <span>🎓</span>
            <h3>Sobre o Projeto</h3>
            <button class="help-modal-close" onclick="hideHelpModal()">×</button>
        </div>
        
        <div class="help-modal-content">
            <!-- Developer Section -->
            <div class="help-section">
                <h4>👨‍💻 Desenvolvedor</h4>
                <div class="help-info">
                    <p><strong>Anderson Henrique da Silva</strong></p>
                    <p>Bacharelado em Ciência da Computação</p>
                    <p>IFSuldeminas Campus Muzambinho</p>
                    
                    <div class="help-links">
                        <a href="https://github.com/anderson-ufrj" target="_blank" class="help-link">
                            <span>🐙</span> GitHub
                        </a>
                        <a href="https://www.linkedin.com/in/anderson-h-silva95/" target="_blank" class="help-link">
                            <span>💼</span> LinkedIn
                        </a>
                        <a href="mailto:andersonhs27@gmail.com" class="help-link">
                            <span>📧</span> Email
                        </a>
                        <a href="https://x.com/neural_thinker" target="_blank" class="help-link">
                            <span>🐦</span> Twitter
                        </a>
                        <a href="https://www.instagram.com/andhenrique_/" target="_blank" class="help-link">
                            <span>📸</span> Instagram
                        </a>
                    </div>
                </div>
            </div>

            <!-- Institution Section -->
            <div class="help-section">
                <h4>🏛️ Instituição</h4>
                <div class="help-info">
                    <p><strong>Instituto Federal do Sul de Minas Gerais</strong></p>
                    <p>Campus Muzambinho</p>
                    <p>Curso: Bacharelado em Ciência da Computação</p>
                    
                    <div class="help-links">
                        <a href="https://cursos.muz.ifsuldeminas.edu.br/ciencia-da-computacao" target="_blank" class="help-link">
                            <span>🏫</span> Curso
                        </a>
                    </div>
                </div>
            </div>

            <!-- Project Section -->
            <div class="help-section">
                <h4>🔍 Projeto</h4>
                <div class="help-info">
                    <p><strong>Cidadão.AI</strong></p>
                    <p>Sistema Multi-Agente de IA para Transparência Pública</p>
                    
                    <div class="help-links">
                        <a href="https://github.com/anderson-ufrj/cidadao.ai" target="_blank" class="help-link">
                            <span>📦</span> Repositório
                        </a>
                        <a href="https://anderson-ufrj.github.io/cidadao.ai/" target="_blank" class="help-link">
                            <span>📖</span> Documentação
                        </a>
                        <a href="https://huggingface.co/spaces/neural-thinker/cidadao.ia" target="_blank" class="help-link">
                            <span>🤗</span> Demo Online
                        </a>
                    </div>
                </div>
            </div>

            <!-- Version Section -->
            <div class="help-section">
                <h4>🏷️ Versão</h4>
                <div class="help-info">
                    <p><strong>v1.0.0</strong> | Todos os direitos reservados</p>
                    <p style="font-size: 0.8rem; margin-top: 10px;">Trabalho de Conclusão de Curso - 2025</p>
                </div>
            </div>
        </div>
    </div>
    """

async def call_groq_api(message):
    """Chamar API do GROQ para chat"""
    if not GROQ_API_KEY:
        return "API key do GROQ não configurada"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "Você é um assistente especializado em dados do governo brasileiro e transparência pública. Responda de forma clara e objetiva sobre gastos públicos, contratos, licitações e dados governamentais."
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "model": "llama3-8b-8192",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Erro na API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erro na requisição: {str(e)}"

def chat_fn(message, history):
    if message:
        history = history or []
        
        # Chamar API do GROQ
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(call_groq_api(message))
            loop.close()
        except Exception as e:
            response = f"Erro ao processar mensagem: {str(e)}"
        
        history.append((message, response))
        return history, ""
    return history, ""

def create_interface():
    """Interface principal"""
    
    # Carregar CSS e JS externos
    with open('static/css/main.css', 'r') as f:
        css_content = f.read()
    
    with open('static/js/main.js', 'r') as f:
        js_content = f.read()
    
    with gr.Blocks(
        css=css_content,
        title="Cidadão.AI",
        theme=gr.themes.Base(),
        head=f"""
        <style>body {{ margin: 0; padding: 0; }}</style>
        <script>{js_content}</script>
        """
    ) as app:
        
        # Landing page como primeira aba
        with gr.Tab("🏠 Cidadão.AI"):
            gr.HTML(create_landing_page())
        
        # Aba de consulta avançada
        with gr.Tab("🔍 Consulta Avançada"):
            gr.HTML("""
                <div class="header">
                    <div class="logo">
                        <span style="font-size: 2rem;">🇧🇷</span>
                        <span class="logo-text">Cidadão.AI</span>
                    </div>
                    <button class="theme-toggle" onclick="toggleTheme()" id="theme-toggle-btn-2">
                        <span>🌙</span> Modo Escuro
                    </button>
                </div>
                <div style="padding-top: 100px;">
                    <h2 style="text-align: center; margin-bottom: 2rem;">Consulta Avançada</h2>
                </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-color);">
                        <h3 style="margin-bottom: 1.5rem;">Filtros</h3>
                    </div>
                    """)
                    
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
                
                with gr.Column(scale=2):
                    results = gr.HTML(
                        value="""
                        <div style="background: var(--bg-secondary); padding: 2rem; border-radius: 12px; border: 1px solid var(--border-color); min-height: 400px;">
                            <h3 style="margin-bottom: 1.5rem;">Resultados</h3>
                            <p style="color: var(--text-secondary);">Digite uma consulta e clique em "Buscar" para ver os resultados</p>
                        </div>
                        """
                    )
            
            search_btn.click(
                fn=search_data,
                inputs=[data_type, year, search_term],
                outputs=results
            )
        
        # Aba de perguntas ao modelo
        with gr.Tab("💬 Pergunte ao Modelo"):
            gr.HTML("""
                <div class="header">
                    <div class="logo">
                        <span style="font-size: 2rem;">🇧🇷</span>
                        <span class="logo-text">Cidadão.AI</span>
                    </div>
                    <button class="theme-toggle" onclick="toggleTheme()" id="theme-toggle-btn-3">
                        <span>🌙</span> Modo Escuro
                    </button>
                </div>
                <div style="padding-top: 100px; text-align: center;">
                    <h2 style="margin-bottom: 2rem;">Pergunte ao Modelo</h2>
                </div>
            """)
            
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
            
            msg.submit(fn=chat_fn, inputs=[msg, chatbot], outputs=[chatbot, msg])
            send_btn.click(fn=chat_fn, inputs=[msg, chatbot], outputs=[chatbot, msg])
    
    return app

# Executar aplicação
if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI - Versão Refatorada...")
    app = create_interface()
    app.launch(
        show_error=True,
        quiet=False,
        favicon_path=None,
        app_kwargs={
            "docs_url": None,
            "redoc_url": None,
        }
    )