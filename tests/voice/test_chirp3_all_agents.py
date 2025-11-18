#!/usr/bin/env python3
"""
Test ALL 16 agents with their new Chirp3-HD voices.
Generate samples showcasing personality variety.
"""

import os

# Add project root to path
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import texttospeech_v1 as texttospeech
from google.oauth2 import service_account

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.agent_voice_profiles import get_agent_voice_profile

# Load environment
load_dotenv()

# Get credentials
credentials_path = os.getenv(
    "GOOGLE_CREDENTIALS_PATH", "config/credentials/google-cloud-key.json"
)
if not Path(credentials_path).is_absolute():
    credentials_path = project_root / credentials_path


def test_all_chirp3_agents():
    """Test all 16 agents with Chirp3-HD voices."""
    print("🎭 Testing ALL 16 Agents with Chirp3-HD Premium Voices")
    print("=" * 80)

    try:
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        client = texttospeech.TextToSpeechClient(credentials=credentials)

        # Test text
        base_text = "Olá, sou {} do Cidadão ponto AI. {}"

        # Agent-specific texts
        agent_texts = {
            "abaporu": "Coordeno todos os agentes com sabedoria estratégica.",
            "zumbi": "Detecto anomalias com precisão implacável.",
            "anita": "Analiso estatísticas com paixão revolucionária.",
            "oxossi": "Caço fraudes com paciência e foco absoluto.",
            "lampiao": "Revelo desigualdades ocultas no sertão.",
            "ayrton_senna": "Tomo decisões em velocidade recorde.",
            "tiradentes": "Gero relatórios claros e confiáveis.",
            "oscar_niemeyer": "Crio visualizações encantadoras.",
            "machado": "Analiso textos com sabedoria literária.",
            "drummond": "Comunico como poeta do povo.",
            "bonifacio": "Avalio legalidade com rigor patriarcal.",
            "maria_quiteria": "Audito segurança com vigilância militar.",
            "nana": "Armazeno sabedoria ancestral.",
            "ceuci": "Prevejo padrões com visão mística.",
            "obaluaie": "Detecto corrupção com poder transformador.",
            "dandara": "Luto por justiça social com paixão ardente.",
        }

        results = []

        print("\n🎤 Generating voice samples for all agents...\n")

        for agent_id in agent_texts.keys():
            try:
                profile = get_agent_voice_profile(agent_id)

                text = base_text.format(profile.agent_name, agent_texts[agent_id])

                print(f"🎭 {profile.agent_name}")
                print(f"   Voice: {profile.voice_name}")
                print(f"   Mythology: {profile.mythological_meaning}")
                print(f"   Gender: {profile.gender.value.title()}")
                print(f"   Speed: {profile.speaking_rate}x")
                print(f"   Pitch: {profile.pitch:+.1f}")

                synthesis_input = texttospeech.SynthesisInput(text=text)
                voice = texttospeech.VoiceSelectionParams(
                    language_code="pt-BR", name=profile.voice_name
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=profile.speaking_rate,
                    pitch=profile.pitch,
                )

                response = client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )

                # Save with descriptive name
                filename = (
                    f"chirp3_{agent_id}_{profile.voice_name.split('-')[-1].lower()}.mp3"
                )
                output_path = project_root / filename

                with open(output_path, "wb") as f:
                    f.write(response.audio_content)

                size_kb = len(response.audio_content) / 1024
                print(f"   ✅ Saved: {filename} ({size_kb:.1f} KB)\n")

                results.append(
                    {
                        "agent": agent_id,
                        "voice": profile.voice_name,
                        "file": filename,
                        "success": True,
                    }
                )

            except Exception as e:
                print(f"   ❌ Error: {e}\n")
                results.append(
                    {"agent": agent_id, "voice": None, "file": None, "success": False}
                )

        # Summary
        print("=" * 80)
        print("📊 GENERATION SUMMARY")
        print("=" * 80)

        successful = sum(1 for r in results if r["success"])
        total = len(results)

        print(f"\n✅ Successful: {successful}/{total} agents")

        # Gender distribution
        from src.services.agent_voice_profiles import VoiceGender, get_agents_by_gender

        male_agents = get_agents_by_gender(VoiceGender.MALE)
        female_agents = get_agents_by_gender(VoiceGender.FEMALE)

        print(f"\n👥 Gender Distribution:")
        print(
            f"   Male: {len([a for a in male_agents if a.agent_id in agent_texts])} agents"
        )
        print(
            f"   Female: {len([a for a in female_agents if a.agent_id in agent_texts])} agents"
        )

        # Speed analysis
        from src.services.agent_voice_profiles import get_voice_statistics

        stats = get_voice_statistics()

        print(f"\n⚡ Speed Variation:")
        print(
            f"   Fastest: {stats['fastest_agent']} ({agent_texts[stats['fastest_agent']]})"
        )
        print(
            f"   Slowest: {stats['slowest_agent']} ({agent_texts[stats['slowest_agent']]})"
        )

        print(f"\n🎵 Pitch Variation:")
        print(f"   Deepest: {stats['deepest_voice']} (most grave/serious)")
        print(f"   Highest: {stats['highest_voice']} (most energetic)")

        print("\n🌟 Chirp3-HD Benefits:")
        print("   ✅ 16 unique premium voices (vs 2 with Neural2)")
        print("   ✅ Each agent has distinct vocal identity")
        print("   ✅ Mythological names add character depth")
        print("   ✅ Ultra-natural Brazilian Portuguese")
        print("   ✅ Perfect personality matching")

        print("\n💡 Listen to the files to hear the amazing variety!")
        print(
            "   Each agent now sounds completely unique and matches their personality!"
        )

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_all_chirp3_agents()
