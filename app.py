#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Interface da API de Transparência para Hugging Face Spaces
Sistema de consulta segura aos dados do Portal da Transparência
"""

import gradio as gr
import os
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

# Import direto para evitar problemas de path no Hugging Face
import httpx
from pydantic import BaseModel, Field

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração segura das variáveis de ambiente
TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# CSS moderno e profissional
custom_css = """
/* Reset e configurações globais */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.gradio-container {
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Página inicial com background profissional */
.hero-section {
    position: relative;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(
        rgba(0, 0, 0, 0.4),
        rgba(0, 0, 0, 0.6)
    ),
    url('https://upload.wikimedia.org/wikipedia/commons/e/e3/Congresso_Nacional_-_Brasília_-_panorama.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: white;
    text-align: center;
}

.hero-content {
    max-width: 800px;
    padding: 3rem 2rem;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
    animation: fadeInUp 1.2s ease-out;
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
    letter-spacing: -2px;
}

.hero-subtitle {
    font-size: 1.4rem;
    margin-bottom: 1rem;
    opacity: 0.95;
    font-weight: 300;
    line-height: 1.6;
}

.hero-description {
    font-size: 1.1rem;
    margin-bottom: 3rem;
    opacity: 0.9;
    line-height: 1.8;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.hero-buttons {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    margin-bottom: 3rem;
    flex-wrap: wrap;
}

.hero-btn {
    background: linear-gradient(135deg, #1565C0, #1976D2);
    border: none;
    color: white;
    padding: 1rem 2rem;
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    box-shadow: 0 8px 25px rgba(21, 101, 192, 0.4);
    min-width: 200px;
    justify-content: center;
}

.hero-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(21, 101, 192, 0.6);
    background: linear-gradient(135deg, #1976D2, #2196F3);
}

.hero-btn.secondary {
    background: linear-gradient(135deg, #388E3C, #4CAF50);
    box-shadow: 0 8px 25px rgba(56, 142, 60, 0.4);
}

.hero-btn.secondary:hover {
    background: linear-gradient(135deg, #4CAF50, #66BB6A);
    box-shadow: 0 12px 35px rgba(56, 142, 60, 0.6);
}

.hero-footer {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    opacity: 0.8;
}

.hero-footer a {
    color: #FFD700;
    text-decoration: none;
    margin: 0 1rem;
    font-weight: 500;
    transition: color 0.3s ease;
}

.hero-footer a:hover {
    color: #FFFFFF;
}

/* Páginas internas - design limpo */
.internal-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
}

.page-header {
    background: linear-gradient(135deg, #1565C0, #1976D2);
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

/* Cards de resultados */
.result-card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    border-left: 4px solid #0049A0;
}

.error-card {
    background: #ffebee;
    border-left-color: #d32f2f;
}

.success-card {
    background: #e8f5e9;
    border-left-color: #4caf50;
}

/* Tabelas de dados */
.data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
}

.data-table th {
    background: #f5f5f5;
    padding: 0.75rem;
    text-align: left;
    border-bottom: 2px solid #ddd;
    font-weight: 600;
}

.data-table td {
    padding: 0.75rem;
    border-bottom: 1px solid #eee;
}

.data-table tr:hover {
    background: #f9f9f9;
}

/* Botões de filtro */
.filter-button {
    background: #e3f2fd;
    border: 1px solid #2196f3;
    border-radius: 20px;
    padding: 0.5rem 1rem;
    margin: 0.25rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

.filter-button:hover {
    background: #2196f3;
    color: white;
}

/* Status badges */
.status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-size: 0.875rem;
    font-weight: 500;
}

.status-active {
    background: #e8f5e9;
    color: #2e7d32;
}

.status-error {
    background: #ffebee;
    color: #c62828;
}

/* Loading animation */
.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #0049A0;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

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
        font-size: 2.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
    }
    
    .hero-description {
        font-size: 1rem;
    }
    
    .hero-buttons {
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }
    
    .hero-btn {
        width: 80%;
    }
    
    .hero-content {
        margin: 1rem;
        padding: 2rem 1.5rem;
    }
}

@media (max-width: 480px) {
    .hero-section {
        background-attachment: scroll;
    }
    
    .hero-content {
        margin: 0.5rem;
        padding: 1.5rem 1rem;
    }
    
    .hero-footer {
        font-size: 0.9rem;
    }
    
    .hero-footer a {
        display: block;
        margin: 0.5rem 0;
    }
}
"""

class SimplifiedTransparencyAPI:
    """Cliente simplificado para a API do Portal da Transparência"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.portaldatransparencia.gov.br"
        self.header_key = "chave-api-dados"
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def search_contracts(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Buscar contratos"""
        try:
            headers = {
                self.header_key: self.api_key,
                "Content-Type": "application/json"
            }
            
            # Converter filtros para formato da API
            params = {}
            if filters.get("ano"):
                params["ano"] = filters["ano"]
            if filters.get("mes"):
                params["mes"] = filters["mes"]
            if filters.get("orgao"):
                params["codigoOrgao"] = filters["orgao"]
            if filters.get("valor_min"):
                params["valorInicial"] = filters["valor_min"]
            if filters.get("valor_max"):
                params["valorFinal"] = filters["valor_max"]
            
            params["pagina"] = filters.get("pagina", 1)
            params["tamanhoPagina"] = min(filters.get("tamanho", 10), 50)
            
            response = await self.client.get(
                f"{self.base_url}/api-de-dados/contratos",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Erro {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search_expenses(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Buscar despesas"""
        try:
            headers = {
                self.header_key: self.api_key,
                "Content-Type": "application/json"
            }
            
            params = {}
            if filters.get("ano"):
                params["ano"] = filters["ano"]
            if filters.get("mes"):
                params["mes"] = filters["mes"]
            if filters.get("orgao"):
                params["codigoOrgao"] = filters["orgao"]
            
            params["pagina"] = filters.get("pagina", 1)
            params["tamanhoPagina"] = min(filters.get("tamanho", 10), 50)
            
            response = await self.client.get(
                f"{self.base_url}/api-de-dados/despesas",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Erro {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search_biddings(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Buscar licitações"""
        try:
            headers = {
                self.header_key: self.api_key,
                "Content-Type": "application/json"
            }
            
            params = {}
            if filters.get("ano"):
                params["ano"] = filters["ano"]
            if filters.get("orgao"):
                params["codigoOrgao"] = filters["orgao"]
            if filters.get("modalidade"):
                params["modalidade"] = filters["modalidade"]
            
            params["pagina"] = filters.get("pagina", 1)
            params["tamanhoPagina"] = min(filters.get("tamanho", 10), 50)
            
            response = await self.client.get(
                f"{self.base_url}/api-de-dados/licitacoes",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Erro {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

def format_currency(value: float) -> str:
    """Formatar valor em moeda brasileira"""
    try:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def format_date(date_str: str) -> str:
    """Formatar data para padrão brasileiro"""
    try:
        if "T" in date_str:
            date_str = date_str.split("T")[0]
        parts = date_str.split("-")
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    except:
        return date_str

async def search_transparency_data(
    data_type: str,
    year: Optional[int],
    month: Optional[int],
    org_code: str,
    min_value: Optional[float],
    max_value: Optional[float],
    page_size: int
):
    """Buscar dados da API de transparência"""
    
    if not TRANSPARENCY_API_KEY:
        return """
        <div class="result-card error-card">
            <h3>❌ API Key não configurada</h3>
            <p>Para usar a API do Portal da Transparência, configure a variável <code>TRANSPARENCY_API_KEY</code> no ambiente.</p>
            <p><strong>Como obter a chave:</strong></p>
            <ol>
                <li>Acesse <a href="https://portaldatransparencia.gov.br/api-de-dados" target="_blank">Portal da Transparência - API</a></li>
                <li>Faça o cadastro gratuito</li>
                <li>Copie sua chave de API</li>
                <li>Configure como variável de ambiente no Hugging Face Spaces</li>
            </ol>
        </div>
        """
    
    try:
        # Preparar filtros
        filters = {
            "ano": year,
            "mes": month,
            "orgao": org_code if org_code else None,
            "valor_min": min_value,
            "valor_max": max_value,
            "pagina": 1,
            "tamanho": page_size
        }
        
        # Remover None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # Criar cliente da API
        async with SimplifiedTransparencyAPI(TRANSPARENCY_API_KEY) as api:
            # Buscar dados conforme o tipo
            if data_type == "Contratos":
                result = await api.search_contracts(filters)
            elif data_type == "Despesas":
                result = await api.search_expenses(filters)
            elif data_type == "Licitações":
                result = await api.search_biddings(filters)
            else:
                return "<div class='result-card error-card'>❌ Tipo de dados inválido</div>"
        
        if not result["success"]:
            return f"""
            <div class="result-card error-card">
                <h3>❌ Erro na consulta</h3>
                <p>{result['error']}</p>
            </div>
            """
        
        # Processar e formatar resultados
        data = result["data"]
        
        if isinstance(data, list):
            items = data
            total = len(data)
        else:
            items = data.get("data", data.get("items", []))
            total = data.get("meta", {}).get("total", len(items))
        
        if not items:
            return """
            <div class="result-card">
                <h3>📭 Nenhum resultado encontrado</h3>
                <p>Tente ajustar os filtros da sua busca.</p>
            </div>
            """
        
        # Criar HTML com os resultados
        html = f"""
        <div class="result-card success-card">
            <h3>✅ {total} resultados encontrados</h3>
            <p>Mostrando até {len(items)} registros</p>
        </div>
        """
        
        # Formatar conforme o tipo de dados
        if data_type == "Contratos":
            html += format_contracts_table(items)
        elif data_type == "Despesas":
            html += format_expenses_table(items)
        elif data_type == "Licitações":
            html += format_biddings_table(items)
        
        return html
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados: {str(e)}")
        return f"""
        <div class="result-card error-card">
            <h3>❌ Erro inesperado</h3>
            <p>{str(e)}</p>
        </div>
        """

def format_contracts_table(items: List[Dict]) -> str:
    """Formatar tabela de contratos"""
    html = """
    <div class="result-card">
        <h4>📄 Contratos Encontrados</h4>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Número</th>
                    <th>Contratado</th>
                    <th>Objeto</th>
                    <th>Valor</th>
                    <th>Data</th>
                    <th>Órgão</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for item in items[:20]:  # Limitar a 20 itens
        numero = item.get("numero", "N/A")
        contratado = item.get("nomeContratado", item.get("contratado", {}).get("nome", "N/A"))
        objeto = item.get("objeto", "N/A")[:100] + "..."
        valor = format_currency(item.get("valorTotal", item.get("valor", 0)))
        data = format_date(item.get("dataAssinatura", item.get("data", "")))
        orgao = item.get("orgao", {}).get("nome", item.get("nomeOrgao", "N/A"))
        
        html += f"""
        <tr>
            <td>{numero}</td>
            <td>{contratado}</td>
            <td>{objeto}</td>
            <td><strong>{valor}</strong></td>
            <td>{data}</td>
            <td>{orgao}</td>
        </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def format_expenses_table(items: List[Dict]) -> str:
    """Formatar tabela de despesas"""
    html = """
    <div class="result-card">
        <h4>💰 Despesas Encontradas</h4>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Documento</th>
                    <th>Favorecido</th>
                    <th>Descrição</th>
                    <th>Valor</th>
                    <th>Data</th>
                    <th>Órgão</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for item in items[:20]:
        documento = item.get("documento", "N/A")
        favorecido = item.get("nomeFavorecido", item.get("favorecido", {}).get("nome", "N/A"))
        descricao = item.get("descricao", "N/A")[:100] + "..."
        valor = format_currency(item.get("valor", 0))
        data = format_date(item.get("data", item.get("dataDocumento", "")))
        orgao = item.get("orgao", {}).get("nome", item.get("nomeOrgao", "N/A"))
        
        html += f"""
        <tr>
            <td>{documento}</td>
            <td>{favorecido}</td>
            <td>{descricao}</td>
            <td><strong>{valor}</strong></td>
            <td>{data}</td>
            <td>{orgao}</td>
        </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def format_biddings_table(items: List[Dict]) -> str:
    """Formatar tabela de licitações"""
    html = """
    <div class="result-card">
        <h4>🏛️ Licitações Encontradas</h4>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Número</th>
                    <th>Modalidade</th>
                    <th>Objeto</th>
                    <th>Valor Estimado</th>
                    <th>Data</th>
                    <th>Órgão</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for item in items[:20]:
        numero = item.get("numero", "N/A")
        modalidade = item.get("modalidade", {}).get("descricao", item.get("modalidadeDescricao", "N/A"))
        objeto = item.get("objeto", "N/A")[:100] + "..."
        valor = format_currency(item.get("valorEstimado", item.get("valor", 0)))
        data = format_date(item.get("dataPublicacao", item.get("data", "")))
        orgao = item.get("orgao", {}).get("nome", item.get("nomeOrgao", "N/A"))
        
        html += f"""
        <tr>
            <td>{numero}</td>
            <td>{modalidade}</td>
            <td>{objeto}</td>
            <td><strong>{valor}</strong></td>
            <td>{data}</td>
            <td>{orgao}</td>
        </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def analyze_with_ai(data_html: str, query: str) -> str:
    """Analisar dados com IA (se disponível)"""
    if not GROQ_API_KEY:
        return """
        <div class="result-card">
            <h4>🤖 Análise IA não disponível</h4>
            <p>Configure a variável <code>GROQ_API_KEY</code> para habilitar análise com IA.</p>
        </div>
        """
    
    # Aqui você pode implementar a análise com Groq
    # Por enquanto, retorna uma mensagem padrão
    return """
    <div class="result-card">
        <h4>🤖 Análise com IA</h4>
        <p>Funcionalidade em desenvolvimento...</p>
    </div>
    """

def create_transparency_interface():
    """Interface principal do Gradio para API de Transparência"""
    
    with gr.Blocks(css=custom_css, title="Cidadão.AI - Transparência Pública") as app:
        
        # Hero Section - Landing Page
        gr.HTML("""
        <div class="hero-section">
            <div class="hero-content">
                <div class="hero-logo">Cidadão.AI</div>
                <div class="hero-subtitle">Bem-vindo ao Cidadão.AI</div>
                <div class="hero-description">
                    Democratizando o acesso aos dados públicos brasileiros através da inteligência artificial. 
                    Consulte contratos, despesas e licitações do governo federal de forma simples e transparente.
                </div>
                <div class="hero-buttons">
                    <button class="hero-btn" onclick="document.querySelector('[data-testid=\\\"tab-🔍 Consultar Dados\\\"]').click()">
                        🔍 Busca Avançada com IA
                    </button>
                    <button class="hero-btn secondary" onclick="document.querySelector('[data-testid=\\\"tab-🤖 Análise com IA\\\"]').click()">
                        🤖 Converse com nosso Modelo
                    </button>
                </div>
                <div class="hero-footer">
                    <a href="https://github.com/anderson-ufrj/cidadao.ai" target="_blank">📖 Documentação Técnica</a>
                    <a href="https://github.com/anderson-ufrj/cidadao.ai" target="_blank">💻 Repositório GitHub</a>
                    <a href="#credits" onclick="document.querySelector('[data-testid=\\\"tab-📚 Documentação\\\"]').click()">👨‍💻 Créditos</a>
                </div>
            </div>
        </div>
        """)
        
        # Status da API
        api_status = "✅ API Configurada" if TRANSPARENCY_API_KEY else "❌ API não configurada"
        ai_status = "✅ IA Habilitada" if GROQ_API_KEY else "⚠️ IA não configurada"
        
        gr.HTML(f"""
        <div class="result-card">
            <h3>📊 Status do Sistema</h3>
            <p><span class="status-badge {'status-active' if TRANSPARENCY_API_KEY else 'status-error'}">{api_status}</span>
               <span class="status-badge {'status-active' if GROQ_API_KEY else 'status-error'}">{ai_status}</span></p>
        </div>
        """)
        
        with gr.Tabs():
            # Aba de Consulta
            with gr.Tab("🔍 Consultar Dados"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 🎯 Filtros de Busca")
                        
                        data_type = gr.Radio(
                            label="Tipo de Dados",
                            choices=["Contratos", "Despesas", "Licitações"],
                            value="Contratos"
                        )
                        
                        with gr.Row():
                            year = gr.Number(
                                label="Ano",
                                value=2024,
                                precision=0,
                                minimum=2010,
                                maximum=2025
                            )
                            
                            month = gr.Number(
                                label="Mês (opcional)",
                                precision=0,
                                minimum=1,
                                maximum=12
                            )
                        
                        org_code = gr.Textbox(
                            label="Código do Órgão (opcional)",
                            placeholder="Ex: 26000 (MEC)",
                            info="Deixe vazio para buscar todos"
                        )
                        
                        gr.Markdown("**Exemplos de códigos:**")
                        gr.Markdown("""
                        - 26000: Ministério da Educação
                        - 36000: Ministério da Saúde  
                        - 52000: Ministério da Defesa
                        - 20000: Presidência da República
                        """)
                        
                        with gr.Row():
                            min_value = gr.Number(
                                label="Valor Mínimo (R$)",
                                minimum=0
                            )
                            
                            max_value = gr.Number(
                                label="Valor Máximo (R$)",
                                minimum=0
                            )
                        
                        page_size = gr.Slider(
                            label="Quantidade de Resultados",
                            minimum=5,
                            maximum=50,
                            value=10,
                            step=5
                        )
                        
                        search_btn = gr.Button(
                            "🔍 Buscar Dados",
                            variant="primary",
                            scale=2
                        )
                    
                    with gr.Column(scale=2):
                        gr.Markdown("### 📊 Resultados")
                        
                        results_output = gr.HTML(
                            value="""
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
                            """
                        )
                
                # Conectar busca
                search_btn.click(
                    fn=lambda *args: asyncio.run(search_transparency_data(*args)),
                    inputs=[
                        data_type, year, month, org_code,
                        min_value, max_value, page_size
                    ],
                    outputs=[results_output]
                )
            
            # Aba de Análise com IA
            with gr.Tab("🤖 Análise com IA"):
                gr.Markdown("""
                ### 🧠 Análise Inteligente de Dados
                
                Cole os dados obtidos na aba anterior e faça perguntas específicas sobre eles.
                """)
                
                with gr.Row():
                    with gr.Column():
                        data_input = gr.Textbox(
                            label="Dados para Análise",
                            placeholder="Cole aqui os dados da consulta anterior...",
                            lines=10
                        )
                        
                        query_input = gr.Textbox(
                            label="Sua Pergunta",
                            placeholder="Ex: Identifique contratos suspeitos ou valores acima da média",
                            lines=3
                        )
                        
                        analyze_btn = gr.Button("🤖 Analisar com IA", variant="primary")
                    
                    with gr.Column():
                        ai_output = gr.HTML(
                            label="Análise da IA",
                            value="""
                            <div class="result-card">
                                <h4>🤖 Aguardando dados...</h4>
                                <p>Cole os dados e faça uma pergunta para receber análise inteligente.</p>
                            </div>
                            """
                        )
                
                analyze_btn.click(
                    fn=analyze_with_ai,
                    inputs=[data_input, query_input],
                    outputs=[ai_output]
                )
            
            # Aba de Documentação
            with gr.Tab("📚 Documentação"):
                gr.Markdown("""
                ## 📖 Como usar a API de Transparência
                
                ### 🔑 Configuração Inicial
                
                1. **Obtenha sua chave de API**:
                   - Acesse [Portal da Transparência - API](https://portaldatransparencia.gov.br/api-de-dados)
                   - Faça o cadastro gratuito
                   - Copie sua chave de API
                
                2. **Configure no Hugging Face Spaces**:
                   - Vá em Settings → Repository secrets
                   - Adicione `TRANSPARENCY_API_KEY` com sua chave
                   - Reinicie o Space
                
                ### 📊 Tipos de Dados Disponíveis
                
                **Contratos**: Informações sobre contratos firmados pelo governo federal
                - Número do contrato
                - Empresa contratada
                - Objeto do contrato
                - Valor total
                - Data de assinatura
                
                **Despesas**: Gastos e pagamentos realizados
                - Documento de pagamento
                - Favorecido
                - Descrição da despesa
                - Valor pago
                - Data do pagamento
                
                **Licitações**: Processos de compra pública
                - Número da licitação
                - Modalidade (Pregão, Concorrência, etc.)
                - Objeto licitado
                - Valor estimado
                - Data de publicação
                
                ### 🎯 Dicas de Uso
                
                - Use filtros específicos para reduzir o volume de dados
                - Códigos de órgão podem ser encontrados no Portal da Transparência
                - Valores devem ser informados sem pontos ou vírgulas
                - A API tem limite de requisições por minuto
                
                ### 🔗 Links Úteis
                
                - [Portal da Transparência](https://portaldatransparencia.gov.br)
                - [Documentação da API](https://portaldatransparencia.gov.br/api-de-dados)
                - [Código no GitHub](https://github.com/anderson-ufrj/cidadao.ai)
                """)
        
        # Footer
        gr.HTML("""
        <div class="footer-credits">
            <p><strong>🤖 Cidadão.AI</strong> - Democratizando o acesso aos dados públicos</p>
            <p>Desenvolvido por Anderson Henrique da Silva | 🇧🇷 Feito para o Brasil</p>
        </div>
        """)
    
    return app

# Executar aplicação
if __name__ == "__main__":
    logger.info("🚀 Iniciando Cidadão.AI - API de Transparência...")
    
    if TRANSPARENCY_API_KEY:
        logger.info("✅ API do Portal da Transparência configurada")
    else:
        logger.warning("⚠️ API key não configurada - funcionalidade limitada")
    
    app = create_transparency_interface()
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )