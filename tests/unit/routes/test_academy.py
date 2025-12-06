"""
Academy API Tests.

Testes unitarios para os endpoints da Academy.
Parceria: Neural Thinker AI Engineering + IFSULDEMINAS/LabSoft
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.api.app import app
from src.schemas.academy import (
    ConversationStatus,
    DifficultyLevel,
    OnboardingStep,
    RankLevel,
    TrackType,
)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_current_user():
    """Mock authenticated user."""
    return {
        "user_id": "test_user_123",
        "sub": "test_user_123",
        "email": "test@example.com",
    }


@pytest.fixture
def auth_headers():
    """Generate auth headers for testing."""
    # For testing, we use a mock token
    return {"Authorization": "Bearer test_token"}


class TestAcademyAgentsEndpoints:
    """Tests for agent endpoints (public)."""

    def test_list_agents(self, client):
        """Test listing all available agents."""
        response = client.get("/api/v1/academy/agents")
        assert response.status_code == 200

        agents = response.json()
        assert isinstance(agents, list)
        assert len(agents) > 0

        # Check first agent has required fields
        agent = agents[0]
        assert "name" in agent
        assert "display_name" in agent
        assert "specialty" in agent
        assert "tracks" in agent
        assert "personality" in agent
        assert "greeting" in agent
        assert "is_available" in agent

    def test_list_agents_by_track(self, client):
        """Test filtering agents by track."""
        response = client.get("/api/v1/academy/agents?track=backend")
        assert response.status_code == 200

        agents = response.json()
        assert isinstance(agents, list)
        # All returned agents should support backend track
        for agent in agents:
            assert "backend" in agent["tracks"]

    def test_get_specific_agent(self, client):
        """Test getting a specific agent."""
        response = client.get("/api/v1/academy/agents/zumbi")
        assert response.status_code == 200

        agent = response.json()
        assert agent["name"] == "zumbi"
        assert agent["display_name"] == "Zumbi dos Palmares"
        assert "backend" in agent["tracks"] or "ia" in agent["tracks"]

    def test_get_nonexistent_agent(self, client):
        """Test getting a nonexistent agent returns 404."""
        response = client.get("/api/v1/academy/agents/nonexistent")
        assert response.status_code == 404


class TestAcademyTracksEndpoints:
    """Tests for tracks endpoints (public)."""

    def test_list_tracks(self, client):
        """Test listing all tracks."""
        response = client.get("/api/v1/academy/tracks")
        assert response.status_code == 200

        tracks = response.json()
        assert isinstance(tracks, list)
        assert len(tracks) == 4  # backend, frontend, ia, devops

        track_ids = [t["id"] for t in tracks]
        assert "backend" in track_ids
        assert "frontend" in track_ids
        assert "ia" in track_ids
        assert "devops" in track_ids

    def test_track_has_required_fields(self, client):
        """Test that each track has required fields."""
        response = client.get("/api/v1/academy/tracks")
        tracks = response.json()

        for track in tracks:
            assert "id" in track
            assert "name" in track
            assert "description" in track
            assert "icon" in track
            assert "color" in track
            assert "recommended_agents" in track


class TestAcademyMissionsEndpoints:
    """Tests for mission endpoints (public)."""

    def test_list_missions(self, client):
        """Test listing all missions."""
        response = client.get("/api/v1/academy/missions")
        assert response.status_code == 200

        missions = response.json()
        assert isinstance(missions, list)
        assert len(missions) > 0

    def test_list_missions_by_track(self, client):
        """Test filtering missions by track."""
        response = client.get("/api/v1/academy/missions?track=backend")
        assert response.status_code == 200

        missions = response.json()
        assert isinstance(missions, list)
        for mission in missions:
            assert mission["track"] == "backend"

    def test_list_missions_by_difficulty(self, client):
        """Test filtering missions by difficulty."""
        response = client.get("/api/v1/academy/missions?difficulty=easy")
        assert response.status_code == 200

        missions = response.json()
        assert isinstance(missions, list)
        for mission in missions:
            assert mission["difficulty"] == "easy"

    def test_list_featured_missions(self, client):
        """Test listing featured missions."""
        response = client.get("/api/v1/academy/missions?featured_only=true")
        assert response.status_code == 200

        missions = response.json()
        assert isinstance(missions, list)
        for mission in missions:
            assert mission["is_featured"] is True

    def test_get_specific_mission(self, client):
        """Test getting a specific mission."""
        response = client.get("/api/v1/academy/missions/mission_001")
        assert response.status_code == 200

        mission = response.json()
        assert mission["id"] == "mission_001"
        assert "title" in mission
        assert "description" in mission
        assert "xp_reward" in mission

    def test_get_nonexistent_mission(self, client):
        """Test getting a nonexistent mission returns 404."""
        response = client.get("/api/v1/academy/missions/nonexistent")
        assert response.status_code == 404


class TestAcademyBadgesEndpoints:
    """Tests for badge endpoints (public)."""

    def test_list_badges(self, client):
        """Test listing all badges."""
        response = client.get("/api/v1/academy/badges")
        assert response.status_code == 200

        badges = response.json()
        assert isinstance(badges, list)
        assert len(badges) > 0

        # Check badge has required fields
        badge = badges[0]
        assert "code" in badge
        assert "name" in badge
        assert "description" in badge
        assert "icon" in badge
        assert "rarity" in badge
        assert "category" in badge

    def test_list_badges_by_category(self, client):
        """Test filtering badges by category."""
        response = client.get("/api/v1/academy/badges?category=streak")
        assert response.status_code == 200

        badges = response.json()
        assert isinstance(badges, list)
        for badge in badges:
            assert badge["category"] == "streak"


class TestAcademyLeaderboardEndpoints:
    """Tests for leaderboard endpoints (public)."""

    def test_get_leaderboard(self, client):
        """Test getting leaderboard."""
        response = client.get("/api/v1/academy/leaderboard")
        assert response.status_code == 200

        leaderboard = response.json()
        assert "entries" in leaderboard
        assert "total_users" in leaderboard
        assert "period" in leaderboard
        assert "updated_at" in leaderboard

    def test_get_leaderboard_by_track(self, client):
        """Test getting leaderboard by track."""
        response = client.get("/api/v1/academy/leaderboard?track=backend")
        assert response.status_code == 200

        leaderboard = response.json()
        assert "entries" in leaderboard


class TestAcademyStatsEndpoints:
    """Tests for stats endpoints (public)."""

    def test_get_academy_stats(self, client):
        """Test getting academy stats."""
        response = client.get("/api/v1/academy/stats")
        assert response.status_code == 200

        stats = response.json()
        assert "total_users" in stats
        assert "total_conversations" in stats
        assert "total_missions_completed" in stats
        assert "total_xp_distributed" in stats


class TestAcademyUserEndpoints:
    """Tests for user endpoints (require auth)."""

    def test_get_my_profile_not_found(self, client):
        """Test that users without profile get 404."""
        response = client.get("/api/v1/academy/users/me")
        # Returns 404 when user profile not found
        assert response.status_code == 404
        # Response format may vary - check for the error message
        body = response.json()
        error_msg = body.get("detail") or body.get("error", {}).get("message", "")
        assert "Perfil nao encontrado" in error_msg

    @patch("src.api.middleware.authentication.get_current_user")
    def test_get_user_profile_public(self, mock_auth, client, mock_current_user):
        """Test getting a user profile by ID (public)."""
        # This endpoint is public, no auth needed
        response = client.get("/api/v1/academy/users/some_user_id")
        # Will be 404 since user doesn't exist
        assert response.status_code == 404


class TestAcademyConversationEndpoints:
    """Tests for conversation endpoints (require auth)."""

    def test_start_conversation_user_not_found(self, client):
        """Test that users without profile cannot start conversations."""
        response = client.post(
            "/api/v1/academy/conversations",
            json={
                "agent_name": "zumbi",
                "track": "backend",
                "difficulty": "easy",
            },
        )
        # Returns error when user doesn't have academy profile
        # Could be 404 (user not found) or 400 (validation error)
        assert response.status_code in [400, 404, 500]


class TestAcademyService:
    """Tests for AcademyService directly."""

    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test that academy service initializes correctly."""
        from src.services.academy_service import academy_service

        assert academy_service is not None
        assert len(academy_service._badges) > 0
        assert len(academy_service._missions) > 0

    @pytest.mark.asyncio
    async def test_create_user(self):
        """Test user creation."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        user = await service.create_user(
            user_id="test_user_001",
            username="testuser",
            email="test@example.com",
            main_track=TrackType.BACKEND,
        )

        assert user.user_id == "test_user_001"
        assert user.username == "testuser"
        assert user.progress.current_level == 1
        assert user.progress.current_rank == RankLevel.NOVATO

    @pytest.mark.asyncio
    async def test_duplicate_user_raises_error(self):
        """Test that creating duplicate user raises error."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        await service.create_user(
            user_id="duplicate_user",
            username="user1",
        )

        with pytest.raises(ValueError, match="Usuario ja cadastrado"):
            await service.create_user(
                user_id="duplicate_user",
                username="user2",
            )

    @pytest.mark.asyncio
    async def test_start_conversation(self):
        """Test starting a conversation."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        user = await service.create_user(
            user_id="conv_test_user",
            username="convtester",
        )

        conversation = await service.start_conversation(
            user_id="conv_test_user",
            agent_name="zumbi",
            track=TrackType.BACKEND,
            topic="Anomaly Detection",
            difficulty=DifficultyLevel.EASY,
        )

        assert conversation.agent_name == "zumbi"
        assert conversation.status == ConversationStatus.ACTIVE
        assert conversation.xp_earned > 0  # XP for starting

    @pytest.mark.asyncio
    async def test_send_message(self):
        """Test sending a message in conversation."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        await service.create_user(
            user_id="msg_test_user",
            username="msgtester",
        )

        conversation = await service.start_conversation(
            user_id="msg_test_user",
            agent_name="anita",
            track=TrackType.IA,
            topic=None,
            difficulty=DifficultyLevel.BEGINNER,
        )

        response = await service.send_message(
            conversation_id=conversation.id,
            user_id="msg_test_user",
            message="Como funciona a deteccao de anomalias?",
        )

        assert response.role == "assistant"
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_complete_conversation(self):
        """Test completing a conversation."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        await service.create_user(
            user_id="complete_test_user",
            username="completetester",
        )

        conversation = await service.start_conversation(
            user_id="complete_test_user",
            agent_name="tiradentes",
            track=TrackType.BACKEND,
            topic=None,
            difficulty=DifficultyLevel.EASY,
        )

        completed = await service.complete_conversation(
            conversation_id=conversation.id,
            user_id="complete_test_user",
            rating=5,
            feedback="Excelente aula!",
        )

        assert completed.status == ConversationStatus.COMPLETED
        assert completed.xp_earned > conversation.xp_earned  # More XP after completion

    @pytest.mark.asyncio
    async def test_start_mission(self):
        """Test starting a mission."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        await service.create_user(
            user_id="mission_test_user",
            username="missiontester",
        )

        user_mission = await service.start_mission(
            user_id="mission_test_user",
            mission_id="mission_001",
        )

        assert user_mission.status == "in_progress"
        assert user_mission.mission.id == "mission_001"

    @pytest.mark.asyncio
    async def test_complete_mission(self):
        """Test completing a mission."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        await service.create_user(
            user_id="mission_complete_user",
            username="missioncomplete",
        )

        await service.start_mission(
            user_id="mission_complete_user",
            mission_id="mission_001",
        )

        completed = await service.complete_mission(
            user_id="mission_complete_user",
            mission_id="mission_001",
            pull_request_url="https://github.com/example/pr/123",
        )

        assert completed.status == "completed"
        assert completed.xp_awarded > 0

    @pytest.mark.asyncio
    async def test_xp_accumulation(self):
        """Test that XP accumulates correctly."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        user = await service.create_user(
            user_id="xp_test_user",
            username="xptester",
        )
        initial_xp = user.progress.total_xp

        # Start conversation (gives XP)
        await service.start_conversation(
            user_id="xp_test_user",
            agent_name="zumbi",
            track=TrackType.BACKEND,
            topic=None,
            difficulty=DifficultyLevel.EASY,
        )

        # Get updated user
        updated_user = await service.get_user_profile("xp_test_user")
        assert updated_user.progress.total_xp > initial_xp

    @pytest.mark.asyncio
    async def test_leaderboard(self):
        """Test leaderboard functionality."""
        from src.services.academy_service import AcademyService

        service = AcademyService()

        # Create multiple users with different XP
        await service.create_user(user_id="leader1", username="leader1")
        await service.create_user(user_id="leader2", username="leader2")

        # Give leader1 more XP
        await service.start_conversation(
            user_id="leader1",
            agent_name="zumbi",
            track=TrackType.BACKEND,
            topic=None,
            difficulty=DifficultyLevel.EASY,
        )

        leaderboard = await service.get_leaderboard(limit=10)

        assert leaderboard.total_users >= 2
        if len(leaderboard.entries) > 0:
            # First entry should have highest XP
            for i in range(len(leaderboard.entries) - 1):
                assert (
                    leaderboard.entries[i].total_xp
                    >= leaderboard.entries[i + 1].total_xp
                )


