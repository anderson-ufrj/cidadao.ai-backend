#!/usr/bin/env python3
"""
Repository Cleanup Script
Author: Anderson Henrique da Silva
Date: 2025-10-31
Purpose: Clean generated files and caches from repository
"""

import shutil
from pathlib import Path


def clean_directory(path, pattern=None):
    """Remove directory or files matching pattern."""
    if pattern:
        for item in Path(".").rglob(pattern):
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
                print(f"  ✓ Removed: {item}")
            else:
                item.unlink(missing_ok=True)
                print(f"  ✓ Removed: {item}")
    elif Path(path).exists():
        if Path(path).is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            Path(path).unlink(missing_ok=True)
        print(f"  ✓ Removed: {path}")


def get_directory_size(path):
    """Calculate total size of a directory."""
    total = 0
    if Path(path).exists():
        for entry in Path(path).rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
    return total


def format_size(bytes):
    """Format bytes to human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024.0:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024.0
    return f"{bytes:.1f}TB"


def main():
    """Main cleanup function."""
    print("=" * 60)
    print("🧹 Cidadão.AI Repository Cleanup")
    print("=" * 60)

    initial_size = sum(f.stat().st_size for f in Path(".").rglob("*") if f.is_file())

    # Python caches
    print("\n📦 Cleaning Python caches...")
    clean_directory(".", "__pycache__")
    clean_directory(".pytest_cache")
    clean_directory(".coverage")
    clean_directory("*.pyc")
    clean_directory("*.pyo")
    clean_directory("*~")

    # Coverage reports
    print("\n📊 Cleaning coverage reports...")
    clean_directory("htmlcov")
    clean_directory(".coverage")
    clean_directory(".coverage.*")

    # Build artifacts
    print("\n🔨 Cleaning build artifacts...")
    clean_directory("build")
    clean_directory("dist")
    clean_directory("*.egg-info")
    clean_directory(".eggs")

    # Node modules (if any)
    print("\n📦 Cleaning Node.js files...")
    clean_directory("node_modules")
    clean_directory("*/node_modules")

    # Temporary files
    print("\n🗑️ Cleaning temporary files...")
    clean_directory("*.log")
    clean_directory("*.tmp")
    clean_directory("*.bak")
    clean_directory("*.swp")
    clean_directory(".DS_Store")

    # Database files (if not needed)
    print("\n💾 Cleaning temporary databases...")
    clean_directory("*.db")
    clean_directory("*.sqlite")
    clean_directory("*.sqlite3")

    # Test files in root (should be in tests/)
    print("\n🧪 Checking for misplaced test files...")
    root_tests = list(Path(".").glob("test_*.py"))
    if root_tests:
        print(f"  ⚠️  Found {len(root_tests)} test files in root:")
        for test in root_tests:
            print(f"    - {test}")
        print("  Consider moving them to tests/ directory")
    else:
        print("  ✓ No test files in root")

    # Calculate space saved
    final_size = sum(f.stat().st_size for f in Path(".").rglob("*") if f.is_file())
    saved = initial_size - final_size

    print("\n" + "=" * 60)
    print("✅ Cleanup Complete!")
    print(f"   Space saved: {format_size(saved)}")
    print(f"   Repository size: {format_size(final_size)}")
    print("=" * 60)

    # Reminder
    print("\n📝 Remember to run regularly:")
    print("   python3 scripts/clean_repo.py")
    print("   python3 scripts/validate_documentation.py")


if __name__ == "__main__":
    main()
