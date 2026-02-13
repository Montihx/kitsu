# CLAUDE.md — AI Assistant Guide for Kitsu

## Project Overview

Kitsu is an anime catalog and HLS playback web service. It is a monorepo with two separate applications:

- **`frontend/`** — Next.js 15 (React 18, App Router) UI and HTTP client
- **`backend/`** — FastAPI (Python 3.12+) REST API and business logic

The primary documentation language is Russian. Code, comments, and variable names are in English.

## Architecture

### Frontend (Next.js 15)

- **Framework:** Next.js 15 with App Router (`frontend/app/`)
- **State management:** Zustand (`frontend/store/`)
- **Server state:** React Query 3 + Axios (`frontend/query/`, `frontend/mutation/`)
- **Styling:** Tailwind CSS 3 + Radix UI (headless) + shadcn/ui (`frontend/components/ui/`)
- **Video player:** Artplayer + hls.js (`frontend/components/kitsune-player.tsx` — excluded from TypeScript checking)
- **PWA:** Enabled via `next-pwa` (disabled in development)
- **Output:** Standalone (`next.config.mjs` → `output: "standalone"`)
- **Path alias:** `@/*` maps to `frontend/*` root

### Backend (FastAPI)

- **Framework:** FastAPI (async/ASGI) served by Uvicorn
- **Database:** PostgreSQL 16 via async SQLAlchemy 2 + asyncpg
- **Migrations:** Alembic (`backend/alembic/versions/`)
- **Auth:** JWT (HS256) — access tokens (30 min) + refresh tokens (14 days)
- **RBAC:** Role-based access control enforced via `require_enforced_permission()` dependency
- **Background jobs:** In-process queue (`default_job_runner`) — no persistence, clears on restart
- **Caching/coordination:** Redis 7

### Backend Layers

```
Routers (API) → Use Cases → Services → CRUD/Repositories → SQLAlchemy Models → PostgreSQL
                                     → Domain/Ports (abstractions)
                                     → Infrastructure (Redis, external HTTP)
```

- `app/routers/` — HTTP route handlers
- `app/schemas/` — Pydantic request/response schemas
- `app/use_cases/` — Application use cases (auth, favorites, watch)
- `app/services/` — Business services
- `app/crud/` — Data access operations
- `app/models/` — SQLAlchemy ORM models
- `app/domain/ports/` — Abstract interfaces
- `app/infrastructure/` — Redis, external services
- `app/security/` — JWT handling
- `app/parser/` — Anime parser subsystem (staging architecture)
- `app/api/` — API sub-routing (internal + proxy layers)

### API Boundary

- **`/api/internal/`** — Business endpoints with DB access (favorites, watch, users, health)
- **`/api/proxy/`** — Thin read-only layer proxying external sources (HiAnime, AniList) — no business logic, no DB writes
- **`/auth/*`** — Authentication endpoints (register, login, refresh, logout)

## Contracts (Source of Truth)

**`docs/contracts/` is the mandatory source of truth.** Before making changes, read the relevant contract. Any documentation outside `contracts/` that contradicts a contract is considered stale.

| Contract | File | Governs |
|----------|------|---------|
| Auth | `docs/contracts/auth.md` | JWT tokens, login/register/refresh/logout flows |
| API boundary | `docs/contracts/api-boundary.md` | Internal vs proxy layer separation |
| RBAC | `docs/contracts/rbac.md` | Roles, permissions, enforcement |
| Background jobs | `docs/contracts/background-jobs.md` | Job lifecycle, idempotency, retry policy |
| Frontend-backend | `docs/contracts/frontend-backend.md` | Routes the frontend calls, error handling |
| Player | `docs/contracts/player.md` | Playback metadata types (foundation only) |
| Parser | `docs/contracts/parser.md` | Parser actor permissions, staging architecture, invariants |

## Quick Start — Development

### Frontend

```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

Dev server runs on port 3000.

### Backend

Requires PostgreSQL and optionally Redis:

```bash
cd backend
python -m pip install -e .[dev]
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/kitsu \
SECRET_KEY=please-set-secret-key \
ALLOWED_ORIGINS=http://localhost:3000 \
python -m uvicorn app.main:app
```

Dev server runs on port 8000. Alembic migrations run automatically on startup.

### Docker (full stack)

```bash
BACKEND_PORT=8000 FRONTEND_PORT=3000 docker compose up --build frontend backend
```

Services: PostgreSQL 16, Redis 7, backend (FastAPI), frontend (Next.js).

## Commands

### Frontend (`frontend/`)

| Command | What it does |
|---------|-------------|
| `npm run dev` | Start Next.js dev server |
| `npm run build` | Production build |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm test` | Run Vitest (`vitest run --passWithNoTests`) |

### Backend (`backend/`)

| Command | What it does |
|---------|-------------|
| `pip install -e .[dev]` | Install with dev dependencies |
| `python -m pytest` | Run all tests |
| `python -m uvicorn app.main:app` | Start dev server |
| `alembic upgrade head` | Apply all migrations |
| `alembic revision --autogenerate -m "desc"` | Generate new migration |
| `python scripts/seed_admin_core.py` | Seed admin roles/permissions |

## Testing

### Frontend tests

- **Framework:** Vitest 3.2
- **Config:** `frontend/vitest.config.ts`
- **Test location:** `frontend/__tests__/**/*.test.ts`
- **Run:** `cd frontend && npm test`
- Uses `--passWithNoTests` flag — passes when no tests exist

### Backend tests

- **Framework:** pytest 8 + pytest-asyncio
- **Config:** `backend/pyproject.toml` `[tool.pytest.ini_options]`
- **Test location:** `backend/tests/test_*.py`
- **Run:** `cd backend && python -m pytest`
- Async mode: `auto` (no need for `@pytest.mark.asyncio`)

