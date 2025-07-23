#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Backend Interface with Visual Activity Tracking
"""

import os
import time
import asyncio
import random
from datetime import datetime, timedelta
from threading import Thread
from typing import Dict, List, Any

import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Global metrics storage
metrics = {
    "requests_total": 0,
    "api_calls": 0,
    "data_processed": 0,
    "last_activity": "Inicializando...",
    "status": "🟢 Online",
    "connections": {
        "portal_transparencia": "🟡 Testando...",
        "database": "🟢 Conectado", 
        "redis": "🟡 Verificando...",
        "ai_service": "🟢 Ativo"
    },
    "recent_activities": []
}

# Create FastAPI backend
app = FastAPI(
    title="Cidadão.AI API",
    description="🏛️ API para transparência pública brasileira",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def add_activity(activity: str, activity_type: str = "info"):
    """Add new activity to tracking"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    metrics["recent_activities"].insert(0, {
        "time": timestamp,
        "activity": activity,
        "type": activity_type
    })
    
    # Keep only last 10 activities
    metrics["recent_activities"] = metrics["recent_activities"][:10]
    metrics["last_activity"] = f"[{timestamp}] {activity}"

def simulate_backend_activity():
    """Simulate backend activity for demo"""
    activities = [
        ("Analisando dados do Portal da Transparência", "process"),
        ("Conectando com API externa", "api"),
        ("Processando análise de anomalias", "ai"),
        ("Salvando resultados no banco", "database"),
        ("Gerando relatório automático", "report"),
        ("Verificando integridade dos dados", "check"),
        ("Atualizando cache de consultas", "cache"),
        ("Executando rotina de limpeza", "maintenance")
    ]
    
    while True:
        activity, act_type = random.choice(activities)
        add_activity(activity, act_type)
        
        # Update metrics
        metrics["requests_total"] += random.randint(1, 3)
        metrics["api_calls"] += random.randint(0, 2)
        metrics["data_processed"] += random.randint(50, 200)
        
        # Randomly update connection status
        if random.random() < 0.1:  # 10% chance
            services = list(metrics["connections"].keys())
            service = random.choice(services)
            statuses = ["🟢 Conectado", "🟡 Lento", "🔴 Erro"]
            metrics["connections"][service] = random.choice(statuses)
        
        time.sleep(random.uniform(2, 8))

