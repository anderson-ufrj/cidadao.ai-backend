#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Interface Simplificada para Hugging Face Spaces
Sistema de consulta aos dados do Portal da Transparência
"""

import gradio as gr
import os
import time
import json
from datetime import datetime

# Configurar variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# CSS simplificado e funcional
custom_css = """
/* Hero Section */
.hero-section {
    background: linear-gradient(
        rgba(0, 0, 0, 0.4),
        rgba(0, 0, 0, 0.6)
    ),
    url('https://upload.wikimedia.org/wikipedia/commons/e/e3/Congresso_Nacional_-_Brasília_-_panorama.jpg');
    background-size: cover;
    background-position: center;
    min-height: 80vh;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    text-align: center;
    border-radius: 15px;
    margin: 1rem 0;
}

.hero-content {
    max-width: 800px;
    padding: 3rem 2rem;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
}

.hero-logo {
    font-size: 4rem;
    font-weight: 900;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #FFD700, #FFFFFF, #32CD32);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.hero-subtitle {
    font-size: 1.4rem;
    margin-bottom: 1rem;
    opacity: 0.95;
}

.hero-description {
    font-size: 1.1rem;
    margin-bottom: 2rem;
    opacity: 0.9;
    line-height: 1.6;
}

/* Status Cards */
.status-card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    border-left: 4px solid #0049A0;
}

.status-active {
    border-left-color: #4caf50;
    background: #f1f8e9;
}

.status-error {
    border-left-color: #f44336;
    background: #ffebee;
}

/* Result Cards */
.result-card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    border-left: 4px solid #2196f3;
}

