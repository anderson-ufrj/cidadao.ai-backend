#!/usr/bin/env python3
"""
Documentation Index Generator

Automatically generates index files for documentation directories.
Scans markdown files and creates organized INDEX.md files with
statistics, quick navigation, and file listings.

Usage:
    python scripts/generate_doc_index.py
    python scripts/generate_doc_index.py --directory docs/agents
    python scripts/generate_doc_index.py --all  # Regenerate all indexes
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"


class DocIndexGenerator:
    """Generates documentation index files."""

    def __init__(self):
        self.stats: dict[str, int] = {}

    def count_lines(self, file_path: Path) -> int:
        """Count lines in a file."""
        try:
            return len(file_path.read_text(encoding="utf-8").splitlines())
        except Exception:
            return 0

    def extract_title(self, file_path: Path) -> str:
        """Extract title from markdown file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            for raw_line in content.splitlines():
                stripped = raw_line.strip()
                if stripped.startswith("# "):
                    return stripped[2:].strip()
            return file_path.stem.replace("_", " ").title()
        except Exception:
            return file_path.stem.replace("_", " ").title()

    def extract_description(self, file_path: Path) -> str:
        """Extract first paragraph as description."""
        try:
            content = file_path.read_text(encoding="utf-8")
            in_front_matter = False
            found_title = False

            for raw_line in content.splitlines():
                stripped = raw_line.strip()

                # Skip front matter
                if stripped == "---":
                    in_front_matter = not in_front_matter
                    continue
                if in_front_matter:
                    continue

                # Skip title
                if stripped.startswith("# "):
                    found_title = True
                    continue

                # First non-empty line after title is description
                if found_title and stripped and not stripped.startswith("#"):
                    # Clean up markdown
                    cleaned = stripped.replace("**", "").replace("*", "")
                    return cleaned[:100] + ("..." if len(cleaned) > 100 else "")

            return ""
        except Exception:
            return ""

    def generate_agents_index(self) -> str:
        """Generate index for agents/ directory."""
        agents_dir = DOCS_DIR / "agents"
        md_files = sorted(
            [
                f
                for f in agents_dir.glob("*.md")
                if f.name not in ["INDEX.md", "README.md", "INVENTORY.md"]
                and not f.name.startswith("AGENT_")
                and not f.name.endswith("_ANALYSIS.md")
            ]
        )

        content = [
            "# 🤖 Agents Documentation Index",
            "",
            f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}",
            f"**Total Agents**: {len(md_files)} documented",
            "",
            "---",
            "",
            "## 📚 Agent Documentation Files",
            "",
        ]

        # Group by first letter for better organization
        current_letter = ""
        for md_file in md_files:
            first_letter = md_file.stem[0].upper()
            if first_letter != current_letter:
                current_letter = first_letter
                content.append(f"### {current_letter}")
                content.append("")

            title = self.extract_title(md_file)
            desc = self.extract_description(md_file)
            lines = self.count_lines(md_file)

            content.append(f"- **[{title}]({md_file.name})**")
            if desc:
                content.append(f"  - {desc}")
            content.append(f"  - {lines:,} lines")
            content.append("")

        content.extend(
            [
                "---",
                "",
                "## 📊 Statistics",
                "",
                f"- Total documented agents: {len(md_files)}",
                f"- Total documentation lines: {sum(self.count_lines(f) for f in md_files):,}",
                "",
                "---",
                "",
                "**For agent architecture**: See [multi-agent-architecture.md](../architecture/multi-agent-architecture.md)",
            ]
        )

        return "\n".join(content)

    def generate_api_index(self) -> str:
        """Generate index for api/ directory."""
        api_dir = DOCS_DIR / "api"
        md_files = sorted(
            [f for f in api_dir.glob("*.md") if f.name not in ["INDEX.md", "README.md"]]
        )

        content = [
            "# 🌐 API Documentation Index",
            "",
            f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}",
            f"**Total Documents**: {len(md_files)}",
            "",
            "---",
            "",
            "## 📚 API Documentation Files",
            "",
        ]

        # Categorize API docs
        categories = {
            "Integration": [],
            "Implementation": [],
            "Status": [],
            "Other": [],
        }

        for md_file in md_files:
            title = self.extract_title(md_file)
            if "INTEGRATION" in md_file.name.upper():
                categories["Integration"].append((md_file, title))
            elif "IMPLEMENTATION" in md_file.name.upper():
                categories["Implementation"].append((md_file, title))
            elif "STATUS" in md_file.name.upper():
                categories["Status"].append((md_file, title))
            else:
                categories["Other"].append((md_file, title))

        for category, files in categories.items():
            if files:
                content.append(f"### {category}")
                content.append("")
                for md_file, title in sorted(files, key=lambda x: x[1]):
                    desc = self.extract_description(md_file)
                    content.append(f"- **[{title}]({md_file.name})**")
                    if desc:
                        content.append(f"  - {desc}")
                    content.append("")

        content.extend(
            [
                "---",
                "",
                "## 📊 Statistics",
                "",
                f"- Total API documents: {len(md_files)}",
                f"- Integration guides: {len(categories['Integration'])}",
                f"- Implementation docs: {len(categories['Implementation'])}",
                f"- Status reports: {len(categories['Status'])}",
                "",
            ]
        )

        return "\n".join(content)

    def generate_generic_index(self, directory: Path) -> str:
        """Generate generic index for any directory."""
        md_files = sorted(
            [
                f
                for f in directory.glob("*.md")
                if f.name not in ["INDEX.md", "README.md"]
            ]
        )

        dir_name = directory.name.replace("_", " ").title()

        content = [
            f"# {dir_name} Documentation Index",
            "",
            f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}",
            f"**Total Documents**: {len(md_files)}",
            "",
            "---",
            "",
            "## 📚 Documentation Files",
            "",
        ]

        for md_file in md_files:
            title = self.extract_title(md_file)
            desc = self.extract_description(md_file)
            lines = self.count_lines(md_file)

            content.append(f"- **[{title}]({md_file.name})**")
            if desc:
                content.append(f"  - {desc}")
            content.append(f"  - {lines:,} lines")
            content.append("")

        content.extend(
            [
                "---",
                "",
                "## 📊 Statistics",
                "",
                f"- Total documents: {len(md_files)}",
                f"- Total lines: {sum(self.count_lines(f) for f in md_files):,}",
            ]
        )

        return "\n".join(content)

    def generate_index(self, directory: Path) -> bool:
        """Generate index for a specific directory."""
        print(f"📝 Generating index for {directory.relative_to(BASE_DIR)}")

        # Choose specialized generator if available
        if directory.name == "agents":
            content = self.generate_agents_index()
        elif directory.name == "api":
            content = self.generate_api_index()
        else:
            content = self.generate_generic_index(directory)

        # Write index file
        index_file = directory / "INDEX.md"
        try:
            index_file.write_text(content, encoding="utf-8")
            print(f"✅ Created {index_file.relative_to(BASE_DIR)}")
            return True
        except Exception as e:
            print(f"❌ Error writing {index_file}: {e}")
            return False

    def generate_all(self) -> bool:
        """Generate indexes for all major documentation directories."""
        print("🔄 Generating all documentation indexes")
        print("=" * 60)

        directories = [
            DOCS_DIR / "agents",
            DOCS_DIR / "api",
            DOCS_DIR / "architecture",
            DOCS_DIR / "deployment",
            DOCS_DIR / "testing",
        ]

        success = True
        for directory in directories:
            if directory.exists():
                if not self.generate_index(directory):
                    success = False
            else:
                print(f"⚠️  Directory not found: {directory}")

        print("=" * 60)
        if success:
            print("✅ All indexes generated successfully!")
        else:
            print("❌ Some indexes failed to generate")

        return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate documentation indexes")
    parser.add_argument(
        "--directory",
        "-d",
        type=Path,
        help="Specific directory to generate index for",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Generate indexes for all major directories",
    )

    args = parser.parse_args()

    generator = DocIndexGenerator()

    if args.all:
        success = generator.generate_all()
    elif args.directory:
        directory = (
            args.directory
            if args.directory.is_absolute()
            else BASE_DIR / args.directory
        )
        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            return 1
        success = generator.generate_index(directory)
    else:
        # Default: generate for main directories
        success = generator.generate_all()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
