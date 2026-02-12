# Frontend (Next.js)

## Назначение
Пользовательский интерфейс каталога и плеера. Работает только при доступном FastAPI и HLS‑прокси, читает данные через REST.

## Конфигурация
- `NEXT_PUBLIC_API_BASE_URL` — базовый URL FastAPI (обязателен).
- `NEXT_PUBLIC_PROXY_URL` — базовый URL HLS/m3u8 прокси, используется плеером для потоков.
- Переменные читаются в рантайме через `next-runtime-env`; отсутствие `NEXT_PUBLIC_API_BASE_URL` делает запросы к API невозможными.

## Источники данных
- **FastAPI**: axios‑клиент (`frontend/lib/api.ts`) добавляет Bearer токен из auth‑стора. Используются маршруты `/auth/*`, `/users/me`, `/favorites`, `/anime`, `/releases`, `/episodes`, `/watch/continue` и `/watch/progress`.
- **HiAnime (aniwatch) через FastAPI proxy**: поиск (`/api/search`), расписание (`/api/schedule`), домашние списки (`/api/home`), детали аниме и эпизодов (`/api/anime/[id]`, `/api/episode/*`), AniList import (`/api/import/anilist`) для сопоставления с HiAnime.
- **Прокси потоков**: `NEXT_PUBLIC_PROXY_URL/m3u8-proxy?url=...&referer=...` формируется внутри плеера (`frontend/components/kitsune-player.tsx`).

## Основные потоки UI
- **Аутентификация**: `login-popover-button` вызывает `/auth/login` и `/auth/register`, сохраняет токены и подгружает `/users/me`. Навбар обновляет сессию через `/auth/refresh` при наличии refresh токена.
- **Избранное**: страницы `anime/[slug]` и `anime/watch` отображают кнопку избранного; запросы `GET/POST/DELETE /favorites` выполняются через FastAPI. Кнопка отключается, если нет `write:content`.
- **Профиль**: `profile/[username]` показывает списки и тепловую карту; диалог импорта AniList вызывает `/api/import/anilist` и создаёт закладки локально, доступен только при `write:profile`.
- **Продолжить просмотр**: хуки `use-get-bookmark` и плеер сохраняют прогресс локально (localStorage); серверный `/watch/progress` сейчас не вызывается, выдача списка опирается на локальные данные.

## Ограничения
- UI не содержит собственной БД: все постоянные данные приходят из FastAPI. При ошибках бекенда выводятся пустые состояния или тосты.
- RBAC на клиенте носит характер видимости/дизейблов; фактическое разрешение определяется сервером (см. `RBAC.md`).
