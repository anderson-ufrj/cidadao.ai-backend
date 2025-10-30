"""
Agent Voice Profiles - Personality-based voice selection.

This module maps each AI agent to a specific Google Cloud TTS voice
that matches their personality, role, and communication style.

Each agent has:
- Unique voice (gender, quality, style)
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
    NEURAL2 = "neural2"  # Latest, most natural


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


# ============================================================================
# Agent Voice Profiles - Brazilian AI Agents
# ============================================================================

AGENT_VOICE_PROFILES = {
    # ========================================================================
    # Master Orchestrator
    # ========================================================================
    "abaporu": AgentVoiceProfile(
        agent_id="abaporu",
        agent_name="Abaporu (Tarsila do Amaral)",
        voice_name="pt-BR-Neural2-B",  # Male, very natural
        gender=VoiceGender.MALE,
        quality=VoiceQuality.NEURAL2,
        speaking_rate=1.0,  # Normal pace - calm orchestrator
        pitch=0.0,  # Neutral pitch - authoritative
        description="Voz masculina autoritária e calma, refletindo a liderança do "
        "orquestrador mestre. Tom neutro que transmite confiança e controle.",
        personality_traits=["Leader", "Strategic", "Calm", "Authoritative"],
    ),
    # ========================================================================
    # Analysis & Investigation
    # ========================================================================
    "zumbi": AgentVoiceProfile(
        agent_id="zumbi",
        agent_name="Zumbi dos Palmares",
        voice_name="pt-BR-Wavenet-B",  # Male, professional
        gender=VoiceGender.MALE,
        quality=VoiceQuality.WAVENET,
        speaking_rate=0.95,  # Slightly slower - careful analysis
        pitch=-2.0,  # Slightly deeper - serious tone
        description="Voz masculina profunda e séria, transmitindo a gravidade da "
        "análise de anomalias. Tom mais grave para comunicar autoridade.",
        personality_traits=["Fighter", "Analytical", "Serious", "Determined"],
    ),
    "anita": AgentVoiceProfile(
        agent_id="anita",
        agent_name="Anita Garibaldi",
        voice_name="pt-BR-Neural2-A",  # Female, very natural
        gender=VoiceGender.FEMALE,
        quality=VoiceQuality.NEURAL2,
        speaking_rate=1.05,  # Slightly faster - energetic analysis
        pitch=1.0,  # Slightly higher - energetic tone
        description="Voz feminina energética e clara, refletindo a paixão de Anita "
        "na análise estatística. Tom animado para comunicar descobertas.",
        personality_traits=["Passionate", "Analytical", "Revolutionary", "Bold"],
    ),
    "oxossi": AgentVoiceProfile(
        agent_id="oxossi",
        agent_name="Oxóssi (Hunter)",
        voice_name="pt-BR-Wavenet-B",  # Male, professional
        gender=VoiceGender.MALE,
        quality=VoiceQuality.WAVENET,
        speaking_rate=0.90,  # Slower - careful hunter
        pitch=-1.0,  # Slightly deeper - focused
        description="Voz masculina focada e precisa, como um caçador rastreando fraudes. "
        "Tom sério e calculado para investigações.",
        personality_traits=["Hunter", "Precise", "Patient", "Strategic"],
    ),
    "lampiao": AgentVoiceProfile(
        agent_id="lampiao",
        agent_name="Lampião (Cangaceiro)",
        voice_name="pt-BR-Wavenet-B",  # Male, professional
        gender=VoiceGender.MALE,
        quality=VoiceQuality.WAVENET,
        speaking_rate=1.1,  # Faster - agile like cangaceiro
        pitch=-3.0,  # Deeper - rugged character
        description="Voz masculina marcante e ágil, como o famoso cangaceiro. "
        "Tom mais grave com ritmo rápido para análise regional.",
        personality_traits=["Agile", "Bold", "Regional", "Independent"],
    ),
    # ========================================================================
    # Routing & Orchestration
    # ========================================================================
    "ayrton_senna": AgentVoiceProfile(
        agent_id="ayrton_senna",
        agent_name="Ayrton Senna",
        voice_name="pt-BR-Neural2-B",  # Male, very natural
        gender=VoiceGender.MALE,
        quality=VoiceQuality.NEURAL2,
        speaking_rate=1.15,  # Faster - quick like F1 driver
        pitch=2.0,  # Slightly higher - energetic
        description="Voz masculina rápida e energética, como o lendário piloto. "
        "Ritmo acelerado refletindo decisões rápidas de roteamento.",
        personality_traits=["Fast", "Precise", "Competitive", "Legendary"],
    ),
    # ========================================================================
    # Communication & Reporting
    # ========================================================================
    "tiradentes": AgentVoiceProfile(
        agent_id="tiradentes",
        agent_name="Tiradentes",
        voice_name="pt-BR-Wavenet-B",  # Male, professional
        gender=VoiceGender.MALE,
        quality=VoiceQuality.WAVENET,
        speaking_rate=0.95,  # Slightly slower - formal reports
        pitch=-1.0,  # Slightly deeper - official tone
        description="Voz masculina formal e clara para relatórios oficiais. "
        "Tom sério e profissional, como documentos governamentais.",
        personality_traits=["Revolutionary", "Formal", "Clear", "Official"],
    ),
    "oscar_niemeyer": AgentVoiceProfile(
        agent_id="oscar_niemeyer",
        agent_name="Oscar Niemeyer",
        voice_name="pt-BR-Neural2-B",  # Male, very natural
        gender=VoiceGender.MALE,
        quality=VoiceQuality.NEURAL2,
        speaking_rate=0.90,  # Slower - contemplative artist
        pitch=0.0,  # Neutral - aesthetic focus
        description="Voz masculina calma e contemplativa, como o arquiteto. "
        "Tom suave para descrever visualizações e padrões.",
        personality_traits=["Creative", "Contemplative", "Artistic", "Visionary"],
    ),
    "machado": AgentVoiceProfile(
        agent_id="machado",
        agent_name="Machado de Assis",
        voice_name="pt-BR-Wavenet-B",  # Male, professional
        gender=VoiceGender.MALE,
        quality=VoiceQuality.WAVENET,
        speaking_rate=0.85,  # Slower - literary style
        pitch=-2.0,  # Deeper - wise narrator
        description="Voz masculina sábia e narrativa, como o grande escritor. "
        "Tom profundo e pausado para análise textual sofisticada.",
        personality_traits=["Wise", "Literary", "Analytical", "Sophisticated"],
    ),
    "drummond": AgentVoiceProfile(
        agent_id="drummond",
        agent_name="Carlos Drummond de Andrade",
        voice_name="pt-BR-Wavenet-A",  # Female, natural (default)
        gender=VoiceGender.FEMALE,
        quality=VoiceQuality.WAVENET,
        speaking_rate=1.0,  # Normal - conversational
        pitch=0.0,  # Neutral - friendly
        description="Voz feminina calorosa e conversacional, como o poeta do povo. "
        "Tom amigável e acessível para comunicação natural.",
        personality_traits=["Poetic", "Conversational", "Warm", "Accessible"],
    ),
    # ========================================================================
    # Governance & Security
    # ========================================================================
    "bonifacio": AgentVoiceProfile(
        agent_id="bonifacio",
        agent_name="José Bonifácio",
        voice_name="pt-BR-Wavenet-B",  # Male, professional
        gender=VoiceGender.MALE,
        quality=VoiceQuality.WAVENET,
        speaking_rate=0.90,  # Slower - formal legal analysis
        pitch=-2.0,  # Deeper - authoritative legal voice
        description="Voz masculina autoritária e formal, como o Patriarca. "
        "Tom grave e sério para análise de políticas e legislação.",
        personality_traits=["Authoritative", "Legal", "Formal", "Principled"],
    ),
    "maria_quiteria": AgentVoiceProfile(
        agent_id="maria_quiteria",
        agent_name="Maria Quitéria",
        voice_name="pt-BR-Neural2-A",  # Female, very natural
        gender=VoiceGender.FEMALE,
        quality=VoiceQuality.NEURAL2,
        speaking_rate=1.0,  # Normal - alert and clear
        pitch=0.0,  # Neutral - professional security
        description="Voz feminina firme e profissional, como a heroína militar. "
        "Tom claro e alerta para auditorias de segurança.",
        personality_traits=["Brave", "Vigilant", "Professional", "Strong"],
    ),
    # ========================================================================
    # Memory & Learning
    # ========================================================================
    "nana": AgentVoiceProfile(
        agent_id="nana",
        agent_name="Nanã (Orixá da Sabedoria)",
        voice_name="pt-BR-Wavenet-A",  # Female, natural
        gender=VoiceGender.FEMALE,
        quality=VoiceQuality.WAVENET,
        speaking_rate=0.85,  # Slower - wise and ancient
        pitch=-1.0,  # Slightly deeper - wisdom
        description="Voz feminina sábia e calma, como a orixá anciã. "
        "Tom profundo e pausado transmitindo sabedoria acumulada.",
        personality_traits=["Wise", "Ancient", "Calm", "Knowledgeable"],
    ),
    # ========================================================================
    # ML & Prediction
    # ========================================================================
    "ceuci": AgentVoiceProfile(
        agent_id="ceuci",
        agent_name="Céuci (Indigenous Leader)",
        voice_name="pt-BR-Neural2-A",  # Female, very natural
        gender=VoiceGender.FEMALE,
        quality=VoiceQuality.NEURAL2,
        speaking_rate=0.95,  # Slightly slower - mystical predictions
        pitch=1.0,  # Slightly higher - ethereal quality
        description="Voz feminina suave e mística, como a líder indígena. "
        "Tom etéreo para previsões e insights futuros.",
        personality_traits=["Mystical", "Visionary", "Indigenous", "Prophetic"],
    ),
    "obaluaie": AgentVoiceProfile(
        agent_id="obaluaie",
        agent_name="Obaluaiê (Orixá da Cura)",
        voice_name="pt-BR-Wavenet-B",  # Male, professional
        gender=VoiceGender.MALE,
        quality=VoiceQuality.WAVENET,
        speaking_rate=0.90,  # Slower - healing deliberation
        pitch=-3.0,  # Deeper - mysterious healer
        description="Voz masculina grave e misteriosa, como o orixá curador. "
        "Tom profundo para detectar e 'curar' corrupção.",
        personality_traits=["Healer", "Mysterious", "Patient", "Transformative"],
    ),
    # ========================================================================
    # Social Justice
    # ========================================================================
    "dandara": AgentVoiceProfile(
        agent_id="dandara",
        agent_name="Dandara dos Palmares",
        voice_name="pt-BR-Neural2-A",  # Female, very natural
        gender=VoiceGender.FEMALE,
        quality=VoiceQuality.NEURAL2,
        speaking_rate=1.05,  # Slightly faster - passionate activist
        pitch=2.0,  # Higher - energetic justice
        description="Voz feminina forte e apaixonada, como a guerreira de Palmares. "
        "Tom energético para justiça social e equidade.",
        personality_traits=["Warrior", "Passionate", "Just", "Fierce"],
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
        AgentVoiceProfile with voice configuration

    Raises:
        KeyError: If agent_id not found
    """
    if agent_id not in AGENT_VOICE_PROFILES:
        # Return default profile (Drummond) for unknown agents
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
