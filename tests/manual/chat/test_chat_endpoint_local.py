#!/usr/bin/env python3
"""Test chat endpoint locally to reproduce production error."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables BEFORE importing anything
import os

os.environ["JWT_SECRET_KEY"] = "test"
os.environ["SECRET_KEY"] = "test"


async def test_chat_integration():
    """Test the complete chat integration flow."""
    print("=" * 80)
    print("🧪 Testing Chat Integration (Zumbi Investigation)")
    print("=" * 80 + "\n")

    try:
        # Import after setting env vars
        from src.api.routes.chat_zumbi_integration import run_zumbi_investigation

        query = "Contratos de saúde em MG acima de 1 milhão em 2024"

        print(f"📝 Query: {query}\n")
        print("🔄 Running investigation...")

        result = await run_zumbi_investigation(
            query=query,
            organization_codes=None,
            enable_open_data=True,
            session_id="test-local",
            user_id="test-user",
        )

        print("\n✅ Investigation completed!")
        print(f"\nResult keys: {list(result.keys())}")

        for key, value in result.items():
            if isinstance(value, (list, dict)) and len(str(value)) > 200:
                print(f"{key}: <large object with {len(value)} items>")
            else:
                print(f"{key}: {value}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """Run test."""
    await test_chat_integration()


if __name__ == "__main__":
    asyncio.run(main())
