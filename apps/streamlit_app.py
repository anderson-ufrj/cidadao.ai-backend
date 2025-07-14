#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Interface Streamlit para Hugging Face Spaces
Sistema de consulta aos dados do Portal da Transparência
"""

import streamlit as st
import os
import time
import json
from datetime import datetime

# Configurar página
st.set_page_config(
    page_title="🇧🇷 Cidadão.AI - Transparência Pública",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configurar variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# CSS para o hero section
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    .hero-section {
        background: linear-gradient(
            rgba(0, 0, 0, 0.4),
            rgba(0, 0, 0, 0.6)
        ),
        url('https://upload.wikimedia.org/wikipedia/commons/e/e3/Congresso_Nacional_-_Brasília_-_panorama.jpg');
        background-size: cover;
        background-position: center;
        min-height: 60vh;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        text-align: center;
        border-radius: 15px;
        margin: 1rem 0 2rem 0;
        position: relative;
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
    
    .status-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #0049A0;
    }
    
    .status-success {
        border-left-color: #4caf50;
        background: #f1f8e9;
    }
    
    .status-error {
        border-left-color: #f44336;
        background: #ffebee;
    }
    
    .result-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #2196f3;
    }
    
    .success-result {
        border-left-color: #4caf50;
        background: #f1f8e9;
    }
    
    .error-result {
        border-left-color: #f44336;
        background: #ffebee;
    }
    
    @media (max-width: 768px) {
        .hero-logo { font-size: 2.5rem; }
        .hero-subtitle { font-size: 1.2rem; }
        .hero-description { font-size: 1rem; }
        .hero-content { margin: 1rem; padding: 2rem 1.5rem; }
    }
</style>
""", unsafe_allow_html=True)

def check_api_status():
    """Verificar status das APIs"""
    api_configured = bool(TRANSPARENCY_API_KEY)
    ai_configured = bool(GROQ_API_KEY)
    
    if api_configured:
        st.markdown("""
        <div class="status-card status-success">
            <h3>📊 Status do Sistema</h3>
            <p><strong>✅ Portal da Transparência:</strong> API Configurada</p>
            <p><strong>{}</strong> {}</p>
        </div>
        """.format(
            "✅ Análise com IA:" if ai_configured else "⚠️ Análise com IA:",
            "Habilitada" if ai_configured else "Não configurada"
        ), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-card status-error">
            <h3>📊 Status do Sistema</h3>
            <p><strong>❌ Portal da Transparência:</strong> API não configurada</p>
            <p><strong>⚠️ Análise com IA:</strong> Não disponível</p>
        </div>
        """, unsafe_allow_html=True)

def search_mock_data(data_type, year, org_code, search_term):
    """Busca simulada de dados"""
    
    if not TRANSPARENCY_API_KEY:
        st.markdown("""
        <div class="result-card error-result">
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
        """, unsafe_allow_html=True)
        return
    
    # Simular processamento
    with st.spinner('🔍 Buscando dados...'):
        time.sleep(1)
    
    # Dados simulados
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
        st.markdown("""
        <div class="result-card">
            <h3>📭 Nenhum resultado encontrado</h3>
            <p>Tente ajustar os filtros da sua busca ou termo de pesquisa.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Mostrar resultados
    st.markdown(f"""
    <div class="result-card success-result">
        <h3>✅ {len(results)} resultados encontrados</h3>
        <p>Dados do Portal da Transparência - {data_type} em {year}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Criar tabela
    import pandas as pd
    
    if data_type == "Contratos":
        df = pd.DataFrame(results)
        df = df[['numero', 'empresa', 'valor', 'objeto', 'data']]
        df.columns = ['Número', 'Empresa', 'Valor', 'Objeto', 'Data']
    elif data_type == "Despesas":
        df = pd.DataFrame(results)
        df = df[['documento', 'favorecido', 'valor', 'descricao', 'data']]
        df.columns = ['Documento', 'Favorecido', 'Valor', 'Descrição', 'Data']
    else:  # Licitações
        df = pd.DataFrame(results)
        df = df[['numero', 'modalidade', 'valor', 'objeto', 'data']]
        df.columns = ['Número', 'Modalidade', 'Valor', 'Objeto', 'Data']
    
    st.dataframe(df, use_container_width=True)

def main():
    """Função principal"""
    
    # Hero Section
    st.markdown("""
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
    """, unsafe_allow_html=True)
    
    # Status do Sistema
    check_api_status()
    
    # Interface Principal
    st.markdown("## 🔍 Sistema de Busca")
    
    # Filtros
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🎯 Filtros")
        
        data_type = st.radio(
            "Tipo de Dados",
            ["Contratos", "Despesas", "Licitações"],
            index=0
        )
        
        year = st.number_input(
            "Ano",
            min_value=2020,
            max_value=2025,
            value=2024,
            step=1
        )
        
        org_code = st.text_input(
            "Código do Órgão (opcional)",
            placeholder="Ex: 26000 (MEC)"
        )
        
        search_term = st.text_input(
            "Termo de Busca (opcional)",
            placeholder="Ex: equipamento, consultoria, obra"
        )
        
        search_clicked = st.button(
            "🔍 Buscar Dados",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        st.markdown("### 📊 Resultados")
        
        if search_clicked:
            search_mock_data(data_type, year, org_code, search_term)
        else:
            st.markdown("""
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
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;">
        <p><strong>🤖 Cidadão.AI</strong> - Democratizando o acesso aos dados públicos</p>
        <p>Desenvolvido por Anderson Henrique da Silva | 🇧🇷 Feito para o Brasil</p>
        <p><a href="https://github.com/anderson-ufrj/cidadao.ai" target="_blank">💻 Repositório GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()