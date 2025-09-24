"""
Cidadão.AI - Hugging Face Transformers Integration

Modelo especializado em transparência pública brasileira
compatível com a biblioteca transformers do Hugging Face.
"""

import torch
import torch.nn as nn
from transformers import (
    PreTrainedModel, PretrainedConfig,
    AutoModel, AutoTokenizer,
    pipeline, Pipeline
)
from transformers.modeling_outputs import SequenceClassifierOutput, BaseModelOutput
from typing import Optional, Dict, List, Union, Tuple
from src.core import json_utils
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CidadaoAIConfig(PretrainedConfig):
    """
    Configuração do Cidadão.AI para Hugging Face
    """
    
    model_type = "cidadao-gpt"
    
    def __init__(
        self,
        vocab_size: int = 50257,
        hidden_size: int = 1024,
        num_hidden_layers: int = 24,
        num_attention_heads: int = 16,
        intermediate_size: int = 4096,
        max_position_embeddings: int = 8192,
        
        # Configurações específicas de transparência
        transparency_vocab_size: int = 2048,
        corruption_detection_layers: int = 4,
        financial_analysis_dim: int = 512,
        legal_understanding_dim: int = 256,
        
        # Configurações de dropout
        hidden_dropout_prob: float = 0.1,
        attention_probs_dropout_prob: float = 0.1,
        
        # Configurações de ativação
        hidden_act: str = "gelu",
        
        # Configurações de inicialização
        initializer_range: float = 0.02,
        layer_norm_eps: float = 1e-12,
        
        # Tarefas especializadas
        enable_anomaly_detection: bool = True,
        enable_financial_analysis: bool = True,
        enable_legal_reasoning: bool = True,
        
        # Labels para classificação
        num_anomaly_labels: int = 3,  # Normal, Suspeito, Anômalo
        num_financial_labels: int = 5,  # Muito Baixo, Baixo, Médio, Alto, Muito Alto
        num_legal_labels: int = 2,   # Não Conforme, Conforme
        
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.max_position_embeddings = max_position_embeddings
        
        # Configurações específicas
        self.transparency_vocab_size = transparency_vocab_size
        self.corruption_detection_layers = corruption_detection_layers
        self.financial_analysis_dim = financial_analysis_dim
        self.legal_understanding_dim = legal_understanding_dim
        
        # Dropout
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        
        # Ativação
        self.hidden_act = hidden_act
        
        # Inicialização
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        
        # Tarefas
        self.enable_anomaly_detection = enable_anomaly_detection
        self.enable_financial_analysis = enable_financial_analysis
        self.enable_legal_reasoning = enable_legal_reasoning
        
        # Labels
        self.num_anomaly_labels = num_anomaly_labels
        self.num_financial_labels = num_financial_labels
        self.num_legal_labels = num_legal_labels


class CidadaoAIModel(PreTrainedModel):
    """
    Modelo base Cidadão.AI compatível com Hugging Face
    """
    
    config_class = CidadaoAIConfig
    base_model_prefix = "cidadao_gpt"
    supports_gradient_checkpointing = True
    
    def __init__(self, config: CidadaoAIConfig):
        super().__init__(config)
        
        self.config = config
        
        # Modelo base (usar GPT-2 como backbone)
        from transformers import GPT2Model
        self.backbone = GPT2Model(config)
        
        # Embeddings especializados para transparência
        self.transparency_embeddings = nn.ModuleDict({
            'entity_types': nn.Embedding(100, config.hidden_size // 4),
            'financial_types': nn.Embedding(50, config.hidden_size // 4),
            'legal_types': nn.Embedding(200, config.hidden_size // 4),
            'corruption_indicators': nn.Embedding(20, config.hidden_size // 4)
        })
        
        # Cabeças de classificação especializadas
        if config.enable_anomaly_detection:
            self.anomaly_classifier = nn.Sequential(
                nn.Linear(config.hidden_size, config.hidden_size // 2),
                nn.ReLU(),
                nn.Dropout(config.hidden_dropout_prob),
                nn.Linear(config.hidden_size // 2, config.num_anomaly_labels)
            )
            
            self.anomaly_confidence = nn.Sequential(
                nn.Linear(config.hidden_size, config.hidden_size // 4),
                nn.ReLU(),
                nn.Linear(config.hidden_size // 4, 1),
                nn.Sigmoid()
            )
        
        if config.enable_financial_analysis:
            self.financial_classifier = nn.Sequential(
                nn.Linear(config.hidden_size, config.financial_analysis_dim),
                nn.ReLU(),
                nn.Dropout(config.hidden_dropout_prob),
                nn.Linear(config.financial_analysis_dim, config.num_financial_labels)
            )
            
            self.financial_regressor = nn.Sequential(
                nn.Linear(config.hidden_size, config.financial_analysis_dim),
                nn.ReLU(),
                nn.Linear(config.financial_analysis_dim, 1)
            )
        
        if config.enable_legal_reasoning:
            self.legal_classifier = nn.Sequential(
                nn.Linear(config.hidden_size, config.legal_understanding_dim),
                nn.ReLU(),
                nn.Dropout(config.hidden_dropout_prob),
                nn.Linear(config.legal_understanding_dim, config.num_legal_labels)
            )
        
        # Inicializar pesos
        self.init_weights()
    
    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        
        # Inputs especializados
        entity_types: Optional[torch.Tensor] = None,
        financial_types: Optional[torch.Tensor] = None,
        legal_types: Optional[torch.Tensor] = None,
        corruption_indicators: Optional[torch.Tensor] = None,
        
        # Labels para treinamento
        anomaly_labels: Optional[torch.Tensor] = None,
        financial_labels: Optional[torch.Tensor] = None,
        legal_labels: Optional[torch.Tensor] = None,
    ) -> Union[Tuple, BaseModelOutput]:
        
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        
        # Forward do modelo base
        outputs = self.backbone(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        
        sequence_output = outputs[0]  # [batch_size, seq_len, hidden_size]
        
        # Pooling para classificação (usar [CLS] token ou média)
        pooled_output = sequence_output.mean(dim=1)  # [batch_size, hidden_size]
        
        # Adicionar embeddings especializados se fornecidos
        if entity_types is not None:
            entity_embeds = self.transparency_embeddings['entity_types'](entity_types)
            pooled_output = pooled_output + entity_embeds.mean(dim=1)
        
        if corruption_indicators is not None:
            corruption_embeds = self.transparency_embeddings['corruption_indicators'](corruption_indicators)
            pooled_output = pooled_output + corruption_embeds.mean(dim=1)
        
        result = {
            "last_hidden_state": sequence_output,
            "pooler_output": pooled_output,
            "hidden_states": outputs.hidden_states if output_hidden_states else None,
            "attentions": outputs.attentions if output_attentions else None,
        }
        
        # Adicionar predições das cabeças especializadas
        if hasattr(self, 'anomaly_classifier'):
            anomaly_logits = self.anomaly_classifier(pooled_output)
            anomaly_confidence = self.anomaly_confidence(pooled_output)
            result["anomaly_logits"] = anomaly_logits
            result["anomaly_confidence"] = anomaly_confidence
            
            # Calcular loss se labels fornecidos
            if anomaly_labels is not None:
                loss_fct = nn.CrossEntropyLoss()
                anomaly_loss = loss_fct(anomaly_logits, anomaly_labels)
                result["anomaly_loss"] = anomaly_loss
        
        if hasattr(self, 'financial_classifier'):
            financial_logits = self.financial_classifier(pooled_output)
            financial_value = self.financial_regressor(pooled_output)
            result["financial_logits"] = financial_logits
            result["financial_value"] = financial_value
            
            if financial_labels is not None:
                loss_fct = nn.CrossEntropyLoss()
                financial_loss = loss_fct(financial_logits, financial_labels)
                result["financial_loss"] = financial_loss
        
        if hasattr(self, 'legal_classifier'):
            legal_logits = self.legal_classifier(pooled_output)
            result["legal_logits"] = legal_logits
            
            if legal_labels is not None:
                loss_fct = nn.CrossEntropyLoss()
                legal_loss = loss_fct(legal_logits, legal_labels)
                result["legal_loss"] = legal_loss
        
        # Calcular loss total se em modo de treinamento
        if any(key.endswith('_loss') for key in result.keys()):
            total_loss = 0
            loss_count = 0
            
            for key, value in result.items():
                if key.endswith('_loss'):
                    total_loss += value
                    loss_count += 1
            
            if loss_count > 0:
                result["loss"] = total_loss / loss_count
        
        if not return_dict:
            return tuple(v for v in result.values() if v is not None)
        
        return BaseModelOutput(**result)


class CidadaoAIForAnomalyDetection(PreTrainedModel):
    """Modelo Cidadão.AI especializado para detecção de anomalias"""
    
    config_class = CidadaoAIConfig
    
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_anomaly_labels
        self.cidadao_gpt = CidadaoAIModel(config)
        
    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        labels=None,
        **kwargs
    ):
        outputs = self.cidadao_gpt(
            input_ids=input_ids,
            attention_mask=attention_mask,
            anomaly_labels=labels,
            **kwargs
        )
        
        logits = outputs.get("anomaly_logits")
        confidence = outputs.get("anomaly_confidence")
        loss = outputs.get("anomaly_loss")
        
        return SequenceClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.get("hidden_states"),
            attentions=outputs.get("attentions"),
        )


class CidadaoAIForFinancialAnalysis(PreTrainedModel):
    """Modelo Cidadão.AI especializado para análise financeira"""
    
    config_class = CidadaoAIConfig
    
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_financial_labels
        self.cidadao_gpt = CidadaoAIModel(config)
        
    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        labels=None,
        **kwargs
    ):
        outputs = self.cidadao_gpt(
            input_ids=input_ids,
            attention_mask=attention_mask,
            financial_labels=labels,
            **kwargs
        )
        
        logits = outputs.get("financial_logits")
        value = outputs.get("financial_value")
        loss = outputs.get("financial_loss")
        
        return SequenceClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.get("hidden_states"),
            attentions=outputs.get("attentions"),
        )


class CidadaoAIForLegalCompliance(PreTrainedModel):
    """Modelo Cidadão.AI especializado para conformidade legal"""
    
    config_class = CidadaoAIConfig
    
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_legal_labels
        self.cidadao_gpt = CidadaoAIModel(config)
        
    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        labels=None,
        **kwargs
    ):
        outputs = self.cidadao_gpt(
            input_ids=input_ids,
            attention_mask=attention_mask,
            legal_labels=labels,
            **kwargs
        )
        
        logits = outputs.get("legal_logits")
        loss = outputs.get("legal_loss")
        
        return SequenceClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.get("hidden_states"),
            attentions=outputs.get("attentions"),
        )


# Pipelines personalizados para cada tarefa

class TransparencyAnalysisPipeline(Pipeline):
    """Pipeline personalizado para análise de transparência"""
    
    def __init__(self, model, tokenizer, task="transparency-analysis", **kwargs):
        super().__init__(model=model, tokenizer=tokenizer, task=task, **kwargs)
        
        self.anomaly_labels = ["Normal", "Suspeito", "Anômalo"]
        self.financial_labels = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
        self.legal_labels = ["Não Conforme", "Conforme"]
    
    def _sanitize_parameters(self, **kwargs):
        preprocess_kwargs = {}
        forward_kwargs = {}
        postprocess_kwargs = {}
        
        if "max_length" in kwargs:
            preprocess_kwargs["max_length"] = kwargs["max_length"]
        
        if "return_all_scores" in kwargs:
            postprocess_kwargs["return_all_scores"] = kwargs["return_all_scores"]
            
        return preprocess_kwargs, forward_kwargs, postprocess_kwargs
    
    def preprocess(self, inputs, max_length=512):
        return self.tokenizer(
            inputs,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt"
        )
    
    def _forward(self, model_inputs):
        return self.model(**model_inputs)
    
    def postprocess(self, model_outputs, return_all_scores=False):
        results = {}
        
        # Detecção de anomalias
        if hasattr(model_outputs, 'anomaly_logits') or 'anomaly_logits' in model_outputs:
            anomaly_logits = model_outputs.get('anomaly_logits', model_outputs.anomaly_logits)
            anomaly_probs = torch.softmax(anomaly_logits, dim=-1)
            anomaly_pred = torch.argmax(anomaly_probs, dim=-1)
            
            results["anomaly"] = {
                "label": self.anomaly_labels[anomaly_pred.item()],
                "score": anomaly_probs.max().item(),
                "all_scores": [
                    {"label": label, "score": score.item()}
                    for label, score in zip(self.anomaly_labels, anomaly_probs[0])
                ] if return_all_scores else None
            }
        
        # Análise financeira
        if hasattr(model_outputs, 'financial_logits') or 'financial_logits' in model_outputs:
            financial_logits = model_outputs.get('financial_logits', model_outputs.financial_logits)
            financial_probs = torch.softmax(financial_logits, dim=-1)
            financial_pred = torch.argmax(financial_probs, dim=-1)
            
            results["financial"] = {
                "label": self.financial_labels[financial_pred.item()],
                "score": financial_probs.max().item(),
                "all_scores": [
                    {"label": label, "score": score.item()}
                    for label, score in zip(self.financial_labels, financial_probs[0])
                ] if return_all_scores else None
            }
        
        # Conformidade legal
        if hasattr(model_outputs, 'legal_logits') or 'legal_logits' in model_outputs:
            legal_logits = model_outputs.get('legal_logits', model_outputs.legal_logits)
            legal_probs = torch.softmax(legal_logits, dim=-1)
            legal_pred = torch.argmax(legal_probs, dim=-1)
            
            results["legal"] = {
                "label": self.legal_labels[legal_pred.item()],
                "score": legal_probs.max().item(),
                "all_scores": [
                    {"label": label, "score": score.item()}
                    for label, score in zip(self.legal_labels, legal_probs[0])
                ] if return_all_scores else None
            }
        
        return results


# Registro dos modelos no AutoModel
from transformers import AutoConfig, AutoModel

AutoConfig.register("cidadao-gpt", CidadaoAIConfig)
AutoModel.register(CidadaoAIConfig, CidadaoAIModel)


def create_cidadao_pipeline(
    model_name_or_path: str = "neural-thinker/cidadao-gpt",
    task: str = "transparency-analysis",
    **kwargs
) -> TransparencyAnalysisPipeline:
    """
    Criar pipeline Cidadão.AI
    
    Args:
        model_name_or_path: Nome do modelo no HF Hub ou caminho local
        task: Tipo de tarefa
        **kwargs: Argumentos adicionais
    
    Returns:
        Pipeline configurado
    """
    
    model = AutoModel.from_pretrained(model_name_or_path, **kwargs)
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, **kwargs)
    
    return TransparencyAnalysisPipeline(
        model=model,
        tokenizer=tokenizer,
        task=task
    )


# Função de conveniência para uso rápido
def analyze_transparency(
    text: str,
    model_name: str = "neural-thinker/cidadao-gpt"
) -> Dict:
    """
    Análise rápida de transparência
    
    Args:
        text: Texto para análise
        model_name: Nome do modelo
    
    Returns:
        Resultados da análise
    """
    
    pipe = create_cidadao_pipeline(model_name)
    return pipe(text, return_all_scores=True)


if __name__ == "__main__":
    # Exemplo de uso
    
    # Criar configuração
    config = CidadaoAIConfig(
        vocab_size=50257,
        hidden_size=768,
        num_hidden_layers=12,
        num_attention_heads=12,
        enable_anomaly_detection=True,
        enable_financial_analysis=True,
        enable_legal_reasoning=True
    )
    
    # Criar modelo
    model = CidadaoAIModel(config)
    
    print(f"✅ Modelo Cidadão.AI criado com {sum(p.numel() for p in model.parameters()):,} parâmetros")
    print(f"🎯 Tarefas habilitadas: Anomalias, Financeiro, Legal")
    
    # Teste básico
    batch_size, seq_len = 2, 128
    input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_len))
    attention_mask = torch.ones(batch_size, seq_len)
    
    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
    
    print(f"📊 Output shape: {outputs.last_hidden_state.shape}")
    print(f"🔍 Anomaly logits: {outputs.anomaly_logits.shape if 'anomaly_logits' in outputs else 'N/A'}")
    print(f"💰 Financial logits: {outputs.financial_logits.shape if 'financial_logits' in outputs else 'N/A'}")
    print(f"⚖️ Legal logits: {outputs.legal_logits.shape if 'legal_logits' in outputs else 'N/A'}")