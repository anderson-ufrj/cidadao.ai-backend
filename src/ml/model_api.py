"""
API de Deployment para Cidadão.AI

Interface completa para servir o modelo especializado em transparência pública.
Similar ao padrão Kimi K2, mas otimizado para análise governamental brasileira.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Generator
import asyncio
import torch
import json
import logging
from pathlib import Path
from datetime import datetime
import uvicorn
from contextlib import asynccontextmanager
import tempfile
import pandas as pd
from io import StringIO

from .cidadao_model import CidadaoAIForTransparency, create_cidadao_model
from .training_pipeline import TransparencyDataset
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)


# === MODELOS DE REQUEST/RESPONSE ===

class TransparencyAnalysisRequest(BaseModel):
    """Request para análise de transparência"""
    
    text: str = Field(..., description="Texto para análise (contrato, despesa, etc.)")
    analysis_type: str = Field(
        default="complete",
        description="Tipo de análise: 'anomaly', 'financial', 'legal', 'complete'"
    )
    include_explanation: bool = Field(
        default=True,
        description="Incluir explicação detalhada dos resultados"
    )
    confidence_threshold: float = Field(
        default=0.7,
        description="Limiar de confiança para alertas",
        ge=0.0,
        le=1.0
    )


class BatchAnalysisRequest(BaseModel):
    """Request para análise em lote"""
    
    texts: List[str] = Field(..., description="Lista de textos para análise")
    analysis_type: str = Field(default="complete")
    include_explanation: bool = Field(default=True)
    format: str = Field(default="json", description="Formato de saída: 'json' ou 'csv'")


class ChatRequest(BaseModel):
    """Request para chat com Cidadão.AI"""
    
    messages: List[Dict[str, str]] = Field(..., description="Histórico de mensagens")
    temperature: float = Field(default=0.6, ge=0.0, le=2.0)
    max_tokens: int = Field(default=512, ge=1, le=2048)
    stream: bool = Field(default=False, description="Usar streaming de resposta")
    tools: Optional[List[Dict]] = Field(default=None, description="Ferramentas disponíveis")


class TransparencyAnalysisResponse(BaseModel):
    """Response da análise de transparência"""
    
    analysis_id: str = Field(..., description="ID único da análise")
    text: str = Field(..., description="Texto analisado")
    timestamp: str = Field(..., description="Timestamp da análise")
    
    # Resultados de anomalia
    anomaly_detection: Optional[Dict] = Field(None, description="Resultados de detecção de anomalias")
    
    # Resultados financeiros
    financial_analysis: Optional[Dict] = Field(None, description="Análise de risco financeiro")
    
    # Resultados legais
    legal_compliance: Optional[Dict] = Field(None, description="Verificação de conformidade legal")
    
    # Resumo executivo
    executive_summary: Dict = Field(..., description="Resumo executivo da análise")
    
    # Recomendações
    recommendations: List[str] = Field(..., description="Recomendações baseadas na análise")
    
    # Metadados
    confidence: float = Field(..., description="Confiança geral da análise")
    processing_time: float = Field(..., description="Tempo de processamento em segundos")


class ChatResponse(BaseModel):
    """Response do chat"""
    
    message: str = Field(..., description="Resposta do assistente")
    tools_used: Optional[List[str]] = Field(None, description="Ferramentas utilizadas")
    confidence: float = Field(..., description="Confiança da resposta")
    sources: Optional[List[str]] = Field(None, description="Fontes consultadas")


class ModelInfoResponse(BaseModel):
    """Informações do modelo"""
    
    model_name: str = Field(..., description="Nome do modelo")
    version: str = Field(..., description="Versão do modelo")
    specialization: List[str] = Field(..., description="Tarefas especializadas")
    total_parameters: int = Field(..., description="Número total de parâmetros")
    training_data: Dict = Field(..., description="Informações sobre dados de treinamento")
    performance_metrics: Dict = Field(..., description="Métricas de performance")


# === GERENCIADOR DE MODELO ===

class CidadaoAIManager:
    """Gerenciador do modelo Cidadão.AI"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model: Optional[CidadaoAIForTransparency] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.loaded = False
        
        # Estatísticas de uso
        self.usage_stats = {
            "total_requests": 0,
            "anomaly_detections": 0,
            "financial_analyses": 0,
            "legal_checks": 0,
            "chat_requests": 0,
            "average_processing_time": 0.0
        }

    async def load_model(self):
        """Carregar modelo"""
        try:
            logger.info("🤖 Carregando Cidadão.AI...")
            
            if self.model_path and Path(self.model_path).exists():
                # Carregar modelo treinado
                self.model = CidadaoAIForTransparency.load_model(self.model_path)
                logger.info(f"✅ Modelo carregado de {self.model_path}")
            else:
                # Carregar modelo base
                self.model = create_cidadao_model(
                    specialized_tasks=["all"],
                    model_size="medium"
                )
                logger.info("✅ Modelo base criado")
            
            # Carregar tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Mover para device
            self.model.to(self.device)
            self.model.eval()
            
            self.loaded = True
            logger.info(f"🎯 Modelo pronto no device: {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo: {e}")
            raise

    async def analyze_transparency(
        self, 
        request: TransparencyAnalysisRequest
    ) -> TransparencyAnalysisResponse:
        """Executar análise de transparência"""
        
        if not self.loaded:
            raise HTTPException(status_code=503, detail="Modelo não carregado")
        
        start_time = datetime.now()
        
        try:
            # Tokenizar texto
            inputs = self.tokenizer(
                request.text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            ).to(self.device)
            
            # Executar análises baseadas no tipo solicitado
            results = {}
            
            if request.analysis_type in ["anomaly", "complete"]:
                anomaly_results = self.model.detect_anomalies(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"]
                )
                results["anomaly_detection"] = anomaly_results
            
            if request.analysis_type in ["financial", "complete"]:
                financial_results = self.model.analyze_financial_risk(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"]
                )
                results["financial_analysis"] = financial_results
            
            if request.analysis_type in ["legal", "complete"]:
                legal_results = self.model.check_legal_compliance(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"]
                )
                results["legal_compliance"] = legal_results
            
            # Gerar resumo executivo e recomendações
            executive_summary, recommendations, overall_confidence = self._generate_summary(
                results, request.confidence_threshold
            )
            
            # Calcular tempo de processamento
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Atualizar estatísticas
            self.usage_stats["total_requests"] += 1
            if "anomaly_detection" in results:
                self.usage_stats["anomaly_detections"] += 1
            if "financial_analysis" in results:
                self.usage_stats["financial_analyses"] += 1
            if "legal_compliance" in results:
                self.usage_stats["legal_checks"] += 1
            
            # Atualizar tempo médio
            current_avg = self.usage_stats["average_processing_time"]
            total_requests = self.usage_stats["total_requests"]
            self.usage_stats["average_processing_time"] = (
                (current_avg * (total_requests - 1) + processing_time) / total_requests
            )
            
            # Construir response
            response = TransparencyAnalysisResponse(
                analysis_id=f"cidadao_{int(start_time.timestamp())}",
                text=request.text,
                timestamp=start_time.isoformat(),
                anomaly_detection=results.get("anomaly_detection"),
                financial_analysis=results.get("financial_analysis"),
                legal_compliance=results.get("legal_compliance"),
                executive_summary=executive_summary,
                recommendations=recommendations,
                confidence=overall_confidence,
                processing_time=processing_time
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
            raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

    async def batch_analyze(
        self, 
        request: BatchAnalysisRequest
    ) -> Union[List[TransparencyAnalysisResponse], str]:
        """Análise em lote"""
        
        results = []
        
        for text in request.texts:
            analysis_request = TransparencyAnalysisRequest(
                text=text,
                analysis_type=request.analysis_type,
                include_explanation=request.include_explanation
            )
            
            result = await self.analyze_transparency(analysis_request)
            results.append(result)
        
        if request.format == "csv":
            return self._convert_to_csv(results)
        
        return results

    async def chat_completion(self, request: ChatRequest) -> Union[ChatResponse, Generator]:
        """Completação de chat"""
        
        if not self.loaded:
            raise HTTPException(status_code=503, detail="Modelo não carregado")
        
        self.usage_stats["chat_requests"] += 1
        
        try:
            # Extrair última mensagem do usuário
            user_message = request.messages[-1]["content"]
            
            # Detectar se é uma pergunta sobre transparência
            transparency_keywords = [
                "contrato", "licitação", "despesa", "gasto", "anomalia",
                "suspeito", "irregular", "transparência", "corrupção"
            ]
            
            is_transparency_query = any(
                keyword in user_message.lower() 
                for keyword in transparency_keywords
            )
            
            if is_transparency_query:
                # Usar análise especializada
                analysis_request = TransparencyAnalysisRequest(
                    text=user_message,
                    analysis_type="complete"
                )
                
                analysis_result = await self.analyze_transparency(analysis_request)
                
                # Gerar resposta em linguagem natural
                response_message = self._format_analysis_for_chat(analysis_result)
                
                return ChatResponse(
                    message=response_message,
                    tools_used=["transparency_analysis"],
                    confidence=analysis_result.confidence,
                    sources=["Portal da Transparência", "Cidadão.AI Analysis"]
                )
            else:
                # Resposta geral do chatbot
                response_message = self._generate_general_response(user_message)
                
                return ChatResponse(
                    message=response_message,
                    tools_used=None,
                    confidence=0.8,
                    sources=None
                )
                
        except Exception as e:
            logger.error(f"❌ Erro no chat: {e}")
            raise HTTPException(status_code=500, detail=f"Erro no chat: {str(e)}")

    def _generate_summary(
        self, 
        results: Dict, 
        confidence_threshold: float
    ) -> Tuple[Dict, List[str], float]:
        """Gerar resumo executivo e recomendações"""
        
        summary = {
            "overall_risk": "Baixo",
            "main_findings": [],
            "alert_level": "Verde"
        }
        
        recommendations = []
        confidences = []
        
        # Análise de anomalias
        if "anomaly_detection" in results:
            anomaly_data = results["anomaly_detection"]
            anomalous_count = anomaly_data["summary"]["anomalous_count"]
            
            if anomalous_count > 0:
                summary["main_findings"].append(f"{anomalous_count} anomalias detectadas")
                summary["alert_level"] = "Vermelho"
                summary["overall_risk"] = "Alto"
                recommendations.append("🚨 Investigação imediata necessária devido a anomalias detectadas")
            
            # Coletar confiança média
            high_conf_count = anomaly_data["summary"]["high_confidence_count"]
            total_samples = anomaly_data["summary"]["total_samples"]
            if total_samples > 0:
                confidences.append(high_conf_count / total_samples)
        
        # Análise financeira
        if "financial_analysis" in results:
            financial_data = results["financial_analysis"]
            high_risk_count = financial_data["summary"]["high_risk_count"]
            avg_value = financial_data["summary"]["average_estimated_value"]
            
            if high_risk_count > 0:
                summary["main_findings"].append(f"{high_risk_count} contratos de alto risco financeiro")
                if summary["overall_risk"] == "Baixo":
                    summary["overall_risk"] = "Médio"
                    summary["alert_level"] = "Amarelo"
                recommendations.append("⚠️ Revisão financeira recomendada para contratos de alto risco")
            
            if avg_value > 10000000:  # > 10M
                summary["main_findings"].append(f"Valor médio elevado: R$ {avg_value:,.2f}")
        
        # Análise legal
        if "legal_compliance" in results:
            legal_data = results["legal_compliance"]
            compliance_rate = legal_data["summary"]["compliance_rate"]
            
            if compliance_rate < 0.8:
                summary["main_findings"].append(f"Taxa de conformidade baixa: {compliance_rate:.1%}")
                recommendations.append("📋 Revisão de processos de compliance necessária")
        
        # Calcular confiança geral
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.7
        
        # Recomendações padrão
        if not recommendations:
            recommendations.append("✅ Análise não identificou problemas críticos")
        
        return summary, recommendations, overall_confidence

    def _format_analysis_for_chat(self, analysis: TransparencyAnalysisResponse) -> str:
        """Formatar análise para resposta de chat"""
        
        response_parts = []
        
        # Resumo executivo
        summary = analysis.executive_summary
        response_parts.append(f"📊 **Análise de Transparência**")
        response_parts.append(f"🎯 **Nível de Risco**: {summary['overall_risk']}")
        response_parts.append(f"🚨 **Alerta**: {summary['alert_level']}")
        
        # Principais descobertas
        if summary["main_findings"]:
            response_parts.append("\n🔍 **Principais Descobertas**:")
            for finding in summary["main_findings"]:
                response_parts.append(f"• {finding}")
        
        # Recomendações
        response_parts.append("\n💡 **Recomendações**:")
        for rec in analysis.recommendations:
            response_parts.append(f"• {rec}")
        
        # Detalhes técnicos
        if analysis.anomaly_detection:
            anomaly_count = analysis.anomaly_detection["summary"]["anomalous_count"]
            if anomaly_count > 0:
                response_parts.append(f"\n⚠️ **Anomalias Detectadas**: {anomaly_count}")
        
        if analysis.financial_analysis:
            high_risk = analysis.financial_analysis["summary"]["high_risk_count"]
            if high_risk > 0:
                response_parts.append(f"💰 **Contratos Alto Risco**: {high_risk}")
        
        # Confiança
        response_parts.append(f"\n📈 **Confiança da Análise**: {analysis.confidence:.1%}")
        
        return "\n".join(response_parts)

    def _generate_general_response(self, message: str) -> str:
        """Gerar resposta geral do chatbot"""
        
        # Respostas baseadas em palavras-chave
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["olá", "oi", "bom dia", "boa tarde"]):
            return ("Olá! Sou o Cidadão.AI, seu assistente de IA especializado em transparência pública brasileira. "
                   "Posso ajudar você a analisar contratos, detectar anomalias e verificar conformidade legal. "
                   "Como posso ajudá-lo hoje?")
        
        elif any(word in message_lower for word in ["ajuda", "help", "como"]):
            return ("🤖 **Cidadão.AI - Suas Funcionalidades**\n\n"
                   "• 🔍 **Análise de Anomalias**: Detectar padrões suspeitos em contratos\n"
                   "• 💰 **Análise Financeira**: Avaliar riscos em gastos públicos\n"
                   "• ⚖️ **Conformidade Legal**: Verificar adequação às normas\n"
                   "• 📊 **Relatórios**: Gerar análises detalhadas\n\n"
                   "Compartilhe um texto de contrato ou despesa pública para análise!")
        
        elif any(word in message_lower for word in ["obrigado", "obrigada", "valeu"]):
            return ("Fico feliz em ajudar! 😊 A transparência pública é fundamental para a democracia. "
                   "Se precisar de mais análises, estarei aqui!")
        
        else:
            return ("Entendo que você tem uma pergunta. Como sou especializado em análise de transparência pública, "
                   "funciono melhor quando você compartilha textos de contratos, licitações ou despesas para análise. "
                   "Você poderia reformular sua pergunta incluindo dados de transparência?")

    def _convert_to_csv(self, results: List[TransparencyAnalysisResponse]) -> str:
        """Converter resultados para CSV"""
        
        rows = []
        
        for result in results:
            row = {
                "analysis_id": result.analysis_id,
                "timestamp": result.timestamp,
                "text_preview": result.text[:100] + "..." if len(result.text) > 100 else result.text,
                "overall_risk": result.executive_summary["overall_risk"],
                "alert_level": result.executive_summary["alert_level"],
                "confidence": result.confidence,
                "processing_time": result.processing_time
            }
            
            # Adicionar detalhes de anomalia
            if result.anomaly_detection:
                row["anomalous_count"] = result.anomaly_detection["summary"]["anomalous_count"]
            
            # Adicionar detalhes financeiros
            if result.financial_analysis:
                row["high_risk_count"] = result.financial_analysis["summary"]["high_risk_count"]
                row["avg_estimated_value"] = result.financial_analysis["summary"]["average_estimated_value"]
            
            # Adicionar conformidade legal
            if result.legal_compliance:
                row["compliance_rate"] = result.legal_compliance["summary"]["compliance_rate"]
            
            rows.append(row)
        
        # Converter para CSV
        df = pd.DataFrame(rows)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        
        return csv_buffer.getvalue()

    def get_model_info(self) -> ModelInfoResponse:
        """Obter informações do modelo"""
        
        if not self.loaded:
            raise HTTPException(status_code=503, detail="Modelo não carregado")
        
        # Contar parâmetros
        total_params = sum(p.numel() for p in self.model.parameters())
        
        return ModelInfoResponse(
            model_name="Cidadão.AI",
            version="1.0.0",
            specialization=["anomaly_detection", "financial_analysis", "legal_compliance"],
            total_parameters=total_params,
            training_data={
                "source": "Portal da Transparência + Dados Sintéticos",
                "languages": ["pt-BR"],
                "domains": ["contratos_públicos", "licitações", "despesas_governo"]
            },
            performance_metrics=self.usage_stats
        )


