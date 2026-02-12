# Backend (FastAPI)

## Назначение
- Авторизация (JWT access/refresh), выпуск и отзыв токенов.
- Каталог аниме, релизы, эпизоды, поиск.
- Избранное и прогресс просмотра с асинхронной фиксацией в БД.
- Загрузка и раздача аватаров пользователей по `/media/avatars`.

## Конфигурация и зависимости
- Обязательные переменные: `SECRET_KEY`, `DATABASE_URL=postgresql+asyncpg://...`.
  - Альтернатива для docker-compose: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.
- Дополнительно: `ACCESS_TOKEN_EXPIRE_MINUTES` (30 по умолчанию), `REFRESH_TOKEN_EXPIRE_DAYS` (14), `ALGORITHM` (HS256), `ALLOWED_ORIGINS` (CORS, список), `DEBUG`, пул БД (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_RECYCLE`, `DB_POOL_PRE_PING`).
  - **ВАЖНО для `ALLOWED_ORIGINS`**: Указывайте origins БЕЗ завершающего слеша. Например: `https://frontend-79rs.onrender.com` (правильно), а не `https://frontend-79rs.onrender.com/` (неправильно).
- На старте выполняются Alembic‑миграции и проверка доступности БД; при ошибке приложение не поднимается. `/health` возвращает 200 при успешном подключении к БД, 503 иначе.

## API (текущее состояние)
- **Аутентификация** (публично): `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`.
- **Пользователи**:
  - `GET /users/me` — профиль текущего пользователя (Bearer обязателен).
  - `PATCH /users/me` — загрузка аватара, требует `write:profile`.
  - `GET /users`, `POST /users`, `GET /users/{user_id}` — заглушки (возвращают фиктивные данные).
- **Каталог**: `GET /anime` (пагинация), `GET /anime/{id}`, `GET /releases`, `GET /releases/{id}`, `GET /episodes?release_id=...` (404, если релиз не найден).
- **Поиск**: `GET /search/anime?q=...` (минимум 2 символа).
- **Избранное**: `GET /favorites` (Bearer), `POST /favorites` (write:content), `DELETE /favorites/{anime_id}` (write:content).
- **Просмотры**: `POST /watch/progress` (write:content) — валидация эпизода, процентов и позиции; `GET /watch/continue` — продолжить просмотр по пользователю.
- **Collections/Views**: `GET/POST /collections`, `GET/POST /views` — заглушки для будущей реализации.
- **Статика**: `/media/avatars/<файл>` — отдаётся напрямую FastAPI.
- **HiAnime proxy**: `/api/health`, `/api/home`, `/api/schedule`, `/api/search`, `/api/anime/*`, `/api/episode/*`, `/api/import/anilist` проксируют к HiAnime (aniwatch) и возвращают данные для плеера и поиска.

## Use cases и фоновые задачи
- `POST /favorites` и `DELETE /favorites/{anime_id}` возвращают результат сразу и ставят задачу в `default_job_runner` (ключи `favorite:add:*` и `favorite:remove:*`). Каждая задача открывает новую БД‑сессию и коммитит изменение; при ошибке выполняется rollback.
- `POST /watch/progress` создаёт или обновляет запись прогресса через задачу `watch-progress:*`, проверяя наличие аниме и валидность данных.
- Очередь in‑process: нет персистентности, статусы (`queued`, `running`, `succeeded`, `failed`) хранятся в памяти; повторное добавление с тем же ключом блокируется пока задача не завершится.

## Ошибки и безопасность
- Своё семейство ошибок (`AppError`, `ValidationError`, `AuthError`, `PermissionError`, `NotFoundError`, `ConflictError`, `InternalError`) сериализуется как `{"code": ..., "message": ..., "details": ...}`.
- HTTP‑исключения мапятся на безопасные сообщения и коды ошибок (`resolve_error_code`) для 4xx/5xx.
- Аутентификация: Bearer токен обязателен для защищённых маршрутов; неверный или истёкший токен даёт 401. RBAC‑проверки возвращают 403 при недостатке разрешений.
