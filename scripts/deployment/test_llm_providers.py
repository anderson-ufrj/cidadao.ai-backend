#!/usr/bin/env python3
"""
Test LLM providers (Maritaca AI and Anthropic Claude).

Usage:
    python scripts/deployment/test_llm_providers.py
    python scripts/deployment/test_llm_providers.py --provider maritaca
    python scripts/deployment/test_llm_providers.py --provider anthropic
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Validation constants
MIN_RESPONSE_LENGTH = 10


async def test_maritaca():
    """Test Maritaca AI connection."""
    print(f"\n{BLUE}{'=' * 60}")
    print("🇧🇷 Testing Maritaca AI (Sabiá-3)")
    print(f"{'=' * 60}{RESET}")

    api_key = os.getenv("MARITACA_API_KEY")
    if not api_key or api_key == "your-maritaca-api-key-here":
        print(f"{RED}❌ MARITACA_API_KEY not configured{RESET}")
        print(f"\n{YELLOW}Get your API key at: https://plataforma.maritaca.ai/{RESET}")
        return False

    try:
        from src.services.maritaca_client import MaritacaClient, MaritacaModel

        print(f"  API Key: {GREEN}{api_key[:20]}...{RESET}")
        print(f"  Model: {GREEN}{os.getenv('MARITACA_MODEL', 'sabiazinho-4')}{RESET}")

        # Initialize client
        client = MaritacaClient(
            api_key=api_key,
            model=MaritacaModel(os.getenv("MARITACA_MODEL", "sabiazinho-4")),
        )

        # Test prompt (Portuguese)
        test_prompt = "Olá! Você é um assistente brasileiro de transparência pública. Responda em uma frase: qual é sua função?"

        print(f"\n{YELLOW}Sending test prompt...{RESET}")
        print(f"  Prompt: {test_prompt}")

        # Generate response using chat method
        response = await client.chat(
            messages=[{"role": "user", "content": test_prompt}],
            max_tokens=100,
            temperature=0.7,
        )

        print(f"\n{GREEN}✅ Response received:{RESET}")
        print(f"  {response.content[:200]}...")

        # Check response quality
        if len(response.content) < MIN_RESPONSE_LENGTH:
            print(f"{YELLOW}⚠️  Response too short{RESET}")
            return False

        print(f"\n{GREEN}✅ Maritaca AI is working!{RESET}")
        return True

    except ImportError as e:
        print(f"{RED}❌ Import error: {e}{RESET}")
        print(f"{YELLOW}Run: pip install -r requirements.txt{RESET}")
        return False
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")
        return False


async def test_anthropic():  # noqa: PLR0911
    """Test Anthropic Claude connection."""
    print(f"\n{BLUE}{'=' * 60}")
    print("🤖 Testing Anthropic Claude")
    print(f"{'=' * 60}{RESET}")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print(f"{RED}❌ ANTHROPIC_API_KEY not configured{RESET}")
        return False

    try:
        import anthropic

        print(f"  API Key: {GREEN}{api_key[:20]}...{RESET}")
        print(
            f"  Model: {GREEN}{os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')}{RESET}"
        )

        # Initialize client
        client = anthropic.Anthropic(api_key=api_key)

        # Test prompt (Portuguese for consistency)
        test_prompt = "Olá! Você é um assistente de análise de transparência governamental. Responda em uma frase: qual é sua função?"

        print(f"\n{YELLOW}Sending test prompt...{RESET}")
        print(f"  Prompt: {test_prompt}")

        # Generate response
        message = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=100,
            messages=[{"role": "user", "content": test_prompt}],
        )

        response = message.content[0].text

        print(f"\n{GREEN}✅ Response received:{RESET}")
        print(f"  {response[:200]}...")

        # Check response quality
        if len(response) < MIN_RESPONSE_LENGTH:
            print(f"{YELLOW}⚠️  Response too short{RESET}")
            return False

        print(f"\n{GREEN}✅ Anthropic Claude is working!{RESET}")
        return True

    except ImportError:
        print(f"{RED}❌ Anthropic SDK not installed{RESET}")
        print(f"{YELLOW}Run: pip install anthropic{RESET}")
        return False
    except anthropic.AuthenticationError:
        print(f"{RED}❌ Invalid API key{RESET}")
        return False
    except anthropic.RateLimitError:
        print(f"{YELLOW}⚠️  Rate limit exceeded{RESET}")
        return False
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")
        return False


async def main():  # noqa: C901
    parser = argparse.ArgumentParser(description="Test LLM providers")
    parser.add_argument(
        "--provider",
        type=str,
        choices=["maritaca", "anthropic", "all"],
        default="all",
        help="Which provider to test",
    )

    args = parser.parse_args()

    print(f"\n{BLUE}{'=' * 60}")
    print("🔍 LLM Provider Testing")
    print(f"{'=' * 60}{RESET}")

    # Load .env file if exists
    env_file = Path(".env")
    if env_file.exists():
        print(f"\n📄 Loading environment from: {env_file}")
        for env_line in env_file.read_text().splitlines():
            env_line = env_line.strip()  # noqa: PLW2901
            if env_line and not env_line.startswith("#") and "=" in env_line:
                key, value = env_line.split("=", 1)
                if key not in os.environ:
                    os.environ[key] = value

    results = {}

    # Test providers
    if args.provider in ["maritaca", "all"]:
        results["maritaca"] = await test_maritaca()

    if args.provider in ["anthropic", "all"]:
        results["anthropic"] = await test_anthropic()

    # Summary
    print(f"\n{BLUE}{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}{RESET}")

    for provider, success in results.items():
        status = f"{GREEN}✅ Working{RESET}" if success else f"{RED}❌ Failed{RESET}"
        print(f"  {provider.capitalize()}: {status}")

    # Exit status
    all_passed = all(results.values())

    if all_passed:
        print(f"\n{GREEN}✅ All LLM providers are working!{RESET}")

        # Configuration tip
        print(f"\n{BLUE}💡 Configuration:{RESET}")
        print(
            f"  Primary provider: {GREEN}Maritaca AI{RESET} (Brazilian Portuguese native)"
        )
        print(
            f"  Fallback provider: {GREEN}Claude{RESET} (Complex analysis, multi-language)"
        )
        print("\n  Set in .env:")
        print("    LLM_PROVIDER=maritaca")

        return 0

    print(f"\n{YELLOW}⚠️  Some providers failed{RESET}")

    if not results.get("maritaca", True):
        print(f"\n{YELLOW}Maritaca AI setup:{RESET}")
        print("  1. Visit https://plataforma.maritaca.ai/")
        print("  2. Create account and get API key")
        print("  3. Add to .env: MARITACA_API_KEY=your-key-here")

    if not results.get("anthropic", True):
        print(f"\n{YELLOW}Anthropic Claude setup:{RESET}")
        print("  1. Visit https://console.anthropic.com/")
        print("  2. Get API key from dashboard")
        print("  3. Add to .env: ANTHROPIC_API_KEY=your-key-here")

    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
