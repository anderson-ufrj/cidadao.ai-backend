#!/usr/bin/env python3
"""
Endpoint Analysis Script
Analyzes all API endpoints to identify redundancy, inconsistencies, and issues.
"""

import os
import re
from collections import defaultdict
from pathlib import Path


class EndpointAnalyzer:
    def __init__(self, routes_dir: str):
        self.routes_dir = Path(routes_dir)
        self.endpoints: dict[str, list[dict]] = defaultdict(list)
        self.routes_by_file: dict[str, list[dict]] = defaultdict(list)
        self.prefixes_by_file: dict[str, str] = {}

    def extract_router_prefix(self, content: str, filename: str) -> str:
        """Extract router prefix from file content."""
        # Look for: router = APIRouter(prefix="/something")
        prefix_match = re.search(
            r'router\s*=\s*APIRouter\s*\(\s*prefix\s*=\s*["\']([^"\']+)["\']', content
        )
        if prefix_match:
            return prefix_match.group(1)
        return ""

    def extract_endpoints_from_file(self, filepath: Path) -> list[dict]:
        """Extract all endpoint decorators from a Python file."""
        try:
            with open(filepath) as f:
                content = f.read()

            # Extract router prefix
            prefix = self.extract_router_prefix(content, filepath.name)
            self.prefixes_by_file[filepath.name] = prefix

            endpoints = []

            # Regex patterns for different decorator styles
            patterns = [
                # @router.get("/path")
                r'@router\.(get|post|put|delete|patch|websocket)\s*\(\s*["\']([^"\']+)["\']',
                # @router.api_route("/path", methods=["GET"])
                r'@router\.api_route\s*\(\s*["\']([^"\']+)["\'].*methods\s*=\s*\[([^\]]+)\]',
            ]

            for pattern in patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    if pattern == patterns[0]:  # Standard decorator
                        method = match.group(1).upper()
                        path = match.group(2)
                    else:  # api_route
                        path = match.group(1)
                        methods = (
                            match.group(2).replace('"', "").replace("'", "").split(",")
                        )
                        for method in methods:
                            method = method.strip()
                            endpoints.append(
                                {
                                    "file": filepath.name,
                                    "method": method,
                                    "path": path,
                                    "prefix": prefix,
                                    "full_path": (
                                        prefix + path if path != "/" else prefix or "/"
                                    ),
                                }
                            )
                        continue

                    endpoints.append(
                        {
                            "file": filepath.name,
                            "method": method,
                            "path": path,
                            "prefix": prefix,
                            "full_path": (
                                prefix + path if path != "/" else prefix or "/"
                            ),
                        }
                    )

            return endpoints

        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            return []

    def analyze(self) -> None:
        """Analyze all route files."""
        route_files = list(self.routes_dir.glob("*.py"))

        for filepath in route_files:
            if filepath.name in ["__init__.py", "__pycache__"]:
                continue

            endpoints = self.extract_endpoints_from_file(filepath)
            self.routes_by_file[filepath.name] = endpoints

            for endpoint in endpoints:
                key = f"{endpoint['method']} {endpoint['full_path']}"
                self.endpoints[key].append(endpoint)

    def find_duplicates(self) -> list[tuple[str, list[dict]]]:
        """Find duplicate endpoints (same method + path)."""
        duplicates = []
        for key, endpoints in self.endpoints.items():
            if len(endpoints) > 1:
                duplicates.append((key, endpoints))
        return duplicates

    def find_similar_routes(self) -> list[tuple[str, str, float]]:
        """Find suspiciously similar route files."""

        similar = []
        files = list(self.routes_by_file.keys())

        for i, file1 in enumerate(files):
            for file2 in files[i + 1 :]:
                # Compare endpoint sets
                set1 = {
                    f"{e['method']} {e['path']}" for e in self.routes_by_file[file1]
                }
                set2 = {
                    f"{e['method']} {e['path']}" for e in self.routes_by_file[file2]
                }

                if set1 and set2:
                    intersection = set1 & set2
                    union = set1 | set2
                    similarity = len(intersection) / len(union) if union else 0

                    if similarity > 0.5:  # 50% similarity threshold
                        similar.append((file1, file2, similarity))

        return similar

    def find_inconsistent_patterns(self) -> dict[str, list[str]]:
        """Find endpoints that don't follow REST conventions."""
        issues = defaultdict(list)

        for key, endpoints in self.endpoints.items():
            endpoint = endpoints[0]  # Just check first one
            method = endpoint["method"]
            path = endpoint["full_path"]

            # Check for inconsistent naming
            if method in ["POST", "PUT", "PATCH"] and path.endswith("s"):
                issues["plural_in_mutation"].append(f"{method} {path}")

            # Check for verbs in paths (should use HTTP methods instead)
            verbs = [
                "create",
                "update",
                "delete",
                "get",
                "fetch",
                "list",
                "search",
                "find",
            ]
            path_lower = path.lower()
            for verb in verbs:
                if verb in path_lower:
                    issues["verb_in_path"].append(f"{method} {path}")
                    break

            # Check for missing API version
            if not path.startswith("/api/v"):
                issues["missing_version"].append(f"{method} {path}")

        return issues

    def generate_report(self) -> str:
        """Generate comprehensive analysis report."""
        report = []
        report.append("=" * 80)
        report.append("API ENDPOINT ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")

        # Summary
        total_files = len(self.routes_by_file)
        total_endpoints = sum(len(self.endpoints[key]) for key in self.endpoints)
        unique_endpoints = len(self.endpoints)

        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Total route files: {total_files}")
        report.append(f"Total endpoint definitions: {total_endpoints}")
        report.append(f"Unique endpoints: {unique_endpoints}")
        report.append(f"Duplicate definitions: {total_endpoints - unique_endpoints}")
        report.append("")

        # Duplicates
        duplicates = self.find_duplicates()
        if duplicates:
            report.append("DUPLICATE ENDPOINTS (CRITICAL)")
            report.append("-" * 80)
            for key, endpoints in duplicates:
                report.append(f"\n{key}")
                for ep in endpoints:
                    report.append(f"  - {ep['file']} (prefix: '{ep['prefix']}')")
            report.append("")

        # Similar files
        similar = self.find_similar_routes()
        if similar:
            report.append("SIMILAR/REDUNDANT ROUTE FILES")
            report.append("-" * 80)
            for file1, file2, similarity in sorted(
                similar, key=lambda x: x[2], reverse=True
            ):
                report.append(f"{file1} ↔ {file2}: {similarity*100:.1f}% similar")
            report.append("")

        # Pattern inconsistencies
        issues = self.find_inconsistent_patterns()
        if issues:
            report.append("PATTERN INCONSISTENCIES")
            report.append("-" * 80)

            if issues["verb_in_path"]:
                report.append("\nVerbs in paths (should use HTTP methods):")
                for path in sorted(set(issues["verb_in_path"]))[:10]:
                    report.append(f"  - {path}")

            if issues["missing_version"]:
                report.append("\nMissing API version prefix:")
                for path in sorted(set(issues["missing_version"]))[:10]:
                    report.append(f"  - {path}")
            report.append("")

        # All endpoints by file
        report.append("ENDPOINTS BY FILE")
        report.append("-" * 80)
        for filename in sorted(self.routes_by_file.keys()):
            endpoints = self.routes_by_file[filename]
            if endpoints:
                report.append(f"\n{filename} ({len(endpoints)} endpoints)")
                prefix = self.prefixes_by_file.get(filename, "")
                if prefix:
                    report.append(f"  Router prefix: {prefix}")
                for ep in sorted(endpoints, key=lambda x: (x["method"], x["path"])):
                    report.append(f"  {ep['method']:8} {ep['full_path']}")

        return "\n".join(report)


if __name__ == "__main__":
    analyzer = EndpointAnalyzer("src/api/routes")
    analyzer.analyze()

    report = analyzer.generate_report()
    print(report)

    # Save to file
    output_file = "docs/project/reports/endpoint_analysis.txt"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        f.write(report)

    print(f"\n\n✅ Report saved to: {output_file}")
