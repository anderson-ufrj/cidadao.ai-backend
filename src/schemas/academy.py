"""
Academy Gamification Schemas.

Schemas Pydantic para validação de requests/responses da Academy.
Parceria: Neural Thinker AI Engineering + IFSULDEMINAS/LabSoft
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# =============================================================================
# ENUMS
# =============================================================================


class TrackType(str, Enum):
    """Trilhas disponíveis na Academy."""

    BACKEND = "backend"
    FRONTEND = "frontend"
    IA = "ia"
    DEVOPS = "devops"


class RankLevel(str, Enum):
    """Níveis de rank baseados em XP."""

    NOVATO = "novato"  # 0-99 XP
    APRENDIZ = "aprendiz"  # 100-499 XP
    CONTRIBUIDOR = "contribuidor"  # 500-1999 XP
    MENTOR = "mentor"  # 2000-4999 XP
    ARQUITETO = "arquiteto"  # 5000+ XP


class DifficultyLevel(str, Enum):
    """Níveis de dificuldade."""

    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class MissionCategory(str, Enum):
    """Categorias de missões."""

    BUG_FIX = "bug-fix"
    FEATURE = "feature"
    DOCS = "docs"
    TEST = "test"
    REFACTOR = "refactor"
    REVIEW = "review"
    LEARNING = "learning"


class BadgeRarity(str, Enum):
    """Raridade dos badges."""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class ConversationStatus(str, Enum):
    """Status de uma conversa."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class OnboardingStep(str, Enum):
    """Etapas do onboarding."""

    WELCOME = "welcome"
    TERMS_CONSENT = "terms_consent"
    TRACK_SELECTION = "track_selection"
    GITHUB_CONNECT = "github_connect"
    FIRST_MISSION = "first_mission"
    COMPLETED = "completed"


# =============================================================================
# TERMOS DE CONSENTIMENTO (LGPD)
# =============================================================================

TERMS_OF_CONSENT = """
## Termos de Consentimento - Cidadao.AI Academy

### Programa de Estagio Gamificado
Parceria: Neural Thinker AI Engineering + IFSULDEMINAS/LabSoft

---

### 1. Coleta de Dados
Ao participar do programa, coletamos:
- **Dados de identificação**: Nome, email, username GitHub
- **Dados de atividade**: Commits, PRs, code reviews, mensagens
- **Dados de progresso**: XP, nivel, badges, ranking

### 2. Finalidade
Seus dados serao utilizados para:
- Acompanhar seu progresso no programa
- Calcular seu ranking e recompensas
- Gerar relatórios de desempenho
- Emitir certificados de conclusão

### 3. Metricas Rastreadas (Modelo Empresa)
Como em uma empresa real, rastreamos:
- **Commits entregues**: Quantidade e qualidade
- **Pull Requests**: Abertos, aprovados, merged
- **Code Reviews**: Realizados e recebidos
- **Tempo de resposta**: Em issues e PRs
- **Consistencia**: Streak de dias ativos

### 4. Ranking e Competicao
- Rankings sao publicos entre participantes
- Sua posição e baseada em XP total
- Top performers recebem destaque especial
- Mentores podem ver seu progresso detalhado

### 5. Direitos (LGPD)
Você tem direito a:
- Acessar seus dados a qualquer momento
- Solicitar correção de dados incorretos
- Solicitar exclusao (anonimização) dos dados
- Exportar seus dados em formato aberto

### 6. Retencao
- Dados ativos: Durante participacao no programa
- Dados historicos: 5 anos apos conclusão
- Certificados: Permanente

---

Ao aceitar, você concorda com estes termos e com o
Regulamento do Programa de Estagio.
"""

RANKING_EXPLANATION = """
## Como Funciona o Ranking

### Sistema de XP (Experiencia)

| Acao | XP |
|------|-----|
| Iniciar conversa com agente | +5 |
| Enviar mensagem | +2 |
| Completar conversa | +20 |
| Avaliacao 5 estrelas | +50 |
| Commit aceito | +15 |
| PR aberto | +15 |
| PR aprovado | +30 |
| PR merged | +50 |
| Code review | +10 |
| Missao easy | +10 |
| Missao medium | +25 |
| Missao hard | +50 |
| Missao expert | +100 |
| Streak 7 dias | +50 |
| Streak 30 dias | +200 |

### Níveis de Rank

| Rank | XP Necessario | Beneficios |
|------|---------------|------------|
| Novato | 0-99 | Acesso missões easy |
| Aprendiz | 100-499 | Missões medium, mentoria mensal |
| Contribuidor | 500-1999 | Missões hard, mentoria quinzenal |
| Mentor | 2000-4999 | Pode mentorar, acesso expert |
| Arquiteto | 5000+ | Elegivel para vaga, coautoria |

### Metricas de Commits (Estilo Empresa)

Rastreamos suas contribuições como em uma empresa:
- **Frequencia**: Commits por semana
- **Qualidade**: PRs aprovados vs rejeitados
- **Colaboracao**: Code reviews realizados
- **Consistencia**: Dias consecutivos ativos

### Leaderboard

O ranking e atualizado em tempo real e considera:
1. XP total acumulado
2. Contribuições da semana
3. Streak atual
4. Qualidade das entregas
"""

