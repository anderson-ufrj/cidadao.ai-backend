#!/usr/bin/env python3
"""
Build the routing-evaluation dataset (SBCARS 2026).

Emits a labeled CSV of Portuguese queries spanning the twelve intent classes
and five target agents used by Cidadao.AI. The dataset is deliberately diverse
to control for *authorship bias*: each intent is covered by four query styles so
that the LLM advantage can be measured on queries that do NOT contain the
trigger keywords the rule-based baseline relies on.

Query styles (the `source` column):
  - keyword_rich   : contains the lexical triggers the keyword baseline expects
  - paraphrase_nokw: same intent, trigger keywords deliberately avoided
  - adversarial    : ambiguous / mixed-intent / indirect phrasing
  - conversational : greetings, thanks, goodbye, help, about-system

Gold labels are assigned by INTENT (what the query means), independently of
what the current classifier/router actually returns. Agent mapping follows the
documented responsibility split:
  investigation-type intents      -> InvestigatorAgent
  analysis-type intents           -> AnalystAgent
  report-phrased requests         -> ReporterAgent
  conversational / general / help -> MasterAgent

Deterministic: no randomness, no timestamps. Same input -> same CSV.

Usage:
    python scripts/experiments/build_routing_dataset.py \
        --out scripts/experiments/data/routing_eval.full.csv

Author: Anderson Henrique da Silva
Created: 2026-05-31
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

# Agent constants (must match SemanticRouter targets)
INVESTIGATOR = "InvestigatorAgent"
ANALYST = "AnalystAgent"
REPORTER = "ReporterAgent"
MASTER = "MasterAgent"

# Each entry: (query, gold_intent, gold_agent, source)
# Curated by hand for naturalness and diversity. Kept in code (not a loose CSV)
# so the artifact is reproducible and reviewable.
ROWS: list[tuple[str, str, str, str]] = []


def add(query: str, intent: str, agent: str, source: str) -> None:
    ROWS.append((query.strip(), intent, agent, source))


# ============================================================
# 1. contract_anomaly_detection  -> InvestigatorAgent
# ============================================================
# keyword_rich
add("Contratos de saúde acima de R$ 1 milhão em 2025", "contract_anomaly_detection", INVESTIGATOR, "keyword_rich")
add("Verificar licitações suspeitas da Secretaria de Educação", "contract_anomaly_detection", INVESTIGATOR, "keyword_rich")
add("Analisar contratos com valores irregulares acima de R$ 500 mil", "contract_anomaly_detection", INVESTIGATOR, "keyword_rich")
add("Auditar despesas suspeitas em contratos do município", "contract_anomaly_detection", INVESTIGATOR, "keyword_rich")
add("Investigar contratos superfaturados na prefeitura", "contract_anomaly_detection", INVESTIGATOR, "keyword_rich")
# paraphrase_nokw (avoid contrato/licitação/suspeito/valor)
add("Tem algo estranho nos maiores pagamentos da prefeitura ano passado?", "contract_anomaly_detection", INVESTIGATOR, "paraphrase_nokw")
add("Alguma compra do governo que fuja totalmente do padrão dos demais?", "contract_anomaly_detection", INVESTIGATOR, "paraphrase_nokw")
add("Quais acordos firmados pelo órgão destoam dos preços de mercado?", "contract_anomaly_detection", INVESTIGATOR, "paraphrase_nokw")
add("Existe alguma aquisição pública que pareça fora da curva?", "contract_anomaly_detection", INVESTIGATOR, "paraphrase_nokw")
# adversarial
add("Por que aquele acordo da saúde de 2024 foi tão mais caro que os outros?", "contract_anomaly_detection", INVESTIGATOR, "adversarial")
add("Me mostra onde o dinheiro do município parece ter sido mal gasto", "contract_anomaly_detection", INVESTIGATOR, "adversarial")

# ============================================================
# 2. supplier_investigation  -> InvestigatorAgent
# ============================================================
add("CNPJ 12.345.678/0001-90 recebeu quanto do governo federal?", "supplier_investigation", INVESTIGATOR, "keyword_rich")
add("Investigar o fornecedor Construtora Alfa Ltda", "supplier_investigation", INVESTIGATOR, "keyword_rich")
add("Quanto ganha o servidor João da Silva Pereira?", "supplier_investigation", INVESTIGATOR, "keyword_rich")
add("Qual a remuneração do funcionário público Carlos Andrade?", "supplier_investigation", INVESTIGATOR, "keyword_rich")
add("Salário do professor da rede federal Antônio Souza", "supplier_investigation", INVESTIGATOR, "keyword_rich")
# paraphrase_nokw
add("Essa empresa de construção fechou muitos negócios com o estado?", "supplier_investigation", INVESTIGATOR, "paraphrase_nokw")
add("Quanto a Construtora Alfa já faturou com dinheiro público?", "supplier_investigation", INVESTIGATOR, "paraphrase_nokw")
add("Quero saber tudo sobre quem fornece merenda pra rede municipal", "supplier_investigation", INVESTIGATOR, "paraphrase_nokw")
add("Aquela empreiteira aparece em quantos acordos com a administração?", "supplier_investigation", INVESTIGATOR, "paraphrase_nokw")
# adversarial
add("Tem uma empresa só que vence tudo aqui na minha cidade, dá pra ver?", "supplier_investigation", INVESTIGATOR, "adversarial")
add("Quem é que tá por trás dos maiores recebimentos do órgão?", "supplier_investigation", INVESTIGATOR, "adversarial")

# ============================================================
# 3. corruption_indicators  -> InvestigatorAgent
# ============================================================
add("Detectar fraudes em licitações da área de obras", "corruption_indicators", INVESTIGATOR, "keyword_rich")
add("Identificar indícios de corrupção nos contratos de 2024", "corruption_indicators", INVESTIGATOR, "keyword_rich")
add("Padrões de irregularidades em pagamentos municipais", "corruption_indicators", INVESTIGATOR, "keyword_rich")
add("Sinais de fraude e desvio de recursos na secretaria", "corruption_indicators", INVESTIGATOR, "keyword_rich")
# paraphrase_nokw
add("Dá pra notar algum esquema nos repasses pra essas ONGs?", "corruption_indicators", INVESTIGATOR, "paraphrase_nokw")
add("Algum sinal de que andaram desviando verba pública por aqui?", "corruption_indicators", INVESTIGATOR, "paraphrase_nokw")
add("Existe combinação entre as empresas que disputam as obras?", "corruption_indicators", INVESTIGATOR, "paraphrase_nokw")
add("Parece que tem cartel nas compras do hospital, confere isso", "corruption_indicators", INVESTIGATOR, "paraphrase_nokw")
# adversarial
add("Será que esse monte de aditivo no mesmo contrato é normal?", "corruption_indicators", INVESTIGATOR, "adversarial")
add("Por que sempre os mesmos ganham e os preços só sobem?", "corruption_indicators", INVESTIGATOR, "adversarial")

# ============================================================
# 4. budget_analysis  -> AnalystAgent
# ============================================================
add("Como está distribuído o orçamento da educação municipal?", "budget_analysis", ANALYST, "keyword_rich")
add("Análise dos gastos do município por área em 2025", "budget_analysis", ANALYST, "keyword_rich")
add("Distribuição do orçamento federal entre os ministérios", "budget_analysis", ANALYST, "keyword_rich")
add("Quanto do orçamento foi para infraestrutura este ano?", "budget_analysis", ANALYST, "keyword_rich")
add("Compare os gastos de 2023 e 2024 ao longo do tempo", "budget_analysis", ANALYST, "keyword_rich")
# paraphrase_nokw
add("Pra onde foi a maior parte do dinheiro da cidade no ano passado?", "budget_analysis", ANALYST, "paraphrase_nokw")
add("Como o estado repartiu os recursos entre as áreas?", "budget_analysis", ANALYST, "paraphrase_nokw")
add("Em que o governo mais aplicou recursos recentemente?", "budget_analysis", ANALYST, "paraphrase_nokw")
add("A fatia destinada à cultura cresceu ou caiu nos últimos anos?", "budget_analysis", ANALYST, "paraphrase_nokw")
# adversarial
add("A prefeitura prioriza mais asfalto ou escola, em números?", "budget_analysis", ANALYST, "adversarial")
add("Me dá um panorama de pra onde vai a grana pública daqui", "budget_analysis", ANALYST, "adversarial")

# ============================================================
# 5. health_budget_analysis  -> AnalystAgent
# ============================================================
add("Qual a verba do SUS para hospitais este ano?", "health_budget_analysis", ANALYST, "keyword_rich")
add("Investimento em saúde pública no município em 2025", "health_budget_analysis", ANALYST, "keyword_rich")
add("Gastos com hospitais e postos de saúde da rede federal", "health_budget_analysis", ANALYST, "keyword_rich")
add("Orçamento da saúde por região do país", "health_budget_analysis", ANALYST, "keyword_rich")
# paraphrase_nokw
add("Quanto a cidade reservou pra atender quem precisa de médico?", "health_budget_analysis", ANALYST, "paraphrase_nokw")
add("O dinheiro destinado aos postos aumentou depois da pandemia?", "health_budget_analysis", ANALYST, "paraphrase_nokw")
add("Quanto foi aplicado em remédios e vacinas pela rede pública?", "health_budget_analysis", ANALYST, "paraphrase_nokw")
# adversarial
add("Minha cidade cuida bem do hospital ou investe pouco nisso?", "health_budget_analysis", ANALYST, "adversarial")
add("Tem mais grana indo pra UTI ou pra atenção básica?", "health_budget_analysis", ANALYST, "adversarial")

# ============================================================
# 6. education_performance  -> AnalystAgent
# ============================================================
add("Desempenho das escolas no ENEM por região", "education_performance", ANALYST, "keyword_rich")
add("Resultado do IDEB das escolas municipais", "education_performance", ANALYST, "keyword_rich")
add("Qualidade do ensino na rede pública estadual", "education_performance", ANALYST, "keyword_rich")
add("Notas das escolas federais no último exame nacional", "education_performance", ANALYST, "keyword_rich")
# paraphrase_nokw
add("As escolas daqui vão bem nas avaliações nacionais?", "education_performance", ANALYST, "paraphrase_nokw")
add("Os alunos da rede pública aprendem mais que antes?", "education_performance", ANALYST, "paraphrase_nokw")
add("Como anda o aprendizado nas escolas do meu estado?", "education_performance", ANALYST, "paraphrase_nokw")
# adversarial
add("Vale a pena botar meu filho na escola pública daqui, pelos números?", "education_performance", ANALYST, "adversarial")
add("Onde os estudantes se saem melhor, no litoral ou no interior?", "education_performance", ANALYST, "adversarial")

# ============================================================
# 7. (report-phrased)  -> ReporterAgent
#    Intent stays contract_anomaly_detection but the user asks for a REPORT,
#    which should route to the reporter. Tests agent-routing disambiguation.
# ============================================================
add("Gere um relatório dos contratos suspeitos do Ministério da Saúde", "contract_anomaly_detection", REPORTER, "adversarial")
add("Monte um resumo em PDF das licitações irregulares de 2024", "contract_anomaly_detection", REPORTER, "adversarial")
add("Quero um documento consolidando os achados sobre o fornecedor X", "supplier_investigation", REPORTER, "adversarial")
add("Produza um relatório das anomalias encontradas nos gastos", "contract_anomaly_detection", REPORTER, "adversarial")
add("Exporta um resumo dos indícios de fraude para eu apresentar", "corruption_indicators", REPORTER, "adversarial")

# ============================================================
# 8. general_query  -> MasterAgent
# ============================================================
add("Como funciona a busca de dados?", "general_query", MASTER, "keyword_rich")
add("Quais dados eu consigo consultar aqui?", "general_query", MASTER, "keyword_rich")
add("De onde vêm as informações que você usa?", "general_query", MASTER, "paraphrase_nokw")
add("Posso confiar nos números que aparecem?", "general_query", MASTER, "paraphrase_nokw")
add("Que tipo de pergunta eu posso fazer?", "general_query", MASTER, "paraphrase_nokw")
add("Isso aqui cobre dados de qualquer cidade do Brasil?", "general_query", MASTER, "adversarial")

# ============================================================
# 9-13. conversational  -> MasterAgent
# ============================================================
# greeting
add("Olá, tudo bem?", "greeting", MASTER, "conversational")
add("Oi, bom dia!", "greeting", MASTER, "conversational")
add("E aí, beleza?", "greeting", MASTER, "conversational")
add("Boa tarde, tudo certo?", "greeting", MASTER, "conversational")
# thanks
add("Obrigado pela ajuda!", "thanks", MASTER, "conversational")
add("Valeu, muito bom!", "thanks", MASTER, "conversational")
add("Agradeço demais pela explicação", "thanks", MASTER, "conversational")
# goodbye
add("Tchau, até logo", "goodbye", MASTER, "conversational")
add("Falou, até a próxima", "goodbye", MASTER, "conversational")
add("Adeus, obrigado por tudo", "goodbye", MASTER, "conversational")
# help_request
add("Preciso de ajuda, não sei como usar", "help_request", MASTER, "conversational")
add("Pode me ajudar a começar?", "help_request", MASTER, "conversational")
add("Não entendi como faço pra pesquisar", "help_request", MASTER, "conversational")
# about_system
add("O que é o Cidadão.AI?", "about_system", MASTER, "conversational")
add("Quem criou esse sistema?", "about_system", MASTER, "conversational")
add("Para que serve essa ferramenta?", "about_system", MASTER, "conversational")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build routing-eval dataset")
    parser.add_argument(
        "--out",
        default="scripts/experiments/data/routing_eval.full.csv",
        help="output CSV path",
    )
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    # integrity checks before writing
    seen = set()
    dups = [q for q, *_ in ROWS if (q in seen or seen.add(q))]
    if dups:
        raise SystemExit(f"Duplicate queries found: {dups[:5]}")

    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["query", "gold_intent", "gold_agent", "source", "notes"])
        for query, intent, agent, source in ROWS:
            w.writerow([query, intent, agent, source, ""])

    # distribution report
    from collections import Counter

    by_intent = Counter(r[1] for r in ROWS)
    by_agent = Counter(r[2] for r in ROWS)
    by_source = Counter(r[3] for r in ROWS)
    print(f"Wrote {len(ROWS)} rows to {out}")
    print("By intent:", dict(by_intent))
    print("By agent :", dict(by_agent))
    print("By source:", dict(by_source))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
