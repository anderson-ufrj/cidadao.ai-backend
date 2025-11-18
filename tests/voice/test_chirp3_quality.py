#!/usr/bin/env python3
"""
Test Chirp3-HD voices for Brazilian Portuguese quality.

IMPORTANT: Chirp3-HD voices may be:
1. Multilingual voices that support pt-BR
2. Primarily English voices with pt-BR capability
3. Lower quality for pt-BR than native pt-BR voices

This script tests actual speech quality in Portuguese.
"""

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


def test_chirp3_portuguese():
    """Test Chirp3-HD voices with Portuguese text."""
    print("🧪 Testing Chirp3-HD Quality for Brazilian Portuguese")
    print("=" * 80)

    try:
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        client = texttospeech.TextToSpeechClient(credentials=credentials)

        # Test text with Portuguese-specific sounds
        test_texts = {
            "simple": "Olá, como vai você?",
            "complex": "Olá, sou um agente de inteligência artificial do Cidadão ponto AI. Minha missão é combater a corrupção no Brasil através da análise de contratos governamentais.",
            "portuguese_sounds": "A região, o coração, não, ação, função, investigação, conclusão.",
        }

        # Select diverse Chirp3-HD voices to test
        chirp3_voices_to_test = [
            ("pt-BR-Chirp3-HD-Achird", "MALE"),
            ("pt-BR-Chirp3-HD-Aoede", "FEMALE"),
            ("pt-BR-Chirp3-HD-Charon", "MALE"),
            ("pt-BR-Chirp3-HD-Despina", "FEMALE"),
        ]

        # Also test Neural2 for comparison
        reference_voices = [
            ("pt-BR-Neural2-B", "MALE", "Neural2"),
            ("pt-BR-Neural2-A", "FEMALE", "Neural2"),
        ]

        print("\n📋 Testing with text:")
        print(f'   "{test_texts["complex"]}"')
        print()

        results = []

        # Test Chirp3-HD voices
        print("🎙️  Testing Chirp3-HD Voices:")
        print("-" * 80)

        for voice_name, gender in chirp3_voices_to_test:
            try:
                print(f"\n   {voice_name} ({gender})")

                synthesis_input = texttospeech.SynthesisInput(
                    text=test_texts["complex"]
                )
                voice = texttospeech.VoiceSelectionParams(
                    language_code="pt-BR", name=voice_name
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=1.0,
                    pitch=0.0,
                )

                response = client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )

                # Save sample
                filename = f"chirp3_test_{voice_name.split('-')[-1].lower()}.mp3"
                output_path = project_root / filename

                with open(output_path, "wb") as f:
                    f.write(response.audio_content)

                size_kb = len(response.audio_content) / 1024
                print(f"      ✅ Generated: {filename} ({size_kb:.1f} KB)")

                results.append(
                    {
                        "voice": voice_name,
                        "category": "Chirp3-HD",
                        "gender": gender,
                        "file": filename,
                        "success": True,
                    }
                )

            except Exception as e:
                print(f"      ❌ Error: {e}")
                results.append(
                    {
                        "voice": voice_name,
                        "category": "Chirp3-HD",
                        "gender": gender,
                        "file": None,
                        "success": False,
                        "error": str(e),
                    }
                )

        # Test reference (Neural2) for comparison
        print("\n🧠 Testing Neural2 Reference Voices (for comparison):")
        print("-" * 80)

        for voice_name, gender, category in reference_voices:
            try:
                print(f"\n   {voice_name} ({gender})")

                synthesis_input = texttospeech.SynthesisInput(
                    text=test_texts["complex"]
                )
                voice = texttospeech.VoiceSelectionParams(
                    language_code="pt-BR", name=voice_name
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=1.0,
                    pitch=0.0,
                )

                response = client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )

                filename = f"reference_{voice_name.lower().replace('-', '_')}.mp3"
                output_path = project_root / filename

                with open(output_path, "wb") as f:
                    f.write(response.audio_content)

                size_kb = len(response.audio_content) / 1024
                print(f"      ✅ Generated: {filename} ({size_kb:.1f} KB)")

                results.append(
                    {
                        "voice": voice_name,
                        "category": category,
                        "gender": gender,
                        "file": filename,
                        "success": True,
                    }
                )

            except Exception as e:
                print(f"      ❌ Error: {e}")

        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)

        chirp3_success = sum(
            1 for r in results if r["category"] == "Chirp3-HD" and r["success"]
        )
        chirp3_total = sum(1 for r in results if r["category"] == "Chirp3-HD")

        print(f"\n✅ Chirp3-HD: {chirp3_success}/{chirp3_total} voices successful")

        if chirp3_success > 0:
            print("\n🎧 LISTENING TEST:")
            print("   1. Play the Chirp3-HD samples")
            print("   2. Play the Neural2 reference samples")
            print("   3. Compare:")
            print("      - Naturalness of speech")
            print(
                "      - Correct pronunciation of Portuguese sounds (ão, ção, lh, nh)"
            )
            print("      - Prosody (rhythm and intonation)")
            print("      - Overall quality")

        print("\n💡 EXPECTED OUTCOMES:")
        print("   ✅ If Chirp3-HD sounds native and natural:")
        print("      → Great option! We have 30 premium voices available")
        print("   ⚠️  If Chirp3-HD has accent or pronunciation issues:")
        print("      → Stick with Neural2/WaveNet (native Brazilian voices)")

        print("\n🎯 RECOMMENDATION WILL DEPEND ON YOUR LISTENING TEST!")

        # List generated files
        print("\n📂 Generated test files:")
        for result in results:
            if result["success"]:
                print(
                    f"   • {result['file']} - {result['category']} ({result['gender']})"
                )

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_chirp3_portuguese()
