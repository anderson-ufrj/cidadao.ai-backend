#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Portal da Transparência
PROFESSIONAL UX/UI - Anthropic Designer Level
"""

import gradio as gr
import os
import time
from datetime import datetime

# Configurar variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Função de chat aprimorada
def chat_fn(message, history):
    """Função de chat com typing indicator"""
    if not message:
        return history, ""
    
    # Simular typing delay para UX realista
    time.sleep(0.5)
    
    # Resposta contextual baseada no input
    if "contrato" in message.lower():
        response = f"🔍 **Análise de Contratos:** Sobre '{message}' - Posso ajudar você a analisar contratos públicos, verificar valores, fornecedores e modalidades de licitação. Que aspecto específico você gostaria de investigar?"
    elif "licitação" in message.lower():
        response = f"📋 **Análise de Licitações:** Sobre '{message}' - Posso auxiliar na análise de processos licitatórios, verificar regularidade, prazos e documentação. Qual processo você gostaria de examinar?"
    elif "despesa" in message.lower():
        response = f"💰 **Análise de Despesas:** Sobre '{message}' - Posso ajudar a investigar gastos públicos, identificar anomalias e verificar conformidade orçamentária. Que tipo de despesa você quer analisar?"
    else:
        response = f"🤖 **Assistente de Transparência:** Entendi sua consulta sobre '{message}'. Sou especializado em análise de transparência pública. Posso ajudar com contratos, licitações, despesas e conformidade legal. Como posso ser mais específico?"
    
    history.append((message, response))
    return history, ""

# Função de busca aprimorada
def search_data(data_type, year, search_term):
    """Função de busca com resultados estruturados"""
    if not search_term:
        return "💡 **Dica:** Digite um termo de busca para começar sua investigação de transparência pública."
    
    # Simular delay de busca para UX realista
    time.sleep(0.8)
    
    # Resultados estruturados baseados no tipo
    if data_type == "Contratos Públicos":
        results = f"""
# 🔍 **Resultados da Investigação - Contratos Públicos**

**📊 Resumo da Busca:**
- 🎯 **Termo:** {search_term}
- 📅 **Ano:** {year}
- 📈 **Encontrados:** 247 contratos
- 💰 **Valor Total:** R$ 15.750.000,00

---

## 🏆 **Principais Contratos Identificados:**

### 1. **Contrato #2024-001** 
**💰 Valor:** R$ 2.500.000,00 | **📊 Status:** ⚠️ **Requer Análise**
- **🏢 Fornecedor:** Empresa ABC Tecnologia Ltda
- **📋 Modalidade:** Dispensa de Licitação
- **⏱️ Prazo:** 12 meses
- **🚨 Alertas:** Valor acima da média (25%)

### 2. **Contrato #2024-002**
**💰 Valor:** R$ 1.850.000,00 | **📊 Status:** ✅ **Regular**
- **🏢 Fornecedor:** Empresa XYZ Serviços S/A
- **📋 Modalidade:** Pregão Eletrônico
- **⏱️ Prazo:** 24 meses
- **✅ Conformidade:** Processo regular

### 3. **Contrato #2024-003**
**💰 Valor:** R$ 3.200.000,00 | **📊 Status:** 🔍 **Em Análise**
- **🏢 Fornecedor:** Empresa 123 Consultoria Ltda
- **📋 Modalidade:** Concorrência Pública
- **⏱️ Prazo:** 36 meses
- **🔍 Observações:** Documentação em verificação

---

## 📈 **Análise Estatística:**
- **🎯 Regularidade:** 68% dos contratos em conformidade
- **⚠️ Atenção:** 32% necessitam análise adicional
- **💡 Recomendação:** Focar nos contratos com dispensa de licitação

**🔍 Quer análise mais detalhada? Use filtros específicos.**
        """
    elif data_type == "Despesas Orçamentárias":
        results = f"""
# 💰 **Análise de Despesas Orçamentárias**

**📊 Resumo da Investigação:**
- 🎯 **Termo:** {search_term}
- 📅 **Ano:** {year}
- 📈 **Registros:** 1.342 despesas
- 💸 **Valor Total:** R$ 8.950.000,00

---

## 🏆 **Principais Despesas Identificadas:**

### 1. **Despesa #ORÇ-2024-001**
**💰 Valor:** R$ 450.000,00 | **📊 Status:** ✅ **Aprovada**
- **🏢 Órgão:** Secretaria de Educação
- **📋 Categoria:** Material Permanente
- **🎯 Finalidade:** Equipamentos educacionais
- **✅ Conformidade:** Dentro do orçamento

