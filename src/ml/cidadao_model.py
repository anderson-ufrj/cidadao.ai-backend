"""
Cidadão.AI - Modelo de IA Especializado para Transparência Pública Brasileira

Inspirado no Kimi K2, este modelo é otimizado especificamente para:
- Análise de gastos públicos
- Detecção de anomalias em contratos governamentais
- Compreensão de linguagem jurídica e administrativa brasileira
- Raciocínio sobre padrões de corrupção e irregularidades
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from torch import nn
from transformers import AutoConfig

from src.core import json_utils

logger = logging.getLogger(__name__)


@dataclass
class CidadaoModelConfig:
    """Configuração do modelo Cidadão.AI"""

    # Arquitetura base
    base_model_name: str = "microsoft/DialoGPT-medium"  # Modelo base para fine-tuning
    hidden_size: int = 1024
    num_attention_heads: int = 16
    num_hidden_layers: int = 24
    intermediate_size: int = 4096
    max_position_embeddings: int = 8192
    vocab_size: int = 50257

    # Configurações específicas para transparência
    transparency_vocab_size: int = 2048  # Vocabulário especializado
    corruption_detection_layers: int = 4  # Camadas específicas para detecção
    financial_analysis_dim: int = 512  # Dimensão para análise financeira
    legal_understanding_dim: int = 256  # Dimensão para compreensão jurídica

    # Configurações de treinamento
    dropout_rate: float = 0.1
    attention_dropout: float = 0.1
    use_cache: bool = True

    # Tarefas especializadas
    enable_anomaly_detection: bool = True
    enable_financial_analysis: bool = True
    enable_legal_reasoning: bool = True
    enable_pattern_recognition: bool = True


class TransparencyEmbeddings(nn.Module):
    """Embeddings especializados para dados de transparência"""

    def __init__(self, config: CidadaoModelConfig):
        super().__init__()
        self.config = config

        # Embeddings principais
        self.word_embeddings = nn.Embedding(config.vocab_size, config.hidden_size)
        self.position_embeddings = nn.Embedding(
            config.max_position_embeddings, config.hidden_size
        )

        # Embeddings especializados para transparência
        self.entity_type_embeddings = nn.Embedding(
            100, config.hidden_size // 4
        )  # Tipos de entidade
        self.financial_embeddings = nn.Embedding(
            50, config.hidden_size // 4
        )  # Tipos financeiros
        self.legal_embeddings = nn.Embedding(
            200, config.hidden_size // 4
        )  # Termos jurídicos
        self.corruption_indicator_embeddings = nn.Embedding(
            20, config.hidden_size // 4
        )  # Indicadores

        self.layer_norm = nn.LayerNorm(config.hidden_size)
        self.dropout = nn.Dropout(config.dropout_rate)

    def forward(
        self,
        input_ids: torch.Tensor,
        position_ids: torch.Tensor | None = None,
        entity_types: torch.Tensor | None = None,
        financial_types: torch.Tensor | None = None,
        legal_types: torch.Tensor | None = None,
        corruption_indicators: torch.Tensor | None = None,
    ) -> torch.Tensor:

        seq_length = input_ids.size(1)

        if position_ids is None:
            position_ids = torch.arange(
                seq_length, dtype=torch.long, device=input_ids.device
            )
            position_ids = position_ids.unsqueeze(0).expand_as(input_ids)

        # Embeddings principais
        word_embeds = self.word_embeddings(input_ids)
        position_embeds = self.position_embeddings(position_ids)

        embeddings = word_embeds + position_embeds

        # Adicionar embeddings especializados se disponíveis
        if entity_types is not None:
            entity_embeds = self.entity_type_embeddings(entity_types)
            embeddings = embeddings + entity_embeds

        if financial_types is not None:
            financial_embeds = self.financial_embeddings(financial_types)
            embeddings = embeddings + financial_embeds

        if legal_types is not None:
            legal_embeds = self.legal_embeddings(legal_types)
            embeddings = embeddings + legal_embeds

        if corruption_indicators is not None:
            corruption_embeds = self.corruption_indicator_embeddings(
                corruption_indicators
            )
            embeddings = embeddings + corruption_embeds

        embeddings = self.layer_norm(embeddings)
        embeddings = self.dropout(embeddings)

        return embeddings


class AnomalyDetectionHead(nn.Module):
    """Cabeça especializada para detecção de anomalias"""

    def __init__(self, config: CidadaoModelConfig):
        super().__init__()
        self.config = config

        self.anomaly_classifier = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_size // 2, config.hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_size // 4, 3),  # Normal, Suspeito, Anômalo
        )

        self.confidence_estimator = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size // 4),
            nn.ReLU(),
            nn.Linear(config.hidden_size // 4, 1),
            nn.Sigmoid(),
        )

    def forward(self, hidden_states: torch.Tensor) -> dict[str, torch.Tensor]:
        # Usar pooling na sequência para classificação
        pooled_output = hidden_states.mean(dim=1)

        anomaly_logits = self.anomaly_classifier(pooled_output)
        confidence_score = self.confidence_estimator(pooled_output)

        return {"anomaly_logits": anomaly_logits, "confidence_score": confidence_score}


class FinancialAnalysisHead(nn.Module):
    """Cabeça especializada para análise financeira"""

    def __init__(self, config: CidadaoModelConfig):
        super().__init__()
        self.config = config

        self.value_estimator = nn.Sequential(
            nn.Linear(config.hidden_size, config.financial_analysis_dim),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.financial_analysis_dim, 1),
        )

        self.risk_classifier = nn.Sequential(
            nn.Linear(config.hidden_size, config.financial_analysis_dim),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(
                config.financial_analysis_dim, 5
            ),  # Muito Baixo, Baixo, Médio, Alto, Muito Alto
        )

    def forward(self, hidden_states: torch.Tensor) -> dict[str, torch.Tensor]:
        pooled_output = hidden_states.mean(dim=1)

        estimated_value = self.value_estimator(pooled_output)
        risk_logits = self.risk_classifier(pooled_output)

        return {"estimated_value": estimated_value, "risk_logits": risk_logits}


class LegalReasoningHead(nn.Module):
    """Cabeça especializada para raciocínio jurídico"""

    def __init__(self, config: CidadaoModelConfig):
        super().__init__()
        self.config = config

        self.legal_classifier = nn.Sequential(
            nn.Linear(config.hidden_size, config.legal_understanding_dim),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(
                config.legal_understanding_dim, 10
            ),  # Classificação de tipos legais
        )

        self.compliance_checker = nn.Sequential(
            nn.Linear(config.hidden_size, config.legal_understanding_dim),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.legal_understanding_dim, 2),  # Conforme, Não Conforme
        )

    def forward(self, hidden_states: torch.Tensor) -> dict[str, torch.Tensor]:
        pooled_output = hidden_states.mean(dim=1)

        legal_type_logits = self.legal_classifier(pooled_output)
        compliance_logits = self.compliance_checker(pooled_output)

        return {
            "legal_type_logits": legal_type_logits,
            "compliance_logits": compliance_logits,
        }


class CidadaoAIModel(nn.Module):
    """
    Cidadão.AI - Modelo de IA especializado para transparência pública brasileira

    Características principais:
    - Fine-tuned para dados governamentais brasileiros
    - Otimizado para detecção de anomalias e análise de corrupção
    - Compreende linguagem jurídica e administrativa
    - Especializado em análise financeira de contratos públicos
    """

    def __init__(self, config: CidadaoModelConfig):
        super().__init__()
        self.config = config

        # Modelo base
        self.embeddings = TransparencyEmbeddings(config)

        # Transformer layers (usar implementação padrão ou customizada)
        from transformers.models.gpt2.modeling_gpt2 import GPT2Block

        self.layers = nn.ModuleList(
            [
                GPT2Block(
                    AutoConfig.from_pretrained(config.base_model_name), layer_idx=i
                )
                for i in range(config.num_hidden_layers)
            ]
        )

        self.ln_f = nn.LayerNorm(config.hidden_size)

        # Cabeças especializadas
        if config.enable_anomaly_detection:
            self.anomaly_head = AnomalyDetectionHead(config)

        if config.enable_financial_analysis:
            self.financial_head = FinancialAnalysisHead(config)

        if config.enable_legal_reasoning:
            self.legal_head = LegalReasoningHead(config)

        # Cabeça de geração de linguagem
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)

        self.init_weights()

    def init_weights(self):
        """Inicializar pesos do modelo"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
                if module.bias is not None:
                    torch.nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        position_ids: torch.Tensor | None = None,
        entity_types: torch.Tensor | None = None,
        financial_types: torch.Tensor | None = None,
        legal_types: torch.Tensor | None = None,
        corruption_indicators: torch.Tensor | None = None,
        task: str = "generation",
        **kwargs,
    ) -> dict[str, torch.Tensor]:

        # Embeddings
        hidden_states = self.embeddings(
            input_ids=input_ids,
            position_ids=position_ids,
            entity_types=entity_types,
            financial_types=financial_types,
            legal_types=legal_types,
            corruption_indicators=corruption_indicators,
        )

        # Transformer layers
        for layer in self.layers:
            hidden_states = layer(hidden_states, attention_mask=attention_mask)[0]

        hidden_states = self.ln_f(hidden_states)

        outputs = {"last_hidden_state": hidden_states}

        # Aplicar cabeças especializadas baseadas na tarefa
        if task == "anomaly_detection" and hasattr(self, "anomaly_head"):
            anomaly_outputs = self.anomaly_head(hidden_states)
            outputs.update(anomaly_outputs)

        elif task == "financial_analysis" and hasattr(self, "financial_head"):
            financial_outputs = self.financial_head(hidden_states)
            outputs.update(financial_outputs)

        elif task == "legal_reasoning" and hasattr(self, "legal_head"):
            legal_outputs = self.legal_head(hidden_states)
            outputs.update(legal_outputs)

        elif task == "generation":
            lm_logits = self.lm_head(hidden_states)
            outputs["logits"] = lm_logits

        return outputs


