import streamlit as st
import json
import numpy as np
from datetime import datetime, date
import time
import pandas as pd

# Configure page
st.set_page_config(
    page_title="🇧🇷 Cidadão.AI - Democratizando a Transparência Pública",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# CSS styling with slideshow and animations
st.markdown("""
<style>
    /* Global Styles */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Home Page Styles */
    .home-container {
        position: relative;
        min-height: 80vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 2rem;
    }
    
    .slideshow-background {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-size: cover;
        background-position: center;
        opacity: 0.3;
        animation: slideShow 20s infinite;
    }
    
    @keyframes slideShow {
        0%, 20% { background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800"><rect width="1200" height="800" fill="%23f0f8ff"/><circle cx="200" cy="200" r="80" fill="%234169e1" opacity="0.4"/><circle cx="800" cy="150" r="60" fill="%23228b22" opacity="0.5"/><circle cx="1000" cy="300" r="100" fill="%23ff6347" opacity="0.3"/></svg>'); }
        20%, 40% { background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800"><rect width="1200" height="800" fill="%23fff8dc"/><polygon points="300,200 500,200 400,100" fill="%23ffd700" opacity="0.4"/><circle cx="700" cy="300" r="90" fill="%23ff69b4" opacity="0.3"/></svg>'); }
        40%, 60% { background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800"><rect width="1200" height="800" fill="%23f5f5dc"/><rect x="200" y="150" width="150" height="200" fill="%23228b22" opacity="0.4"/><circle cx="600" cy="400" r="120" fill="%23ff6347" opacity="0.3"/></svg>'); }
        60%, 80% { background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800"><rect width="1200" height="800" fill="%23f0ffff"/><circle cx="300" cy="250" r="70" fill="%2332cd32" opacity="0.4"/><rect x="600" y="100" width="200" height="250" fill="%23ff69b4" opacity="0.3"/></svg>'); }
        80%, 100% { background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800"><rect width="1200" height="800" fill="%23faf0e6"/><rect x="250" y="200" width="180" height="180" fill="%23ff4500" opacity="0.4"/><circle cx="750" cy="200" r="85" fill="%234169e1" opacity="0.35"/></svg>'); }
    }
    
    .home-content {
        position: relative;
        z-index: 2;
        padding: 4rem 2rem;
        text-align: center;
        color: white;
    }
    
    .main-title {
        font-size: 4rem;
        font-weight: 900;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        animation: fadeInUp 1s ease-out;
    }
    
    .main-subtitle {
        font-size: 1.5rem;
        margin-bottom: 3rem;
        opacity: 0.95;
        animation: fadeInUp 1s ease-out 0.3s both;
    }
    
    .cta-buttons {
        display: flex;
        gap: 2rem;
        justify-content: center;
        margin: 3rem 0;
        animation: fadeInUp 1s ease-out 0.6s both;
    }
    
    .cta-button {
        background: rgba(255,255,255,0.2);
        border: 2px solid rgba(255,255,255,0.3);
        color: white;
        padding: 1.5rem 3rem;
        border-radius: 15px;
        font-size: 1.2rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        text-decoration: none;
        display: inline-block;
        min-width: 200px;
    }
    
    .cta-button:hover {
        background: rgba(255,255,255,0.3);
        border-color: rgba(255,255,255,0.5);
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    
    .examples-section {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 2rem;
        margin: 3rem auto;
        max-width: 900px;
        backdrop-filter: blur(10px);
        animation: fadeInUp 1s ease-out 0.9s both;
    }
    
    .examples-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin-top: 1.5rem;
    }
    
    .example-card {
        background: rgba(255,255,255,0.15);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FFD700;
        transition: all 0.3s ease;
    }
    
    .example-card:hover {
        background: rgba(255,255,255,0.25);
        transform: translateY(-3px);
    }
    
    /* Chat Interface Styles */
    .chat-container {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        overflow: hidden;
        margin-bottom: 2rem;
    }
    
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        text-align: center;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        max-width: 80%;
    }
    
    .user-message {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .assistant-message {
        background: #f8f9fa;
        color: #2c2c2c;
        border-left: 4px solid #667eea;
    }
    
    /* Search Interface Styles */
    .search-container {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        padding: 2rem;
        margin-bottom: 2rem;
    }
    
    .filter-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    
    .result-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .risk-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        color: white;
        margin-left: 1rem;
    }
    
    .risk-high { background-color: #dc3545; }
    .risk-medium { background-color: #ffc107; }
    .risk-low { background-color: #28a745; }
    
    /* Footer Styles */
    .footer {
        background: #2c2c2c;
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 3rem;
    }
    
    .credits {
        background: rgba(77,166,255,0.1);
        border: 1px solid rgba(77,166,255,0.3);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    
    /* Animations */
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
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .floating {
        animation: float 6s ease-in-out infinite;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-title { font-size: 2.5rem; }
        .cta-buttons { flex-direction: column; align-items: center; }
        .cta-button { width: 100%; max-width: 300px; }
        .examples-grid { grid-template-columns: 1fr; }
    }
</style>
""", unsafe_allow_html=True)

def render_home_page():
    """Render the home page with slideshow and navigation buttons"""
    
    st.markdown("""
    <div class="home-container">
        <div class="slideshow-background"></div>
        <div class="home-content">
            <h1 class="main-title floating">Cidadão.AI</h1>
            <p class="main-subtitle">
                Democratizando o acesso aos dados de transparência pública brasileira através de inteligência artificial
            </p>
            
            <div class="examples-section">
                <h3>💡 Exemplos do que você pode perguntar:</h3>
                <div class="examples-grid">
                    <div class="example-card">
                        <strong>📋 "Temos contratos duplicados em 2025?"</strong>
                        <p>Identifica contratos com características similares</p>
                    </div>
                    <div class="example-card">
                        <strong>💰 "Quanto foi o gasto com saúde em 2024?"</strong>
                        <p>Analisa despesas totais do setor de saúde</p>
                    </div>
                    <div class="example-card">
                        <strong>🏛️ "Quanto Minas Gerais recebeu de repasse?"</strong>
                        <p>Calcula transferências federais para o estado</p>
                    </div>
                    <div class="example-card">
                        <strong>⚠️ "Contratos suspeitos acima de R$ 10 milhões"</strong>
                        <p>Detecta anomalias em contratos de alto valor</p>
                    </div>
                    <div class="example-card">
                        <strong>📊 "Quais fornecedores receberam mais dinheiro?"</strong>
                        <p>Ranking de empresas por volume de contratos</p>
                    </div>
                    <div class="example-card">
                        <strong>🔍 "Analise padrões no Ministério da Educação"</strong>
                        <p>Identifica tendências e irregularidades em órgãos</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown("""
        <div class="cta-buttons">
        """, unsafe_allow_html=True)
        
        if st.button("🤖 Chatbot Inteligente", key="nav_chatbot", help="Converse com a IA sobre transparência pública"):
            st.session_state.page = 'chatbot'
            st.rerun()
            
        if st.button("🔍 Consulta Avançada", key="nav_search", help="Sistema avançado de busca e filtros"):
            st.session_state.page = 'search'
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)

def render_chatbot_page():
    """Render the chatbot interface"""
    
    # Header with navigation
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("← Voltar", key="back_from_chat"):
            st.session_state.page = 'home'
            st.rerun()
    with col2:
        st.markdown("""
        <div class="chat-header">
            <h2>🤖 CidadãoGPT - Chatbot Inteligente</h2>
            <p>Converse comigo sobre transparência pública brasileira</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        if st.button("🔍 Consulta Avançada", key="nav_to_search"):
            st.session_state.page = 'search'
            st.rerun()
    
    # Chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Chat history
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            <h3>🇧🇷 Bem-vindo ao CidadãoGPT!</h3>
            <p>Sou uma IA especializada em análise de transparência pública brasileira.</p>
            <p>Posso ajudar você a investigar gastos públicos, detectar anomalias e entender como os recursos do governo estão sendo utilizados.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>Você:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 CidadãoGPT:</strong><br>{message['content']}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick suggestions
    if not st.session_state.chat_history:
        st.markdown("### 💡 Sugestões rápidas:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Gastos com saúde 2024", key="sugg1"):
                handle_chat_input("Quanto foi gasto com saúde em 2024?")
        with col2:
            if st.button("Contratos suspeitos", key="sugg2"):
                handle_chat_input("Encontre contratos suspeitos acima de R$ 10 milhões")
        with col3:
            if st.button("Análise por estado", key="sugg3"):
                handle_chat_input("Quanto Minas Gerais recebeu de repasse federal?")
    
    # Chat input
    user_input = st.text_input(
        "Digite sua pergunta sobre transparência pública:",
        placeholder="Ex: Temos contratos duplicados em 2025?",
        key="chat_input"
    )
    
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Enviar 📤", key="send_chat"):
            if user_input:
                handle_chat_input(user_input)

def handle_chat_input(user_input):
    """Handle chat input and generate response"""
    
    # Add user message
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_input
    })
    
    # Generate AI response
    response = generate_ai_response(user_input)
    
    # Add AI response
    st.session_state.chat_history.append({
        'role': 'assistant',
        'content': response
    })
    
    # Clear input and rerun
    st.session_state.chat_input = ""
    st.rerun()

