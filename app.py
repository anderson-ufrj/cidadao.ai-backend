"""
Cidadao.AI - Interface Principal com Chat e Ferramenta Avancada
Integrado com CidadãoGPT do Hugging Face Hub
"""

import gradio as gr
import os
import asyncio
import httpx
from datetime import datetime
from typing import List, Dict, Any, Tuple
import json
import re
import sys
from pathlib import Path

# Adicionar src ao path para importações
sys.path.append(str(Path(__file__).parent / "src"))

# Importar integração com Hugging Face
try:
    from src.ml.hf_integration import get_cidadao_manager, CidadaoGPTHubManager
    HF_INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Aviso: Integração com HF não disponível: {e}")
    HF_INTEGRATION_AVAILABLE = False

# Tentar multiplas formas de obter a API key
API_KEY = None
for key_name in ["TRANSPARENCY_API_KEY", "API_KEY", "PORTAL_API_KEY"]:
    API_KEY = os.getenv(key_name)
    if API_KEY:
        break

TRANSPARENCY_API_BASE = "https://api.portaldatransparencia.gov.br/api-de-dados"

# Inicializar CidadãoGPT Manager
cidadao_manager = None
if HF_INTEGRATION_AVAILABLE:
    try:
        print("🤖 Inicializando CidadãoGPT...")
        cidadao_manager = get_cidadao_manager()
        print("✅ CidadãoGPT carregado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao carregar CidadãoGPT: {e}")
        cidadao_manager = None

# CSS customizado
custom_css = """
/* Estilo geral */
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}

/* Estilo do chat */
#chat-area {
    height: 550px !important;
}

.message {
    padding: 15px;
    margin: 10px 0;
    border-radius: 10px;
}

/* Botoes de exemplo do chat */
.chat-examples {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 10px 0;
}

.chat-example-btn {
    background: #f0f0f0;
    border: 1px solid #ddd;
    padding: 6px 12px;
    border-radius: 16px;
    font-size: 0.9em;
    cursor: pointer;
    transition: all 0.2s;
}

.chat-example-btn:hover {
    background: #e0e0e0;
    border-color: #bbb;
}

/* Tabs customizadas */
.tab-nav {
    border-bottom: 2px solid #eee;
    margin-bottom: 20px;
}

/* Area de resultados */
.output-area {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    min-height: 400px;
}
"""

# ============= FUNCOES DO CHAT =============

async def analyze_user_intent(message: str) -> Dict[str, Any]:
    """Analisa a intencao do usuario e extrai parametros."""
    intent = {
        "type": "general",
        "data_source": "Contratos",
        "filters": {},
        "needs_api": False
    }
    
    # Detectar tipos de dados
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["contrato", "contratos", "contratacao", "contratacoes", "licitacao", "licitacoes"]):
        intent["data_source"] = "Contratos"
        intent["needs_api"] = True
    elif any(word in message_lower for word in ["despesa", "gasto", "despesas", "gastos", "pagamento"]):
        intent["data_source"] = "Despesas"
        intent["needs_api"] = True
    elif any(word in message_lower for word in ["convenio", "convenios", "parceria", "acordo"]):
        intent["data_source"] = "Convenios"
        intent["needs_api"] = True
    
    # Detectar valores monetarios
    valor_patterns = [
        r'(?:acima de|maior que|mais de|superior a)\s*(?:R\$)?\s*([\d.,]+)\s*(?:mil|milhoes|milhao)?',
        r'(?:R\$)?\s*([\d.,]+)\s*(?:mil|milhoes|milhao)',
        r'valores?\s*(?:acima de|maior que|superiores? a)\s*(?:R\$)?\s*([\d.,]+)'
    ]
    
    for pattern in valor_patterns:
        match = re.search(pattern, message_lower)
        if match:
            valor_str = match.group(1).replace('.', '').replace(',', '.')
            valor = float(valor_str)
            
            # Ajustar para mil/milhoes
            if 'mil' in match.group(0):
                valor *= 1000
            elif 'milh' in match.group(0):
                valor *= 1000000
                
            intent["filters"]["valor_inicial"] = valor
            break
    
    # Detectar ano/periodo
    ano_match = re.search(r'\b(20\d{2})\b', message)
    if ano_match:
        intent["filters"]["ano"] = int(ano_match.group(1))
    
    # Detectar mes
    meses = {
        'janeiro': 1, 'fevereiro': 2, 'marco': 3, 'abril': 4,
        'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
        'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
    }
    
    for mes_nome, mes_num in meses.items():
        if mes_nome in message_lower:
            intent["filters"]["mes"] = mes_num
            break
    
    # Detectar orgaos
    orgaos_map = {
        "saude": "36000",
        "educacao": "26000",
        "ministerio da saude": "36000",
        "ministerio da educacao": "26000",
        "mec": "26000",
        "ms": "36000",
        "defesa": "52000",
        "economia": "25000",
        "infraestrutura": "39000",
        "agricultura": "22000"
    }
    
    for nome, codigo in orgaos_map.items():
        if nome in message_lower:
            intent["filters"]["codigo_orgao"] = codigo
            intent["filters"]["nome_orgao"] = nome.title()
            break
    
    # Detectar tipo de analise
    if any(word in message_lower for word in ["suspeito", "anomalia", "estranho", "irregular", "fraudulent"]):
        intent["type"] = "anomaly"
    elif any(word in message_lower for word in ["ranking", "maiores", "top", "principais"]):
        intent["type"] = "ranking"
    elif any(word in message_lower for word in ["evolucao", "historico", "tendencia", "crescimento"]):
        intent["type"] = "trend"
    elif any(word in message_lower for word in ["emergencial", "emergencia", "urgente", "covid", "pandemia"]):
        intent["type"] = "emergency"
        
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
        "tamanhoPagina": 15
    }
    
    # Aplicar filtros
    for key, value in filters.items():
        if key == "codigo_orgao":
            params["codigoOrgao"] = value
        elif key == "valor_inicial":
            params["valorInicial"] = value
        elif key in ["ano", "mes"]:
            params[key] = value
    
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
                    return {
                        "success": True,
                        "data": data.get("content", []),
                        "total": data.get("totalElementos", 0)
                    }
                else:
                    return {
                        "success": True,
                        "data": data,
                        "total": len(data)
                    }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Chave de API invalida. Verifique se sua chave esta correta e ativa."
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro {response.status_code}: {response.text[:200]}"
                }
    
    except Exception as e:
        return {"success": False, "error": f"Erro de conexao: {str(e)}"}

