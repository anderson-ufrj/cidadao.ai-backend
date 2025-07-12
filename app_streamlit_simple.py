import streamlit as st
import json
import numpy as np
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="🇧🇷 CidadãoGPT - Análise de Transparência",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
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

def analyze_text_mock(text: str):
    """Mock analysis function - replace with real model when available"""
    # Simulate analysis based on text content
    np.random.seed(hash(text) % 2**32)
    
    # Keywords that trigger different classifications
    suspicious_keywords = ["emergencial", "dispensa", "urgência", "sem licitação", "direto"]
    high_risk_keywords = ["milhões", "elevado", "acima do mercado", "superfaturamento"]
    compliance_keywords = ["licitação", "pregão", "transparência", "regular"]
    
    text_lower = text.lower()
    
    # Count suspicious indicators
    suspicious_count = sum(1 for keyword in suspicious_keywords if keyword in text_lower)
    risk_count = sum(1 for keyword in high_risk_keywords if keyword in text_lower)
    compliance_count = sum(1 for keyword in compliance_keywords if keyword in text_lower)
    
    # Determine anomaly level
    if suspicious_count >= 2 or "emergencial" in text_lower and "milhões" in text_lower:
        anomaly_class = "Anômalo"
        anomaly_conf = 0.75 + np.random.rand() * 0.2
    elif suspicious_count >= 1:
        anomaly_class = "Suspeito"
        anomaly_conf = 0.5 + np.random.rand() * 0.3
    else:
        anomaly_class = "Normal"
        anomaly_conf = 0.7 + np.random.rand() * 0.3
    
    # Determine financial risk
    if risk_count >= 2 or "milhões" in text_lower:
        risk_level = "Alto"
        risk_conf = 0.7 + np.random.rand() * 0.2
    elif risk_count >= 1:
        risk_level = "Médio"
        risk_conf = 0.5 + np.random.rand() * 0.3
    else:
        risk_level = "Baixo"
        risk_conf = 0.6 + np.random.rand() * 0.3
    
    # Determine compliance
    if compliance_count >= 2:
        compliance_status = "Conforme"
        compliance_conf = 0.7 + np.random.rand() * 0.3
    else:
        compliance_status = "Não Conforme"
        compliance_conf = 0.6 + np.random.rand() * 0.3
    
    return {
        "anomalia": {
            "classificacao": anomaly_class,
            "confianca": anomaly_conf
        },
        "risco_financeiro": {
            "nivel": risk_level,
            "confianca": risk_conf
        },
        "conformidade": {
            "status": compliance_status,
            "confianca": compliance_conf
        }
    }

def main():
    # Header
    st.markdown('<h1 class="main-header">🇧🇷 CidadãoGPT</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Análise Inteligente de Transparência Pública Brasileira</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Sobre o Sistema")
        st.info("""
        **CidadãoGPT** é um sistema de IA especializado em análise de transparência pública, 
        desenvolvido para detectar anomalias, avaliar riscos financeiros e verificar conformidade 
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
        
        st.markdown("---")
        st.markdown("### ⚠️ Demonstração")
        st.warning("Esta é uma versão de demonstração. O modelo completo está em desenvolvimento.")
    
    # Main interface
    st.markdown("### 📝 Análise de Documento")
    
    # Example texts
    examples = {
        "Contrato Suspeito": """Contrato emergencial no valor de R$ 25.000.000,00 para aquisição de equipamentos médicos dispensando licitação devido à pandemia. Fornecedor: Empresa XYZ LTDA criada em 01/03/2020. Prazo de entrega: 7 dias. Valor unitário 300% acima da média de mercado.""",
        "Despesa Normal": """Despesa com material de escritório no valor de R$ 15.000,00 através de licitação pública nº 001/2024. Fornecedor: Papelaria Central LTDA. Itens: papel A4, canetas, grampeadores conforme especificação técnica. Entrega em 15 dias úteis.""",
        "Licitação Irregular": """Licitação para serviços de consultoria em TI no valor de R$ 5.000.000,00 com apenas 2 dias para apresentação de propostas. Especificação técnica direcionada para empresa específica."""
    }
    
    # Text input
    selected_example = st.selectbox("Escolha um exemplo ou digite seu próprio texto:", ["Texto Personalizado"] + list(examples.keys()))
    
    if selected_example == "Texto Personalizado":
        text_input = st.text_area(
            "Digite ou cole o texto do documento público para análise:",
            height=200,
            placeholder="Exemplo: Contrato emergencial no valor de R$ 25.000.000,00 para aquisição de equipamentos..."
        )
    else:
        text_input = st.text_area(
            "Texto selecionado:",
            value=examples[selected_example],
            height=200
        )
    
    # Analysis button
    if st.button("🔍 Analisar Documento", type="primary", use_container_width=True):
        if text_input.strip():
            with st.spinner("🤖 Analisando documento..."):
                # Simulate processing time
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                # Get results
                results = analyze_text_mock(text_input)
            
            # Display results
            st.markdown("---")
            st.markdown("### 📊 Resultados da Análise")
            
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
            
            # Alerts
            st.markdown("### 🚨 Alertas e Recomendações")
            
            # Anomaly alert
            if results['anomalia']['classificacao'] == "Anômalo":
                st.markdown("""
                <div class="alert-high">
                    🚨 <strong>ANOMALIA DETECTADA</strong><br>
                    Este documento apresenta características anômalas que requerem investigação detalhada.
                </div>
                """, unsafe_allow_html=True)
            elif results['anomalia']['classificacao'] == "Suspeito":
                st.markdown("""
                <div class="alert-medium">
                    ⚠️ <strong>DOCUMENTO SUSPEITO</strong><br>
                    Este documento apresenta algumas características que merecem atenção.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="alert-low">
                    ✅ <strong>DOCUMENTO NORMAL</strong><br>
                    Este documento não apresenta anomalias significativas.
                </div>
                """, unsafe_allow_html=True)
            
            # Risk alert
            if results['risco_financeiro']['nivel'] == "Alto":
                st.markdown("""
                <div class="alert-high">
                    💰 <strong>ALTO RISCO FINANCEIRO</strong><br>
                    Esta transação apresenta características de alto risco financeiro.
                </div>
                """, unsafe_allow_html=True)
            
            # JSON results
            with st.expander("🔧 Resultados Técnicos (JSON)"):
                st.json(results)
            
            # Analysis details
            with st.expander("📋 Detalhes da Análise"):
                st.markdown("""
                **Metodologia:**
                - Análise semântica do texto
                - Detecção de palavras-chave suspeitas
                - Avaliação de padrões de risco
                - Verificação de conformidade regulatória
                
                **Indicadores Analisados:**
                - Urgência/emergência sem justificativa
                - Valores acima do mercado
                - Dispensa de licitação
                - Prazos inadequados
                - Especificações direcionadas
                """)
        else:
            st.warning("⚠️ Por favor, insira um texto para análise.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🤖 <strong>CidadãoGPT</strong> - Democratizando o Acesso à Transparência Pública</p>
        <p>Desenvolvido com ❤️ para fortalecer a democracia brasileira</p>
        <p>⚠️ <em>Versão de demonstração - Resultados devem ser validados por especialistas</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()