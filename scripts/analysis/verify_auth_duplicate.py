#!/usr/bin/env python3
"""
Verify duplicate authentication implementation.
"""

import difflib


def compare_files(file1_path: str, file2_path: str) -> dict:
    """Compare two files and show differences."""

    with open(file1_path) as f1:
        lines1 = f1.readlines()

    with open(file2_path) as f2:
        lines2 = f2.readlines()

    # Calculate similarity
    matcher = difflib.SequenceMatcher(None, lines1, lines2)
    similarity = matcher.ratio() * 100

    # Get differences
    diff = list(difflib.unified_diff(lines1, lines2, lineterm=""))

    return {
        "file1": file1_path,
        "file2": file2_path,
        "similarity": similarity,
        "diff_lines": len([d for d in diff if d.startswith("+") or d.startswith("-")]),
        "total_lines_1": len(lines1),
        "total_lines_2": len(lines2),
    }


if __name__ == "__main__":
    auth_py = "src/api/routes/auth.py"
    auth_db_py = "src/api/routes/auth_db.py"

    print("=" * 80)
    print("AUTHENTICATION DUPLICATION ANALYSIS")
    print("=" * 80)
    print()

    result = compare_files(auth_py, auth_db_py)

    print(f"File 1: {result['file1']}")
    print(f"  Lines: {result['total_lines_1']}")
    print()
    print(f"File 2: {result['file2']}")
    print(f"  Lines: {result['total_lines_2']}")
    print()
    print(f"Similarity: {result['similarity']:.2f}%")
    print(f"Different lines: {result['diff_lines']}")
    print()

    # Read and compare endpoints
    print("ENDPOINT COMPARISON")
    print("-" * 80)

    import re

    def extract_endpoints(filepath):
        """Extract endpoints from file."""
        with open(filepath) as f:
            content = f.read()

        endpoints = []
        pattern = r"@router\.(get|post|put|delete|patch)\([\"']([^\"']+)[\"']"

        for match in re.finditer(pattern, content):
            method = match.group(1).upper()
            path = match.group(2)
            endpoints.append(f"{method:6} {path}")

        return endpoints

    endpoints_1 = extract_endpoints(auth_py)
    endpoints_2 = extract_endpoints(auth_db_py)

    print(f"\n{auth_py}:")
    for ep in sorted(endpoints_1):
        print(f"  {ep}")

    print(f"\n{auth_db_py}:")
    for ep in sorted(endpoints_2):
        print(f"  {ep}")

    # Check for identical endpoints
    set1 = set(endpoints_1)
    set2 = set(endpoints_2)

    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)

    if set1 == set2:
        print("✅ CONFIRMED: Both files have IDENTICAL endpoints")
        print(f"   Total endpoints: {len(set1)}")
    else:
        print("⚠️  Endpoints differ:")
        only_1 = set1 - set2
        only_2 = set2 - set1

        if only_1:
            print(f"\n  Only in {auth_py}:")
            for ep in sorted(only_1):
                print(f"    {ep}")

        if only_2:
            print(f"\n  Only in {auth_db_py}:")
            for ep in sorted(only_2):
                print(f"    {ep}")

    # Key differences
    print("\n" + "=" * 80)
    print("KEY DIFFERENCES")
    print("=" * 80)

    print(f"\n{auth_py}:")
    print("  - Uses in-memory auth manager (src/api/auth.py)")
    print("  - Prefix: /api/v1/auth")
    print("  - Synchronous operations")
    print("  - No token revocation on logout")

    print(f"\n{auth_db_py}:")
    print("  - Uses database-backed auth manager (src/api/auth_db.py)")
    print("  - Prefix: /auth (INCONSISTENT - missing /api/v1)")
    print("  - Async/await operations")
    print("  - Token revocation on logout")

    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print("\n❌ DELETE: src/api/routes/auth.py")
    print("✅ KEEP:   src/api/routes/auth_db.py")
    print("\n⚠️  REQUIRED CHANGE:")
    print("   Update auth_db.py router prefix from '/auth' to '/api/v1/auth'")
    print()
