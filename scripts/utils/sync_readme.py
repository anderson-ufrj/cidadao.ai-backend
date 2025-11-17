#!/usr/bin/env python3
"""
README Sync Script - Cidadão.AI
Automatically manages README files for GitHub and HF Spaces

Usage:
  python scripts/sync_readme.py --target github   # Sync to GitHub
  python scripts/sync_readme.py --target hf       # Sync to HF Spaces
  python scripts/sync_readme.py --check           # Check sync status
  python scripts/sync_readme.py --auto-detect     # Auto-detect and sync
"""

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# HF Spaces YAML Header
HF_YAML_HEADER = """---
title: Cidadão.AI - Public Transparency Platform / Plataforma de Transparência Pública
emoji: 🔍
colorFrom: green
colorTo: yellow
sdk: gradio
sdk_version: "5.0.0"
app_file: apps/gradio_app.py
pinned: true
license: apache-2.0
language:
  - pt
  - en
tags:
  - transparency
  - government
  - corruption-detection
  - anomaly-detection
  - brazilian-government
  - public-spending
  - accountability
  - SDG16
  - open-government
  - civic-tech
pipeline_tag: text-classification
library_name: transformers
base_model: gpt2
datasets:
  - portal-da-transparencia
  - custom
metrics:
  - accuracy
  - f1
  - precision
  - recall
description: >
  Cidadão.AI is an enterprise-grade multi-agent AI platform for Brazilian government transparency analysis.
  Features 8 specialized agents, 40+ API endpoints, and achieves 89.2% accuracy in anomaly detection.
  Aligned with UN SDG16 and Open Government Partnership principles.
---

"""


def get_project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


def get_current_branch():
    """Get current git branch."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except:
        return "unknown"


def get_git_remote():
    """Detect if we're on GitHub or HF remote."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip()

        if "github.com" in remote_url:
            return "github"
        elif "hf.co" in remote_url or "huggingface.co" in remote_url:
            return "hf"
        else:
            return "unknown"
    except:
        return "unknown"


def read_base_readme():
    """Read the base README content without YAML header."""
    readme_path = get_project_root() / "README.md"
    if not readme_path.exists():
        # Try README_HF.md as source
        readme_hf_path = get_project_root() / "README_HF.md"
        if readme_hf_path.exists():
            content = readme_hf_path.read_text(encoding="utf-8")
        else:
            raise FileNotFoundError("Neither README.md nor README_HF.md found")
    else:
        content = readme_path.read_text(encoding="utf-8")

    # Remove YAML header if exists
    if content.startswith("---"):
        lines = content.split("\n")
        yaml_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                yaml_end = i
                break

        if yaml_end > 0:
            content = "\n".join(lines[yaml_end + 1 :]).lstrip("\n")

    return content


def sync_to_github():
    """Sync README for GitHub (clean, no YAML header)."""
    print("🔄 Syncing README for GitHub...")

    base_content = read_base_readme()
    readme_path = get_project_root() / "README.md"

    # Write clean content
    readme_path.write_text(base_content, encoding="utf-8")

    print("✅ GitHub README synced (clean format)")
    return True


def sync_to_hf():
    """Sync README for HF Spaces (with YAML header)."""
    print("🔄 Syncing README for HF Spaces...")

    base_content = read_base_readme()
    readme_path = get_project_root() / "README.md"

    # Add HF YAML header
    hf_content = HF_YAML_HEADER + base_content
    readme_path.write_text(hf_content, encoding="utf-8")

    print("✅ HF Spaces README synced (with YAML header)")
    return True


def check_readme_status():
    """Check current README status."""
    print("🔍 Checking README status...")

    readme_path = get_project_root() / "README.md"
    if not readme_path.exists():
        print("❌ README.md not found")
        return False

    content = readme_path.read_text(encoding="utf-8")

    has_yaml = content.startswith("---")
    has_app_file = "app_file:" in content

    branch = get_current_branch()
    remote = get_git_remote()

    print(f"📍 Current branch: {branch}")
    print(f"🌐 Git remote: {remote}")

    if has_yaml and has_app_file:
        print("📝 README is configured for HF Spaces (has YAML header)")
        print("   - Contains HF metadata")
        print("   - Ready for HF Spaces deployment")
        return "hf"
    elif not has_yaml:
        print("📝 README is configured for GitHub (clean format)")
        print("   - No YAML metadata")
        print("   - Clean documentation format")
        return "github"
    else:
        print("⚠️  README format unclear")
        return "unknown"


def auto_detect_and_sync():
    """Auto-detect environment and sync accordingly."""
    print("🤖 Auto-detecting environment...")

    remote = get_git_remote()

    if remote == "github":
        print("📍 Detected GitHub environment")
        return sync_to_github()
    elif remote == "hf":
        print("📍 Detected HF Spaces environment")
        return sync_to_hf()
    else:
        print("⚠️  Cannot auto-detect environment")
        print("💡 Use --target github or --target hf explicitly")
        return False


def backup_readme():
    """Create backup of current README."""
    readme_path = get_project_root() / "README.md"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = get_project_root() / f"README_backup_{timestamp}.md"

    if readme_path.exists():
        shutil.copy2(readme_path, backup_path)
        print(f"💾 Backup created: {backup_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Sync README files for different platforms"
    )
    parser.add_argument("--target", choices=["github", "hf"], help="Target platform")
    parser.add_argument("--check", action="store_true", help="Check current status")
    parser.add_argument(
        "--auto-detect", action="store_true", help="Auto-detect and sync"
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create backup before sync"
    )

    args = parser.parse_args()

    # Default behavior for backward compatibility
    if len(sys.argv) == 2 and sys.argv[1] in ["github", "hf"]:
        args.target = sys.argv[1]

    if args.check:
        status = check_readme_status()
        sys.exit(0)

    if args.auto_detect:
        if args.backup:
            backup_readme()
        success = auto_detect_and_sync()
        sys.exit(0 if success else 1)

    if not args.target:
        parser.print_help()
        sys.exit(1)

    try:
        if args.backup:
            backup_readme()

        if args.target == "github":
            sync_to_github()
        elif args.target == "hf":
            sync_to_hf()

        print(f"\n🎯 README synced for {args.target.upper()}")
        print("💡 Don't forget to commit and push the changes!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
