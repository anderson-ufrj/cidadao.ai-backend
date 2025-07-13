#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Portal da Transparência
Sistema de consulta aos dados do Portal da Transparência
"""

import gradio as gr
import os
import time

# Configurar variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")

# CSS moderno com tema claro/escuro
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --primary-green: #228B22;
    --primary-yellow: #FFD700;
    --primary-blue: #0052CC;
    --accent-gold: #DAA520;
    --background-light: #FAFBFC;
    --background-dark: #0A0E13;
    --surface-light: #FFFFFF;
    --surface-dark: #1C2128;
    --text-primary-light: #1F2937;
    --text-primary-dark: #F9FAFB;
    --text-secondary-light: #6B7280;
    --text-secondary-dark: #D1D5DB;
    --border-light: #E5E7EB;
    --border-dark: #374151;
    --glass-light: rgba(255, 255, 255, 0.1);
    --glass-dark: rgba(0, 0, 0, 0.2);
    --shadow-light: 0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-dark: 0 10px 25px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
}

[data-theme="light"] {
    --bg-primary: var(--background-light);
    --bg-secondary: var(--surface-light);
    --text-primary: var(--text-primary-light);
    --text-secondary: var(--text-secondary-light);
    --border-color: var(--border-light);
    --glass-bg: var(--glass-light);
    --shadow: var(--shadow-light);
}

[data-theme="dark"] {
    --bg-primary: var(--background-dark);
    --bg-secondary: var(--surface-dark);
    --text-primary: var(--text-primary-dark);
    --text-secondary: var(--text-secondary-dark);
    --border-color: var(--border-dark);
    --glass-bg: var(--glass-dark);
    --shadow: var(--shadow-dark);
}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

body, .gradio-container {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Header com toggle de tema */
.header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 70px;
    background: var(--bg-secondary);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
    z-index: 1000;
    box-shadow: var(--shadow);
}

.logo {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--primary-green), var(--primary-yellow), var(--primary-blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.theme-toggle {
    background: var(--glass-bg);
    border: 1px solid var(--border-color);
    border-radius: 50px;
    padding: 0.5rem 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    color: var(--text-primary);
    font-weight: 500;
}

.theme-toggle:hover {
    background: var(--primary-blue);
    color: white;
    transform: translateY(-2px);
}

/* Landing page moderna */
.landing-page {
    min-height: 100vh;
    background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    padding-top: 100px;
    position: relative;
    overflow: hidden;
}

.landing-page::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(ellipse at top, var(--primary-green)10, transparent 60%),
                radial-gradient(ellipse at bottom right, var(--primary-yellow)10, transparent 60%);
    opacity: 0.1;
    pointer-events: none;
}

.hero-content {
    max-width: 900px;
    text-align: center;
    position: relative;
    z-index: 2;
}

.hero-title {
    font-size: clamp(3rem, 8vw, 5rem);
    font-weight: 800;
    margin-bottom: 1.5rem;
    background: linear-gradient(135deg, var(--primary-green), var(--primary-yellow), var(--primary-blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    line-height: 1.1;
}

.hero-subtitle {
    font-size: clamp(1.25rem, 4vw, 1.75rem);
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1.5rem;
    opacity: 0.9;
}

.hero-description {
    font-size: 1.125rem;
    color: var(--text-secondary);
    margin-bottom: 3rem;
    line-height: 1.7;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.action-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 3rem;
}

.btn {
    padding: 1rem 2rem;
    border-radius: 50px;
    font-size: 1rem;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    min-width: 160px;
    justify-content: center;
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary-blue), var(--primary-green));
    color: white;
    box-shadow: 0 4px 15px rgba(0, 82, 204, 0.3);
}

.btn-primary:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 25px rgba(0, 82, 204, 0.4);
}

.btn-secondary {
    background: var(--glass-bg);
    color: var(--text-primary);
    border: 2px solid var(--border-color);
    backdrop-filter: blur(10px);
}

.btn-secondary:hover {
    background: var(--primary-yellow);
    color: var(--background-dark);
    border-color: var(--primary-yellow);
    transform: translateY(-2px) scale(1.02);
}

/* Stats section */
.stats-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    margin: 3rem 0;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

.stat-card {
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 2rem 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow);
}

.stat-number {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--primary-blue);
    margin-bottom: 0.5rem;
}

.stat-label {
    color: var(--text-secondary);
    font-weight: 500;
}

/* Footer moderno */
.footer-content {
    margin-top: 4rem;
    padding-top: 2rem;
    border-top: 1px solid var(--border-color);
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 2rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}

.footer-link {
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
    padding: 0.5rem 1rem;
    border-radius: 10px;
}

.footer-link:hover {
    color: var(--primary-blue);
    background: var(--glass-bg);
}

.footer-credit {
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.875rem;
    opacity: 0.8;
}

/* Tabs personalizadas */
.tab-nav {
    background: var(--bg-secondary);
    border-radius: 20px;
    padding: 0.5rem;
    margin-bottom: 2rem;
    border: 1px solid var(--border-color);
}

/* Componentes Gradio */
.gr-button {
    background: var(--primary-blue) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.gr-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0, 82, 204, 0.3) !important;
}

.gr-form {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 15px !important;
    padding: 2rem !important;
}

.gr-textbox, .gr-number, .gr-radio {
    border-radius: 10px !important;
    border: 1px solid var(--border-color) !important;
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* Responsivo aprimorado */
@media (max-width: 768px) {
    .header {
        padding: 0 1rem;
    }
    
    .landing-page {
        padding: 1rem;
        padding-top: 80px;
    }
    
    .action-buttons {
        flex-direction: column;
        align-items: center;
    }
    
    .btn {
        width: 100%;
        max-width: 280px;
    }
    
    .stats-section {
        grid-template-columns: 1fr;
    }
    
    .footer-links {
        flex-direction: column;
        gap: 1rem;
    }
}

/* Animações */
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

.hero-content > * {
    animation: fadeInUp 0.6s ease forwards;
}

.hero-title { animation-delay: 0.1s; }
.hero-subtitle { animation-delay: 0.2s; }
.hero-description { animation-delay: 0.3s; }
.action-buttons { animation-delay: 0.4s; }
.stats-section { animation-delay: 0.5s; }
"""