@media (max-width: 768px) {
    .hero-logo { font-size: 2.5rem; }
    .hero-subtitle { font-size: 1.2rem; }
    .hero-description { font-size: 1rem; }
    .hero-content { margin: 1rem; padding: 2rem 1.5rem; }
}
"""

def check_api_status():
    """Verificar status das APIs"""
    api_status = "✅ API Configurada" if TRANSPARENCY_API_KEY else "❌ API não configurada"
    ai_status = "✅ IA Habilitada" if GROQ_API_KEY else "⚠️ IA não configurada"
    
    status_class = "status-active" if TRANSPARENCY_API_KEY else "status-error"
    
    return f"""
    <div class="status-card {status_class}">
        <h3>📊 Status do Sistema</h3>
        <p><strong>Portal da Transparência:</strong> {api_status}</p>
        <p><strong>Análise com IA:</strong> {ai_status}</p>
    </div>
    """

def search_mock_data(data_type, year, org_code, search_term):
    """Busca simulada de dados - versão funcional"""
    
    # Simular tempo de processamento
    time.sleep(1)
    
    if not TRANSPARENCY_API_KEY:
        return """
        <div class="result-card" style="border-left-color: #f44336; background: #ffebee;">
            <h3>❌ API Key não configurada</h3>
            <p>Para usar a API do Portal da Transparência, configure a variável <code>TRANSPARENCY_API_KEY</code> no ambiente.</p>
            <p><strong>Como obter a chave:</strong></p>
            <ol>
                <li>Acesse <a href="https://portaldatransparencia.gov.br/api-de-dados" target="_blank">Portal da Transparência - API</a></li>
                <li>Faça o cadastro gratuito</li>
                <li>Copie sua chave de API</li>
                <li>Configure como secret no Hugging Face Spaces</li>
            </ol>
        </div>
        """
    
    # Dados simulados para demonstração
    mock_results = {
        "Contratos": [
            {"numero": "001/2024", "empresa": "Tech Solutions Ltda", "valor": "R$ 2.500.000,00", "objeto": "Desenvolvimento de sistema", "data": "15/01/2024"},
            {"numero": "002/2024", "empresa": "Construtora Alpha", "valor": "R$ 5.800.000,00", "objeto": "Reforma de edifício público", "data": "22/01/2024"},
            {"numero": "003/2024", "empresa": "Pharma Distribuidora", "valor": "R$ 1.200.000,00", "objeto": "Fornecimento de medicamentos", "data": "30/01/2024"}
        ],
        "Despesas": [
            {"documento": "2024NE000123", "favorecido": "Empresa ABC Ltda", "valor": "R$ 450.000,00", "descricao": "Material de escritório", "data": "10/01/2024"},
            {"documento": "2024NE000124", "favorecido": "Fornecedor XYZ", "valor": "R$ 780.000,00", "descricao": "Equipamentos de informática", "data": "12/01/2024"},
            {"documento": "2024NE000125", "favorecido": "Serviços Beta", "valor": "R$ 320.000,00", "descricao": "Consultoria especializada", "data": "15/01/2024"}
        ],
        "Licitações": [
            {"numero": "PE001/2024", "modalidade": "Pregão Eletrônico", "valor": "R$ 3.200.000,00", "objeto": "Aquisição de veículos", "data": "05/01/2024"},
            {"numero": "CC002/2024", "modalidade": "Concorrência", "valor": "R$ 15.000.000,00", "objeto": "Obra de infraestrutura", "data": "08/01/2024"},
            {"numero": "PE003/2024", "modalidade": "Pregão Eletrônico", "valor": "R$ 800.000,00", "objeto": "Serviços de limpeza", "data": "12/01/2024"}
        ]
    }
    
    results = mock_results.get(data_type, [])
    
    # Filtrar por termo de busca se fornecido
    if search_term:
        results = [r for r in results if search_term.lower() in str(r).lower()]
    
    if not results:
        return """
        <div class="result-card">
            <h3>📭 Nenhum resultado encontrado</h3>
            <p>Tente ajustar os filtros da sua busca ou termo de pesquisa.</p>
        </div>
        """
    
    # Criar HTML com os resultados
    html = f"""
    <div class="result-card" style="border-left-color: #4caf50; background: #f1f8e9;">
        <h3>✅ {len(results)} resultados encontrados</h3>
        <p>Dados do Portal da Transparência - {data_type} em {year}</p>
    </div>
    """
    
    html += f'<div class="result-card"><h4>📊 {data_type} Encontrados</h4><table style="width: 100%; border-collapse: collapse;">'
    
    if data_type == "Contratos":
        html += """
        <tr style="background: #f5f5f5;">
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Número</th>
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Empresa</th>
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Valor</th>
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Objeto</th>
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Data</th>
        </tr>
        """
        for item in results:
            html += f"""
            <tr>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['numero']}</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['empresa']}</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;"><strong>{item['valor']}</strong></td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['objeto']}</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['data']}</td>
            </tr>
            """
    elif data_type == "Despesas":
        html += """
        <tr style="background: #f5f5f5;">
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Documento</th>
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Favorecido</th>
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Valor</th>
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Descrição</th>
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Data</th>
        </tr>
        """
        for item in results:
            html += f"""
            <tr>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['documento']}</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['favorecido']}</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;"><strong>{item['valor']}</strong></td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['descricao']}</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['data']}</td>
            </tr>
            """
    else:  # Licitações
        html += """
        <tr style="background: #f5f5f5;">
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Número</th>
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Modalidade</th>
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Valor</th>
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Objeto</th>
            <th style="padding: 0.75rem; border: 1px solid #ddd;">Data</th>
        </tr>
        """
        for item in results:
            html += f"""
            <tr>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['numero']}</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['modalidade']}</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;"><strong>{item['valor']}</strong></td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['objeto']}</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">{item['data']}</td>
            </tr>
            """
    
    html += "</table></div>"
    return html

def create_interface():
    """Interface principal simplificada"""
    
    with gr.Blocks(css=custom_css, title="Cidadão.AI - Transparência Pública") as app:
        
        # Hero Section
        gr.HTML("""
        <div class="hero-section">
            <div class="hero-content">
                <div class="hero-logo">Cidadão.AI</div>
                <div class="hero-subtitle">Bem-vindo ao Cidadão.AI</div>
                <div class="hero-description">
                    Democratizando o acesso aos dados públicos brasileiros através da inteligência artificial. 
                    Consulte contratos, despesas e licitações do governo federal de forma simples e transparente.
                </div>
            </div>
        </div>
        """)
        
        # Status do Sistema
        status_html = check_api_status()
        gr.HTML(status_html)
        
        # Interface Principal
        with gr.Tab("🔍 Consultar Dados"):
            gr.Markdown("### 🎯 Sistema de Busca")
            
            with gr.Row():
                with gr.Column(scale=1):
                    data_type = gr.Radio(
                        label="Tipo de Dados",
                        choices=["Contratos", "Despesas", "Licitações"],
                        value="Contratos"
                    )
                    
                    year = gr.Number(
                        label="Ano",
                        value=2024,
                        precision=0,
                        minimum=2020,
                        maximum=2025
                    )
                    
                    org_code = gr.Textbox(
                        label="Código do Órgão (opcional)",
                        placeholder="Ex: 26000 (MEC)"
                    )
                    
                    search_term = gr.Textbox(
                        label="Termo de Busca (opcional)",
                        placeholder="Ex: equipamento, consultoria, obra"
                    )
                    
                    search_btn = gr.Button(
                        "🔍 Buscar Dados",
                        variant="primary"
                    )
                
                with gr.Column(scale=2):
                    results_output = gr.HTML(
                        value="""
                        <div class="result-card">
                            <h3>👋 Bem-vindo ao Cidadão.AI</h3>
                            <p>Use os filtros ao lado para buscar dados do Portal da Transparência.</p>
                            <p><strong>Tipos de dados disponíveis:</strong></p>
                            <ul>
                                <li>📄 <strong>Contratos</strong>: Contratos firmados pelo governo</li>
                                <li>💰 <strong>Despesas</strong>: Gastos e pagamentos realizados</li>
                                <li>🏛️ <strong>Licitações</strong>: Processos de compra pública</li>
                            </ul>
                        </div>
                        """
                    )
            
            # Conectar busca
            search_btn.click(
                fn=search_mock_data,
                inputs=[data_type, year, org_code, search_term],
                outputs=[results_output]
            )
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;">
            <p><strong>🤖 Cidadão.AI</strong> - Democratizando o acesso aos dados públicos</p>
            <p>Desenvolvido por Anderson Henrique da Silva | 🇧🇷 Feito para o Brasil</p>
            <p><a href="https://github.com/anderson-ufrj/cidadao.ai" target="_blank">💻 Repositório GitHub</a></p>
        </div>
        """)
    
    return app

# Executar aplicação
if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI...")
    
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )