#!/usr/bin/env python3
"""
Documentation Link Validator

Validates all internal links in markdown files to ensure documentation
integrity. Checks for broken links, missing files, and incorrect paths.

Usage:
    python scripts/validate_doc_links.py
    python scripts/validate_doc_links.py --fix  # Auto-fix some issues
    python scripts/validate_doc_links.py --verbose  # Detailed output
"""

import re
import sys
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"


class LinkValidator:
    """Validates markdown links in documentation."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors: list[tuple[Path, int, str]] = []
        self.warnings: list[tuple[Path, int, str]] = []
        self.checked_files = 0
        self.checked_links = 0

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled."""
        if self.verbose or level in ("ERROR", "WARNING"):
            prefix = {"INFO": "ℹ️ ", "WARNING": "⚠️ ", "ERROR": "❌"}
            print(f"{prefix.get(level, '')} {message}")

    def find_markdown_files(self, directory: Path) -> list[Path]:
        """Find all markdown files in directory."""
        return list(directory.rglob("*.md"))

    def extract_links(self, content: str, file_path: Path) -> list[tuple[int, str]]:
        """Extract markdown links with line numbers."""
        links = []

        # Match markdown links: [text](url)
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

        for line_num, line in enumerate(content.split("\n"), start=1):
            for match in re.finditer(link_pattern, line):
                url = match.group(2)
                # Only check relative links (internal documentation)
                if not url.startswith(("http://", "https://", "mailto:", "#")):
                    links.append((line_num, url))

        return links

    def resolve_link_path(self, source_file: Path, link: str) -> Path:
        """Resolve relative link to absolute path."""
        # Remove anchor fragments
        link = link.split("#")[0]

        if not link:  # Pure anchor link
            return source_file

        # Resolve relative to source file's directory
        source_dir = source_file.parent
        return (source_dir / link).resolve()

    def validate_link(self, source_file: Path, line_num: int, link: str) -> bool:
        """Validate a single link."""
        self.checked_links += 1

        try:
            target_path = self.resolve_link_path(source_file, link)

            # Check if target exists
            if not target_path.exists():
                error_msg = f"Broken link: {link} (target does not exist)"
                self.errors.append((source_file, line_num, error_msg))
                self.log(f"  Line {line_num}: {error_msg}", "ERROR")
                return False

            # Check if it's a file (not directory) when expected
            if not link.endswith("/") and target_path.is_dir():
                warning_msg = f"Link points to directory: {link} (consider adding /)"
                self.warnings.append((source_file, line_num, warning_msg))
                self.log(f"  Line {line_num}: {warning_msg}", "WARNING")

            return True

        except Exception as e:
            error_msg = f"Error resolving link {link}: {e}"
            self.errors.append((source_file, line_num, error_msg))
            self.log(f"  Line {line_num}: {error_msg}", "ERROR")
            return False

    def validate_file(self, file_path: Path) -> bool:
        """Validate all links in a markdown file."""
        self.checked_files += 1
        self.log(f"Checking {file_path.relative_to(BASE_DIR)}...")

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            self.log(f"Error reading {file_path}: {e}", "ERROR")
            return False

        links = self.extract_links(content, file_path)

        if links:
            self.log(f"  Found {len(links)} links to validate")

        all_valid = True
        for line_num, link in links:
            if not self.validate_link(file_path, line_num, link):
                all_valid = False

        return all_valid

    def validate_all(self) -> bool:  # noqa: C901, PLR0912
        """Validate all markdown files in docs directory."""
        print("🔍 Starting Documentation Link Validation")
        print(f"📁 Base directory: {BASE_DIR}")
        print(f"📚 Docs directory: {DOCS_DIR}")
        print("-" * 60)

        markdown_files = self.find_markdown_files(DOCS_DIR)

        # Also check root README files
        for readme in ["README.md", "CONTRIBUTING.md", "SECURITY.md", "QUICKSTART.md"]:
            readme_path = BASE_DIR / readme
            if readme_path.exists():
                markdown_files.append(readme_path)

        print(f"📄 Found {len(markdown_files)} markdown files to check\n")

        all_valid = True
        for md_file in sorted(markdown_files):
            if not self.validate_file(md_file):
                all_valid = False

        # Print summary
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Files checked: {self.checked_files}")
        print(f"Links validated: {self.checked_links}")
        print(f"Errors found: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")

        if self.errors:
            print("\n❌ ERRORS FOUND:")
            for file_path, line_num, error_msg in self.errors[:10]:  # Show first 10
                rel_path = file_path.relative_to(BASE_DIR)
                print(f"  {rel_path}:{line_num} - {error_msg}")

            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for file_path, line_num, warning_msg in self.warnings[:5]:
                rel_path = file_path.relative_to(BASE_DIR)
                print(f"  {rel_path}:{line_num} - {warning_msg}")

            if len(self.warnings) > 5:
                print(f"  ... and {len(self.warnings) - 5} more warnings")

        if all_valid and not self.warnings:
            print("\n✅ All documentation links are valid!")
        elif all_valid:
            print("\n✅ No broken links, but some warnings to review")
        else:
            print("\n❌ Validation failed - broken links found")

        print("=" * 60)

        return all_valid


def main():
    """Main entry point."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    validator = LinkValidator(verbose=verbose)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
