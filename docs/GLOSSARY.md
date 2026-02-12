# Глоссарий

- **Access token** — короткоживущий JWT, кладётся в `Authorization: Bearer` для защищённых маршрутов FastAPI.
- **Refresh token** — долгоживущий токен для обновления пары токенов через `/auth/refresh`; logout удаляет refresh‑сессию.
- **RBAC** — ролевое управление доступом с ролями `guest/user/admin` и правами `read|write:profile/content`, `admin:*`.
- **Избранное (favorites)** — связь пользователь ↔ аниме. Создаётся/удаляется через `/favorites`, хранится в БД, UI отображает кнопки на страницах аниме.
- **Прогресс просмотра** — запись `WatchProgress` с эпизодом, позицией и процентом; обновляется через `/watch/progress`, читается в `/watch/continue`.
- **HLS-прокси** — внешний endpoint `/m3u8-proxy` по `NEXT_PUBLIC_PROXY_URL`, который пробрасывает HLS‑потоки для плеера.
- **HiAnime (aniwatch)** — внешний источник каталога/потоков, обёрнутый в Next API routes (`/api/search`, `/api/anime/[id]`, `/api/episode/*`).
- **Очередь фоновых задач** — `default_job_runner`, in‑process worker для записей избранного и прогресса, без персистентности.
- **Аватары** — файлы пользователей, загруженные через `PATCH /users/me`, хранятся в `backend/uploads/avatars` и раздаются по `/media/avatars`.