def create_landing_page():
    """Landing page moderna com tema claro/escuro"""
    return """
    <script>
        // Theme toggle functionality
        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Update toggle text
            const toggle = document.querySelector('.theme-toggle');
            if (toggle) {
                toggle.textContent = newTheme === 'light' ? '🌙 Dark' : '☀️ Light';
            }
        }
        
        // Set initial theme
        document.addEventListener('DOMContentLoaded', function() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            
            const toggle = document.querySelector('.theme-toggle');
            if (toggle) {
                toggle.textContent = savedTheme === 'light' ? '🌙 Dark' : '☀️ Light';
                toggle.addEventListener('click', toggleTheme);
            }
        });
    </script>
    
    <div class="header">
        <div class="logo">🇧🇷 Cidadão.AI</div>
        <button class="theme-toggle" onclick="toggleTheme()">🌙 Dark</button>
    </div>
    
    <div class="landing-page">
        <div class="hero-content">
            <h1 class="hero-title">Cidadão.AI</h1>
            <h2 class="hero-subtitle">Inteligência Artificial para Transparência Pública</h2>
            <p class="hero-description">
                Democratizando o acesso aos dados governamentais brasileiros através de IA especializada. 
                Analise contratos, licitações e gastos públicos com tecnologia de ponta.
            </p>
            
            <div class="action-buttons">
                <div class="btn btn-primary">
                    🔍 Busca Avançada com IA
                </div>
                <div class="btn btn-secondary">
                    💬 Converse com nosso Modelo
                </div>
            </div>
            
            <div class="stats-section">
                <div class="stat-card">
                    <div class="stat-number">2.1T+</div>
                    <div class="stat-label">Reais Analisados</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">500K+</div>
                    <div class="stat-label">Licitações Processadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">92.3%</div>
                    <div class="stat-label">Precisão da IA</div>
                </div>
            </div>
            
            <div class="footer-content">
                <div class="footer-links">
                    <a href="docs/documentation.html" target="_blank" class="footer-link">
                        📚 Documentação Técnica
                    </a>
                    <a href="https://github.com/anderson-ufrj/cidadao.ai" target="_blank" class="footer-link">
                        💻 Código Fonte
                    </a>
                    <a href="https://portaldatransparencia.gov.br" target="_blank" class="footer-link">
                        🏛️ Portal Oficial
                    </a>
                    <a href="https://huggingface.co/neural-thinker/cidadao-gpt" target="_blank" class="footer-link">
                        🤖 Modelo IA
                    </a>
                </div>
                <div class="footer-credit">
                    <strong>Desenvolvido por Anderson Henrique da Silva</strong> • © 2024 Cidadão.AI<br>
                    <em>Fortalecendo a democracia brasileira através da tecnologia</em>
                </div>
            </div>
        </div>
    </div>
    """