@app.get("/")
async def root():
    add_activity("Requisição GET / recebida", "api")
    metrics["requests_total"] += 1
    return {
        "message": "Cidadão.AI Backend",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    add_activity("Health check executado", "check")
    return {"status": "healthy"}

@app.get("/metrics")
async def get_metrics():
    add_activity("Métricas solicitadas", "api")
    return metrics

def create_interface():
    with gr.Blocks(
        title="Cidadão.AI Backend - Monitor",
        theme=gr.themes.Soft(
            primary_hue="green",
            secondary_hue="blue",
        ),
        css="""
        .gradio-container {
            max-width: 1200px !important;
            margin: auto !important;
        }
        .main-content {
            text-align: center;
            padding: 1rem;
        }
        .logo {
            font-size: 3rem;
            margin-bottom: 0.5rem;
        }
        .title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #22c55e 0%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            font-size: 1rem;
            color: #6b7280;
            margin-bottom: 1rem;
        }
        .status-online {
            color: #22c55e;
            font-weight: bold;
        }
        .status-warning {
            color: #f59e0b;
            font-weight: bold;
        }
        .status-error {
            color: #ef4444;
            font-weight: bold;
        }
        .metric-card {
            background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
            border: 1px solid #bbf7d0;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 0.5rem;
        }
        .activity-item {
            padding: 0.5rem;
            margin: 0.25rem 0;
            border-left: 3px solid #22c55e;
            background: #f9fafb;
            border-radius: 0.25rem;
            font-size: 0.875rem;
        }
        .link-button {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: white;
            text-decoration: none;
            border-radius: 0.375rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(34, 197, 94, 0.2);
            margin: 0.25rem;
        }
        .link-button:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 8px 12px rgba(34, 197, 94, 0.3);
        }
        """
    ) as interface:
        
        with gr.Column(elem_classes="main-content"):
            gr.HTML("""
                <div class="logo">🏛️</div>
                <h1 class="title">Cidadão.AI Backend Monitor</h1>
                <p class="subtitle">Sistema de Transparência Pública com IA - Monitoramento em Tempo Real</p>
            """)
            
            # Status geral
            status_display = gr.HTML()
            
            # Métricas em tempo real
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📊 Métricas em Tempo Real")
                    metrics_display = gr.HTML()
                
                with gr.Column():
                    gr.Markdown("### 🔗 Status das Conexões")
                    connections_display = gr.HTML()
            
            # Atividades recentes
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### ⚡ Atividades Recentes")
                    activities_display = gr.HTML()
                
                with gr.Column():
                    gr.Markdown("### 📈 Gráfico de Atividade")
                    activity_plot = gr.LinePlot(
                        x="time", 
                        y="value",
                        title="Requisições por Minuto",
                        height=200
                    )
            
            # Links e documentação
            gr.Markdown("""
            ### 📚 Documentação e Links
            """)
            
            gr.HTML("""
                <div style="text-align: center; margin: 1rem 0;">
                    <a href="https://anderson-ufrj.github.io/cidadao.ai-docs/" target="_blank" class="link-button">
                        📖 Documentação Completa
                    </a>
                    <a href="/docs" target="_blank" class="link-button">
                        🔧 API Docs (Swagger)
                    </a>
                </div>
            """)
            
            # Rodapé
            gr.HTML("""
                <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e5e7eb; text-align: center;">
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

        def update_dashboard():
            # Status geral
            status_html = f"""
                <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%); border-radius: 0.5rem; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: #15803d;">
                        {metrics['status']} Backend Operacional
                    </h3>
                    <p style="margin: 0.5rem 0; color: #374151;">
                        Última atividade: {metrics['last_activity']}
                    </p>
                </div>
            """
            
            # Métricas
            metrics_html = f"""
                <div class="metric-card">
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; font-weight: bold; color: #22c55e;">{metrics['requests_total']}</div>
                            <div style="font-size: 0.875rem; color: #6b7280;">Requisições Total</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; font-weight: bold; color: #3b82f6;">{metrics['api_calls']}</div>
                            <div style="font-size: 0.875rem; color: #6b7280;">Chamadas API</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; font-weight: bold; color: #f59e0b;">{metrics['data_processed']}</div>
                            <div style="font-size: 0.875rem; color: #6b7280;">Dados Processados (MB)</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; font-weight: bold; color: #8b5cf6;">{len(metrics['recent_activities'])}</div>
                            <div style="font-size: 0.875rem; color: #6b7280;">Atividades Recentes</div>
                        </div>
                    </div>
                </div>
            """
            
            # Conexões
            connections_html = "<div>"
            for service, status in metrics['connections'].items():
                service_name = service.replace('_', ' ').title()
                connections_html += f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; margin: 0.25rem 0; background: #f9fafb; border-radius: 0.25rem;">
                        <span style="font-weight: 500;">{service_name}</span>
                        <span>{status}</span>
                    </div>
                """
            connections_html += "</div>"
            
            # Atividades
            activities_html = "<div>"
            for activity in metrics['recent_activities']:
                activities_html += f"""
                    <div class="activity-item">
                        <span style="color: #6b7280; font-size: 0.75rem;">{activity['time']}</span><br>
                        <span>{activity['activity']}</span>
                    </div>
                """
            activities_html += "</div>"
            
            # Dados para gráfico
            plot_data = []
            base_time = datetime.now()
            for i in range(10):
                plot_data.append({
                    "time": (base_time - timedelta(minutes=9-i)).strftime("%H:%M"),
                    "value": random.randint(5, 25)
                })
            
            return status_html, metrics_html, connections_html, activities_html, plot_data

        # Auto-update every 3 seconds
        interface.load(
            update_dashboard,
            outputs=[status_display, metrics_display, connections_display, activities_display, activity_plot],
            every=3
        )

    return interface

# Run FastAPI in background
def run_api():
    uvicorn.run(app, host="0.0.0.0", port=7860)

# Start activity simulator
def start_activity_simulator():
    simulator_thread = Thread(target=simulate_backend_activity, daemon=True)
    simulator_thread.start()

# Launch application
if __name__ == "__main__":
    # Start activity simulator
    start_activity_simulator()
    add_activity("Sistema iniciado com sucesso", "system")
    
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