# === APLICAÇÃO FASTAPI ===

# Instância global do gerenciador
model_manager = CidadaoAIManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    # Startup
    await model_manager.load_model()
    yield
    # Shutdown
    pass

# Criar aplicação FastAPI
app = FastAPI(
    title="Cidadão.AI API",
    description="API de IA especializada em análise de transparência pública brasileira",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === ENDPOINTS ===

@app.get("/", summary="Informações da API")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "name": "Cidadão.AI API",
        "version": "1.0.0",
        "description": "API de IA especializada em transparência pública brasileira",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", summary="Health Check")
async def health_check():
    """Verificar saúde da API"""
    return {
        "status": "healthy" if model_manager.loaded else "loading",
        "model_loaded": model_manager.loaded,
        "device": str(model_manager.device),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/model/info", response_model=ModelInfoResponse, summary="Informações do Modelo")
async def get_model_info():
    """Obter informações detalhadas do modelo"""
    return model_manager.get_model_info()

@app.post("/analyze", response_model=TransparencyAnalysisResponse, summary="Análise de Transparência")
async def analyze_transparency(request: TransparencyAnalysisRequest):
    """
    Analisar texto para detectar anomalias, riscos financeiros e conformidade legal
    
    - **text**: Texto do contrato, despesa ou licitação para análise
    - **analysis_type**: Tipo de análise (anomaly, financial, legal, complete)
    - **include_explanation**: Incluir explicações detalhadas
    - **confidence_threshold**: Limiar de confiança para alertas
    """
    return await model_manager.analyze_transparency(request)

@app.post("/analyze/batch", summary="Análise em Lote")
async def batch_analyze(request: BatchAnalysisRequest):
    """
    Analisar múltiplos textos em lote
    
    - **texts**: Lista de textos para análise
    - **analysis_type**: Tipo de análise
    - **format**: Formato de saída (json ou csv)
    """
    results = await model_manager.batch_analyze(request)
    
    if request.format == "csv":
        return StreamingResponse(
            iter([results]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=cidadao_analysis.csv"}
        )
    
    return results

@app.post("/chat", response_model=ChatResponse, summary="Chat com Cidadão.AI")
async def chat_completion(request: ChatRequest):
    """
    Conversar com o Cidadão.AI sobre transparência pública
    
    - **messages**: Histórico de mensagens
    - **temperature**: Criatividade da resposta
    - **max_tokens**: Tamanho máximo da resposta
    """
    return await model_manager.chat_completion(request)

@app.post("/upload", summary="Upload de Arquivo para Análise")
async def upload_file(file: UploadFile = File(...)):
    """
    Fazer upload de arquivo (CSV, TXT, JSON) para análise em lote
    """
    
    if not file.filename.endswith(('.csv', '.txt', '.json')):
        raise HTTPException(
            status_code=400, 
            detail="Formato não suportado. Use CSV, TXT ou JSON."
        )
    
    try:
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            # Processar CSV
            df = pd.read_csv(StringIO(content.decode('utf-8')))
            texts = df.iloc[:, 0].tolist()  # Primeira coluna
            
        elif file.filename.endswith('.txt'):
            # Processar TXT (uma linha por texto)
            texts = content.decode('utf-8').strip().split('\n')
            
        elif file.filename.endswith('.json'):
            # Processar JSON
            data = json.loads(content.decode('utf-8'))
            if isinstance(data, list):
                texts = [str(item) for item in data]
            else:
                texts = [str(data)]
        
        # Limitar a 100 textos para evitar sobrecarga
        texts = texts[:100]
        
        # Executar análise em lote
        batch_request = BatchAnalysisRequest(
            texts=texts,
            analysis_type="complete",
            format="json"
        )
        
        results = await model_manager.batch_analyze(batch_request)
        
        return {
            "filename": file.filename,
            "processed_count": len(texts),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

@app.get("/stats", summary="Estatísticas de Uso")
async def get_usage_stats():
    """Obter estatísticas de uso da API"""
    return model_manager.usage_stats

@app.get("/examples", summary="Exemplos de Uso")
async def get_examples():
    """Obter exemplos de uso da API"""
    
    return {
        "transparency_analysis": {
            "description": "Análise completa de transparência",
            "example": {
                "text": "Contrato para aquisição de equipamentos médicos no valor de R$ 2.500.000,00 firmado entre Ministério da Saúde e Empresa XYZ LTDA via dispensa de licitação.",
                "analysis_type": "complete",
                "include_explanation": True
            }
        },
        "anomaly_detection": {
            "description": "Detectar apenas anomalias",
            "example": {
                "text": "Contrato emergencial sem licitação para fornecimento de insumos hospitalares. Valor: R$ 15.000.000,00. Empresa com CNPJ irregular.",
                "analysis_type": "anomaly"
            }
        },
        "chat": {
            "description": "Conversar sobre transparência",
            "example": {
                "messages": [
                    {"role": "user", "content": "Analise este contrato: Aquisição de medicamentos por R$ 5 milhões sem licitação."}
                ]
            }
        }
    }


# === EXECUÇÃO ===

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Executar servidor
    uvicorn.run(
        "src.ml.model_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )