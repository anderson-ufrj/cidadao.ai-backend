"""
Agent Voice Profiles - Chirp3-HD Premium Edition.

This module maps each AI agent to a specific Google Cloud Chirp3-HD voice
that matches their personality, role, and communication style.

Chirp3-HD voices are Google's latest premium multilingual voices with:
- Ultra-high quality and naturalness
- Excellent Brazilian Portuguese pronunciation
- Wide variety (30 voices: 16 male, 14 female)
- Unique mythological names (stars, moons, deities)

Each agent has:
- Unique Chirp3-HD voice (gender, mythological name)
- Speaking rate (faster/slower based on personality)
- Pitch adjustment (higher/lower for character)
- Voice description explaining the choice
"""

from dataclasses import dataclass
from enum import Enum


class VoiceQuality(Enum):
    """Voice quality levels."""

    STANDARD = "standard"  # Basic quality
    WAVENET = "wavenet"  # High quality neural
    NEURAL2 = "neural2"  # Very high quality
    CHIRP3_HD = "chirp3-hd"  # Premium quality (CURRENT)


class VoiceGender(Enum):
    """Voice gender options."""

    FEMALE = "female"
    MALE = "male"


@dataclass
class AgentVoiceProfile:
    """Voice profile configuration for an agent."""

    agent_id: str
    agent_name: str
    voice_name: str
    gender: VoiceGender
    quality: VoiceQuality
    speaking_rate: float  # 0.25-4.0 (1.0 = normal)
    pitch: float  # -20.0 to 20.0 (0.0 = normal)
    description: str
    personality_traits: list[str]
    mythological_meaning: str  # Meaning of the Chirp3-HD name


# ============================================================================
# Agent Voice Profiles - Brazilian AI Agents with Chirp3-HD
# ============================================================================

AGENT_VOICE_PROFILES = {
    # ========================================================================
    # Master Orchestrator
    # ========================================================================
    "abaporu": AgentVoiceProfile(
        agent_id="abaporu",
        agent_name="Abaporu (Tarsila do Amaral)",
        voice_name="pt-BR-Chirp3-HD-Rasalgethi",  # Male, "Head of the Serpent Charmer"
        gender=VoiceGender.MALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=1.0,  # Normal pace - calm orchestrator
        pitch=0.0,  # Chirp3-HD no pitch - Neutral pitch - authoritative
        description="Voz masculina profunda e comandante, como quem domina serpentes. "
        "Perfeita para o orquestrador mestre que coordena todos os agentes.",
        personality_traits=["Leader", "Strategic", "Calm", "Authoritative"],
        mythological_meaning="Rasalgethi = Cabeça do Encantador de Serpentes (estrela α Herculis)",
    ),
    # ========================================================================
    # Analysis & Investigation
    # ========================================================================
    "zumbi": AgentVoiceProfile(
        agent_id="zumbi",
        agent_name="Zumbi dos Palmares",
        voice_name="pt-BR-Chirp3-HD-Fenrir",  # Male, Norse wolf who breaks chains
        gender=VoiceGender.MALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=0.95,  # Slightly slower - careful analysis
        pitch=0.0,  # Chirp3-HD no pitch - Neutral (Chirp3-HD doesn't support pitch adjustment)
        description="Voz masculina feroz e determinada, como o lobo Fenrir que rompe correntes. "
        "Perfeita para quem detecta e destrói anomalias.",
        personality_traits=["Fighter", "Analytical", "Serious", "Determined"],
        mythological_meaning="Fenrir = Lobo gigante da mitologia nórdica que rompe todas as correntes",
    ),
    "anita": AgentVoiceProfile(
        agent_id="anita",
        agent_name="Anita Garibaldi",
        voice_name="pt-BR-Chirp3-HD-Callirrhoe",  # Female, "Beautiful Flow"
        gender=VoiceGender.FEMALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=1.05,  # Slightly faster - energetic analysis
        pitch=0.0,  # Chirp3-HD no pitch - Slightly higher - energetic tone
        description="Voz feminina fluida e bela como córrego cristalino. "
        "Energia natural que flui através da análise estatística.",
        personality_traits=["Passionate", "Analytical", "Revolutionary", "Bold"],
        mythological_meaning="Callirrhoe = Belo Fluxo (ninfa grega, lua de Júpiter)",
    ),
    "oxossi": AgentVoiceProfile(
        agent_id="oxossi",
        agent_name="Oxóssi (Hunter)",
        voice_name="pt-BR-Chirp3-HD-Orus",  # Male, Egyptian sky deity
        gender=VoiceGender.MALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=0.90,  # Slower - patient hunter
        pitch=0.0,  # Chirp3-HD no pitch - Chirp3-HD no pitch - Slightly deeper - focused
        description="Voz masculina celestial e vigilante como o deus do céu Hórus. "
        "Olhos aguçados que tudo veem, caçador paciente de fraudes.",
        personality_traits=["Hunter", "Precise", "Patient", "Strategic"],
        mythological_meaning="Orus (Hórus) = Deus egípcio do céu, senhor dos céus",
    ),
    "lampiao": AgentVoiceProfile(
        agent_id="lampiao",
        agent_name="Lampião (Cangaceiro)",
        voice_name="pt-BR-Chirp3-HD-Sadachbia",  # Male, "Lucky Star of Hidden Things"
        gender=VoiceGender.MALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=1.1,  # Faster - agile like cangaceiro
        pitch=0.0,  # Chirp3-HD no pitch - Chirp3-HD no pitch - Deeper - rugged character
        description="Voz masculina áspera e rápida, a sorte das coisas ocultas. "
        "Revela desigualdades escondidas no sertão.",
        personality_traits=["Agile", "Bold", "Regional", "Independent"],
        mythological_meaning="Sadachbia = Estrela da Sorte das Coisas Ocultas (γ Aquarii)",
    ),
    # ========================================================================
    # Routing & Orchestration
    # ========================================================================
    "ayrton_senna": AgentVoiceProfile(
        agent_id="ayrton_senna",
        agent_name="Ayrton Senna",
        voice_name="pt-BR-Chirp3-HD-Algenib",  # Male, "The Side" (Pegasus)
        gender=VoiceGender.MALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=1.15,  # Fastest - quick like F1 driver
        pitch=0.0,  # Chirp3-HD no pitch - Higher - energetic
        description="Voz masculina veloz como a asa de Pégaso. "
        "Velocidade lendária nas decisões de roteamento.",
        personality_traits=["Fast", "Precise", "Competitive", "Legendary"],
        mythological_meaning="Algenib = Flanco/Lado (estrela γ Pegasi, asa do cavalo alado)",
    ),
    # ========================================================================
    # Communication & Reporting
    # ========================================================================
    "tiradentes": AgentVoiceProfile(
        agent_id="tiradentes",
        agent_name="Tiradentes",
        voice_name="pt-BR-Chirp3-HD-Schedar",  # Male, "The Breast" (Cassiopeia)
        gender=VoiceGender.MALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=0.95,  # Slightly slower - formal reports
        pitch=0.0,  # Chirp3-HD no pitch - Chirp3-HD no pitch - Slightly deeper - official tone
        description="Voz masculina formal e maternal como Cassiopeia. "
        "Nutre os cidadãos com informação clara e confiável.",
        personality_traits=["Revolutionary", "Formal", "Clear", "Official"],
        mythological_meaning="Schedar = Peito (estrela α Cassiopeiae, rainha etíope)",
    ),
    "oscar_niemeyer": AgentVoiceProfile(
        agent_id="oscar_niemeyer",
        agent_name="Oscar Niemeyer",
        voice_name="pt-BR-Chirp3-HD-Puck",  # Male, Shakespeare's fairy
        gender=VoiceGender.MALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=0.90,  # Slower - contemplative artist
        pitch=0.0,  # Chirp3-HD no pitch - Neutral - aesthetic focus
        description="Voz masculina travessa e criativa como a fada de Shakespeare. "
        "Brincalhona ao criar visualizações encantadoras.",
        personality_traits=["Creative", "Contemplative", "Artistic", "Visionary"],
        mythological_meaning="Puck = Fada travessa de 'Sonho de Uma Noite de Verão' (lua de Urano)",
    ),
    "machado": AgentVoiceProfile(
        agent_id="machado",
        agent_name="Machado de Assis",
        voice_name="pt-BR-Chirp3-HD-Iapetus",  # Male, Titan of mortality
        gender=VoiceGender.MALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=0.85,  # Slowest - literary wisdom
        pitch=0.0,  # Chirp3-HD no pitch - Chirp3-HD no pitch - Deeper - wise narrator
        description="Voz masculina profunda e antiga como o Titã da mortalidade. "
        "Sabedoria ancestral para análise textual sofisticada.",
        personality_traits=["Wise", "Literary", "Analytical", "Sophisticated"],
        mythological_meaning="Jápeto = Titã da mortalidade humana (pai de Prometeu, lua de Saturno)",
    ),
    "drummond": AgentVoiceProfile(
        agent_id="drummond",
        agent_name="Carlos Drummond de Andrade",
        voice_name="pt-BR-Chirp3-HD-Zephyr",  # Female, gentle west wind
        gender=VoiceGender.FEMALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=1.0,  # Normal - conversational
        pitch=0.0,  # Chirp3-HD no pitch - Neutral - friendly
        description="Voz feminina suave como brisa do oeste. "
        "Comunicação gentil e acessível, poeta do povo.",
        personality_traits=["Poetic", "Conversational", "Warm", "Accessible"],
        mythological_meaning="Zéfiro = Vento oeste gentil da primavera (mitologia grega)",
    ),
    # ========================================================================
    # Governance & Security
    # ========================================================================
    "bonifacio": AgentVoiceProfile(
        agent_id="bonifacio",
        agent_name="José Bonifácio",
        voice_name="pt-BR-Chirp3-HD-Charon",  # Male, ferryman of the dead
        gender=VoiceGender.MALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=0.90,  # Slower - formal legal analysis
        pitch=0.0,  # Chirp3-HD no pitch - Chirp3-HD no pitch - Deeper - authoritative legal voice
        description="Voz masculina solene como barqueiro dos mortos. "
        "Guia através das águas turvas da legislação.",
        personality_traits=["Authoritative", "Legal", "Formal", "Principled"],
        mythological_meaning="Caronte = Barqueiro que leva almas pelo rio Estige (lua de Plutão)",
    ),
    "maria_quiteria": AgentVoiceProfile(
        agent_id="maria_quiteria",
        agent_name="Maria Quitéria",
        voice_name="pt-BR-Chirp3-HD-Despina",  # Female, "Lady"
        gender=VoiceGender.FEMALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=1.0,  # Normal - alert and clear
        pitch=0.0,  # Chirp3-HD no pitch - Neutral - professional security
        description="Voz feminina nobre e vigilante como senhora guerreira. "
        "Elegância militar em auditorias de segurança.",
        personality_traits=["Brave", "Vigilant", "Professional", "Strong"],
        mythological_meaning="Despina = Senhora/Dama (ninfa, lua de Netuno)",
    ),
    # ========================================================================
    # Memory & Learning
    # ========================================================================
    "nana": AgentVoiceProfile(
        agent_id="nana",
        agent_name="Nanã (Orixá da Sabedoria)",
        voice_name="pt-BR-Chirp3-HD-Leda",  # Female, mother of Helen of Troy
        gender=VoiceGender.FEMALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=0.85,  # Slowest - wise and ancient
        pitch=0.0,  # Chirp3-HD no pitch - Chirp3-HD no pitch - Deeper - wisdom
        description="Voz feminina ancestral como mãe de Helena. "
        "Sabedoria que deu origem à maior história da antiguidade.",
        personality_traits=["Wise", "Ancient", "Calm", "Knowledgeable"],
        mythological_meaning="Leda = Rainha visitada por Zeus, mãe de Helena de Troia (lua de Júpiter)",
    ),
    # ========================================================================
    # ML & Prediction
    # ========================================================================
    "ceuci": AgentVoiceProfile(
        agent_id="ceuci",
        agent_name="Céuci (Indigenous Leader)",
        voice_name="pt-BR-Chirp3-HD-Aoede",  # Female, Muse of song
        gender=VoiceGender.FEMALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=0.95,  # Slightly slower - mystical predictions
        pitch=0.0,  # Chirp3-HD no pitch - Slightly higher - ethereal quality
        description="Voz feminina melódica como musa do canto. "
        "Previsões fluem como canção mística.",
        personality_traits=["Mystical", "Visionary", "Indigenous", "Prophetic"],
        mythological_meaning="Aoede = Musa do Canto (uma das três musas originais, lua de Júpiter)",
    ),
    "obaluaie": AgentVoiceProfile(
        agent_id="obaluaie",
        agent_name="Obaluaiê (Orixá da Cura)",
        voice_name="pt-BR-Chirp3-HD-Enceladus",  # Male, buried giant
        gender=VoiceGender.MALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=0.90,  # Slower - healing deliberation
        pitch=0.0,  # Chirp3-HD no pitch - Chirp3-HD no pitch - Deepest - mysterious healer
        description="Voz masculina profunda e telúrica como gigante sepultado. "
        "Poder subterrâneo que cura e transforma corrupção.",
        personality_traits=["Healer", "Mysterious", "Patient", "Transformative"],
        mythological_meaning="Encélado = Gigante sepultado sob o Etna, causa terremotos (lua de Saturno)",
    ),
    # ========================================================================
    # Social Justice
    # ========================================================================
    "dandara": AgentVoiceProfile(
        agent_id="dandara",
        agent_name="Dandara dos Palmares",
        voice_name="pt-BR-Chirp3-HD-Gacrux",  # Female, "Cross" (Southern Cross)
        gender=VoiceGender.FEMALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=1.05,  # Slightly faster - passionate activist
        pitch=0.0,  # Chirp3-HD no pitch - Highest - energetic justice
        description="Voz feminina radiante como estrela do Cruzeiro do Sul. "
        "Guia para justiça social no hemisfério sul.",
        personality_traits=["Warrior", "Passionate", "Just", "Fierce"],
        mythological_meaning="Gacrux = Gama Crucis, estrela vermelha brilhante do Cruzeiro do Sul",
    ),
    # ========================================================================
    # Additional Tier 2 Agents
    # ========================================================================
    "additional_male_1": AgentVoiceProfile(
        agent_id="additional_male_1",
        agent_name="Reserve Male Voice 1",
        voice_name="pt-BR-Chirp3-HD-Achird",  # Male
        gender=VoiceGender.MALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=1.0,
        pitch=0.0,
        description="Voz masculina reserva para futuros agentes.",
        personality_traits=["Versatile"],
        mythological_meaning="Achird = Estrela η Cassiopeiae",
    ),
    "additional_male_2": AgentVoiceProfile(
        agent_id="additional_male_2",
        agent_name="Reserve Male Voice 2",
        voice_name="pt-BR-Chirp3-HD-Algieba",  # Male
        gender=VoiceGender.MALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=1.0,
        pitch=0.0,
        description="Voz masculina reserva para futuros agentes.",
        personality_traits=["Versatile"],
        mythological_meaning="Algieba = Testa do Leão (γ Leonis)",
    ),
    "additional_female_1": AgentVoiceProfile(
        agent_id="additional_female_1",
        agent_name="Reserve Female Voice 1",
        voice_name="pt-BR-Chirp3-HD-Achernar",  # Female
        gender=VoiceGender.FEMALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=1.0,
        pitch=0.0,
        description="Voz feminina reserva para futuros agentes.",
        personality_traits=["Versatile"],
        mythological_meaning="Achernar = Fim do Rio (α Eridani)",
    ),
    "additional_female_2": AgentVoiceProfile(
        agent_id="additional_female_2",
        agent_name="Reserve Female Voice 2",
        voice_name="pt-BR-Chirp3-HD-Autonoe",  # Female
        gender=VoiceGender.FEMALE,
        quality=VoiceQuality.CHIRP3_HD,
        speaking_rate=1.0,
        pitch=0.0,
        description="Voz feminina reserva para futuros agentes.",
        personality_traits=["Versatile"],
        mythological_meaning="Autonoe = Mente Própria (ninfa, lua de Júpiter)",
    ),
}


# ============================================================================
# Voice Selection Functions
# ============================================================================


def get_agent_voice_profile(agent_id: str) -> AgentVoiceProfile:
    """
    Get voice profile for a specific agent.

    Args:
        agent_id: Agent identifier (e.g., "drummond", "zumbi")

    Returns:
        AgentVoiceProfile with Chirp3-HD voice configuration

    Raises:
        KeyError: If agent_id not found
    """
    if agent_id not in AGENT_VOICE_PROFILES:
        # Return default profile (Drummond with Zephyr voice)
        return AGENT_VOICE_PROFILES["drummond"]

    return AGENT_VOICE_PROFILES[agent_id]


def list_all_agent_voices() -> dict[str, AgentVoiceProfile]:
    """
    List all agent voice profiles.

    Returns:
        Dictionary mapping agent_id to AgentVoiceProfile
    """
    return AGENT_VOICE_PROFILES.copy()


def get_agents_by_voice_quality(quality: VoiceQuality) -> list[AgentVoiceProfile]:
    """
    Get all agents using a specific voice quality.

    Args:
        quality: Voice quality to filter by

    Returns:
        List of AgentVoiceProfile matching the quality
    """
    return [
        profile
        for profile in AGENT_VOICE_PROFILES.values()
        if profile.quality == quality
    ]


