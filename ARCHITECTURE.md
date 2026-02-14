# Kitsu Architecture

Этот документ фиксирует целевую промышленную архитектуру репозитория и текущие инварианты проекта.

## Repository layout

- `frontend/` — клиент на Next.js 15 (App Router, UI, SSR/CSR, state management).
- `backend/` — API и бизнес-логика на FastAPI.
- `docs/` — детальные контракты, решения и спецификации.
- `docs/archive/` — архив нерелевантных/исторических артефактов и рабочих заметок.

## Backend (FastAPI)

`backend/app/` разбит на слои:

- `api/` и `routers/` — HTTP endpoints, зависимости, версионирование API.
- `schemas/` — Pydantic DTO и ответные контракты.
- `models/` — SQLAlchemy ORM модели домена.
- `crud/` и `services/` — доступ к данным и бизнес-операции.
- `auth/` и `security/` — JWT, RBAC, permission enforcement.
- `infrastructure/` — Redis и внешняя инфраструктура.
- `parser/` и `background/` — планировщики, worker-процессы и интеграции.

Ключевые архитектурные принципы:

1. **Контрактность API** — форматы запросов/ответов определяются в `schemas/`.
2. **Изоляция бизнес-логики** — роутеры не содержат бизнес-правил.
3. **Infrastructure as boundary** — Redis/БД/внешние API за abstraction-слоем.
4. **Безопасность по умолчанию** — централизованные auth и RBAC policy.

## Frontend (Next.js 15)

- `frontend/app/` — маршруты и рендеринг (SSR/CSR/streaming).
- `frontend/components/` — UI-слой и player-компоненты.
- `frontend/query/` и `frontend/mutation/` — удалённые запросы.
- `frontend/store/` — локальный state (Zustand).
- `frontend/lib/` — API-клиент, адаптеры и инфраструктурный код.
- `frontend/types/` — единый источник типизации клиентских контрактов.

Ключевые архитектурные принципы:

1. **Typed boundaries** — строгие TypeScript типы для API/компонентов.
2. **Composition over duplication** — переиспользование UI и query-модулей.
3. **Predictable data flow** — чёткое разделение server/client state.

## Quality gates

Репозиторий валидируется CI workflow (`.github/workflows/ci.yml`):

- Backend: `ruff check app tests`, `mypy app/models app/schemas`, `pytest`.
- Frontend: `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build`.

## Documentation map

- `README.md` — быстрый старт, запуск и команды разработки.
- `docs/ARCHITECTURE.md` — расширенная схема архитектуры.
- `docs/contracts/*.md` — контракты API/границ.
- `CHANGELOG.md` — журнал изменений по принципу Keep a Changelog.
