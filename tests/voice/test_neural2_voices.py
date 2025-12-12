#!/usr/bin/env python3
"""
Test Neural2 voices for different agents.

Generates audio samples demonstrating:
- Voice quality (ultra-natural Neural2)
- Personality variations (speaking rate, pitch)
- Gender diversity (male/female)
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.services.agent_voice_profiles import get_agent_voice_profile
from src.services.voice_service import VoiceService


async def test_agent_voices():
    """Test Neural2 voices for different agents."""
    print("🎙️  Testing Neural2 Voices - Ultra Natural Quality")
    print("=" * 60)

    # Initialize voice service
    voice_service = VoiceService()

    # Test different agents showcasing variety
    test_agents = [
        {
            "agent_id": "drummond",
            "text": "Olá, sou Drummond, o poeta do povo. Minha voz é calorosa e conversacional, perfeita para comunicação natural com os cidadãos.",
        },
        {
            "agent_id": "ayrton_senna",
            "text": "Aqui é Ayrton Senna! Sou rápido e energético nas decisões, assim como nas pistas. Velocidade é essencial!",
        },
        {
            "agent_id": "machado",
            "text": "Machado de Assis ao seu dispor. Minha voz é sábia e pausada, ideal para análises textuais sofisticadas e narrativas profundas.",
        },
        {
            "agent_id": "zumbi",
            "text": "Zumbi dos Palmares. Voz séria e profunda para análise de anomalias. Gravidade é necessária ao comunicar fraudes.",
        },
        {
            "agent_id": "anita",
            "text": "Anita Garibaldi! Energética e apaixonada na análise estatística. Descobertas devem ser comunicadas com entusiasmo!",
        },
    ]

    results = []

    for agent_data in test_agents:
        agent_id = agent_data["agent_id"]
        text = agent_data["text"]

        print(f"\n🎭 Agent: {agent_id.upper()}")
        print(f"📝 Text: {text[:80]}...")

        # Get voice profile
        profile = get_agent_voice_profile(agent_id)
        print(f"🎤 Voice: {profile.voice_name}")
        print(f"   Gender: {profile.gender.value}")
        print(f"   Speed: {profile.speaking_rate}x")
        print(f"   Pitch: {profile.pitch:+.1f}")
        print(f"   Traits: {', '.join(profile.personality_traits)}")

        try:
            # Generate audio
            audio_content = await voice_service.text_to_speech(
                text=text,
                agent_id=agent_id,  # Automatic voice selection
            )

            if audio_content:
                # Save to file
                filename = f"test_neural2_{agent_id}.mp3"
                output_path = project_root / filename

                with open(output_path, "wb") as f:
                    f.write(audio_content)

                print(f"✅ Saved: {filename}")
                results.append({"agent": agent_id, "file": filename, "success": True})
            else:
                print(f"❌ Failed to generate audio for {agent_id}")
                results.append({"agent": agent_id, "file": None, "success": False})

        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({"agent": agent_id, "file": None, "success": False})

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    successful = sum(1 for r in results if r["success"])
    total = len(results)

    print(f"✅ Successful: {successful}/{total}")
    print("\n🎧 Generated files:")
    for result in results:
        if result["success"]:
            print(f"   - {result['file']}")

    print("\n🎯 Voice Quality Highlights:")
    print("   • Neural2 = Ultra-natural, latest technology")
    print("   • Speaking rate: 0.85x (slow) to 1.15x (fast)")
    print("   • Pitch: -3 (deep) to +2 (high)")
    print("   • Same cost as Wavenet ($16 per 1M characters)")

    print("\n💡 Play these files to hear the personality differences!")


if __name__ == "__main__":
    asyncio.run(test_agent_voices())
