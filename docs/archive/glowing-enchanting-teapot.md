# KITSU — RISK REGISTER & STABILIZATION BASELINE

---

## ЧАСТЬ VI: EXECUTION CONSTRAINTS

### CRITICAL CORE — модули с каскадным blast radius

Изменение любого из этих модулей может вызвать каскадные ошибки в зависимых файлах. Каждое изменение требует верификации всех downstream-зависимостей.

| Модуль | Importers | Downstream-зона |
|--------|-----------|-----------------|
| `backend/app/dependencies.py` | 13 файлов | Все 7 роутеров + admin + parser admin + auth helpers + api admin |
| `backend/app/database.py` | 5 файлов | dependencies.py → (все роутеры), parser autoupdate, parser worker, permission_service |
| `backend/app/errors.py` | 9 файлов | main.py, auth helpers, parser, все use_cases (auth, favorites, watch) |
| `backend/app/config.py` | 6 файлов | database.py → (все через dependencies), alembic, parser, main.py |
| `frontend/store/auth-store.tsx` | 20 файлов | 8 pages, 6 components, 2 hooks, api.ts, auth-errors.ts, rbac.ts, store-provider |
| `frontend/lib/api.ts` | 19 файлов | 9 query hooks, 3 pages, 2 components, 2 hooks, 2 adapters, api-retry |
| `frontend/types/anime.ts` | 22 файла | 7 components, 4 pages, 6 queries, store, constants, proxy adapter, mapper |

**Правило:** Любое изменение Critical Core модуля — это отдельная единица работы с обязательной верификацией всех importers до перехода к следующей задаче.

---

### УРОВЕНЬ S0: ТЕСТОВАЯ ИНФРАСТРУКТУРА (C4)

**Устраняемый риск:** C4 — нулевое покрытие тестами.
**Задача:** Создание тестовой инфраструктуры

**Deliverables (файлы, которые будут созданы/изменены):**

| Действие | Файл | Назначение |
|----------|------|------------|
| ИЗМЕНИТЬ | `backend/pyproject.toml` | Заменить `pytest-anyio==0.0.0` на `pytest-asyncio`; добавить `[tool.pytest.ini_options]`. `filterwarnings` — опционально, добавлять только если runner падает из-за warnings-as-errors |
| СОЗДАТЬ | `backend/tests/__init__.py` | Пустой файл, делает `tests/` пакетом Python |
| СОЗДАТЬ | `backend/tests/conftest.py` | Минимальный conftest: override env vars для `Settings.from_env()` |
| СОЗДАТЬ | `backend/tests/test_smoke.py` | Smoke-тест: `from app.main import app` → `isinstance(app, FastAPI)` |
| ИЗМЕНИТЬ | `frontend/package.json` | Добавить test runner и скрипт `"test"` в devDependencies/scripts |
| СОЗДАТЬ | `frontend/vitest.config.ts` | Конфигурация Vitest (или аналогичного runner) |
| СОЗДАТЬ | `frontend/__tests__/smoke.test.ts` | Smoke-тест: `expect(true).toBe(true)` — runner стартует |

**Разрешено изменять:**
- Создание `backend/tests/` директории и файлов внутри неё
- Создание `frontend/__tests__/` и файлов внутри неё
- `backend/pyproject.toml` — ТОЛЬКО секция `[tool.pytest]`, `[project.optional-dependencies]`
- `frontend/package.json` — ТОЛЬКО test-зависимости в `devDependencies` и `scripts.test`
- Создание `frontend/vitest.config.ts` (новый файл, не production)

**Read-only (запрещено изменять):**
- Все файлы `backend/app/` — бизнес-логика, роутеры, модели, CRUD, use_cases, config, database, dependencies
- Все файлы `frontend/app/`, `frontend/components/`, `frontend/lib/`, `frontend/store/`
- `backend/alembic/` — миграции
- Docker-конфигурация
- `frontend/tsconfig.json`, `frontend/next.config.mjs`

**Scope backend smoke-теста:**
- Импорт `app.main:app` — проверка что FastAPI instance создаётся
- БЕЗ обращения к БД, БЕЗ обращения к Redis, БЕЗ запуска lifespan
- conftest.py ТОЛЬКО устанавливает `os.environ` для `Settings.from_env()` — НЕ создаёт engine, НЕ импортирует модели, НЕ создаёт fixture для DB session
- DATABASE_URL и REDIS_URL в conftest задаются **исключительно** для прохождения валидации `Settings.from_env()`; smoke-тест НЕ должен требовать поднятого Postgres или Redis
- Если `from app.main import app` инициирует реальное подключение к DB/Redis (I/O на этапе импорта) — это **STOP CONDITION**: вернуться к анализу, зафиксировать как блокер

**Scope frontend smoke-теста:**
- Test runner запускается и завершается с exit code 0
- `--passWithNoTests` допускается
- БЕЗ импорта компонентов, БЕЗ чтения `frontend/lib/*`, `frontend/store/*`

**Dev deps policy (S0):**
- Backend: допускаются ТОЛЬКО `pytest` + `pytest-asyncio` (один async-плагин). Любые дополнительные тестовые библиотеки, плагины или раннеры — только по отдельному согласованию.
- Frontend: допускается один test runner (Vitest или аналог). Дополнительные плагины — только по согласованию.

**Выход за scope:**
- Изменение любого production-файла ради "тестируемости"
- Добавление mock-фреймворков, которые требуют изменения production-кода
- Рефакторинг зависимостей для инъекции в тестах
- Изменение структуры проекта
- Создание DB fixture, test database, async session factory (это deliverable БУДУЩИХ уровней)
- Импорт/чтение production моделей (`app/models/*`) в тестовых fixtures
- Тестирование CRUD-функций, использование `Base.metadata.create_all`
- Добавление тестовых библиотек/плагинов сверх разрешённых в Dev deps policy

**Stop Conditions — остановиться и вернуться к анализу если:**
- Smoke-тест `from app.main import app` требует изменений в `config.py` или `main.py`
- Test runner требует изменений в конфигурации приложения
- Обнаружены circular imports при попытке импорта `app.main`
- `from app.main import app` инициирует реальное I/O (подключение к DB/Redis) — smoke-тест не должен требовать поднятой инфраструктуры
- Frontend test runner не запускается без изменений в `tsconfig.json` или `next.config.mjs`

**Команды проверки:**
```
cd backend && python -m pytest --co       → тест-файлы обнаруживаются
cd backend && python -m pytest            → exit code 0
cd frontend && npm test                   → exit code 0 (passWithNoTests допустим)
npm run build                             → exit code 0 (regression guard)
git diff --name-only                      → ТОЛЬКО: tests/, pyproject.toml, package.json,
                                             vitest.config.ts, __tests__/
```

---

### УРОВЕНЬ S1: БЕЗОПАСНОСТЬ (C3, L3, M7, M8)

**Устраняемые риски:** C3, L3, M7, M8.

**C3 — Утечка str(exc) в exception handlers**

**Разрешено изменять:**
- `backend/app/main.py` — ТОЛЬКО exception handler функции (строки 271-382)