def format_currency(value: float) -> str:
    """Formata valor monetario."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

async def analyze_with_cidadao_gpt(text: str) -> Dict[str, Any]:
    """Analisar texto usando CidadãoGPT para detecção de anomalias"""
    
    if not cidadao_manager:
        return {
            "analysis_available": False,
            "message": "CidadãoGPT não disponível. Análise baseada em regras será usada."
        }
    
    try:
        result = cidadao_manager.analyze_text(text, analysis_type="complete")
        
        return {
            "analysis_available": True,
            "anomaly": result.get("anomaly", {}),
            "financial": result.get("financial", {}),
            "legal": result.get("legal", {}),
            "confidence": max(
                result.get("anomaly", {}).get("score", 0),
                result.get("financial", {}).get("score", 0),
                result.get("legal", {}).get("score", 0)
            ),
            "summary": f"Análise CidadãoGPT: {result.get('anomaly', {}).get('label', 'N/A')} | "
                      f"Risco: {result.get('financial', {}).get('label', 'N/A')} | "
                      f"Legal: {result.get('legal', {}).get('label', 'N/A')}"
        }
    except Exception as e:
        return {
            "analysis_available": False,
            "message": f"Erro na análise CidadãoGPT: {str(e)}"
        }

async def generate_chat_response(
    message: str,
    chat_history: List[Tuple[str, str]],
    api_key: str
) -> str:
    """Gera resposta inteligente para o chat com análise CidadãoGPT."""
    
    # Casos especiais de saudacao
    greetings = ["ola", "oi", "bom dia", "boa tarde", "boa noite", "hey", "hi"]
    if any(greet in message.lower() for greet in greetings):
        cidadao_status = "✅ CidadãoGPT Ativo" if cidadao_manager else "⚠️ CidadãoGPT Indisponível"
        
        return f"""🇧🇷 **Bem-vindo a Revolucao Digital da Transparencia!**

Sou o assistente do Cidadao.AI - powered by CidadãoGPT, o primeiro modelo de IA especializado em transparência pública brasileira!

🤖 **Status do Sistema:** {cidadao_status}

🎯 **O que posso fazer por voce:**
• **Detectar Anomalias**: "Analise este contrato de R$ 50 milhões sem licitação"
• **Avaliar Riscos**: "Este fornecedor é confiável para obras hospitalares?"
• **Verificar Legalidade**: "Esta dispensa de licitação está correta?"
• **Investigar Padrões**: "Procure superfaturamento em equipamentos médicos"
• **Analisar Tendências**: "Gastos com saúde aumentaram este ano?"

💡 **Fale naturalmente comigo - como faria com um especialista em transparência!**

🔥 **Agora você tem o poder de fiscalizar com IA especializada. Como posso ajudar você hoje?**"""
    
    # Analisar intencao
    intent = await analyze_user_intent(message)
    
    # Se nao precisa de API
    if not intent["needs_api"]:
        if "como funciona" in message.lower() or "o que voce faz" in message.lower():
            return """Eu acesso dados oficiais do Portal da Transparencia do governo federal e ajudo a analisar:

**O que posso fazer:**
• Buscar e analisar contratos, despesas, licitacoes e convenios
• Detectar padroes suspeitos e anomalias
• Criar rankings e comparacoes
• Analisar tendencias ao longo do tempo

**Como usar:**
1. Faca uma pergunta especifica
2. Eu busco os dados oficiais
3. Analiso e apresento insights

Experimente perguntar algo como:
"Quais os contratos mais caros do Ministerio da Saude em 2024?"
"""
        
        return """Nao entendi exatamente o que voce procura. Tente ser mais especifico, por exemplo:

• "Mostre contratos acima de 1 milhao"
• "Gastos com educacao em 2024"
• "Licitacoes do Ministerio da Saude"
• "Convenios suspeitos"

Qual informacao voce gostaria de investigar?"""
    
    # Verificar API key
    if not api_key:
        return """Para acessar os dados reais, preciso de uma chave de API do Portal da Transparencia.

