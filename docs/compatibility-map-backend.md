# Backend Compatibility Map (Phase 2 baseline)

Цель документа: зафиксировать текущие контракты до реорганизации backend, чтобы не сломать фронт и существующие интеграции.

## 1) Точки входа

- Основной ASGI entrypoint: `backend/app/main.py` (`app = FastAPI(...)`).
- Lifespan и startup/shutdown логика находятся в том же модуле (`main.py`).
- Дополнительный агрегатор `/api/*` маршрутов: `backend/app/api/router.py`.

## 2) Текущие API пути (baseline scan)

Сканировано из OpenAPI (`PYTHONPATH=backend python ... from app.main import app; app.openapi()`) и подтверждено по роутерам.

### Public/Auth/Core

- `POST /auth/register` -> access/refresh токены (`201`).
- `POST /auth/login` -> access/refresh токены (`200`).
- `POST /auth/refresh` -> новые токены (`200`).
- `POST /auth/logout` -> `204` без тела.
- `GET /auth/users/me` -> текущий пользователь (`200`).
- `GET /anime/` -> список аниме (`200`).
- `GET /anime/{anime_id}` -> детали аниме (`200`, `404` через HTTPException).
- `GET /releases/` -> список релизов (`200`).
- `GET /releases/{release_id}` -> релиз по id (`200`, `404` через HTTPException).
- `GET /episodes/` -> эпизоды по `release_id` (`200`, `404` через HTTPException).
- `GET /favorites/` -> список избранного (`200`).
- `POST /favorites/` -> добавить в избранное (`201`).
- `DELETE /favorites/{anime_id}` -> удалить из избранного (`204`).
- `POST /watch/progress` -> upsert прогресса (`200`).
- `GET /watch/continue` -> continue watching (`200`).
- `GET /health` -> health status (`200`, сейчас `{ "status": "ok" | "error" }`).

### Internal/Proxy/Admin API under `/api`

- `GET /api/health`
- `GET /api/home`
- `GET /api/schedule`
- `GET /api/search`
- `GET /api/search/suggestion`
- `GET /api/anime/{anime_id}`
- `GET /api/anime/{anime_id}/episodes`
- `GET /api/episode/servers`
- `GET /api/episode/sources`
- `POST /api/import/{provider}`
- `GET /api/admin/anime/`
- `GET /api/admin/anime/{anime_id}`
- `PATCH /api/admin/anime/{anime_id}`

### Admin/Parser control endpoints

- `/admin/users*`, `/admin/roles*`, `/admin/permissions`, `/admin/system/health`, `/admin/system/maintenance`
- `/admin/parser/*` (dashboard, settings, run, publish, logs, mode, emergency-stop и т.д.)

## 3) Текущий формат ответов (как есть)

В проекте **нет единого envelope-контракта на всех эндпоинтах**. Есть смешанные форматы:

1. Прямые Pydantic response_model (например `/anime`, `/favorites`, `/auth/*`) — возвращают объект/массив без `{data,error}`.
2. Proxy API часто возвращает `{ "data": ... }`.
3. `/health` возвращает `{ "status": "ok|error" }`.
4. Ошибки централизуются в `main.py` через exception handlers и могут формироваться как legacy payload с кодом/сообщением.

Вывод: для Phase 2 нужен адаптерный подход, чтобы не ломать фронт-контракты.

## 4) Зависимости фронта от backend (по поиску вызовов)

Фронтенд явно вызывает:

- Auth: `/auth/login`, `/auth/register`, `/users/me`, `/auth/logout`, `/auth/refresh`
- Catalog/User: `/anime/*`, `/favorites`, `/watch/progress`, `/watch/continue`
- Proxy: `/api/schedule`, `/api/episode/sources`, `/api/episode/servers`, `/api/import/anilist`, `/api/search*`
- Admin UI: `/api/admin/anime/*`

Чувствительные для совместимости места: auth/favorites/watch/anime и proxy `/api/*`, т.к. они напрямую дергаются компонентами/хуками фронта.

## 5) “Не ломаемые” контракты для Phase 2

Минимум, который нельзя ломать:

- Пути и HTTP-методы перечисленных endpoint-ов.
- Статусы: `201` для register/favorites create, `204` для logout/favorites delete.
- Базовые поля токенов в auth ответах: `access_token`, `refresh_token`.
- Базовые поля профиля (`/auth/users/me`), избранного (`/favorites`), прогресса (`/watch/*`).
- Доступность `GET /health` для compose healthcheck.

## 6) Known risks / fragile areas

- `backend/app/main.py` перегружен (lifespan + middleware + handlers + routing) — высокий риск регрессий при правках.
- Смешение форматов ответа (`plain model` vs `{data: ...}`) — риск несовместимости фронта.
- Многоуровневая маршрутизация (`routers/*`, `api/*`, `admin/*`, `parser/admin/*`) — легко сломать префиксы.
- Настройки/инициализация завязаны на env и внешние зависимости (Postgres/Redis), важен аккуратный deferred init.
- Парсер/админ контур содержит много endpoint-ов с operational semantics (restart/sync/mode/emergency-stop); трогать только структурно и с тестами.

## 7) Baseline команды сканирования

- `rg -n "@(?:app|router)\.(get|post|put|delete|patch)\(" backend/app -S`
- `PYTHONPATH=backend python -c "... from app.main import app; print(app.openapi()) ..."`
- `python script` по frontend для поиска `api.get/post/...` вызовов.