**Read-only:**
- `backend/app/errors.py` — структура ошибок не меняется
- Все роутеры, use_cases, CRUD — они генерируют исключения, не обрабатывают
- Frontend — он потребляет error response, его менять не нужно

**Выход за scope:**
- Изменение формата `error_payload()` в `errors.py`
- Добавление нового middleware для error handling
- Изменение status_code или error code маппинга
- Изменение логирования (формат, уровни)

**Stop Conditions:**
- Обнаружено, что `error_payload()` в `errors.py` сама формирует details с `str(exc)` — тогда нужно менять `errors.py` (Critical Core), вернуться к анализу
- Обнаружены exception handlers вне `main.py` (в роутерах, middleware), которые тоже утекают данные — расширение scope

---

**L3 — Валидация SECRET_KEY length**

**Разрешено изменять:**
- `backend/app/config.py` — ТОЛЬКО метод `from_env()`, секция валидации secret_key

**Read-only:**
- Всё остальное — config.py уже Critical Core

**Выход за scope:**
- Изменение типа поля `secret_key` в Settings-модели
- Добавление новых полей в Settings
- Изменение `_SettingsProxy` или `get_settings()`

**Stop Conditions:**
- Изменение валидации ломает инициализацию — текущий SECRET_KEY в `.env` не проходит новую валидацию

---

**M7 — Проверка user.is_active**

**Разрешено изменять:**
- `backend/app/dependencies.py` — ТОЛЬКО функция `get_current_user()` (строки 73-130)

**Read-only:**
- `backend/app/models/user.py` — модель User не меняется
- Все роутеры — они получают user через Depends, не меняются
- Frontend — он получает 401/403, обработка уже есть

**Выход за scope:**
- Изменение `get_current_user_optional()`
- Добавление нового middleware для проверки is_active
- Изменение модели User

**Stop Conditions:**
- Обнаружено, что `is_active` не имеет default в модели или миграции — нужно сначала проверить миграцию
- Обнаружены другие dependency-функции, которые тоже должны проверять is_active — расширение scope

---

**M8 — Legacy fallback в verify_password**

**Разрешено изменять:**
- `backend/app/utils/security.py` — ТОЛЬКО функция `verify_password()` (строки 39-49)

**Read-only:**
- `hash_password()` — механизм хеширования не меняется
- Все use_cases, которые вызывают verify_password
- `backend/app/use_cases/auth/login_user.py` — вызывает verify_password

**Выход за scope:**
- Изменение `hash_password()` или `_normalize_password()`
- Миграция существующих хешей в БД
- Добавление новых схем хеширования

**Stop Conditions:**
- Обнаружено, что в БД существуют хеши, созданные БЕЗ SHA256-нормализации (legacy-пароли) — удаление fallback сломает вход этих пользователей. Необходим анализ данных перед изменением.
- Невозможно определить, какие пароли в БД были созданы по какой схеме — требуется data audit

---

### УРОВЕНЬ S2: DATA INTEGRITY (C1, H1)

**Устраняемые риски:** C1, H1.

**C1 — Race condition в refresh token rotation**

**Разрешено изменять:**
- `backend/app/crud/refresh_token.py` — ТОЛЬКО функция `create_or_rotate_refresh_token()` (строки 11-33)

**Read-only:**
- `backend/app/use_cases/auth/refresh_session.py` — вызывающий код, не меняется
- `backend/app/use_cases/auth/register_user.py` — тоже вызывает issue_tokens→create_or_rotate
- `backend/app/dependencies.py` — проверяет token, не ротирует
- `backend/app/models/refresh_token.py` — модель не меняется
- Frontend auth flow — клиент не меняется

**Выход за scope:**
- Изменение схемы таблицы refresh_tokens
- Добавление новых полей в RefreshToken модель
- Изменение API-контракта `/auth/refresh`
- Переход на другую стратегию ротации (например, token families)

**Stop Conditions:**
- Тест на concurrency показывает, что race condition не в `create_or_rotate`, а в `_validate_and_issue_tokens` (вся цепочка) — scope шире, чем одна функция
- `UNIQUE(user_id)` constraint на таблице refresh_tokens означает, что INSERT-ветка create_or_rotate невозможна при существующем пользователе — нужно пересмотреть логику целиком
- FOR UPDATE создаёт deadlock с другим запросом в той же транзакции — нужно пересмотреть transaction boundaries

---

**H1 — Фильтрация soft-deleted и draft записей**

**Разрешено изменять:**
- `backend/app/crud/anime.py` — ТОЛЬКО существующие query-функции (get_anime_list, search_anime, get_anime_by_id)

**Read-only:**
- `backend/app/models/anime.py` — модель Anime не меняется
- `backend/app/routers/anime.py` — роутер вызывает CRUD, не меняется
- `backend/app/crud/anime_admin.py` — admin CRUD может требовать доступ к deleted/draft, не трогать
- Frontend — получает отфильтрованные данные, не меняется

**Выход за scope:**
- Добавление soft-delete middleware или автоматического фильтра на уровне ORM
- Изменение модели Anime
- Добавление новых query-функций
- Изменение admin CRUD (admin может нуждаться в доступе к deleted/draft)

**Stop Conditions:**
- В БД нет записей со state != 'draft' — все записи draft, фильтр уберёт весь контент. Нужно понять какой state является "published"
- `crud/anime_admin.py` переиспользует те же функции из `crud/anime.py` — фильтрация сломает admin
- Parser publish_service записывает anime с определённым state — нужно знать какой, прежде чем фильтровать
- Обнаружено, что `api/internal/` endpoints используют другие CRUD-функции — scope шире

---

### УРОВЕНЬ S3: CONTRACT (C2)

**Устраняемый риск:** C2 — runtime crash в маппере.
M4 закрыт на этапе аудита (backend schema не отдаёт poster_url).

**C2 — Семантическое расхождение status ↔ type**

**Разрешено изменять:**
- `frontend/mappers/anime.mapper.ts` — ТОЛЬКО функция `mapStatusToType()` и маппинг-функции, которые её вызывают

**Read-only:**
- `backend/app/models/anime.py` — backend schema не меняется
- `backend/app/crud/anime.py` — backend queries не меняются
- `frontend/types/anime.ts` — доменные типы не меняются (22 importers)
- Все компоненты, использующие `IAnime`, `SpotlightAnime`, `TopUpcomingAnime`

**Выход за scope:**
- Добавление нового поля в Backend Anime модель (например, `media_type`)
- Изменение `frontend/types/anime.ts` — доменные типы (каскад на 22 файла)
- Изменение backend API response формата
- Изменение Pydantic schemas в backend

**Stop Conditions:**
- Backend `Anime.status` не содержит значений, которые можно маппить в media type (TV/ONA/MOVIE). Status хранит ТОЛЬКО трансляционный статус → маппинг в type принципиально невозможен из текущих данных. Нужен анализ: откуда должен приходить media type
- Backend НЕ ИМЕЕТ поля для media type → нужно решение уровня data model, что выходит за scope этого уровня
- Proxy API отдаёт media type в другом формате → два маппинга нужны, один для internal, другой для proxy

