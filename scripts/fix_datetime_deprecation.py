#!/usr/bin/env python3
"""
Fix datetime.now(UTC) deprecation warnings across the codebase.

Replaces all occurrences of datetime.now(UTC) with datetime.now(UTC).
"""

import re
from pathlib import Path


def fix_datetime_in_file(file_path: Path) -> bool:
    """Fix datetime.now(UTC) deprecation in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Check if file already imports UTC
        has_utc_import = "from datetime import UTC" in content or ", UTC" in content

        # Replace datetime.now(UTC) with datetime.now(UTC)
        if "datetime.now(UTC)" in content:
            content = content.replace("datetime.now(UTC)", "datetime.now(UTC)")

            # Add UTC import if needed
            if not has_utc_import:
                # Find the datetime import line
                import_patterns = [
                    (
                        r"from datetime import ([^;\n]+)",
                        r"from datetime import UTC, \1",
                    ),
                    (
                        r"from datetime import\s+datetime\s*$",
                        "from datetime import UTC, datetime",
                    ),
                ]

                for pattern, replacement in import_patterns:
                    if re.search(pattern, content, re.MULTILINE):
                        content = re.sub(pattern, replacement, content, count=1)
                        break

        # Also fix datetime.datetime.now(UTC)
        if "datetime.datetime.now(UTC)" in content:
            content = content.replace(
                "datetime.datetime.now(UTC)", "datetime.datetime.now(UTC)"
            )

            # Add UTC import if needed
            if not has_utc_import:
                # Check various import patterns
                if "import datetime" in content and "from datetime" not in content:
                    # Add a new import line
                    content = re.sub(
                        r"(import datetime\s*\n)",
                        r"\1from datetime import UTC\n",
                        content,
                        count=1,
                    )

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Fix datetime.now(UTC) deprecation across the codebase."""

    # Define directories to search
    src_dir = Path(
        "/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend/src"
    )
    tests_dir = Path(
        "/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend/tests"
    )
    scripts_dir = Path(
        "/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend/scripts"
    )

    fixed_files = []

    for directory in [src_dir, tests_dir, scripts_dir]:
        if not directory.exists():
            continue

        for py_file in directory.rglob("*.py"):
            # Skip __pycache__ and other generated files
            if "__pycache__" in str(py_file):
                continue

            # Check if file contains deprecated datetime.now(UTC)
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    if (
                        "datetime.now(UTC)" in content
                        or "datetime.datetime.now(UTC)" in content
                    ):
                        if fix_datetime_in_file(py_file):
                            fixed_files.append(py_file)
                            print(f"✅ Fixed: {py_file.relative_to(directory.parent)}")
            except Exception as e:
                print(f"❌ Error reading {py_file}: {e}")

    print("\n📊 Summary:")
    print(f"Fixed {len(fixed_files)} files")

    if fixed_files:
        print("\nFixed files:")
        for f in sorted(fixed_files):
            print(f"  - {f.name}")


if __name__ == "__main__":
    main()
