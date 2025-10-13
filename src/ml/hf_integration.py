#!/usr/bin/env python3
"""
Integração completa entre Cidadão.AI e Hugging Face Hub

Este módulo facilita a integração entre o modelo especializado
e a biblioteca transformers do Hugging Face.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

import torch
from transformers import AutoConfig, AutoModel, AutoTokenizer

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.ml.hf_cidadao_model import TransparencyAnalysisPipeline

logger = logging.getLogger(__name__)


class CidadaoAIHubManager:
    """Gerenciador de integração com Hugging Face Hub"""

    def __init__(
        self,
        model_name: str = "neural-thinker/cidadao-gpt",
        cache_dir: Optional[str] = None,
        use_auth_token: Optional[str] = None,
    ):
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.use_auth_token = use_auth_token or os.getenv("HUGGINGFACE_HUB_TOKEN")

        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.config = None

        # Setup logging
        logging.basicConfig(level=logging.INFO)

    def load_from_hub(self) -> bool:
        """Carregar modelo do Hugging Face Hub"""

        try:
            logger.info(f"🔄 Carregando Cidadão.AI de {self.model_name}...")

            # Carregar configuração
            self.config = AutoConfig.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                use_auth_token=self.use_auth_token,
            )

            # Carregar tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                use_auth_token=self.use_auth_token,
            )

            # Carregar modelo
            self.model = AutoModel.from_pretrained(
                self.model_name,
                config=self.config,
                cache_dir=self.cache_dir,
                use_auth_token=self.use_auth_token,
            )

            # Criar pipeline especializado
            self.pipeline = TransparencyAnalysisPipeline(
                model=self.model, tokenizer=self.tokenizer, task="transparency-analysis"
            )

            logger.info("✅ Modelo carregado com sucesso do Hugging Face Hub")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao carregar do Hub: {e}")
            logger.info("🔄 Tentando carregar modelo local...")
            return self._load_local_fallback()

    def _load_local_fallback(self) -> bool:
        """Fallback para modelo local se Hub não disponível"""

        try:
            from src.ml.cidadao_model import create_cidadao_model

            logger.info("📂 Carregando modelo local...")

            # Criar modelo local
            self.model = create_cidadao_model(
                specialized_tasks=["all"], model_size="medium"
            )

            # Usar tokenizer base
            self.tokenizer = AutoTokenizer.from_pretrained("gpt2")

            # Adicionar tokens especiais
            special_tokens = [
                "[CONTRACT]",
                "[ENTITY]",
                "[VALUE]",
                "[ANOMALY]",
                "[LEGAL]",
                "[FINANCIAL]",
                "[CORRUPTION]",
                "[COMPLIANCE]",
            ]

            self.tokenizer.add_special_tokens(
                {"additional_special_tokens": special_tokens}
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            logger.info("✅ Modelo local carregado com sucesso")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo local: {e}")
            return False

    def analyze_text(
        self,
        text: str,
        analysis_type: str = "complete",
        return_all_scores: bool = False,
    ) -> dict:
        """Analisar texto usando modelo Cidadão.AI"""

        if not self.model:
            raise RuntimeError(
                "Modelo não carregado. Execute load_from_hub() primeiro."
            )

        try:
            if self.pipeline:
                # Usar pipeline se disponível
                return self.pipeline(text, return_all_scores=return_all_scores)
            else:
                # Usar modelo diretamente
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    padding=True,
                    max_length=512,
                )

                with torch.no_grad():
                    outputs = self.model(**inputs)

                # Processar outputs
                results = {}

                # Anomalias
                if hasattr(outputs, "anomaly_logits") or "anomaly_logits" in outputs:
                    anomaly_logits = outputs.get(
                        "anomaly_logits", outputs.anomaly_logits
                    )
                    anomaly_probs = torch.softmax(anomaly_logits, dim=-1)
                    anomaly_pred = torch.argmax(anomaly_probs, dim=-1)

                    anomaly_labels = ["Normal", "Suspeito", "Anômalo"]
                    results["anomaly"] = {
                        "label": anomaly_labels[anomaly_pred.item()],
                        "score": anomaly_probs.max().item(),
                    }

                # Risco financeiro
                if (
                    hasattr(outputs, "financial_logits")
                    or "financial_logits" in outputs
                ):
                    financial_logits = outputs.get(
                        "financial_logits", outputs.financial_logits
                    )
                    financial_probs = torch.softmax(financial_logits, dim=-1)
                    financial_pred = torch.argmax(financial_probs, dim=-1)

                    financial_labels = [
                        "Muito Baixo",
                        "Baixo",
                        "Médio",
                        "Alto",
                        "Muito Alto",
                    ]
                    results["financial"] = {
                        "label": financial_labels[financial_pred.item()],
                        "score": financial_probs.max().item(),
                    }

                # Conformidade legal
                if hasattr(outputs, "legal_logits") or "legal_logits" in outputs:
                    legal_logits = outputs.get("legal_logits", outputs.legal_logits)
                    legal_probs = torch.softmax(legal_logits, dim=-1)
                    legal_pred = torch.argmax(legal_probs, dim=-1)

                    legal_labels = ["Não Conforme", "Conforme"]
                    results["legal"] = {
                        "label": legal_labels[legal_pred.item()],
                        "score": legal_probs.max().item(),
                    }

                return results

        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
            raise

    def batch_analyze(
        self, texts: list[str], analysis_type: str = "complete"
    ) -> list[dict]:
        """Análise em lote de textos"""

        results = []
        for text in texts:
            try:
                result = self.analyze_text(text, analysis_type)
                results.append(result)
            except Exception as e:
                logger.error(f"❌ Erro na análise do texto: {e}")
                results.append({"error": str(e)})

        return results

    def get_model_info(self) -> dict:
        """Obter informações do modelo"""

        if not self.model:
            return {"status": "not_loaded"}

        try:
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(
                p.numel() for p in self.model.parameters() if p.requires_grad
            )

            info = {
                "model_name": self.model_name,
                "total_parameters": total_params,
                "trainable_parameters": trainable_params,
                "model_size_gb": total_params * 4 / (1024**3),  # Estimativa FP32
                "status": "loaded",
                "source": "huggingface_hub" if self.pipeline else "local",
            }

            if self.config:
                info.update(
                    {
                        "hidden_size": getattr(self.config, "hidden_size", None),
                        "num_layers": getattr(self.config, "num_hidden_layers", None),
                        "vocab_size": getattr(self.config, "vocab_size", None),
                        "specialized_tasks": {
                            "anomaly_detection": getattr(
                                self.config, "enable_anomaly_detection", False
                            ),
                            "financial_analysis": getattr(
                                self.config, "enable_financial_analysis", False
                            ),
                            "legal_reasoning": getattr(
                                self.config, "enable_legal_reasoning", False
                            ),
                        },
                    }
                )

            return info

        except Exception as e:
            logger.error(f"❌ Erro ao obter informações: {e}")
            return {"status": "error", "error": str(e)}

    def test_model(self) -> dict:
        """Testar modelo com exemplo padrão"""

        test_text = """
        Contrato emergencial no valor de R$ 25.000.000,00 para aquisição
        de equipamentos médicos dispensando licitação. Fornecedor: Empresa XYZ LTDA.
        """

        try:
            result = self.analyze_text(test_text.strip())

            return {
                "status": "success",
                "test_input": test_text.strip(),
                "analysis_result": result,
                "model_info": self.get_model_info(),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "model_info": self.get_model_info(),
            }


# Função de conveniência para uso global
_global_manager = None


def get_cidadao_manager(
    model_name: str = "neural-thinker/cidadao-gpt", force_reload: bool = False
) -> CidadaoAIHubManager:
    """Obter instância global do manager"""

    global _global_manager

    if _global_manager is None or force_reload:
        _global_manager = CidadaoAIHubManager(model_name)
        success = _global_manager.load_from_hub()

        if not success:
            logger.warning(
                "⚠️ Falha ao carregar modelo. Verifique conectividade ou configuração."
            )

    return _global_manager


def quick_analyze(text: str, model_name: str = "neural-thinker/cidadao-gpt") -> dict:
    """Análise rápida usando modelo do HF Hub"""

    manager = get_cidadao_manager(model_name)
    return manager.analyze_text(text)


if __name__ == "__main__":
    # Demonstração de uso

    print("🤖 Testando integração Cidadão.AI + Hugging Face")
    print("=" * 60)

    # Criar manager
    manager = CidadaoAIHubManager()

    # Carregar modelo
    success = manager.load_from_hub()

    if success:
        print("✅ Modelo carregado com sucesso!")

        # Teste básico
        test_result = manager.test_model()

        print("\n📊 Resultado do teste:")
        print(f"Status: {test_result['status']}")

        if test_result["status"] == "success":
            result = test_result["analysis_result"]
            print(f"Anomalia: {result.get('anomaly', {}).get('label', 'N/A')}")
            print(
                f"Risco Financeiro: {result.get('financial', {}).get('label', 'N/A')}"
            )
            print(f"Conformidade Legal: {result.get('legal', {}).get('label', 'N/A')}")
        else:
            print(f"Erro: {test_result.get('error', 'Desconhecido')}")

        # Informações do modelo
        info = manager.get_model_info()
        print("\n🔧 Informações do modelo:")
        print(f"Parâmetros: {info.get('total_parameters', 0):,}")
        print(f"Fonte: {info.get('source', 'Desconhecida')}")

    else:
        print("❌ Falha ao carregar modelo")
