#!/usr/bin/env python3
"""
Teste rápido de vozes Chirp3-HD - 4 agentes para demonstração
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from google.cloud import texttospeech_v1 as texttospeech
from google.oauth2 import service_account

from src.services.agent_voice_profiles import get_agent_voice_profile

# Get credentials
credentials_path = os.getenv(
    "GOOGLE_CREDENTIALS_PATH", "config/credentials/google-cloud-key.json"
)
if not Path(credentials_path).is_absolute():
    credentials_path = project_root / credentials_path

print("🎤 Teste de Vozes Chirp3-HD - Cidadão.AI")
print("=" * 80)

# Select 4 diverse agents to showcase
test_agents = ["zumbi", "drummond", "anita", "tiradentes"]

try:
    # Load credentials
    credentials = service_account.Credentials.from_service_account_file(
        str(credentials_path),
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    client = texttospeech.TextToSpeechClient(credentials=credentials)

    print("\n🎭 Gerando 4 amostras de voz...\n")

    for agent_id in test_agents:
        profile = get_agent_voice_profile(agent_id)

        # Create personalized text for each agent
        texts = {
            "zumbi": "Olá, sou Zumbi dos Palmares. Detectei anomalias estatísticas nos contratos governamentais.",
            "drummond": "Olá, sou Carlos Drummond de Andrade. Comunico os resultados das investigações de forma clara e acessível.",
            "anita": "Olá, sou Anita Garibaldi. Analiso padrões estatísticos e tendências nos dados de transparência.",
            "tiradentes": "Olá, sou Tiradentes. Gero relatórios técnicos detalhados sobre as investigações realizadas.",
        }

        text = texts.get(agent_id, f"Olá, sou {profile.agent_name}.")

        print(f"🎭 {profile.agent_name}")
        print(f"   Voice: {profile.voice_name}")
        print(f"   Mythology: {profile.mythological_meaning}")
        print(
            f"   Gender: {profile.gender.value.title()}, Speed: {profile.speaking_rate}x"
        )

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

        # Save with clear name
        filename = f"test_voice_{agent_id}.mp3"
        output_path = project_root / filename

        with open(output_path, "wb") as f:
            f.write(response.audio_content)

        size_kb = len(response.audio_content) / 1024
        print(f"   ✅ Salvo: {filename} ({size_kb:.1f} KB)\n")

    print("=" * 80)
    print("✅ 4 amostras geradas com sucesso!")
    print("\n🎧 Para ouvir:")
    print("   test_voice_zumbi.mp3       - Voz masculina grave (Fenrir)")
    print("   test_voice_drummond.mp3    - Voz feminina suave (Zephyr)")
    print("   test_voice_anita.mp3       - Voz feminina enérgica (Athena)")
    print("   test_voice_tiradentes.mp3  - Voz masculina clara (Hermes)")
    print("\n💡 Cada voz tem personalidade única do Chirp3-HD!")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback

    traceback.print_exc()