class TestAcademyOnboardingService:
    """Tests for onboarding service methods."""

    @pytest.mark.asyncio
    async def test_get_onboarding_state_new_user(self):
        """Test onboarding state for non-existent user."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        state = await service.get_onboarding_state(
            user_id="new_user_onboarding",
            demo_mode=True,
        )

        assert state.step == OnboardingStep.WELCOME
        assert "Bem-vindo" in state.message

    @pytest.mark.asyncio
    async def test_get_onboarding_demo_mode_shows_terms(self):
        """Test that demo mode always shows terms."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        await service.create_user(
            user_id="demo_user",
            username="demouser",
        )

        state = await service.get_onboarding_state(
            user_id="demo_user",
            demo_mode=True,
        )

        assert state.step == OnboardingStep.TERMS_CONSENT
        assert state.show_terms is True
        assert state.terms_content is not None
        assert "Termos de Consentimento" in state.terms_content
        assert state.ranking_explanation is not None
        assert "Sistema de XP" in state.ranking_explanation

    @pytest.mark.asyncio
    async def test_accept_terms(self):
        """Test accepting terms of consent."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        await service.create_user(
            user_id="terms_user",
            username="termsuser",
        )

        result = await service.accept_terms(
            user_id="terms_user",
            accepted=True,
            main_track=TrackType.BACKEND,
        )

        assert result.step == OnboardingStep.TRACK_SELECTION
        assert result.data.get("terms_accepted") is True
        assert result.data.get("xp_earned") == 10

    @pytest.mark.asyncio
    async def test_complete_onboarding(self):
        """Test completing the onboarding process."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        await service.create_user(
            user_id="complete_onboarding_user",
            username="completeuser",
        )

        result = await service.complete_onboarding(
            user_id="complete_onboarding_user",
            main_track=TrackType.IA,
            github_username="testgithub",
        )

        assert result.step == OnboardingStep.COMPLETED
        assert result.data.get("onboarding_completed") is True
        assert result.data.get("main_track") == "ia"


