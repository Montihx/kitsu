# Backend Architecture Contract

## 1.1 Слои системы

1) transport/
- FastAPI routers
- HTTP-ответы
- error mapping
- ❌ не знает domain
- ❌ не знает infra
- ❌ не содержит бизнес-логики

2) use_cases/
- orchestration
- бизнес-потоки
- работа с портами (interfaces)
- ❌ не знает FastAPI
- ❌ не знает SQLAlchemy

3) application/
- rate limit
- application services
- repository factories
- glue-код между use_cases и infra

4) domain/
- entities
- domain errors
- ports (interfaces)
- ❌ НИКАКИХ импортов из других слоёв

5) security/
- token inspection
- crypto
- ❌ не знает rate limit
- ❌ не знает бизнес

6) infrastructure / crud
- SQLAlchemy
- внешние API
- реализации портов

## 1.2 Разрешённые зависимости (таблица или список)

- transport → use_cases
- use_cases → domain, application, security
- application → domain
- security → domain
- infrastructure → domain

❌ Любые другие зависимости запрещены.

## 1.3 Запрещённые практики

- ❌ бизнес-логика в router
- ❌ AppError вне transport
- ❌ SQLAlchemy в use_cases
- ❌ domain, который импортирует что-либо
- ❌ security, который знает про rate limit
- ❌ rate limit, который знает про токены
