from fastapi import status
from ...application.auth_rate_limit import (
    RATE_LIMIT_MESSAGE,
    RateLimitExceededError,
    check_login_rate_limit,
    record_login_failure,
    reset_login_limit,
)
from ...domain.ports.token import RefreshTokenPort
from ...domain.ports.user import UserPort
from ...errors import AppError, AuthError, PermissionError
from ...utils.security import verify_password
from .register_user import AuthTokens, issue_tokens


async def _authenticate_user(
    user_port: UserPort,
    token_port: RefreshTokenPort,
    email: str,
    password: str,
) -> AuthTokens:
    user = await user_port.get_by_email(email)
    if user is None or not verify_password(password, user.password_hash):
        raise AuthError()
    return await issue_tokens(token_port, user.id)


async def login_user(
    user_port: UserPort,
    token_port: RefreshTokenPort,
    email: str,
    password: str,
    *,
    client_ip: str | None = None,
) -> AuthTokens:
    try:
        key = await check_login_rate_limit(email, client_ip)
    except RateLimitExceededError:
        raise AppError(
            RATE_LIMIT_MESSAGE,
            code="RATE_LIMITED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        ) from None

    try:
        tokens = await _authenticate_user(user_port, token_port, email, password)
    except (AuthError, PermissionError):
        await record_login_failure(key)
        await token_port.rollback()
        raise
    except AppError:
        await token_port.rollback()
        raise
    except Exception:
        await token_port.rollback()
        raise
    await reset_login_limit(key)
    return tokens
