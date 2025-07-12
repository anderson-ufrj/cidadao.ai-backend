"""
Versão com API real do Portal da Transparência
ATENÇÃO: Requer chave de API válida
"""

import gradio as gr
import os
import asyncio
import httpx
from datetime import datetime
from typing import List, Dict, Any

# Configuração da API
TRANSPARENCY_API_BASE = "https://api.portaldatransparencia.gov.br/api-de-dados"
API_KEY = os.getenv("TRANSPARENCY_API_KEY")  # Configurar no HF Spaces

async def real_api_investigate(
    query: str,
    data_source: str,
    organization: str,
    date_start: str,
    date_end: str,
    anomaly_types: list,
    include_explanations: bool
) -> str:
    """Investigação real usando API do Portal da Transparência"""
    
    if not API_KEY:
        return "❌ **Erro**: Chave da API não configurada. Configure TRANSPARENCY_API_KEY no HF Spaces."
    
    try:
        # Headers para autenticação
        headers = {
            "chave-api-dados": API_KEY,
            "Accept": "application/json"
        }
        
        # Mapear fonte de dados para endpoint
        endpoint_map = {
            "Contratos": "/contratos",
            "Despesas": "/despesas/execucao",
            "Licitações": "/licitacoes",
            "Convênios": "/convenios"
        }
        
        endpoint = endpoint_map.get(data_source, "/contratos")
        
        # Parâmetros da consulta
        params = {
            "pagina": 1,
            "tamanhoPagina": 100
        }
        
        # Adicionar filtros se fornecidos
        if organization:
            params["codigoOrgao"] = organization
        if date_start:
            params["dataInicial"] = date_start.replace("/", "-")
        if date_end:
            params["dataFinal"] = date_end.replace("/", "-")
        
        output = f"# 🔍 Investigação Real - {data_source}\n\n"
        output += f"**Query**: {query}\n"
        output += f"**Endpoint**: {TRANSPARENCY_API_BASE}{endpoint}\n\n"
        
        # Fazer requisição real
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{TRANSPARENCY_API_BASE}{endpoint}",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                total_registros = len(data) if isinstance(data, list) else data.get("total", 0)
                
                output += f"## ✅ Dados Obtidos da API\n\n"
                output += f"- **Status**: Sucesso (HTTP 200)\n"
                output += f"- **Registros**: {total_registros}\n"
                output += f"- **Timestamp**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                
                # Análise básica dos dados
                if isinstance(data, list) and len(data) > 0:
                    output += f"## 📊 Análise Preliminar\n\n"
                    
                    # Exemplo de análise simples
                    if data_source == "Contratos":
                        valores = []
                        fornecedores = set()
                        
                        for item in data[:10]:  # Analisar primeiros 10
                            if "valor" in item:
                                try:
                                    valor = float(item["valor"])
                                    valores.append(valor)
                                except:
                                    pass
                            
                            if "nomeRazaoSocialFornecedor" in item:
                                fornecedores.add(item["nomeRazaoSocialFornecedor"])
                        
                        if valores:
                            valor_medio = sum(valores) / len(valores)
                            valor_max = max(valores)
                            valor_min = min(valores)
                            
                            output += f"### 💰 Análise de Valores\n"
                            output += f"- **Valor Médio**: R$ {valor_medio:,.2f}\n"
                            output += f"- **Valor Máximo**: R$ {valor_max:,.2f}\n"
                            output += f"- **Valor Mínimo**: R$ {valor_min:,.2f}\n"
                            output += f"- **Fornecedores Únicos**: {len(fornecedores)}\n\n"
                            
                            # Detecção simples de anomalias
                            anomalias_valor = [v for v in valores if v > valor_medio * 3]
                            if anomalias_valor:
                                output += f"## 🚨 Possíveis Anomalias Detectadas\n\n"
                                output += f"### Valores Acima de 3x a Média\n"
                                output += f"- **Quantidade**: {len(anomalias_valor)}\n"
                                output += f"- **Valores**: {[f'R$ {v:,.2f}' for v in anomalias_valor[:5]]}\n\n"
                
                # Mostrar amostra dos dados
                output += f"## 📋 Amostra dos Dados (Primeiros 3 registros)\n\n"
                output += "```json\n"
                if isinstance(data, list) and len(data) > 0:
                    import json
                    for i, item in enumerate(data[:3]):
                        output += f"// Registro {i+1}\n"
                        output += json.dumps(item, indent=2, ensure_ascii=False)[:500] + "...\n\n"
                output += "```\n"
                
            elif response.status_code == 403:
                output += f"## ❌ Erro de Autenticação\n\n"
                output += f"- **Status**: HTTP 403 - Forbidden\n"
                output += f"- **Causa**: Chave de API inválida ou sem permissão\n"
                output += f"- **Solução**: Verifique se a chave está correta e ativa\n"
                
            elif response.status_code == 429:
                output += f"## ⚠️ Rate Limit Excedido\n\n"
                output += f"- **Status**: HTTP 429 - Too Many Requests\n"
                output += f"- **Causa**: Muitas requisições em pouco tempo\n"
                output += f"- **Solução**: Aguarde alguns minutos e tente novamente\n"
                
            else:
                output += f"## ❌ Erro na API\n\n"
                output += f"- **Status**: HTTP {response.status_code}\n"
                output += f"- **Resposta**: {response.text[:500]}\n"
        
        output += f"\n---\n*Consulta realizada em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}*"
        
        return output
        
    except httpx.TimeoutException:
        return "⏰ **Timeout**: A API demorou muito para responder. Tente novamente."
    except httpx.RequestError as e:
        return f"🌐 **Erro de Conexão**: {str(e)}"
    except Exception as e:
        return f"❌ **Erro Inesperado**: {str(e)}"