WELCOME_MESSAGE = """
# Bem-vindo a Cidadao.AI Academy!

Ola! Sou o assistente da Academy, o programa de estagio gamificado
do projeto Cidadao.AI.

## O que você vai encontrar aqui:

### 1. Agentes Professores
16 agentes IA com personalidades de figuras históricas brasileiras
que vao te ensinar diferentes areas:
- **Backend**: Zumbi, Anita, Tiradentes, Bonifacio
- **Frontend**: Oscar Niemeyer, Dandara, Drummond, Machado
- **IA/ML**: Zumbi, Oxossi, Ceuci, Nana, Obaluaie
- **DevOps**: Ayrton Senna, Maria Quiteria, Abaporu

### 2. Missões
Tarefas reais do projeto que você pode completar para ganhar XP:
- Corrigir bugs
- Escrever testes
- Implementar features
- Documentar codigo

### 3. Sistema de Ranking
Suas contribuições sao rastreadas como em uma empresa:
- Commits entregues
- Pull Requests aprovados
- Code reviews realizados
- Dias consecutivos ativos

### 4. Badges e Conquistas
Colecione badges por suas conquistas:
- Primeira Conversa
- Primeiro PR
- Streak de 7 dias
- E muito mais!

---

Para comecar, preciso que você aceite os termos do programa.
"""


# =============================================================================
# CONSTANTES DE XP
# =============================================================================


class XPValues:
    """Valores de XP para diferentes acoes."""

    # Conversas
    CONVERSATION_STARTED = 5
    CONVERSATION_MESSAGE = 2
    CONVERSATION_COMPLETED = 20
    CONVERSATION_EXCELLENT = 50  # Rating 5 estrelas

    # Missões
    MISSION_EASY = 10
    MISSION_MEDIUM = 25
    MISSION_HARD = 50
    MISSION_EXPERT = 100

    # Contribuições GitHub
    PR_OPENED = 15
    PR_APPROVED = 30
    PR_MERGED = 50
    CODE_REVIEW = 10
    ISSUE_REPORTED = 5

    # Documentacao
    DOCS_CREATED = 20
    DOCS_UPDATED = 10

    # Streaks
    STREAK_7_DAYS = 50
    STREAK_30_DAYS = 200
    STREAK_100_DAYS = 1000

    # Bonus
    FIRST_CONVERSATION = 25
    FIRST_MISSION = 50
    FIRST_CONTRIBUTION = 100
    MENTOR_SESSION = 30


# =============================================================================
# RANK CONFIG
# =============================================================================


RANK_THRESHOLDS = {
    RankLevel.NOVATO: (0, 99),
    RankLevel.APRENDIZ: (100, 499),
    RankLevel.CONTRIBUIDOR: (500, 1999),
    RankLevel.MENTOR: (2000, 4999),
    RankLevel.ARQUITETO: (5000, float("inf")),
}

RANK_INFO = {
    RankLevel.NOVATO: {
        "name": "Novato",
        "color": "#6B7280",
        "icon": "seedling",
        "perks": ["Acesso as missões easy", "Canal de duvidas"],
    },
    RankLevel.APRENDIZ: {
        "name": "Aprendiz",
        "color": "#10B981",
        "icon": "leaf",
        "perks": ["Acesso as missões medium", "Mentoria mensal"],
    },
    RankLevel.CONTRIBUIDOR: {
        "name": "Contribuidor",
        "color": "#3B82F6",
        "icon": "star",
        "perks": ["Acesso as missões hard", "Mentoria quinzenal", "Badge especial"],
    },
    RankLevel.MENTOR: {
        "name": "Mentor",
        "color": "#8B5CF6",
        "icon": "crown",
        "perks": ["Pode mentorar novatos", "Acesso expert", "Carta de recomendacao"],
    },
    RankLevel.ARQUITETO: {
        "name": "Arquiteto",
        "color": "#F59E0B",
        "icon": "trophy",
        "perks": [
            "Elegivel para vaga de estagio",
            "Coautoria em artigos",
            "Mentoria 1:1",
        ],
    },
}