class TestAcademyGitHubService:
    """Tests for GitHub stats service methods."""

    @pytest.mark.asyncio
    async def test_connect_github(self):
        """Test connecting GitHub account."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        await service.create_user(
            user_id="github_user",
            username="githubuser",
        )

        result = await service.connect_github(
            user_id="github_user",
            github_username="testgithub",
        )

        assert result["success"] is True
        assert result["github_username"] == "testgithub"

    @pytest.mark.asyncio
    async def test_get_github_stats(self):
        """Test getting GitHub stats."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        await service.create_user(
            user_id="stats_user",
            username="statsuser",
            github_username="teststats",
        )

        stats = await service.get_github_stats(user_id="stats_user")

        assert stats is not None
        assert stats.github_username == "teststats"
        assert stats.total_commits == 0
        assert stats.total_prs_merged == 0

    @pytest.mark.asyncio
    async def test_update_github_stats_commits(self):
        """Test updating GitHub stats with commits."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        user = await service.create_user(
            user_id="commit_user",
            username="commituser",
            github_username="commitgithub",
        )
        initial_xp = user.progress.total_xp

        stats = await service.update_github_stats(
            user_id="commit_user",
            commits=5,
        )

        assert stats.total_commits == 5
        assert stats.commits_this_week == 5

        # Verify XP was awarded (15 XP per commit)
        updated_user = await service.get_user_profile("commit_user")
        assert updated_user.progress.total_xp > initial_xp

    @pytest.mark.asyncio
    async def test_update_github_stats_prs(self):
        """Test updating GitHub stats with PRs."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        await service.create_user(
            user_id="pr_user",
            username="pruser",
            github_username="prgithub",
        )

        stats = await service.update_github_stats(
            user_id="pr_user",
            prs_opened=2,
            prs_merged=1,
            prs_approved=1,
        )

        assert stats.total_prs_opened == 2
        assert stats.total_prs_merged == 1
        assert stats.total_prs_approved == 1
        assert stats.contribution_quality_score > 0

    @pytest.mark.asyncio
    async def test_first_pr_badge(self):
        """Test that first PR merged awards badge."""
        from src.services.academy_service import AcademyService

        service = AcademyService()
        await service.create_user(
            user_id="first_pr_user",
            username="firstpruser",
            github_username="firstprgithub",
        )

        await service.update_github_stats(
            user_id="first_pr_user",
            prs_merged=1,
        )

        user = await service.get_user_profile("first_pr_user")
        badge_codes = [b.code for b in user.badges]
        assert "first_pr" in badge_codes