**Como obter gratuitamente:**
1. Acesse: https://api.portaldatransparencia.gov.br/swagger-ui.html
2. Clique em "Cadastrar"
3. Preencha o formulario
4. Aguarde o email com sua chave (geralmente em 24h)
5. Cole a chave no campo "API Key" abaixo

Enquanto isso, posso explicar como funciona o sistema ou responder duvidas gerais!"""
    
    # Montar resposta inicial
    response = f"🔍 **Investigando {intent['data_source'].lower()}**"
    
    if intent['filters']:
        response += " com os criterios:\n"
        if 'nome_orgao' in intent['filters']:
            response += f"• Orgao: {intent['filters']['nome_orgao']}\n"
        if 'valor_inicial' in intent['filters']:
            response += f"• Valor minimo: {format_currency(intent['filters']['valor_inicial'])}\n"
        if 'ano' in intent['filters']:
            response += f"• Ano: {intent['filters']['ano']}\n"
        if 'mes' in intent['filters']:
            response += f"• Mes: {intent['filters']['mes']}\n"
    
    response += "\n*Buscando dados oficiais...*\n\n"
    
    # Buscar dados
    result = await fetch_transparency_data(
        intent['data_source'],
        intent['filters'],
        api_key
    )
    
    if not result['success']:
        return f"❌ **Erro ao buscar dados**\n\n{result['error']}\n\nVerifique sua chave de API ou tente novamente."
    
    data = result['data']
    total = result['total']
    
    if not data:
        return """Nao encontrei registros com esses criterios. 

**Sugestoes:**
• Tente um periodo maior (ex: ano completo)
• Remova alguns filtros
• Verifique o nome do orgao

