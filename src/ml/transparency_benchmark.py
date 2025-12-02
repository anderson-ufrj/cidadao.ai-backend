"""
Benchmark Especializado para Tarefas de Transparência Pública

Sistema de avaliação inspirado no padrão Kimi K2, mas otimizado para
análise de transparência governamental brasileira.
"""

import asyncio
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score,
)

from src.core import json_utils

from .cidadao_model import CidadaoAIForTransparency
from .model_api import CidadaoAIManager, TransparencyAnalysisRequest

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkConfig:
    """Configuração do benchmark"""

    # Configurações gerais
    benchmark_name: str = "TransparenciaBench-BR"
    version: str = "1.0.0"

    # Configurações de teste
    test_data_path: str = "./data/benchmark/test_data.json"
    max_samples_per_task: int = 1000
    batch_size: int = 32

    # Tarefas a serem avaliadas
    tasks: list[str] = None

    # Configurações de métrica
    confidence_threshold: float = 0.7
    time_limit_per_sample: float = 10.0  # segundos

    # Configurações de output
    output_dir: str = "./benchmark_results"
    save_detailed_results: bool = True
    generate_plots: bool = True

    def __post_init__(self):
        if self.tasks is None:
            self.tasks = [
                "anomaly_detection",
                "financial_analysis",
                "legal_compliance",
                "integration",
            ]


@dataclass
class TaskMetrics:
    """Métricas para uma tarefa específica"""

    task_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_score: float | None = None
    confidence_score: float = 0.0
    processing_time: float = 0.0
    sample_count: int = 0

    # Métricas específicas de transparência
    anomaly_detection_rate: float | None = None
    false_positive_rate: float | None = None
    compliance_accuracy: float | None = None
    risk_assessment_accuracy: float | None = None


@dataclass
class BenchmarkResults:
    """Resultados completos do benchmark"""

    benchmark_name: str
    model_name: str
    timestamp: str

    # Métricas por tarefa
    task_metrics: dict[str, TaskMetrics]

    # Métricas agregadas
    overall_accuracy: float
    overall_f1: float
    average_confidence: float
    average_processing_time: float

    # Métricas específicas de transparência
    transparency_score: float  # Score composto
    corruption_detection_ability: float
    legal_compliance_understanding: float
    financial_risk_assessment: float

    # Comparações
    compared_to_baselines: dict[str, float] | None = None
    improvement_over_baseline: float | None = None


