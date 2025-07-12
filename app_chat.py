"""
Cidadao.AI - Interface de Chat estilo Claude
"""

import gradio as gr
import os
import asyncio
import httpx
from datetime import datetime
from typing import List, Dict, Any, Tuple
import json
import re

# Tentar multiplas formas de obter a API key
API_KEY = None
for key_name in ["TRANSPARENCY_API_KEY", "API_KEY", "PORTAL_API_KEY"]:
    API_KEY = os.getenv(key_name)
    if API_KEY:
        break

TRANSPARENCY_API_BASE = "https://api.portaldatransparencia.gov.br/api-de-dados"

# CSS customizado estilo Claude
custom_css = """
.gradio-container {
    max-width: 900px !important;
    margin: auto !important;
}

#chat-area {
    height: 600px !important;
}

.message {
    padding: 15px;
    margin: 10px 0;
    border-radius: 10px;
}

.user-message {
    background-color: #f7f7f8;
    margin-left: 20%;
}

.assistant-message {
    background-color: #fff;
    border: 1px solid #e5e5e5;
    margin-right: 20%;
}

#intro-text {
    text-align: center;
    color: #666;
    padding: 20px;
    font-size: 1.1em;
}

.suggested-queries {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    margin: 20px 0;
}

.suggested-query {
    background: #f0f0f0;
    padding: 8px 16px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.2s;
}

.suggested-query:hover {
    background: #e0e0e0;
}
"""

async def analyze_user_intent(message: str) -> Dict[str, Any]:
    """Analisa a intencao do usuario e extrai parametros."""
    intent = {
        "type": "general",
        "data_source": "Contratos",
        "filters": {},
        "needs_api": False
    }
    
    # Detectar tipos de dados
    if any(word in message.lower() for word in ["contrato", "contratos", "contratacao", "contratacoes"]):
        intent["data_source"] = "Contratos"
        intent["needs_api"] = True
    elif any(word in message.lower() for word in ["despesa", "gasto", "despesas", "gastos"]):
        intent["data_source"] = "Despesas"
        intent["needs_api"] = True
    elif any(word in message.lower() for word in ["licitacao", "licitacoes", "pregao", "concorrencia"]):
        intent["data_source"] = "Licitacoes"
        intent["needs_api"] = True
    elif any(word in message.lower() for word in ["convenio", "convenios", "parceria"]):
        intent["data_source"] = "Convenios"
        intent["needs_api"] = True
    
    # Detectar valores
    valor_match = re.search(r'(?:acima de|maior que|mais de)\s*(?:R\$)?\s*([\d.,]+)', message.lower())
    if valor_match:
        valor_str = valor_match.group(1).replace('.', '').replace(',', '.')
        intent["filters"]["valor_inicial"] = float(valor_str)
    
    # Detectar datas
    ano_match = re.search(r'\b(202[0-9])\b', message)
    if ano_match:
        intent["filters"]["ano"] = int(ano_match.group(1))
    
    # Detectar orgaos conhecidos
    orgaos = {
        "educacao": "26000",
        "saude": "36000",
        "ministerio da saude": "36000",
        "ministerio da educacao": "26000",
        "mec": "26000",
        "ms": "36000"
    }
    
    for nome, codigo in orgaos.items():
        if nome in message.lower():
            intent["filters"]["codigo_orgao"] = codigo
            break
    
    # Detectar analises especificas
    if any(word in message.lower() for word in ["suspeito", "anomalia", "estranho", "irregular"]):
        intent["type"] = "anomaly_detection"
    elif any(word in message.lower() for word in ["ranking", "maiores", "top"]):
        intent["type"] = "ranking"
    elif any(word in message.lower() for word in ["evolucao", "historico", "tendencia"]):
        intent["type"] = "trend"
    
    return intent

