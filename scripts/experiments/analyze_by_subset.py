#!/usr/bin/env python3
"""
Per-subset accuracy breakdown for the routing experiment (SBCARS 2026).

Re-runs the dataset through both conditions and reports accuracy split by query
`source` (keyword_rich / paraphrase_nokw / adversarial / conversational). This
is the key anti-bias evidence: if the LLM advantage holds on paraphrase_nokw and
adversarial (where the keyword baseline cannot rely on lexical triggers), the
gain is real rather than an artifact of author-written keyword-friendly queries.

Usage:
    JWT_SECRET_KEY=test SECRET_KEY=test \
    MARITACA_API_KEY=... ANTHROPIC_API_KEY=... \
      python scripts/experiments/analyze_by_subset.py \
        --dataset scripts/experiments/data/routing_eval.full.csv \
        --out /tmp/routing_subset.json

Author: Anderson Henrique da Silva
Created: 2026-05-31
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))


async def main_async(args) -> int:
    from src.services.orchestration.query_planner.intent_classifier import (
        IntentClassifier,
    )

    rows = list(csv.DictReader(open(args.dataset, encoding="utf-8")))

    # intent only (cheapest signal; agent stage adds little to the bias argument)
    kw = IntentClassifier(keyword_only=True)
    llm = IntentClassifier(keyword_only=False)

    # tally[source][condition] = [correct, total]
    tally: dict[str, dict[str, list[int]]] = defaultdict(
        lambda: {"keyword": [0, 0], "llm": [0, 0]}
    )

    for r in rows:
        q, gold, src = r["query"], r["gold_intent"], r["source"]

        rk = await kw.classify(q)
        pk = getattr(rk.get("intent"), "value", rk.get("intent"))
        tally[src]["keyword"][1] += 1
        tally[src]["keyword"][0] += int(str(pk) == gold)

        rl = await llm.classify(q)
        pl = getattr(rl.get("intent"), "value", rl.get("intent"))
        tally[src]["llm"][1] += 1
        tally[src]["llm"][0] += int(str(pl) == gold)

    out = {}
    print(f"{'subset':18s} {'keyword':>10s} {'llm':>10s} {'n':>4s}")
    for src in ("keyword_rich", "paraphrase_nokw", "adversarial", "conversational"):
        if src not in tally:
            continue
        kc, kt = tally[src]["keyword"]
        lc, lt = tally[src]["llm"]
        ka = kc / kt if kt else 0.0
        la = lc / lt if lt else 0.0
        out[src] = {"keyword_acc": round(ka, 3), "llm_acc": round(la, 3), "n": kt}
        print(f"{src:18s} {ka:>10.3f} {la:>10.3f} {kt:>4d}")

    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\nWrote {args.out}")
    return 0


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--out", default="/tmp/routing_subset.json")
    return p.parse_args()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main_async(parse_args())))
