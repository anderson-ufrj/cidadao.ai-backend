#!/usr/bin/env python3
"""
Routing evaluation harness — SBCARS 2026 experiment.

Measures the two-stage routing pipeline of Cidadao.AI:
  Stage 1 (intent):  IntentClassifier   — baseline=keyword-only, treatment=keyword+LLM
  Stage 2 (agent):   SemanticRouter      — baseline=rule-only,    treatment=rule+semantic

Reads a labeled CSV, runs each condition over the same queries, and emits
per-stage metrics (accuracy, macro-F1, confusion matrix) plus the fast-path vs
LLM split that ties back to the paper's latency story.

Usage:
    JWT_SECRET_KEY=test SECRET_KEY=test \\
      python scripts/experiments/routing_eval.py \\
        --dataset data/routing_eval.csv \\
        --out results/routing/ \\
        [--no-llm]   # baseline-only run, no API key / cost

Dataset CSV columns:
    query, gold_intent, gold_agent, source, notes

Author: Anderson Henrique da Silva
Created: 2026-05-31
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Make `src` importable regardless of CWD: this file lives at
# <backend>/scripts/experiments/routing_eval.py, so the backend root is two
# levels up. Prepend it so `from src...` resolves when run directly.
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))


# --------------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------------
@dataclass
class Sample:
    query: str
    gold_intent: str
    gold_agent: str
    source: str = ""
    notes: str = ""


@dataclass
class Prediction:
    query: str
    gold: str
    pred: str
    method: str  # "keyword" | "llm" | "rule" | "semantic" | "fallback"
    confidence: float
    latency_ms: float


@dataclass
class StageReport:
    name: str
    condition: str
    predictions: list[Prediction] = field(default_factory=list)

    def accuracy(self) -> float:
        if not self.predictions:
            return 0.0
        hits = sum(1 for p in self.predictions if p.pred == p.gold)
        return hits / len(self.predictions)

    def pct_via(self, method: str) -> float:
        if not self.predictions:
            return 0.0
        n = sum(1 for p in self.predictions if p.method == method)
        return n / len(self.predictions)

    def mean_latency_ms(self) -> float:
        if not self.predictions:
            return 0.0
        return sum(p.latency_ms for p in self.predictions) / len(self.predictions)


# --------------------------------------------------------------------------
# Dataset
# --------------------------------------------------------------------------
def load_dataset(path: Path) -> list[Sample]:
    samples: list[Sample] = []
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        required = {"query", "gold_intent", "gold_agent"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"CSV missing required columns: {missing}")
        for row in reader:
            q = (row.get("query") or "").strip()
            if not q:
                continue
            samples.append(
                Sample(
                    query=q,
                    gold_intent=(row.get("gold_intent") or "").strip(),
                    gold_agent=(row.get("gold_agent") or "").strip(),
                    source=(row.get("source") or "").strip(),
                    notes=(row.get("notes") or "").strip(),
                )
            )
    if not samples:
        raise SystemExit(f"No samples loaded from {path}")
    return samples


# --------------------------------------------------------------------------
# Stage 1 — Intent classification
# --------------------------------------------------------------------------
async def run_intent_stage(
    samples: list[Sample], *, use_llm: bool
) -> StageReport:
    """Run the real IntentClassifier in baseline (keyword-only) or treatment."""
    from src.services.orchestration.query_planner.intent_classifier import (
        IntentClassifier,
    )

    condition = "keyword+llm" if use_llm else "keyword-only"
    clf = IntentClassifier(keyword_only=not use_llm)
    report = StageReport(name="intent", condition=condition)

    for s in samples:
        t0 = time.perf_counter()
        result = await clf.classify(s.query)
        dt = (time.perf_counter() - t0) * 1000.0

        intent = result.get("intent")
        # InvestigationIntent enum -> its .value; conversational intents are str
        pred = getattr(intent, "value", intent)
        report.predictions.append(
            Prediction(
                query=s.query,
                gold=s.gold_intent,
                pred=str(pred),
                method=str(result.get("method", "")),
                confidence=float(result.get("confidence", 0.0)),
                latency_ms=dt,
            )
        )
    return report


# --------------------------------------------------------------------------
# Stage 2 — Agent routing
# --------------------------------------------------------------------------
async def run_agent_stage(
    samples: list[Sample], *, use_llm: bool
) -> StageReport:
    """Run the real SemanticRouter (Ayrton Senna).

    Baseline = rule-based only (we disable the semantic fallback by passing an
    LLM stub that raises, so routing falls through to rule/fallback).
    Treatment = rule + semantic LLM.
    """
    from src.agents.ayrton_senna import SemanticRouter
    from src.agents.deodoro import AgentContext

    condition = "rule+semantic" if use_llm else "rule-only"

    if use_llm:
        llm_service = _make_real_llm_service()
    else:
        llm_service = _NullLLM()  # forces rule-based / fallback path

    router = SemanticRouter(llm_service=llm_service)
    await router.initialize()

    # Register the five known target agents so validation/suggestion work.
    for agent in (
        "MasterAgent",
        "InvestigatorAgent",
        "AnalystAgent",
        "ReporterAgent",
        "ContextMemoryAgent",
    ):
        router.register_agent_capabilities(agent, ["investigate", "analyze", "report"])

    report = StageReport(name="agent", condition=condition)
    ctx = AgentContext(investigation_id="routing-eval")

    for s in samples:
        t0 = time.perf_counter()
        decision = await router.route_query(s.query, ctx)
        dt = (time.perf_counter() - t0) * 1000.0
        report.predictions.append(
            Prediction(
                query=s.query,
                gold=s.gold_agent,
                pred=str(decision.target_agent),
                method=str(decision.rule_used),
                confidence=float(decision.confidence),
                latency_ms=dt,
            )
        )

    await router.shutdown()
    return report


class _NullLLM:
    """LLM stub that always fails generation, forcing rule/fallback routing."""

    async def initialize(self) -> None:  # noqa: D401
        return None

    async def shutdown(self) -> None:
        return None

    async def generate(self, *args: Any, **kwargs: Any) -> str:
        raise RuntimeError("LLM disabled for baseline condition")


def _make_real_llm_service() -> Any:
    """Construct the production LLM client for the treatment condition."""
    from src.core.llm_client import LLMClient

    return LLMClient()


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------
def compute_metrics(report: StageReport) -> dict[str, Any]:
    golds = [p.gold for p in report.predictions]
    preds = [p.pred for p in report.predictions]
    out: dict[str, Any] = {
        "stage": report.name,
        "condition": report.condition,
        "n": len(report.predictions),
        "accuracy": round(report.accuracy(), 4),
        "mean_latency_ms": round(report.mean_latency_ms(), 2),
        "method_split": {},
    }
    methods = {p.method for p in report.predictions}
    for m in sorted(methods):
        out["method_split"][m] = round(report.pct_via(m), 4)

    # sklearn is optional — degrade gracefully if absent.
    try:
        from sklearn.metrics import (
            classification_report,
            confusion_matrix,
            f1_score,
        )

        labels = sorted(set(golds) | set(preds))
        out["macro_f1"] = round(
            f1_score(golds, preds, average="macro", labels=labels, zero_division=0),
            4,
        )
        out["per_class"] = classification_report(
            golds, preds, labels=labels, zero_division=0, output_dict=True
        )
        out["labels"] = labels
        out["confusion_matrix"] = confusion_matrix(
            golds, preds, labels=labels
        ).tolist()
    except ImportError:
        out["macro_f1"] = None
        out["note"] = "install scikit-learn for macro-F1 / confusion matrix"
    return out


def pipeline_exact_match(
    intent_rep: StageReport, agent_rep: StageReport
) -> dict[str, Any]:
    """End-to-end: fraction of queries where BOTH stages are correct."""
    by_query_intent = {p.query: (p.pred == p.gold) for p in intent_rep.predictions}
    by_query_agent = {p.query: (p.pred == p.gold) for p in agent_rep.predictions}
    common = set(by_query_intent) & set(by_query_agent)
    if not common:
        return {"n": 0, "exact_match": 0.0}
    both = sum(1 for q in common if by_query_intent[q] and by_query_agent[q])
    return {"n": len(common), "exact_match": round(both / len(common), 4)}


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
async def main_async(args: argparse.Namespace) -> int:
    samples = load_dataset(Path(args.dataset))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    conditions = [False] if args.no_llm else [False, True]
    all_metrics: list[dict[str, Any]] = []
    reports: dict[str, StageReport] = {}

    for use_llm in conditions:
        tag = "treatment" if use_llm else "baseline"
        print(f"[intent:{tag}] running {len(samples)} queries...", file=sys.stderr)
        intent_rep = await run_intent_stage(samples, use_llm=use_llm)
        print(f"[agent:{tag}] running {len(samples)} queries...", file=sys.stderr)
        agent_rep = await run_agent_stage(samples, use_llm=use_llm)

        all_metrics.append(compute_metrics(intent_rep))
        all_metrics.append(compute_metrics(agent_rep))
        reports[f"intent_{tag}"] = intent_rep
        reports[f"agent_{tag}"] = agent_rep

        # pipeline exact-match for this condition
        pm = pipeline_exact_match(intent_rep, agent_rep)
        pm.update({"condition": tag})
        all_metrics.append({"stage": "pipeline", **pm})

    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(all_metrics, indent=2, ensure_ascii=False))
    print(f"\nWrote {metrics_path}")

    # Console summary
    print("\n=== SUMMARY ===")
    for m in all_metrics:
        if m["stage"] == "pipeline":
            print(
                f"pipeline [{m.get('condition')}]: "
                f"exact-match={m['exact_match']:.3f} (n={m['n']})"
            )
        else:
            f1 = m.get("macro_f1")
            f1s = f"{f1:.3f}" if isinstance(f1, float) else "n/a"
            print(
                f"{m['stage']:7s} [{m['condition']:14s}] "
                f"acc={m['accuracy']:.3f} macroF1={f1s} "
                f"lat={m['mean_latency_ms']:.1f}ms"
            )
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Routing evaluation harness (SBCARS 2026)")
    p.add_argument("--dataset", required=True, help="path to routing_eval.csv")
    p.add_argument("--out", default="results/routing", help="output directory")
    p.add_argument(
        "--no-llm",
        action="store_true",
        help="baseline-only run (no LLM calls, no API key/cost)",
    )
    return p.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main_async(parse_args(sys.argv[1:]))))
