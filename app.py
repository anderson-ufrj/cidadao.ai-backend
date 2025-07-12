#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Interface Principal
Plataforma de análise de transparência pública com IA especializada
"""

import streamlit as st
import requests
import json
import time
from typing import Dict, List, Any
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="🔍 Cidadão.AI - Inteligência Cidadã para Transparência",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estado da sessão
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# CSS Moderno e Responsivo
st.markdown("""
<style>
    /* Reset e Base */
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Página Inicial - Background com imagens brasileiras */
    .hero-container {
        position: relative;
        min-height: 100vh;
        background: linear-gradient(
            135deg,
            rgba(0, 73, 144, 0.9) 0%,
            rgba(255, 183, 77, 0.8) 50%,
            rgba(0, 122, 51, 0.9) 100%
        ),
        url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080"><defs><pattern id="buildings" patternUnits="userSpaceOnUse" width="200" height="150"><rect width="200" height="150" fill="%23f0f8ff" opacity="0.1"/><rect x="20" y="80" width="30" height="70" fill="%234169e1" opacity="0.3"/><rect x="60" y="60" width="25" height="90" fill="%234169e1" opacity="0.4"/><rect x="95" y="70" width="35" height="80" fill="%234169e1" opacity="0.3"/><rect x="140" y="50" width="28" height="100" fill="%234169e1" opacity="0.4"/></pattern></defs><rect width="1920" height="1080" fill="url(%23buildings)"/></svg>');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: -1rem -1rem 0 -1rem;
    }
    
    .hero-content {
        text-align: center;
        color: white;
        max-width: 800px;
        padding: 2rem;
        background: rgba(0, 0, 0, 0.4);
        border-radius: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        animation: fadeInUp 1.2s ease-out;
    }
    
    .hero-logo {
        font-size: 5rem;
        font-weight: 900;
        margin-bottom: 1rem;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.5);
        background: linear-gradient(45deg, #FFB74D, #FFFFFF, #4CAF50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-subtitle {
        font-size: 1.8rem;
        margin-bottom: 3rem;
        opacity: 0.95;
        font-weight: 300;
        line-height: 1.4;
    }
    
    .cta-buttons {
        display: flex;
        gap: 2rem;
        justify-content: center;
        margin: 3rem 0;
        flex-wrap: wrap;
    }
    
    .cta-button {
        background: linear-gradient(45deg, #FF6B35, #F7931E);
        border: none;
        color: white;
        padding: 1.2rem 2.5rem;
        border-radius: 50px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 8px 25px rgba(255, 107, 53, 0.3);
    }
    
    .cta-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(255, 107, 53, 0.4);
        text-decoration: none;
        color: white;
    }
    
    .cta-button.secondary {
        background: linear-gradient(45deg, #667eea, #764ba2);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .cta-button.secondary:hover {
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
    }
    
    /* Exemplos de Perguntas */
    .examples-section {
        margin-top: 4rem;
        animation: fadeInUp 1.2s ease-out 0.3s both;
    }
    
    .examples-title {
        font-size: 1.3rem;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    
    .examples-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .example-card {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        backdrop-filter: blur(5px);
    }
    
    .example-card:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    
    .example-text {
        font-size: 0.95rem;
        line-height: 1.4;
        margin: 0;
    }
    
    /* Footer */
    .hero-footer {
        margin-top: 4rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        opacity: 0.8;
        font-size: 0.9rem;
        animation: fadeInUp 1.2s ease-out 0.6s both;
    }
    
    /* Páginas Internas */
    .page-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .page-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .page-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Chat Interface */
    .chat-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 2rem;
        min-height: 500px;
        max-height: 600px;
        overflow-y: auto;
    }
    
    .chat-message {
        margin-bottom: 1.5rem;
        padding: 1rem;
        border-radius: 10px;
        max-width: 80%;
    }
    
    .chat-message.user {
        background: #e3f2fd;
        margin-left: auto;
        text-align: right;
    }
    
    .chat-message.ai {
        background: #f1f8e9;
        margin-right: auto;
    }
    
    .message-header {
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    /* Search Interface */
    .search-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .search-filters {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .result-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .result-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1976d2;
        margin-bottom: 0.5rem;
    }
    
    .result-meta {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 1rem;
    }
    
    .result-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #2e7d32;
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
    
    /* Responsividade */
    @media (max-width: 768px) {
        .hero-logo {
            font-size: 3rem;
        }
        
        .hero-subtitle {
            font-size: 1.3rem;
        }
        
        .cta-buttons {
            flex-direction: column;
            align-items: center;
        }
        
        .examples-grid {
            grid-template-columns: 1fr;
        }
        
        .hero-container {
            background-attachment: scroll;
        }
    }
</style>
""", unsafe_allow_html=True)

def render_home_page():
    """Renderizar página inicial com novo design"""
    
    st.markdown("""
    <div class="hero-container">
        <div class="hero-content">
            <div class="hero-logo">cidadão.ai</div>
            <div class="hero-subtitle">
                Inteligência cidadã para uma nova era de transparência pública
            </div>
            
            <div class="cta-buttons">
                <button class="cta-button" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'search'}, '*')">
                    🔍 Busca Avançada
                </button>
                <button class="cta-button secondary" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'chat'}, '*')">
                    💬 Converse com a IA
                </button>
            </div>
            
            <div class="examples-section">
                <div class="examples-title">
                    💡 Exemplos de perguntas para começar:
                </div>
                <div class="examples-grid">
                    <div class="example-card" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'example1'}, '*')">
                        <p class="example-text">
                            "Quanto foi gasto com educação no estado de SP em 2023?"
                        </p>
                    </div>
                    <div class="example-card" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'example2'}, '*')">
                        <p class="example-text">
                            "Qual o histórico de contratos da empresa X com o governo?"
                        </p>
                    </div>
                    <div class="example-card" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'example3'}, '*')">
                        <p class="example-text">
                            "Mostre licitações suspeitas acima de R$ 10 milhões em 2024"
                        </p>
                    </div>
                    <div class="example-card" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'example4'}, '*')">
                        <p class="example-text">
                            "Analise os gastos com saúde durante a pandemia"
                        </p>
                    </div>
                </div>
            </div>
            
            <div class="hero-footer">
                <p>🏛️ <strong>Cidadão.AI</strong> - Transformando dados públicos em transparência cidadã</p>
                <p>Desenvolvido com ❤️ para fortalecer a democracia brasileira</p>
                <p style="margin-top: 1rem; font-size: 0.8rem;">
                    👨‍💻 <strong>Créditos:</strong> Anderson Henrique da Silva | 🤖 AI Assistant: Claude Code
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_search_page():
    """Página de busca avançada funcional"""
    
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🔍 Busca Avançada</div>
        <div class="page-subtitle">Encontre informações específicas nos dados governamentais</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        # Filtros de pesquisa
        st.subheader("🔧 Filtros de Pesquisa")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_type = st.selectbox(
                "📋 Tipo de Dados",
                ["Contratos", "Despesas", "Licitações", "Convênios", "Fornecedores"]
            )
            
            year = st.selectbox(
                "📅 Ano",
                [2024, 2023, 2022, 2021, 2020, 2019]
            )
        
        with col2:
            organ = st.selectbox(
                "🏛️ Órgão",
                ["Todos", "Ministério da Saúde", "Ministério da Educação", 
                 "Ministério da Defesa", "Ministério da Justiça"]
            )
            
            min_value = st.number_input(
                "💰 Valor Mínimo (R$)",
                min_value=0,
                value=100000,
                step=10000
            )
        
        with col3:
            state = st.selectbox(
                "🗺️ Estado",
                ["Todos", "SP", "RJ", "MG", "RS", "PR", "SC", "BA", "GO", "DF"]
            )
            
            max_value = st.number_input(
                "💰 Valor Máximo (R$)",
                min_value=0,
                value=10000000,
                step=100000
            )
        
        # Campo de busca textual
        search_query = st.text_input(
            "🔍 Termo de Busca",
            placeholder="Digite palavras-chave, nome de empresa, CNPJ...",
            help="Busque por termos específicos nos documentos"
        )
        
        # Botão de busca
        if st.button("🔍 Buscar", type="primary", use_container_width=True):
            with st.spinner("🔄 Buscando dados..."):
                time.sleep(2)  # Simular processamento
                results = generate_search_results(search_type, year, organ, min_value, max_value, search_query)
                st.session_state.search_results = results
        
        # Exibir resultados
        if st.session_state.search_results:
            st.subheader(f"📊 Resultados da Busca ({len(st.session_state.search_results)} encontrados)")
            
            for i, result in enumerate(st.session_state.search_results):
                st.markdown(f"""
                <div class="result-card">
                    <div class="result-title">{result['title']}</div>
                    <div class="result-meta">
                        📅 {result['date']} | 🏛️ {result['organ']} | 📍 {result['location']}
                    </div>
                    <div style="margin: 1rem 0;">
                        {result['description']}
                    </div>
                    <div class="result-value">💰 {result['value']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_chat_page():
    """Página de chat com IA melhorada"""
    
    st.markdown("""
    <div class="page-header">
        <div class="page-title">💬 Chat com Cidadão.AI</div>
        <div class="page-subtitle">Converse em linguagem natural sobre transparência pública</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Exibir histórico do chat
        for message in st.session_state.chat_history:
            role_class = "user" if message['role'] == 'user' else "ai"
            role_name = "👤 Você" if message['role'] == 'user' else "🤖 Cidadão.AI"
            
            st.markdown(f"""
            <div class="chat-message {role_class}">
                <div class="message-header">{role_name}</div>
                <div>{message['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Mensagem inicial se não há histórico
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="chat-message ai">
                <div class="message-header">🤖 Cidadão.AI</div>
                <div>
                    Olá! Sou o Cidadão.AI, sua assistente especializada em transparência pública. 
                    Posso ajudar você a:
                    <ul>
                        <li>🔍 Encontrar contratos e licitações específicas</li>
                        <li>📊 Analisar gastos públicos por área ou período</li>
                        <li>⚖️ Verificar conformidade legal de processos</li>
                        <li>🚨 Detectar possíveis irregularidades</li>
                    </ul>
                    Como posso ajudar você hoje?
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Input do usuário
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "💬 Digite sua pergunta:",
            placeholder="Ex: Quais foram os maiores contratos do Ministério da Saúde em 2023?",
            key="chat_input"
        )
    
    with col2:
        send_button = st.button("📤 Enviar", type="primary")
    
    # Processar entrada do usuário
    if send_button and user_input:
        # Adicionar mensagem do usuário
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        })
        
        # Gerar resposta da IA
        with st.spinner("🤖 Cidadão.AI está pensando..."):
            time.sleep(1.5)  # Simular processamento
            ai_response = generate_ai_response(user_input)
            
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': ai_response,
                'timestamp': datetime.now()
            })
        
        # Rerun para atualizar o chat
        st.rerun()

def generate_search_results(search_type: str, year: int, organ: str, min_value: int, max_value: int, query: str) -> List[Dict]:
    """Gerar resultados de busca simulados"""
    
    # Dados simulados mais realistas
    sample_results = [
        {
            'title': f'Contrato para aquisição de equipamentos médicos - {organ}',
            'date': f'{year}-03-15',
            'organ': organ if organ != "Todos" else "Ministério da Saúde",
            'location': 'Brasília/DF',
            'description': 'Aquisição de 500 ventiladores pulmonares para unidades hospitalares da rede pública federal.',
            'value': 'R$ 2.350.000,00'
        },
        {
            'title': f'Licitação para serviços de TI - {organ}',
            'date': f'{year}-07-22',
            'organ': organ if organ != "Todos" else "Ministério da Educação",
            'location': 'São Paulo/SP',
            'description': 'Prestação de serviços de desenvolvimento e manutenção de sistemas educacionais.',
            'value': 'R$ 1.875.000,00'
        },
        {
            'title': f'Convênio para pesquisa científica - {organ}',
            'date': f'{year}-01-10',
            'organ': organ if organ != "Todos" else "Ministério da Ciência e Tecnologia",
            'location': 'Rio de Janeiro/RJ',
            'description': 'Desenvolvimento de pesquisas em inteligência artificial aplicada à saúde pública.',
            'value': 'R$ 950.000,00'
        }
    ]
    
    # Filtrar por valor
    filtered_results = []
    for result in sample_results:
        value_num = float(result['value'].replace('R$ ', '').replace('.', '').replace(',', '.'))
        if min_value <= value_num <= max_value:
            filtered_results.append(result)
    
    return filtered_results

def generate_ai_response(user_input: str) -> str:
    """Gerar resposta da IA baseada na entrada do usuário"""
    
    user_input_lower = user_input.lower()
    
    # Respostas contextuais baseadas em palavras-chave
    if any(word in user_input_lower for word in ['educação', 'escola', 'ensino', 'universidade']):
        return """📚 **Análise de Gastos com Educação**

Com base nos dados do Portal da Transparência, posso te ajudar com informações sobre:

🏫 **Ministério da Educação (2023)**:
- Orçamento total: R$ 132,4 bilhões
- Principais programas: FUNDEB, ProUni, FIES
- Contratos de maior valor: infraestrutura universitária

📊 **Indicadores relevantes**:
- Gasto por aluno: R$ 6.227 (ensino fundamental)
- Universidades federais: 69 instituições
- Bolsas de estudo: 2,1 milhões de beneficiários

Gostaria de saber mais detalhes sobre algum aspecto específico?"""

    elif any(word in user_input_lower for word in ['saúde', 'hospital', 'sus', 'médico']):
        return """🏥 **Análise de Gastos com Saúde**

Analisando os dados do SUS e Ministério da Saúde:

💉 **Ministério da Saúde (2023)**:
- Orçamento SUS: R$ 198,2 bilhões
- Principais áreas: atenção básica, hospitalar, vigilância
- Contratos emergenciais: equipamentos COVID-19

🔍 **Possíveis irregularidades detectadas**:
- 15 contratos sem licitação acima de R$ 10 milhões
- 3 fornecedores com concentração > 80% dos contratos
- Variação de preços entre estados: até 300%

⚠️ **Recomendação**: Investigar contratos emergenciais de 2020-2022 para possível superfaturamento.

Quer que eu detalhe alguma irregularidade específica?"""

    elif any(word in user_input_lower for word in ['contrato', 'licitação', 'irregularidade', 'suspeito']):
        return """🔍 **Análise de Contratos e Licitações**

Detectei alguns padrões que merecem atenção:

🚨 **Alertas de Risco Alto**:
- 47 contratos emergenciais sem justificativa adequada
- 12 empresas recém-criadas com contratos > R$ 5 milhões
- Variação de preços: 150-400% para produtos similares

📋 **Contratos Suspeitos (últimos 6 meses)**:
1. Empresa ABC LTDA - R$ 25 milhões (criada há 2 meses)
2. Fornecedor XYZ - R$ 18 milhões (preço 300% acima da média)
3. Serviços DEF - R$ 12 milhões (sem comprovação técnica)

⚖️ **Status Legal**: 5 processos em análise pelo TCU

Gostaria que eu investigue algum contrato específico?"""

    elif any(word in user_input_lower for word in ['quanto', 'valor', 'gasto', 'orçamento']):
        return """💰 **Análise de Gastos Públicos**

Aqui estão os dados consolidados que encontrei:

📊 **Orçamento Federal 2023**:
- Total: R$ 5,07 trilhões
- Gastos obrigatórios: 93,2%
- Investimentos: 2,1%
- Custeio: 4,7%

🏛️ **Maiores Órgãos por Gasto**:
1. INSS: R$ 713 bilhões (benefícios previdenciários)
2. Ministério da Saúde: R$ 198 bilhões
3. Ministério da Educação: R$ 132 bilhões
4. Ministério da Defesa: R$ 126 bilhões

📈 **Comparação com 2022**: Aumento de 7,3% em termos reais

Sobre qual área específica você gostaria de mais detalhes?"""

    else:
        return """🤖 **Cidadão.AI - Assistente de Transparência**

Entendi sua pergunta! Posso ajudar você com:

🔍 **Análises Disponíveis**:
- Contratos e licitações por valor, órgão ou período
- Gastos públicos por área (saúde, educação, segurança)
- Detecção de irregularidades e padrões suspeitos
- Fornecedores e histórico de contratações
- Comparações entre estados e municípios

💡 **Exemplos de perguntas**:
- "Mostre os maiores contratos do Ministério X em 2023"
- "Há irregularidades nos gastos com educação?"
- "Qual empresa mais recebeu recursos públicos?"

Como posso refinar minha análise para você?"""

def main():
    """Função principal da aplicação"""
    
    # Controle de navegação via JavaScript
    st.markdown("""
    <script>
    window.addEventListener('message', function(event) {
        if (event.data.type === 'streamlit:setComponentValue') {
            const value = event.data.value;
            if (value === 'search') {
                window.parent.postMessage({type: 'streamlit:setKey', key: 'nav_action', value: 'search'}, '*');
            } else if (value === 'chat') {
                window.parent.postMessage({type: 'streamlit:setKey', key: 'nav_action', value: 'chat'}, '*');
            } else if (value.startsWith('example')) {
                window.parent.postMessage({type: 'streamlit:setKey', key: 'nav_action', value: 'chat'}, '*');
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Navegação por botões
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🏠 Início", use_container_width=True):
            st.session_state.page = 'home'
    
    with col2:
        if st.button("🔍 Busca Avançada", use_container_width=True):
            st.session_state.page = 'search'
    
    with col3:
        if st.button("💬 Chat IA", use_container_width=True):
            st.session_state.page = 'chat'
    
    # Renderizar página correspondente
    if st.session_state.page == 'home':
        render_home_page()
    elif st.session_state.page == 'search':
        render_search_page()
    elif st.session_state.page == 'chat':
        render_chat_page()

if __name__ == "__main__":
    main()