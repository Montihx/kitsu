from datetime import datetime, timezone

from fastapi import status
from ...application.auth_rate_limit import (
    RATE_LIMIT_MESSAGE,
    RateLimitExceededError,
    check_refresh_rate_limit,
    record_refresh_failure,
    reset_refresh_limit,
)
from ...domain.ports.token import RefreshTokenPort
from ...errors import AppError, AuthError, PermissionError
from ...security.token_inspection import InvalidTokenError, validate_refresh_token
from .register_user import AuthTokens, issue_tokens


REFRESH_TOKEN_IDENTIFIER_LENGTH = 16


async def _validate_and_issue_tokens(
    token_port: RefreshTokenPort, token_hash: str
) -> AuthTokens:
    stored_token = await token_port.get_by_hash(token_hash, for_update=True)
    if stored_token is None:
        raise AuthError()
    if stored_token.revoked:
        raise PermissionError()
    if stored_token.expires_at <= datetime.now(timezone.utc):
        raise AuthError()
    return await issue_tokens(token_port, stored_token.user_id)


async def refresh_session(
    token_port: RefreshTokenPort,
    refresh_token: str,
    *,
    client_ip: str | None = None,
) -> AuthTokens:
    try:
        token_hash = validate_refresh_token(refresh_token)
    except InvalidTokenError:
        raise AuthError() from None

    token_identifier = token_hash[:REFRESH_TOKEN_IDENTIFIER_LENGTH]
    try:
        key = await check_refresh_rate_limit(token_identifier, client_ip)
    except RateLimitExceededError:
        raise AppError(
            RATE_LIMIT_MESSAGE,
            code="RATE_LIMITED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        ) from None

    try:
        tokens = await _validate_and_issue_tokens(token_port, token_hash)
    except (AuthError, PermissionError):
        await record_refresh_failure(key)
        await token_port.rollback()
        raise
    except AppError:
        await token_port.rollback()
        raise
    except Exception:
        await token_port.rollback()
        raise
    await reset_refresh_limit(key)
    return tokens