---

**M4 — Маппинг poster_url/description**

**Разрешено изменять:**
- `frontend/mappers/anime.mapper.ts` — маппинг-функции (добавление маппинга новых полей из BackendAnime)
- `frontend/mappers/anime.mapper.ts` — тип `BackendAnime` (internal, не экспортируется)

**Read-only:**
- `frontend/types/anime.ts` — IAnime interface не меняется (если poster/description уже есть в типе)
- Backend — ничего не меняется
- Компоненты — не меняются

**Выход за scope:**
- Изменение IAnime interface (каскад на 22 файла)
- Добавление новых полей в backend response
- Изменение компонентов для отображения новых данных

**Stop Conditions:**
- `IAnime.poster` имеет тип `string`, а backend `poster_url` может быть `null` — типы несовместимы без изменения IAnime (каскад)
- Backend реально не отдаёт `poster_url` в response (Pydantic schema может не включать это поле) — нужно проверить schema
- Компоненты используют `poster` как URL напрямую в `<img src>` — placeholder vs real URL может потребовать изменений в компонентах

---

### УРОВЕНЬ S4: FRONTEND AUTH STATE (H5)

**H5 — Сброс authFailureCommitted**

**Разрешено изменять:**
- `frontend/lib/auth-errors.ts` — ТОЛЬКО функции `handleAuthFailure()` и `getAuthFailureState()`

**Read-only:**
- `frontend/lib/api.ts` — interceptor не меняется
- `frontend/store/auth-store.tsx` — store не меняется (20 importers)
- `frontend/package.json` — зависимости не меняются (React Query upgrade — Post-Stabilization)
- Все компоненты и pages

**Выход за scope:**
- Изменение auth interceptor в `api.ts`
- Изменение auth store structure
- Добавление нового middleware или provider для auth state
- React Query upgrade (Post-Stabilization P1)

**Stop Conditions:**
- `authFailureCommitted` используется не только в `auth-errors.ts` — нужно проверить все usages
- Сброс флага требует знания момента "re-login" — если re-login не имеет явного события, которое можно перехватить, подход не работает
- Обнаружено, что `setAuth()` в store не вызывает side-effects — нет hook point для сброса

---

### УРОВЕНЬ S5: PERFORMANCE (H2, H3, H4)

**Устраняемые риски:** H2, H3, H4.

**H2 — Оптимизация auth DB queries**

**Разрешено изменять:**
- `backend/app/dependencies.py` — ТОЛЬКО `get_current_user()` (строки 73-130)
- `backend/app/crud/refresh_token.py` — ТОЛЬКО read-функции (get_by_hash, get_by_user_id)

**Read-only:**
- `backend/app/models/` — модели не меняются
- `backend/app/database.py` — engine/session не меняется
- Все роутеры — они не знают о внутренней реализации auth check

**Выход за scope:**
- Добавление Redis-кеширования для auth
- Изменение token-модели или user-модели
- Изменение JWT payload structure
- Добавление middleware для auth

**Stop Conditions:**
- Объединение двух запросов в один JOIN невозможно из-за разных session lifecycles (user query и token query через разные ports) — нужна restructuring dependencies
- Оптимизация требует изменения port interface (RefreshTokenPort) — каскад на все реализации

---

**H3 — Trigram index для ILIKE**

**Разрешено изменять:**
- Создание новой Alembic-миграции (новый файл в `backend/alembic/versions/`)

**Read-only:**
- `backend/app/crud/anime.py` — query-код не меняется (ILIKE использует index автоматически)
- `backend/app/models/anime.py` — модель не меняется
- Все остальные файлы

**Выход за scope:**
- Изменение search query logic
- Добавление full-text search
- Изменение API поисковых endpoints

**Stop Conditions:**
- PostgreSQL версия в Docker не поддерживает pg_trgm extension — нужно обновить image
- Extension `pg_trgm` требует superuser для CREATE EXTENSION — Alembic user не имеет прав

---

**H4 — Pool sizing**

**Разрешено изменять:**
- `backend/app/config.py` — ТОЛЬКО default-значения `db_pool_size` и `db_max_overflow`
- `.env.example` — документирование рекомендованных значений

**Read-only:**
- `backend/app/database.py` — engine creation logic не меняется
- Все остальные файлы

**Выход за scope:**
- Изменение pooling strategy (например, pgbouncer)
- Изменение session management
- Добавление connection monitoring

**Stop Conditions:**
- Нет — это изолированное изменение конфигурации

---

### МАТРИЦА КРИТИЧНОСТИ МОДУЛЕЙ (Stabilization S0–S5)

```
Модуль                        | S0  | S1  | S2  | S3  | S4  | S5  |
------------------------------|-----|-----|-----|-----|-----|-----|
backend/app/config.py         | RO  | W*  | RO  | RO  | RO  | W*  |
backend/app/database.py       | RO  | RO  | RO  | RO  | RO  | RO  |
backend/app/errors.py         | RO  | RO  | RO  | RO  | RO  | RO  |
backend/app/dependencies.py   | RO  | W*  | RO  | RO  | RO  | W*  |
backend/app/main.py           | RO  | W*  | RO  | RO  | RO  | RO  |
backend/app/crud/refresh_t.py | RO  | RO  | W*  | RO  | RO  | W*  |
backend/app/crud/anime.py     | RO  | RO  | W*  | RO  | RO  | RO  |
backend/app/models/*.py       | RO  | RO  | RO  | RO  | RO  | RO  |
backend/app/utils/security.py | RO  | W*  | RO  | RO  | RO  | RO  |
backend/alembic/versions/     | RO  | RO  | RO  | RO  | RO  | W+  |
frontend/lib/api.ts           | RO  | RO  | RO  | RO  | RO  | RO  |
frontend/lib/auth-errors.ts   | RO  | RO  | RO  | RO  | W*  | RO  |
frontend/store/auth-store.tsx  | RO  | RO  | RO  | RO  | RO  | RO  |
frontend/mappers/anime.map.ts | RO  | RO  | RO  | W*  | RO  | RO  |
frontend/types/anime.ts       | RO  | RO  | RO  | RO  | RO  | RO  |
frontend/query/*.ts           | RO  | RO  | RO  | RO  | RO  | RO  |
frontend/components/player/   | RO  | RO  | RO  | RO  | RO  | RO  |
frontend/app/*/page.tsx       | RO  | RO  | RO  | RO  | RO  | RO  |
frontend/package.json         | W+  | RO  | RO  | RO  | RO  | RO  |
backend/pyproject.toml        | W+  | RO  | RO  | RO  | RO  | RO  |

RO  = Read-Only в этой фазе
W*  = Writable, ограниченный scope (конкретные функции)
W+  = Writable, новый контент (новые файлы, новые зависимости)
```

**Правило разграничения:** Любое изменение, не адресующее конкретную запись Risk Register (C1–C4, H1–H6, M3–M8, L2–L4), автоматически классифицируется как Post-Stabilization и не входит в матрицу.

---

### ГЛОБАЛЬНЫЕ STOP CONDITIONS (применимы к любому уровню)

