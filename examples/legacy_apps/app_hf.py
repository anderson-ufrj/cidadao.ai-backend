"""
Cidadão.AI - Versão Hugging Face Spaces
Interface Gradio para transparência pública com IA
"""

import gradio as gr
import asyncio
from datetime import datetime
from typing import List, Dict, Any

# Importar nossos módulos
from src.agents.master_agent import MasterAgent
from src.agents.investigator_agent import InvestigatorAgent
from src.agents.analyst_agent import AnalystAgent
from src.llm.groq_service import GroqService
from src.tools.transparency_api_client import TransparencyAPIClient

# CSS customizado para a interface
custom_css = """
#title {
    text-align: center;
    color: #0066cc;
}
.gradio-container {
    font-family: 'Inter', sans-serif;
}
.output-markdown {
    padding: 20px;
    background-color: #f8f9fa;
    border-radius: 8px;
}
"""

# Inicializar agentes
llm_service = GroqService()
master_agent = MasterAgent("master-1", llm_service)
investigator = InvestigatorAgent("investigator-1", llm_service)
analyst = AnalystAgent("analyst-1", llm_service)

async def investigate_spending(
    query: str,
    data_source: str,
    organization: str,
    date_start: str,
    date_end: str,
    include_analysis: bool
) -> str:
    """Processar investigação de gastos públicos"""
    try:
        # Criar contexto da investigação
        context = {
            "query": query,
            "data_source": data_source,
            "organization": organization if organization else None,
            "date_range": {
                "start": date_start if date_start else None,
                "end": date_end if date_end else None
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Executar investigação
        result = await master_agent.investigate(context)
        
        # Formatar resultado em Markdown
        output = f"# 🔍 Resultados da Investigação\n\n"
        output += f"**Query**: {query}\n\n"
        
        if result.get("anomalies"):
            output += "## 🚨 Anomalias Detectadas\n\n"
            for i, anomaly in enumerate(result["anomalies"], 1):
                output += f"### {i}. {anomaly['type']}\n"
                output += f"- **Confiança**: {anomaly['confidence']:.1%}\n"
                output += f"- **Descrição**: {anomaly['description']}\n"
                output += f"- **Impacto**: {anomaly.get('impact', 'N/A')}\n\n"
        
        if include_analysis and result.get("analysis"):
            output += "## 📊 Análise Detalhada\n\n"
            output += result["analysis"] + "\n\n"
        
        if result.get("recommendations"):
            output += "## 💡 Recomendações\n\n"
            for rec in result["recommendations"]:
                output += f"- {rec}\n"
        
        return output
        
    except Exception as e:
        return f"❌ Erro na investigação: {str(e)}"

def analyze_patterns(
    analysis_type: str,
    data_source: str,
    time_period: str
) -> str:
    """Analisar padrões nos dados"""
    try:
        # Executar análise de forma síncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        context = {
            "type": analysis_type,
            "source": data_source,
            "period": time_period
        }
        
        result = loop.run_until_complete(analyst.analyze_patterns(context))
        
        # Formatar resultado
        output = f"# 📈 Análise de {analysis_type}\n\n"
        output += f"**Período**: {time_period}\n"
        output += f"**Fonte**: {data_source}\n\n"
        
        if result.get("insights"):
            output += "## Insights Principais\n\n"
            for insight in result["insights"]:
                output += f"- {insight}\n"
        
        return output
        
    except Exception as e:
        return f"❌ Erro na análise: {str(e)}"

# Interface Gradio
with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as app:
    gr.Markdown(
        """
        <h1 id="title">🏛️ Cidadão.AI - Transparência Pública com Inteligência Artificial</h1>
        <p align="center">Investigue gastos públicos e detecte anomalias usando IA avançada</p>
        """
    )
    
    with gr.Tabs():
        # Aba de Investigação
        with gr.TabItem("🔍 Investigar Gastos"):
            with gr.Row():
                with gr.Column(scale=1):
                    query_input = gr.Textbox(
                        label="O que você quer investigar?",
                        placeholder="Ex: contratos suspeitos do ministério da saúde",
                        lines=2
                    )
                    
                    data_source = gr.Dropdown(
                        label="Fonte de Dados",
                        choices=["contratos", "despesas", "licitações", "convênios"],
                        value="contratos"
                    )
                    
                    organization = gr.Textbox(
                        label="Órgão (opcional)",
                        placeholder="Ex: 26000 (Ministério da Educação)"
                    )
                    
                    with gr.Row():
                        date_start = gr.Textbox(
                            label="Data Início",
                            placeholder="YYYY-MM-DD"
                        )
                        date_end = gr.Textbox(
                            label="Data Fim", 
                            placeholder="YYYY-MM-DD"
                        )
                    
                    include_analysis = gr.Checkbox(
                        label="Incluir análise detalhada",
                        value=True
                    )
                    
                    investigate_btn = gr.Button(
                        "🔍 Investigar",
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=2):
                    investigation_output = gr.Markdown(
                        label="Resultados",
                        elem_classes=["output-markdown"]
                    )
            
            # Exemplos
            gr.Examples(
                examples=[
                    ["contratos emergenciais com valores acima da média", "contratos", "", "", "", True],
                    ["fornecedores com múltiplos contratos pequenos", "contratos", "", "", "", True],
                    ["despesas com diárias e passagens", "despesas", "", "2024-01-01", "2024-12-31", False]
                ],
                inputs=[query_input, data_source, organization, date_start, date_end, include_analysis]
            )
        
        # Aba de Análise
        with gr.TabItem("📊 Análise de Padrões"):
            with gr.Row():
                with gr.Column():
                    analysis_type = gr.Radio(
                        label="Tipo de Análise",
                        choices=[
                            "Tendências de Gastos",
                            "Concentração de Fornecedores",
                            "Padrões Temporais",
                            "Anomalias Estatísticas"
                        ],
                        value="Tendências de Gastos"
                    )
                    
                    analysis_source = gr.Dropdown(
                        label="Fonte de Dados",
                        choices=["contratos", "despesas", "todos"],
                        value="contratos"
                    )
                    
                    time_period = gr.Radio(
                        label="Período",
                        choices=["Último mês", "Últimos 3 meses", "Último ano"],
                        value="Últimos 3 meses"
                    )
                    
                    analyze_btn = gr.Button("📊 Analisar", variant="primary")
                
                with gr.Column():
                    analysis_output = gr.Markdown(
                        label="Resultados da Análise",
                        elem_classes=["output-markdown"]
                    )
        
        # Aba Sobre
        with gr.TabItem("ℹ️ Sobre"):
            gr.Markdown(
                """
                ## Sobre o Cidadão.AI
                
                O **Cidadão.AI** é uma plataforma de transparência pública que usa Inteligência Artificial
                para analisar gastos governamentais e detectar possíveis irregularidades.
                
                ### 🎯 Funcionalidades
                - **Investigação Inteligente**: Busca anomalias em contratos e despesas
                - **Análise de Padrões**: Identifica tendências e comportamentos suspeitos
                - **Processamento em Tempo Real**: Análise rápida de grandes volumes de dados
                - **Explicações em Português**: Resultados claros e compreensíveis
                
                ### 🔒 Privacidade
                - Todos os dados são públicos (Portal da Transparência)
                - Não armazenamos informações pessoais
                - Análises são feitas em tempo real
                
                ### 🤝 Contribua
                Este é um projeto open-source! Contribua em:
                [github.com/seu-usuario/cidadao-ai](https://github.com/seu-usuario/cidadao-ai)
                
                ---
                Feito com ❤️ para o Brasil
                """
            )
    
    # Conectar eventos
    investigate_btn.click(
        fn=investigate_spending,
        inputs=[query_input, data_source, organization, date_start, date_end, include_analysis],
        outputs=investigation_output
    )
    
    analyze_btn.click(
        fn=analyze_patterns,
        inputs=[analysis_type, analysis_source, time_period],
        outputs=analysis_output
    )

# Configurar para Hugging Face Spaces
app.queue(concurrency_count=3)
app.launch(
    share=False,
    server_name="0.0.0.0",
    server_port=7860
)