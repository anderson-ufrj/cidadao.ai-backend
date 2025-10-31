#!/usr/bin/env python3
"""
Script to migrate Pydantic V1 validators to V2
"""
import re
from pathlib import Path


def migrate_file(file_path: Path) -> bool:
    """Migrate a single file from Pydantic V1 to V2."""
    content = file_path.read_text()
    original_content = content

    # Replace validator import
    content = re.sub(
        r"from pydantic import (.*?)validator",
        r"from pydantic import \1field_validator",
        content,
    )

    # Replace @validator decorators with @field_validator
    # Pattern to match @validator with any arguments
    pattern = r"@validator\((.*?)\)"

    # Find all validator decorators
    matches = list(re.finditer(pattern, content))

    # Process from end to beginning to maintain positions
    for match in reversed(matches):
        start = match.start()
        end = match.end()

        # Check if there's already a @classmethod decorator
        # Look for the next line after the decorator
        next_line_start = content.find("\n", end) + 1
        next_line_end = content.find("\n", next_line_start)
        next_line = (
            content[next_line_start:next_line_end]
            if next_line_end != -1
            else content[next_line_start:]
        )

        # Replace @validator with @field_validator
        replacement = f"@field_validator({match.group(1)})"

        # If next line doesn't have @classmethod, add it
        if "@classmethod" not in next_line and "def " in next_line:
            # Add @classmethod decorator
            indent = len(next_line) - len(next_line.lstrip())
            replacement += f'\n{" " * indent}@classmethod'

        content = content[:start] + replacement + content[end:]

    # Replace class Config: with model_config
    content = re.sub(
        r"class Config:\s*\n((?:[ \t]+.*\n)*)",
        lambda m: convert_config_to_dict(m.group(1)),
        content,
    )

    # Save if changed
    if content != original_content:
        file_path.write_text(content)
        return True
    return False


def convert_config_to_dict(config_content: str) -> str:
    """Convert class Config to model_config dictionary."""
    lines = config_content.strip().split("\n")
    config_items = []

    for line in lines:
        line = line.strip()
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Map common config options
            if key == "orm_mode":
                key = "from_attributes"
            elif key == "allow_population_by_field_name":
                key = "populate_by_name"
            elif key == "schema_extra":
                key = "json_schema_extra"

            config_items.append(f'"{key}": {value}')

    if config_items:
        return f'model_config = {{\n    {",\\n    ".join(config_items)}\n}}\n'
    return ""


def main():
    """Main migration function."""
    # Files to migrate
    files_to_migrate = [
        "src/tools/transparency_models.py",
        "src/tools/transparency_api.py",
        "src/services/email_service.py",
        "src/models/notification_models.py",
        "src/api/routes/analysis.py",
        "src/api/routes/batch.py",
        "src/api/routes/export.py",
        "src/api/routes/investigations.py",
        "src/api/routes/reports.py",
        "src/services/webhook_service.py",
    ]

    project_root = Path(
        "/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend"
    )

    for file_path in files_to_migrate:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"Migrating {file_path}...")
            if migrate_file(full_path):
                print(f"  ✓ Migrated successfully")
            else:
                print(f"  - No changes needed")
        else:
            print(f"  ✗ File not found: {file_path}")

    print("\nMigration complete!")


if __name__ == "__main__":
    main()
