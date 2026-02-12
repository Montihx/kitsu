# RBAC

## Роли и разрешения
- Роли: `guest`, `user`, `admin`.
- Разрешения:
  - `read:profile`, `write:profile`
  - `read:content`, `write:content`
  - `admin:*`
- Соответствие ролей и прав (backend `app/auth/rbac.py`, frontend `src/auth/rbac.ts`):
  - `guest`: `read:content`
  - `user`: `read:profile`, `write:profile`, `read:content`, `write:content`
  - `admin`: все базовые разрешения + `admin:*`

## Разрешение роли
- Backend: `resolve_role` использует `user.role`, либо `is_admin`/`is_superuser`; при отсутствии пользователя роль `guest`.
- Frontend: `resolveRole` читает auth‑стор; без access‑токена роль `guest`.

## Применение
- Backend: зависимость `require_enforced_permission` читает матрицу (`ENFORCEMENT_MATRIX`) и проверяет наличие разрешения у текущего пользователя; при отсутствии — 403.
- Frontend: хуки `usePermissions`/`useRole` управляют видимостью/disabled кнопок (избранное, импорт AniList). Это облегчает UX, но не заменяет серверные проверки.

Подробное сопоставление маршрутов и разрешений приведено в `RBAC_CONTRACTS.md`.