class CidadaoAIForTransparency(nn.Module):
    """Wrapper para treinamento e inferência completa"""

    def __init__(self, config: CidadaoModelConfig):
        super().__init__()
        self.config = config
        self.model = CidadaoAIModel(config)

        # Métricas de transparência
        self.transparency_metrics = {
            "corruption_risk_threshold": 0.7,
            "anomaly_confidence_threshold": 0.8,
            "financial_risk_threshold": 0.6,
        }

    def detect_anomalies(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Detectar anomalias em dados de transparência"""

        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            task="anomaly_detection",
            **kwargs,
        )

        anomaly_probs = torch.softmax(outputs["anomaly_logits"], dim=-1)
        confidence = outputs["confidence_score"]

        # Interpretação dos resultados
        predictions = torch.argmax(anomaly_probs, dim=-1)
        anomaly_labels = ["Normal", "Suspeito", "Anômalo"]

        results = []
        for i, (pred, conf) in enumerate(zip(predictions, confidence, strict=False)):
            results.append(
                {
                    "sample_id": i,
                    "anomaly_type": anomaly_labels[pred.item()],
                    "confidence": conf.item(),
                    "probabilities": {
                        "normal": anomaly_probs[i][0].item(),
                        "suspicious": anomaly_probs[i][1].item(),
                        "anomalous": anomaly_probs[i][2].item(),
                    },
                    "is_high_confidence": conf.item()
                    > self.transparency_metrics["anomaly_confidence_threshold"],
                }
            )

        return {
            "predictions": results,
            "summary": {
                "total_samples": len(results),
                "anomalous_count": sum(
                    1 for r in results if r["anomaly_type"] == "Anômalo"
                ),
                "suspicious_count": sum(
                    1 for r in results if r["anomaly_type"] == "Suspeito"
                ),
                "high_confidence_count": sum(
                    1 for r in results if r["is_high_confidence"]
                ),
            },
        }

    def analyze_financial_risk(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Analisar risco financeiro"""

        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            task="financial_analysis",
            **kwargs,
        )

        risk_probs = torch.softmax(outputs["risk_logits"], dim=-1)
        estimated_values = outputs["estimated_value"]

        risk_labels = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
        risk_predictions = torch.argmax(risk_probs, dim=-1)

        results = []
        for i, (risk_pred, value) in enumerate(
            zip(risk_predictions, estimated_values, strict=False)
        ):
            results.append(
                {
                    "sample_id": i,
                    "risk_level": risk_labels[risk_pred.item()],
                    "estimated_value": value.item(),
                    "risk_probabilities": {
                        label: prob.item()
                        for label, prob in zip(risk_labels, risk_probs[i], strict=False)
                    },
                    "is_high_risk": risk_pred.item() >= 3,  # Alto ou Muito Alto
                }
            )

        return {
            "predictions": results,
            "summary": {
                "total_samples": len(results),
                "high_risk_count": sum(1 for r in results if r["is_high_risk"]),
                "average_estimated_value": sum(r["estimated_value"] for r in results)
                / len(results),
            },
        }

    def check_legal_compliance(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Verificar conformidade legal"""

        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            task="legal_reasoning",
            **kwargs,
        )

        compliance_probs = torch.softmax(outputs["compliance_logits"], dim=-1)
        legal_type_probs = torch.softmax(outputs["legal_type_logits"], dim=-1)

        compliance_predictions = torch.argmax(compliance_probs, dim=-1)
        compliance_labels = ["Não Conforme", "Conforme"]

        results = []
        for i, comp_pred in enumerate(compliance_predictions):
            results.append(
                {
                    "sample_id": i,
                    "compliance_status": compliance_labels[comp_pred.item()],
                    "compliance_confidence": compliance_probs[i][
                        comp_pred.item()
                    ].item(),
                    "legal_analysis": {
                        "compliant_prob": compliance_probs[i][1].item(),
                        "non_compliant_prob": compliance_probs[i][0].item(),
                    },
                    "is_compliant": comp_pred.item() == 1,
                }
            )

        return {
            "predictions": results,
            "summary": {
                "total_samples": len(results),
                "compliant_count": sum(1 for r in results if r["is_compliant"]),
                "non_compliant_count": sum(1 for r in results if not r["is_compliant"]),
                "compliance_rate": sum(1 for r in results if r["is_compliant"])
                / len(results),
            },
        }

    def generate_transparency_report(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        max_length: int = 512,
        **kwargs,
    ) -> str:
        """Gerar relatório de transparência em linguagem natural"""

        # Análise completa
        anomaly_results = self.detect_anomalies(input_ids, attention_mask, **kwargs)
        financial_results = self.analyze_financial_risk(
            input_ids, attention_mask, **kwargs
        )
        legal_results = self.check_legal_compliance(input_ids, attention_mask, **kwargs)

        # Geração de texto
        generation_outputs = self.model(
            input_ids=input_ids, attention_mask=attention_mask, task="generation"
        )

        # Construir relatório estruturado
        report = {
            "executive_summary": {
                "anomaly_analysis": anomaly_results["summary"],
                "financial_analysis": financial_results["summary"],
                "legal_analysis": legal_results["summary"],
            },
            "detailed_findings": {
                "anomalies": anomaly_results["predictions"],
                "financial_risks": financial_results["predictions"],
                "legal_compliance": legal_results["predictions"],
            },
            "recommendations": self._generate_recommendations(
                anomaly_results, financial_results, legal_results
            ),
        }

        return report

    def _generate_recommendations(
        self, anomaly_results: dict, financial_results: dict, legal_results: dict
    ) -> list[str]:
        """Gerar recomendações baseadas na análise"""

        recommendations = []

        # Recomendações baseadas em anomalias
        if anomaly_results["summary"]["anomalous_count"] > 0:
            recommendations.append(
                f"🚨 Foram detectadas {anomaly_results['summary']['anomalous_count']} "
                f"anomalias que requerem investigação imediata."
            )

        # Recomendações baseadas em risco financeiro
        if financial_results["summary"]["high_risk_count"] > 0:
            recommendations.append(
                f"⚠️ {financial_results['summary']['high_risk_count']} contratos "
                f"apresentam alto risco financeiro e devem ser revisados."
            )

        # Recomendações baseadas em conformidade legal
        compliance_rate = legal_results["summary"]["compliance_rate"]
        if compliance_rate < 0.8:
            recommendations.append(
                f"📋 Taxa de conformidade legal baixa ({compliance_rate:.1%}). "
                f"Recomenda-se revisão dos processos de compliance."
            )

        if not recommendations:
            recommendations.append("✅ Análise não identificou problemas críticos.")

        return recommendations

    def save_model(self, save_path: str):
        """Salvar modelo treinado"""
        save_dir = Path(save_path)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Salvar pesos do modelo
        torch.save(self.state_dict(), save_dir / "model.pt")

        # Salvar configuração
        with open(save_dir / "config.json", "w") as f:
            json_utils.dump(self.config.__dict__, f, indent=2)

        logger.info(f"Modelo salvo em {save_path}")

    @classmethod
    def load_model(cls, load_path: str):
        """Carregar modelo treinado"""
        load_dir = Path(load_path)

        # Carregar configuração
        with open(load_dir / "config.json") as f:
            config_dict = json_utils.load(f)

        config = CidadaoModelConfig(**config_dict)
        model = cls(config)

        # Carregar pesos
        model.load_state_dict(torch.load(load_dir / "model.pt"))

        logger.info(f"Modelo carregado de {load_path}")
        return model


# Factory function para facilitar uso
def create_cidadao_model(
    specialized_tasks: list[str] = None, model_size: str = "medium"
) -> CidadaoAIForTransparency:
    """
    Criar modelo Cidadão.AI com configurações otimizadas

    Args:
        specialized_tasks: Lista de tarefas ['anomaly', 'financial', 'legal', 'all']
        model_size: Tamanho do modelo ['small', 'medium', 'large']
    """

    if specialized_tasks is None:
        specialized_tasks = ["all"]

    # Configurações por tamanho
    size_configs = {
        "small": {
            "hidden_size": 512,
            "num_attention_heads": 8,
            "num_hidden_layers": 12,
            "intermediate_size": 2048,
        },
        "medium": {
            "hidden_size": 1024,
            "num_attention_heads": 16,
            "num_hidden_layers": 24,
            "intermediate_size": 4096,
        },
        "large": {
            "hidden_size": 1536,
            "num_attention_heads": 24,
            "num_hidden_layers": 36,
            "intermediate_size": 6144,
        },
    }

    config = CidadaoModelConfig(**size_configs[model_size])

    # Configurar tarefas especializadas
    if "all" in specialized_tasks:
        config.enable_anomaly_detection = True
        config.enable_financial_analysis = True
        config.enable_legal_reasoning = True
    else:
        config.enable_anomaly_detection = "anomaly" in specialized_tasks
        config.enable_financial_analysis = "financial" in specialized_tasks
        config.enable_legal_reasoning = "legal" in specialized_tasks

    return CidadaoAIForTransparency(config)


if __name__ == "__main__":
    # Exemplo de uso
    print("🤖 Criando Cidadão.AI - Modelo especializado para transparência pública")

    model = create_cidadao_model(specialized_tasks=["all"], model_size="medium")

    print(
        f"✅ Modelo criado com {sum(p.numel() for p in model.parameters())} parâmetros"
    )
    print(
        "🎯 Tarefas especializadas: Detecção de anomalias, Análise financeira, Raciocínio jurídico"
    )