1. **Circular dependency detected** — изменение модуля A требует изменения модуля B, который должен быть RO на этом уровне → вернуться к анализу dependency order
2. **Cascade beyond scope** — изменение затрагивает > 3 файлов, не указанных в "Разрешено изменять" → вернуться к анализу
3. **Test infrastructure broken** — после Уровня 0, если тесты перестают проходить на любом последующем уровне → остановить текущий уровень, починить тесты
4. **Data state unknown** — изменение зависит от содержимого БД (какие значения status существуют, какие пароли по какой схеме хешированы), а данные не проверены → data audit перед продолжением
5. **Contract break** — изменение backend API response формата или frontend request формата → координация frontend+backend, не одностороннее изменение
6. **Model migration required** — изменение требует новой колонки/индекса/constraint в модели → отдельная единица работы с миграцией

---

## ЧАСТЬ VII: LEVEL COMPLETION CRITERIA

### Разделение: Stabilization vs Architecture Evolution

Каждый элемент проверен по критерию: **устраняет ли он конкретный риск из Risk Register (падение, потеря данных, утечка, деградация под нагрузкой) — или улучшает архитектуру/maintainability?**

| ID | Описание | Риск из RR | Классификация | Обоснование |
|----|----------|------------|---------------|-------------|
| C4 | Тестовая инфраструктура | CRITICAL: нет safety net | **STABILIZATION** | Блокирует верификацию всех fixes |
| C3 | Info leak в exception handlers | CRITICAL: утечка SQL/traces | **STABILIZATION** | Устраняет уязвимость безопасности |
| L3 | SECRET_KEY validation | LOW: слабый ключ | **STABILIZATION** | Устраняет конфигурационный риск |
| M7 | user.is_active check | MEDIUM: доступ деактивированных | **STABILIZATION** | Устраняет дыру в авторизации |
| M8 | Password fallback | MEDIUM: обход нормализации | **STABILIZATION** | Устраняет legacy security path |
| C1 | Race condition в token rotation | CRITICAL: потеря сессий | **STABILIZATION** | Устраняет data corruption |
| H1 | Soft-delete/state не фильтруется | HIGH: deleted данные видны | **STABILIZATION** | Устраняет утечку данных |
| C2 | Mapper crash (status≠type) | CRITICAL: runtime throw | **STABILIZATION** | Устраняет runtime crash |
| M4 | poster_url/description не маппится | MEDIUM: placeholder | **STABILIZATION** (closed) | Закрыт: backend schema не отдаёт поля, mapper корректен |
| H5 | authFailureCommitted не сбрасывается | HIGH: broken re-login | **STABILIZATION** | Устраняет сломанный auth cycle |
| H2 | 2 DB query на auth request | HIGH: DB bottleneck | **STABILIZATION** | Устраняет конкретный bottleneck |
| H3 | ILIKE без trigram index | HIGH: full table scan | **STABILIZATION** | Устраняет конкретную деградацию |
| H4 | Pool size 5+10 | HIGH: exhaustion при ~7 users | **STABILIZATION** | Устраняет конкретный лимит |
| M1 | React Query v3→v5 | MEDIUM: EOL библиотека | **ARCHITECTURE** | Смена библиотеки, v3 работает, не падает |
| M2 | SSR/SSG | MEDIUM: нет SEO | **ARCHITECTURE** | Новая rendering модель |
| M5 | Endpoint consolidation | MEDIUM: дублирование | **ARCHITECTURE** | Рефакторинг структуры API |
| M9 | PlayerShell decomposition | MEDIUM: монолитный компонент | **ARCHITECTURE** | Рефакторинг для maintainability |

---

## STABILIZATION PHASE (Уровни S0–S5)

Цель: устранение конкретных рисков из Risk Register.
Граница: после S5 система стабильна для текущей и прогнозируемой нагрузки.

---

### УРОВЕНЬ S0: ТЕСТОВАЯ ИНФРАСТРУКТУРА (C4)

**Устраняемый риск:** C4 — нулевое покрытие тестами, невозможность верификации любых изменений.

**Completion Criteria:**
1. `pytest` запускается из корня backend без ошибок импорта и возвращает exit code 0
2. Существует `backend/tests/conftest.py` с минимальным набором env var overrides для `Settings.from_env()`. DATABASE_URL/REDIS_URL задаются только для прохождения валидации — smoke-тест не требует поднятого Postgres/Redis
3. Как минимум один smoke-тест проходит: `from app.main import app` → `isinstance(app, FastAPI)` без I/O (без обращения к БД и Redis)
4. На frontend: test runner запускается через `npm test` без ошибок конфигурации
5. `npm run build` → exit code 0 (regression)

**Non-goals:**
- Написание тестов для бизнес-логики — задача последующих уровней
- Достижение какого-либо % покрытия
- Тестирование frontend компонентов (render tests)
- Создание DB fixture, async session, test database — задача последующих уровней
- Интеграционные тесты с реальной PostgreSQL
- CI/CD pipeline
- Импорт/использование production-моделей (`app/models/*`) в fixtures
- Добавление тестовых библиотек/плагинов сверх: pytest + pytest-asyncio (backend), один runner (frontend)

**Regression Guard:**
- `npm run build` → exit code 0
- Никакие production-файлы не изменены
- `git diff --name-only` → только `tests/`, `pyproject.toml`, `package.json`, `vitest.config.ts`, `__tests__/`

**Exit Check:**
```
1. cd backend && python -m pytest --co       → тест-файлы обнаруживаются
2. cd backend && python -m pytest            → exit code 0
3. cd frontend && npm test                   → exit code 0 (passWithNoTests допустим)
4. cd frontend && npm run build              → exit code 0
5. git diff --name-only                      → только tests/, pyproject.toml, package.json,
                                                vitest.config.ts, __tests__/
```

---

### УРОВЕНЬ S1: БЕЗОПАСНОСТЬ (C3, L3, M7, M8)

**Устраняемые риски:**
- C3 — утечка SQL/stack traces клиенту
- L3 — слабый SECRET_KEY при неверной конфигурации
- M7 — деактивированные пользователи сохраняют доступ
- M8 — legacy fallback обходит SHA256-нормализацию

**Completion Criteria:**

*C3 — Info leak:*
1. Ни один exception handler в `main.py` не передаёт `str(exc)` в `details` ответа клиенту
2. Обработчики `IntegrityError`, `ProgrammingError`, `NoResultFound`, `MultipleResultsFound`, `Exception` возвращают generic-сообщение в `details` (или `details=None`)
3. `str(exc)` остаётся в server-side логах

*L3 — SECRET_KEY:*
4. `Settings.from_env()` отвергает SECRET_KEY короче 32 символов с ValueError

*M7 — is_active:*
5. `get_current_user()` возвращает HTTP 403 если `user.is_active == False`

*M8 — Password fallback:*
6. `verify_password()` не содержит fallback-ветки с прямым bcrypt без SHA256

**Non-goals:**
- Миграция legacy-паролей в БД
- Rate limiting на новые endpoints
- Аудит CORS
- HTTPS enforcement
- Изменение JWT algorithm или token structure
- Изменение `error_payload()` в `errors.py`

