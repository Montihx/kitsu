# Kitsu

Веб‑сервис каталога и воспроизведения аниме с разделением на:
- **frontend/** — Next.js (UI, HTTP‑клиент)
- **backend/** — FastAPI (единственный API и бизнес‑логика)

Подробности архитектуры и процессов: [docs/README.md](docs/README.md).

## Запуск локально

- Frontend:  
  ```
  cd frontend
  NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
  ```
- Backend (требует PostgreSQL):  
  ```
  cd backend
  DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/kitsu \
  SECRET_KEY=please-set-secret-key \
  ALLOWED_ORIGINS=http://localhost:3000 \
  python -m uvicorn app.main:app
  ```
  
  Примечание: `ALLOWED_ORIGINS` поддерживает оба формата:
  - CSV: `http://localhost:3000,http://localhost:8080`
  - JSON: `["http://localhost:3000","http://localhost:8080"]`
  - **ВАЖНО**: НЕ добавляйте завершающий слеш к origins (например: `https://frontend.onrender.com`, а не `https://frontend.onrender.com/`)

## Docker

- Frontend Dockerfile — корень репозитория (`./Dockerfile`, контекст корня).
- Backend Dockerfile — `./backend/Dockerfile`.
- Компоновка сервисов:  
  ```
  BACKEND_PORT=8000 FRONTEND_PORT=3000 docker compose up --build frontend backend
  ```
  Переменная `BACKEND_PORT` используется только для backend, чтобы избежать конфликта с портом фронтенда.
  Для Render/CI выставляйте корень фронтенда в `/frontend`, бэкенда — в `/backend`.

## Тесты

```
cd backend
python -m pip install -e .[dev]
python -m pytest tests/test_watch_use_cases.py tests/test_watch_adapters.py tests/test_architecture_contract.py
```
