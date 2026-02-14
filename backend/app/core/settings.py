from __future__ import annotations

import os
from functools import lru_cache

from pydantic import BaseModel, Field

from app.config import get_settings as get_legacy_settings


class CoreSettings(BaseModel):
    app_name: str
    debug: bool
    secret_key: str
    database_url: str
    redis_url: str
    allowed_origins: list[str]
    log_level: str = Field(default="INFO")


@lru_cache(maxsize=1)
def get_settings() -> CoreSettings:
    legacy = get_legacy_settings()
    return CoreSettings(
        app_name=legacy.app_name,
        debug=legacy.debug,
        secret_key=legacy.secret_key or "",
        database_url=legacy.database_url,
        redis_url=legacy.redis_url,
        allowed_origins=legacy.allowed_origins,
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
