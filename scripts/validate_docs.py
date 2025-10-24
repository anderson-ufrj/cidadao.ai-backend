#!/usr/bin/env python3
"""
Validate documentation claims against codebase reality.

This script checks key metrics mentioned in documentation and compares
them against actual codebase state to identify documentation drift.

Usage:
    python scripts/validate_docs.py
    python scripts/validate_docs.py --json  # JSON output
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class DocumentationValidator:
    """Validates documentation claims against codebase."""

    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.results: dict[str, Any] = {}
        self.failures = 0

    def count_agents(self) -> int:
        """Count actual agent files (excluding base classes and utilities)."""
        agents_dir = self.root / "src" / "agents"
        if not agents_dir.exists():
            return 0

        excludes = {
            "__init__",
            "deodoro",
            "agent_pool",
            "simple_agent_pool",
            "parallel_processor",
            "metrics_wrapper",
            "zumbi_wrapper",
            "agent_pool_interface",
            "drummond_simple",
        }

        agents = [f.stem for f in agents_dir.glob("*.py") if f.stem not in excludes]
        return len(agents)

    def count_test_files(self) -> int:
        """Count agent test files."""
        test_dir = self.root / "tests" / "unit" / "agents"
        if not test_dir.exists():
            return 0
        return len(list(test_dir.glob("test_*.py")))

    def count_route_files(self) -> int:
        """Count API route modules."""
        routes_dir = self.root / "src" / "api" / "routes"
        if not routes_dir.exists():
            return 0
        return len([f for f in routes_dir.glob("*.py") if f.name != "__init__.py"])

    def count_documented_agents(self) -> int:
        """Count agent documentation files."""
        docs_dir = self.root / "docs" / "agents"
        if not docs_dir.exists():
            return 0

        excludes = {"README", "INVENTORY", "OXOSSI", "example"}
        docs = [
            f.stem
            for f in docs_dir.glob("*.md")
            if not any(excl in f.stem for excl in excludes)
        ]
        return len(docs)

    def check_api_key_configured(self) -> bool:
        """Check if TRANSPARENCY_API_KEY is in .env file."""
        env_file = self.root / ".env"
        if not env_file.exists():
            return False

        with open(env_file) as f:
            for line in f:
                if line.startswith("TRANSPARENCY_API_KEY="):
                    value = line.split("=", 1)[1].strip()
                    return bool(value) and value != ""
        return False

    def check_entry_point(self) -> dict[str, bool]:
        """Check app entry points."""
        return {
            "root_app_py_exists": (self.root / "app.py").exists(),
            "src_api_app_py_exists": (self.root / "src" / "api" / "app.py").exists(),
        }

    def validate_all(self) -> dict[str, Any]:
        """Run all validation checks."""
        self.results = {"validation_date": "2025-10-24", "checks": {}}

        # Agent count
        agent_count = self.count_agents()
        self.results["checks"]["agent_count"] = {
            "actual": agent_count,
            "expected": 16,
            "status": "✅" if agent_count == 16 else "❌",
            "pass": agent_count == 16,
        }
        if agent_count != 16:
            self.failures += 1

        # Test files
        test_count = self.count_test_files()
        self.results["checks"]["test_files"] = {
            "actual": test_count,
            "documented": 24,
            "status": "✅" if test_count >= 24 else "❌",
            "pass": test_count >= 24,
            "note": "Actual is better than documented" if test_count > 24 else None,
        }
        if test_count < 24:
            self.failures += 1

        # Route files
        route_count = self.count_route_files()
        self.results["checks"]["route_modules"] = {
            "actual": route_count,
            "documented": 36,
            "status": "✅" if route_count == 36 else "⚠️",
            "pass": route_count == 36,
            "note": (
                "Count matches documentation"
                if route_count == 36
                else f"Expected 36, found {route_count}"
            ),
        }
        # Not a failure if close
        if abs(route_count - 36) > 5:
            self.failures += 1

        # Documented agents
        doc_count = self.count_documented_agents()
        self.results["checks"]["documented_agents"] = {
            "actual": doc_count,
            "expected": 16,
            "status": "✅" if doc_count >= 16 else "⚠️",
            "pass": doc_count >= 16,
        }

        # API key
        has_key = self.check_api_key_configured()
        self.results["checks"]["transparency_api_key"] = {
            "configured": has_key,
            "status": "✅" if has_key else "⚠️",
            "pass": has_key,
            "note": "Demo mode active" if not has_key else "Real data enabled",
        }

        # Entry points
        entry_points = self.check_entry_point()
        correct_entry = (
            not entry_points["root_app_py_exists"]
            and entry_points["src_api_app_py_exists"]
        )
        self.results["checks"]["entry_point"] = {
            "root_app_py_absent": not entry_points["root_app_py_exists"],
            "src_api_app_py_present": entry_points["src_api_app_py_exists"],
            "status": "✅" if correct_entry else "❌",
            "pass": correct_entry,
        }
        if not correct_entry:
            self.failures += 1

        # Overall status
        self.results["overall_status"] = "PASS" if self.failures == 0 else "FAIL"
        self.results["failures"] = self.failures

        return self.results

    def print_results(self):
        """Print validation results in human-readable format."""
        print("\n" + "=" * 70)
        print("📋 DOCUMENTATION VALIDATION REPORT")
        print("=" * 70 + "\n")

        checks = self.results["checks"]

        print("1. AGENT COUNT")
        ac = checks["agent_count"]
        print(f"   {ac['status']} Actual: {ac['actual']} | Expected: {ac['expected']}")

        print("\n2. TEST FILES")
        tf = checks["test_files"]
        print(
            f"   {tf['status']} Actual: {tf['actual']} | Documented: {tf['documented']}"
        )
        if tf.get("note"):
            print(f"   💡 {tf['note']}")

        print("\n3. ROUTE MODULES")
        rm = checks["route_modules"]
        print(
            f"   {rm['status']} Actual: {rm['actual']} | Documented: {rm['documented']}"
        )

        print("\n4. DOCUMENTED AGENTS")
        da = checks["documented_agents"]
        print(f"   {da['status']} Actual: {da['actual']} | Expected: {da['expected']}")

        print("\n5. TRANSPARENCY API KEY")
        tk = checks["transparency_api_key"]
        print(f"   {tk['status']} Configured: {tk['configured']}")
        print(f"   💡 {tk['note']}")

        print("\n6. ENTRY POINT")
        ep = checks["entry_point"]
        print(f"   {ep['status']} Root app.py absent: {ep['root_app_py_absent']}")
        print(
            f"   {ep['status']} src/api/app.py present: {ep['src_api_app_py_present']}"
        )

        print("\n" + "=" * 70)
        print(f"OVERALL: {self.results['overall_status']}")
        print(f"Failures: {self.failures}")
        print("=" * 70 + "\n")

        if self.failures > 0:
            print("⚠️  Documentation validation FAILED!")
            print("📝 See docs/project/DOCUMENTATION_AUDIT_2025_10_24.md for details\n")
            return 1

        print("✅ Documentation validation PASSED!\n")
        return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate documentation against codebase"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    validator = DocumentationValidator()
    results = validator.validate_all()

    if args.json:
        print(json.dumps(results, indent=2))
        return 0 if results["overall_status"] == "PASS" else 1

    return validator.print_results()


if __name__ == "__main__":
    sys.exit(main())
