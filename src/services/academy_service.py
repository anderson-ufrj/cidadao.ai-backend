"""
Academy Service.

Servico de logica de negocios para o sistema gamificado.
Parceria: Neural Thinker AI Engineering + IFSULDEMINAS/LabSoft
"""

import json
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

from src.agents import get_agent
from src.agents.deodoro import AgentContext, AgentMessage
from src.schemas.academy import (
    AGENT_TEACHERS,
    AcademyStatsResponse,
    AcademyUserResponse,
    BadgeInfo,
    ConversationMessageResponse,
    ConversationResponse,
    ConversationStatus,
    DifficultyLevel,
    LeaderboardEntry,
    LeaderboardResponse,
    MissionResponse,
    ProgressInfo,
    RankLevel,
    TrackType,
    UserMissionResponse,
    XPTransactionResponse,
    XPValues,
    calculate_level,
    calculate_rank,
    get_rank_info,
    xp_for_next_level,
)


class AcademyService:
    """
    Servico principal da Academy.

    Gerencia usuarios, conversas, missoes e gamificacao.
    """

    def __init__(self):
        # Em producao, isso seria injetado via dependency injection
        # Por enquanto, usamos armazenamento em memoria para MVP
        self._users: dict[str, dict] = {}
        self._conversations: dict[str, dict] = {}
        self._missions: dict[str, dict] = {}
        self._badges: dict[str, dict] = {}
        self._user_missions: dict[str, list[dict]] = {}
        self._xp_transactions: dict[str, list[dict]] = {}

        # Inicializar badges padrao
        self._init_default_badges()
        # Inicializar missoes de exemplo
        self._init_default_missions()

    def _init_default_badges(self):
        """Inicializa badges padrao do sistema."""
        default_badges = [
            {
                "code": "first_conversation",
                "name": "Primeira Conversa",
                "description": "Iniciou sua primeira conversa com um agente",
                "icon": "message-circle",
                "color": "#10B981",
                "rarity": "common",
                "category": "learning",
                "xp_bonus": 25,
            },
            {
                "code": "streak_7",
                "name": "Semana de Fogo",
                "description": "Manteve streak de 7 dias consecutivos",
                "icon": "flame",
                "color": "#F59E0B",
                "rarity": "uncommon",
                "category": "streak",
                "xp_bonus": 50,
            },
            {
                "code": "streak_30",
                "name": "Mes Dedicado",
                "description": "Manteve streak de 30 dias consecutivos",
                "icon": "calendar",
                "color": "#8B5CF6",
                "rarity": "rare",
                "category": "streak",
                "xp_bonus": 200,
            },
            {
                "code": "first_mission",
                "name": "Primeira Missao",
                "description": "Completou sua primeira missao",
                "icon": "target",
                "color": "#3B82F6",
                "rarity": "common",
                "category": "contribution",
                "xp_bonus": 50,
            },
            {
                "code": "first_pr",
                "name": "Primeiro PR",
                "description": "Teve seu primeiro Pull Request aprovado",
                "icon": "git-pull-request",
                "color": "#10B981",
                "rarity": "uncommon",
                "category": "contribution",
                "xp_bonus": 100,
            },
            {
                "code": "all_agents",
                "name": "Conhecedor",
                "description": "Conversou com todos os agentes",
                "icon": "users",
                "color": "#8B5CF6",
                "rarity": "rare",
                "category": "learning",
                "xp_bonus": 150,
            },
            {
                "code": "mentor_badge",
                "name": "Mentor",
                "description": "Alcancou o rank de Mentor",
                "icon": "crown",
                "color": "#F59E0B",
                "rarity": "epic",
                "category": "special",
                "xp_bonus": 300,
            },
            {
                "code": "architect_badge",
                "name": "Arquiteto",
                "description": "Alcancou o rank maximo de Arquiteto",
                "icon": "trophy",
                "color": "#EF4444",
                "rarity": "legendary",
                "category": "special",
                "xp_bonus": 500,
            },
        ]
        for badge in default_badges:
            self._badges[badge["code"]] = badge

    def _init_default_missions(self):
        """Inicializa missoes de exemplo."""
        default_missions = [
            {
                "id": "mission_001",
                "code": "fix_typo_docs",
                "title": "Corrigir Typo na Documentacao",
                "description": "Encontre e corrija um erro de digitacao na documentacao do projeto.",
                "track": TrackType.BACKEND,
                "difficulty": DifficultyLevel.EASY,
                "category": "docs",
                "xp_reward": 10,
                "required_level": 1,
                "prerequisites": [],
                "recommended_agent": "machado",
                "is_active": True,
                "is_featured": True,
                "times_completed": 0,
            },
            {
                "id": "mission_002",
                "code": "write_unit_test",
                "title": "Escrever Teste Unitario",
                "description": "Adicione um teste unitario para uma funcao existente.",
                "track": TrackType.BACKEND,
                "difficulty": DifficultyLevel.EASY,
                "category": "test",
                "xp_reward": 15,
                "required_level": 1,
                "prerequisites": [],
                "recommended_agent": "zumbi",
                "is_active": True,
                "is_featured": True,
                "times_completed": 0,
            },
            {
                "id": "mission_003",
                "code": "fix_simple_bug",
                "title": "Corrigir Bug Simples",
                "description": "Resolva um bug marcado como 'good first issue' no GitHub.",
                "track": TrackType.BACKEND,
                "difficulty": DifficultyLevel.MEDIUM,
                "category": "bug-fix",
                "xp_reward": 25,
                "required_level": 2,
                "prerequisites": ["fix_typo_docs"],
                "recommended_agent": "anita",
                "github_issue_url": "https://github.com/anderson-ufrj/cidadao.ai-backend/issues",
                "is_active": True,
                "is_featured": True,
                "times_completed": 0,
            },
            {
                "id": "mission_004",
                "code": "implement_component",
                "title": "Implementar Componente React",
                "description": "Crie um novo componente reutilizavel para o frontend.",
                "track": TrackType.FRONTEND,
                "difficulty": DifficultyLevel.MEDIUM,
                "category": "feature",
                "xp_reward": 30,
                "required_level": 2,
                "prerequisites": [],
                "recommended_agent": "oscar_niemeyer",
                "is_active": True,
                "is_featured": False,
                "times_completed": 0,
            },
            {
                "id": "mission_005",
                "code": "optimize_query",
                "title": "Otimizar Query SQL",
                "description": "Identifique e otimize uma query lenta no sistema.",
                "track": TrackType.BACKEND,
                "difficulty": DifficultyLevel.HARD,
                "category": "refactor",
                "xp_reward": 50,
                "required_level": 5,
                "prerequisites": ["fix_simple_bug"],
                "recommended_agent": "ayrton_senna",
                "is_active": True,
                "is_featured": False,
                "times_completed": 0,
            },
        ]
        for mission in default_missions:
            self._missions[mission["id"]] = mission

    # =========================================================================
    # USER METHODS
    # =========================================================================

    async def create_user(
        self,
        user_id: str,
        username: str,
        email: str | None = None,
        main_track: TrackType = TrackType.BACKEND,
        github_username: str | None = None,
    ) -> AcademyUserResponse:
        """Criar novo usuario na Academy."""
        if user_id in self._users:
            raise ValueError("Usuario ja cadastrado")

        user = {
            "id": user_id,
            "user_id": user_id,
            "username": username,
            "email": email,
            "avatar_url": None,
            "total_xp": 0,
            "current_level": 1,
            "current_rank": RankLevel.NOVATO,
            "main_track": main_track,
            "badges": [],
            "current_streak": 0,
            "longest_streak": 0,
            "last_activity_date": None,
            "total_conversations": 0,
            "total_missions_completed": 0,
            "github_username": github_username,
            "enrolled_at": datetime.now(UTC),
        }

        self._users[user_id] = user
        self._xp_transactions[user_id] = []

        return self._build_user_response(user)

    async def get_user_profile(self, user_id: str) -> AcademyUserResponse | None:
        """Obter perfil do usuario."""
        user = self._users.get(user_id)
        if not user:
            return None
        return self._build_user_response(user)

    async def get_xp_history(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> list[XPTransactionResponse]:
        """Obter historico de XP do usuario."""
        transactions = self._xp_transactions.get(user_id, [])
        paginated = transactions[offset : offset + limit]
        return [
            XPTransactionResponse(
                id=t["id"],
                amount=t["amount"],
                balance_after=t["balance_after"],
                source_type=t["source_type"],
                description=t["description"],
                created_at=t["created_at"],
            )
            for t in paginated
        ]

    def _build_user_response(self, user: dict) -> AcademyUserResponse:
        """Construir response de usuario."""
        rank = user["current_rank"]
        if isinstance(rank, str):
            rank = RankLevel(rank)

        total_xp = user["total_xp"]
        current_level = calculate_level(total_xp)
        next_level_xp = xp_for_next_level(current_level)
        current_level_xp = (current_level - 1) * 100
        xp_in_level = total_xp - current_level_xp
        progress_pct = (xp_in_level / 100) * 100 if next_level_xp > 0 else 100

        progress = ProgressInfo(
            total_xp=total_xp,
            current_level=current_level,
            current_rank=rank,
            xp_to_next_level=next_level_xp - xp_in_level,
            progress_percentage=min(progress_pct, 100),
            rank_info=get_rank_info(rank),
        )

        badges = [
            BadgeInfo(
                code=b["code"],
                name=b["name"],
                description=b["description"],
                icon=b["icon"],
                color=b.get("color"),
                rarity=b["rarity"],
                category=b["category"],
                earned_at=b.get("earned_at"),
            )
            for b in user.get("badges", [])
        ]

        main_track = user["main_track"]
        if isinstance(main_track, str):
            main_track = TrackType(main_track)

        return AcademyUserResponse(
            id=user["id"],
            user_id=user["user_id"],
            username=user["username"],
            avatar_url=user.get("avatar_url"),
            progress=progress,
            main_track=main_track,
            badges=badges,
            current_streak=user["current_streak"],
            longest_streak=user["longest_streak"],
            total_conversations=user["total_conversations"],
            total_missions_completed=user["total_missions_completed"],
            github_username=user.get("github_username"),
            enrolled_at=user["enrolled_at"],
        )

    async def _add_xp(
        self,
        user_id: str,
        amount: int,
        source_type: str,
        source_id: str | None,
        description: str,
    ) -> int:
        """Adicionar XP ao usuario."""
        user = self._users.get(user_id)
        if not user:
            return 0

        user["total_xp"] += amount
        new_balance = user["total_xp"]

        # Atualizar nivel e rank
        user["current_level"] = calculate_level(new_balance)
        user["current_rank"] = calculate_rank(new_balance)

        # Registrar transacao
        transaction = {
            "id": f"xp_{datetime.now(UTC).timestamp()}",
            "amount": amount,
            "balance_after": new_balance,
            "source_type": source_type,
            "source_id": source_id,
            "description": description,
            "created_at": datetime.now(UTC),
        }
        self._xp_transactions.setdefault(user_id, []).insert(0, transaction)

        # Verificar badges de rank
        await self._check_rank_badges(user_id)

        return new_balance

    async def _check_rank_badges(self, user_id: str):
        """Verificar e conceder badges de rank."""
        user = self._users.get(user_id)
        if not user:
            return

        rank = user["current_rank"]
        if isinstance(rank, str):
            rank = RankLevel(rank)

        badge_code = None
        if rank == RankLevel.MENTOR:
            badge_code = "mentor_badge"
        elif rank == RankLevel.ARQUITETO:
            badge_code = "architect_badge"

        if badge_code and badge_code not in [b["code"] for b in user["badges"]]:
            await self._award_badge(user_id, badge_code)

    async def _award_badge(self, user_id: str, badge_code: str) -> BadgeInfo | None:
        """Conceder badge ao usuario."""
        user = self._users.get(user_id)
        badge_template = self._badges.get(badge_code)

        if not user or not badge_template:
            return None

        # Verificar se ja tem
        if badge_code in [b["code"] for b in user["badges"]]:
            return None

        badge = {
            **badge_template,
            "earned_at": datetime.now(UTC),
        }
        user["badges"].append(badge)

        # Dar XP bonus do badge
        if badge_template.get("xp_bonus", 0) > 0:
            await self._add_xp(
                user_id=user_id,
                amount=badge_template["xp_bonus"],
                source_type="badge",
                source_id=badge_code,
                description=f"Badge conquistado: {badge_template['name']}",
            )

        return BadgeInfo(
            code=badge["code"],
            name=badge["name"],
            description=badge["description"],
            icon=badge["icon"],
            color=badge.get("color"),
            rarity=badge["rarity"],
            category=badge["category"],
            earned_at=badge["earned_at"],
        )

    # =========================================================================
    # CONVERSATION METHODS
    # =========================================================================

    async def start_conversation(
        self,
        user_id: str,
        agent_name: str,
        track: TrackType,
        topic: str | None,
        difficulty: DifficultyLevel,
    ) -> ConversationResponse:
        """Iniciar nova conversa com agente."""
        user = self._users.get(user_id)
        if not user:
            raise ValueError("Usuario nao encontrado")

        agent_info = AGENT_TEACHERS.get(agent_name)
        if not agent_info:
            raise ValueError("Agente nao encontrado")

        conv_id = f"conv_{datetime.now(UTC).timestamp()}"
        conversation = {
            "id": conv_id,
            "user_id": user_id,
            "agent_name": agent_name,
            "agent_display_name": agent_info["display_name"],
            "track": track,
            "topic": topic,
            "difficulty": difficulty,
            "title": f"Conversa com {agent_info['display_name']}",
            "messages": [],
            "xp_earned": 0,
            "badges_earned": [],
            "status": ConversationStatus.ACTIVE,
            "started_at": datetime.now(UTC),
            "completed_at": None,
            "duration_minutes": 0,
        }

        self._conversations[conv_id] = conversation

        # XP por iniciar conversa
        await self._add_xp(
            user_id=user_id,
            amount=XPValues.CONVERSATION_STARTED,
            source_type="conversation",
            source_id=conv_id,
            description="Iniciou nova conversa",
        )
        conversation["xp_earned"] += XPValues.CONVERSATION_STARTED

        # Badge de primeira conversa
        if user["total_conversations"] == 0:
            badge = await self._award_badge(user_id, "first_conversation")
            if badge:
                conversation["badges_earned"].append(badge.model_dump())

        user["total_conversations"] += 1

        # Adicionar mensagem inicial do agente
        greeting_message = {
            "role": "assistant",
            "content": agent_info["greeting"],
            "xp_awarded": 0,
            "timestamp": datetime.now(UTC),
        }
        conversation["messages"].append(greeting_message)

        return self._build_conversation_response(conversation)

    async def list_conversations(
        self,
        user_id: str,
        status: str | None = None,
        agent_name: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ConversationResponse]:
        """Listar conversas do usuario."""
        conversations = [
            c for c in self._conversations.values() if c["user_id"] == user_id
        ]

        if status:
            conversations = [c for c in conversations if c["status"].value == status]
        if agent_name:
            conversations = [c for c in conversations if c["agent_name"] == agent_name]

        # Ordenar por data (mais recente primeiro)
        conversations.sort(key=lambda x: x["started_at"], reverse=True)

        paginated = conversations[offset : offset + limit]
        return [self._build_conversation_response(c) for c in paginated]

    async def get_conversation(
        self, conversation_id: str, user_id: str
    ) -> ConversationResponse | None:
        """Obter conversa por ID."""
        conversation = self._conversations.get(conversation_id)
        if not conversation or conversation["user_id"] != user_id:
            return None
        return self._build_conversation_response(conversation)

    async def get_conversation_messages(
        self, conversation_id: str, user_id: str
    ) -> list[ConversationMessageResponse]:
        """Obter mensagens de uma conversa."""
        conversation = self._conversations.get(conversation_id)
        if not conversation or conversation["user_id"] != user_id:
            return []

        return [
            ConversationMessageResponse(
                role=m["role"],
                content=m["content"],
                xp_awarded=m.get("xp_awarded", 0),
                badges_earned=m.get("badges_earned", []),
                metadata=m.get("metadata", {}),
                timestamp=m["timestamp"],
            )
            for m in conversation["messages"]
        ]

    async def send_message(
        self,
        conversation_id: str,
        user_id: str,
        message: str,
        metadata: dict | None = None,
    ) -> ConversationMessageResponse:
        """Enviar mensagem e receber resposta do agente."""
        conversation = self._conversations.get(conversation_id)
        if not conversation or conversation["user_id"] != user_id:
            raise ValueError("Conversa nao encontrada")

        if conversation["status"] != ConversationStatus.ACTIVE:
            raise ValueError("Conversa nao esta ativa")

        # Salvar mensagem do usuario
        user_message = {
            "role": "user",
            "content": message,
            "xp_awarded": XPValues.CONVERSATION_MESSAGE,
            "timestamp": datetime.now(UTC),
            "metadata": metadata or {},
        }
        conversation["messages"].append(user_message)

        # Dar XP por mensagem
        await self._add_xp(
            user_id=user_id,
            amount=XPValues.CONVERSATION_MESSAGE,
            source_type="conversation",
            source_id=conversation_id,
            description="Enviou mensagem",
        )
        conversation["xp_earned"] += XPValues.CONVERSATION_MESSAGE

        # Gerar resposta do agente
        agent_response = await self._generate_agent_response(
            conversation=conversation,
            user_message=message,
        )

        # Salvar resposta do agente
        assistant_message = {
            "role": "assistant",
            "content": agent_response,
            "xp_awarded": 0,
            "timestamp": datetime.now(UTC),
        }
        conversation["messages"].append(assistant_message)

        return ConversationMessageResponse(
            role="assistant",
            content=agent_response,
            xp_awarded=XPValues.CONVERSATION_MESSAGE,
            badges_earned=[],
            metadata={},
            timestamp=assistant_message["timestamp"],
        )

    async def send_message_stream(
        self,
        conversation_id: str,
        user_id: str,
        message: str,
        metadata: dict | None = None,
    ) -> AsyncGenerator[str, None]:
        """Enviar mensagem com resposta em streaming."""
        # Por enquanto, simula streaming retornando resposta completa
        response = await self.send_message(
            conversation_id=conversation_id,
            user_id=user_id,
            message=message,
            metadata=metadata,
        )

        # Simular streaming palavra por palavra
        words = response.content.split()
        for i, word in enumerate(words):
            chunk = {"content": word + " ", "done": i == len(words) - 1}
            yield json.dumps(chunk)

    async def _generate_agent_response(
        self, conversation: dict, user_message: str
    ) -> str:
        """Gerar resposta educacional do agente."""
        agent_name = conversation["agent_name"]
        agent_info = AGENT_TEACHERS.get(agent_name, {})
        track = conversation["track"]
        difficulty = conversation["difficulty"]

        # Construir prompt educacional
        system_prompt = f"""Voce e {agent_info.get('display_name', agent_name)}, um professor especialista em {agent_info.get('specialty', 'tecnologia')}.

Sua personalidade: {agent_info.get('personality', 'amigavel e didatico')}.

Voce esta ensinando na trilha de {track.value if isinstance(track, TrackType) else track}, nivel {difficulty.value if isinstance(difficulty, DifficultyLevel) else difficulty}.

Regras:
1. Responda de forma educacional e encorajadora
2. Use exemplos praticos do projeto Cidadao.AI quando possivel
3. Faca perguntas para verificar entendimento
4. Sugira proximos passos de aprendizado
5. Mantenha respostas concisas mas informativas
6. Use portugues brasileiro

Historico da conversa:
{self._format_conversation_history(conversation)}

Mensagem do aluno: {user_message}
"""

        # Tentar usar o agente real
        try:
            agent = get_agent(agent_name)
            if agent:
                context = AgentContext(
                    investigation_id=conversation["id"],
                    user_id=conversation["user_id"],
                    metadata={
                        "educational_mode": True,
                        "track": track.value if isinstance(track, TrackType) else track,
                        "difficulty": (
                            difficulty.value
                            if isinstance(difficulty, DifficultyLevel)
                            else difficulty
                        ),
                    },
                )

                message = AgentMessage(
                    sender="academy",
                    recipient=agent_name,
                    action="teach",
                    payload={
                        "query": user_message,
                        "system_prompt": system_prompt,
                        "educational_mode": True,
                    },
                    context={"conversation_id": conversation["id"]},
                )

                response = await agent.process(message, context)
                if response and response.result:
                    return str(response.result)
        except Exception:
            pass

        # Fallback: resposta simulada
        return self._generate_fallback_response(agent_info, user_message, difficulty)

    def _format_conversation_history(self, conversation: dict) -> str:
        """Formatar historico da conversa para o prompt."""
        history = []
        for msg in conversation["messages"][-10:]:  # Ultimas 10 mensagens
            role = "Aluno" if msg["role"] == "user" else "Professor"
            history.append(f"{role}: {msg['content']}")
        return "\n".join(history)

    def _generate_fallback_response(
        self, agent_info: dict, user_message: str, difficulty: DifficultyLevel
    ) -> str:
        """Gerar resposta fallback quando agente real nao disponivel."""
        display_name = agent_info.get("display_name", "Professor")
        specialty = agent_info.get("specialty", "tecnologia")

        responses = {
            DifficultyLevel.BEGINNER: f"Otima pergunta! Como {display_name}, vou te explicar de forma simples. "
            f"No contexto de {specialty}, isso significa que voce esta no caminho certo. "
            f"Quer que eu detalhe mais algum ponto especifico?",
            DifficultyLevel.EASY: "Interessante! Vejo que voce esta progredindo bem. "
            "Sobre sua pergunta, no projeto Cidadao.AI trabalhamos muito com isso. "
            "Vamos explorar mais a fundo?",
            DifficultyLevel.MEDIUM: "Excelente observacao! Isso demonstra que voce esta entendendo os conceitos. "
            "Na pratica, aplicamos isso de varias formas. "
            "Que tal tentarmos um exercicio pratico?",
            DifficultyLevel.HARD: f"Voce tocou em um ponto importante! Como especialista em {specialty}, "
            f"posso dizer que essa e uma area que requer pratica. "
            f"Vamos analisar um caso real do projeto?",
            DifficultyLevel.EXPERT: "Impressionante! Sua pergunta mostra maturidade tecnica. "
            "Vamos discutir as nuances arquiteturais disso. "
            "Ja considerou as implicacoes de performance?",
        }

        return responses.get(difficulty, responses[DifficultyLevel.BEGINNER])

    async def complete_conversation(
        self,
        conversation_id: str,
        user_id: str,
        rating: int | None = None,
        feedback: str | None = None,
    ) -> ConversationResponse:
        """Finalizar conversa."""
        conversation = self._conversations.get(conversation_id)
        if not conversation or conversation["user_id"] != user_id:
            raise ValueError("Conversa nao encontrada")

        conversation["status"] = ConversationStatus.COMPLETED
        conversation["completed_at"] = datetime.now(UTC)
        conversation["rating"] = rating
        conversation["feedback"] = feedback

        # Calcular duracao
        if conversation["started_at"]:
            duration = datetime.now(UTC) - conversation["started_at"]
            conversation["duration_minutes"] = int(duration.total_seconds() / 60)

        # XP por completar
        xp_amount = XPValues.CONVERSATION_COMPLETED
        if rating and rating == 5:
            xp_amount = XPValues.CONVERSATION_EXCELLENT

        await self._add_xp(
            user_id=user_id,
            amount=xp_amount,
            source_type="conversation",
            source_id=conversation_id,
            description="Completou conversa",
        )
        conversation["xp_earned"] += xp_amount

        return self._build_conversation_response(conversation)

    def _build_conversation_response(self, conversation: dict) -> ConversationResponse:
        """Construir response de conversa."""
        track = conversation["track"]
        if isinstance(track, str):
            track = TrackType(track)

        difficulty = conversation["difficulty"]
        if isinstance(difficulty, str):
            difficulty = DifficultyLevel(difficulty)

        status = conversation["status"]
        if isinstance(status, str):
            status = ConversationStatus(status)

        return ConversationResponse(
            id=conversation["id"],
            agent_name=conversation["agent_name"],
            agent_display_name=conversation["agent_display_name"],
            track=track,
            topic=conversation.get("topic"),
            difficulty=difficulty,
            title=conversation.get("title"),
            messages_count=len(conversation.get("messages", [])),
            xp_earned=conversation["xp_earned"],
            status=status,
            started_at=conversation["started_at"],
            completed_at=conversation.get("completed_at"),
            duration_minutes=conversation.get("duration_minutes", 0),
        )

    # =========================================================================
    # MISSION METHODS
    # =========================================================================

    async def list_missions(
        self,
        track: TrackType | None = None,
        difficulty: DifficultyLevel | None = None,
        category: str | None = None,
        featured_only: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MissionResponse]:
        """Listar missoes disponiveis."""
        missions = list(self._missions.values())

        if track:
            missions = [m for m in missions if m["track"] == track]
        if difficulty:
            missions = [m for m in missions if m["difficulty"] == difficulty]
        if category:
            missions = [m for m in missions if m["category"] == category]
        if featured_only:
            missions = [m for m in missions if m.get("is_featured", False)]

        missions = [m for m in missions if m.get("is_active", True)]

        paginated = missions[offset : offset + limit]
        return [self._build_mission_response(m) for m in paginated]

    async def get_mission(self, mission_id: str) -> MissionResponse | None:
        """Obter missao por ID."""
        mission = self._missions.get(mission_id)
        if not mission:
            return None
        return self._build_mission_response(mission)

    async def list_user_missions(
        self, user_id: str, status: str | None = None
    ) -> list[UserMissionResponse]:
        """Listar missoes do usuario."""
        user_missions = self._user_missions.get(user_id, [])
        if status:
            user_missions = [m for m in user_missions if m["status"] == status]
        return [self._build_user_mission_response(um) for um in user_missions]

    async def start_mission(self, user_id: str, mission_id: str) -> UserMissionResponse:
        """Iniciar missao."""
        mission = self._missions.get(mission_id)
        if not mission:
            raise ValueError("Missao nao encontrada")

        user = self._users.get(user_id)
        if not user:
            raise ValueError("Usuario nao encontrado")

        # Verificar nivel
        if user["current_level"] < mission.get("required_level", 1):
            raise ValueError(
                f"Nivel minimo: {mission['required_level']}. Seu nivel: {user['current_level']}"
            )

        user_mission = {
            "id": f"um_{datetime.now(UTC).timestamp()}",
            "user_id": user_id,
            "mission_id": mission_id,
            "mission": mission,
            "status": "in_progress",
            "started_at": datetime.now(UTC),
            "completed_at": None,
            "pull_request_url": None,
            "xp_awarded": 0,
        }

        self._user_missions.setdefault(user_id, []).append(user_mission)
        return self._build_user_mission_response(user_mission)

    async def complete_mission(
        self,
        user_id: str,
        mission_id: str,
        pull_request_url: str | None = None,
        notes: str | None = None,
    ) -> UserMissionResponse:
        """Completar missao."""
        user_missions = self._user_missions.get(user_id, [])
        user_mission = next(
            (
                m
                for m in user_missions
                if m["mission_id"] == mission_id and m["status"] == "in_progress"
            ),
            None,
        )

        if not user_mission:
            raise ValueError("Missao nao encontrada ou nao iniciada")

        mission = user_mission["mission"]
        xp_reward = mission.get("xp_reward", 10)

        user_mission["status"] = "completed"
        user_mission["completed_at"] = datetime.now(UTC)
        user_mission["pull_request_url"] = pull_request_url
        user_mission["xp_awarded"] = xp_reward

        # Dar XP
        await self._add_xp(
            user_id=user_id,
            amount=xp_reward,
            source_type="mission",
            source_id=mission_id,
            description=f"Completou missao: {mission['title']}",
        )

        # Atualizar contador
        user = self._users.get(user_id)
        if user:
            user["total_missions_completed"] += 1

            # Badge de primeira missao
            if user["total_missions_completed"] == 1:
                await self._award_badge(user_id, "first_mission")

        # Atualizar contador da missao
        mission["times_completed"] = mission.get("times_completed", 0) + 1

        return self._build_user_mission_response(user_mission)

    def _build_mission_response(self, mission: dict) -> MissionResponse:
        """Construir response de missao."""
        track = mission["track"]
        if isinstance(track, str):
            track = TrackType(track)

        difficulty = mission["difficulty"]
        if isinstance(difficulty, str):
            difficulty = DifficultyLevel(difficulty)

        return MissionResponse(
            id=mission["id"],
            code=mission["code"],
            title=mission["title"],
            description=mission["description"],
            track=track,
            difficulty=difficulty,
            category=mission["category"],
            xp_reward=mission["xp_reward"],
            badge_reward=mission.get("badge_reward"),
            required_level=mission.get("required_level", 1),
            prerequisites=mission.get("prerequisites", []),
            github_issue_url=mission.get("github_issue_url"),
            resources=mission.get("resources", []),
            video_url=mission.get("video_url"),
            recommended_agent=mission.get("recommended_agent"),
            is_featured=mission.get("is_featured", False),
            times_completed=mission.get("times_completed", 0),
        )

    def _build_user_mission_response(self, user_mission: dict) -> UserMissionResponse:
        """Construir response de missao do usuario."""
        return UserMissionResponse(
            mission=self._build_mission_response(user_mission["mission"]),
            status=user_mission["status"],
            started_at=user_mission["started_at"],
            completed_at=user_mission.get("completed_at"),
            pull_request_url=user_mission.get("pull_request_url"),
            xp_awarded=user_mission.get("xp_awarded", 0),
        )

    # =========================================================================
    # BADGE METHODS
    # =========================================================================

    async def list_badges(
        self, category: str | None = None, include_secret: bool = False
    ) -> list[BadgeInfo]:
        """Listar badges disponiveis."""
        badges = list(self._badges.values())
        if category:
            badges = [b for b in badges if b["category"] == category]
        if not include_secret:
            badges = [b for b in badges if not b.get("is_secret", False)]

        return [
            BadgeInfo(
                code=b["code"],
                name=b["name"],
                description=b["description"],
                icon=b["icon"],
                color=b.get("color"),
                rarity=b["rarity"],
                category=b["category"],
            )
            for b in badges
        ]

    async def get_user_badges(self, user_id: str) -> list[BadgeInfo]:
        """Listar badges do usuario."""
        user = self._users.get(user_id)
        if not user:
            return []

        return [
            BadgeInfo(
                code=b["code"],
                name=b["name"],
                description=b["description"],
                icon=b["icon"],
                color=b.get("color"),
                rarity=b["rarity"],
                category=b["category"],
                earned_at=b.get("earned_at"),
            )
            for b in user.get("badges", [])
        ]

    # =========================================================================
    # LEADERBOARD METHODS
    # =========================================================================

    async def get_leaderboard(
        self,
        track: TrackType | None = None,
        period: str = "all_time",
        limit: int = 10,
    ) -> LeaderboardResponse:
        """Obter leaderboard."""
        users = list(self._users.values())

        if track:
            users = [u for u in users if u["main_track"] == track]

        # Ordenar por XP
        users.sort(key=lambda x: x["total_xp"], reverse=True)

        entries = []
        for i, user in enumerate(users[:limit]):
            entries.append(
                LeaderboardEntry(
                    rank=i + 1,
                    user_id=user["user_id"],
                    username=user["username"],
                    avatar_url=user.get("avatar_url"),
                    total_xp=user["total_xp"],
                    current_rank=user["current_rank"],
                    main_track=user["main_track"],
                    badges_count=len(user.get("badges", [])),
                    weekly_xp=0,
                    change=0,
                )
            )

        return LeaderboardResponse(
            entries=entries,
            total_users=len(users),
            period=period,
            updated_at=datetime.now(UTC),
        )

    async def get_user_ranking(
        self, user_id: str, period: str = "all_time"
    ) -> dict[str, Any]:
        """Obter posicao do usuario no ranking."""
        users = list(self._users.values())
        users.sort(key=lambda x: x["total_xp"], reverse=True)

        for i, user in enumerate(users):
            if user["user_id"] == user_id:
                return {
                    "rank": i + 1,
                    "total_users": len(users),
                    "percentile": round((1 - i / len(users)) * 100, 1) if users else 0,
                    "period": period,
                }

        return {
            "rank": None,
            "total_users": len(users),
            "percentile": 0,
            "period": period,
        }

    # =========================================================================
    # STATS METHODS
    # =========================================================================

    async def get_stats(self) -> AcademyStatsResponse:
        """Obter estatisticas gerais."""
        users = list(self._users.values())
        conversations = list(self._conversations.values())

        total_xp = sum(u["total_xp"] for u in users)
        completed_missions = sum(u["total_missions_completed"] for u in users)

        # Track mais popular
        track_counts: dict[TrackType, int] = {}
        for user in users:
            track = user["main_track"]
            track_counts[track] = track_counts.get(track, 0) + 1
        top_track = (
            max(track_counts.keys(), key=lambda x: track_counts[x])
            if track_counts
            else TrackType.BACKEND
        )

        return AcademyStatsResponse(
            total_users=len(users),
            total_conversations=len(conversations),
            total_missions_completed=completed_missions,
            total_xp_distributed=total_xp,
            active_users_today=len([u for u in users if u.get("last_activity_date")]),
            top_track=top_track,
            avg_daily_xp=total_xp / max(len(users), 1),
        )

    async def get_user_stats(self, user_id: str) -> dict[str, Any]:
        """Obter estatisticas do usuario."""
        user = self._users.get(user_id)
        if not user:
            return {}

        conversations = [
            c for c in self._conversations.values() if c["user_id"] == user_id
        ]
        missions = self._user_missions.get(user_id, [])

        return {
            "total_xp": user["total_xp"],
            "current_level": user["current_level"],
            "current_rank": user["current_rank"],
            "total_conversations": len(conversations),
            "completed_conversations": len(
                [
                    c
                    for c in conversations
                    if c["status"] == ConversationStatus.COMPLETED
                ]
            ),
            "total_missions": len(missions),
            "completed_missions": len(
                [m for m in missions if m["status"] == "completed"]
            ),
            "badges_count": len(user.get("badges", [])),
            "current_streak": user["current_streak"],
            "longest_streak": user["longest_streak"],
            "agents_talked_to": list(set(c["agent_name"] for c in conversations)),
        }


# Singleton do servico
academy_service = AcademyService()
