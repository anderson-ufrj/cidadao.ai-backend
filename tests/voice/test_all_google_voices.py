#!/usr/bin/env python3
"""
Comprehensive test of ALL available Google Cloud voices for Brazilian Portuguese.

This script will:
1. List ALL pt-BR voices available (Standard, Wavenet, Neural2, Studio, Journey)
2. Categorize them by quality and gender
3. Test samples from each category
4. Generate comparison report
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import texttospeech_v1 as texttospeech
from google.oauth2 import service_account

# Load environment
load_dotenv()

# Get credentials
credentials_path = os.getenv(
    "GOOGLE_CREDENTIALS_PATH", "config/credentials/google-cloud-key.json"
)
project_root = Path(__file__).parent
if not Path(credentials_path).is_absolute():
    credentials_path = project_root / credentials_path


async def discover_all_voices():
    """Discover ALL available pt-BR voices."""
    print("🔍 Discovering ALL Brazilian Portuguese Voices")
    print("=" * 80)

    try:
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        # Initialize client
        client = texttospeech.TextToSpeechClient(credentials=credentials)

        # List all voices
        response = client.list_voices(language_code="pt-BR")

        # Categorize voices
        voices_by_category = {
            "Standard": [],
            "WaveNet": [],
            "Neural2": [],
            "Studio": [],
            "Journey": [],
            "Polyglot": [],
            "News": [],
            "Other": [],
        }

        for voice in response.voices:
            # Only pt-BR voices
            if "pt-BR" not in voice.name:
                continue

            voice_info = {
                "name": voice.name,
                "gender": voice.ssml_gender.name,
                "natural_sample_rate": voice.natural_sample_rate_hertz,
                "language_codes": list(voice.language_codes),
            }

            # Categorize by name pattern
            if "Studio" in voice.name:
                voices_by_category["Studio"].append(voice_info)
            elif "Journey" in voice.name:
                voices_by_category["Journey"].append(voice_info)
            elif "Neural2" in voice.name:
                voices_by_category["Neural2"].append(voice_info)
            elif "Wavenet" in voice.name or "WaveNet" in voice.name:
                voices_by_category["WaveNet"].append(voice_info)
            elif "Polyglot" in voice.name:
                voices_by_category["Polyglot"].append(voice_info)
            elif "News" in voice.name:
                voices_by_category["News"].append(voice_info)
            elif "Standard" in voice.name:
                voices_by_category["Standard"].append(voice_info)
            else:
                voices_by_category["Other"].append(voice_info)

        # Print report
        total_voices = sum(len(v) for v in voices_by_category.values())
        print(f"\n📊 Total Brazilian Portuguese Voices: {total_voices}\n")

        for category, voices in voices_by_category.items():
            if not voices:
                continue

            print(f"\n{'='*80}")
            print(f"🎤 {category.upper()} VOICES ({len(voices)} voices)")
            print(f"{'='*80}")

            # Count by gender
            male_count = sum(1 for v in voices if v["gender"] == "MALE")
            female_count = sum(1 for v in voices if v["gender"] == "FEMALE")
            neutral_count = sum(1 for v in voices if v["gender"] == "NEUTRAL")

            print(
                f"Gender Distribution: {male_count} Male, {female_count} Female, {neutral_count} Neutral\n"
            )

            for voice in sorted(voices, key=lambda x: (x["gender"], x["name"])):
                print(f"  • {voice['name']}")
                print(f"    Gender: {voice['gender']}")
                print(f"    Sample Rate: {voice['natural_sample_rate']} Hz")
                print(f"    Languages: {', '.join(voice['language_codes'])}")
                print()

        # Quality tier recommendations
        print("\n" + "=" * 80)
        print("🌟 QUALITY TIERS & RECOMMENDATIONS")
        print("=" * 80)

        print("\n1️⃣ HIGHEST QUALITY (Premium)")
        if voices_by_category["Studio"]:
            print("   🎙️  Studio Voices:")
            print("   - Ultra-premium quality")
            print("   - Professional broadcast standard")
            print("   - Most expensive ($16-24 per 1M chars)")
            print("   - Best for: Premium experiences, audiobooks")
            for v in voices_by_category["Studio"]:
                print(f"      • {v['name']} ({v['gender']})")

        if voices_by_category["Journey"]:
            print("\n   🚀 Journey Voices:")
            print("   - Conversational, dynamic")
            print("   - Suitable for interactive experiences")
            print("   - Premium pricing")
            for v in voices_by_category["Journey"]:
                print(f"      • {v['name']} ({v['gender']})")

        print("\n2️⃣ HIGH QUALITY (Recommended)")
        if voices_by_category["Neural2"]:
            print("   🧠 Neural2 Voices (CURRENT CHOICE):")
            print("   - Ultra-natural, latest technology")
            print("   - Excellent prosody and expressiveness")
            print("   - $16 per 1M characters")
            print("   - Best for: Production applications")
            for v in voices_by_category["Neural2"]:
                print(f"      • {v['name']} ({v['gender']})")

        print("\n3️⃣ GOOD QUALITY")
        if voices_by_category["WaveNet"]:
            print(
                f"   🌊 WaveNet Voices ({len(voices_by_category['WaveNet'])} available):"
            )
            print("   - Good natural quality")
            print("   - $16 per 1M characters (same as Neural2)")
            print("   - Note: Neural2 is better at same price")
            print(f"   - {male_count} male, {female_count} female options")

        print("\n4️⃣ BASIC QUALITY")
        if voices_by_category["Standard"]:
            print(
                f"   📻 Standard Voices ({len(voices_by_category['Standard'])} available):"
            )
            print("   - Basic synthesized speech")
            print("   - $4 per 1M characters (cheapest)")
            print("   - Best for: High-volume, cost-sensitive use cases")

        # Recommendations
        print("\n" + "=" * 80)
        print("💡 RECOMMENDATIONS FOR CIDADÃO.AI")
        print("=" * 80)

        print("\n✅ Option 1: Keep Neural2 (Current)")
        print("   - Already using best value-for-money")
        print("   - 2 voices: pt-BR-Neural2-A (F), pt-BR-Neural2-B (M)")
        print("   - Ultra-natural quality")
        print("   - $16 per 1M chars")

        if voices_by_category["WaveNet"]:
            wavenet_male = [
                v for v in voices_by_category["WaveNet"] if v["gender"] == "MALE"
            ]
            wavenet_female = [
                v for v in voices_by_category["WaveNet"] if v["gender"] == "FEMALE"
            ]

            print(f"\n🔄 Option 2: Mix Neural2 + WaveNet for MORE VARIETY")
            print(
                f"   - Add {len(wavenet_male)} male + {len(wavenet_female)} female WaveNet voices"
            )
            print("   - Same cost as Neural2 ($16 per 1M chars)")
            print("   - MORE voice options for personality matching")
            print("   - Slightly less natural than Neural2")
            print("\n   Available WaveNet voices:")
            print(f"   Male ({len(wavenet_male)}):")
            for v in wavenet_male[:5]:  # Show first 5
                print(f"      • {v['name']}")
            if len(wavenet_male) > 5:
                print(f"      ... and {len(wavenet_male) - 5} more")

            print(f"   Female ({len(wavenet_female)}):")
            for v in wavenet_female[:5]:
                print(f"      • {v['name']}")
            if len(wavenet_female) > 5:
                print(f"      ... and {len(wavenet_female) - 5} more")

        if voices_by_category["Studio"]:
            print("\n⭐ Option 3: Upgrade to Studio (Premium)")
            print("   - Absolute best quality available")
            print("   - Professional broadcast standard")
            print("   - Higher cost (check pricing)")
            print("   - Best for: Premium user tier")

        # Gender diversity analysis
        print("\n" + "=" * 80)
        print("👥 GENDER DIVERSITY ANALYSIS")
        print("=" * 80)

        print("\nCurrent System (Neural2 only):")
        print("   - 2 voices total: 1 male, 1 female")
        print("   - Limited personality options")
        print("   - All agents must share one of two voices")

        if voices_by_category["WaveNet"]:
            wavenet_male = [
                v for v in voices_by_category["WaveNet"] if v["gender"] == "MALE"
            ]
            wavenet_female = [
                v for v in voices_by_category["WaveNet"] if v["gender"] == "FEMALE"
            ]

            print(f"\nWith WaveNet Addition:")
            print(
                f"   - {len(wavenet_male) + 1} male voices (Neural2-B + {len(wavenet_male)} WaveNet)"
            )
            print(
                f"   - {len(wavenet_female) + 1} female voices (Neural2-A + {len(wavenet_female)} WaveNet)"
            )
            print("   - Much more personality variety!")
            print("   - Better matching of agent personalities")

        return voices_by_category

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def generate_voice_samples(voices_by_category):
    """Generate samples from different voice categories."""
    print("\n" + "=" * 80)
    print("🎙️  GENERATING SAMPLE COMPARISONS")
    print("=" * 80)

    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        client = texttospeech.TextToSpeechClient(credentials=credentials)

        test_text = "Olá, sou um agente de inteligência artificial do Cidadão ponto AI. Minha missão é combater a corrupção no Brasil."

        # Test samples from each category
        samples_to_generate = []

        # Neural2 (current)
        if voices_by_category.get("Neural2"):
            samples_to_generate.append(
                {
                    "category": "Neural2",
                    "voice": "pt-BR-Neural2-B",
                    "label": "neural2_male_current",
                }
            )
            samples_to_generate.append(
                {
                    "category": "Neural2",
                    "voice": "pt-BR-Neural2-A",
                    "label": "neural2_female_current",
                }
            )

        # WaveNet samples (if available)
        if voices_by_category.get("WaveNet"):
            wavenet_male = [
                v for v in voices_by_category["WaveNet"] if v["gender"] == "MALE"
            ]
            wavenet_female = [
                v for v in voices_by_category["WaveNet"] if v["gender"] == "FEMALE"
            ]

            if wavenet_male:
                # Test first 2 male WaveNet voices
                for i, voice in enumerate(wavenet_male[:2]):
                    samples_to_generate.append(
                        {
                            "category": "WaveNet",
                            "voice": voice["name"],
                            "label": f"wavenet_male_{i+1}",
                        }
                    )

            if wavenet_female:
                # Test first 2 female WaveNet voices
                for i, voice in enumerate(wavenet_female[:2]):
                    samples_to_generate.append(
                        {
                            "category": "WaveNet",
                            "voice": voice["name"],
                            "label": f"wavenet_female_{i+1}",
                        }
                    )

        # Studio (if available)
        if voices_by_category.get("Studio"):
            studio_voice = voices_by_category["Studio"][0]
            samples_to_generate.append(
                {
                    "category": "Studio",
                    "voice": studio_voice["name"],
                    "label": "studio_premium",
                }
            )

        print(f"\n📝 Generating {len(samples_to_generate)} voice samples...\n")

        for sample in samples_to_generate:
            try:
                print(f"🎤 {sample['category']}: {sample['voice']}")

                synthesis_input = texttospeech.SynthesisInput(text=test_text)
                voice = texttospeech.VoiceSelectionParams(
                    language_code="pt-BR", name=sample["voice"]
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=1.0,
                    pitch=0.0,
                )

                response = client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )

                filename = f"comparison_{sample['label']}.mp3"
                output_path = project_root / filename

                with open(output_path, "wb") as f:
                    f.write(response.audio_content)

                size_kb = len(response.audio_content) / 1024
                print(f"   ✅ Saved: {filename} ({size_kb:.1f} KB)\n")

            except Exception as e:
                print(f"   ❌ Error: {e}\n")

        print("\n💡 Listen to comparison_*.mp3 files to hear quality differences!")

    except Exception as e:
        print(f"❌ Failed to generate samples: {e}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    voices = loop.run_until_complete(discover_all_voices())

    if voices:
        print("\n" + "=" * 80)
        user_input = input("\n🎧 Generate voice comparison samples? (y/n): ")
        if user_input.lower() == "y":
            loop.run_until_complete(generate_voice_samples(voices))
