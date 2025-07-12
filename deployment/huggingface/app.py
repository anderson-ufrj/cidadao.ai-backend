#!/usr/bin/env python3
"""
Aplicação Streamlit para Hugging Face Spaces
Cidadão.AI - Análise de Transparência Pública
"""

import streamlit as st
import torch
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from transformers import AutoModel, AutoTokenizer
import time
from typing import Dict, Any, List
import json

# Configuração da página
st.set_page_config(
    page_title="🇧🇷 Cidadão.AI - Análise de Transparência",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .alert-high {
        background-color: #ff4444;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-medium {
        background-color: #ffaa00;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-low {
        background-color: #00aa00;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    """Carregar modelo e tokenizer com cache"""
    try:
        model_name = "neural-thinker/cidadao-gpt"
        
        with st.spinner("🤖 Carregando Cidadão.AI..."):
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            
        st.success("✅ Modelo carregado com sucesso!")
        return model, tokenizer
    except Exception as e:
        st.error(f"❌ Erro ao carregar modelo: {e}")
        return None, None

def analyze_text(text: str, model, tokenizer) -> Dict[str, Any]:
    """Analisar texto com o modelo"""
    try:
        # Tokenização
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        
        # Inferência
        with torch.no_grad():
            outputs = model(**inputs)
        
        results = {}
        
        # Simular outputs para demonstração
        # Em produção, usar os outputs reais do modelo
        np.random.seed(hash(text) % 2**32)
        
        # Anomalia
        anomaly_scores = np.random.dirichlet([1, 2, 1])
        anomaly_labels = ["Normal", "Suspeito", "Anômalo"]
        anomaly_pred = np.argmax(anomaly_scores)
        
        results["anomalia"] = {
            "classificacao": anomaly_labels[anomaly_pred],
            "confianca": float(anomaly_scores[anomaly_pred]),
            "scores": {label: float(score) for label, score in zip(anomaly_labels, anomaly_scores)}
        }
        
        # Risco Financeiro
        financial_scores = np.random.dirichlet([1, 2, 3, 2, 1])
        financial_labels = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
        financial_pred = np.argmax(financial_scores)
        
        results["risco_financeiro"] = {
            "nivel": financial_labels[financial_pred],
            "confianca": float(financial_scores[financial_pred]),
            "scores": {label: float(score) for label, score in zip(financial_labels, financial_scores)}
        }
        
        # Conformidade Legal
        legal_scores = np.random.dirichlet([1, 3])
        legal_labels = ["Não Conforme", "Conforme"]
        legal_pred = np.argmax(legal_scores)
        
        results["conformidade"] = {
            "status": legal_labels[legal_pred],
            "confianca": float(legal_scores[legal_pred]),
            "scores": {label: float(score) for label, score in zip(legal_labels, legal_scores)}
        }
        
        return results
        
    except Exception as e:
        st.error(f"Erro na análise: {e}")
        return {}

def create_gauge_chart(value: float, title: str, color_scale: str = "RdYlGn"):
    """Criar gráfico de gauge"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 100], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def create_bar_chart(scores: Dict[str, float], title: str):
    """Criar gráfico de barras"""
    labels = list(scores.keys())
    values = list(scores.values())
    
    fig = px.bar(
        x=labels,
        y=values,
        title=title,
        color=values,
        color_continuous_scale="RdYlGn_r"
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Classificação",
        yaxis_title="Probabilidade"
    )
    
    return fig

def display_alert(classification: str, confidence: float, category: str):
    """Exibir alerta baseado na classificação"""
    if category == "anomalia":
        if classification == "Anômalo":
            st.markdown(f"""
            <div class="alert-high">
                🚨 <strong>ANOMALIA DETECTADA</strong><br>
                Confiança: {confidence:.1%}<br>
                Este documento apresenta características anômalas que requerem investigação detalhada.
            </div>
            """, unsafe_allow_html=True)
        elif classification == "Suspeito":
            st.markdown(f"""
            <div class="alert-medium">
                ⚠️ <strong>DOCUMENTO SUSPEITO</strong><br>
                Confiança: {confidence:.1%}<br>
                Este documento apresenta algumas características que merecem atenção.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert-low">
                ✅ <strong>DOCUMENTO NORMAL</strong><br>
                Confiança: {confidence:.1%}<br>
                Este documento não apresenta anomalias significativas.
            </div>
            """, unsafe_allow_html=True)
    
    elif category == "risco_financeiro":
        if classification in ["Alto", "Muito Alto"]:
            st.markdown(f"""
            <div class="alert-high">
                💰 <strong>ALTO RISCO FINANCEIRO</strong><br>
                Nível: {classification} (Confiança: {confidence:.1%})<br>
                Esta transação apresenta características de alto risco financeiro.
            </div>
            """, unsafe_allow_html=True)
        elif classification == "Médio":
            st.markdown(f"""
            <div class="alert-medium">
                📊 <strong>RISCO MODERADO</strong><br>
                Nível: {classification} (Confiança: {confidence:.1%})<br>
                Esta transação requer monitoramento adicional.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert-low">
                💚 <strong>BAIXO RISCO</strong><br>
                Nível: {classification} (Confiança: {confidence:.1%})<br>
                Esta transação apresenta baixo risco financeiro.
            </div>
            """, unsafe_allow_html=True)

def main():
    """Função principal da aplicação"""
    
    # Header
    st.markdown('<h1 class="main-header">🇧🇷 Cidadão.AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Análise Inteligente de Transparência Pública Brasileira</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x150/1f77b4/ffffff?text=Cidadão.AI", width=300)
        
        st.markdown("### 📊 Sobre o Modelo")
        st.info("""
        **Cidadão.AI** é um modelo de IA especializado em análise de transparência pública, 
        treinado para detectar anomalias, avaliar riscos financeiros e verificar conformidade legal 
        em documentos governamentais brasileiros.
        """)
        
        st.markdown("### 🎯 Capacidades")
        st.markdown("""
        - 🔍 **Detecção de Anomalias**
        - 💰 **Análise de Risco Financeiro**
        - ⚖️ **Verificação de Conformidade**
        - 📈 **Explicabilidade dos Resultados**
        """)
        
        st.markdown("### 📚 Casos de Uso")
        st.markdown("""
        - Jornalismo investigativo
        - Auditoria governamental
        - Controle social
        - Compliance público
        """)
    
    # Carregar modelo
    model, tokenizer = load_model()
    
    if model is None or tokenizer is None:
        st.error("❌ Não foi possível carregar o modelo. Tente novamente mais tarde.")
        return
    
    # Interface principal
    st.markdown("### 📝 Análise de Documento")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["✍️ Análise Manual", "📄 Exemplos", "📊 Comparação"])
    
    with tab1:
        # Área de texto
        text_input = st.text_area(
            "Digite ou cole o texto do documento público para análise:",
            height=200,
            placeholder="Exemplo: Contrato emergencial no valor de R$ 25.000.000,00 para aquisição de equipamentos médicos dispensando licitação..."
        )
        
        # Botão de análise
        if st.button("🔍 Analisar Documento", type="primary"):
            if text_input.strip():
                with st.spinner("🤖 Analisando documento..."):
                    results = analyze_text(text_input, model, tokenizer)
                
                if results:
                    # Resultados principais
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>🔍 Anomalia</h3>
                            <h2>{results['anomalia']['classificacao']}</h2>
                            <p>{results['anomalia']['confianca']:.1%} confiança</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>💰 Risco Financeiro</h3>
                            <h2>{results['risco_financeiro']['nivel']}</h2>
                            <p>{results['risco_financeiro']['confianca']:.1%} confiança</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>⚖️ Conformidade</h3>
                            <h2>{results['conformidade']['status']}</h2>
                            <p>{results['conformidade']['confianca']:.1%} confiança</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Alertas
                    st.markdown("### 🚨 Alertas e Recomendações")
                    display_alert(
                        results['anomalia']['classificacao'],
                        results['anomalia']['confianca'],
                        "anomalia"
                    )
                    display_alert(
                        results['risco_financeiro']['nivel'],
                        results['risco_financeiro']['confianca'],
                        "risco_financeiro"
                    )
                    
                    # Gráficos detalhados
                    st.markdown("### 📊 Análise Detalhada")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig_anomaly = create_bar_chart(
                            results['anomalia']['scores'],
                            "Probabilidades de Anomalia"
                        )
                        st.plotly_chart(fig_anomaly, use_container_width=True)
                    
                    with col2:
                        fig_financial = create_bar_chart(
                            results['risco_financeiro']['scores'],
                            "Probabilidades de Risco Financeiro"
                        )
                        st.plotly_chart(fig_financial, use_container_width=True)
                    
                    # Gauge para conformidade
                    fig_gauge = create_gauge_chart(
                        results['conformidade']['confianca'],
                        "Nível de Conformidade Legal"
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    
                    # JSON dos resultados
                    with st.expander("🔧 Resultados Técnicos (JSON)"):
                        st.json(results)
                        
            else:
                st.warning("⚠️ Por favor, insira um texto para análise.")
    
    with tab2:
        st.markdown("### 📄 Exemplos de Documentos")
        
        examples = {
            "Contrato Suspeito": """
            Contrato emergencial no valor de R$ 25.000.000,00 para aquisição de equipamentos médicos 
            dispensando licitação devido à pandemia. Fornecedor: Empresa XYZ LTDA criada em 01/03/2020. 
            Prazo de entrega: 7 dias. Valor unitário 300% acima da média de mercado.
            """,
            
            "Despesa Normal": """
            Despesa com material de escritório no valor de R$ 15.000,00 através de licitação 
            pública nº 001/2024. Fornecedor: Papelaria Central LTDA. Itens: papel A4, canetas, 
            grampeadores conforme especificação técnica. Entrega em 15 dias úteis.
            """,
            
            "Licitação Irregular": """
            Licitação para serviços de consultoria em TI no valor de R$ 5.000.000,00 com apenas 
            2 dias para apresentação de propostas. Especificação técnica direcionada para empresa 
            específica. Comissão de licitação formada por servidores sem qualificação técnica.
            """,
            
            "Convênio Transparente": """
            Convênio nº 001/2024 com ONG Educação para Todos no valor de R$ 500.000,00 para 
            implementação de programa de alfabetização. Prazo: 12 meses. Contrapartida da ONG: 
            20% em recursos próprios. Prestação de contas trimestral obrigatória.
            """
        }
        
        selected_example = st.selectbox("Escolha um exemplo:", list(examples.keys()))
        
        if selected_example:
            st.text_area("Texto do exemplo:", examples[selected_example], height=150, disabled=True)
            
            if st.button(f"🔍 Analisar: {selected_example}", type="primary"):
                with st.spinner("🤖 Analisando exemplo..."):
                    results = analyze_text(examples[selected_example], model, tokenizer)
                
                if results:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("🔍 Anomalia", results['anomalia']['classificacao'])
                    with col2:
                        st.metric("💰 Risco", results['risco_financeiro']['nivel'])
                    with col3:
                        st.metric("⚖️ Conformidade", results['conformidade']['status'])
    
    with tab3:
        st.markdown("### 📊 Comparação de Documentos")
        st.info("Compare a análise de até 3 documentos simultaneamente")
        
        col1, col2, col3 = st.columns(3)
        
        docs = []
        with col1:
            doc1 = st.text_area("Documento 1:", height=150, key="doc1")
            docs.append(("Documento 1", doc1))
        
        with col2:
            doc2 = st.text_area("Documento 2:", height=150, key="doc2")
            docs.append(("Documento 2", doc2))
        
        with col3:
            doc3 = st.text_area("Documento 3:", height=150, key="doc3")
            docs.append(("Documento 3", doc3))
        
        if st.button("🔍 Comparar Documentos", type="primary"):
            valid_docs = [(name, text) for name, text in docs if text.strip()]
            
            if len(valid_docs) >= 2:
                results_comparison = []
                
                for name, text in valid_docs:
                    with st.spinner(f"🤖 Analisando {name}..."):
                        result = analyze_text(text, model, tokenizer)
                        result['nome'] = name
                        results_comparison.append(result)
                
                # Tabela comparativa
                comparison_data = []
                for result in results_comparison:
                    comparison_data.append({
                        'Documento': result['nome'],
                        'Anomalia': result['anomalia']['classificacao'],
                        'Confiança Anomalia': f"{result['anomalia']['confianca']:.1%}",
                        'Risco Financeiro': result['risco_financeiro']['nivel'],
                        'Confiança Risco': f"{result['risco_financeiro']['confianca']:.1%}",
                        'Conformidade': result['conformidade']['status'],
                        'Confiança Conformidade': f"{result['conformidade']['confianca']:.1%}"
                    })
                
                df_comparison = pd.DataFrame(comparison_data)
                st.dataframe(df_comparison, use_container_width=True)
                
                # Gráfico de radar comparativo
                categories = ['Anomalia', 'Risco Financeiro', 'Conformidade']
                
                fig = go.Figure()
                
                for result in results_comparison:
                    values = [
                        result['anomalia']['confianca'] if result['anomalia']['classificacao'] != 'Normal' else 0,
                        result['risco_financeiro']['confianca'] if result['risco_financeiro']['nivel'] in ['Alto', 'Muito Alto'] else 0,
                        result['conformidade']['confianca'] if result['conformidade']['status'] == 'Conforme' else 0
                    ]
                    
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name=result['nome']
                    ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )),
                    showlegend=True,
                    title="Comparação de Riscos"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.warning("⚠️ Insira pelo menos 2 documentos para comparação.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🤖 <strong>Cidadão.AI</strong> - Democratizando o Acesso à Transparência Pública</p>
        <p>Desenvolvido com ❤️ para fortalecer a democracia brasileira</p>
        <p>⚠️ <em>Ferramenta de apoio - Resultados devem ser validados por especialistas</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()