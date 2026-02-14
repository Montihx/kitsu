# Kitsu

Kitsu — аниме-стриминг сервис с явным разделением репозитория:

- `backend/` — FastAPI + SQLAlchemy/Alembic + PostgreSQL + Redis
- `frontend/` — Next.js 15 + TypeScript + Zustand + React Query

Служебные каталоги в корне:

- `docs/` — архитектура, контракты, архив и ассеты документации
- `.github/` — CI workflow
- `scripts/` — инженерные скрипты проекта

## Run locally

### Docker Compose

```bash
docker compose up --build
```

### Backend

```bash
cd backend
python -m pip install -e .[dev]
export DATABASE_URL='postgresql+asyncpg://user:pass@localhost:5432/kitsu'
export SECRET_KEY='please-set-secret-key'
export ALLOWED_ORIGINS='http://localhost:3000'
python -m uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm ci
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

## Quality checks

### Backend

```bash
cd backend
ruff check app tests
mypy app/models app/schemas
python -m pytest
```

### Frontend

```bash
cd frontend
npm run lint
npm run typecheck
npm run test
npm run build
```

## CI

Workflow: `.github/workflows/ci.yml`.

- backend: `ruff`, `mypy`, `pytest`
- frontend: `eslint`, `tsc`, `vitest`, `next build`
