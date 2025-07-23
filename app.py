#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Backend Interface for Hugging Face Spaces
"""

import os
import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from threading import Thread

# Create FastAPI backend
app = FastAPI(
    title="Cidadão.AI API",
    description="🏛️ API para transparência pública brasileira",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Cidadão.AI Backend",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Create Gradio interface
def create_interface():
    with gr.Blocks(
        title="Cidadão.AI Backend",
        theme=gr.themes.Soft(
            primary_hue="emerald",
            secondary_hue="blue",
        ),
        css="""
        .gradio-container {
            max-width: 800px !important;
            margin: auto !important;
        }
        .main-content {
            text-align: center;
            padding: 2rem;
        }
        .logo {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        .title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            font-size: 1.2rem;
            color: #6b7280;
            margin-bottom: 2rem;
        }
        .status {
            display: inline-block;
            padding: 0.5rem 1rem;
            background: #10b981;
            color: white;
            border-radius: 2rem;
            font-weight: 500;
            margin-bottom: 2rem;
        }
        .link-button {
            display: inline-block;
            padding: 1rem 2rem;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            text-decoration: none;
            border-radius: 0.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
        }
        .link-button:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 8px 12px rgba(16, 185, 129, 0.3);
        }
        .api-info {
            margin-top: 3rem;
            padding: 1.5rem;
            background: #f3f4f6;
            border-radius: 0.5rem;
            text-align: left;
        }
        """
    ) as interface:
        with gr.Column(elem_classes="main-content"):
            gr.HTML("""
                <div class="logo">🏛️</div>
                <h1 class="title">Cidadão.AI Backend</h1>
                <p class="subtitle">Sistema de Transparência Pública com IA</p>
                <div class="status">✅ Backend Operacional</div>
            """)
            
            gr.Markdown("""
            Este é o servidor backend do **Cidadão.AI**, responsável por processar e analisar dados de transparência pública brasileira usando inteligência artificial.
            
            ### 🚀 Funcionalidades
            - Sistema multi-agente de IA para análise de dados públicos
            - API RESTful para integração com frontends
            - Processamento em tempo real de informações governamentais
            - Detecção de anomalias e padrões suspeitos
            
            ### 📚 Documentação Completa
            Para mais informações sobre o projeto, arquitetura e como contribuir:
            """)
            
            gr.HTML("""
                <div style="text-align: center; margin: 2rem 0;">
                    <a href="https://anderson-ufrj.github.io/cidadao.ai-docs/" target="_blank" class="link-button">
                        📖 Acessar Documentação Completa
                    </a>
                </div>
            """)
            
            gr.HTML("""
                <div class="api-info">
                    <h3>🔧 API Endpoints</h3>
                    <p><strong>Base URL:</strong> https://huggingface.co/spaces/neural-thinker/cidadao.ai-backend</p>
                    <ul>
                        <li><code>GET /</code> - Status da API</li>
                        <li><code>GET /health</code> - Health check</li>
                        <li><code>GET /docs</code> - Documentação interativa (Swagger)</li>
                    </ul>
                </div>
            """)
            
            gr.HTML("""
                <div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #e5e7eb; text-align: center;">
                    <p style="margin-bottom: 1rem;">
                        <strong>Desenvolvido por:</strong> Anderson Henrique da Silva<br>
                        <strong>Licença:</strong> Apache 2.0 | <strong>SDG:</strong> 16 - Paz, Justiça e Instituições Eficazes
                    </p>
                    <div style="display: flex; gap: 1rem; justify-content: center; align-items: center;">
                        <a href="https://github.com/anderson-ufrj/cidadao.ai-backend" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: #24292e; color: white; text-decoration: none; border-radius: 0.375rem; font-size: 0.875rem; transition: all 0.2s;">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                            </svg>
                            GitHub
                        </a>
                        <a href="https://huggingface.co/spaces/neural-thinker/cidadao.ai-backend" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: #ff6b6b; color: white; text-decoration: none; border-radius: 0.375rem; font-size: 0.875rem; transition: all 0.2s;">
                            🤗 Hugging Face
                        </a>
                    </div>
                </div>
            """)
    
    return interface

# Run FastAPI in background
def run_api():
    uvicorn.run(app, host="0.0.0.0", port=7860)

# Launch Gradio interface
if __name__ == "__main__":
    # Start API in background thread
    api_thread = Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Detect environment
    is_huggingface = os.getenv("SPACE_ID") is not None
    is_local = not is_huggingface and os.getenv("ENV", "").lower() in ["local", "dev", "development"]
    
    # Create and launch Gradio interface
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7861 if not is_huggingface else 7860,
        share=True if is_local else False,
        show_error=True
    )