async def fetch_transparency_data(
    data_source: str,
    filters: Dict[str, Any],
    api_key: str
) -> Dict[str, Any]:
    """Busca dados na API do Portal da Transparencia."""
    
    endpoint_map = {
        "Contratos": "/contratos",
        "Despesas": "/despesas/execucao",
        "Licitacoes": "/licitacoes",
        "Convenios": "/convenios"
    }
    
    endpoint = endpoint_map.get(data_source, "/contratos")
    
    headers = {
        "chave-api-dados": api_key,
        "Accept": "application/json",
        "User-Agent": "CidadaoAI/1.0"
    }
    
    params = {
        "pagina": 1,
        "tamanhoPagina": 10  # Menos dados para respostas mais rapidas
    }
    
    # Adicionar filtros
    if "codigo_orgao" in filters:
        params["codigoOrgao"] = filters["codigo_orgao"]
    if "ano" in filters:
        params["ano"] = filters["ano"]
    if "valor_inicial" in filters:
        params["valorInicial"] = filters["valor_inicial"]
    
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{TRANSPARENCY_API_BASE}{endpoint}",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    return {"success": True, "data": data.get("content", []), "total": data.get("totalElementos", 0)}
                else:
                    return {"success": True, "data": data, "total": len(data)}
            else:
                return {"success": False, "error": f"Erro {response.status_code}: {response.text[:200]}"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

async def generate_chat_response(
    message: str,
    chat_history: List[Tuple[str, str]],
    api_key: str
) -> str:
    """Gera resposta para o chat."""
    
    # Analisar intencao
    intent = await analyze_user_intent(message)
    
    # Se nao precisa de API, dar resposta geral
    if not intent["needs_api"]:
        return """Ola! Sou o assistente do Cidadao.AI. Posso ajudar voce a investigar:

- **Contratos governamentais**: "Mostre contratos do Ministerio da Saude"
- **Despesas publicas**: "Quais foram os maiores gastos de 2024?"
- **Licitacoes**: "Procure licitacoes suspeitas"
- **Convenios**: "Liste convenios da educacao"

Como posso ajudar voce hoje?"""
    
    # Verificar API key
    if not api_key:
        return """Para acessar dados reais do Portal da Transparencia, preciso de uma chave de API.

**Como obter sua chave:**
1. Acesse: https://api.portaldatransparencia.gov.br/swagger-ui.html
2. Faca o cadastro e solicite uma chave
3. Cole a chave no campo "API Key" abaixo

Enquanto isso, posso responder perguntas gerais sobre transparencia publica!"""
    
    # Buscar dados
    response = f"Entendi! Vou buscar {intent['data_source'].lower()} "
    if intent['filters']:
        response += "com os seguintes filtros:\n"
        for key, value in intent['filters'].items():
            response += f"- {key}: {value}\n"
    response += "\nBuscando dados...\n\n"
    
    # Fazer requisicao
    result = await fetch_transparency_data(intent['data_source'], intent['filters'], api_key)
    
    if not result['success']:
        return f"Desculpe, encontrei um erro ao buscar os dados:\n{result['error']}\n\nTente reformular sua pergunta ou verificar se a API key esta correta."
    
    # Processar e formatar resposta
    data = result['data']
    total = result['total']
    
    if not data:
        return "Nao encontrei nenhum registro com esses criterios. Tente ampliar sua busca ou usar outros filtros."
    
    response = f"Encontrei **{total:,}** registros. Aqui estao os principais:\n\n"
    
    # Formatar dados por tipo
    if intent['data_source'] == "Contratos":
        for i, contrato in enumerate(data[:5], 1):
            response += f"**{i}. Contrato {contrato.get('numero', 'S/N')}**\n"
            response += f"- Fornecedor: {contrato.get('nomeRazaoSocialFornecedor', 'N/A')}\n"
            response += f"- Valor: R$ {contrato.get('valor', 0):,.2f}\n"
            response += f"- Objeto: {contrato.get('objeto', 'N/A')[:100]}...\n\n"
        
        # Analise rapida
        if intent['type'] == 'anomaly_detection':
            valores = [c.get('valor', 0) for c in data if c.get('valor')]
            if valores:
                media = sum(valores) / len(valores)
                altos = [v for v in valores if v > media * 2]
                if altos:
                    response += f"\n⚠️ **Possivel anomalia**: {len(altos)} contratos com valores 2x acima da media!"
    
    elif intent['data_source'] == "Despesas":
        for i, despesa in enumerate(data[:5], 1):
            response += f"**{i}. Despesa**\n"
            response += f"- Orgao: {despesa.get('nomeOrgao', 'N/A')}\n"
            response += f"- Valor: R$ {despesa.get('valor', 0):,.2f}\n"
            response += f"- Descricao: {despesa.get('descricao', 'N/A')[:100]}...\n\n"
    
    # Adicionar insights
    if total > len(data):
        response += f"\n*Mostrando apenas os primeiros {len(data)} de {total} registros.*"
    
    response += "\n\nQuer que eu faca uma analise mais profunda ou procure algo especifico?"
    
    return response

async def chat_interface(
    message: str,
    history: List[Tuple[str, str]],
    api_key: str
) -> Tuple[List[Tuple[str, str]], str]:
    """Interface principal do chat."""
    
    if not message:
        return history, ""
    
    # Adicionar mensagem do usuario ao historico
    history = history + [(message, None)]
    
    # Gerar resposta
    response = await generate_chat_response(message, history, api_key)
    
    # Atualizar historico com resposta
    history[-1] = (message, response)
    
    return history, ""

# Interface Gradio
with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as app:
    gr.HTML("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="font-size: 2.5em; margin-bottom: 10px;">Cidadao.AI</h1>
        <p style="color: #666; font-size: 1.2em;">
            Converse comigo sobre os gastos publicos do Brasil
        </p>
    </div>
    """)
    
    # Area de sugestoes inicial
    gr.HTML("""
    <div id="intro-text">
        <p>Faca perguntas como:</p>
        <div class="suggested-queries">
            <span class="suggested-query">Quais os maiores contratos do Ministerio da Saude?</span>
            <span class="suggested-query">Mostre gastos com educacao em 2024</span>
            <span class="suggested-query">Procure licitacoes suspeitas</span>
            <span class="suggested-query">Contratos emergenciais acima de 1 milhao</span>
        </div>
    </div>
    """)
    
    # Chat interface
    chatbot = gr.Chatbot(
        elem_id="chat-area",
        label="Conversa",
        show_label=False,
        height=500
    )
    
    with gr.Row():
        with gr.Column(scale=8):
            msg = gr.Textbox(
                label="Digite sua pergunta",
                placeholder="Ex: Quais foram os contratos mais caros do governo em 2024?",
                lines=2,
                show_label=False
            )
        with gr.Column(scale=2):
            submit = gr.Button("Enviar", variant="primary", scale=1)
    
    # API Key (opcional se configurada no ambiente)
    with gr.Accordion("Configuracoes", open=not API_KEY):
        api_key_input = gr.Textbox(
            label="API Key do Portal da Transparencia",
            placeholder="Cole sua chave aqui (opcional se ja configurada)",
            type="password" if not API_KEY else "text",
            value="" if not API_KEY else "Configurada"
        )
        
        gr.HTML("""
        <p style="font-size: 0.9em; color: #666; margin-top: 10px;">
        Nao tem uma chave? 
        <a href="https://api.portaldatransparencia.gov.br/swagger-ui.html" target="_blank">
            Solicite gratuitamente aqui
        </a>
        </p>
        """)
    
    # Exemplos
    gr.Examples(
        examples=[
            "Quais os maiores contratos do Ministerio da Saude em 2024?",
            "Mostre despesas com educacao acima de 1 milhao",
            "Procure contratos emergenciais suspeitos",
            "Qual a evolucao dos gastos publicos?",
            "Liste as maiores licitacoes do ano"
        ],
        inputs=msg,
        label="Exemplos de perguntas"
    )
    
    # Configurar eventos
    msg.submit(
        fn=lambda m, h, k: asyncio.run(chat_interface(m, h, k)),
        inputs=[msg, chatbot, api_key_input],
        outputs=[chatbot, msg]
    )
    
    submit.click(
        fn=lambda m, h, k: asyncio.run(chat_interface(m, h, k)),
        inputs=[msg, chatbot, api_key_input],
        outputs=[chatbot, msg]
    )
    
    # Link para ferramenta avancada
    gr.HTML("""
    <div style="text-align: center; margin-top: 30px; padding: 20px; border-top: 1px solid #eee;">
        <p style="color: #666;">
            Precisa de uma analise mais profunda? 
            <a href="app_advanced.py" style="color: #0066cc;">
                Use nossa ferramenta avancada
            </a>
        </p>
    </div>
    """)

if __name__ == "__main__":
    app.launch()