**Regression Guard:**
- Все тесты S0 проходят
- Приложение стартует без ошибок
- `POST /auth/login` с валидными credentials → 200
- `POST /auth/login` с невалидными credentials → 401
- `GET /health` → 200

**Exit Check:**
```
1. grep -n "str(exc)" backend/app/main.py    → ТОЛЬКО в _log_error(), НЕ в JSONResponse
2. Тест: IntegrityError → response.details НЕ содержит SQL
3. Тест: SECRET_KEY="short" → ValueError
4. Тест: user.is_active=False → HTTP 403
5. Тест: verify_password → только normalized path
6. cd backend && python -m pytest             → exit code 0
```

---

### УРОВЕНЬ S2: DATA INTEGRITY (C1, H1)

**Устраняемые риски:**
- C1 — concurrent refresh инвалидирует токены (потеря сессий)
- H1 — soft-deleted и draft записи видны пользователям

**Completion Criteria:**

*C1 — Race condition:*
1. `create_or_rotate_refresh_token()` выполняет SELECT с FOR UPDATE перед UPDATE/INSERT
2. Существует тест на concurrent вызовы для одного `user_id`

*H1 — Soft-delete filter:*
3. `get_anime_list()` — только `is_deleted == False`
4. `search_anime()` — только `is_deleted == False`
5. `get_anime_by_id()` — возвращает `None` для `is_deleted == True`
6. Фильтрация по `state` определена после data audit
7. Тесты для пунктов 3-5

**Non-goals:**
- Автоматический soft-delete на уровне ORM
- Изменение admin CRUD
- Изменение API response schema
- Другая стратегия ротации токенов
- Добавление индексов (это S5)

**Regression Guard:**
- Все тесты S0-S1 проходят
- `POST /auth/refresh` → 200 + новые токены
- `GET /anime/` → 200 + список
- `GET /anime/{id}` → 200 для published anime
- Admin endpoints не затронуты

**Exit Check:**
```
1. grep -n "for_update\|with_for_update" backend/app/crud/refresh_token.py → в create_or_rotate
2. grep -n "is_deleted" backend/app/crud/anime.py → в get_anime_list, search_anime, get_anime_by_id
3. cd backend && python -m pytest tests/test_refresh_token.py → exit code 0
4. cd backend && python -m pytest tests/test_anime_crud.py    → exit code 0
5. cd backend && python -m pytest                              → exit code 0
```

---

### УРОВЕНЬ S3: CONTRACT (C2)

**Устраняемый риск:** C2 — runtime crash при маппинге anime (SpotlightAnime/TopUpcomingAnime throw Error для всех реальных значений status).

**Примечание:** M4 (poster_url/description) закрыт на этапе аудита. Backend schemas `AnimeRead` и `AnimeListItem` не содержат `poster_url`. Маппер корректно использует placeholder. Проблема существует в backend schema, что выходит за scope стабилизации (это расширение API, не fix).

**Completion Criteria:**
1. `mapStatusToType()` не выбрасывает Error для значений status из backend БД
2. `mapBackendAnimeToSpotlightAnime()` не throw при отсутствии mappable status
3. `mapBackendAnimeToTopUpcomingAnime()` — аналогично
4. Документировано (комментарий в коде) какие значения `Anime.status` backend использует

**Non-goals:**
- Изменение backend Pydantic schemas
- Изменение backend Anime model
- Добавление `media_type` в backend
- Изменение `frontend/types/anime.ts` (22 importers)
- Изменение компонентов
- Расширение backend API (добавление poster_url в schema) — это architecture evolution

**Regression Guard:**
- Все тесты S0-S2 проходят
- `GET /anime/` → response парсится frontend без Error
- Hero-секция не падает
- Search работает без Error
- Backend response format не изменён

**Exit Check:**
```
1. cd frontend && npm run build               → exit code 0
2. mapStatusToType("ongoing")                 → не throw
3. mapBackendAnimeToSpotlightAnime(status=null) → не throw
4. cd backend && python -m pytest             → exit code 0
5. Ручная проверка: главная страница рендерится без crash
```

---

### УРОВЕНЬ S4: FRONTEND AUTH STATE (H5)

**Устраняемый риск:** H5 — `authFailureCommitted` не сбрасывается, повторный auth failure после re-login не обрабатывается (logout не происходит).

**Completion Criteria:**
1. После `clearAuth()` + `setAuth()` (re-login), `authFailureCommitted` сброшен в `false`
2. Повторный auth failure после re-login вызывает `handleAuthFailure()` (logout)
3. Существует тест: login → auth failure → logout → login → auth failure → logout (оба logout срабатывают)

**Non-goals:**
- Изменение auth interceptor в `api.ts`
- Изменение auth store structure
- React Query upgrade (Post-Stabilization)
- Изменение компонентов

**Regression Guard:**
- Все тесты S0-S3 проходят
- `npm run build` → exit code 0
- Auth flow: login → navigate → refresh → auth сохранён
- Все страницы загружаются

**Exit Check:**
```
1. grep -rn "authFailureCommitted = true" frontend/lib/auth-errors.ts → присутствует
2. grep -rn "authFailureCommitted = false\|authFailureCommitted: false" frontend/ → присутствует (сброс)
3. cd frontend && npm run build              → exit code 0
4. cd backend && python -m pytest            → exit code 0
```

---

### УРОВЕНЬ S5: PERFORMANCE (H2, H3, H4)

**Устраняемые риски:**
- H2 — 2 DB-запроса на каждый authenticated request → DB bottleneck
- H3 — ILIKE full table scan → деградация поиска при росте каталога
- H4 — pool 5+10 → exhaustion при ~7 concurrent users

**Completion Criteria:**

*H2 — Auth queries:*
1. `get_current_user()` оптимизирован (1 query или другой демонстрируемый способ)
2. **ИЛИ** зафиксировано как architectural limitation (port interface не позволяет JOIN), не блокирует уровень

*H3 — Trigram index:*
3. Alembic-миграция создаёт pg_trgm GIN-индекс на `anime.title`
4. `EXPLAIN ANALYZE ... ILIKE ...` → Index Scan

*H4 — Pool sizing:*
5. Default `db_pool_size` >= 10, `db_max_overflow` >= 20
6. `.env.example` документирует значения

**Non-goals:**
- Redis-кеширование auth
- pgbouncer
- Connection monitoring
- Full-text search
- Изменение port interfaces

**Regression Guard:**
- Все тесты S0-S4 проходят
- `POST /auth/login` → 200
- `POST /auth/refresh` → 200
- `GET /anime/` → 200
- Search → 200
- `alembic upgrade head` → ok
- `alembic downgrade -1` → ok

**Exit Check:**
```
1. alembic upgrade head                      → exit code 0
2. EXPLAIN ANALYZE ... ILIKE ...             → "Index Scan"
3. grep "db_pool_size" backend/app/config.py → default >= 10
4. cd backend && python -m pytest            → exit code 0
5. cd frontend && npm run build              → exit code 0
```

---