## Linting & Type Checking

### Frontend

- **ESLint** config: `frontend/.eslintrc.json`
  - Extends: `next/core-web-vitals`, `next/typescript`
  - Disabled rules: `@typescript-eslint/no-explicit-any`, `@typescript-eslint/no-non-null-asserted-optional-chain`, `react-hooks/exhaustive-deps`
- **TypeScript** strict mode enabled (`frontend/tsconfig.json`)
  - `strict: true`, `noEmit: true`, `isolatedModules: true`
  - Excluded from TS: `player/**/*`, `components/kitsune-player.tsx`

### Backend

- No explicit Python linter configured in `pyproject.toml`

## Environment Variables

### Frontend

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API URL (e.g., `http://localhost:8000`) |
| `NEXT_PUBLIC_PROXY_URL` | m3u8 proxy URL for HLS playback (external service) |

### Backend

| Variable | Required | Purpose |
|----------|----------|---------|
| `SECRET_KEY` | Yes | JWT signing key (>= 32 chars) |
| `DATABASE_URL` | Yes | PostgreSQL async connection string |
| `ALLOWED_ORIGINS` | Yes | CORS origins (CSV or JSON array, **no trailing slashes**) |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Alt | Individual DB connection params |
| `REDIS_URL` | No | Redis connection string (default: `redis://localhost:6379/0`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Access token TTL (default: 30) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | Refresh token TTL (default: 14) |
| `LOG_LEVEL` | No | Logging level (default: INFO) |
| `DEBUG` | No | Debug mode (default: false) |

## Key Conventions

### Architectural rules

1. **Contracts first**: Read `docs/contracts/` before modifying auth, API boundaries, RBAC, background jobs, or parser logic.
2. **Proxy layer is read-only**: `/api/proxy/` endpoints must never write to DB, manage tokens, or execute business logic.
3. **RBAC is backend-only**: Frontend may hide UI elements based on roles but must never enforce access control — the backend is the sole authority.
4. **Background jobs are fire-and-forget**: HTTP responses must not depend on job success. Jobs use idempotent keys and create their own DB sessions.
5. **Parser is not admin**: The parser is a separate system actor with limited permissions (`parser.*` only). It cannot publish, delete, or override `source = "manual"` data. All parser writes go through staging tables first.

### Code conventions

- **Frontend path imports**: Use `@/` alias (e.g., `@/components/ui/button`)
- **Frontend UI components**: shadcn/ui lives in `frontend/components/ui/` — generated via shadcn CLI configured in `frontend/components.json`
- **Backend schemas**: Pydantic v2 models in `app/schemas/`
- **Backend models**: SQLAlchemy 2 declarative models in `app/models/`
- **Migrations**: Sequential numbered files (`0001_`, `0002_`, ...) in `backend/alembic/versions/`

### Error handling conventions

- Backend returns `{code, message, details?}` structure on errors
- Frontend does not mask server errors — 401/403/5xx are surfaced to the user
- Proxy endpoints return 502/500 when upstream is unavailable
- Axios timeout: 10 seconds, no automatic retries

## Database

- **Engine:** PostgreSQL 16
- **ORM:** SQLAlchemy 2 (async)
- **Tables:** users, anime, releases, episodes, favorites, watch_progress, refresh_tokens, roles, permissions, role_permissions, user_roles, audit_log
- **Migrations:** 7 applied (0001–0007)
- **Connection pool:** Configurable via `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_RECYCLE`, `DB_POOL_PRE_PING`
- Migrations run automatically on backend startup

## File Layout Reference

```
kitsu/
├── frontend/
│   ├── app/              # Next.js pages (app router)
│   ├── components/       # React components
│   │   ├── ui/           # shadcn/ui primitives
│   │   ├── common/       # Shared components
│   │   └── player/       # Player components
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utilities
│   ├── store/            # Zustand stores
│   ├── query/            # React Query configs
│   ├── mutation/         # React Query mutations
│   ├── mappers/          # Data mappers
│   ├── types/            # TypeScript type definitions
│   ├── auth/             # Auth utilities
│   ├── providers/        # Context providers
│   ├── constants/        # Constants
│   ├── utils/            # Utility functions
│   ├── __tests__/        # Vitest tests
│   └── public/           # Static assets & PWA manifest
├── backend/
│   ├── app/
│   │   ├── main.py       # FastAPI app entry point
│   │   ├── config.py     # Settings (from env vars)
│   │   ├── database.py   # SQLAlchemy async engine
│   │   ├── models/       # ORM models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── routers/      # API routes
│   │   ├── api/          # API sub-routing (internal/proxy)
│   │   ├── use_cases/    # Application use cases
│   │   ├── services/     # Business services
│   │   ├── crud/         # CRUD operations
│   │   ├── domain/ports/ # Abstract interfaces
│   │   ├── infrastructure/ # Redis, externals
│   │   ├── security/     # JWT, auth
│   │   ├── auth/         # RBAC definitions
│   │   ├── parser/       # Parser subsystem
│   │   ├── player/       # Player domain (stub)
│   │   └── background/   # Background job runner
│   ├── alembic/          # Database migrations
│   ├── tests/            # pytest tests
│   ├── scripts/          # Utility scripts
│   └── docs/             # Backend-specific docs
├── docs/                 # Project documentation
│   ├── contracts/        # Architectural contracts (source of truth)
│   ├── ARCHITECTURE.md   # System architecture
│   ├── BACKEND.md        # Backend details
│   ├── FRONTEND.md       # Frontend details
│   └── ...
├── docker-compose.yml    # Multi-service orchestration
├── Dockerfile            # Frontend Docker build
└── README.md             # Quick start (Russian)
```