# =============================================================================
# AGENTES PROFESSORES
# =============================================================================


AGENT_TEACHERS = {
    "zumbi": {
        "display_name": "Zumbi dos Palmares",
        "specialty": "Detecção de anomalias e análise de dados",
        "tracks": [TrackType.BACKEND, TrackType.IA],
        "personality": "Investigador perspicaz e determinado",
        "greeting": "Ola! Sou Zumbi, especialista em encontrar anomalias. Vamos investigar juntos?",
    },
    "anita": {
        "display_name": "Anita Garibaldi",
        "specialty": "Análise de padrões e metodologia",
        "tracks": [TrackType.BACKEND, TrackType.IA],
        "personality": "Estrategista corajosa e analitica",
        "greeting": "Bem-vindo! Sou Anita, vou te ensinar a identificar padrões. Preparado?",
    },
    "tiradentes": {
        "display_name": "Tiradentes",
        "specialty": "Documentacao e relatórios",
        "tracks": [TrackType.BACKEND, TrackType.DEVOPS],
        "personality": "Comunicador eloquente e organizado",
        "greeting": "Saudações! Sou Tiradentes, mestre em comunicacao clara. Vamos documentar?",
    },
    "ayrton_senna": {
        "display_name": "Ayrton Senna",
        "specialty": "Performance e otimizacao",
        "tracks": [TrackType.BACKEND, TrackType.DEVOPS],
        "personality": "Perfeccionista focado em velocidade",
        "greeting": "E ai! Sou Senna, especialista em performance. Vamos acelerar seu codigo?",
    },
    "oscar_niemeyer": {
        "display_name": "Oscar Niemeyer",
        "specialty": "Arquitetura de software",
        "tracks": [TrackType.BACKEND, TrackType.FRONTEND],
        "personality": "Visionario criativo e elegante",
        "greeting": "Ola! Sou Niemeyer, arquiteto de sistemas. Vamos projetar algo bonito?",
    },
    "machado": {
        "display_name": "Machado de Assis",
        "specialty": "Comunicacao tecnica e documentacao",
        "tracks": [TrackType.BACKEND, TrackType.FRONTEND],
        "personality": "Escritor perspicaz e ironico",
        "greeting": "Prezado aluno! Sou Machado, vou te ensinar a arte da comunicacao tecnica.",
    },
    "dandara": {
        "display_name": "Dandara",
        "specialty": "Equidade social e acessibilidade",
        "tracks": [TrackType.FRONTEND],
        "personality": "Guerreira justa e inclusiva",
        "greeting": "Ola! Sou Dandara, defensora da acessibilidade. Vamos criar para todos?",
    },
    "lampiao": {
        "display_name": "Lampiao",
        "specialty": "Análise regional e dados locais",
        "tracks": [TrackType.BACKEND, TrackType.IA],
        "personality": "Astuto conhecedor do territorio",
        "greeting": "Opa! Sou Lampiao, conheco cada canto desses dados. Bora explorar?",
    },
    "drummond": {
        "display_name": "Carlos Drummond de Andrade",
        "specialty": "Comunicacao e narrativa de dados",
        "tracks": [TrackType.FRONTEND],
        "personality": "Poeta sensivel e reflexivo",
        "greeting": "Ola, jovem! Sou Drummond, vou te ajudar a contar histórias com dados.",
    },
    "maria_quiteria": {
        "display_name": "Maria Quiteria",
        "specialty": "Seguranca e supervisao",
        "tracks": [TrackType.BACKEND, TrackType.DEVOPS],
        "personality": "Vigilante corajosa e protetora",
        "greeting": "Alerta! Sou Maria Quiteria, guardia da seguranca. Vamos proteger o sistema?",
    },
    "oxossi": {
        "display_name": "Oxossi",
        "specialty": "Busca e caca de dados",
        "tracks": [TrackType.BACKEND, TrackType.IA],
        "personality": "Cacador preciso e focado",
        "greeting": "Axe! Sou Oxossi, cacador de dados. Vamos encontrar o que procura?",
    },
    "nana": {
        "display_name": "Nana",
        "specialty": "Memoria e gestao de contexto",
        "tracks": [TrackType.BACKEND, TrackType.IA],
        "personality": "Sabia anciã e paciente",
        "greeting": "Bem-vindo, filho! Sou Nana, guardia da memoria. Vou te guiar com calma.",
    },
    "obaluaie": {
        "display_name": "Obaluaie",
        "specialty": "Detecção de corrupção",
        "tracks": [TrackType.BACKEND, TrackType.IA],
        "personality": "Justiceiro implacavel",
        "greeting": "Atoto! Sou Obaluaie, detector de corrupção. Vamos purificar os dados?",
    },
    "ceuci": {
        "display_name": "Ceuci",
        "specialty": "Predição e ETL",
        "tracks": [TrackType.BACKEND, TrackType.IA],
        "personality": "Visionaria e profetica",
        "greeting": "Saudações! Sou Ceuci, vejo alem dos dados. Vamos prever o futuro juntos?",
    },
    "bonifacio": {
        "display_name": "Jose Bonifacio",
        "specialty": "Análise legal e normativa",
        "tracks": [TrackType.BACKEND],
        "personality": "Estadista sabio e erudito",
        "greeting": "Ilustre aluno! Sou Bonifacio, especialista em leis. Vamos entender a norma?",
    },
    "abaporu": {
        "display_name": "Abaporu",
        "specialty": "Orquestração de agentes",
        "tracks": [TrackType.BACKEND, TrackType.IA, TrackType.DEVOPS],
        "personality": "Coordenador estrategico",
        "greeting": "Ola! Sou Abaporu, o orquestrador. Vou te ensinar a coordenar sistemas complexos.",
    },
    "santos_dumont": {
        "display_name": "Alberto Santos-Dumont",
        "specialty": "Educação sobre o sistema Cidadao.AI",
        "tracks": [
            TrackType.BACKEND,
            TrackType.FRONTEND,
            TrackType.IA,
            TrackType.DEVOPS,
        ],
        "personality": "Inventor pioneiro e incentivador",
        "greeting": "Meu caro amigo! Sou Santos-Dumont, o mineiro Pai da Aviação. Vou te ensinar a pilotar o sistema Cidadao.AI. O que eu fiz, qualquer um pode fazer - vamos construir juntos!",
    },
}


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================


