import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt as passlib_bcrypt

from ..config import settings

class TokenExpiredError(Exception):
    pass


class TokenInvalidError(Exception):
    pass


passlib_bcrypt.set_backend("bcrypt")
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",
)


def _normalize_password(password: str) -> str:
    """Normalize passwords to avoid bcrypt's 72-byte input limit."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    normalized_password = _normalize_password(password)
    return pwd_context.hash(normalized_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    normalized_password = _normalize_password(plain_password)
    try:
        if pwd_context.verify(normalized_password, hashed_password):
            return True
    except ValueError:
        pass
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        return False


def create_access_token(payload: dict[str, Any]) -> str:
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError from exc
    except jwt.InvalidTokenError as exc:
        raise TokenInvalidError from exc


def create_refresh_token() -> str:
    return secrets.token_urlsafe()


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def verify_refresh_token(token: str, token_hash: str) -> bool:
    return hmac.compare_digest(hash_refresh_token(token), token_hash)