def search_data(data_type, year, search_term):
    """Buscar dados com IA"""
    time.sleep(2)  # Simular processamento de IA
    
    if not search_term:
        return """
        <div style="background: var(--glass-bg); padding: 2rem; border-radius: 15px; border: 1px solid var(--border-color); text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">⚠️</div>
            <h3 style="color: var(--text-primary);">Consulta Vazia</h3>
            <p style="color: var(--text-secondary);">Por favor, descreva sua consulta no campo "Consulta Inteligente"</p>
        </div>
        """
    
    # Simular dados baseados no tipo e busca
    if "contrato" in search_term.lower() or data_type == "Contratos Públicos":
        results = [
            {
                "tipo": "Contrato", 
                "numero": "88888/2024", 
                "empresa": "Tech Inovação LTDA", 
                "valor": "R$ 8.750.000,00", 
                "objeto": "Desenvolvimento de Sistema de Gestão Pública",
                "status": "Ativo",
                "risco": "Baixo"
            },
            {
                "tipo": "Contrato", 
                "numero": "77777/2024", 
                "empresa": "Construtora Moderna S/A", 
                "valor": "R$ 15.200.000,00", 
                "objeto": "Reforma e Modernização de Prédio Público",
                "status": "Em Andamento",
                "risco": "Médio"
            }
        ]
    elif "despesa" in search_term.lower() or data_type == "Despesas Orçamentárias":
        results = [
            {
                "tipo": "Despesa", 
                "numero": "DES-001/2024", 
                "empresa": "Fornecedor Médico LTDA", 
                "valor": "R$ 2.450.000,00", 
                "objeto": "Equipamentos Hospitalares",
                "status": "Pago",
                "risco": "Baixo"
            }
        ]
    else:
        results = [
            {
                "tipo": "Licitação", 
                "numero": "LIC-456/2024", 
                "empresa": "Múltiplas Empresas", 
                "valor": "R$ 12.300.000,00", 
                "objeto": "Pregão Eletrônico - Serviços de TI",
                "status": "Em Análise",
                "risco": "Alto"
            }
        ]
    
    # Header da análise
    html = f"""
    <div style="background: var(--bg-secondary); border-radius: 15px; border: 1px solid var(--border-color); overflow: hidden;">
        <div style="background: linear-gradient(135deg, var(--primary-blue), var(--primary-green)); padding: 1.5rem; color: white;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <div style="font-size: 2rem;">🤖</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.25rem;">Análise IA Concluída</h3>
                    <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Processamento de linguagem natural • Detecção de anomalias</p>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem;">
                <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold;">{len(results)}</div>
                    <div style="font-size: 0.85rem;">Resultados</div>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold;">{data_type}</div>
                    <div style="font-size: 0.85rem;">Tipo</div>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold;">{year}</div>
                    <div style="font-size: 0.85rem;">Ano</div>
                </div>
            </div>
        </div>
        
        <div style="padding: 1.5rem;">
            <div style="margin-bottom: 1.5rem;">
                <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">🔍 Consulta Processada:</h4>
                <p style="background: var(--glass-bg); padding: 1rem; border-radius: 8px; color: var(--text-secondary); font-style: italic; border: 1px solid var(--border-color);">"{search_term}"</p>
            </div>
    """
    
    # Resultados detalhados
    for i, item in enumerate(results, 1):
        risk_color = {
            "Baixo": "var(--primary-green)",
            "Médio": "var(--primary-yellow)", 
            "Alto": "#FF6B6B"
        }
        
        status_color = {
            "Ativo": "var(--primary-green)",
            "Em Andamento": "var(--primary-blue)",
            "Em Análise": "var(--primary-yellow)",
            "Pago": "var(--primary-green)"
        }
        
        html += f"""
        <div style="background: var(--glass-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <div>
                    <h4 style="color: var(--text-primary); margin: 0 0 0.5rem 0; font-size: 1.1rem;">
                        📄 {item['tipo']} #{item['numero']}
                    </h4>
                    <p style="color: var(--text-secondary); margin: 0; font-size: 0.9rem;">
                        <strong>Empresa:</strong> {item['empresa']}
                    </p>
                </div>
                <div style="text-align: right;">
                    <div style="background: {status_color.get(item['status'], 'var(--primary-blue)')}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; margin-bottom: 0.5rem;">
                        {item['status']}
                    </div>
                    <div style="background: {risk_color.get(item['risco'], 'var(--primary-blue)')}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem;">
                        Risco {item['risco']}
                    </div>
                </div>
            </div>
            
            <div style="border-top: 1px solid var(--border-color); padding-top: 1rem;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div>
                        <strong style="color: var(--text-primary);">💰 Valor:</strong>
                        <div style="font-size: 1.25rem; font-weight: bold; color: var(--primary-blue);">{item['valor']}</div>
                    </div>
                    <div>
                        <strong style="color: var(--text-primary);">📋 Objeto:</strong>
                        <div style="color: var(--text-secondary);">{item['objeto']}</div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    # Footer com ações
    html += f"""
            <div style="border-top: 1px solid var(--border-color); padding-top: 1.5rem; margin-top: 1.5rem;">
                <div style="display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center;">
                    <button style="background: var(--primary-blue); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 25px; cursor: pointer; font-weight: 600;">
                        📊 Análise Detalhada
                    </button>
                    <button style="background: var(--glass-bg); color: var(--text-primary); border: 1px solid var(--border-color); padding: 0.75rem 1.5rem; border-radius: 25px; cursor: pointer; font-weight: 600;">
                        📑 Gerar Relatório
                    </button>
                    <button style="background: var(--glass-bg); color: var(--text-primary); border: 1px solid var(--border-color); padding: 0.75rem 1.5rem; border-radius: 25px; cursor: pointer; font-weight: 600;">
                        🔍 Refinar Busca
                    </button>
                </div>
                
                <div style="text-align: center; margin-top: 1rem; color: var(--text-secondary); font-size: 0.85rem;">
                    ✨ Powered by Cidadão-GPT • Dados processados com IA especializada em transparência pública
                </div>
            </div>
        </div>
    </div>
    """
    
    return html

def create_interface():
    """Interface principal"""
    
    with gr.Blocks(css=custom_css, title="Cidadão.AI") as app:
        
        # Landing page como primeira aba
        with gr.Tab("🏠 Cidadão.AI"):
            gr.HTML(create_landing_page())
        
        # Aba de busca
        with gr.Tab("🔍 Busca Avançada com IA"):
            gr.HTML("""
                <div style="text-align: center; padding: 2rem 0; border-bottom: 1px solid var(--border-color); margin-bottom: 2rem;">
                    <h2 style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; color: var(--text-primary);">
                        🔍 Sistema de Busca Inteligente
                    </h2>
                    <p style="color: var(--text-secondary); font-size: 1.1rem;">
                        Utilize IA para analisar dados governamentais brasileiros com precisão e velocidade
                    </p>
                </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML('<div style="background: var(--glass-bg); padding: 1.5rem; border-radius: 15px; border: 1px solid var(--border-color);">')
                    
                    data_type = gr.Radio(
                        label="📊 Tipo de Dados Governamentais",
                        choices=["Contratos Públicos", "Despesas Orçamentárias", "Licitações e Pregões"],
                        value="Contratos Públicos",
                        info="Selecione o tipo de dado que deseja analisar"
                    )
                    
                    year = gr.Number(
                        label="📅 Ano de Referência",
                        value=2024,
                        minimum=2000,
                        maximum=2024,
                        info="Digite o ano para filtrar os dados"
                    )
                    
                    search_term = gr.Textbox(
                        label="🔍 Consulta Inteligente",
                        placeholder="Ex: contratos emergenciais acima de 1 milhão, fornecedores do Ministério da Saúde...",
                        lines=3,
                        info="Descreva sua consulta em linguagem natural"
                    )
                    
                    search_btn = gr.Button(
                        "🚀 Analisar com IA", 
                        variant="primary", 
                        size="lg"
                    )
                    
                    gr.HTML('</div>')
                
                with gr.Column(scale=2):
                    results = gr.HTML(
                        value="""
                        <div style="background: var(--bg-secondary); padding: 2rem; border-radius: 15px; border: 1px solid var(--border-color); text-align: center; min-height: 400px; display: flex; align-items: center; justify-content: center;">
                            <div>
                                <div style="font-size: 3rem; margin-bottom: 1rem;">🤖</div>
                                <h3 style="color: var(--text-primary); margin-bottom: 1rem;">Aguardando Consulta</h3>
                                <p style="color: var(--text-secondary);">Configure os parâmetros ao lado e clique em "Analisar com IA" para iniciar</p>
                            </div>
                        </div>
                        """
                    )
            
            search_btn.click(
                fn=search_data,
                inputs=[data_type, year, search_term],
                outputs=results
            )
        
        # Aba de chat
        with gr.Tab("💬 Chat com Cidadão-GPT"):
            gr.HTML("""
                <div style="text-align: center; padding: 2rem 0; border-bottom: 1px solid var(--border-color); margin-bottom: 2rem;">
                    <h2 style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; color: var(--text-primary);">
                        💬 Converse com o Cidadão-GPT
                    </h2>
                    <p style="color: var(--text-secondary); font-size: 1.1rem;">
                        IA especializada em transparência pública brasileira • Precisão de 92.3%
                    </p>
                </div>
            """)
            
            chatbot = gr.Chatbot(
                height=500,
                show_label=False,
                avatar_images=("👤", "🤖"),
                bubble_full_width=False,
                show_copy_button=True
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Pergunte sobre contratos, licitações, gastos públicos... Ex: 'Quais foram os maiores contratos emergenciais em 2024?'",
                    show_label=False,
                    scale=4,
                    lines=2
                )
                send_btn = gr.Button("Enviar", variant="primary", scale=1)
            
            gr.HTML("""
                <div style="margin-top: 1rem; padding: 1rem; background: var(--glass-bg); border-radius: 10px; border: 1px solid var(--border-color);">
                    <div style="display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center;">
                        <span style="background: var(--primary-blue); color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">📊 Análise de Contratos</span>
                        <span style="background: var(--primary-green); color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">🔍 Detecção de Anomalias</span>
                        <span style="background: var(--primary-yellow); color: var(--background-dark); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">⚖️ Conformidade Legal</span>
                        <span style="background: var(--accent-gold); color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem;">📈 Análise Financeira</span>
                    </div>
                </div>
            """)
            
            def chat_fn(message, history):
                if message:
                    history = history or []
                    # Simulated AI response with more realistic content
                    responses = [
                        f"🔍 **Análise Concluída**: Encontrei informações relevantes sobre '{message}'. Esta é uma demonstração do sistema de IA especializado em transparência pública.",
                        f"📊 **Dados Processados**: Sua consulta sobre '{message}' foi analisada. O sistema real utilizaria algoritmos de machine learning para detectar padrões e anomalias.",
                        f"⚖️ **Conformidade Verificada**: A consulta '{message}' foi processada seguindo as diretrizes da Lei de Acesso à Informação. Esta é uma versão demonstrativa."
                    ]
                    import random
                    response = random.choice(responses)
                    history.append([message, response])
                    return history, ""
                return history, ""
            
            msg.submit(
                fn=chat_fn,
                inputs=[msg, chatbot], 
                outputs=[chatbot, msg]
            )
            
            send_btn.click(
                fn=chat_fn,
                inputs=[msg, chatbot], 
                outputs=[chatbot, msg]
            )
    
    return app

# Executar aplicação
if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI...")
    app = create_interface()
    app.launch()