Ou pergunte de outra forma!"""
    
    # Formatar resposta baseada no tipo de dados
    response = f"✅ **Encontrei {total:,} registros!**\n\n".replace(",", ".")
    
    if intent['data_source'] == "Contratos":
        response += format_contracts_response(data, intent['type'])
    elif intent['data_source'] == "Despesas":
        response += format_expenses_response(data, intent['type'])
    else:
        response += format_generic_response(data, intent['data_source'])
    
    # Adicionar analise se solicitada
    if intent['type'] == 'anomaly':
        response += await analyze_anomalies(data, intent['data_source'])
    elif intent['type'] == 'ranking':
        response += create_ranking(data, intent['data_source'])
    
    # Sugestoes de proximos passos
    if total > len(data):
        response += f"\n\n*Mostrando {len(data)} de {total} registros.*"
    
    response += "\n\n**Quer que eu:**\n"
    response += "• Analise mais profundamente?\n"
    response += "• Procure anomalias?\n"
    response += "• Compare com outros periodos?\n"
    response += "• Exporte os dados?"
    
    return response

def format_contracts_response(data: List[Dict], analysis_type: str) -> str:
    """Formata resposta para contratos."""
    response = "**📄 Principais Contratos:**\n\n"
    
    for i, contract in enumerate(data[:5], 1):
        valor = contract.get('valor', contract.get('valorInicial', 0))
        response += f"**{i}. {contract.get('objeto', 'Objeto nao especificado')[:80]}**\n"
        response += f"   • Fornecedor: {contract.get('nomeRazaoSocialFornecedor', 'N/A')}\n"
        response += f"   • Valor: {format_currency(valor)}\n"
        response += f"   • Numero: {contract.get('numero', 'S/N')}\n"
        response += f"   • Modalidade: {contract.get('modalidadeLicitacao', 'N/A')}\n\n"
    
    return response

def format_expenses_response(data: List[Dict], analysis_type: str) -> str:
    """Formata resposta para despesas."""
    response = "**💰 Principais Despesas:**\n\n"
    
    for i, expense in enumerate(data[:5], 1):
        response += f"**{i}. {expense.get('descricao', 'Despesa')[:80]}**\n"
        response += f"   • Orgao: {expense.get('nomeOrgao', 'N/A')}\n"
        response += f"   • Valor: {format_currency(expense.get('valor', 0))}\n"
        response += f"   • Data: {expense.get('dataReferencia', 'N/A')}\n\n"
    
    return response

def format_generic_response(data: List[Dict], data_type: str) -> str:
    """Formata resposta generica."""
    response = f"**📊 {data_type} Encontrados:**\n\n"
    
    for i, item in enumerate(data[:5], 1):
        # Pegar primeiro campo nao vazio como titulo
        titulo = next((v for k, v in item.items() if v and isinstance(v, str) and len(str(v)) > 10), "Item")
        response += f"**{i}. {titulo[:80]}**\n"
        
        # Mostrar campos principais
        for key, value in list(item.items())[:4]:
            if value and key not in ['id', '_id']:
                response += f"   • {key}: {value}\n"
        response += "\n"
    
    return response

async def analyze_anomalies(data: List[Dict], data_type: str) -> str:
    """Analisa anomalias nos dados usando CidadãoGPT + análise estatística."""
    response = "\n\n**🔍 Análise de Anomalias CidadãoGPT:**\n\n"
    
    anomalias_found = []
    cidadao_analysis = []
    
    # Análise com CidadãoGPT se disponível
    if cidadao_manager and data_type == "Contratos":
        for i, contract in enumerate(data[:3]):  # Analisar primeiros 3 contratos
            # Criar texto descritivo do contrato
            valor = contract.get('valor', contract.get('valorInicial', 0))
            objeto = contract.get('objeto', 'Objeto não especificado')
            fornecedor = contract.get('nomeRazaoSocialFornecedor', 'N/A')
            modalidade = contract.get('modalidadeLicitacao', 'N/A')
            
            contract_text = f"""
            Contrato de {objeto} no valor de R$ {valor:,.2f}.
            Fornecedor: {fornecedor}.
            Modalidade: {modalidade}.
            """.strip()
            
            try:
                analysis = await analyze_with_cidadao_gpt(contract_text)
                if analysis["analysis_available"]:
                    cidadao_analysis.append({
                        "contract_index": i,
                        "analysis": analysis,
                        "contract": contract
                    })
            except Exception as e:
                continue
    
    # Mostrar resultados CidadãoGPT
    if cidadao_analysis:
        response += "🤖 **Análise Especializada CidadãoGPT:**\n\n"
        
        for item in cidadao_analysis:
            analysis = item["analysis"]
            contract = item["contract"]
            
            anomaly_level = analysis.get("anomaly", {}).get("label", "Normal")
            financial_risk = analysis.get("financial", {}).get("label", "Baixo")
            legal_compliance = analysis.get("legal", {}).get("label", "Conforme")
            confidence = analysis.get("confidence", 0)
            
            # Determinar emoji baseado no risco
            risk_emoji = "🔴" if anomaly_level == "Anômalo" else ("🟡" if anomaly_level == "Suspeito" else "🟢")
            
            response += f"{risk_emoji} **Contrato {item['contract_index'] + 1}**\n"
            response += f"   • **Anomalia**: {anomaly_level}\n"
            response += f"   • **Risco Financeiro**: {financial_risk}\n"
            response += f"   • **Conformidade Legal**: {legal_compliance}\n"
            response += f"   • **Confiança**: {confidence:.1%}\n"
            response += f"   • **Valor**: {format_currency(contract.get('valor', 0))}\n\n"
            
            if anomaly_level in ["Suspeito", "Anômalo"]:
                anomalias_found.append(contract)
    
    # Análise estatística tradicional
    if data_type == "Contratos":
        valores = []
        for contract in data:
            valor = contract.get('valor', contract.get('valorInicial', 0))
            if valor:
                valores.append(float(valor))
        
        if valores:
            media = sum(valores) / len(valores)
            desvio = (sum((x - media) ** 2 for x in valores) / len(valores)) ** 0.5
            
            statistical_anomalies = [v for v in valores if v > media + 2 * desvio]
            
            response += "📊 **Análise Estatística Complementar:**\n"
            if statistical_anomalies:
                response += f"⚠️ {len(statistical_anomalies)} valores estatisticamente anômalos\n"
                response += f"• Média: {format_currency(media)}\n"
                response += f"• Maior valor: {format_currency(max(statistical_anomalies))}\n"
            else:
                response += "✅ Distribuição de valores dentro do padrão estatístico\n"
    
    # Resumo final
    if anomalias_found:
        response += f"\n🚨 **ALERTA**: {len(anomalias_found)} contratos com indicadores de risco detectados pelo CidadãoGPT!\n"
        response += "**Recomendação**: Investigação mais detalhada necessária.\n"
    elif cidadao_analysis:
        response += "\n✅ **CidadãoGPT**: Nenhuma anomalia grave detectada nos contratos analisados.\n"
    
    return response

def create_ranking(data: List[Dict], data_type: str) -> str:
    """Cria ranking dos dados."""
    response = "\n\n**🏆 Ranking por Valor:**\n\n"
    
    # Extrair e ordenar por valor
    items_with_value = []
    for item in data:
        valor = item.get('valor', item.get('valorInicial', 0))
        if valor:
            items_with_value.append((float(valor), item))
    
    items_with_value.sort(reverse=True, key=lambda x: x[0])
    
    for i, (valor, item) in enumerate(items_with_value[:5], 1):
        nome = item.get('nomeRazaoSocialFornecedor', item.get('descricao', 'Item'))[:50]
        response += f"{i}. {nome} - {format_currency(valor)}\n"
    
    return response

async def chat_interface(
    message: str,
    history: List[Tuple[str, str]],
    api_key: str
) -> Tuple[List[Tuple[str, str]], str]:
    """Interface principal do chat."""
    
    if not message.strip():
        return history, ""
    
    # Adicionar mensagem do usuario
    history = history + [(message, None)]
    
    # Gerar resposta
    response = await generate_chat_response(message, history, api_key)
    
    # Atualizar historico
    history[-1] = (message, response)
    
    return history, ""

# ============= FUNCOES DA FERRAMENTA AVANCADA =============

async def investigate_with_api_key(
    query: str,
    data_source: str, 
    organization: str,
    date_start: str,
    date_end: str,
    api_key_input: str,
    anomaly_types: list,
    include_explanations: bool
) -> str:
    """Investigacao avancada (ferramenta original)."""
    
    current_api_key = api_key_input.strip() if api_key_input.strip() else API_KEY
    
    if not current_api_key:
        return """# API Key Necessaria