### 2. **Despesa #ORÇ-2024-002**
**💰 Valor:** R$ 780.000,00 | **📊 Status:** ⚠️ **Verificação**
- **🏢 Órgão:** Secretaria de Saúde
- **📋 Categoria:** Serviços Terceirizados
- **🎯 Finalidade:** Manutenção hospitalar
- **⚠️ Alerta:** Valor 15% acima do previsto

### 3. **Despesa #ORÇ-2024-003**
**💰 Valor:** R$ 1.200.000,00 | **📊 Status:** 🔍 **Análise**
- **🏢 Órgão:** Secretaria de Obras
- **📋 Categoria:** Obras e Instalações
- **🎯 Finalidade:** Infraestrutura urbana
- **🔍 Observação:** Aguardando documentação

---

## 📊 **Distribuição por Categoria:**
- **🏫 Educação:** 35% (R$ 3.132.500,00)
- **🏥 Saúde:** 28% (R$ 2.506.000,00)
- **🏗️ Obras:** 22% (R$ 1.969.000,00)
- **🏛️ Administração:** 15% (R$ 1.342.500,00)
        """
    else:  # Licitações e Pregões
        results = f"""
# 📋 **Análise de Licitações e Pregões**

**📊 Resumo da Investigação:**
- 🎯 **Termo:** {search_term}
- 📅 **Ano:** {year}
- 📈 **Processos:** 89 licitações
- 💰 **Valor Total:** R$ 12.300.000,00

---

## 🏆 **Principais Licitações Identificadas:**

### 1. **Licitação #LIC-2024-001**
**💰 Valor:** R$ 2.800.000,00 | **📊 Status:** ✅ **Homologada**
- **📋 Modalidade:** Concorrência Pública
- **🏢 Vencedor:** Construtora Alpha S/A
- **⏱️ Prazo:** 18 meses
- **👥 Participantes:** 8 empresas

### 2. **Pregão #PRE-2024-002**
**💰 Valor:** R$ 1.450.000,00 | **📊 Status:** 🔍 **Em Análise**
- **📋 Modalidade:** Pregão Eletrônico
- **🏢 Vencedor:** TechSoft Soluções Ltda
- **⏱️ Prazo:** 12 meses
- **👥 Participantes:** 12 empresas

### 3. **Licitação #LIC-2024-003**
**💰 Valor:** R$ 3.500.000,00 | **📊 Status:** ⚠️ **Recurso**
- **📋 Modalidade:** Tomada de Preços
- **🏢 Vencedor:** Empresa Beta Ltda
- **⏱️ Prazo:** 24 meses
- **⚠️ Observação:** Recurso administrativo em andamento

---

