#!/usr/bin/env python3
"""
Documentation Validation Script for Cidadão.AI Backend
Author: Anderson Henrique da Silva
Date: 2025-10-31
Purpose: Validate documentation against actual code implementation
"""

import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


class DocumentationValidator:
    """Validate documentation against code reality."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.agents_dir = self.project_root / "src" / "agents"
        self.tests_dir = self.project_root / "tests" / "unit" / "agents"
        self.docs_dir = self.project_root / "docs"

    def count_agent_lines(self) -> Dict[str, int]:
        """Count actual lines in each agent file."""
        agent_lines = {}

        if not self.agents_dir.exists():
            print(f"Error: {self.agents_dir} not found")
            return agent_lines

        for agent_file in sorted(self.agents_dir.glob("*.py")):
            if "__" not in agent_file.name and agent_file.name != "__init__.py":
                try:
                    lines = len(agent_file.read_text().splitlines())
                    agent_lines[agent_file.stem] = lines
                except Exception as e:
                    print(f"Error reading {agent_file}: {e}")

        return agent_lines

    def count_test_files(self) -> Tuple[int, List[str]]:
        """Count and list test files."""
        if not self.tests_dir.exists():
            print(f"Error: {self.tests_dir} not found")
            return 0, []

        test_files = list(self.tests_dir.glob("test_*.py"))
        test_names = [f.stem for f in test_files]
        return len(test_files), sorted(test_names)

    def extract_documented_lines(self) -> Dict[str, int]:
        """Extract line counts from documentation."""
        documented_lines = {}
        readme_path = self.docs_dir / "agents" / "README.md"

        if not readme_path.exists():
            print(f"Warning: {readme_path} not found")
            return documented_lines

        content = readme_path.read_text()

        # Pattern to match agent descriptions with line counts
        # Example: "**Arquivo**: `src/agents/zumbi.py` (1,266 linhas)"
        pattern = (
            r"\*\*Arquivo\*\*:\s*`src/agents/(\w+)\.py`\s*\(([0-9,\.]+)\s*linhas?\)"
        )

        for match in re.finditer(pattern, content):
            agent_name = match.group(1)
            lines_str = match.group(2).replace(",", "").replace(".", "")
            try:
                documented_lines[agent_name] = int(lines_str)
            except ValueError:
                print(
                    f"Warning: Could not parse line count for {agent_name}: {lines_str}"
                )

        return documented_lines

    def find_undocumented_files(self) -> List[str]:
        """Find agent files not mentioned in documentation."""
        actual_files = set(self.count_agent_lines().keys())
        documented_files = set(self.extract_documented_lines().keys())

        # Common infrastructure files that might not need individual documentation
        infrastructure_files = {
            "agent_pool_interface",
            "metrics_wrapper",
            "parallel_processor",
            "simple_agent_pool",
            "deodoro",  # Base class
        }

        undocumented = actual_files - documented_files - infrastructure_files
        return sorted(list(undocumented))

    def analyze_test_coverage(self) -> Dict[str, bool]:
        """Check which agents have tests."""
        agents = self.count_agent_lines().keys()
        _, test_files = self.count_test_files()

        coverage = {}
        for agent in agents:
            # Check if there's at least one test file for this agent
            has_test = any(f"test_{agent}" in test for test in test_files)
            coverage[agent] = has_test

        return coverage

    def find_date_stamped_files(self) -> Dict[str, List[str]]:
        """Find files with dates in their names."""
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{4}_\d{2}_\d{2}",  # YYYY_MM_DD
            r"2025-10",  # Partial dates
            r"2024",  # Year only
            r"2025",  # Year only
        ]

        dated_files = defaultdict(list)

        for pattern in date_patterns:
            for file_path in self.docs_dir.rglob("*.md"):
                if re.search(pattern, file_path.name):
                    dated_files[pattern].append(
                        str(file_path.relative_to(self.project_root))
                    )

        return dict(dated_files)

    def generate_report(self) -> str:
        """Generate comprehensive validation report."""
        report = []
        report.append("=" * 80)
        report.append("DOCUMENTATION VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")

        # Agent line counts comparison
        actual_lines = self.count_agent_lines()
        documented_lines = self.extract_documented_lines()

        report.append("## AGENT LINE COUNT VALIDATION")
        report.append("-" * 40)
        report.append(
            f"{'Agent':<20} {'Documented':<12} {'Actual':<12} {'Difference':<12}"
        )
        report.append("-" * 40)

        total_diff = 0
        for agent in sorted(set(actual_lines.keys()) | set(documented_lines.keys())):
            doc_count = documented_lines.get(agent, 0)
            actual_count = actual_lines.get(agent, 0)
            diff = actual_count - doc_count
            total_diff += abs(diff)

            if agent in actual_lines and agent in documented_lines:
                status = "✓" if diff == 0 else "⚠"
                report.append(
                    f"{agent:<20} {doc_count:<12} {actual_count:<12} {diff:+12} {status}"
                )
            elif agent in actual_lines:
                report.append(
                    f"{agent:<20} {'NOT DOCUMENTED':<12} {actual_count:<12} {'+' + str(actual_count):<12} ❌"
                )
            else:
                report.append(
                    f"{agent:<20} {doc_count:<12} {'NOT FOUND':<12} {'-' + str(doc_count):<12} ❌"
                )

        report.append("-" * 40)
        report.append(f"Total line count difference: {total_diff:,} lines")
        report.append("")

        # Test files count
        test_count, test_files = self.count_test_files()
        report.append("## TEST FILES VALIDATION")
        report.append("-" * 40)
        report.append(f"Total test files found: {test_count}")
        report.append(
            f"Test files: {', '.join(test_files[:5])}{'...' if len(test_files) > 5 else ''}"
        )
        report.append("")

        # Test coverage
        coverage = self.analyze_test_coverage()
        agents_with_tests = sum(1 for has_test in coverage.values() if has_test)
        total_agents = len(coverage)

        report.append("## TEST COVERAGE BY AGENT")
        report.append("-" * 40)
        report.append(
            f"Agents with tests: {agents_with_tests}/{total_agents} ({agents_with_tests/total_agents*100:.1f}%)"
        )
        report.append("")
        report.append("Agents WITHOUT tests:")
        for agent, has_test in sorted(coverage.items()):
            if not has_test and agent not in [
                "deodoro",
                "agent_pool_interface",
                "metrics_wrapper",
            ]:
                report.append(f"  ❌ {agent}")
        report.append("")

        # Undocumented files
        undocumented = self.find_undocumented_files()
        if undocumented:
            report.append("## UNDOCUMENTED AGENT FILES")
            report.append("-" * 40)
            for file in undocumented:
                report.append(f"  ⚠️  {file}.py")
            report.append("")

        # Date-stamped files
        dated_files = self.find_date_stamped_files()
        if dated_files:
            total_dated = sum(len(files) for files in dated_files.values())
            report.append("## DATE-STAMPED DOCUMENTATION FILES")
            report.append("-" * 40)
            report.append(f"Total files with dates: {total_dated}")
            report.append("Recommendation: Archive or rename these files")
            report.append("")

        # Summary
        report.append("## SUMMARY")
        report.append("-" * 40)

        issues = []
        if total_diff > 100:
            issues.append(
                f"⚠️  Large documentation drift: {total_diff:,} lines difference"
            )
        if agents_with_tests < total_agents * 0.8:
            issues.append(
                f"⚠️  Low test coverage: {agents_with_tests/total_agents*100:.1f}%"
            )
        if undocumented:
            issues.append(f"⚠️  {len(undocumented)} undocumented agent files")
        if dated_files:
            issues.append(
                f"⚠️  {sum(len(f) for f in dated_files.values())} date-stamped files need cleanup"
            )

        if issues:
            report.append("Issues found:")
            for issue in issues:
                report.append(f"  {issue}")
        else:
            report.append("✅ Documentation is up to date!")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    def save_json_report(self, filename: str = "documentation_validation.json"):
        """Save validation results as JSON."""
        results = {
            "agent_lines": self.count_agent_lines(),
            "documented_lines": self.extract_documented_lines(),
            "test_count": self.count_test_files()[0],
            "test_coverage": self.analyze_test_coverage(),
            "undocumented_files": self.find_undocumented_files(),
            "date_stamped_files": self.find_date_stamped_files(),
        }

        output_path = self.project_root / filename
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"JSON report saved to: {output_path}")


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate Cidadão.AI documentation")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--json", action="store_true", help="Save JSON report")
    parser.add_argument("--output", help="Output file for report")

    args = parser.parse_args()

    validator = DocumentationValidator(args.root)

    # Generate and print report
    report = validator.generate_report()
    print(report)

    # Save report if requested
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report)
        print(f"\nReport saved to: {output_path}")

    # Save JSON if requested
    if args.json:
        validator.save_json_report()

    # Return exit code based on validation results
    actual_lines = validator.count_agent_lines()
    documented_lines = validator.extract_documented_lines()
    total_diff = sum(
        abs(actual_lines.get(a, 0) - documented_lines.get(a, 0))
        for a in set(actual_lines.keys()) | set(documented_lines.keys())
    )

    if total_diff > 1000:
        print("\n⚠️  Significant documentation drift detected!")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