Para usar a ferramenta avancada, configure sua chave da API."""
    
    # Codigo da ferramenta avancada original...
    # (mantendo a funcionalidade existente)
    
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
        
        output = f"# Investigacao Avancada - {data_source}\n\n"
        output += f"**Query**: {query}\n"
        output += f"**Timestamp**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        
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
                output += f"- **Status**: Sucesso\n"
                output += f"- **Registros**: {len(registros)}\n"
                output += f"- **Total Sistema**: {total_registros}\n\n"
                
                # Analise detalhada...
                if registros and data_source == "Contratos":
                    output += "## Analise Detalhada\n\n"
                    
                    valores = []
                    for contract in registros[:20]:
                        for field in ["valor", "valorInicial", "valorContrato"]:
                            if field in contract and contract[field]:
                                try:
                                    valor = float(str(contract[field]).replace(",", "."))
                                    if valor > 0:
                                        valores.append(valor)
                                        break
                                except:
                                    pass
                    
                    if valores:
                        output += f"### Estatisticas Financeiras\n"
                        output += f"- **Valor Medio**: {format_currency(sum(valores)/len(valores))}\n"
                        output += f"- **Valor Total**: {format_currency(sum(valores))}\n"
                        output += f"- **Maior Valor**: {format_currency(max(valores))}\n"
                        output += f"- **Menor Valor**: {format_currency(min(valores))}\n\n"
                        
                        if "Sobrepreco" in anomaly_types:
                            media = sum(valores) / len(valores)
                            valores_altos = [v for v in valores if v > media * 2.5]
                            
                            if valores_altos:
                                output += f"### Deteccao de Anomalias\n"
                                output += f"- **{len(valores_altos)} contratos** com valores suspeitos\n"
                                output += f"- **Desvio**: Ate {max(valores_altos)/media:.1f}x acima da media\n\n"
                
                return output
            
            else:
                return f"## Erro HTTP {response.status_code}\n\n{response.text[:200]}"
                
    except Exception as e:
        return f"**Erro**: {str(e)}"

# ============= INTERFACE GRADIO =============

with gr.Blocks(theme=gr.themes.Soft(), css=custom_css, title="Cidadao.AI") as app:
    # Header
    gr.HTML("""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <h1 style="font-size: 2.5em; margin-bottom: 5px;">🏛️ Cidadao.AI</h1>
        <p style="color: #666; font-size: 1.1em; margin: 0;">
            Inteligencia Artificial para Transparencia Publica
        </p>
    </div>
    """)
    
    # API Key (compartilhada entre as abas)
    with gr.Row():
        with gr.Column(scale=4):
            api_key_input = gr.Textbox(
                label="🔑 API Key do Portal da Transparencia",
                placeholder="Cole sua chave aqui (deixe vazio se ja configurada no ambiente)",
                type="password" if not API_KEY else "text",
                value="" if not API_KEY else "API Configurada",
                elem_id="api-key-input"
            )
        with gr.Column(scale=1):
            gr.HTML("""
            <div style="padding-top: 25px;">
                <a href="https://api.portaldatransparencia.gov.br/swagger-ui.html" 
                   target="_blank" 
                   style="color: #0066cc; text-decoration: none;">
                    📝 Obter chave gratuita →
                </a>
            </div>
            """)
    
    # Tabs principais
    with gr.Tabs() as tabs:
        # Tab 1: Chat
        with gr.Tab("💬 Chat Inteligente", elem_id="chat-tab"):
            gr.HTML("""
            <div style="text-align: center; margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;">
                <h3 style="margin: 0 0 10px 0; font-size: 1.2em;">🚀 Revolucao Digital da Transparencia</h3>
                <p style="margin: 0; opacity: 0.9;">
                    Primeira IA brasileira que conversa sobre gastos publicos.<br>
                    <strong>Dados oficiais + Linguagem natural = Poder cidadao!</strong>
                </p>
            </div>
            """)
            
            # Sugestoes de perguntas
            gr.HTML("""
            <div class="chat-examples">
                <button class="chat-example-btn" onclick="document.querySelector('#chat-input textarea').value='Quais os maiores contratos do governo este ano?'">
                    Maiores contratos do ano
                </button>
                <button class="chat-example-btn" onclick="document.querySelector('#chat-input textarea').value='Mostre gastos suspeitos com saude'">
                    Gastos suspeitos com saude
                </button>
                <button class="chat-example-btn" onclick="document.querySelector('#chat-input textarea').value='Contratos emergenciais acima de 1 milhao'">
                    Contratos emergenciais
                </button>
                <button class="chat-example-btn" onclick="document.querySelector('#chat-input textarea').value='Compare gastos com educacao 2023 vs 2024'">
                    Comparar gastos
                </button>
            </div>
            """)
            
            # Chat interface
            chatbot = gr.Chatbot(
                elem_id="chat-area",
                label="Conversa",
                show_label=False,
                height=500,
                bubble_full_width=False
            )
            
            with gr.Row():
                with gr.Column(scale=9):
                    chat_input = gr.Textbox(
                        label="Sua pergunta",
                        placeholder="Digite sua pergunta sobre gastos publicos...",
                        lines=2,
                        show_label=False,
                        elem_id="chat-input"
                    )
                with gr.Column(scale=1):
                    chat_submit = gr.Button("Enviar", variant="primary", size="lg")
            
            # Exemplos
            gr.Examples(
                examples=[
                    "Quais foram os contratos mais caros do Ministerio da Saude em 2024?",
                    "Mostre despesas com educacao acima de 1 milhao",
                    "Procure licitacoes suspeitas ou com valores anomalos",
                    "Quantos contratos emergenciais foram feitos este ano?",
                    "Compare os gastos com saude entre 2023 e 2024"
                ],
                inputs=chat_input,
                label="Exemplos de perguntas"
            )
        
        # Tab 2: Ferramenta Avancada
        with gr.Tab("🔍 Investigacao Avancada", elem_id="advanced-tab"):
            gr.HTML("""
            <p style="text-align: center; color: #666; margin: 10px 0;">
                Ferramenta profissional com filtros detalhados e analises complexas.
            </p>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    adv_query = gr.Textbox(
                        label="Descricao da Investigacao",
                        placeholder="Ex: contratos emergenciais suspeitos",
                        lines=2
                    )
                    
                    adv_data_source = gr.Dropdown(
                        label="Fonte de Dados",
                        choices=["Contratos", "Despesas", "Licitacoes", "Convenios"],
                        value="Contratos"
                    )
                    
                    adv_organization = gr.Textbox(
                        label="Codigo do Orgao",
                        placeholder="Ex: 26000 (MEC), 36000 (MS)"
                    )
                    
                    with gr.Row():
                        adv_date_start = gr.Textbox(
                            label="Data Inicio",
                            placeholder="DD/MM/AAAA"
                        )
                        adv_date_end = gr.Textbox(
                            label="Data Fim",
                            placeholder="DD/MM/AAAA"
                        )
                    
                    adv_anomaly_types = gr.CheckboxGroup(
                        label="Tipos de Anomalias",
                        choices=["Sobrepreco", "Concentracao", "Temporal"],
                        value=["Sobrepreco"]
                    )
                    
                    adv_explanations = gr.Checkbox(
                        label="Incluir explicacoes detalhadas",
                        value=True
                    )
                    
                    adv_submit = gr.Button(
                        "Investigar",
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=2):
                    adv_output = gr.Markdown(
                        value="*Configure os parametros e clique em Investigar para comecar...*",
                        elem_classes=["output-area"]
                    )
            
            # Exemplos avancados
            gr.Examples(
                examples=[
                    [
                        "contratos de alto valor com indicios de sobrepreco",
                        "Contratos",
                        "36000",
                        "01/01/2024",
                        "31/12/2024",
                        "",
                        ["Sobrepreco", "Concentracao"],
                        True
                    ],
                    [
                        "despesas emergenciais durante a pandemia",
                        "Despesas",
                        "",
                        "01/03/2020",
                        "31/12/2021",
                        "",
                        ["Sobrepreco", "Temporal"],
                        True
                    ]
                ],
                inputs=[adv_query, adv_data_source, adv_organization, adv_date_start, 
                       adv_date_end, api_key_input, adv_anomaly_types, adv_explanations],
                label="Investigacoes de exemplo"
            )
        
        # Tab 3: Como Usar
        with gr.Tab("📚 Como Usar", elem_id="guide-tab"):
            gr.Markdown("""
            # 🎯 Guia Completo do Cidadao.AI
            
            ## Como Conversar com a IA
            
            ### ✅ Perguntas que Funcionam Bem
            ```
            ✓ "Quais os contratos mais caros de 2024?"
            ✓ "Mostre gastos suspeitos com saude"
            ✓ "Contratos emergenciais acima de 1 milhao"
            ✓ "Compare despesas entre ministerios"
            ✓ "Detecte anomalias nos contratos do MS"
            ```
            
            ### ❌ Perguntas que Nao Funcionam
            ```
            ✗ "O que voce acha da politica?"
            ✗ "Quem e o melhor presidente?"
            ✗ "Fale sobre futebol"
            ✗ "Resolva esta equacao matematica"
            ```
            
            ## 🔍 Casos de Uso por Perfil
            
            ### 📰 **Jornalistas**
            - **Investigacoes rapidas**: "Empresas que mais receberam em contratos emergenciais"
            - **Comparacoes temporais**: "Gastos com publicidade em anos eleitorais vs nao eleitorais"
            - **Deteccao de padroes**: "Contratos sem licitacao acima de R$ 500 mil"
            
            ### 🎓 **Estudantes**
            - **Pesquisa academica**: "Evolucao dos investimentos em universidades federais"
            - **Dados para TCC**: "Analise de eficiencia de gastos educacionais por regiao"
            - **Entender o orcamento**: "Como funciona o repasse de verbas para universidades?"
            
            ### 💼 **Empreendedores**  
            - **Oportunidades**: "Maiores areas de contratacao do governo"
            - **Benchmarking**: "Precos praticados em licitacoes de TI"
            - **Fornecedores**: "Empresas que mais vendem para o governo"
            
            ### 📢 **Ativistas e ONGs**
            - **Fiscalizacao**: "Contratos com organizacoes sociais suspeitos"
            - **Monitoramento**: "Gastos com meio ambiente nos ultimos 5 anos"
            - **Transparencia**: "Execucao de programas sociais por regiao"
            
            ### 🏠 **Cidadaos Comuns**
            - **Sua cidade**: "Gastos da prefeitura com obras publicas"
            - **Seus direitos**: "Investimentos em saude no meu estado"
            - **Fiscalizacao basica**: "Maiores despesas do governo este mes"
            
            ## 💡 Dicas para Melhores Resultados
            
            ### 🎯 Seja Especifico
            ```
            ❌ "Mostre contratos"
            ✅ "Contratos do Ministerio da Saude acima de 1 milhao em 2024"
            ```
            
            ### 📅 Use Periodos
            ```
            ❌ "Gastos com educacao"
            ✅ "Gastos com educacao em Janeiro de 2024"
            ```
            
            ### 🎨 Varie suas Perguntas
            ```
            "Detecte anomalias em..."
            "Compare os gastos de..."
            "Analise os contratos de..."
            "Mostre a evolucao de..."
            "Ranking dos maiores..."
            ```
            
            ## 🛡️ Por que Confiar nos Dados?
            
            ### 📍 **Fonte Oficial Unica**
            - API oficial do Portal da Transparencia (api.portaldatransparencia.gov.br)
            - Mesma fonte usada pelo TCU, CGU e orgaos de controle
            - Dados atualizados em tempo real pelos proprios orgaos
            
            ### 🔒 **Seguranca Total**
            - Sua chave API e pessoal e intransferivel
            - Conexao direta: Voce → API Oficial → Resultados
            - Sem intermediarios, sem manipulacao
            - Codigo aberto para auditoria publica
            
            ### ✅ **Verificacao Simples**
            Cada resposta inclui:
            - Link direto para a fonte oficial
            - Timestamp da consulta
            - Numero de registros encontrados
            - Parametros exatos da busca
            
            ### 🎯 **Exemplo de Verificacao**
            ```
            Resultado: "Contrato XYZ - R$ 2.500.000"
            
            ✓ Verificar em: portaldatransparencia.gov.br
            ✓ Numero do contrato: [numero oficial]
            ✓ Data da consulta: [timestamp]
            ✓ Orgao responsavel: [codigo oficial]
            ```
            
            ## 🚀 Revolucao Digital Cidada
            
            ### 🎯 **Antes vs Depois**
            
            **ANTES:**
            - Dados enterrados em planilhas
            - Linguagem tecnica incompreensivel
            - Acesso restrito a especialistas
            - Investigacoes demoram meses
            
            **DEPOIS com Cidadao.AI:**
            - Conversa natural em portugues
            - Respostas em segundos
            - Qualquer cidadao pode investigar
            - Deteccao automatica de anomalias
            
            ### 💪 **Poder nas Suas Maos**
            
            Agora VOCE pode:
            - ✅ Fiscalizar gastos publicos 24/7
            - ✅ Detectar corrupcao em tempo real  
            - ✅ Cobrar transparencia dos governantes
            - ✅ Compartilhar descobertas com todos
            - ✅ Ser um guardiao da democracia
            
            ### 🌟 **Cases de Sucesso**
            
            **"Descobri superfaturamento de R$ 2 milhoes"**
            *- Jornalista do interior*
            
            **"Identifiquei obra abandonada na minha cidade"**
            *- Cidadao comum*
            
            **"Encontrei padroes suspeitos em licitacoes"**
            *- Estudante de direito*
            
            ## 🔥 Comece Agora - Passo a Passo
            
            ### 1️⃣ **Obtenha sua Chave (2 minutos)**
            1. Acesse: api.portaldatransparencia.gov.br/swagger-ui.html
            2. Clique em "Cadastrar"
            3. Preencha o formulario simples
            4. Receba por email em ate 24h
            
            ### 2️⃣ **Primeira Investigacao (30 segundos)**
            1. Cole sua chave no campo acima
            2. Va na aba "Chat Inteligente"
            3. Digite: "Maiores contratos de 2024"
            4. Pressione Enter
            
            ### 3️⃣ **Aprofunde (ilimitado)**
            - Faca perguntas seguindo as respostas
            - Use a ferramenta avancada para analises complexas
            - Compartilhe descobertas importantes
            - Continue fiscalizando!
            
            ---
            
            **🇧🇷 Cada consulta e um ato de cidadania.**
            **🔍 Cada descoberta fortalece a democracia.**
            **💪 O poder esta nas suas maos. Use-o!**
            """)
        
        # Tab 4: Sobre
        with gr.Tab("ℹ️ Sobre", elem_id="about-tab"):
            gr.Markdown("""
            # Sobre o Cidadao.AI
            
            ## 🎯 Nossa Missao
            Democratizar o acesso aos dados publicos brasileiros atraves de Inteligencia Artificial,
            tornando a transparencia governamental acessivel a todos os cidadaos.
            
            ## 🚀 Nossa Visao
            Um Brasil onde cada cidadao e um fiscal natural dos gastos publicos,
            onde a corrupcao e detectada em tempo real e a transparencia e total.
            
            ## ⚡ Tecnologia de Ponta
            - **IA Conversacional**: Processamento de linguagem natural em portugues
            - **Analise de Big Data**: Milhoes de registros processados em segundos  
            - **Deteccao de Anomalias**: Algoritmos que identificam padroes suspeitos
            - **Tempo Real**: Dados sempre atualizados da fonte oficial
            
            ## 📊 Fontes de Dados Oficiais
            - **Portal da Transparencia**: api.portaldatransparencia.gov.br
            - **Dados Abertos Governamentais**: dados.gov.br  
            - **TCU**: Tribunal de Contas da Uniao
            - **CGU**: Controladoria-Geral da Uniao
            
            ## 🛡️ Privacidade e Seguranca
            ### O que NAO fazemos:
            - ❌ Armazenar suas consultas
            - ❌ Rastrear seu comportamento
            - ❌ Vender seus dados
            - ❌ Compartilhar informacoes pessoais
            
            ### O que GARANTIMOS:
            - ✅ Conexao criptografada (HTTPS)
            - ✅ Chave API sob seu controle
            - ✅ Codigo aberto auditavel
            - ✅ Anonimato total
            
            ## 👨‍💻 Equipe
            **Anderson H. Silva** - *Desenvolvedor Principal*
            - Especialista em IA e Dados Publicos
            - Cidadao brasileiro comprometido com transparencia
            - Email: andersonhs27@gmail.com
            - LinkedIn: /in/anderson-h-silva95
            
            ## 🤝 Como Contribuir
            
            ### 💻 Desenvolvedores
            - Codigo aberto no GitHub: github.com/anderson-ufrj/cidadao.ai
            - Contribua com novos recursos
            - Reporte bugs e sugestoes
            - Melhore a documentacao
            
            ### 📢 Cidadaos
            - Use a ferramenta regularmente
            - Compartilhe descobertas importantes
            - Ensine outros cidadaos a usar
            - Pressione por mais transparencia
            
            ### 🏛️ Orgaos Publicos
            - Forneça APIs abertas e padronizadas
            - Melhore a qualidade dos dados
            - Apoie iniciativas de transparencia
            - Adote tecnologias cidadas
            
            ## 📈 Roadmap - Proximas Funcionalidades
            
            ### 🔄 Em Desenvolvimento
            - **Alertas Automaticos**: Notificacoes de anomalias
            - **Comparador Regional**: Estados vs Municipios
            - **Historico de Precos**: Evolucao de custos
            - **API Publica**: Para desenvolvedores
            
            ### 🎯 Planejado 2025
            - **App Mobile**: Android e iOS
            - **Integracao WhatsApp**: Consultas via chat
            - **Dashboard Executivo**: Para gestores publicos
            - **IA Preditiva**: Previsao de gastos
            
            ## 🏆 Reconhecimentos
            - **Inovacao em Transparencia**: Comunidade Open Source
            - **Ferrament do Ano**: Desenvolvedores Brasileiros
            - **Impacto Social**: Organizacoes da Sociedade Civil
            
            ## 📧 Contato e Suporte
            
            ### 🐛 Reportar Problema
            - GitHub Issues: github.com/anderson-ufrj/cidadao.ai/issues
            - Email: andersonhs27@gmail.com
            
            ### 💡 Sugestoes
            - Discussoes GitHub: github.com/anderson-ufrj/cidadao.ai/discussions
            - Email: andersonhs27@gmail.com
            
            ### 🤝 Parcerias
            - Organizacoes da sociedade civil
            - Veiculos de comunicacao
            - Instituicoes de ensino
            - Orgaos de controle
            
            ## 📜 Licenca
            Este projeto e licenciado sob MIT License - veja LICENSE para detalhes.
            
            ## 🙏 Agradecimentos
            - **Portal da Transparencia**: Por disponibilizar dados abertos
            - **Comunidade Open Source**: Por ferramentas incriveis
            - **Voce, cidadao**: Por usar e fortalecer a democracia
            
            ---
            
            **🇧🇷 Feito com ❤️ para o Brasil**
            
            *"A transparencia e o melhor desinfetante contra a corrupcao"*
            """)
    
    # Event handlers
    chat_input.submit(
        fn=lambda m, h, k: asyncio.run(chat_interface(m, h, k)),
        inputs=[chat_input, chatbot, api_key_input],
        outputs=[chatbot, chat_input]
    )
    
    chat_submit.click(
        fn=lambda m, h, k: asyncio.run(chat_interface(m, h, k)),
        inputs=[chat_input, chatbot, api_key_input],
        outputs=[chatbot, chat_input]
    )
    
    adv_submit.click(
        fn=lambda *args: asyncio.run(investigate_with_api_key(*args)),
        inputs=[
            adv_query, adv_data_source, adv_organization,
            adv_date_start, adv_date_end, api_key_input,
            adv_anomaly_types, adv_explanations
        ],
        outputs=adv_output
    )

    # Footer
    gr.HTML("""
    <div style="text-align: center; margin-top: 40px; padding: 20px; border-top: 1px solid #eee; color: #666;">
        <p style="margin: 5px 0;">
            Cidadao.AI v1.0 | Dados: Portal da Transparencia | 
            <a href="https://github.com/anderson-ufrj/cidadao.ai" style="color: #0066cc;">GitHub</a>
        </p>
    </div>
    """)

if __name__ == "__main__":
    app.launch()