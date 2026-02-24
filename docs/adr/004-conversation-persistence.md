# ADR-004: Conversation Persistence in Railway PostgreSQL

**Status**: Accepted
**Date**: 2026-02-24
**Author**: Anderson Henrique da Silva

## Context

After a production audit (2026-02-24), we discovered that **agent conversations are NOT being persisted durably**. The current state:

### What EXISTS in production (Railway Postgres)

| Table | Records | Persistent? |
|-------|---------|-------------|
| `investigations` | 119 | Yes |
| `alembic_version` | 1 | Yes |

### What is MISSING

| Expected Table | Status |
|---------------|--------|
| `academy_users` | NOT CREATED |
| `academy_conversations` | NOT CREATED |
| `academy_xp_transactions` | NOT CREATED |
| `academy_missions` | NOT CREATED |
| `academy_user_missions` | NOT CREATED |
| `academy_badges` | NOT CREATED |
| `entity_nodes` | NOT CREATED |
| `entity_relationships` | NOT CREATED |
| **chat_sessions** | NOT DESIGNED |
| **chat_messages** | NOT DESIGNED |

### Current (broken) conversation storage

| Layer | Storage | TTL | Survives deploy? |
|-------|---------|-----|-----------------|
| Chat sessions | Python dict (RAM) | Process lifetime | NO |
| Chat messages | Python dict (RAM) | Process lifetime | NO |
| Nana conversational memory | Redis | 24h | Partially |
| Nana episodic memory | Redis | 30 days | Partially |
| Investigations | PostgreSQL | Permanent | YES |

### Supabase role

The Supabase project (`pbsiyuattnwgohvkkkks` / cidadao.ai) is used **only for OAuth**. No `SUPABASE_URL` or `SUPABASE_SERVICE_ROLE_KEY` is set in the cidadao-api service.

## Decision

**Use Railway PostgreSQL as the single source of truth for all persistent data.**

- Supabase: OAuth only (login social)
- Railway Postgres: All application data (investigations, conversations, academy, entities)
- Railway Redis: Volatile cache, rate limiting, Nana short-term memory

## Changes Required

### Phase 1: New tables via Alembic migration

1. **`chat_sessions`** - Persistent chat sessions linked to user
2. **`chat_messages`** - Individual messages with role, content, agent_id, metadata
3. **`academy_users`** - Academy student profiles (already modeled in code)
4. **`academy_conversations`** - Educational conversations (already modeled)
5. **`academy_xp_transactions`** - XP ledger (already modeled)
6. **`academy_missions`** - Available missions (already modeled)
7. **`academy_user_missions`** - User progress (already modeled)
8. **`academy_badges`** - Badges (already modeled)

### Phase 2: Modify ChatService to persist to DB

Replace in-memory `self.sessions` and `self.messages` dicts with PostgreSQL writes:

- `get_or_create_session()` -> DB upsert
- `add_message()` -> DB insert
- `get_session_messages()` -> DB query
- `clear_session()` -> DB soft-delete

### Phase 3: Wire up academy endpoints

Ensure academy routes actually use DB sessions.

## Consequences

### Positive
- Conversations survive deploys and restarts
- Full audit trail of all agent interactions
- Enables analytics and usage metrics
- Academy gamification becomes functional

### Negative
- Slight latency increase for message storage (~5ms per DB write)
- Migration must be applied carefully to production

### Risks
- Alembic head mismatch if migrations were never properly chained
- Need to verify current `alembic_version` (`0dba430d74c4`) matches the latest migration
