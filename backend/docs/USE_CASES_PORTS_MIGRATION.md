# Use Cases → Ports Migration Plan (No Code)

## Current State (Fact)

| Use case file | Forbidden imports (app.crud/app.models/sqlalchemy/database) | Proposed domain port (concept) |
| --- | --- | --- |
| app/use_cases/auth/register_user.py | sqlalchemy.ext.asyncio.AsyncSession; app.crud.user; app.crud.refresh_token; app.models.user | UserRepository, TokenRepository |
| app/use_cases/auth/login_user.py | sqlalchemy.ext.asyncio.AsyncSession; app.crud.user | UserRepository, TokenRepository |
| app/use_cases/auth/refresh_session.py | sqlalchemy.ext.asyncio.AsyncSession; app.crud.refresh_token | TokenRepository |
| app/use_cases/auth/logout_user.py | sqlalchemy.ext.asyncio.AsyncSession; app.crud.refresh_token | TokenRepository |
| app/use_cases/favorites/add_favorite.py | sqlalchemy.ext.asyncio.AsyncSession; app.crud.anime; app.crud.favorite; app.database.AsyncSessionLocal | FavoriteRepository |
| app/use_cases/favorites/remove_favorite.py | sqlalchemy.ext.asyncio.AsyncSession; app.crud.favorite; app.database.AsyncSessionLocal | FavoriteRepository |
| app/use_cases/favorites/get_favorites.py | sqlalchemy.ext.asyncio.AsyncSession; app.crud.favorite; app.models.favorite | FavoriteRepository |
| app/use_cases/watch/get_continue_watching.py | sqlalchemy.ext.asyncio.AsyncSession; app.crud.watch_progress; app.models.watch_progress | WatchProgressRepository |
| app/use_cases/watch/update_progress.py | sqlalchemy.ext.asyncio.AsyncSession; app.crud.anime; app.crud.watch_progress; app.database.AsyncSessionLocal | WatchProgressRepository |

## Target Ports (Concept Only)

### UserRepository
- **Назначение:** доступ к данным пользователя для регистрации и аутентификации без прямого ORM/CRUD.
- **Методы (словами):**
  - найти пользователя по email
  - создать пользователя и вернуть сущность с id
- **Возвращаемые domain entities:** User

### TokenRepository
- **Назначение:** работа с refresh-токенами без прямого доступа к SQLAlchemy.
- **Методы (словами):**
  - создать или ротировать refresh-токен для пользователя
  - получить refresh-токен по хэшу
  - отозвать refresh-токен (по хэшу или id)
- **Возвращаемые domain entities:** RefreshToken

### FavoriteRepository
- **Назначение:** управление избранным и проверкой существования аниме без прямого CRUD.
- **Методы (словами):**
  - проверить существование аниме по id
  - получить избранное по user_id + anime_id
  - список избранного для пользователя
  - добавить избранное
  - удалить избранное
- **Возвращаемые domain entities:** Favorite (и при необходимости Anime для проверки существования)

### WatchProgressRepository
- **Назначение:** управление прогрессом просмотра и проверкой существования аниме без прямого CRUD.
- **Методы (словами):**
  - проверить существование аниме по id
  - получить прогресс по user_id + anime_id
  - список прогресса для пользователя
  - создать прогресс
  - обновить прогресс
- **Возвращаемые domain entities:** WatchProgress (и при необходимости Anime для проверки существования)

## Migration Phases

### Phase 1 — Auth
- **Use cases:** register_user, login_user, refresh_session, logout_user
- **Порты:** UserRepository, TokenRepository
- **Тесты, которые должны быть добавлены:**
  - unit-тесты use_cases с фейковыми UserRepository/TokenRepository
  - контрактные тесты адаптеров UserRepository/TokenRepository в infrastructure/crud
  - обновление guard-теста, чтобы он проверял только auth use_cases
- **Критерий «фаза завершена»:**
  - auth use_cases принимают только ports и не импортируют CRUD/SQLAlchemy
  - adapters для UserRepository/TokenRepository находятся в infrastructure/crud
  - auth тесты и guard-тест по фазе зелёные

### Phase 2 — Favorites
- **Use cases:** add_favorite, remove_favorite, get_favorites
- **Порты:** FavoriteRepository
- **Тесты, которые должны быть добавлены:**
  - unit-тесты favorites use_cases с фейковым FavoriteRepository
  - контрактные тесты адаптера FavoriteRepository в infrastructure/crud
  - расширение guard-теста на favorites use_cases
- **Критерий «фаза завершена»:**
  - favorites use_cases получают только FavoriteRepository
  - фоновые операции внутри favorites не используют AsyncSessionLocal напрямую
  - guard-тест для auth + favorites зелёный

### Phase 3 — Watch / Progress
- **Use cases:** get_continue_watching, update_progress
- **Порты:** WatchProgressRepository
- **Тесты, которые должны быть добавлены:**
  - unit-тесты watch use_cases с фейковым WatchProgressRepository
  - контрактные тесты адаптера WatchProgressRepository в infrastructure/crud
  - расширение guard-теста на watch use_cases
- **Критерий «фаза завершена»:**
  - watch use_cases получают только WatchProgressRepository
  - guard-тест для auth + favorites + watch зелёный

### Phase 4 — Background jobs (если применимо)
- **Use cases:** persist_add_favorite, persist_update_progress (фоновые ветки в favorites/watch)
- **Порты:** FavoriteRepository, WatchProgressRepository
- **Тесты, которые должны быть добавлены:**
  - unit-тесты фоновых handlers с фейковыми репозиториями
  - контрактные тесты адаптеров для фонового исполнения (при необходимости)
- **Критерий «фаза завершена»:**
  - фоновые ветки используют только ports и не создают AsyncSessionLocal внутри use_cases
  - фоновые тесты зелёные

## Rules of Migration

- ❌ один PR = одна фаза
- ❌ нельзя мигрировать несколько фич сразу
- ❌ нельзя менять бизнес-логику
- ❌ нельзя «чинить заодно»
- ✅ use_cases получают ТОЛЬКО ports
- ✅ adapters живут ТОЛЬКО в infrastructure/crud
- ✅ guard-тест включается ПОЭТАПНО
