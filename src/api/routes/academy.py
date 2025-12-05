"""
Academy API Routes.

Endpoints para o sistema gamificado de estagio Cidadao.AI Academy.
Parceria: Neural Thinker AI Engineering + IFSULDEMINAS/LabSoft
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from src.api.middleware.authentication import get_current_user
from src.schemas.academy import (
    AGENT_TEACHERS,
    AcademyStatsResponse,
    AcademyUserCreateRequest,
    AcademyUserResponse,
    AgentTeacherInfo,
    BadgeInfo,
    ConversationCompleteRequest,
    ConversationMessageRequest,
    ConversationMessageResponse,
    ConversationResponse,
    ConversationStartRequest,
    DifficultyLevel,
    LeaderboardEntry,
    LeaderboardResponse,
    MissionCompleteRequest,
    MissionResponse,
    MissionStartRequest,
    ProgressInfo,
    RankLevel,
    TrackType,
    UserMissionResponse,
    XPTransactionResponse,
    calculate_level,
    calculate_rank,
    get_rank_info,
    xp_for_next_level,
)
from src.services.academy_service import academy_service

router = APIRouter()


# =============================================================================
# USER ENDPOINTS
# =============================================================================


@router.post("/users", response_model=AcademyUserResponse)
async def create_academy_user(
    request: AcademyUserCreateRequest,
    current_user: dict = Depends(get_current_user),
) -> AcademyUserResponse:
    """
    Criar perfil de usuario na Academy.

    Registra o usuario no programa de estagio gamificado.
    """
    user = await academy_service.create_user(
        user_id=current_user.get("user_id", current_user.get("sub")),
        username=request.username,
        email=request.email,
        main_track=request.main_track,
        github_username=request.github_username,
    )
    return user


@router.get("/users/me", response_model=AcademyUserResponse)
async def get_my_profile(
    current_user: dict = Depends(get_current_user),
) -> AcademyUserResponse:
    """
    Obter meu perfil na Academy.

    Retorna informacoes completas de progresso, badges e estatisticas.
    """
    user = await academy_service.get_user_profile(
        user_id=current_user.get("user_id", current_user.get("sub")),
    )
    if not user:
        raise HTTPException(
            status_code=404, detail="Perfil nao encontrado. Cadastre-se primeiro."
        )
    return user


@router.get("/users/{user_id}", response_model=AcademyUserResponse)
async def get_user_profile(
    user_id: str,
) -> AcademyUserResponse:
    """
    Obter perfil de um usuario.

    Retorna informacoes publicas do perfil.
    """
    user = await academy_service.get_user_profile(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return user


@router.get("/users/me/xp-history", response_model=list[XPTransactionResponse])
async def get_my_xp_history(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[XPTransactionResponse]:
    """
    Obter historico de XP.

    Lista todas as transacoes de XP do usuario.
    """
    transactions = await academy_service.get_xp_history(
        user_id=current_user.get("user_id", current_user.get("sub")),
        limit=limit,
        offset=offset,
    )
    return transactions


# =============================================================================
# AGENT ENDPOINTS
# =============================================================================


@router.get("/agents", response_model=list[AgentTeacherInfo])
async def list_agents(
    track: TrackType | None = None,
) -> list[AgentTeacherInfo]:
    """
    Listar agentes professores disponiveis.

    Retorna todos os agentes que podem ensinar na Academy.
    """
    agents = []
    for name, info in AGENT_TEACHERS.items():
        if track is None or track in info["tracks"]:
            agents.append(
                AgentTeacherInfo(
                    name=name,
                    display_name=info["display_name"],
                    specialty=info["specialty"],
                    tracks=info["tracks"],
                    personality=info["personality"],
                    greeting=info["greeting"],
                    is_available=True,
                )
            )
    return agents


@router.get("/agents/{agent_name}", response_model=AgentTeacherInfo)
async def get_agent(
    agent_name: str,
) -> AgentTeacherInfo:
    """
    Obter informacoes de um agente.
    """
    if agent_name not in AGENT_TEACHERS:
        raise HTTPException(status_code=404, detail="Agente nao encontrado")

    info = AGENT_TEACHERS[agent_name]
    return AgentTeacherInfo(
        name=agent_name,
        display_name=info["display_name"],
        specialty=info["specialty"],
        tracks=info["tracks"],
        personality=info["personality"],
        greeting=info["greeting"],
        is_available=True,
    )


# =============================================================================
# CONVERSATION ENDPOINTS
# =============================================================================


@router.post("/conversations", response_model=ConversationResponse)
async def start_conversation(
    request: ConversationStartRequest,
    current_user: dict = Depends(get_current_user),
) -> ConversationResponse:
    """
    Iniciar conversa/aula com um agente.

    Cria uma nova sessao de aprendizado com o agente escolhido.
    """
    if request.agent_name not in AGENT_TEACHERS:
        raise HTTPException(status_code=400, detail="Agente invalido")

    conversation = await academy_service.start_conversation(
        user_id=current_user.get("user_id", current_user.get("sub")),
        agent_name=request.agent_name,
        track=request.track,
        topic=request.topic,
        difficulty=request.difficulty,
    )
    return conversation


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_my_conversations(
    current_user: dict = Depends(get_current_user),
    status: str | None = None,
    agent_name: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ConversationResponse]:
    """
    Listar minhas conversas/aulas.

    Historico de todas as sessoes de aprendizado.
    """
    conversations = await academy_service.list_conversations(
        user_id=current_user.get("user_id", current_user.get("sub")),
        status=status,
        agent_name=agent_name,
        limit=limit,
        offset=offset,
    )
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
) -> ConversationResponse:
    """
    Obter detalhes de uma conversa.
    """
    conversation = await academy_service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.get("user_id", current_user.get("sub")),
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa nao encontrada")
    return conversation


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
) -> list[ConversationMessageResponse]:
    """
    Obter mensagens de uma conversa.
    """
    messages = await academy_service.get_conversation_messages(
        conversation_id=conversation_id,
        user_id=current_user.get("user_id", current_user.get("sub")),
    )
    return messages


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    request: ConversationMessageRequest,
    current_user: dict = Depends(get_current_user),
) -> ConversationMessageResponse:
    """
    Enviar mensagem em uma conversa.

    O agente responde de forma educacional e gamificada.
    """
    response = await academy_service.send_message(
        conversation_id=conversation_id,
        user_id=current_user.get("user_id", current_user.get("sub")),
        message=request.message,
        metadata=request.metadata,
    )
    return response


@router.post("/conversations/{conversation_id}/messages/stream")
async def send_message_stream(
    conversation_id: str,
    request: ConversationMessageRequest,
    current_user: dict = Depends(get_current_user),
) -> StreamingResponse:
    """
    Enviar mensagem com resposta em streaming.

    Retorna a resposta do agente em tempo real via SSE.
    """

    async def generate():
        async for chunk in academy_service.send_message_stream(
            conversation_id=conversation_id,
            user_id=current_user.get("user_id", current_user.get("sub")),
            message=request.message,
            metadata=request.metadata,
        ):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


@router.post(
    "/conversations/{conversation_id}/complete", response_model=ConversationResponse
)
async def complete_conversation(
    conversation_id: str,
    request: ConversationCompleteRequest,
    current_user: dict = Depends(get_current_user),
) -> ConversationResponse:
    """
    Finalizar uma conversa/aula.

    Marca a conversa como completa e calcula XP final.
    """
    conversation = await academy_service.complete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.get("user_id", current_user.get("sub")),
        rating=request.rating,
        feedback=request.feedback,
    )
    return conversation


# =============================================================================
# MISSION ENDPOINTS
# =============================================================================


@router.get("/missions", response_model=list[MissionResponse])
async def list_missions(
    track: TrackType | None = None,
    difficulty: DifficultyLevel | None = None,
    category: str | None = None,
    featured_only: bool = False,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[MissionResponse]:
    """
    Listar missoes disponiveis.

    Filtra por trilha, dificuldade ou categoria.
    """
    missions = await academy_service.list_missions(
        track=track,
        difficulty=difficulty,
        category=category,
        featured_only=featured_only,
        limit=limit,
        offset=offset,
    )
    return missions


@router.get("/missions/{mission_id}", response_model=MissionResponse)
async def get_mission(
    mission_id: str,
) -> MissionResponse:
    """
    Obter detalhes de uma missao.
    """
    mission = await academy_service.get_mission(mission_id=mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Missao nao encontrada")
    return mission


@router.get("/missions/me", response_model=list[UserMissionResponse])
async def list_my_missions(
    current_user: dict = Depends(get_current_user),
    status: str | None = None,
) -> list[UserMissionResponse]:
    """
    Listar minhas missoes.

    Retorna missoes em progresso e completadas.
    """
    missions = await academy_service.list_user_missions(
        user_id=current_user.get("user_id", current_user.get("sub")),
        status=status,
    )
    return missions


@router.post("/missions/{mission_id}/start", response_model=UserMissionResponse)
async def start_mission(
    mission_id: str,
    current_user: dict = Depends(get_current_user),
) -> UserMissionResponse:
    """
    Iniciar uma missao.

    Registra o inicio da missao para o usuario.
    """
    user_mission = await academy_service.start_mission(
        user_id=current_user.get("user_id", current_user.get("sub")),
        mission_id=mission_id,
    )
    return user_mission


@router.post("/missions/{mission_id}/complete", response_model=UserMissionResponse)
async def complete_mission(
    mission_id: str,
    request: MissionCompleteRequest,
    current_user: dict = Depends(get_current_user),
) -> UserMissionResponse:
    """
    Completar uma missao.

    Marca a missao como concluida e atribui XP.
    """
    user_mission = await academy_service.complete_mission(
        user_id=current_user.get("user_id", current_user.get("sub")),
        mission_id=mission_id,
        pull_request_url=request.pull_request_url,
        notes=request.notes,
    )
    return user_mission


# =============================================================================
# BADGE ENDPOINTS
# =============================================================================


@router.get("/badges", response_model=list[BadgeInfo])
async def list_badges(
    category: str | None = None,
    include_secret: bool = False,
) -> list[BadgeInfo]:
    """
    Listar badges disponiveis.
    """
    badges = await academy_service.list_badges(
        category=category,
        include_secret=include_secret,
    )
    return badges


@router.get("/badges/me", response_model=list[BadgeInfo])
async def list_my_badges(
    current_user: dict = Depends(get_current_user),
) -> list[BadgeInfo]:
    """
    Listar meus badges conquistados.
    """
    badges = await academy_service.get_user_badges(
        user_id=current_user.get("user_id", current_user.get("sub")),
    )
    return badges


# =============================================================================
# LEADERBOARD ENDPOINTS
# =============================================================================


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    track: TrackType | None = None,
    period: str = Query(default="all_time", regex="^(daily|weekly|monthly|all_time)$"),
    limit: int = Query(default=10, ge=1, le=100),
) -> LeaderboardResponse:
    """
    Obter leaderboard.

    Ranking dos melhores alunos por XP.
    """
    leaderboard = await academy_service.get_leaderboard(
        track=track,
        period=period,
        limit=limit,
    )
    return leaderboard


@router.get("/leaderboard/me")
async def get_my_ranking(
    current_user: dict = Depends(get_current_user),
    period: str = Query(default="all_time", regex="^(daily|weekly|monthly|all_time)$"),
) -> dict[str, Any]:
    """
    Obter minha posicao no ranking.
    """
    ranking = await academy_service.get_user_ranking(
        user_id=current_user.get("user_id", current_user.get("sub")),
        period=period,
    )
    return ranking


# =============================================================================
# STATS ENDPOINTS
# =============================================================================


@router.get("/stats", response_model=AcademyStatsResponse)
async def get_academy_stats() -> AcademyStatsResponse:
    """
    Obter estatisticas gerais da Academy.
    """
    stats = await academy_service.get_stats()
    return stats


@router.get("/stats/me")
async def get_my_stats(
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Obter minhas estatisticas detalhadas.
    """
    stats = await academy_service.get_user_stats(
        user_id=current_user.get("user_id", current_user.get("sub")),
    )
    return stats