### STABILIZATION COMPLETE GATE

После S5 стабилизация завершена. Перед переходом к Post-Stabilization:

```
ОБЯЗАТЕЛЬНО:
1. cd backend && python -m pytest            → exit code 0 (все тесты)
2. cd frontend && npm run build              → exit code 0
3. docker-compose up --build                 → приложение стартует
4. Ручная верификация critical paths:
   - Auth: register → login → refresh → logout
   - Anime: list → detail → search
   - Player: episode select → playback → progress
   - Admin: pages load

РЕЗУЛЬТАТ:
- Все CRITICAL risks (C1-C4) устранены
- Все HIGH risks (H1-H6) устранены или зафиксированы с escape hatch (H2, H6)
- Security holes (C3, L3, M7, M8) закрыты
- Система выдерживает >7 concurrent users без pool exhaustion
- Поиск использует индекс
- Frontend не падает на реальных данных
```

---

## POST-STABILIZATION PHASE (Architecture Evolution)

Цель: улучшение архитектуры и maintainability.
Предусловие: Stabilization Phase завершена, Stabilization Complete Gate пройден.
Характер: **не устраняет риски падения/потери данных**, улучшает developer experience, SEO, код-базу.

### P1: React Query v3 → v5 (M1)

**Обоснование отнесения к Post-Stabilization:**
React Query v3 работает. Не вызывает runtime crashes, не теряет данные, не создаёт security holes. Это EOL-библиотека (M1 severity MEDIUM), что означает отсутствие security patches, но не немедленный risk. Upgrade — это миграция API 9+ query hooks + mutation hooks + provider config. Это **library migration**, не **bug fix**.

**Scope:** `frontend/package.json`, `frontend/providers/query-provider.tsx`, `frontend/query/*.ts`, `frontend/mutation/*.ts`

**Completion Criteria:**
1. `@tanstack/react-query` вместо `react-query` в `package.json`
2. Все query/mutation hooks используют v5 API
3. `npm run build` → exit code 0
4. Все страницы загружаются без error

---

### P2: SSR/SSG (M2)

**Обоснование отнесения к Post-Stabilization:**
Отсутствие SSR — это архитектурное решение (все страницы `"use client"`). Не вызывает crashes, не теряет данные. Влияет на SEO и FCP. Это **новая rendering модель**, не fix.

**Scope:** `frontend/app/*/page.tsx`, `frontend/app/*/layout.tsx`, `frontend/providers/`

**Precondition:** P1 (React Query v5) завершён — v3 не поддерживает SSR hydration.

---

### P3: Endpoint consolidation (M5)

**Обоснование отнесения к Post-Stabilization:**
Дублирование endpoints (routers/ vs api/internal/) — архитектурное несоответствие. Оба набора работают. Не создаёт runtime errors. Это **рефакторинг API structure**, не fix.

**Scope:** `backend/app/routers/`, `backend/app/api/internal/`, `backend/app/main.py` (router registration)

**Precondition:** Frontend URLs и backend routes стабилизированы.

---

### P4: PlayerShell decomposition (M9)

**Обоснование отнесения к Post-Stabilization:**
~660 строк в одном компоненте — проблема maintainability. Компонент работает. Не падает. Это **рефакторинг для читаемости**, не fix.

**Scope:** `frontend/components/player/PlayerShell.tsx`, новые файлы в `frontend/components/player/`

---

### CROSS-LEVEL INVARIANT (для обеих фаз)

После каждого уровня, перед переходом к следующему:

```
ОБЯЗАТЕЛЬНО:
1. cd backend && python -m pytest         → exit code 0
2. cd frontend && npm run build           → exit code 0
3. git diff --stat                        → изменены только файлы из "Разрешено изменять"
4. docker-compose up --build              → приложение стартует

ПРИ НАРУШЕНИИ:
- Пункт 1 или 2 нарушен → исправить до перехода
- Пункт 3 нарушен → оценить выход за scope, вернуться к Execution Constraints
- Пункт 4 нарушен → regression, остановка
```

---

## ЧАСТЬ I: AUDIT FINDINGS (Полный аудит)

### КОНТЕКСТ

Kitsu — full-stack приложение для стриминга аниме.
**Backend:** FastAPI + SQLAlchemy (async) + PostgreSQL + Redis
**Frontend:** Next.js 15 + React 18 + TypeScript + Zustand + React Query
**Инфраструктура:** Docker Compose, Alembic миграции, Redis для координации

Аудит проведён на основе чтения исходного кода. Каждый вывод подкреплён ссылкой на файл и строку.

---

### 1. ОБЩАЯ АРХИТЕКТУРА

#### 1.1 Структура системы

**Backend** организован в слои: `routers` → `use_cases` → `crud` → `models`, с дополнительным `domain/ports` слоем (Protocol-based интерфейсы). Есть отдельный подсистемный модуль `parser/` со своими domain, ports, repositories, services, jobs.

**Frontend** построен на Next.js App Router, но все страницы используют `"use client"` — фактически это SPA с Next.js в роли dev-сервера и билд-системы, без серверного рендеринга.

#### 1.2 Точки входа

- Backend: `backend/app/main.py` → FastAPI app с lifespan-менеджером
- Frontend: `frontend/app/layout.tsx` → root layout с провайдерами (Query, Store, Theme)

#### 1.3 Поток данных

```
Browser → Next.js (client) → Axios → FastAPI Router → Use Case → CRUD → PostgreSQL
                                                          ↕
                                                        Redis (rate limits, locks)
```

#### 1.4 Двойственность данных

Система получает аниме-данные из **двух источников**:
1. Собственная БД (CRUD через internal API: `/anime`, `/favorites`, `/watch`)
2. Внешний парсер + proxy-слой (`/api/proxy/*`) — HTML-скрейпинг внешнего сайта

Frontend использует **разные маппинг-цепочки** для каждого источника — два параллельных потока данных с разными типами и контрактами.

---

### 2. BACKEND AUDIT

#### 2.1 Структура API

Роутеры разделены на три группы:
- **Пользовательские:** `auth`, `anime`, `releases`, `episodes`, `favorites`, `watch`
- **Admin:** `admin/router.py`, `parser/admin/router.py`
- **API layer:** `api/router.py` с подгруппами `internal/`, `admin/`, `proxy/`

**Факт:** Существуют два набора endpoints для favorites и watch — в `routers/` и в `api/internal/`. Неоднозначность каноничного API.

#### 2.2 Бизнес-логика

Слой `use_cases/` существует только для auth-потока (register, login, refresh, logout). Для anime, favorites, watch — роутеры напрямую вызывают CRUD-функции, минуя use case слой.

#### 2.3 Модели данных

Модель `Anime` (`backend/app/models/anime.py`) содержит 25+ колонок: контент-данные, state machine (строковое поле без DB enum), ownership (4 FK на users), lock mechanism, soft delete.

**Факт:** `get_anime_list` и `search_anime` (`backend/app/crud/anime.py:9-19, 26-36`) не фильтруют по `is_deleted` или `state`. Soft-deleted и draft записи возвращаются клиенту.

#### 2.4 Race condition в refresh token