class TransparencyBenchmarkSuite:
    """Suite de benchmark para tarefas de transparência"""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.test_datasets = {}
        self.baseline_results = {}

        # Carregar dados de teste
        self._load_test_datasets()

        # Carregar baselines se disponíveis
        self._load_baseline_results()

    def _load_test_datasets(self):
        """Carregar datasets de teste para cada tarefa"""

        logger.info("📊 Carregando datasets de teste")

        # Se não existir dados de teste, criar datasets sintéticos
        if not Path(self.config.test_data_path).exists():
            logger.warning(
                "⚠️ Dados de teste não encontrados. Criando datasets sintéticos."
            )
            self._create_synthetic_test_data()

        # Carregar dados
        with open(self.config.test_data_path, encoding="utf-8") as f:
            all_test_data = json_utils.load(f)

        # Organizar por tarefa
        for task in self.config.tasks:
            if task in all_test_data:
                self.test_datasets[task] = all_test_data[task][
                    : self.config.max_samples_per_task
                ]
                logger.info(
                    f"✅ {task}: {len(self.test_datasets[task])} exemplos carregados"
                )

    def _create_synthetic_test_data(self):
        """Criar dados de teste sintéticos"""

        logger.info("🔧 Criando dados de teste sintéticos")

        synthetic_data = {
            "anomaly_detection": self._create_anomaly_test_cases(),
            "financial_analysis": self._create_financial_test_cases(),
            "legal_compliance": self._create_legal_test_cases(),
            "integration": self._create_integration_test_cases(),
        }

        # Salvar dados sintéticos
        output_dir = Path(self.config.test_data_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(self.config.test_data_path, "w", encoding="utf-8") as f:
            json_utils.dump(synthetic_data, f, ensure_ascii=False, indent=2)

        logger.info(f"💾 Dados sintéticos salvos em {self.config.test_data_path}")

    def _create_anomaly_test_cases(self) -> list[dict]:
        """Criar casos de teste para detecção de anomalias"""

        test_cases = []

        # Casos normais (sem anomalias)
        normal_cases = [
            {
                "text": "Contrato para aquisição de equipamentos de informática no valor de R$ 150.000,00 através de pregão eletrônico. Processo licitatório 2024/001, vencedora Empresa Tech Solutions LTDA.",
                "expected_anomaly": 0,  # Normal
                "expected_confidence": 0.8,
                "case_type": "normal_procurement",
            },
            {
                "text": "Convênio de cooperação técnica entre Ministério da Educação e Universidade Federal. Valor de repasse: R$ 500.000,00 para projeto de pesquisa científica.",
                "expected_anomaly": 0,
                "expected_confidence": 0.9,
                "case_type": "normal_cooperation",
            },
        ]

        # Casos suspeitos
        suspicious_cases = [
            {
                "text": "Contrato emergencial sem licitação para aquisição de materiais hospitalares. Valor: R$ 2.000.000,00. Fornecedor: Empresa familiar do prefeito.",
                "expected_anomaly": 1,  # Suspeito
                "expected_confidence": 0.7,
                "case_type": "suspicious_emergency",
            },
            {
                "text": "Licitação com prazo reduzido de 3 dias para obra de pavimentação. Único participante: empresa recém-criada com sócios em comum com a administração.",
                "expected_anomaly": 1,
                "expected_confidence": 0.8,
                "case_type": "suspicious_bidding",
            },
        ]

        # Casos anômalos
        anomalous_cases = [
            {
                "text": "Contrato de R$ 50 milhões para 'consultoria em gestão' com empresa sem funcionários registrados. Pagamento integral antecipado sem garantias.",
                "expected_anomaly": 2,  # Anômalo
                "expected_confidence": 0.95,
                "case_type": "clear_fraud",
            },
            {
                "text": "Dispensa de licitação para aquisição de equipamentos superfaturados em 300%. Empresa beneficiária pertence ao cônjuge do secretário responsável.",
                "expected_anomaly": 2,
                "expected_confidence": 0.9,
                "case_type": "corruption_scheme",
            },
        ]

        # Combinar casos (50 de cada tipo)
        for cases, count in [
            (normal_cases, 50),
            (suspicious_cases, 30),
            (anomalous_cases, 20),
        ]:
            for i in range(count):
                case = cases[i % len(cases)].copy()
                case["id"] = f"anomaly_test_{len(test_cases)}"
                test_cases.append(case)

        return test_cases

    def _create_financial_test_cases(self) -> list[dict]:
        """Criar casos de teste para análise financeira"""

        test_cases = []

        # Baixo risco
        low_risk_cases = [
            {
                "text": "Aquisição de material de escritório via ata de registro de preços. Valor: R$ 50.000,00. Fornecedor tradicional com histórico positivo.",
                "expected_risk": 0,  # Muito baixo
                "expected_confidence": 0.8,
                "case_type": "low_risk_supplies",
            }
        ]

        # Alto risco
        high_risk_cases = [
            {
                "text": "Obra de construção de hospital sem projeto básico detalhado. Valor inicial: R$ 100 milhões. Histórico de aditivos contratuais excessivos.",
                "expected_risk": 4,  # Muito alto
                "expected_confidence": 0.9,
                "case_type": "high_risk_construction",
            }
        ]

        # Criar 80 casos (40 baixo risco, 40 alto risco)
        for cases, expected_risk, count in [
            (low_risk_cases, 0, 40),
            (high_risk_cases, 4, 40),
        ]:
            for i in range(count):
                case = cases[i % len(cases)].copy()
                case["id"] = f"financial_test_{len(test_cases)}"
                case["expected_risk"] = expected_risk
                test_cases.append(case)

        return test_cases

    def _create_legal_test_cases(self) -> list[dict]:
        """Criar casos de teste para conformidade legal"""

        test_cases = []

        # Casos conformes
        compliant_cases = [
            {
                "text": "Processo licitatório conduzido conforme Lei 14.133/2021. Documentação completa, prazo adequado, ampla publicidade e julgamento objetivo.",
                "expected_compliance": 1,  # Conforme
                "expected_confidence": 0.9,
                "case_type": "fully_compliant",
            }
        ]

        # Casos não conformes
        non_compliant_cases = [
            {
                "text": "Contratação direta irregular sem fundamentação legal adequada. Ausência de justificativa para dispensa de licitação.",
                "expected_compliance": 0,  # Não conforme
                "expected_confidence": 0.85,
                "case_type": "non_compliant",
            }
        ]

        # Criar 60 casos (30 de cada tipo)
        for cases, expected, count in [
            (compliant_cases, 1, 30),
            (non_compliant_cases, 0, 30),
        ]:
            for i in range(count):
                case = cases[i % len(cases)].copy()
                case["id"] = f"legal_test_{len(test_cases)}"
                test_cases.append(case)

        return test_cases

    def _create_integration_test_cases(self) -> list[dict]:
        """Criar casos de teste de integração (múltiplas tarefas)"""

        test_cases = []

        # Casos complexos que testam múltiplas dimensões
        complex_cases = [
            {
                "text": "Contratação emergencial de empresa de fachada para obra superfaturada sem projeto básico, com pagamento antecipado integral.",
                "expected_anomaly": 2,
                "expected_risk": 4,
                "expected_compliance": 0,
                "case_type": "multi_violation",
                "complexity": "high",
            },
            {
                "text": "Pregão eletrônico bem conduzido para aquisição de equipamentos com preços de mercado e fornecedor idôneo.",
                "expected_anomaly": 0,
                "expected_risk": 1,
                "expected_compliance": 1,
                "case_type": "exemplary_process",
                "complexity": "low",
            },
        ]

        # Criar 40 casos de integração
        for i in range(40):
            case = complex_cases[i % len(complex_cases)].copy()
            case["id"] = f"integration_test_{i}"
            test_cases.append(case)

        return test_cases

    def _load_baseline_results(self):
        """Carregar resultados de baseline para comparação"""

        baseline_path = Path(self.config.output_dir) / "baselines.json"

        if baseline_path.exists():
            with open(baseline_path) as f:
                self.baseline_results = json_utils.load(f)
            logger.info("📋 Baselines carregados para comparação")
        else:
            # Definir baselines teóricos
            self.baseline_results = {
                "random_classifier": {"accuracy": 0.33, "f1": 0.25},
                "rule_based_system": {"accuracy": 0.65, "f1": 0.60},
                "basic_ml_model": {"accuracy": 0.75, "f1": 0.70},
            }
            logger.info("📋 Usando baselines teóricos")

    async def run_full_benchmark(
        self, model: CidadaoAIForTransparency
    ) -> BenchmarkResults:
        """Executar benchmark completo"""

        logger.info(f"🚀 Iniciando benchmark {self.config.benchmark_name}")
        start_time = datetime.now()

        # Resultados por tarefa
        task_results = {}

        # Executar cada tarefa
        for task_name in self.config.tasks:
            logger.info(f"🎯 Executando benchmark para: {task_name}")

            if task_name not in self.test_datasets:
                logger.warning(f"⚠️ Dataset não encontrado para {task_name}")
                continue

            task_metrics = await self._benchmark_task(model, task_name)
            task_results[task_name] = task_metrics

            logger.info(f"✅ {task_name} concluído - F1: {task_metrics.f1_score:.3f}")

        # Calcular métricas agregadas
        overall_metrics = self._calculate_overall_metrics(task_results)

        # Calcular score de transparência
        transparency_score = self._calculate_transparency_score(task_results)

        # Comparar com baselines
        baseline_comparison = self._compare_with_baselines(overall_metrics)

        # Criar resultado final
        results = BenchmarkResults(
            benchmark_name=self.config.benchmark_name,
            model_name="Cidadão.AI",
            timestamp=start_time.isoformat(),
            task_metrics=task_results,
            overall_accuracy=overall_metrics["accuracy"],
            overall_f1=overall_metrics["f1"],
            average_confidence=overall_metrics["confidence"],
            average_processing_time=overall_metrics["processing_time"],
            transparency_score=transparency_score["overall"],
            corruption_detection_ability=transparency_score["corruption_detection"],
            legal_compliance_understanding=transparency_score["legal_understanding"],
            financial_risk_assessment=transparency_score["financial_assessment"],
            compared_to_baselines=baseline_comparison["comparisons"],
            improvement_over_baseline=baseline_comparison["improvement"],
        )

        # Salvar resultados
        await self._save_benchmark_results(results)

        # Gerar relatório
        self._generate_benchmark_report(results)

        total_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"🎉 Benchmark concluído em {total_time:.1f}s")

        return results

    async def _benchmark_task(
        self, model: CidadaoAIForTransparency, task_name: str
    ) -> TaskMetrics:
        """Executar benchmark para uma tarefa específica"""

        test_data = self.test_datasets[task_name]
        predictions = []
        ground_truth = []
        confidence_scores = []
        processing_times = []

        # Criar manager para API
        manager = CidadaoAIManager()
        manager.model = model
        manager.loaded = True

        # Processar cada exemplo
        for i, test_case in enumerate(test_data):
            if i % 50 == 0:
                logger.info(f"  Processando {i}/{len(test_data)} exemplos")

            try:
                start_time = time.time()

                # Preparar request
                request = TransparencyAnalysisRequest(
                    text=test_case["text"],
                    analysis_type=self._get_analysis_type_for_task(task_name),
                )

                # Executar análise
                result = await manager.analyze_transparency(request)

                processing_time = time.time() - start_time
                processing_times.append(processing_time)

                # Extrair predições baseadas na tarefa
                pred, confidence = self._extract_prediction_for_task(result, task_name)
                predictions.append(pred)
                confidence_scores.append(confidence)

                # Extrair ground truth
                truth = self._extract_ground_truth_for_task(test_case, task_name)
                ground_truth.append(truth)

            except Exception as e:
                logger.error(f"❌ Erro no exemplo {i}: {e}")
                # Usar valores padrão para continuar
                predictions.append(0)
                ground_truth.append(
                    test_case.get(f"expected_{task_name.split('_')[0]}", 0)
                )
                confidence_scores.append(0.5)
                processing_times.append(self.config.time_limit_per_sample)

        # Calcular métricas
        metrics = self._calculate_task_metrics(
            predictions, ground_truth, confidence_scores, processing_times, task_name
        )

        return metrics

    def _get_analysis_type_for_task(self, task_name: str) -> str:
        """Mapear nome da tarefa para tipo de análise"""

        mapping = {
            "anomaly_detection": "anomaly",
            "financial_analysis": "financial",
            "legal_compliance": "legal",
            "integration": "complete",
        }

        return mapping.get(task_name, "complete")

    def _extract_prediction_for_task(
        self, result: Any, task_name: str
    ) -> tuple[int, float]:
        """Extrair predição e confiança para tarefa específica"""

        if task_name == "anomaly_detection":
            if result.anomaly_detection:
                pred_map = {"Normal": 0, "Suspeito": 1, "Anômalo": 2}
                predictions = result.anomaly_detection["predictions"]
                if predictions:
                    anomaly_type = predictions[0]["anomaly_type"]
                    confidence = predictions[0]["confidence"]
                    return pred_map.get(anomaly_type, 0), confidence
            return 0, 0.5

        if task_name == "financial_analysis":
            if result.financial_analysis:
                predictions = result.financial_analysis["predictions"]
                if predictions:
                    risk_map = {
                        "Muito Baixo": 0,
                        "Baixo": 1,
                        "Médio": 2,
                        "Alto": 3,
                        "Muito Alto": 4,
                    }
                    risk_level = predictions[0]["risk_level"]
                    return risk_map.get(risk_level, 2), 0.8
            return 2, 0.5

        if task_name == "legal_compliance":
            if result.legal_compliance:
                predictions = result.legal_compliance["predictions"]
                if predictions:
                    is_compliant = predictions[0]["is_compliant"]
                    confidence = predictions[0]["compliance_confidence"]
                    return int(is_compliant), confidence
            return 1, 0.5

        if task_name == "integration":
            # Para integração, usar anomalia como proxy
            return self._extract_prediction_for_task(result, "anomaly_detection")

        return 0, 0.5

    def _extract_ground_truth_for_task(self, test_case: dict, task_name: str) -> int:
        """Extrair ground truth para tarefa específica"""

        key_mapping = {
            "anomaly_detection": "expected_anomaly",
            "financial_analysis": "expected_risk",
            "legal_compliance": "expected_compliance",
            "integration": "expected_anomaly",
        }

        key = key_mapping.get(task_name, "expected_anomaly")
        return test_case.get(key, 0)

    def _calculate_task_metrics(
        self,
        predictions: list[int],
        ground_truth: list[int],
        confidence_scores: list[float],
        processing_times: list[float],
        task_name: str,
    ) -> TaskMetrics:
        """Calcular métricas para uma tarefa"""

        # Métricas básicas
        accuracy = accuracy_score(ground_truth, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            ground_truth, predictions, average="weighted", zero_division=0
        )

        # AUC score (apenas para tarefas binárias)
        auc_score = None
        if len(set(ground_truth)) == 2:
            try:
                auc_score = roc_auc_score(ground_truth, confidence_scores)
            except:
                auc_score = None

        # Métricas específicas de transparência
        anomaly_detection_rate = None
        false_positive_rate = None

        if task_name == "anomaly_detection":
            # Taxa de detecção de anomalias
            true_anomalies = sum(1 for gt in ground_truth if gt > 0)
            detected_anomalies = sum(
                1
                for gt, pred in zip(ground_truth, predictions, strict=False)
                if gt > 0 and pred > 0
            )

            if true_anomalies > 0:
                anomaly_detection_rate = detected_anomalies / true_anomalies

            # Taxa de falsos positivos
            true_normals = sum(1 for gt in ground_truth if gt == 0)
            false_positives = sum(
                1
                for gt, pred in zip(ground_truth, predictions, strict=False)
                if gt == 0 and pred > 0
            )

            if true_normals > 0:
                false_positive_rate = false_positives / true_normals

        metrics = TaskMetrics(
            task_name=task_name,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            auc_score=auc_score,
            confidence_score=np.mean(confidence_scores),
            processing_time=np.mean(processing_times),
            sample_count=len(predictions),
            anomaly_detection_rate=anomaly_detection_rate,
            false_positive_rate=false_positive_rate,
        )

        return metrics

    def _calculate_overall_metrics(
        self, task_results: dict[str, TaskMetrics]
    ) -> dict[str, float]:
        """Calcular métricas agregadas"""

        if not task_results:
            return {
                "accuracy": 0.0,
                "f1": 0.0,
                "confidence": 0.0,
                "processing_time": 0.0,
            }

        # Média ponderada por número de amostras
        total_samples = sum(metrics.sample_count for metrics in task_results.values())

        if total_samples == 0:
            return {
                "accuracy": 0.0,
                "f1": 0.0,
                "confidence": 0.0,
                "processing_time": 0.0,
            }

        weighted_accuracy = (
            sum(
                metrics.accuracy * metrics.sample_count
                for metrics in task_results.values()
            )
            / total_samples
        )

        weighted_f1 = (
            sum(
                metrics.f1_score * metrics.sample_count
                for metrics in task_results.values()
            )
            / total_samples
        )

        avg_confidence = sum(
            metrics.confidence_score for metrics in task_results.values()
        ) / len(task_results)

        avg_processing_time = sum(
            metrics.processing_time for metrics in task_results.values()
        ) / len(task_results)

        return {
            "accuracy": weighted_accuracy,
            "f1": weighted_f1,
            "confidence": avg_confidence,
            "processing_time": avg_processing_time,
        }

    def _calculate_transparency_score(
        self, task_results: dict[str, TaskMetrics]
    ) -> dict[str, float]:
        """Calcular score específico de transparência"""

        scores = {}

        # Score de detecção de corrupção
        if "anomaly_detection" in task_results:
            anomaly_metrics = task_results["anomaly_detection"]
            corruption_score = (
                anomaly_metrics.f1_score * 0.4
                + anomaly_metrics.recall * 0.4
                + (1 - (anomaly_metrics.false_positive_rate or 0)) * 0.2
            )
            scores["corruption_detection"] = corruption_score
        else:
            scores["corruption_detection"] = 0.0

        # Score de compreensão legal
        if "legal_compliance" in task_results:
            legal_metrics = task_results["legal_compliance"]
            legal_score = legal_metrics.accuracy * 0.5 + legal_metrics.f1_score * 0.5
            scores["legal_understanding"] = legal_score
        else:
            scores["legal_understanding"] = 0.0

        # Score de avaliação financeira
        if "financial_analysis" in task_results:
            financial_metrics = task_results["financial_analysis"]
            financial_score = (
                financial_metrics.accuracy * 0.6
                + financial_metrics.confidence_score * 0.4
            )
            scores["financial_assessment"] = financial_score
        else:
            scores["financial_assessment"] = 0.0

        # Score geral de transparência
        scores["overall"] = np.mean(list(scores.values()))

        return scores

    def _compare_with_baselines(
        self, overall_metrics: dict[str, float]
    ) -> dict[str, Any]:
        """Comparar com baselines"""

        comparisons = {}
        improvements = []

        current_f1 = overall_metrics["f1"]

        for baseline_name, baseline_metrics in self.baseline_results.items():
            baseline_f1 = baseline_metrics.get("f1", 0.0)
            improvement = (current_f1 - baseline_f1) / max(baseline_f1, 0.01) * 100

            comparisons[baseline_name] = {
                "baseline_f1": baseline_f1,
                "current_f1": current_f1,
                "improvement_percent": improvement,
            }

            improvements.append(improvement)

        avg_improvement = np.mean(improvements) if improvements else 0.0

        return {"comparisons": comparisons, "improvement": avg_improvement}

    async def _save_benchmark_results(self, results: BenchmarkResults):
        """Salvar resultados do benchmark"""

        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Salvar resultados completos
        results_path = (
            output_dir / f"benchmark_results_{results.timestamp.replace(':', '-')}.json"
        )

        # Converter TaskMetrics para dict
        results_dict = asdict(results)

        with open(results_path, "w", encoding="utf-8") as f:
            json_utils.dump(results_dict, f, ensure_ascii=False, indent=2)

        logger.info(f"💾 Resultados salvos em {results_path}")

    def _generate_benchmark_report(self, results: BenchmarkResults):
        """Gerar relatório do benchmark"""

        report_lines = []

        # Cabeçalho
        report_lines.append(f"# 📊 {results.benchmark_name} - Relatório de Avaliação")
        report_lines.append(f"**Modelo**: {results.model_name}")
        report_lines.append(f"**Data**: {results.timestamp}")
        report_lines.append("")

        # Resumo executivo
        report_lines.append("## 🎯 Resumo Executivo")
        report_lines.append(f"- **Accuracy Geral**: {results.overall_accuracy:.1%}")
        report_lines.append(f"- **F1 Score Geral**: {results.overall_f1:.1%}")
        report_lines.append(
            f"- **Score de Transparência**: {results.transparency_score:.1%}"
        )
        report_lines.append(
            f"- **Tempo Médio de Processamento**: {results.average_processing_time:.2f}s"
        )
        report_lines.append("")

        # Métricas por tarefa
        report_lines.append("## 📋 Métricas por Tarefa")

        for task_name, metrics in results.task_metrics.items():
            report_lines.append(f"### {task_name.replace('_', ' ').title()}")
            report_lines.append(f"- **Accuracy**: {metrics.accuracy:.1%}")
            report_lines.append(f"- **Precision**: {metrics.precision:.1%}")
            report_lines.append(f"- **Recall**: {metrics.recall:.1%}")
            report_lines.append(f"- **F1 Score**: {metrics.f1_score:.1%}")
            report_lines.append(
                f"- **Confiança Média**: {metrics.confidence_score:.1%}"
            )
            report_lines.append(f"- **Amostras Testadas**: {metrics.sample_count}")

            if metrics.anomaly_detection_rate is not None:
                report_lines.append(
                    f"- **Taxa de Detecção de Anomalias**: {metrics.anomaly_detection_rate:.1%}"
                )

            if metrics.false_positive_rate is not None:
                report_lines.append(
                    f"- **Taxa de Falsos Positivos**: {metrics.false_positive_rate:.1%}"
                )

            report_lines.append("")

        # Comparação com baselines
        if results.compared_to_baselines:
            report_lines.append("## 📈 Comparação com Baselines")

            for baseline_name, comparison in results.compared_to_baselines.items():
                improvement = comparison["improvement_percent"]
                status = "📈" if improvement > 0 else "📉"
                report_lines.append(
                    f"- **{baseline_name}**: {status} {improvement:+.1f}%"
                )

            report_lines.append("")

        # Análise de performance específica
        report_lines.append("## 🔍 Análise Específica de Transparência")
        report_lines.append(
            f"- **Capacidade de Detecção de Corrupção**: {results.corruption_detection_ability:.1%}"
        )
        report_lines.append(
            f"- **Compreensão de Conformidade Legal**: {results.legal_compliance_understanding:.1%}"
        )
        report_lines.append(
            f"- **Avaliação de Risco Financeiro**: {results.financial_risk_assessment:.1%}"
        )
        report_lines.append("")

        # Recomendações
        report_lines.append("## 💡 Recomendações")

        if results.overall_f1 > 0.8:
            report_lines.append(
                "✅ **Excelente**: Modelo demonstra alta capacidade para análise de transparência"
            )
        elif results.overall_f1 > 0.7:
            report_lines.append(
                "👍 **Bom**: Modelo adequado para uso em produção com monitoramento"
            )
        elif results.overall_f1 > 0.6:
            report_lines.append(
                "⚠️ **Moderado**: Recomenda-se melhorias antes do uso em produção"
            )
        else:
            report_lines.append(
                "❌ **Inadequado**: Modelo necessita retreinamento significativo"
            )

        if results.corruption_detection_ability < 0.7:
            report_lines.append(
                "- Melhorar capacidade de detecção de corrupção com mais dados de treinamento"
            )

        if results.average_processing_time > 5.0:
            report_lines.append(
                "- Otimizar velocidade de processamento para uso em tempo real"
            )

        # Salvar relatório
        output_dir = Path(self.config.output_dir)
        report_path = output_dir / "benchmark_report.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        logger.info(f"📄 Relatório salvo em {report_path}")

    def generate_comparison_plots(self, results: BenchmarkResults):
        """Gerar gráficos de comparação"""

        if not self.config.generate_plots:
            return

        output_dir = Path(self.config.output_dir) / "plots"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Configurar estilo
        plt.style.use("seaborn-v0_8")
        sns.set_palette("husl")

        # 1. Gráfico de métricas por tarefa
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Accuracy por tarefa
        tasks = list(results.task_metrics.keys())
        accuracies = [results.task_metrics[task].accuracy for task in tasks]

        axes[0, 0].bar(tasks, accuracies)
        axes[0, 0].set_title("Accuracy por Tarefa")
        axes[0, 0].set_ylabel("Accuracy")
        axes[0, 0].tick_params(axis="x", rotation=45)

        # F1 Score por tarefa
        f1_scores = [results.task_metrics[task].f1_score for task in tasks]

        axes[0, 1].bar(tasks, f1_scores, color="orange")
        axes[0, 1].set_title("F1 Score por Tarefa")
        axes[0, 1].set_ylabel("F1 Score")
        axes[0, 1].tick_params(axis="x", rotation=45)

        # Tempo de processamento
        processing_times = [
            results.task_metrics[task].processing_time for task in tasks
        ]

        axes[1, 0].bar(tasks, processing_times, color="green")
        axes[1, 0].set_title("Tempo de Processamento por Tarefa")
        axes[1, 0].set_ylabel("Tempo (s)")
        axes[1, 0].tick_params(axis="x", rotation=45)

        # Score de transparência
        transparency_scores = [
            results.corruption_detection_ability,
            results.legal_compliance_understanding,
            results.financial_risk_assessment,
        ]
        transparency_labels = [
            "Detecção\nCorrupção",
            "Conformidade\nLegal",
            "Risco\nFinanceiro",
        ]

        axes[1, 1].bar(transparency_labels, transparency_scores, color="red")
        axes[1, 1].set_title("Scores de Transparência")
        axes[1, 1].set_ylabel("Score")

        plt.tight_layout()
        plt.savefig(output_dir / "task_metrics.png", dpi=300, bbox_inches="tight")
        plt.close()

        # 2. Gráfico de comparação com baselines
        if results.compared_to_baselines:
            fig, ax = plt.subplots(figsize=(12, 8))

            baseline_names = list(results.compared_to_baselines.keys())
            current_f1s = [
                results.compared_to_baselines[name]["current_f1"]
                for name in baseline_names
            ]
            baseline_f1s = [
                results.compared_to_baselines[name]["baseline_f1"]
                for name in baseline_names
            ]

            x = np.arange(len(baseline_names))
            width = 0.35

            ax.bar(x - width / 2, baseline_f1s, width, label="Baseline", alpha=0.7)
            ax.bar(x + width / 2, current_f1s, width, label="Cidadão.AI", alpha=0.7)

            ax.set_xlabel("Modelos")
            ax.set_ylabel("F1 Score")
            ax.set_title("Comparação com Baselines")
            ax.set_xticks(x)
            ax.set_xticklabels(baseline_names)
            ax.legend()

            plt.tight_layout()
            plt.savefig(
                output_dir / "baseline_comparison.png", dpi=300, bbox_inches="tight"
            )
            plt.close()

        logger.info(f"📊 Gráficos salvos em {output_dir}")