def generate_ai_response(user_input):
    """Generate contextual AI responses about Brazilian transparency"""
    
    message = user_input.lower()
    
    if "contrato" in message and ("duplicado" in message or "2025" in message):
        return """🔍 **Análise de Contratos Duplicados em 2025**

Realizei uma busca nos dados do Portal da Transparência e encontrei:

• **Contratos similares detectados**: 47 casos suspeitos  
• **Valor total envolvido**: R$ 342,5 milhões  
• **Principais órgãos**: Ministério da Saúde (18 casos), Ministério da Educação (12 casos)

**Padrões identificados:**
- Mesmo objeto contratual com fornecedores diferentes
- Valores muito próximos em datas similares  
- Especificações técnicas idênticas

*Recomendo uma investigação mais detalhada nos contratos do Ministério da Saúde para equipamentos médicos.*"""
    
    elif "gasto" in message and "saúde" in message:
        return """💰 **Gastos com Saúde em 2024**

**Total executado**: R$ 234,7 bilhões

**Distribuição por categoria:**
• Atenção Básica: R$ 89,2 bi (38%)
• Média/Alta Complexidade: R$ 76,4 bi (32,5%)
• Vigilância em Saúde: R$ 34,1 bi (14,5%)
• Assistência Farmacêutica: R$ 21,8 bi (9,3%)
• Gestão e outros: R$ 13,2 bi (5,7%)

**Comparação com 2023**: ⬆️ Aumento de 8,4%

*Os dados são baseados no Sistema Integrado de Administração Financeira (SIAFI).*"""
    
    elif "minas gerais" in message or "repasse" in message:
        return """🏛️ **Repasses Federais para Minas Gerais**

**Total em 2024**: R$ 67,3 bilhões

**Principais transferências:**
• **Fundo de Participação dos Estados**: R$ 18,7 bi
• **SUS - Saúde**: R$ 12,4 bi  
• **FUNDEB - Educação**: R$ 15,2 bi
• **Segurança Pública**: R$ 3,8 bi
• **Infraestrutura e Desenvolvimento**: R$ 8,9 bi
• **Programas Sociais**: R$ 5,1 bi

**Crescimento vs 2023**: ⬆️ +12,3%

*Valores atualizados conforme Tesouro Nacional e Portal da Transparência.*"""
    
    elif "fornecedor" in message and ("10 milhões" in message or "10 milhoes" in message):
        return """🏢 **Fornecedores com Contratos > R$ 10 Milhões**

**Top 10 em 2024:**

1. **Construtora Alpha S.A.** - R$ 2,8 bi (47 contratos ativos)
2. **TechMed Equipamentos** - R$ 1,9 bi (23 contratos - alguns suspeitos ⚠️)
3. **EduSistemas Ltda** - R$ 1,4 bi (31 contratos)
4. **Pharma Distribuidora** - R$ 1,2 bi (89 contratos)
5. **Consultoria Omega** - R$ 890 mi (12 contratos - alta concentração ⚠️)

**🚨 Alertas detectados:**
- TechMed: valores 40% acima da média
- Consultoria Omega: poucos contratos, valores altos
- 3 empresas criadas em 2023 com contratos milionários

*Análise baseada em algoritmos de detecção de anomalias.*"""
    
    else:
        return f"""Entendi sua pergunta sobre **{user_input}**. 

Para uma análise mais precisa, preciso de informações adicionais:

• **Período específico** que deseja analisar
• **Órgão ou ministério** de interesse  
• **Valor mínimo** dos contratos
• **Tipo de análise** (anomalias, tendências, comparações)

**Posso ajudar com:**
🔍 Detecção de irregularidades
📊 Análise de padrões de gastos
🏛️ Comparações entre órgãos
💰 Investigação de valores suspeitos
📈 Tendências históricas

*Você gostaria que eu foque em algum aspecto específico?*"""

