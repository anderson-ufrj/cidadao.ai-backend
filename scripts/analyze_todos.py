#!/usr/bin/env python3
"""
Script para analisar e categorizar todos os TODOs/FIXMEs no código.
"""

import json
import os
import re
from collections import defaultdict
from pathlib import Path


def find_todos(root_dir: str) -> dict[str, list[tuple[int, str, str]]]:
    """
    Encontra todos os TODOs/FIXMEs no código.
    Retorna: Dict[arquivo, List[(linha, tipo, conteúdo)]]
    """
    todos = defaultdict(list)
    patterns = re.compile(
        r"(TODO|FIXME|XXX|HACK|BUG|REFACTOR)[:|\s](.*)$", re.IGNORECASE
    )

    # Diretórios para ignorar
    ignore_dirs = {
        "venv",
        "__pycache__",
        ".git",
        "node_modules",
        "htmlcov",
        ".pytest_cache",
    }

    for root, dirs, files in os.walk(root_dir):
        # Remove diretórios ignorados
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            # Apenas arquivos Python e Markdown
            if not (file.endswith(".py") or file.endswith(".md")):
                continue

            filepath = os.path.join(root, file)
            relative_path = os.path.relpath(filepath, root_dir)

            try:
                with open(filepath, encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        match = patterns.search(line)
                        if match:
                            todo_type = match.group(1).upper()
                            todo_content = match.group(2).strip()
                            todos[relative_path].append(
                                (line_num, todo_type, todo_content)
                            )
            except Exception as e:
                print(f"Erro ao ler {filepath}: {e}")

    return dict(todos)


def categorize_todos(todos: dict[str, list[tuple[int, str, str]]]) -> dict[str, dict]:
    """
    Categoriza TODOs por tipo e prioridade.
    """
    categories = {
        "security": [],  # Segurança crítica
        "auth": [],  # Autenticação/autorização
        "api": [],  # APIs externas
        "database": [],  # Banco de dados
        "performance": [],  # Performance/otimização
        "testing": [],  # Testes
        "documentation": [],  # Documentação
        "agent": [],  # Agentes AI
        "ml": [],  # Machine Learning
        "infrastructure": [],  # Infra/DevOps
        "feature": [],  # Features incompletas
        "refactor": [],  # Refatoração necessária
        "bug": [],  # Bugs conhecidos
        "other": [],  # Outros
    }

    # Palavras-chave para categorização
    keywords = {
        "security": [
            "security",
            "secure",
            "vulnerability",
            "csrf",
            "xss",
            "sql",
            "injection",
            "encrypt",
        ],
        "auth": ["auth", "jwt", "token", "login", "permission", "role", "user"],
        "api": ["api", "endpoint", "route", "portal", "transparência", "external"],
        "database": [
            "database",
            "db",
            "sql",
            "postgres",
            "redis",
            "migration",
            "cache",
        ],
        "performance": [
            "performance",
            "optimize",
            "slow",
            "speed",
            "fast",
            "cache",
            "lazy",
        ],
        "testing": ["test", "mock", "coverage", "pytest", "unit", "integration"],
        "documentation": ["doc", "readme", "comment", "explain", "description"],
        "agent": [
            "agent",
            "zumbi",
            "anita",
            "oxossi",
            "lampiao",
            "dandara",
            "reflection",
        ],
        "ml": ["ml", "machine", "learning", "model", "train", "predict", "anomaly"],
        "infrastructure": [
            "docker",
            "deploy",
            "kubernetes",
            "railway",
            "monitoring",
            "grafana",
        ],
        "feature": ["implement", "feature", "add", "create", "build", "develop"],
        "refactor": [
            "refactor",
            "cleanup",
            "improve",
            "simplify",
            "optimize",
            "rewrite",
        ],
        "bug": ["bug", "fix", "error", "issue", "problem", "broken", "fail"],
    }

    # Categorizar cada TODO
    for filepath, todo_list in todos.items():
        for line_num, todo_type, content in todo_list:
            # Determinar categoria
            category = "other"
            content_lower = content.lower()

            # Prioridade baseada no tipo
            priority = "medium"
            if todo_type in ["FIXME", "BUG"]:
                priority = "high"
            elif todo_type in ["XXX", "HACK"]:
                priority = "critical"
            elif todo_type == "REFACTOR":
                priority = "low"

            # Buscar categoria por palavras-chave
            for cat, words in keywords.items():
                if any(word in content_lower for word in words):
                    category = cat
                    break

            # Ajustar prioridade para categorias críticas
            if category in ["security", "auth", "bug"]:
                priority = "critical"
            elif category in ["api", "database", "ml"]:
                priority = "high"

            # Adicionar à categoria
            todo_item = {
                "file": filepath,
                "line": line_num,
                "type": todo_type,
                "content": content,
                "priority": priority,
            }

            categories[category].append(todo_item)

    return categories


def generate_report(categories: dict[str, list]) -> str:  # noqa: C901, PLR0912, PLR0915
    """
    Gera relatório detalhado dos TODOs.

    Note: This function is intentionally complex to generate comprehensive reports.
    """
    report = []
    report.append("# 🔍 Análise Completa de TODOs/FIXMEs - Cidadão.AI Backend")
    report.append("\n**Data**: 2025-11-21")
    report.append(
        f"**Total de TODOs**: {sum(len(items) for items in categories.values())}"
    )
    report.append("\n---\n")

    # Estatísticas por categoria
    report.append("## 📊 Estatísticas por Categoria\n")
    report.append("| Categoria | Quantidade | Prioridade |")
    report.append("|-----------|------------|------------|")

    priority_icons = {"critical": "🔴", "high": "🟡", "medium": "🟢", "low": "⚪"}

    for category, items in sorted(
        categories.items(), key=lambda x: len(x[1]), reverse=True
    ):
        if items:
            # Contar prioridades
            priorities = defaultdict(int)
            for item in items:
                priorities[item["priority"]] += 1

            priority_str = " ".join(
                f"{priority_icons[p]}{c}" for p, c in priorities.items()
            )
            report.append(
                f"| {category.capitalize()} | {len(items)} | {priority_str} |"
            )

    report.append("\n---\n")

    # TODOs críticos (top 10)
    report.append("## 🚨 TODOs Críticos (Resolver Imediatamente)\n")
    critical_todos = []
    for items in categories.values():
        critical_todos.extend([i for i in items if i["priority"] == "critical"])

    critical_todos = sorted(
        critical_todos, key=lambda x: x["type"] == "BUG", reverse=True
    )[:10]

    for i, todo in enumerate(critical_todos, 1):
        report.append(f"### {i}. [{todo['type']}] {todo['file']}:{todo['line']}")
        report.append("```")
        report.append(f"{todo['content']}")
        report.append("```\n")

    # Detalhes por categoria
    report.append("## 📋 Detalhes por Categoria\n")

    for category, items in categories.items():
        if not items:
            continue

        report.append(f"### {category.upper()} ({len(items)} items)\n")

        # Agrupar por arquivo
        by_file = defaultdict(list)
        for item in items:
            by_file[item["file"]].append(item)

        for filepath, file_items in sorted(by_file.items()):
            report.append(f"**{filepath}**")
            for item in sorted(file_items, key=lambda x: x["line"]):
                icon = priority_icons[item["priority"]]
                report.append(
                    f"- L{item['line']}: {icon} [{item['type']}] {item['content'][:100]}..."
                )
            report.append("")

    # Recomendações
    report.append("\n## 🎯 Recomendações de Ação\n")

    if categories["security"] or categories["auth"]:
        report.append("### 🔒 Segurança (PRIORIDADE MÁXIMA)")
        report.append("- [ ] Revisar e corrigir todos os TODOs de segurança")
        report.append("- [ ] Implementar autenticação/autorização pendente")
        report.append("- [ ] Re-habilitar IP whitelist em produção\n")

    if categories["bug"]:
        report.append("### 🐛 Bugs (ALTA PRIORIDADE)")
        report.append("- [ ] Corrigir todos os bugs conhecidos")
        report.append("- [ ] Adicionar testes para prevenir regressões\n")

    if categories["api"]:
        report.append("### 🔌 APIs Externas")
        report.append("- [ ] Implementar fallbacks para APIs que falham")
        report.append("- [ ] Adicionar mocks para testes de integração\n")

    if categories["testing"]:
        report.append("### 🧪 Testes")
        report.append("- [ ] Implementar testes pendentes")
        report.append("- [ ] Aumentar coverage para 80%+\n")

    if categories["agent"]:
        report.append("### 🤖 Agentes")
        report.append("- [ ] Completar implementação dos agentes Tier 2/3")
        report.append("- [ ] Adicionar testes de integração multi-agente\n")

    return "\n".join(report)


def save_json_summary(categories: dict[str, list], output_path: str):
    """
    Salva um resumo JSON para processamento posterior.
    """
    summary = {
        "total_todos": sum(len(items) for items in categories.values()),
        "by_category": {cat: len(items) for cat, items in categories.items()},
        "by_priority": {},
        "critical_files": [],
    }

    # Contar por prioridade
    priority_count = defaultdict(int)
    file_todo_count = defaultdict(int)

    for items in categories.values():
        for item in items:
            priority_count[item["priority"]] += 1
            file_todo_count[item["file"]] += 1

    summary["by_priority"] = dict(priority_count)

    # Top 10 arquivos com mais TODOs
    summary["critical_files"] = sorted(
        file_todo_count.items(), key=lambda x: x[1], reverse=True
    )[:10]

    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    return summary


def main():
    # Diretório raiz do projeto
    root_dir = Path(__file__).parent.parent

    print("🔍 Analisando TODOs/FIXMEs no projeto...")

    # Encontrar todos os TODOs
    todos = find_todos(root_dir)
    print(
        f"✅ Encontrados {sum(len(t) for t in todos.values())} TODOs em {len(todos)} arquivos"
    )

    # Categorizar
    categories = categorize_todos(todos)

    # Gerar relatório
    report = generate_report(categories)

    # Salvar relatório
    report_path = (
        root_dir / "docs" / "project" / "reports" / "TODO_ANALYSIS_2025_11_21.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        f.write(report)

    print(f"📄 Relatório salvo em: {report_path}")

    # Salvar resumo JSON
    json_path = root_dir / "docs" / "project" / "reports" / "todo_summary.json"
    summary = save_json_summary(categories, json_path)

    print(f"📊 Resumo JSON salvo em: {json_path}")

    # Imprimir resumo
    print("\n📊 RESUMO:")
    print(f"- Total de TODOs: {summary['total_todos']}")
    print(f"- Críticos: {summary['by_priority'].get('critical', 0)}")
    print(f"- Alta prioridade: {summary['by_priority'].get('high', 0)}")
    print(f"- Média prioridade: {summary['by_priority'].get('medium', 0)}")
    print(f"- Baixa prioridade: {summary['by_priority'].get('low', 0)}")

    print("\n🔥 Arquivos com mais TODOs:")
    for file, count in summary["critical_files"][:5]:
        print(f"  - {file}: {count} TODOs")


if __name__ == "__main__":
    main()