`create_or_rotate_refresh_token` (`backend/app/crud/refresh_token.py:14-16`) выполняет SELECT без FOR UPDATE, затем UPDATE/INSERT. TOCTOU-окно: конкурентные refresh-запросы инвалидируют токены друг друга.

В `refresh_session.py:23` — `get_by_hash(for_update=True)`, но затем `issue_tokens` вызывает `create_or_rotate` без блокировки.

#### 2.5 Admin endpoints

`backend/app/admin/router.py` — GET endpoints возвращают mock-данные. Write endpoints — стабы с TODO и fire-and-forget audit logging через `asyncio.create_task()`.

#### 2.6 Search без экранирования LIKE-спецсимволов

`backend/app/crud/anime.py:27` — `f"%{query}%"` подставляется без экранирования `%` и `_`. Не SQL injection, но позволяет манипуляцию паттерном.

---

### 3. FRONTEND AUDIT

#### 3.1 Все страницы — client-side only

Все `page.tsx` используют `"use client"`. Нет SSR/SSG. Нет SEO для динамического контента.

#### 3.2 React Query v3

`frontend/package.json` — `react-query: ^3.39.3`. EOL-версия, несовместима с App Router и Server Components.

#### 3.3 Маппинг status ↔ type

`frontend/mappers/anime.mapper.ts:55-72` — `mapStatusToType` интерпретирует `status` как media type (TV/ONA/MOVIE). Backend хранит в `status` трансляционный статус (ongoing/completed). Маппер вернёт `undefined` для всех реальных значений. Для `SpotlightAnime` и `TopUpcomingAnime` (строки 155-157, 197-199) — throw Error.

#### 3.4 Backend данные не маппятся

`frontend/mappers/anime.mapper.ts:89-91` — `poster: PLACEHOLDER_POSTER`, `episodes: { sub: null, dub: null }`, `description: ""`. Поля `poster_url`, `description`, episode counts из backend игнорируются.

#### 3.5 Токены в localStorage

`frontend/store/auth-store.tsx:69-84` — accessToken и refreshToken в localStorage через Zustand persist.

#### 3.6 Auth failure state не сбрасывается

`frontend/lib/auth-errors.ts:122-124` — `authFailureCommitted = true` устанавливается при первом auth failure и **никогда не сбрасывается**. После re-login последующие auth failures игнорируются.

#### 3.7 Ghost-зависимость PocketBase

`frontend/package.json` — `pocketbase: ^0.25.2`. В `auth-store.tsx:18-19` — реликтовые поля `collectionId`, `collectionName`.

#### 3.8 API interceptor — неочевидная обработка

`frontend/lib/api.ts:143` — `return handleAuthError(error)` для ВСЕХ ошибок, не только auth. `handleAuthError` для non-auth кодов просто throw, но путь неочевиден.

---

### 4. БЕЗОПАСНОСТЬ

#### 4.1 Утечка через exception handlers

`backend/app/main.py` — обработчики `IntegrityError` (строка 332), `ProgrammingError` (строка 343), `NoResultFound` (строка 353), `MultipleResultsFound` (строка 364), `Exception` (строка 382) передают `str(exc)` в `details`. Содержит SQL, имена таблиц, constraint names, stack traces.

#### 4.2 SECRET_KEY без минимальной длины

`backend/app/config.py:30-31` — проверка только на непустоту.

#### 4.3 Fallback в verify_password

`backend/app/utils/security.py:46-49` — если bcrypt(SHA256(password)) не проходит, пробует bcrypt(password) напрямую.

#### 4.4 user.is_active не проверяется

`backend/app/dependencies.py:110` — `get_current_user` не проверяет `user.is_active`.

---

### 5. ПРОИЗВОДИТЕЛЬНОСТЬ

#### 5.1 2 DB-запроса на authenticated request

`backend/app/dependencies.py:110-128` — загрузка user + проверка refresh token.

#### 5.2 ILIKE без trigram-индекса

`backend/app/crud/anime.py:27` — full table scan при поиске.

#### 5.3 Нет eager loading

`backend/app/crud/anime.py` — запросы без `joinedload()`. N+1 при обращении к relationships. В async — `MissingGreenlet` risk.

#### 5.4 Pool size

`backend/app/config.py` — pool_size=5, max_overflow=10. Максимум 15 соединений. При 2 запросах/request — exhaustion при ~7 concurrent users.

---

## ЧАСТЬ II: RISK REGISTER

### Группировка по подсистемам

#### AUTH

| ID | Severity | Описание | Файл:строка |
|----|----------|----------|-------------|
| C1 | CRITICAL | Race condition в refresh token rotation (SELECT без FOR UPDATE) | `crud/refresh_token.py:14-16` |
| H5 | HIGH | `authFailureCommitted` не сбрасывается → logout не работает после re-login | `frontend/lib/auth-errors.ts:122-124` |
| M7 | MEDIUM | `user.is_active` не проверяется при аутентификации | `dependencies.py:110` |
| M8 | MEDIUM | `verify_password` legacy fallback обходит SHA256-нормализацию | `utils/security.py:46-49` |
| L3 | LOW | SECRET_KEY без валидации минимальной длины | `config.py:30-31` |

#### ANIME DOMAIN

| ID | Severity | Описание | Файл:строка |
|----|----------|----------|-------------|
| C2 | CRITICAL | `mapStatusToType` crash — семантическое расхождение status ↔ type | `frontend/mappers/anime.mapper.ts:55-72` |
| H1 | HIGH | Soft-deleted и draft записи возвращаются клиенту | `crud/anime.py:9-19` |
| M4 | MEDIUM | Backend данные (poster_url, description) не маппятся | `frontend/mappers/anime.mapper.ts:89-91` |
| M5 | MEDIUM | Дублирование endpoints (routers/ vs api/internal/) | Обе директории |
| L2 | LOW | State machine — строковое поле без DB-level constraint | `models/anime.py:36-38` |

#### PARSER / PROXY

| ID | Severity | Описание | Файл:строка |
|----|----------|----------|-------------|
| H6 | HIGH | HTML-скрейпинг внешнего сайта без кеширования — single point of failure | `api/proxy/` |

#### FRONTEND MAPPING / STATE

| ID | Severity | Описание | Файл:строка |
|----|----------|----------|-------------|
| M1 | MEDIUM | React Query v3 (EOL, несовместим с App Router) | `frontend/package.json` |
| M2 | MEDIUM | Все страницы "use client" — нет SSR/SSG | `frontend/app/*/page.tsx` |
| M9 | MEDIUM | PlayerShell ~660 строк — монолитный компонент | `frontend/components/player/PlayerShell.tsx` |
| L1 | LOW | Ghost-зависимость PocketBase + реликтовые поля | `frontend/package.json`, `auth-store.tsx:18-19` |

#### INFRASTRUCTURE / PERFORMANCE

| ID | Severity | Описание | Файл:строка |
|----|----------|----------|-------------|
| H2 | HIGH | 2 DB-запроса на каждый authenticated request | `dependencies.py:110-128` |
| H3 | HIGH | ILIKE без trigram-индекса → full table scan | `crud/anime.py:27` |
| H4 | HIGH | Pool size 5+10 → exhaustion при ~7 concurrent users | `config.py:19-20` |