# Interface Gradio adaptada para API real
def create_real_api_interface():
    with gr.Blocks(title="Cidadão.AI - API Real", theme=gr.themes.Soft()) as app:
        gr.HTML("""
        <h1 style="text-align: center;">🏛️ Cidadão.AI - API Real</h1>
        <p style="text-align: center;">Conectado ao Portal da Transparência</p>
        """)
        
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(
                    label="Investigação",
                    placeholder="Descreva o que você quer investigar...",
                    lines=2
                )
                
                data_source = gr.Dropdown(
                    label="Fonte de Dados",
                    choices=["Contratos", "Despesas", "Licitações", "Convênios"],
                    value="Contratos"
                )
                
                organization = gr.Textbox(
                    label="Código do Órgão (opcional)",
                    placeholder="Ex: 26000"
                )
                
                with gr.Row():
                    date_start = gr.Textbox(label="Data Início", placeholder="DD/MM/AAAA")
                    date_end = gr.Textbox(label="Data Fim", placeholder="DD/MM/AAAA")
                
                anomaly_types = gr.CheckboxGroup(
                    label="Tipos de Anomalias",
                    choices=["Sobrepreço", "Concentração", "Temporal"],
                    value=["Sobrepreço"]
                )
                
                include_explanations = gr.Checkbox(label="Incluir explicações", value=True)
                
                investigate_btn = gr.Button("🔍 Investigar (API Real)", variant="primary")
            
            with gr.Column():
                output = gr.Markdown(value="*Aguardando investigação...*")
        
        # Conectar evento - usando async
        investigate_btn.click(
            fn=lambda *args: asyncio.run(real_api_investigate(*args)),
            inputs=[query_input, data_source, organization, date_start, date_end, anomaly_types, include_explanations],
            outputs=output
        )
        
        gr.Examples(
            examples=[
                ["Contratos emergenciais de grande valor", "Contratos", "26000", "01/01/2024", "31/12/2024", ["Sobrepreço"], True]
            ],
            inputs=[query_input, data_source, organization, date_start, date_end, anomaly_types, include_explanations]
        )
    
    return app

# Usar interface baseada se API key existe ou demo se não existe
if API_KEY:
    app = create_real_api_interface()
else:
    # Importar interface demo
    from app import app  # Interface demo original

if __name__ == "__main__":
    app.launch()