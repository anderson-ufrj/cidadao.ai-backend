#!/usr/bin/env python3
"""
Script to migrate Pydantic V1 Config classes to V2 model_config
"""
import re
from pathlib import Path


def migrate_config_class(file_path: Path) -> bool:
    """Migrate Config classes in a file."""
    content = file_path.read_text()
    original_content = content

    # Import ConfigDict if needed
    if "class Config:" in content and "from pydantic import" in content:
        # Add ConfigDict to imports
        content = re.sub(
            r"from pydantic import ([^;\n]+)",
            lambda m: (
                f"from pydantic import ConfigDict, {m.group(1)}"
                if "ConfigDict" not in m.group(1)
                else m.group(0)
            ),
            content,
        )

    # Pattern to match class Config and its content
    pattern = r"(\s+)class Config:\s*\n((?:\1[ ]+.*\n)*)"

    def replace_config(match):
        indent = match.group(1)
        config_body = match.group(2)

        # Parse config lines
        config_dict = {}
        for line in config_body.split("\n"):
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Map old keys to new ones
                if key == "orm_mode":
                    key = "from_attributes"
                elif key == "allow_population_by_field_name":
                    key = "populate_by_name"
                elif key == "schema_extra":
                    key = "json_schema_extra"
                elif key == "allow_mutation":
                    continue  # No longer needed in V2
                elif key == "validate_assignment":
                    key = "validate_assignment"
                elif key == "use_enum_values":
                    key = "use_enum_values"
                elif key == "arbitrary_types_allowed":
                    key = "arbitrary_types_allowed"
                elif key == "json_encoders":
                    key = "json_encoders"

                config_dict[key] = value

        # Build model_config
        if config_dict:
            items = [f'"{k}": {v}' for k, v in config_dict.items()]
            return f'{indent}model_config = ConfigDict(\n{indent}    {f",\n{indent}    ".join(items)}\n{indent})\n'
        else:
            return f"{indent}model_config = ConfigDict()\n"

    content = re.sub(pattern, replace_config, content)

    # Save if changed
    if content != original_content:
        file_path.write_text(content)
        return True
    return False


def main():
    """Main migration function."""
    files_to_migrate = [
        "src/core/secret_manager.py",
        "src/services/transparency_apis/federal_apis/compras_gov_client.py",
        "src/services/transparency_apis/federal_apis/minha_receita_client.py",
        "src/services/transparency_apis/federal_apis/pncp_client.py",
        "src/tools/dados_gov_models.py",
    ]

    project_root = Path(
        "/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend"
    )

    for file_path in files_to_migrate:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"Migrating {file_path}...")
            if migrate_config_class(full_path):
                print(f"  ✓ Migrated successfully")
            else:
                print(f"  - No changes needed")
        else:
            print(f"  ✗ File not found: {file_path}")

    print("\nMigration complete!")


if __name__ == "__main__":
    main()