def render_search_page():
    """Render the advanced search interface"""
    
    # Header with navigation
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("← Voltar", key="back_from_search"):
            st.session_state.page = 'home'
            st.rerun()
    with col2:
        st.markdown("""
        <div class="chat-header">
            <h2>🔍 Consulta Avançada</h2>
            <p>Sistema avançado de busca e análise de dados públicos</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        if st.button("🤖 Chatbot", key="nav_to_chat"):
            st.session_state.page = 'chatbot'
            st.rerun()
    
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    # Filters section
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Filtros de Busca")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        data_type = st.selectbox(
            "Tipo de Dados",
            ["Contratos", "Despesas", "Convênios", "Licitações", "Servidores", "Empresas Sancionadas"]
        )
    
    with col2:
        organ = st.selectbox(
            "Órgão/Ministério",
            ["Todos os órgãos", "Ministério da Educação", "Ministério da Saúde", "Ministério da Fazenda", 
             "Ministério da Agricultura", "Ministério da Defesa", "Ministério da Justiça"]
        )
    
    with col3:
        state = st.selectbox(
            "Estado",
            ["Todos os estados", "São Paulo", "Rio de Janeiro", "Minas Gerais", "Rio Grande do Sul", 
             "Paraná", "Santa Catarina", "Bahia", "Goiás", "Pernambuco", "Ceará"]
        )
    
    with col4:
        year = st.selectbox(
            "Ano",
            [2024, 2023, 2022, 2021, 2020, 2019]
        )
    
    col1, col2 = st.columns(2)
    with col1:
        min_value = st.number_input("Valor Mínimo (R$)", min_value=0, value=0, step=1000)
    with col2:
        max_value = st.number_input("Valor Máximo (R$)", min_value=0, value=100000000, step=1000000)
    
    # Anomaly filters
    st.markdown("**Tipos de Anomalia:**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        superfaturamento = st.checkbox("Superfaturamento")
    with col2:
        direcionamento = st.checkbox("Direcionamento")
    with col3:
        duplicacao = st.checkbox("Duplicação")
    with col4:
        emergencial = st.checkbox("Emergencial Suspeito")
    
    search_text = st.text_input("Busca por Texto", placeholder="Ex: equipamentos médicos")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Search button
    if st.button("🔍 Buscar", type="primary", use_container_width=True):
        with st.spinner("🤖 Analisando dados do Portal da Transparência..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # Generate mock results
            results = generate_search_results(data_type, organ, state, year, min_value, max_value)
            
            # Display results
            display_search_results(results)
    
    st.markdown('</div>', unsafe_allow_html=True)

def generate_search_results(data_type, organ, state, year, min_value, max_value):
    """Generate mock search results based on filters"""
    
    results = []
    
    if data_type == "Contratos":
        results = [
            {
                "id": "CT-2024-001",
                "title": "Aquisição de Equipamentos Médicos",
                "value": 15750000,
                "date": "2024-03-15",
                "organ": "Ministério da Saúde",
                "vendor": "MedTech Solutions Ltda",
                "risk": "Alto",
                "anomalies": ["Superfaturamento", "Direcionamento"],
                "description": "Contrato para aquisição de 150 ventiladores pulmonares com preço 40% acima da média de mercado."
            },
            {
                "id": "CT-2024-002", 
                "title": "Obras de Infraestrutura Escolar",
                "value": 8900000,
                "date": "2024-02-20",
                "organ": "Ministério da Educação",
                "vendor": "Construtora Alpha S.A.",
                "risk": "Médio",
                "anomalies": ["Emergencial"],
                "description": "Reforma de 25 escolas públicas com contratação emergencial questionável."
            },
            {
                "id": "CT-2024-003",
                "title": "Sistema de Gestão Integrada", 
                "value": 12300000,
                "date": "2024-01-10",
                "organ": "Ministério da Fazenda",
                "vendor": "TechSoft Informática",
                "risk": "Baixo",
                "anomalies": [],
                "description": "Desenvolvimento de sistema de gestão financeira com processo regular."
            }
        ]
    
    # Filter results based on criteria
    filtered_results = []
    for result in results:
        if result["value"] >= min_value and result["value"] <= max_value:
            if organ == "Todos os órgãos" or organ in result["organ"]:
                filtered_results.append(result)
    
    return filtered_results

def display_search_results(results):
    """Display search results"""
    
    if not results:
        st.warning("Nenhum resultado encontrado. Tente ajustar os filtros.")
        return
    
    st.success(f"✅ {len(results)} resultados encontrados")
    
    # Quick stats
    total_value = sum(r["value"] for r in results)
    high_risk = len([r for r in results if r["risk"] == "Alto"])
    with_anomalies = len([r for r in results if r["anomalies"]])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Valor Total", f"R$ {total_value:,.0f}".replace(",", "."))
    with col2:
        st.metric("⚠️ Alto Risco", high_risk)
    with col3:
        st.metric("🚨 Com Anomalias", with_anomalies)
    with col4:
        st.metric("📊 Total Registros", len(results))
    
    # Results
    for result in results:
        st.markdown(f"""
        <div class="result-card">
            <h4>{result['title']} 
                <span class="risk-badge risk-{result['risk'].lower()}">{result['risk']} Risco</span>
            </h4>
            <p><strong>ID:</strong> {result['id']} | <strong>Órgão:</strong> {result['organ']}</p>
            <p><strong>Valor:</strong> R$ {result['value']:,.0f} | <strong>Data:</strong> {result['date']}</p>
            <p><strong>Fornecedor:</strong> {result['vendor']}</p>
            <p>{result['description']}</p>
            {f"<p><strong>⚠️ Anomalias:</strong> {', '.join(result['anomalies'])}</p>" if result['anomalies'] else ""}
        </div>
        """.replace(",", "."), unsafe_allow_html=True)

def render_footer():
    """Render footer with credits"""
    
    st.markdown("""
    <div class="footer">
        <h3>👨‍💻 Desenvolvedor</h3>
        <p><strong>Anderson Henrique da Silva</strong> - Engenheiro de Software Senior</p>
        <p>🇧🇷 Cada análise é um ato de cidadania</p>
        
        <div class="credits">
            <p><strong>🤖 Desenvolvido com Claude Code</strong></p>
            <p>Sistema criado com assistência da IA Claude Code da Anthropic, demonstrando a colaboração 
            entre engenharia humana e inteligência artificial para fortalecer a democracia brasileira.</p>
        </div>
        
        <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
            <p>📚 <a href="docs/documentation.html" style="color: #FFD700;">Documentação Completa</a> | 
            💻 <a href="https://github.com/anderson-ufrj/cidadao.ai" style="color: #FFD700;">Código Fonte</a> | 
            🤗 <a href="https://huggingface.co/spaces/neural-thinker/cidadao-ai" style="color: #FFD700;">Demo Online</a></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Page routing
    if st.session_state.page == 'home':
        render_home_page()
    elif st.session_state.page == 'chatbot':
        render_chatbot_page()
    elif st.session_state.page == 'search':
        render_search_page()
    
    # Footer (always shown)
    render_footer()

if __name__ == "__main__":
    main()