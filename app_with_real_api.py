"""
Cidadão.AI - Versão com API real do Portal da Transparência
"""

import gradio as gr
import os
import asyncio
import httpx
from datetime import datetime
from typing import List, Dict, Any

# Configuração da API
TRANSPARENCY_API_BASE = "https://api.portaldatransparencia.gov.br/api-de-dados"
API_KEY = os.getenv("TRANSPARENCY_API_KEY")

# CSS customizado
custom_css = """
.gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
#title {
    text-align: center;
    margin-bottom: 1rem;
}
.output-markdown {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 1rem;
}
"""

async def real_investigate_spending(
    query: str,
    data_source: str,
    organization: str,
    date_start: str,
    date_end: str,
    anomaly_types: list,
    include_explanations: bool
) -> str:
    """Investigação real usando API do Portal da Transparência"""
    
    # Verificar se API key está configurada
    if not API_KEY:
        return """
# ❌ Configuração Necessária

A chave da API do Portal da Transparência não está configurada.

## Como configurar:

1. Vá em **Settings** → **Variables and secrets**
2. Adicione: 
   - **Name**: `TRANSPARENCY_API_KEY`
   - **Value**: sua_chave_da_api
   - **Type**: Secret

3. Reinicie o Space

Depois a investigação usará dados reais do governo federal!
        """
    
    try:
        # Headers para autenticação
        headers = {
            "chave-api-dados": API_KEY,
            "Accept": "application/json",
            "User-Agent": "CidadaoAI/1.0"
        }
        
        # Mapear fonte de dados para endpoint
        endpoint_map = {
            "Contratos": "/contratos",
            "Despesas": "/despesas/execucao", 
            "Licitações": "/licitacoes",
            "Convênios": "/convenios",
            "Todos": "/contratos"  # Default
        }
        
        endpoint = endpoint_map.get(data_source, "/contratos")
        
        # Parâmetros da consulta
        params = {
            "pagina": 1,
            "tamanhoPagina": 50  # Limite menor para HF Spaces
        }
        
        # Adicionar filtros se fornecidos
        if organization:
            params["codigoOrgao"] = organization
        if date_start and date_start.strip():
            # Converter DD/MM/AAAA para AAAA-MM-DD
            try:
                date_parts = date_start.split("/")
                if len(date_parts) == 3:
                    params["dataInicial"] = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
            except:
                pass
        if date_end and date_end.strip():
            try:
                date_parts = date_end.split("/")
                if len(date_parts) == 3:
                    params["dataFinal"] = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
            except:
                pass
        
        output = f"# 🔍 Investigação Real - {data_source}\n\n"
        output += f"**Query**: {query}\n"
        output += f"**API**: Portal da Transparência (Dados Oficiais)\n"
        output += f"**Timestamp**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        
        # Fazer requisição real
        async with httpx.AsyncClient(timeout=20.0) as client:
            full_url = f"{TRANSPARENCY_API_BASE}{endpoint}"
            output += f"**Consultando**: {full_url}\n\n"
            
            response = await client.get(full_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Determinar total de registros
                if isinstance(data, list):
                    total_registros = len(data)
                    registros = data
                elif isinstance(data, dict):
                    total_registros = data.get("totalElementos", len(data.get("content", [])))
                    registros = data.get("content", [])
                else:
                    total_registros = 0
                    registros = []
                
                output += f"## ✅ Dados Obtidos\n\n"
                output += f"- **Status**: Sucesso (HTTP 200)\n"
                output += f"- **Registros Retornados**: {len(registros)}\n"
                output += f"- **Total no Sistema**: {total_registros}\n\n"
                
                # Análise dos dados
                if registros and len(registros) > 0:
                    output += f"## 📊 Análise dos Dados\n\n"
                    
                    # Análise específica por tipo de dados
                    if data_source == "Contratos" and registros:
                        anomalias_detectadas = analyze_contracts(registros, query)
                        if anomalias_detectadas:
                            output += anomalias_detectadas
                    
                    elif data_source == "Despesas" and registros:
                        anomalias_detectadas = analyze_expenses(registros, query)
                        if anomalias_detectadas:
                            output += anomalias_detectadas
                    
                    # Mostrar amostra dos dados
                    output += f"### 📋 Primeiros Registros\n\n"
                    for i, registro in enumerate(registros[:3]):
                        output += f"**Registro {i+1}:**\n"
                        # Mostrar campos principais
                        for key, value in list(registro.items())[:5]:
                            if value and str(value).strip():
                                output += f"- **{key}**: {value}\n"
                        output += "\n"
                
                else:
                    output += f"## ℹ️ Nenhum Registro Encontrado\n\n"
                    output += f"Não foram encontrados registros com os filtros aplicados.\n"
                    output += f"Tente:\n"
                    output += f"- Ampliar o período de datas\n"
                    output += f"- Remover filtros específicos\n"
                    output += f"- Verificar o código do órgão\n"
                
            elif response.status_code == 403:
                output += f"## ❌ Erro de Autenticação\n\n"
                output += f"- **Status**: HTTP 403 - Acesso Negado\n"
                output += f"- **Possíveis Causas**:\n"
                output += f"  - Chave de API inválida\n"
                output += f"  - Chave expirada ou suspensa\n"
                output += f"  - Falta de permissão para este endpoint\n\n"
                output += f"**Solução**: Verifique sua chave de API no Portal da Transparência\n"
                
            elif response.status_code == 429:
                output += f"## ⚠️ Limite de Requisições\n\n"
                output += f"- **Status**: HTTP 429 - Muitas Requisições\n"
                output += f"- **Limite**: Excedeu o rate limit da API\n"
                output += f"- **Solução**: Aguarde alguns minutos e tente novamente\n"
                
            elif response.status_code == 404:
                output += f"## ❌ Endpoint Não Encontrado\n\n"
                output += f"- **Status**: HTTP 404\n"
                output += f"- **Endpoint**: {endpoint}\n"
                output += f"- **Solução**: Verifique se o tipo de dados está correto\n"
                
            else:
                output += f"## ❌ Erro na API\n\n"
                output += f"- **Status**: HTTP {response.status_code}\n"
                output += f"- **Resposta**: {response.text[:300]}...\n"
        
        return output
        
    except httpx.TimeoutException:
        return "⏰ **Timeout**: A API do Portal da Transparência demorou para responder. Tente novamente."
    except httpx.RequestError as e:
        return f"🌐 **Erro de Conexão**: Não foi possível conectar à API.\nDetalhes: {str(e)}"
    except Exception as e:
        return f"❌ **Erro Inesperado**: {str(e)}\n\nTente novamente ou entre em contato com o suporte."

def analyze_contracts(contracts: List[Dict], query: str) -> str:
    """Análise específica para contratos"""
    if not contracts:
        return ""
    
    output = "### 🔍 Análise de Contratos\n\n"
    
    valores = []
    fornecedores = set()
    modalidades = {}
    
    for contract in contracts:
        # Extrair valores
        valor_fields = ["valor", "valorInicial", "valorContrato"]
        for field in valor_fields:
            if field in contract and contract[field]:
                try:
                    valor = float(str(contract[field]).replace(",", "."))
                    if valor > 0:
                        valores.append(valor)
                        break
                except:
                    pass
        
        # Extrair fornecedores
        fornecedor_fields = ["nomeRazaoSocialFornecedor", "fornecedor", "contratado"]
        for field in fornecedor_fields:
            if field in contract and contract[field]:
                fornecedores.add(str(contract[field])[:50])
                break
        
        # Extrair modalidades
        if "modalidadeLicitacao" in contract and contract["modalidadeLicitacao"]:
            mod = contract["modalidadeLicitacao"]
            modalidades[mod] = modalidades.get(mod, 0) + 1
    
    # Análise de valores
    if valores:
        valor_medio = sum(valores) / len(valores)
        valor_max = max(valores)
        valor_min = min(valores)
        
        output += f"**💰 Análise Financeira:**\n"
        output += f"- Valor Médio: R$ {valor_medio:,.2f}\n"
        output += f"- Valor Máximo: R$ {valor_max:,.2f}\n"
        output += f"- Valor Mínimo: R$ {valor_min:,.2f}\n"
        output += f"- Total Analisado: R$ {sum(valores):,.2f}\n\n"
        
        # Detectar possíveis anomalias
        anomalias = []
        
        # Valores muito altos (3x acima da média)
        valores_altos = [v for v in valores if v > valor_medio * 3]
        if valores_altos:
            anomalias.append(f"🚨 **{len(valores_altos)} contratos** com valores 3x acima da média")
        
        # Verificar se query menciona "emergencial" e detectar padrões
        if "emergencial" in query.lower():
            contratos_emergenciais = [c for c in contracts if 
                                    any(word in str(c).lower() for word in ["emergenc", "dispensa", "inexigib"])]
            if contratos_emergenciais:
                anomalias.append(f"⚠️ **{len(contratos_emergenciais)} contratos** com características emergenciais")
        
        if anomalias:
            output += f"**🚨 Possíveis Anomalias:**\n"
            for anomalia in anomalias:
                output += f"- {anomalia}\n"
            output += "\n"
    
    # Análise de fornecedores
    output += f"**🏢 Fornecedores:**\n"
    output += f"- Total de fornecedores únicos: {len(fornecedores)}\n"
    if len(fornecedores) > 0:
        output += f"- Lista (primeiros 5): {list(list(fornecedores)[:5])}\n"
    output += "\n"
    
    # Análise de modalidades
    if modalidades:
        output += f"**📋 Modalidades de Licitação:**\n"
        for mod, count in sorted(modalidades.items(), key=lambda x: x[1], reverse=True):
            output += f"- {mod}: {count} contratos\n"
        output += "\n"
    
    return output

def analyze_expenses(expenses: List[Dict], query: str) -> str:
    """Análise específica para despesas"""
    if not expenses:
        return ""
    
    output = "### 💸 Análise de Despesas\n\n"
    
    valores = []
    orgaos = set()
    
    for expense in expenses:
        # Extrair valores
        if "valor" in expense and expense["valor"]:
            try:
                valor = float(str(expense["valor"]).replace(",", "."))
                if valor > 0:
                    valores.append(valor)
            except:
                pass
        
        # Extrair órgãos
        if "nomeOrgao" in expense and expense["nomeOrgao"]:
            orgaos.add(str(expense["nomeOrgao"])[:30])
    
    if valores:
        output += f"**💰 Análise Financeira:**\n"
        output += f"- Total de Despesas: R$ {sum(valores):,.2f}\n"
        output += f"- Despesa Média: R$ {sum(valores)/len(valores):,.2f}\n"
        output += f"- Maior Despesa: R$ {max(valores):,.2f}\n\n"
    
    output += f"**🏛️ Órgãos Envolvidos:**\n"
    output += f"- Total: {len(orgaos)} órgãos\n"
    if orgaos:
        output += f"- Lista: {list(list(orgaos)[:3])}\n"
    
    return output

# Interface principal
with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as app:
    gr.HTML("""
    <h1 id="title">🏛️ Cidadão.AI - Portal da Transparência</h1>
    <p style="text-align: center; color: #666;">
        Investigação em tempo real com dados oficiais do governo federal
    </p>
    """)
    
    # Status da API
    if API_KEY:
        gr.HTML(f"""
        <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 10px; border-radius: 5px; margin: 10px 0; text-align: center;">
            ✅ <strong>API Configurada</strong> - Conectado ao Portal da Transparência
        </div>
        """)
    else:
        gr.HTML(f"""
        <div style="background: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 5px; margin: 10px 0; text-align: center;">
            ⚠️ <strong>API Não Configurada</strong> - Configure TRANSPARENCY_API_KEY nas configurações
        </div>
        """)
    
    with gr.Row():
        with gr.Column(scale=1):
            query_input = gr.Textbox(
                label="🔍 O que você quer investigar?",
                placeholder="Ex: contratos emergenciais com valores suspeitos",
                lines=3
            )
            
            data_source = gr.Dropdown(
                label="📊 Fonte de Dados",
                choices=["Contratos", "Despesas", "Licitações", "Convênios"],
                value="Contratos"
            )
            
            organization = gr.Textbox(
                label="🏛️ Código do Órgão (opcional)",
                placeholder="Ex: 26000 (Min. Educação), 36000 (Min. Saúde)"
            )
            
            with gr.Row():
                date_start = gr.Textbox(
                    label="📅 Data Início",
                    placeholder="DD/MM/AAAA"
                )
                date_end = gr.Textbox(
                    label="📅 Data Fim", 
                    placeholder="DD/MM/AAAA"
                )
            
            anomaly_types = gr.CheckboxGroup(
                label="🚨 Tipos de Anomalias",
                choices=["Sobrepreço", "Concentração de Fornecedor", "Padrões Temporais"],
                value=["Sobrepreço"]
            )
            
            include_explanations = gr.Checkbox(
                label="📝 Incluir explicações detalhadas",
                value=True
            )
            
            investigate_btn = gr.Button(
                "🔍 Investigar com API Real",
                variant="primary",
                size="lg"
            )
        
        with gr.Column(scale=2):
            output = gr.Markdown(
                value="*Faça sua primeira investigação usando dados reais do Portal da Transparência!*",
                elem_classes=["output-markdown"]
            )
    
    # Exemplos práticos
    gr.Examples(
        examples=[
            [
                "contratos emergenciais de alto valor", 
                "Contratos", 
                "26000", 
                "01/01/2024", 
                "31/12/2024", 
                ["Sobrepreço", "Concentração de Fornecedor"], 
                True
            ],
            [
                "despesas com diárias e passagens", 
                "Despesas", 
                "", 
                "01/06/2024", 
                "30/06/2024", 
                ["Padrões Temporais"], 
                True
            ],
            [
                "licitações do ministério da saúde", 
                "Licitações", 
                "36000", 
                "", 
                "", 
                ["Concentração de Fornecedor"], 
                False
            ]
        ],
        inputs=[query_input, data_source, organization, date_start, date_end, anomaly_types, include_explanations],
        label="📋 Exemplos de Investigações"
    )
    
    # Conectar evento com função async
    investigate_btn.click(
        fn=lambda *args: asyncio.run(real_investigate_spending(*args)),
        inputs=[
            query_input,
            data_source, 
            organization,
            date_start,
            date_end,
            anomaly_types,
            include_explanations
        ],
        outputs=output
    )

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )