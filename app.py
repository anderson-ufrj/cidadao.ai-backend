"""
Cidadao.AI - Versao com API segura usando Secrets
"""

import gradio as gr
import os
import asyncio
import httpx
from datetime import datetime
from typing import List, Dict, Any

# Tentar multiplas formas de obter a API key
API_KEY = None
for key_name in ["TRANSPARENCY_API_KEY", "API_KEY", "PORTAL_API_KEY"]:
    API_KEY = os.getenv(key_name)
    if API_KEY:
        break

# Se nao encontrou, tentar arquivo de secrets (para Docker)
if not API_KEY:
    try:
        with open("/run/secrets/api_key", "r") as f:
            API_KEY = f.read().strip()
    except:
        pass

TRANSPARENCY_API_BASE = "https://api.portaldatransparencia.gov.br/api-de-dados"

async def investigate_with_api_key(
    query: str,
    data_source: str, 
    organization: str,
    date_start: str,
    date_end: str,
    api_key_input: str,  # API key fornecida pelo usuario
    anomaly_types: list,
    include_explanations: bool
) -> str:
    """Investigacao usando API key fornecida pelo usuario"""
    
    # Usar API key fornecida pelo usuario ou a configurada
    current_api_key = api_key_input.strip() if api_key_input.strip() else API_KEY
    
    if not current_api_key:
        return """
# API Key Necessaria

Para usar dados reais do Portal da Transparencia, voce precisa fornecer uma chave de API.

## Como obter:

1. **Acesse**: https://api.portaldatransparencia.gov.br/swagger-ui.html
2. **Solicite** uma chave de acesso
3. **Cole a chave** no campo "API Key" abaixo
4. **Execute** a investigacao

## Alternativamente:

Configure a variavel `TRANSPARENCY_API_KEY` nas configuracoes do Space para uso permanente.

**Nota**: Suas chaves ficam seguras e nao sao armazenadas.
        """
    
    try:
        headers = {
            "chave-api-dados": current_api_key,
            "Accept": "application/json",
            "User-Agent": "CidadaoAI/1.0"
        }
        
        endpoint_map = {
            "Contratos": "/contratos",
            "Despesas": "/despesas/execucao",
            "Licitacoes": "/licitacoes", 
            "Convenios": "/convenios"
        }
        
        endpoint = endpoint_map.get(data_source, "/contratos")
        
        params = {
            "pagina": 1,
            "tamanhoPagina": 30
        }
        
        if organization:
            params["codigoOrgao"] = organization
        if date_start and date_start.strip():
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
        
        output = f"# Investigacao Real - {data_source}\n\n"
        output += f"**Query**: {query}\n"
        output += f"**API**: Portal da Transparencia (Dados Oficiais)\n"
        output += f"**Timestamp**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        output += f"**API Key**: {'Configurada [OK]' if API_KEY else 'Fornecida pelo usuario'}\n\n"
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            full_url = f"{TRANSPARENCY_API_BASE}{endpoint}"
            
            response = await client.get(full_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    registros = data
                    total_registros = len(data)
                elif isinstance(data, dict):
                    registros = data.get("content", [])
                    total_registros = data.get("totalElementos", len(registros))
                else:
                    registros = []
                    total_registros = 0
                
                output += f"## Dados Obtidos\n\n"
                output += f"- **Status**: Sucesso (HTTP 200)\n"
                output += f"- **Registros**: {len(registros)}\n"
                output += f"- **Total Sistema**: {total_registros}\n\n"
                
                if registros:
                    # Analise basica
                    output += f"## Analise dos Dados\n\n"
                    
                    if data_source == "Contratos":
                        valores = []
                        fornecedores = set()
                        
                        for contract in registros[:10]:
                            # Extrair valores
                            for field in ["valor", "valorInicial", "valorContrato"]:
                                if field in contract and contract[field]:
                                    try:
                                        valor = float(str(contract[field]).replace(",", "."))
                                        if valor > 0:
                                            valores.append(valor)
                                            break
                                    except:
                                        pass
                            
                            # Extrair fornecedores
                            for field in ["nomeRazaoSocialFornecedor", "fornecedor"]:
                                if field in contract and contract[field]:
                                    fornecedores.add(str(contract[field])[:40])
                                    break
                        
                        if valores:
                            output += f"### Analise Financeira\n"
                            output += f"- **Valor Medio**: R$ {sum(valores)/len(valores):,.2f}\n"
                            output += f"- **Valor Total**: R$ {sum(valores):,.2f}\n"
                            output += f"- **Maior Valor**: R$ {max(valores):,.2f}\n"
                            output += f"- **Menor Valor**: R$ {min(valores):,.2f}\n\n"
                            
                            # Deteccao de anomalias
                            media = sum(valores) / len(valores)
                            valores_altos = [v for v in valores if v > media * 2.5]
                            
                            if valores_altos:
                                output += f"### Possiveis Anomalias\n"
                                output += f"- **{len(valores_altos)} contratos** com valores 2.5x acima da media\n"
                                output += f"- **Valores suspeitos**: {[f'R$ {v:,.0f}' for v in valores_altos[:3]]}\n\n"
                        
                        output += f"### Fornecedores\n"
                        output += f"- **Total unicos**: {len(fornecedores)}\n"
                        if fornecedores:
                            output += f"- **Lista**: {list(list(fornecedores)[:3])}\n\n"
                    
                    # Mostrar amostra dos dados
                    output += f"### Amostra dos Dados\n\n"
                    for i, registro in enumerate(registros[:2]):
                        output += f"**Registro {i+1}:**\n"
                        for key, value in list(registro.items())[:4]:
                            if value and str(value).strip():
                                output += f"- **{key}**: {str(value)[:80]}\n"
                        output += "\n"
                
                else:
                    output += f"## Nenhum Resultado\n\n"
                    output += f"Nao foram encontrados registros com os filtros aplicados.\n\n"
                    output += f"**Sugestoes:**\n"
                    output += f"- Tente um periodo maior\n"
                    output += f"- Remova filtros especificos\n"
                    output += f"- Verifique o codigo do orgao\n"
                
            elif response.status_code == 403:
                output += f"## Erro de Autenticacao\n\n"
                output += f"A chave de API fornecida nao tem permissao ou e invalida.\n\n"
                output += f"**Solucoes:**\n"
                output += f"- Verifique se a chave esta correta\n"
                output += f"- Confirme se a chave esta ativa\n"
                output += f"- Solicite uma nova chave se necessario\n"
                
            elif response.status_code == 429:
                output += f"## Limite Excedido\n\n"
                output += f"Muitas requisicoes foram feitas. Aguarde alguns minutos.\n"
                
            else:
                output += f"## Erro HTTP {response.status_code}\n\n"
                output += f"Resposta: {response.text[:200]}...\n"
        
        return output
        
    except Exception as e:
        return f"**Erro**: {str(e)}\n\nTente novamente ou verifique sua chave de API."

# Interface
with gr.Blocks(theme=gr.themes.Soft()) as app:
    gr.HTML("""
    <h1 style="text-align: center;">Cidadao.AI</h1>
    <p style="text-align: center; color: #666;">
        Investigacao com dados oficiais do Portal da Transparencia
    </p>
    """)
    
    # Status da API
    if API_KEY:
        gr.HTML("""
        <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 10px; border-radius: 5px; margin: 10px 0; text-align: center;">
            <strong>API Configurada</strong> - Chave encontrada nas configuracoes
        </div>
        """)
    else:
        gr.HTML("""
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0; text-align: center;">
            <strong>Forneca sua API Key</strong> - Cole sua chave do Portal da Transparencia abaixo
        </div>
        """)
    
    with gr.Row():
        with gr.Column():
            query_input = gr.Textbox(
                label="O que investigar?",
                placeholder="Ex: contratos emergenciais suspeitos",
                lines=2
            )
            
            data_source = gr.Dropdown(
                label="Fonte de Dados",
                choices=["Contratos", "Despesas", "Licitacoes", "Convenios"],
                value="Contratos"
            )
            
            organization = gr.Textbox(
                label="Codigo do Orgao",
                placeholder="Ex: 26000, 36000 (opcional)"
            )
            
            with gr.Row():
                date_start = gr.Textbox(
                    label="Data Inicio", 
                    placeholder="DD/MM/AAAA"
                )
                date_end = gr.Textbox(
                    label="Data Fim",
                    placeholder="DD/MM/AAAA"
                )
            
            api_key_input = gr.Textbox(
                label="API Key (se nao configurada)",
                placeholder="Cole sua chave do Portal da Transparencia",
                type="password" if not API_KEY else "text",
                value="" if not API_KEY else "Configurada [OK]"
            )
            
            anomaly_types = gr.CheckboxGroup(
                label="Tipos de Anomalias",
                choices=["Sobrepreco", "Concentracao", "Temporal"],
                value=["Sobrepreco"]
            )
            
            include_explanations = gr.Checkbox(
                label="Explicacoes detalhadas",
                value=True
            )
            
            investigate_btn = gr.Button(
                "Investigar com API Real",
                variant="primary"
            )
        
        with gr.Column():
            output = gr.Markdown(
                value="*Configure sua API key e faca sua primeira investigacao oficial!*"
            )
    
    gr.Examples(
        examples=[
            [
                "contratos de alto valor",
                "Contratos",
                "26000", 
                "01/01/2024",
                "31/12/2024",
                "",
                ["Sobrepreco"],
                True
            ]
        ],
        inputs=[query_input, data_source, organization, date_start, date_end, api_key_input, anomaly_types, include_explanations]
    )
    
    investigate_btn.click(
        fn=lambda *args: asyncio.run(investigate_with_api_key(*args)),
        inputs=[
            query_input, data_source, organization, date_start, date_end, 
            api_key_input, anomaly_types, include_explanations
        ],
        outputs=output
    )

if __name__ == "__main__":
    app.launch()