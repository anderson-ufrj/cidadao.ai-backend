#!/usr/bin/env python3
"""
Update Agent Line Counts in Documentation
Author: Anderson Henrique da Silva
Date: 2025-10-31
"""

import re
from pathlib import Path


def get_actual_line_counts():
    """Get actual line counts from agent files."""
    agents_dir = Path("src/agents")
    line_counts = {}

    for agent_file in agents_dir.glob("*.py"):
        if "__" not in agent_file.name and agent_file.name != "__init__.py":
            lines = len(agent_file.read_text().splitlines())
            line_counts[agent_file.stem] = lines

    return line_counts


def update_readme():
    """Update the agent README with correct line counts."""
    readme_path = Path("docs/agents/README.md")

    if not readme_path.exists():
        print(f"Error: {readme_path} not found")
        return

    content = readme_path.read_text()
    line_counts = get_actual_line_counts()

    # Update existing agents
    for agent, actual_lines in line_counts.items():
        # Pattern: **Arquivo**: `src/agents/agent.py` (X linhas)
        pattern = rf"(\*\*Arquivo\*\*:\s*`src/agents/{agent}\.py`\s*\()([0-9,\.]+)(\s*linhas?\))"
        replacement = rf"\g<1>{actual_lines:,}\g<3>"
        content = re.sub(pattern, replacement, content)

    # Add missing agents section
    documented_agents = set(re.findall(r"src/agents/(\w+)\.py", content))
    missing_agents = (
        set(line_counts.keys())
        - documented_agents
        - {
            "deodoro",
            "agent_pool_interface",
            "metrics_wrapper",
            "parallel_processor",
            "simple_agent_pool",
        }
    )

    if missing_agents:
        # Add section for undocumented agents
        missing_section = "\n\n## 📝 Agents Pending Documentation\n\n"
        for agent in sorted(missing_agents):
            missing_section += f"### {agent.replace('_', ' ').title()}\n"
            missing_section += f"**Status**: ⚠️ **Documentation Pending**\n"
            missing_section += (
                f"**File**: `src/agents/{agent}.py` ({line_counts[agent]:,} lines)\n"
            )
            missing_section += (
                f"**Tests**: Check `tests/unit/agents/test_{agent}.py`\n\n"
            )

        # Insert before the statistics section
        stats_pattern = r"(## 📊 Resumo Estatístico)"
        if re.search(stats_pattern, content):
            content = re.sub(stats_pattern, missing_section + r"\1", content)

    # Update test file count
    test_dir = Path("tests/unit/agents")
    test_count = len(list(test_dir.glob("test_*.py")))
    content = re.sub(
        r"(\*\*Com Testes Completos\*\*\s*\|\s*)(\d+)", rf"\g<1>{test_count}", content
    )

    # Write updated content
    readme_path.write_text(content)
    print(f"Updated {readme_path}")

    return line_counts, missing_agents


def main():
    """Main execution."""
    print("Updating agent line counts in documentation...")

    line_counts, missing = update_readme()

    print(f"\nUpdated line counts for {len(line_counts)} agents")
    if missing:
        print(f"\nAdded documentation placeholders for:")
        for agent in sorted(missing):
            print(f"  - {agent}: {line_counts[agent]:,} lines")

    print("\n✅ Documentation updated successfully!")


if __name__ == "__main__":
    main()
