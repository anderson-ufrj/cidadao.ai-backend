#!/usr/bin/env python3
"""
Simple test of Neural2 voices for different agents.
Direct Google Cloud API usage without complex dependencies.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import texttospeech_v1 as texttospeech
from google.oauth2 import service_account

# Load environment
load_dotenv()

# Get credentials path
credentials_path = os.getenv(
    "GOOGLE_CREDENTIALS_PATH", "config/credentials/google-cloud-key.json"
)
project_root = Path(__file__).parent
if not Path(credentials_path).is_absolute():
    credentials_path = project_root / credentials_path

# Voice profiles for testing (Neural2 only)
VOICE_PROFILES = {
    "drummond": {
        "name": "Carlos Drummond de Andrade",
        "voice_name": "pt-BR-Neural2-A",  # Female, default
        "rate": 1.0,
        "pitch": 0.0,
        "text": "Olá, sou Drummond, o poeta do povo. Minha voz é calorosa e conversacional, perfeita para comunicação natural com os cidadãos.",
    },
    "ayrton_senna": {
        "name": "Ayrton Senna",
        "voice_name": "pt-BR-Neural2-B",  # Male, fast
        "rate": 1.15,
        "pitch": 2.0,
        "text": "Aqui é Ayrton Senna! Sou rápido e energético nas decisões, assim como nas pistas. Velocidade é essencial!",
    },
    "machado": {
        "name": "Machado de Assis",
        "voice_name": "pt-BR-Neural2-B",  # Male, slow
        "rate": 0.85,
        "pitch": -2.0,
        "text": "Machado de Assis ao seu dispor. Minha voz é sábia e pausada, ideal para análises textuais sofisticadas e narrativas profundas.",
    },
    "zumbi": {
        "name": "Zumbi dos Palmares",
        "voice_name": "pt-BR-Neural2-B",  # Male, deep
        "rate": 0.95,
        "pitch": -2.0,
        "text": "Zumbi dos Palmares. Voz séria e profunda para análise de anomalias. Gravidade é necessária ao comunicar fraudes.",
    },
    "anita": {
        "name": "Anita Garibaldi",
        "voice_name": "pt-BR-Neural2-A",  # Female, energetic
        "rate": 1.05,
        "pitch": 1.0,
        "text": "Anita Garibaldi! Energética e apaixonada na análise estatística. Descobertas devem ser comunicadas com entusiasmo!",
    },
}


async def generate_voice_samples():
    """Generate voice samples for different agents."""
    print("🎙️  Testing Neural2 Voices - Ultra Natural Quality")
    print("=" * 60)

    try:
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        # Initialize client
        client = texttospeech.TextToSpeechClient(credentials=credentials)
        print(f"✅ Connected to Google Cloud Text-to-Speech")
        print(f"   Credentials: {credentials_path.name}")
        print()

        results = []

        for agent_id, profile in VOICE_PROFILES.items():
            print(f"🎭 Agent: {agent_id.upper()}")
            print(f"   Name: {profile['name']}")
            print(f"   Voice: {profile['voice_name']}")
            print(f"   Speed: {profile['rate']}x")
            print(f"   Pitch: {profile['pitch']:+.1f}")
            print(f"📝 Text: {profile['text'][:80]}...")

            try:
                # Prepare synthesis input
                synthesis_input = texttospeech.SynthesisInput(text=profile["text"])

                # Configure voice
                voice = texttospeech.VoiceSelectionParams(
                    language_code="pt-BR",
                    name=profile["voice_name"],
                )

                # Configure audio
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=profile["rate"],
                    pitch=profile["pitch"],
                )

                # Generate speech
                response = client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config,
                )

                # Save to file
                filename = f"neural2_{agent_id}.mp3"
                output_path = project_root / filename

                with open(output_path, "wb") as f:
                    f.write(response.audio_content)

                file_size = len(response.audio_content) / 1024  # KB
                print(f"✅ Saved: {filename} ({file_size:.1f} KB)")
                results.append({"agent": agent_id, "file": filename, "success": True})

            except Exception as e:
                print(f"❌ Error: {e}")
                results.append({"agent": agent_id, "file": None, "success": False})

            print()

        # Summary
        print("=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)

        successful = sum(1 for r in results if r["success"])
        total = len(results)

        print(f"✅ Successful: {successful}/{total}")
        print(f"\n🎧 Generated files:")
        for result in results:
            if result["success"]:
                print(f"   - {result['file']}")

        print("\n🎯 Neural2 Voice Quality Features:")
        print("   • Ultra-natural speech (latest Google technology)")
        print("   • Speaking rate: 0.85x (contemplative) to 1.15x (energetic)")
        print("   • Pitch: -2 (deep/wise) to +2 (high/energetic)")
        print("   • Same cost as Wavenet: $16 per 1M characters")
        print("   • 2 voices: pt-BR-Neural2-A (female), pt-BR-Neural2-B (male)")

        print("\n💡 Listen to these files to hear the personality differences!")
        print("   Each agent has a unique vocal identity matching their role.")

    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print(f"\n🔍 Troubleshooting:")
        print(f"   1. Check credentials file exists: {credentials_path}")
        print(f"   2. Verify GOOGLE_CREDENTIALS_PATH in .env")
        print(f"   3. Ensure APIs are enabled in Google Cloud Console")


if __name__ == "__main__":
    asyncio.run(generate_voice_samples())