# =============================================================================
# TRACKS ENDPOINTS
# =============================================================================


@router.get("/tracks")
async def list_tracks() -> list[dict[str, Any]]:
    """
    Listar trilhas disponiveis.
    """
    return [
        {
            "id": TrackType.BACKEND.value,
            "name": "Backend",
            "description": "Python, FastAPI, PostgreSQL, Redis, Celery",
            "icon": "server",
            "color": "#3B82F6",
            "recommended_agents": ["zumbi", "anita", "tiradentes", "bonifacio"],
        },
        {
            "id": TrackType.FRONTEND.value,
            "name": "Frontend",
            "description": "Next.js 15, React 18, TypeScript, Tailwind CSS",
            "icon": "layout",
            "color": "#10B981",
            "recommended_agents": ["oscar_niemeyer", "dandara", "drummond", "machado"],
        },
        {
            "id": TrackType.IA.value,
            "name": "IA/ML",
            "description": "DSPy, LangChain, Transformers, Agentes",
            "icon": "brain",
            "color": "#8B5CF6",
            "recommended_agents": ["zumbi", "oxossi", "ceuci", "nana", "obaluaie"],
        },
        {
            "id": TrackType.DEVOPS.value,
            "name": "DevOps",
            "description": "Docker, GitHub Actions, Prometheus, Grafana",
            "icon": "settings",
            "color": "#F59E0B",
            "recommended_agents": [
                "ayrton_senna",
                "maria_quiteria",
                "tiradentes",
                "abaporu",
            ],
        },
    ]
