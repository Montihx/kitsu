from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class Pagination(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ApiMeta(BaseModel):
    request_id: str | None = None
    extra: dict[str, Any] | None = None


class ApiError(BaseModel):
    code: str
    message: str
    details: Any | None = None


class ApiResponse(BaseModel, Generic[T]):
    data: T | None = None
    meta: ApiMeta | None = None
    error: ApiError | None = None

    @classmethod
    def ok(cls, data: T, meta: ApiMeta | None = None) -> "ApiResponse[T]":
        return cls(data=data, meta=meta, error=None)

    @classmethod
    def fail(
        cls,
        code: str,
        message: str,
        *,
        details: Any | None = None,
        meta: ApiMeta | None = None,
    ) -> "ApiResponse[T]":
        return cls(data=None, meta=meta, error=ApiError(code=code, message=message, details=details))
