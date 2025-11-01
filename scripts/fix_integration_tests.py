#!/usr/bin/env python3
"""
Script to fix integration tests by adding missing @pytest.mark.asyncio decorators
and fixing other common issues.
"""

import os
import re
from pathlib import Path


def fix_async_tests(file_path):
    """Add @pytest.mark.asyncio decorator to async test functions."""
    with open(file_path, "r") as f:
        content = f.read()

    # Check if pytest is imported
    if "import pytest" not in content:
        # Add pytest import at the beginning of imports
        content = "import pytest\n" + content

    lines = content.split("\n")
    modified = False
    new_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is an async test function
        if line.strip().startswith("async def test_"):
            # Check if the previous line has @pytest.mark.asyncio
            prev_line_idx = i - 1
            while prev_line_idx >= 0 and lines[prev_line_idx].strip() == "":
                prev_line_idx -= 1

            has_asyncio_mark = False
            if prev_line_idx >= 0:
                prev_line = lines[prev_line_idx].strip()
                if "@pytest.mark.asyncio" in prev_line:
                    has_asyncio_mark = True
                # Check for other decorators
                elif prev_line.startswith("@"):
                    # Look further back for asyncio mark
                    check_idx = prev_line_idx - 1
                    while check_idx >= 0 and lines[check_idx].strip().startswith("@"):
                        if "@pytest.mark.asyncio" in lines[check_idx]:
                            has_asyncio_mark = True
                            break
                        check_idx -= 1

            if not has_asyncio_mark:
                # Get indentation
                indent = len(line) - len(line.lstrip())
                new_lines.append(" " * indent + "@pytest.mark.asyncio")
                modified = True

        new_lines.append(line)
        i += 1

    if modified:
        content = "\n".join(new_lines)
        with open(file_path, "w") as f:
            f.write(content)
        return True
    return False


def main():
    """Fix all integration test files."""
    test_dir = Path(
        "/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend/tests/integration"
    )

    files_modified = []

    # Process all Python test files
    for test_file in test_dir.rglob("test_*.py"):
        if fix_async_tests(test_file):
            files_modified.append(test_file)
            print(f"✅ Fixed: {test_file.relative_to(test_dir.parent.parent)}")

    if files_modified:
        print(f"\n📝 Modified {len(files_modified)} test files")
    else:
        print("✨ No files needed modification")

    return len(files_modified)


if __name__ == "__main__":
    count = main()
    exit(0 if count >= 0 else 1)
