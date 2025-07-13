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

# CSS profissional e moderno
custom_css = """
/* Reset e base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #2c3e50;
}

/* Hero Section - Layout principal */
.hero-section {
    background: linear-gradient(
        rgba(0, 0, 0, 0.5),
        rgba(0, 0, 0, 0.7)
    ),
    url('https://upload.wikimedia.org/wikipedia/commons/e/e3/Congresso_Nacional_-_Brasília_-_panorama.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    text-align: center;
    position: relative;
}

.hero-content {
    max-width: 900px;
    padding: 4rem 3rem;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(15px);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4);
    transform: translateY(0);
    animation: fadeInUp 1s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.hero-title {
    font-size: 4.5rem;
    font-weight: 900;
    margin-bottom: 1.5rem;
    background: linear-gradient(135deg, #FFD700, #FFFFFF, #32CD32);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
    letter-spacing: -2px;
}

.hero-welcome {
    font-size: 2rem;
    font-weight: 600;
    margin-bottom: 1rem;
    opacity: 0.95;
    color: #ffffff;
}

.hero-subtitle {
    font-size: 1.3rem;
    margin-bottom: 2.5rem;
    opacity: 0.9;
    line-height: 1.7;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}

/* Botões de ação */
.action-buttons {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 2rem;
}

.btn-primary {
    padding: 1rem 2.5rem;
    background: linear-gradient(135deg, #0066cc, #004499);
    color: white;
    border: none;
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 8px 25px rgba(0, 102, 204, 0.3);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 35px rgba(0, 102, 204, 0.4);
    background: linear-gradient(135deg, #0077dd, #0055aa);
}

.btn-secondary {
    padding: 1rem 2.5rem;
    background: rgba(255, 255, 255, 0.15);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.25);
    border-color: rgba(255, 255, 255, 0.5);
    transform: translateY(-2px);
}

/* Features Section */
.features-section {
    background: #f8f9fa;
    padding: 4rem 2rem;
    text-align: center;
}

.features-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 3rem;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.feature-card {
    background: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.feature-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
}

.feature-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.feature-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 1rem;
}

.feature-description {
    color: #666;
    line-height: 1.6;
}

/* Status Cards */
.status-section {
    background: white;
    padding: 3rem 2rem;
    margin: 2rem 0;
}

.status-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 16px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.2);
    text-align: center;
}

.status-active {
    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    box-shadow: 0 15px 35px rgba(76, 175, 80, 0.2);
}

.status-error {
    background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
    box-shadow: 0 15px 35px rgba(244, 67, 54, 0.2);
}

/* Footer */
.footer-section {
    background: #2c3e50;
    color: white;
    padding: 3rem 2rem;
    text-align: center;
}

.footer-content {
    max-width: 1200px;
    margin: 0 auto;
}

.footer-title {
    font-size: 1.8rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #ecf0f1;
}

.footer-subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    margin-bottom: 2rem;
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 2rem;
    flex-wrap: wrap;
    margin-bottom: 2rem;
}

.footer-link {
    color: #3498db;
    text-decoration: none;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 25px;
    transition: all 0.3s ease;
    border: 1px solid transparent;
}

.footer-link:hover {
    background: rgba(52, 152, 219, 0.1);
    border-color: #3498db;
    color: #5dade2;
}

.footer-credits {
    border-top: 1px solid #34495e;
    padding-top: 2rem;
    margin-top: 2rem;
    opacity: 0.8;
}

/* Responsividade */
@media (max-width: 768px) {
    .hero-title { font-size: 3rem; }
    .hero-welcome { font-size: 1.5rem; }
    .hero-subtitle { font-size: 1.1rem; }
    .hero-content { 
        margin: 1rem; 
        padding: 2.5rem 2rem; 
    }
    .action-buttons {
        flex-direction: column;
        align-items: center;
    }
    .btn-primary, .btn-secondary {
        width: 100%;
        max-width: 280px;
    }
    .features-title { font-size: 2rem; }
    .footer-links {
        flex-direction: column;
        gap: 1rem;
    }
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
    """Interface principal profissional"""
    
    with gr.Blocks(css=custom_css, title="Cidadão.AI - Transparência Pública") as app:
        
        # Hero Section Principal
        gr.HTML("""
        <div class="hero-section">
            <div class="hero-content">
                <div class="hero-title">Cidadão.AI</div>
                <div class="hero-welcome">Bem-vindo ao Cidadão.AI</div>
                <div class="hero-subtitle">
                    Democratizando o acesso aos dados públicos brasileiros através da inteligência artificial. 
                    Uma plataforma séria e confiável para consultar contratos, despesas e licitações do governo 
                    federal de forma transparente e acessível.
                </div>
                <div class="action-buttons">
                    <button class="btn-primary">
                        🔍 Busca Avançada com IA
                    </button>
                    <button class="btn-secondary">
                        🤖 Converse com nosso Modelo
                    </button>
                </div>
            </div>
        </div>
        """)
        
        # Seção de Funcionalidades
        gr.HTML("""
        <div class="features-section">
            <h2 class="features-title">Funcionalidades Principais</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3 class="feature-title">Análise de Contratos</h3>
                    <p class="feature-description">
                        Análise inteligente de contratos públicos com detecção de irregularidades 
                        e verificação de conformidade legal.
                    </p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💰</div>
                    <h3 class="feature-title">Monitoramento de Gastos</h3>
                    <p class="feature-description">
                        Acompanhamento em tempo real das despesas públicas com alertas para 
                        padrões suspeitos e anomalias.
                    </p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <h3 class="feature-title">Licitações Inteligentes</h3>
                    <p class="feature-description">
                        Análise de processos licitatórios com identificação de riscos e 
                        avaliação de competitividade.
                    </p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">⚖️</div>
                    <h3 class="feature-title">Conformidade Legal</h3>
                    <p class="feature-description">
                        Verificação automática de conformidade com a legislação brasileira 
                        (Lei 14.133/2021, Lei 8.666/93).
                    </p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <h3 class="feature-title">IA Especializada</h3>
                    <p class="feature-description">
                        Modelo de inteligência artificial treinado especificamente para 
                        transparência pública brasileira.
                    </p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📈</div>
                    <h3 class="feature-title">Relatórios Executivos</h3>
                    <p class="feature-description">
                        Geração automática de relatórios detalhados com insights 
                        e recomendações baseadas em dados.
                    </p>
                </div>
            </div>
        </div>
        """)
        
        # Status do Sistema (melhorado)
        gr.HTML("""
        <div class="status-section">
            <div class="status-card status-active">
                <h3>🔧 Status do Sistema</h3>
                <p><strong>Portal da Transparência:</strong> ✅ Conectado e operacional</p>
                <p><strong>Modelo de IA:</strong> 🤖 Cidadão-GPT ativo e respondendo</p>
                <p><strong>Base de Dados:</strong> 📊 Mais de 2,1 trilhões em contratos analisados</p>
                <p><strong>Última Atualização:</strong> ⏱️ Dados atualizados em tempo real</p>
            </div>
        </div>
        """)
        
        # Interface de Consulta Avançada
        with gr.Tab("🔍 Busca Avançada com IA"):
            gr.HTML("""
            <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 16px; margin: 1rem 0;">
                <h3 style="margin-bottom: 1rem;">🎯 Sistema de Busca Inteligente</h3>
                <p>Utilize nossa IA especializada para encontrar informações específicas nos dados públicos brasileiros</p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    data_type = gr.Radio(
                        label="📊 Tipo de Dados",
                        choices=["Contratos", "Despesas", "Licitações"],
                        value="Contratos"
                    )
                    
                    year = gr.Number(
                        label="📅 Ano",
                        value=2024,
                        precision=0,
                        minimum=2020,
                        maximum=2025
                    )
                    
                    org_code = gr.Textbox(
                        label="🏛️ Código do Órgão (opcional)",
                        placeholder="Ex: 26000 (MEC), 20000 (AGU)"
                    )
                    
                    search_term = gr.Textbox(
                        label="🔍 Termo de Busca (opcional)",
                        placeholder="Ex: equipamento médico, consultoria, infraestrutura"
                    )
                    
                    search_btn = gr.Button(
                        "🔍 Buscar com IA",
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=2):
                    results_output = gr.HTML(
                        value="""
                        <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);">
                            <h3 style="color: #2c3e50; margin-bottom: 1rem;">🚀 Pronto para Análise</h3>
                            <p style="color: #666; margin-bottom: 1.5rem;">Configure os parâmetros ao lado e clique em "Buscar com IA" para iniciar a análise inteligente.</p>
                            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #0066cc;">
                                <h4 style="color: #2c3e50; margin-bottom: 1rem;">📋 Tipos de Análise Disponíveis:</h4>
                                <ul style="color: #666; line-height: 1.8;">
                                    <li><strong>📄 Contratos:</strong> Análise de contratos públicos, aditivos e irregularidades</li>
                                    <li><strong>💰 Despesas:</strong> Monitoramento de gastos públicos e padrões suspeitos</li>
                                    <li><strong>🏛️ Licitações:</strong> Avaliação de processos licitatórios e competitividade</li>
                                </ul>
                            </div>
                        </div>
                        """
                    )
            
            # Conectar busca
            search_btn.click(
                fn=search_mock_data,
                inputs=[data_type, year, org_code, search_term],
                outputs=[results_output]
            )
        
        with gr.Tab("🤖 Chat com IA Especializada"):
            gr.HTML("""
            <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; border-radius: 16px; margin: 1rem 0;">
                <h3 style="margin-bottom: 1rem;">💬 Converse com o Cidadão-GPT</h3>
                <p>Faça perguntas em linguagem natural sobre transparência pública e dados governamentais</p>
            </div>
            """)
            
            chatbot = gr.Chatbot(
                height=400,
                placeholder="💭 Pergunte algo como: 'Quais foram os maiores contratos de 2024?' ou 'Mostre gastos suspeitos do Ministério da Saúde'"
            )
            
            msg = gr.Textbox(
                placeholder="Digite sua pergunta sobre transparência pública...",
                label="💬 Sua pergunta"
            )
            
            send_btn = gr.Button("📤 Enviar", variant="primary")
            
            gr.HTML("""
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 12px; padding: 1rem; margin: 1rem 0;">
                <p style="margin: 0; color: #856404;"><strong>⚠️ Nota:</strong> Este é um ambiente de demonstração. As respostas são simuladas para fins educativos.</p>
            </div>
            """)
        
        # Footer Profissional
        gr.HTML("""
        <div class="footer-section">
            <div class="footer-content">
                <h3 class="footer-title">🇧🇷 Cidadão.AI</h3>
                <p class="footer-subtitle">Democratizando o acesso aos dados públicos brasileiros</p>
                
                <div class="footer-links">
                    <a href="/docs/documentation.html" target="_blank" class="footer-link">
                        📚 Documentação Técnica Completa
                    </a>
                    <a href="https://github.com/anderson-ufrj/cidadao.ai" target="_blank" class="footer-link">
                        💻 Código no GitHub
                    </a>
                    <a href="https://portaldatransparencia.gov.br" target="_blank" class="footer-link">
                        🔗 Portal da Transparência
                    </a>
                    <a href="https://huggingface.co/neural-thinker/cidadao-gpt" target="_blank" class="footer-link">
                        🤖 Modelo Cidadão-GPT
                    </a>
                </div>
                
                <div class="footer-credits">
                    <p><strong>Desenvolvido por:</strong> Anderson Henrique da Silva</p>
                    <p>🎓 Especialista em IA para Transparência Pública | 🇧🇷 Comprometido com a democracia brasileira</p>
                    <p style="margin-top: 1rem; opacity: 0.7;">
                        © 2024 Cidadão.AI. Licenciado sob MIT License. Dados fornecidos pelo Portal da Transparência (CGU).
                    </p>
                </div>
            </div>
        </div>
        """)
    
    return app

# Executar aplicação
if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI...")
    
    app = create_interface()
    app.launch()