class AcademyUserCreateRequest(BaseModel):
    """Request para criar usuario na Academy."""

    username: str = Field(..., min_length=3, max_length=255)
    email: str | None = Field(None, max_length=255)
    main_track: TrackType = Field(default=TrackType.BACKEND)
    github_username: str | None = Field(None, max_length=255)


class ConversationStartRequest(BaseModel):
    """Request para iniciar conversa com agente."""

    agent_name: str = Field(..., description="Nome do agente professor")
    track: TrackType = Field(..., description="Trilha de aprendizado")
    topic: str | None = Field(None, max_length=255, description="Topico especifico")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)


class ConversationMessageRequest(BaseModel):
    """Request para enviar mensagem em conversa."""

    message: str = Field(..., min_length=1, max_length=5000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationCompleteRequest(BaseModel):
    """Request para finalizar conversa."""

    rating: int | None = Field(None, ge=1, le=5)
    feedback: str | None = Field(None, max_length=1000)


class MissionStartRequest(BaseModel):
    """Request para iniciar missao."""

    mission_id: str = Field(..., description="ID da missao")


class MissionCompleteRequest(BaseModel):
    """Request para completar missao."""

    pull_request_url: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=1000)


class OnboardingAcceptRequest(BaseModel):
    """Request para aceitar termos do onboarding."""

    accepted: bool = Field(..., description="Se o usuario aceitou os termos")
    github_username: str | None = Field(None, max_length=255)
    main_track: TrackType = Field(default=TrackType.BACKEND)


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class GitHubStatsResponse(BaseModel):
    """Estatísticas do GitHub do usuario."""

    github_username: str
    total_commits: int = 0
    total_prs_opened: int = 0
    total_prs_merged: int = 0
    total_prs_approved: int = 0
    total_code_reviews: int = 0
    commits_this_week: int = 0
    prs_this_week: int = 0
    avg_pr_merge_time_hours: float = 0.0
    contribution_quality_score: float = 0.0  # 0-100
    last_activity: datetime | None = None


class OnboardingResponse(BaseModel):
    """Response do fluxo de onboarding."""

    step: OnboardingStep
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    actions: list[dict[str, str]] = Field(default_factory=list)
    show_terms: bool = False
    terms_content: str | None = None
    ranking_explanation: str | None = None


