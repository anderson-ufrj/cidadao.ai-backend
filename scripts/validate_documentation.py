#!/usr/bin/env python3
"""
Documentation Validation Script
Validates that documentation is in sync with actual codebase.

Usage:
    python scripts/validate_documentation.py

Returns:
    0 if all validations pass
    1 if any validation fails
"""

import re
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class DocumentationValidator:
    """Validates documentation against actual code."""

    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.success_count = 0

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Starting Documentation Validation\n")
        print("=" * 70)

        # Run all validators
        self.validate_agent_count()
        self.validate_test_file_count()
        self.validate_lines_of_code()
        self.validate_agent_tests()
        self.validate_endpoint_count()

        # Print results
        print("\n" + "=" * 70)
        print(f"\n✅ Passed: {self.success_count}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")

        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")

        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  ❌ {error}")
            return False

        print("\n🎉 All documentation validations passed!")
        return True

    def validate_agent_count(self):
        """Validate that agent count in docs matches actual files."""
        print("\n📊 Validating Agent Count...")

        # Count agent files
        agents_dir = self.root / "src" / "agents"
        agent_files = list(agents_dir.glob("*.py"))

        # Exclude base framework and utility files
        excluded = {
            "__init__.py",
            "__init__lazy.py",
            "deodoro.py",  # Base framework
            "agent_pool_interface.py",  # Utility
            "simple_agent_pool.py",  # Utility
            "parallel_processor.py",  # Utility
            "metrics_wrapper.py",  # Utility
            "drummond_simple.py",  # Lightweight version (documented as utility)
            "zumbi_wrapper.py",  # Utility wrapper
        }
        operational_agents = [f for f in agent_files if f.name not in excluded]

        actual_count = len(operational_agents)
        total_files = len(agent_files)

        # Check README.md
        readme = (self.root / "README.md").read_text()
        readme_match = re.search(r"Agents-(\d+)_Operational", readme)

        if readme_match:
            doc_count = int(readme_match.group(1))
            if doc_count == actual_count:
                print(f"  ✅ README.md: {doc_count} operational agents (correct)")
                self.success_count += 1
            else:
                self.errors.append(
                    f"README.md shows {doc_count} agents, but found {actual_count} operational agents"
                )
        else:
            self.warnings.append("Could not find agent count badge in README.md")

        # Check CLAUDE.md (optional - may be gitignored)
        claude_path = self.root / "CLAUDE.md"
        if claude_path.exists():
            claude_md = claude_path.read_text()
            claude_match = re.search(r"(\d+) agents total", claude_md)

            if claude_match:
                doc_total = int(claude_match.group(1))
                expected_total = actual_count + 1  # +1 for deodoro (base framework)

                if doc_total == expected_total:
                    print(f"  ✅ CLAUDE.md: {doc_total} total agent files (correct)")
                    self.success_count += 1
                else:
                    self.warnings.append(
                        f"CLAUDE.md shows {doc_total} total agents, expected {expected_total}"
                    )
        else:
            print("  ℹ️  CLAUDE.md not found (gitignored) - skipping validation")

        print(
            f"  📁 Found: {actual_count} operational + 1 base + {total_files - actual_count - 1} utilities"
        )

    def validate_test_file_count(self):
        """Validate test file count."""
        print("\n🧪 Validating Test File Count...")

        # Count test files
        tests_dir = self.root / "tests"
        test_files = list(tests_dir.rglob("test_*.py"))
        actual_count = len(test_files)

        # Check README.md
        readme = (self.root / "README.md").read_text()
        readme_match = re.search(r"(\d+) test files", readme)

        if readme_match:
            doc_count = int(readme_match.group(1))
            if doc_count == actual_count:
                print(f"  ✅ README.md: {doc_count} test files (correct)")
                self.success_count += 1
            else:
                self.errors.append(
                    f"README.md shows {doc_count} test files, but found {actual_count}"
                )
        else:
            self.warnings.append("Could not find test file count in README.md")

        print(f"  📁 Found: {actual_count} test files")

    def validate_lines_of_code(self):
        """Validate lines of code count."""
        print("\n📏 Validating Lines of Code...")

        # Count lines in agent files
        agents_dir = self.root / "src" / "agents"
        total_lines = 0

        for agent_file in agents_dir.glob("*.py"):
            lines = len(agent_file.read_text().splitlines())
            total_lines += lines

        # Check README.md
        readme = (self.root / "README.md").read_text()
        readme_match = re.search(r"Code-~([\d.]+)k_lines", readme)

        if readme_match:
            doc_lines_k = float(readme_match.group(1))
            actual_lines_k = total_lines / 1000

            # Allow 5% tolerance
            tolerance = doc_lines_k * 0.05
            if abs(doc_lines_k - actual_lines_k) <= tolerance:
                print(
                    f"  ✅ README.md: ~{doc_lines_k}k lines (actual: {actual_lines_k:.1f}k)"
                )
                self.success_count += 1
            else:
                self.errors.append(
                    f"README.md shows ~{doc_lines_k}k lines, but found {actual_lines_k:.1f}k (>{tolerance:.1f}k difference)"
                )
        else:
            self.warnings.append("Could not find lines of code count in README.md")

        print(f"  📁 Found: {total_lines:,} lines ({total_lines/1000:.1f}k)")

    def validate_agent_tests(self):
        """Validate that all agents have tests."""
        print("\n🧪 Validating Agent Test Coverage...")

        # Get operational agents (exclude utilities)
        agents_dir = self.root / "src" / "agents"
        excluded = {
            "__init__.py",
            "__init__lazy.py",
            "deodoro.py",  # Base framework
            "agent_pool_interface.py",  # Utility
            "simple_agent_pool.py",  # Utility
            "parallel_processor.py",  # Utility
            "metrics_wrapper.py",  # Utility
            "drummond_simple.py",  # Lightweight version
            "zumbi_wrapper.py",  # Utility wrapper
        }
        agent_files = [
            f.stem for f in agents_dir.glob("*.py") if f.name not in excluded
        ]

        # Get test files
        tests_dir = self.root / "tests" / "unit" / "agents"
        test_files = [f.stem.replace("test_", "") for f in tests_dir.glob("test_*.py")]

        # Find agents without tests
        agents_without_tests = set(agent_files) - set(test_files)

        if not agents_without_tests:
            print(f"  ✅ All {len(agent_files)} agents have tests")
            self.success_count += 1
        else:
            missing_list = ", ".join(sorted(agents_without_tests))
            self.errors.append(
                f"{len(agents_without_tests)} agents missing tests: {missing_list}"
            )
            print(
                f"  ❌ {len(agents_without_tests)}/{len(agent_files)} agents missing tests"
            )

        coverage_pct = (
            (len(agent_files) - len(agents_without_tests)) / len(agent_files) * 100
        )
        print(
            f"  📊 Coverage: {len(agent_files) - len(agents_without_tests)}/{len(agent_files)} ({coverage_pct:.1f}%)"
        )

    def validate_endpoint_count(self):
        """Validate endpoint count by loading FastAPI app."""
        print("\n🌐 Validating Endpoint Count...")

        try:
            # Import FastAPI app
            from src.api.app import app

            # Count endpoints
            endpoint_count = len(
                [route for route in app.routes if hasattr(route, "methods")]
            )

            # Check README.md
            readme = (self.root / "README.md").read_text()
            readme_match = re.search(r"(\d+) endpoints", readme)

            if readme_match:
                doc_count = int(readme_match.group(1))

                # Allow 10% tolerance (endpoints may change frequently)
                tolerance = doc_count * 0.1
                if abs(doc_count - endpoint_count) <= tolerance:
                    print(
                        f"  ✅ README.md: {doc_count} endpoints (actual: {endpoint_count})"
                    )
                    self.success_count += 1
                else:
                    self.warnings.append(
                        f"README.md shows {doc_count} endpoints, but found {endpoint_count} (difference: {abs(doc_count - endpoint_count)})"
                    )
            else:
                self.warnings.append("Could not find endpoint count in README.md")

            print(f"  📁 Found: {endpoint_count} endpoints")

        except Exception as e:
            self.warnings.append(f"Could not validate endpoint count: {str(e)}")


def main():
    """Main entry point."""
    validator = DocumentationValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