#### SECURITY

| ID | Severity | Описание | Файл:строка |
|----|----------|----------|-------------|
| C3 | CRITICAL | Exception handlers утекают str(exc) клиенту | `main.py:327-382` |
| M3 | MEDIUM | Admin endpoints — 100% mock data за реальными RBAC-проверками | `admin/router.py` |
| M6 | MEDIUM | Fire-and-forget audit logging — ошибки теряются | `admin/router.py` |

#### CROSS-CUTTING

| ID | Severity | Описание | Файл:строка |
|----|----------|----------|-------------|
| C4 | CRITICAL | Нулевое покрытие тестами | Весь проект |
| L4 | LOW | expire_on_commit=False — stale data risk | `database.py` |

---

## ЧАСТЬ III: ROOT CAUSES

Проблемы не существуют изолированно. Ниже — корневые причины, которые порождают несколько симптомов одновременно.

### RC1: Отсутствие единого контракта данных между backend и frontend

**Порождает:** C2, M4, M5

Backend `Anime` модель имеет поля `status` (трансляционный статус) и `state` (состояние записи), но нет задокументированного API-контракта, который бы фиксировал семантику каждого поля. Frontend маппер интерпретирует `status` как media type. Backend данные (poster_url, description) не маппятся, потому что фронтенд-типы (`IAnime`) спроектированы под внешний API (proxy), а не под собственный backend.

Два набора endpoints (routers/ vs api/internal/) существуют потому, что система эволюционировала от proxy-only к hybrid-модели без синхронизации контрактов.

### RC2: Отсутствие защитного слоя (query filters) на уровне CRUD

**Порождает:** H1, H3, 5.3 (N+1)

CRUD-функции — тонкие обёртки над SQLAlchemy без бизнес-логических фильтров. Нет базового "published-only" фильтра, нет eager loading defaults, нет индексной стратегии. Каждый новый endpoint должен самостоятельно добавлять фильтры — и забывает это делать.

### RC3: Auth flow не учитывает concurrency

**Порождает:** C1, H5

Backend `create_or_rotate` не использует row-level locking. Frontend `authFailureCommitted` — одноразовый флаг без сброса. Оба — следствие проектирования auth flow для single-request scenario без учёта concurrent requests и повторных auth cycles.

### RC4: Отсутствие тестов блокирует обнаружение всех остальных проблем

**Порождает:** C4 (напрямую), усиливает все остальные

Без тестов: C1 (race condition) не обнаруживается до production, C2 (mapper crash) не обнаруживается до загрузки страницы с реальными данными, H1 (soft delete bypass) не обнаруживается до manual review.

### RC5: Exception handlers спроектированы для debug, а не для production

**Порождает:** C3

Все exception handlers используют `str(exc)` в details. Это полезно при разработке, но в production раскрывает internal structure. Нет разделения debug/production режимов в error response formatting.

---

## ЧАСТЬ IV: DEPENDENCY ORDER (порядок стабилизации)

### Принцип: нельзя стабилизировать то, что нельзя проверить.

### Stabilization Program (S0–S5)

```
S0 (ФУНДАМЕНТ — блокирует всё):
  C4: Тестовая инфраструктура

S1 (БЕЗОПАСНОСТЬ — можно делать параллельно):
  C3: Убрать утечку str(exc) из exception handlers
  L3: Валидация SECRET_KEY length
  M7: Проверка user.is_active
  M8: Убрать legacy fallback в verify_password

S2 (DATA INTEGRITY — зависит от тестов):
  C1: FOR UPDATE в create_or_rotate
  H1: Фильтрация is_deleted/state

S3 (CONTRACT — зависит от data integrity):
  C2: Устранение runtime crash в mapStatusToType
  M4: Закрыт (backend schema не отдаёт poster_url)

S4 (FRONTEND AUTH STATE — зависит от backend auth):
  H5: Сброс authFailureCommitted

S5 (PERFORMANCE — после стабилизации логики):
  H2: Оптимизация auth DB queries
  H3: Trigram index
  H4: Pool sizing
```

### Post-Stabilization (P1–P4, отделён от Stabilization)

```
P1: M1 — React Query v3→v5 (library migration)
P2: M2 — SSR/SSG (новая rendering модель)
P3: M5 — Консолидация endpoints (рефакторинг API)
P4: M9 — Декомпозиция PlayerShell (рефакторинг компонента)
```

### Блокирующие зависимости внутри Stabilization

```
C4 → C1  (нужны тесты для проверки fix race condition)
C4 → H1  (нужны тесты для проверки фильтрации)
H1 → C2  (нужно знать какие данные отдаёт backend, прежде чем фиксировать маппинг)
C1 → H5  (нужно зафиксировать backend auth flow, прежде чем чинить frontend auth state)
```

### Блокирующие зависимости Post-Stabilization

```
Stabilization Complete Gate → P1, P2, P3, P4
P1 → P2  (React Query v5 нужен для SSR hydration)
```

### Независимые (можно делать параллельно с любым уровнем S)

```
C3 (info leak) — изолированное изменение в exception handlers
L3 (secret key) — изолированное изменение в config validation
M7 (is_active) — изолированное изменение в dependencies.py
M8 (password fallback) — изолированное изменение в security.py
H6 (proxy caching) — изолированная подсистема
M6 (audit logging) — изолированное изменение
L1 (PocketBase cleanup) — изолированное удаление
L2 (state enum) — изолированная миграция
```

### Правило разграничения

**Любое изменение, которое не адресует конкретную запись Risk Register (C1–C4, H1–H6, M3–M8, L2–L4), автоматически классифицируется как Post-Stabilization.** Это правило действует даже если проблема обнаружена в ходе исполнения стабилизационного уровня.

---

## ЧАСТЬ V: ВЕРИФИКАЦИЯ АУДИТА

Как подтвердить каждый critical/high finding:

| ID | Как воспроизвести |
|----|-------------------|
| C1 | 2 параллельных POST `/auth/refresh` с одним refresh token → один запрос получит невалидный ответ |
| C2 | Создать anime с `status='ongoing'` в БД → загрузить главную → SpotlightAnime mapper throws |
| C3 | Вызвать IntegrityError (дублирующая запись) → response.details содержит SQL |
| C4 | `find . -name "*test*" -o -name "*spec*"` → 0 результатов |
| H1 | `UPDATE anime SET is_deleted=true WHERE id=...` → GET `/anime/` → запись в ответе |
| H2 | Логировать SQL queries при authenticated request → 2+ SELECT до основного запроса |
| H3 | `EXPLAIN ANALYZE SELECT * FROM anime WHERE title ILIKE '%test%'` → Seq Scan |
| H4 | 8+ concurrent authenticated requests → connection pool timeout в логах |
| H5 | Login → trigger auth failure → login again → trigger auth failure → logout не происходит |
| H6 | Изменить HTML-структуру внешнего сайта (или он станет недоступен) → proxy endpoints ломаются |