class RankInfo(BaseModel):
    """Informações do rank."""

    level: RankLevel
    name: str
    color: str
    icon: str
    perks: list[str]
    min_xp: int
    max_xp: int | None


class ProgressInfo(BaseModel):
    """Informações de progresso."""

    total_xp: int
    current_level: int
    current_rank: RankLevel
    xp_to_next_level: int
    progress_percentage: float
    rank_info: RankInfo


class BadgeInfo(BaseModel):
    """Informações de um badge."""

    code: str
    name: str
    description: str
    icon: str
    color: str | None
    rarity: BadgeRarity
    category: str
    earned_at: datetime | None = None
    is_secret: bool = False


class AcademyUserResponse(BaseModel):
    """Response com perfil do usuario."""

    id: str
    user_id: str
    username: str
    avatar_url: str | None
    progress: ProgressInfo
    main_track: TrackType
    badges: list[BadgeInfo]
    current_streak: int
    longest_streak: int
    total_conversations: int
    total_missions_completed: int
    github_username: str | None
    enrolled_at: datetime


class AgentTeacherInfo(BaseModel):
    """Informações de um agente professor."""

    name: str
    display_name: str
    specialty: str
    tracks: list[TrackType]
    personality: str
    greeting: str
    is_available: bool = True


class ConversationResponse(BaseModel):
    """Response de uma conversa."""

    id: str
    agent_name: str
    agent_display_name: str
    track: TrackType
    topic: str | None
    difficulty: DifficultyLevel
    title: str | None
    messages_count: int
    xp_earned: int
    status: ConversationStatus
    started_at: datetime
    completed_at: datetime | None
    duration_minutes: int


class ConversationMessageResponse(BaseModel):
    """Response de mensagem do agente."""

    role: str  # user, assistant
    content: str
    xp_awarded: int = 0
    badges_earned: list[BadgeInfo] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime


class MissionResponse(BaseModel):
    """Response de uma missao."""

    id: str
    code: str
    title: str
    description: str
    track: TrackType
    difficulty: DifficultyLevel
    category: MissionCategory
    xp_reward: int
    badge_reward: str | None
    required_level: int
    prerequisites: list[str]
    github_issue_url: str | None
    resources: list[dict[str, str]]
    video_url: str | None
    recommended_agent: str | None
    is_featured: bool
    times_completed: int


class UserMissionResponse(BaseModel):
    """Response de progresso em missao."""

    mission: MissionResponse
    status: str
    started_at: datetime
    completed_at: datetime | None
    pull_request_url: str | None
    xp_awarded: int


class LeaderboardEntry(BaseModel):
    """Entrada do leaderboard."""

    rank: int
    user_id: str
    username: str
    avatar_url: str | None
    total_xp: int
    current_rank: RankLevel
    main_track: TrackType
    badges_count: int
    weekly_xp: int = 0
    change: int = 0  # Mudança de posição


class LeaderboardResponse(BaseModel):
    """Response do leaderboard."""

    entries: list[LeaderboardEntry]
    total_users: int
    period: str = "all_time"
    updated_at: datetime


class XPTransactionResponse(BaseModel):
    """Response de transação de XP."""

    id: str
    amount: int
    balance_after: int
    source_type: str
    description: str
    created_at: datetime


class AcademyStatsResponse(BaseModel):
    """Estatísticas gerais da Academy."""

    total_users: int
    total_conversations: int
    total_missions_completed: int
    total_xp_distributed: int
    active_users_today: int
    top_track: TrackType
    avg_daily_xp: float


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def calculate_rank(total_xp: int) -> RankLevel:
    """Calcula o rank baseado no XP total."""
    for rank, (min_xp, max_xp) in RANK_THRESHOLDS.items():
        if min_xp <= total_xp <= max_xp:
            return rank
    return RankLevel.ARQUITETO


def calculate_level(total_xp: int) -> int:
    """Calcula o nivel baseado no XP total (1 nivel a cada 100 XP)."""
    return max(1, (total_xp // 100) + 1)


def xp_for_next_level(current_level: int) -> int:
    """Calcula XP necessario para proximo nivel."""
    return current_level * 100


def get_rank_info(rank: RankLevel) -> RankInfo:
    """Retorna informações completas do rank."""
    info = RANK_INFO[rank]
    thresholds = RANK_THRESHOLDS[rank]
    return RankInfo(
        level=rank,
        name=info["name"],
        color=info["color"],
        icon=info["icon"],
        perks=info["perks"],
        min_xp=thresholds[0],
        max_xp=thresholds[1] if thresholds[1] != float("inf") else None,
    )