def get_agents_by_gender(gender: VoiceGender) -> list[AgentVoiceProfile]:
    """
    Get all agents with a specific voice gender.

    Args:
        gender: Voice gender to filter by

    Returns:
        List of AgentVoiceProfile matching the gender
    """
    return [
        profile for profile in AGENT_VOICE_PROFILES.values() if profile.gender == gender
    ]


# ============================================================================
# Voice Profile Statistics
# ============================================================================


def get_voice_statistics() -> dict:
    """
    Get statistics about agent voice profiles.

    Returns:
        Dictionary with voice usage statistics
    """
    total = len(AGENT_VOICE_PROFILES)

    # Count by quality
    quality_counts = {}
    for quality in VoiceQuality:
        count = len(get_agents_by_voice_quality(quality))
        quality_counts[quality.value] = count

    # Count by gender
    gender_counts = {}
    for gender in VoiceGender:
        count = len(get_agents_by_gender(gender))
        gender_counts[gender.value] = count

    # Average speaking rates
    rates = [p.speaking_rate for p in AGENT_VOICE_PROFILES.values()]
    avg_rate = sum(rates) / len(rates) if rates else 1.0

    # Average pitch
    pitches = [p.pitch for p in AGENT_VOICE_PROFILES.values()]
    avg_pitch = sum(pitches) / len(pitches) if pitches else 0.0

    return {
        "total_agents": total,
        "quality_distribution": quality_counts,
        "gender_distribution": gender_counts,
        "average_speaking_rate": round(avg_rate, 2),
        "average_pitch": round(avg_pitch, 2),
        "fastest_agent": max(
            AGENT_VOICE_PROFILES.items(), key=lambda x: x[1].speaking_rate
        )[0],
        "slowest_agent": min(
            AGENT_VOICE_PROFILES.items(), key=lambda x: x[1].speaking_rate
        )[0],
        "deepest_voice": min(AGENT_VOICE_PROFILES.items(), key=lambda x: x[1].pitch)[0],
        "highest_voice": max(AGENT_VOICE_PROFILES.items(), key=lambda x: x[1].pitch)[0],
    }