## 📈 **Análise de Competitividade:**
- **🎯 Média de Participantes:** 6,7 por licitação
- **✅ Taxa de Sucesso:** 92% dos processos homologados
- **⚠️ Recursos:** 8% dos processos com recursos
- **💡 Economia:** R$ 2.1M economizados vs. preço referência
        """
    
    return results

def create_professional_interface():
    """Interface profissional com UX/UI otimizado"""
    
    # Tema profissional simplificado
    professional_theme = gr.themes.Soft(
        primary_hue="green",
        secondary_hue="blue",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Inter")
    ).set(
        # Customizações básicas compatíveis
        body_background_fill="#ffffff",
        body_text_color="#0f172a",
        button_primary_background_fill="#22c55e",
        button_primary_background_fill_hover="#16a34a",
        button_secondary_background_fill="#3b82f6",
        button_secondary_background_fill_hover="#2563eb"
    )
    
    # CSS profissional avançado
    professional_css = """
    /* Root variables for consistency */
    :root {
        --primary-green: #22c55e;
        --primary-blue: #3b82f6;
        --neutral-50: #f8fafc;
        --neutral-100: #f1f5f9;
        --neutral-200: #e2e8f0;
        --neutral-500: #64748b;
        --neutral-900: #0f172a;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        --blur-sm: blur(4px);
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Hide Gradio elements */
    .gradio-container footer,
    .gradio-container .footer,
    .gradio-container .built-with,
    .gradio-container .version {
        display: none !important;
    }
    
    /* Global container improvements */
    .gradio-container {
        max-width: none !important;
        margin: 0 !important;
        padding: 0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Professional header */
    .professional-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: var(--blur-sm);
        border-bottom: 1px solid var(--neutral-200);
        padding: 1rem 2rem;
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
    }
    
    .professional-header:hover {
        box-shadow: var(--shadow-md);
    }
    
    .logo-professional {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-green);
        text-decoration: none;
        transition: var(--transition);
    }
    
    .logo-professional:hover {
        transform: translateY(-1px);
    }
    
    .flag-icon {
        font-size: 2rem;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
    }
    
    /* Enhanced landing page */
    .landing-professional {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: calc(100vh - 80px);
        padding: 2rem;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        position: relative;
        overflow: hidden;
    }
    
    .landing-professional::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 30% 80%, rgba(34, 197, 94, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(59, 130, 246, 0.1) 0%, transparent 50%);
        pointer-events: none;
    }
    
    .hero-professional {
        max-width: 900px;
        text-align: center;
        position: relative;
        z-index: 1;
    }
    
    .hero-title-professional {
        font-size: clamp(2.5rem, 8vw, 5rem);
        font-weight: 800;
        color: var(--primary-green);
        margin-bottom: 1.5rem;
        line-height: 1.1;
        letter-spacing: -0.025em;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        animation: fadeInUp 0.8s ease-out;
    }
    
    .hero-subtitle-professional {
        font-size: clamp(1.1rem, 3vw, 1.35rem);
        color: var(--neutral-500);
        margin-bottom: 3rem;
        line-height: 1.6;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
        animation: fadeInUp 0.8s ease-out 0.2s both;
    }
    
    /* Professional buttons */
    .buttons-professional {
        display: flex;
        gap: 1.5rem;
        justify-content: center;
        flex-wrap: wrap;
        animation: fadeInUp 0.8s ease-out 0.4s both;
    }
    
    .btn-professional {
        position: relative;
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1.25rem 2.5rem !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        transition: var(--transition) !important;
        border: none !important;
        cursor: pointer !important;
        min-width: 220px !important;
        justify-content: center !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(0) !important;
        overflow: hidden !important;
    }
    
    .btn-professional::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.5s ease;
    }
    
    .btn-professional:hover::before {
        left: 100%;
    }
    
    .btn-professional:hover {
        transform: translateY(-3px) !important;
        box-shadow: var(--shadow-xl) !important;
    }
    
    .btn-professional:active {
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    .btn-primary-professional {
        background: linear-gradient(135deg, var(--primary-blue), #60a5fa) !important;
        color: white !important;
    }
    
    .btn-primary-professional:hover {
        background: linear-gradient(135deg, #2563eb, var(--primary-blue)) !important;
        color: white !important;
    }
    
    .btn-secondary-professional {
        background: linear-gradient(135deg, var(--primary-green), #4ade80) !important;
        color: white !important;
    }
    
    .btn-secondary-professional:hover {
        background: linear-gradient(135deg, #16a34a, var(--primary-green)) !important;
        color: white !important;
    }
    
    /* Professional page layouts */
    .page-professional {
        padding: 2rem;
        max-width: 1400px;
        margin: 0 auto;
        animation: fadeIn 0.5s ease-out;
    }
    
    .page-title-professional {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--neutral-900);
        margin-bottom: 3rem;
        position: relative;
        display: inline-block;
        width: 100%;
    }
    
    .page-title-professional::after {
        content: '';
        position: absolute;
        bottom: -0.5rem;
        left: 50%;
        transform: translateX(-50%);
        width: 80px;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-blue), var(--primary-green));
        border-radius: 2px;
    }
    
    /* Professional sidebar */
    .sidebar-professional {
        background: var(--neutral-50);
        border: 1px solid var(--neutral-200);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
        height: fit-content;
        position: sticky;
        top: 120px;
    }
    
    .sidebar-professional:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    
    .sidebar-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--neutral-900);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Professional dashboard */
    .dashboard-professional {
        background: var(--neutral-50);
        border: 1px solid var(--neutral-200);
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
        min-height: 600px;
    }
    
    .dashboard-professional:hover {
        box-shadow: var(--shadow-md);
    }
    
    /* Professional form elements */
    .form-group-professional {
        margin-bottom: 1.5rem;
    }
    
    .form-group-professional label {
        display: block;
        font-weight: 600;
        color: var(--neutral-900);
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }
    
    /* Professional chat */
    .chat-professional {
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .chat-title-professional {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--neutral-900);
        margin-bottom: 1rem;
    }
    
    .chat-subtitle-professional {
        text-align: center;
        color: var(--neutral-500);
        margin-bottom: 3rem;
        font-size: 1.1rem;
        line-height: 1.6;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .chat-interface-professional {
        background: var(--neutral-50);
        border: 1px solid var(--neutral-200);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: var(--shadow-sm);
    }
    
    /* Header buttons */
    .header-buttons {
        display: flex;
        gap: 0.75rem;
        align-items: center;
    }
    
    .header-btn {
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: var(--transition) !important;
        border: 2px solid var(--neutral-200) !important;
        background: white !important;
        color: var(--neutral-500) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .header-btn:hover {
        background: var(--neutral-50) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
        color: var(--neutral-900) !important;
    }
    
    .header-btn-primary {
        background: var(--primary-green) !important;
        color: white !important;
        border-color: var(--primary-green) !important;
    }
    
    .header-btn-primary:hover {
        background: #16a34a !important;
        color: white !important;
    }
    
    /* Loading animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s ease-in-out infinite;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
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
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .professional-header {
            padding: 1rem;
        }
        
        .buttons-professional {
            flex-direction: column;
            align-items: center;
        }
        
        .btn-professional {
            min-width: 280px !important;
        }
        
        .page-professional {
            padding: 1rem;
        }
        
        .sidebar-professional,
        .dashboard-professional {
            padding: 1.5rem;
        }
        
        .hero-title-professional {
            font-size: 2.5rem;
        }
    }
    
    /* Accessibility improvements */
    .btn-professional:focus,
    .header-btn:focus {
        outline: 2px solid var(--primary-blue);
        outline-offset: 2px;
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        :root {
            --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.3);
            --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.3);
            --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.3);
        }
        
        .btn-professional {
            border: 2px solid currentColor !important;
        }
    }
    
    /* Print styles */
    @media print {
        .professional-header,
        .buttons-professional,
        .header-buttons {
            display: none !important;
        }
        
        .page-professional {
            padding: 0 !important;
        }
    }
    """
    
    with gr.Blocks(
        theme=professional_theme,
        css=professional_css,
        title="Cidadão.AI - Transparência Pública Brasileira",
        head="""
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Plataforma profissional de transparência pública brasileira">
        <meta name="keywords" content="transparência, governo, Brasil, contratos, licitações">
        <meta name="author" content="Anderson H. Silva">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        """
    ) as app:
        
        # Estado da aplicação
        current_page = gr.State("landing")
        
        # Header profissional
        with gr.Row(elem_classes="professional-header"):
            with gr.Column(scale=2):
                gr.HTML("""
                <div class="logo-professional">
                    <span class="flag-icon">🇧🇷</span>
                    <span>Cidadão.AI</span>
                </div>
                """)
            
            with gr.Column(scale=1):
                with gr.Row(elem_classes="header-buttons"):
                    credits_btn = gr.Button(
                        "ℹ️ Créditos",
                        elem_classes="header-btn",
                        size="sm"
                    )
                    theme_btn = gr.Button(
                        "🌙 Tema",
                        elem_classes="header-btn",
                        size="sm"
                    )
                    back_btn = gr.Button(
                        "🏠 Início",
                        elem_classes="header-btn header-btn-primary",
                        size="sm",
                        visible=False
                    )
        
        # Landing Page Profissional
        with gr.Column(visible=True, elem_classes="landing-professional") as landing_page:
            gr.HTML("""
            <div class="hero-professional">
                <h1 class="hero-title-professional">Cidadão.AI</h1>
                <p class="hero-subtitle-professional">
                    Plataforma inteligente que facilita a análise de dados públicos brasileiros. 
                    Descubra contratos suspeitos, gastos irregulares e licitações problemáticas 
                    de forma simples, rápida e profissional.
                </p>
            </div>
            """)
            
            with gr.Row(elem_classes="buttons-professional"):
                advanced_nav_btn = gr.Button(
                    "🔍 Consulta Avançada",
                    elem_classes="btn-professional btn-primary-professional",
                    size="lg"
                )
                
                chat_nav_btn = gr.Button(
                    "💬 Pergunte ao Modelo",
                    elem_classes="btn-professional btn-secondary-professional",
                    size="lg"
                )
        
        # Advanced Search Page Profissional
        with gr.Column(visible=False, elem_classes="page-professional") as advanced_page:
            gr.HTML('<h2 class="page-title-professional">🔍 Consulta Avançada</h2>')
            
            with gr.Row():
                # Sidebar Profissional
                with gr.Column(scale=1, elem_classes="sidebar-professional"):
                    gr.HTML('<h3 class="sidebar-title">⚙️ Configurações de Busca</h3>')
                    
                    with gr.Group(elem_classes="form-group-professional"):
                        data_type = gr.Radio(
                            label="📊 Tipo de Dados",
                            choices=["Contratos Públicos", "Despesas Orçamentárias", "Licitações e Pregões"],
                            value="Contratos Públicos",
                            info="Selecione o tipo de dados para investigação"
                        )
                    
                    with gr.Group(elem_classes="form-group-professional"):
                        year = gr.Number(
                            label="📅 Ano de Referência",
                            value=2024,
                            minimum=2010,
                            maximum=2024,
                            info="Ano dos dados a serem analisados"
                        )
                    
                    with gr.Group(elem_classes="form-group-professional"):
                        search_term = gr.Textbox(
                            label="🔍 Termo de Busca",
                            placeholder="Digite palavras-chave para busca...",
                            lines=2,
                            info="Ex: 'equipamentos médicos', 'obras públicas'"
                        )
                    
                    search_btn = gr.Button(
                        "🚀 Iniciar Investigação",
                        variant="primary",
                        size="lg",
                        elem_classes="btn-professional"
                    )
                
                # Dashboard Profissional
                with gr.Column(scale=2, elem_classes="dashboard-professional"):
                    gr.HTML("""
                    <div style="text-align: center; padding: 2rem 0;">
                        <h3 style="color: #0f172a; margin-bottom: 1rem;">📊 Dashboard de Transparência</h3>
                        <p style="color: #64748b; margin-bottom: 2rem;">Configure os filtros ao lado e inicie sua investigação para ver resultados detalhados aqui.</p>
                    </div>
                    """)
                    
                    results = gr.Markdown(
                        value="💡 **Dica Profissional:** Use os filtros ao lado para começar uma investigação detalhada sobre transparência pública. O sistema analisará automaticamente os dados e apresentará insights relevantes.",
                        elem_classes="results-professional"
                    )
        
        # Chat Page Profissional
        with gr.Column(visible=False, elem_classes="chat-professional") as chat_page:
            gr.HTML("""
            <div class="chat-title-professional">💬 Assistente de Transparência</div>
            <div class="chat-subtitle-professional">
                Converse com nosso assistente especializado em transparência pública. 
                Faça perguntas sobre contratos, licitações, despesas governamentais e 
                obtenha análises detalhadas e contextualizadas.
            </div>
            """)
            
            with gr.Group(elem_classes="chat-interface-professional"):
                chatbot = gr.Chatbot(
                    height=500,
                    show_label=False,
                    type="tuples",
                    elem_classes="chatbot-professional"
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Digite sua pergunta sobre transparência pública...",
                        show_label=False,
                        scale=4,
                        lines=1,
                        elem_classes="input-professional"
                    )
                    send_btn = gr.Button(
                        "✈️ Enviar",
                        variant="primary",
                        scale=1,
                        elem_classes="btn-professional"
                    )
        
        # Funções de navegação melhoradas
        def show_advanced():
            return {
                landing_page: gr.Column(visible=False),
                advanced_page: gr.Column(visible=True),
                chat_page: gr.Column(visible=False),
                back_btn: gr.Button(visible=True),
                current_page: "advanced"
            }
        
        def show_chat():
            return {
                landing_page: gr.Column(visible=False),
                advanced_page: gr.Column(visible=False),
                chat_page: gr.Column(visible=True),
                back_btn: gr.Button(visible=True),
                current_page: "chat"
            }
        
        def show_landing():
            return {
                landing_page: gr.Column(visible=True),
                advanced_page: gr.Column(visible=False),
                chat_page: gr.Column(visible=False),
                back_btn: gr.Button(visible=False),
                current_page: "landing"
            }
        
        # Event handlers
        advanced_nav_btn.click(
            fn=show_advanced,
            outputs=[landing_page, advanced_page, chat_page, back_btn, current_page]
        )
        
        chat_nav_btn.click(
            fn=show_chat,
            outputs=[landing_page, advanced_page, chat_page, back_btn, current_page]
        )
        
        back_btn.click(
            fn=show_landing,
            outputs=[landing_page, advanced_page, chat_page, back_btn, current_page]
        )
        
        # Funcionalidades principais
        search_btn.click(
            fn=search_data,
            inputs=[data_type, year, search_term],
            outputs=[results],
            show_progress=True
        )
        
        msg.submit(
            fn=chat_fn,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg],
            show_progress=True
        )
        
        send_btn.click(
            fn=chat_fn,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg],
            show_progress=True
        )
        
        # Funcionalidades do header
        def show_credits():
            return gr.Info("💡 Créditos: Anderson H. Silva - IFSuldeminas Campus Muzambinho | Bacharelado em Ciência da Computação")
        
        def toggle_theme():
            return gr.Info("🌙 Sistema de temas será implementado em breve. Atualmente otimizado para modo claro.")
        
        credits_btn.click(fn=show_credits)
        theme_btn.click(fn=toggle_theme)
    
    return app

if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI - Professional UX/UI...")
    app = create_professional_interface()
    app.launch(
        show_error=True,
        quiet=False,
        share=False,
        server_name="0.0.0.0",
        server_port=7860
    )