async def run_transparency_benchmark(
    model_path: str | None = None, config: BenchmarkConfig | None = None
) -> BenchmarkResults:
    """
    Executar benchmark completo de transparência

    Args:
        model_path: Caminho para modelo treinado
        config: Configuração do benchmark

    Returns:
        Resultados do benchmark
    """

    if config is None:
        config = BenchmarkConfig()

    logger.info("🚀 Iniciando TransparenciaBench-BR")

    # Carregar modelo
    if model_path:
        model = CidadaoAIForTransparency.load_model(model_path)
    else:
        from .cidadao_model import create_cidadao_model

        model = create_cidadao_model(["all"], "medium")

    # Criar suite de benchmark
    benchmark_suite = TransparencyBenchmarkSuite(config)

    # Executar benchmark
    results = await benchmark_suite.run_full_benchmark(model)

    # Gerar plots
    benchmark_suite.generate_comparison_plots(results)

    logger.info("🎉 TransparenciaBench-BR concluído!")

    return results


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    # Executar benchmark
    config = BenchmarkConfig(
        max_samples_per_task=50,  # Reduzido para teste
        output_dir="./benchmark_results_test",
    )

    results = asyncio.run(run_transparency_benchmark(config=config))

    print("🎯 Resultados do Benchmark:")
    print(f"📊 Score de Transparência: {results.transparency_score:.1%}")
    print(f"🎯 F1 Score Geral: {results.overall_f1:.1%}")
    print(f"🚀 Detecção de Corrupção: {results.corruption_detection_ability:.1%}")
